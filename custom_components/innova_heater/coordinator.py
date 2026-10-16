"""Data coordinator for Innova Cloud."""
import asyncio
import logging
import struct
from datetime import timedelta

import aiohttp
import grpc
from google.protobuf import empty_pb2

from homeassistant.const import CONF_EMAIL, CONF_PASSWORD
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ConfigEntryAuthFailed, HomeAssistantError
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed
from homeassistant.config_entries import ConfigEntry

from .api import validate_login
from .const import (
    DOMAIN,
    GRPC_HOST,
    GRPC_PORT,
    UPDATE_INTERVAL,
    EVENT_TYPE_CURRENT_TEMP,
    EVENT_TYPE_TARGET_TEMP,
    EVENT_TYPE_POWER_STATE,
    EVENT_TYPE_OPERATION_MODE,
    EVENT_TYPE_FAN_SPEED,
    EVENT_TYPE_FANCOIL_FAN_SPEED,
    EVENT_TYPE_FANCOIL_OPERATION_MODE,
    EVENT_TYPE_FANCOIL_ROOM_TEMP,
    EVENT_TYPE_FANCOIL_SETPOINT,
    EVENT_TYPE_FANCOIL_POWER_STATE,
    EVENT_TYPE_FANCOIL_FLAP,
    OP_TYPE_POWER_STATE,
    OP_TYPE_SETPOINT,
    OP_TYPE_OPERATION_MODE,
    OP_TYPE_FAN_SPEED,
    OP_TYPE_FLAP,
    OP_TYPE_REBOOT,
)
from . import controls_pb2, controls_pb2_grpc

_LOGGER = logging.getLogger(__name__)


def _is_auth_error(err: Exception) -> bool:
    """Return True if the gRPC error means our token is invalid/expired."""
    return isinstance(err, grpc.aio.AioRpcError) and err.code() == grpc.StatusCode.UNAUTHENTICATED


class InnovaHeaterCoordinator(DataUpdateCoordinator):
    """Coordinator to manage Innova Cloud data."""

    def __init__(self, hass: HomeAssistant, entry: ConfigEntry) -> None:
        """Initialize coordinator."""
        _LOGGER.info("Initializing InnovaHeaterCoordinator for MAC: %s", entry.data.get("mac_address"))

        # Events push changes in real time; the periodic poll re-syncs the full
        # status so missed events or ignored commands don't leave HA out of sync.
        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=timedelta(seconds=UPDATE_INTERVAL),
        )
        self.entry = entry
        self.mac_address = entry.data["mac_address"]
        self.token = entry.data["token"]
        self.channel = None
        self.stub = None
        self._event_task = None
        self._token_lock = asyncio.Lock()
        self._initial_data_received = False

        # Initialize with default data
        self.data = {
            "current_temp": None,
            "target_temp": None,
            "min_temp": 5.0,
            "max_temp": 40.0,
            "target_temp_step": 0.5,
            "power_state": None,
            "operation_mode": None,
            "fan_speed": None,
            "flap": None,
            "has_flap": False,
            "calendar_active": None,
            "keyboard_lock": None,
            "mode_lock": None,
            "hotel_mode": None,
            "temperature_unit": None,
            "wifi_ssid": None,
            "wifi_rssi": None,
            "connection_type": None,
            "fw_version": None,
            "serial_number": None,
        }

    def _metadata(self) -> list[tuple[str, str]]:
        """Build gRPC call metadata with the current token."""
        return [
            ("mac_address", self.mac_address),
            ("authorization", f"Bearer {self.token}"),
        ]

    async def _async_renew_token(self, failed_token: str) -> None:
        """Log in again with the stored credentials to get a new token.

        Raises ConfigEntryAuthFailed if no credentials are stored or they are rejected,
        which makes Home Assistant ask the user to re-authenticate.
        """
        async with self._token_lock:
            if self.token != failed_token:
                # Another call already renewed the token while we were waiting
                return

            email = self.entry.data.get(CONF_EMAIL)
            password = self.entry.data.get(CONF_PASSWORD)
            if not email or not password:
                raise ConfigEntryAuthFailed(
                    "Innova Cloud token expired and no credentials are stored; please re-authenticate"
                )

            _LOGGER.info("Innova Cloud token expired, logging in again")
            try:
                result = await validate_login(self.hass, email, password)
            except (aiohttp.ClientError, TimeoutError) as err:
                raise UpdateFailed(f"Could not reach Innova Cloud to renew token: {err}") from err

            if not result or not result.get("token"):
                raise ConfigEntryAuthFailed("Innova Cloud rejected the stored credentials")

            self.token = result["token"]
            self.hass.config_entries.async_update_entry(
                self.entry, data={**self.entry.data, "token": self.token}
            )
            _LOGGER.info("Innova Cloud token renewed")

    async def _async_call(self, method, request):
        """Call a unary gRPC method, renewing the token once if it has expired."""
        token = self.token
        try:
            return await method(request, metadata=self._metadata())
        except grpc.aio.AioRpcError as err:
            if not _is_auth_error(err):
                raise
            await self._async_renew_token(token)
            return await method(request, metadata=self._metadata())

    async def _async_setup_channel(self):
        """Set up the gRPC channel and start the event listener."""
        credentials = grpc.ssl_channel_credentials()
        self.channel = grpc.aio.secure_channel(
            f"{GRPC_HOST}:{GRPC_PORT}",
            credentials
        )
        self.stub = controls_pb2_grpc.ControlsStub(self.channel)

    async def _fetch_status(self):
        """Fetch the full device status and merge it into self.data."""
        status = await self._async_call(self.stub.GetDeviceStatus, empty_pb2.Empty())

        if not status.HasField('main_status'):
            _LOGGER.warning("No main_status in response")
            return

        main = status.main_status

        if main.serial_number:
            self.data["serial_number"] = main.serial_number

        device_type = main.WhichOneof('device_status')
        device_status = getattr(main, device_type) if device_type else None

        if device_status:
            _LOGGER.debug("Device type: %s", device_type)
            # Protobuf hasattr() is always True for declared fields, so check
            # the message descriptor to see which fields this device type has.
            fields = device_status.DESCRIPTOR.fields_by_name

            if 'power_state' in fields:
                self.data["power_state"] = device_status.power_state

            if 'room_temperature' in fields and device_status.room_temperature > 0:
                self.data["current_temp"] = device_status.room_temperature / 10.0
                self._initial_data_received = True

            if 'temperature_setpoint' in fields and device_status.HasField('temperature_setpoint'):
                setpoint = device_status.temperature_setpoint
                self.data["target_temp"] = setpoint.value / 10.0
                self.data["min_temp"] = setpoint.min / 10.0 if setpoint.min > 0 else 5.0
                self.data["max_temp"] = setpoint.max / 10.0 if setpoint.max > 0 else 40.0
                self.data["target_temp_step"] = setpoint.step / 10.0 if setpoint.step > 0 else 0.5

            if 'operation_mode' in fields:
                self.data["operation_mode"] = device_status.operation_mode

            if 'fan_speed' in fields:
                self.data["fan_speed"] = device_status.fan_speed

            if 'flap' in fields:
                self.data["flap"] = device_status.flap

            if 'has_flap' in fields:
                self.data["has_flap"] = device_status.has_flap

            if 'keyboard_lock' in fields:
                self.data["keyboard_lock"] = device_status.keyboard_lock

            if 'mode_lock' in fields:
                self.data["mode_lock"] = device_status.mode_lock

            if 'hotel_mode' in fields:
                self.data["hotel_mode"] = device_status.hotel_mode

            if 'temperature_unit' in fields:
                self.data["temperature_unit"] = device_status.temperature_unit

            if 'calendar' in fields and device_status.HasField('calendar'):
                self.data["calendar_active"] = device_status.calendar.is_active
        else:
            _LOGGER.debug("GetDeviceStatus returned no device status, waiting for events...")

        # Parse IoT status (WiFi, firmware, etc.)
        if status.HasField('iot_status'):
            iot = status.iot_status

            if iot.fw_version:
                self.data["fw_version"] = iot.fw_version

            if iot.HasField('wifi'):
                self.data["connection_type"] = "WiFi"
                self.data["wifi_ssid"] = iot.wifi.ssid
                self.data["wifi_rssi"] = iot.wifi.rssi
            elif iot.HasField('ethernet'):
                self.data["connection_type"] = "Ethernet"
            elif iot.HasField('thread'):
                self.data["connection_type"] = "Thread"

        _LOGGER.debug("Status loaded: %s", self.data)

    async def _listen_events(self):
        """Listen to device events in background."""
        _LOGGER.info("Starting event listener for MAC: %s", self.mac_address)

        retry_delay = 5  # Start with 5 seconds
        max_retry_delay = 60  # Max 60 seconds between retries

        while True:
            token = self.token
            try:
                _LOGGER.debug("Subscribing to device events...")
                empty = empty_pb2.Empty()
                async for event in self.stub.SubscribeToDeviceEvents(empty, metadata=self._metadata()):
                    await self._process_event(event)
                    # Reset retry delay on successful event processing
                    retry_delay = 5

            except asyncio.CancelledError:
                _LOGGER.info("Event listener cancelled")
                break
            except Exception as err:
                if _is_auth_error(err):
                    try:
                        # Reconnect with the new token after the (backed-off) delay below,
                        # so a server that keeps rejecting tokens doesn't cause a login storm
                        await self._async_renew_token(token)
                    except ConfigEntryAuthFailed as auth_err:
                        _LOGGER.error("Event stream stopped: %s", auth_err)
                        self.entry.async_start_reauth(self.hass)
                        break
                    except UpdateFailed as renew_err:
                        _LOGGER.warning("%s", renew_err)
                else:
                    _LOGGER.error("Event stream error: %s", err, exc_info=True)
                _LOGGER.info("Reconnecting to event stream in %d seconds...", retry_delay)
                await asyncio.sleep(retry_delay)

                # Exponential backoff with max limit
                retry_delay = min(retry_delay * 2, max_retry_delay)

    async def _process_event(self, event):
        """Process incoming event and update data."""
        _LOGGER.debug("Received event type=%s, value=%s", event.type, event.value.hex() if event.value else None)

        if event.value and len(event.value) >= 2:
            value_int = struct.unpack('>H', event.value[:2])[0]

            updated = False
            # Temperature events (Fancoil uses 253/254, legacy uses same)
            if event.type in (EVENT_TYPE_CURRENT_TEMP, EVENT_TYPE_FANCOIL_ROOM_TEMP):
                self.data["current_temp"] = value_int / 10.0
                _LOGGER.debug("Event: Current temp = %s°C", self.data["current_temp"])
                updated = True
                self._initial_data_received = True
            elif event.type in (EVENT_TYPE_TARGET_TEMP, EVENT_TYPE_FANCOIL_SETPOINT):
                self.data["target_temp"] = value_int / 10.0
                _LOGGER.debug("Event: Target temp = %s°C", self.data["target_temp"])
                updated = True
            # Power state (Fancoil=255, legacy=1)
            elif event.type in (EVENT_TYPE_POWER_STATE, EVENT_TYPE_FANCOIL_POWER_STATE):
                self.data["power_state"] = bool(value_int)
                _LOGGER.debug("Event: Power state = %s", self.data["power_state"])
                updated = True
            # Operation mode (Fancoil=252, legacy=3)
            elif event.type in (EVENT_TYPE_OPERATION_MODE, EVENT_TYPE_FANCOIL_OPERATION_MODE):
                old_mode = self.data["operation_mode"]
                self.data["operation_mode"] = value_int
                _LOGGER.debug("Event: Operation mode changed from %s to %s", old_mode, value_int)
                updated = True
            # Fan speed (Fancoil=251, legacy=4)
            elif event.type in (EVENT_TYPE_FAN_SPEED, EVENT_TYPE_FANCOIL_FAN_SPEED):
                self.data["fan_speed"] = value_int
                _LOGGER.debug("Event: Fan speed = %s", self.data["fan_speed"])
                updated = True
            # Flap position (Fancoil=250)
            elif event.type == EVENT_TYPE_FANCOIL_FLAP:
                self.data["flap"] = value_int
                _LOGGER.debug("Event: Flap position = %s", self.data["flap"])
                updated = True
            else:
                _LOGGER.debug("Unknown event type: %s, value: %s", event.type, value_int)

            if updated:
                # Infer power state if we have temp data but no explicit power event
                if self.data["power_state"] is None and self.data["current_temp"] is not None:
                    _LOGGER.debug("Inferring power state = ON from temp data")
                    self.data["power_state"] = True

                _LOGGER.debug("Updated data: %s", self.data)
                # Create a new dict copy to ensure Home Assistant detects the change
                self.async_set_updated_data(dict(self.data))

    async def _async_update_data(self):
        """Fetch the full device status; real-time changes arrive via the event stream."""
        if self.channel is None:
            await self._async_setup_channel()

        try:
            await self._fetch_status()
        except grpc.aio.AioRpcError as err:
            raise UpdateFailed(f"Failed to fetch device status: {err.code().name} {err.details()}") from err

        if self._event_task is None or self._event_task.done():
            self._event_task = self.entry.async_create_background_task(
                self.hass, self._listen_events(), f"{DOMAIN}_events_{self.mac_address}"
            )

        return dict(self.data)

    async def _async_set_value(self, op_type: int, value: int, key: str | None = None, new_state=None) -> None:
        """Send a SetDeviceValue command, optimistically updating `key` to `new_state`.

        If the command fails the optimistic update is rolled back, so HA does not
        show a state the device never received.
        """
        request = controls_pb2.SetDeviceValueRequest(type=op_type, value=value)

        if key is not None:
            old_state = self.data.get(key)
            self.data[key] = new_state
            self.async_set_updated_data(dict(self.data))

        try:
            await self._async_call(self.stub.SetDeviceValue, request)
        except Exception as err:
            if key is not None:
                self.data[key] = old_state
                self.async_set_updated_data(dict(self.data))
            if isinstance(err, ConfigEntryAuthFailed):
                self.entry.async_start_reauth(self.hass)
            raise HomeAssistantError(f"Innova Cloud command failed (type={op_type}, value={value}): {err}") from err

        _LOGGER.debug("Sent command type=%d value=%d", op_type, value)

    async def async_set_temperature(self, temperature: float) -> None:
        """Set target temperature."""
        await self._async_set_value(OP_TYPE_SETPOINT, round(temperature * 10), "target_temp", temperature)

    async def async_set_power(self, power_on: bool) -> None:
        """Set power state."""
        await self._async_set_value(OP_TYPE_POWER_STATE, 1 if power_on else 0, "power_state", power_on)

    async def async_set_operation_mode(self, mode: int) -> None:
        """Set operation mode (0=Auto, 1=Heat, 2=Cool, 3=Fan, 4=Dry)."""
        if self.data.get("mode_lock"):
            _LOGGER.warning(
                "Device reports mode_lock=%s; the operation mode change may be ignored by the device",
                self.data["mode_lock"],
            )
        await self._async_set_value(OP_TYPE_OPERATION_MODE, mode, "operation_mode", mode)

    async def async_set_fan_speed(self, speed: int) -> None:
        """Set fan speed (device-dependent values)."""
        await self._async_set_value(OP_TYPE_FAN_SPEED, speed, "fan_speed", speed)

    async def async_set_flap(self, position: int) -> None:
        """Set flap position (if device has flap support)."""
        if not self.data.get("has_flap"):
            _LOGGER.warning("Device does not support flap control")
            return
        await self._async_set_value(OP_TYPE_FLAP, position, "flap", position)

    async def async_reboot(self) -> None:
        """Reboot the device."""
        await self._async_set_value(OP_TYPE_REBOOT, 1)

    async def async_shutdown(self):
        """Shutdown coordinator."""
        _LOGGER.info("Shutting down coordinator for MAC: %s", self.mac_address)
        await super().async_shutdown()

        if self._event_task and not self._event_task.done():
            self._event_task.cancel()
            try:
                await self._event_task
            except asyncio.CancelledError:
                _LOGGER.debug("Event task cancelled successfully")
            except Exception as err:
                _LOGGER.warning("Error while cancelling event task: %s", err)

        if self.channel:
            try:
                await self.channel.close()
                _LOGGER.debug("gRPC channel closed")
            except Exception as err:
                _LOGGER.warning("Error while closing channel: %s", err)
