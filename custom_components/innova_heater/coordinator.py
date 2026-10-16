"""Data coordinator for Innova Cloud (v2 API)."""
import asyncio
import logging
import uuid
from datetime import timedelta

import aiohttp
import grpc

from homeassistant.const import CONF_EMAIL, CONF_PASSWORD
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ConfigEntryAuthFailed, HomeAssistantError
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed
from homeassistant.config_entries import ConfigEntry

from .api import get_devices, validate_login
from .const import (
    DOMAIN,
    CONF_NODE_ID,
    CONF_HOME_ID,
    GRPC_HOST,
    GRPC_PORT,
    UPDATE_INTERVAL,
    COMMAND_TIMEOUT,
    HVAC_MODE_AUTO,
    OPERATION_MODE_CALENDAR,
)
from . import app_service_pb2 as pb, app_service_pb2_grpc as pb_grpc

_LOGGER = logging.getLogger(__name__)

# Node types that share the climate state/command layout
CLIMATE_NODE_TYPES = ("ac", "fancoil", "thermostat")


class InnovaApiError(Exception):
    """The Innova Cloud returned an error response."""


def _is_auth_error(err: Exception) -> bool:
    """Return True if the gRPC error means our token is invalid/expired."""
    return isinstance(err, grpc.aio.AioRpcError) and err.code() == grpc.StatusCode.UNAUTHENTICATED


def _enum_name(enum, value: int) -> str:
    """Return the name of a protobuf enum value, tolerating unknown values."""
    try:
        return enum.Name(value)
    except ValueError:
        return str(value)


class InnovaHeaterCoordinator(DataUpdateCoordinator):
    """Coordinator to manage Innova Cloud data."""

    def __init__(self, hass: HomeAssistant, entry: ConfigEntry) -> None:
        """Initialize coordinator."""
        _LOGGER.info("Initializing InnovaHeaterCoordinator for MAC: %s", entry.data.get("mac_address"))

        # Events push changes in real time; the periodic poll re-syncs the full
        # state so missed events or ignored commands don't leave HA out of sync.
        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=timedelta(seconds=UPDATE_INTERVAL),
        )
        self.entry = entry
        self.mac_address = entry.data["mac_address"]
        # Entries created against the v1 API lack these; resolved on first update
        self.node_id = entry.data.get(CONF_NODE_ID)
        self.home_id = entry.data.get(CONF_HOME_ID)
        self.token = entry.data["token"]
        self.node_type = None  # "ac" / "fancoil" / "thermostat", from get_state
        self.channel = None
        self.stub = None
        self._event_task = None
        self._token_lock = asyncio.Lock()

        self.data = {
            "online": None,
            "current_temp": None,
            "target_temp": None,
            "min_temp": 5.0,
            "max_temp": 40.0,
            "target_temp_step": 0.5,
            "power_state": None,
            "hvac_mode": None,         # what the device is set to (HVAC_MODE_*)
            "hvac_mode_actual": None,  # what it is doing now, e.g. HEAT while set to AUTO
            "hvac_modes": [],          # modes the device supports
            "fan_speed": None,
            "fan_speeds": [],
            "flap_swing": None,
            "humidity": None,
            "alarms": None,
            "calendar_active": None,
            "wifi_ssid": None,
            "wifi_rssi": None,
            "connection_type": None,
            "fw_version": None,
            "serial_number": None,
        }

    @property
    def _mac_bytes(self) -> bytes:
        """MAC address as the 6 raw bytes used on the wire."""
        return bytes(int(part, 16) for part in self.mac_address.split(":"))

    def _metadata(self) -> list[tuple[str, str]]:
        """Build gRPC call metadata with the current token."""
        return [("authorization", f"Bearer {self.token}")]

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
            return await method(request, metadata=self._metadata(), timeout=COMMAND_TIMEOUT)
        except grpc.aio.AioRpcError as err:
            if not _is_auth_error(err):
                raise
            await self._async_renew_token(token)
            return await method(request, metadata=self._metadata(), timeout=COMMAND_TIMEOUT)

    async def _async_send(self, device_request: pb.DeviceRequest) -> pb.SendDeviceResponse:
        """Send a request to our device node and return the response."""
        request = pb.SendDeviceRequest(
            mac_address=self._mac_bytes,
            node_id=self.node_id,
            request=device_request,
        )
        response = await self._async_call(self.stub.SendDevice, request)
        if response.WhichOneof("type") == "error":
            raise InnovaApiError(
                f"{_enum_name(pb.ResponseErrorCode, response.error.code)}: {response.error.message}"
            )
        return response

    async def _async_setup_channel(self):
        """Set up the gRPC channel."""
        self.channel = grpc.aio.secure_channel(
            f"{GRPC_HOST}:{GRPC_PORT}",
            grpc.ssl_channel_credentials()
        )
        self.stub = pb_grpc.AppServiceStub(self.channel)

    async def _async_resolve_device(self):
        """Look up node_id/home_id for entries created before the v2 API."""
        if self.node_id is not None and self.home_id:
            return

        token = self.token
        try:
            try:
                devices = await get_devices(self.hass, self.token)
            except PermissionError:
                await self._async_renew_token(token)
                devices = await get_devices(self.hass, self.token)
        except (aiohttp.ClientError, TimeoutError, PermissionError) as err:
            raise UpdateFailed(f"Could not list Innova Cloud devices: {err}") from err

        device = next(
            (d for d in devices if (d["mac"] or "").lower() == self.mac_address.lower()), None
        )
        if device is None:
            raise UpdateFailed(f"Device {self.mac_address} not found on the Innova Cloud account")

        self.node_id = device["node_id"]
        self.home_id = device["home_id"]
        self.hass.config_entries.async_update_entry(
            self.entry,
            data={**self.entry.data, CONF_NODE_ID: self.node_id, CONF_HOME_ID: self.home_id},
        )
        _LOGGER.info("Resolved %s to node %s in home %s", self.mac_address, self.node_id, self.home_id)

    async def _fetch_status(self):
        """Fetch the full device state and merge it into self.data."""
        response = await self._async_send(
            pb.DeviceRequest(shared=pb.SharedRequest(get_state=pb.SharedRequest.GetState()))
        )
        state = response.device.shared.state

        if state.HasField("gateway"):
            self._apply_gateway(state.gateway)

        node = state.nodes.get(self.node_id)
        if node is None:
            raise InnovaApiError(f"Node {self.node_id} missing from device state (nodes: {list(state.nodes)})")

        kind = node.WhichOneof("type")
        if kind == "error":
            _LOGGER.warning("Device reports node error: %s", _enum_name(pb.NodeErrorCode, node.error.code))
            self.data["online"] = False
            return
        if kind not in CLIMATE_NODE_TYPES:
            raise InnovaApiError(f"Unsupported node type: {kind}")

        self.node_type = kind
        s = getattr(node, kind)
        self.data["online"] = True
        self.data["power_state"] = s.power
        self.data["current_temp"] = round(s.air_temperature, 1)
        self.data["alarms"] = s.alarms

        if s.HasField("temperature_setpoint"):
            sp = s.temperature_setpoint
            self.data["target_temp"] = round(sp.value, 1)
            self.data["min_temp"] = sp.min or 5.0
            self.data["max_temp"] = sp.max or 40.0
            self.data["target_temp_step"] = sp.step or 0.5

        if s.HasField("hvac_mode"):
            self.data["hvac_mode"] = s.hvac_mode.value
            self.data["hvac_mode_actual"] = s.hvac_mode.actual_value
            self.data["hvac_modes"] = list(s.hvac_mode.capabilities)

        if s.HasField("fan_speed"):
            self.data["fan_speed"] = s.fan_speed.value
            self.data["fan_speeds"] = list(s.fan_speed.capabilities)

        if s.HasField("flap_swing"):
            self.data["flap_swing"] = s.flap_swing

        if s.HasField("air_humidity"):
            self.data["humidity"] = round(s.air_humidity, 1)

        if s.HasField("operation_mode"):
            self.data["calendar_active"] = s.operation_mode.active == OPERATION_MODE_CALENDAR

        _LOGGER.debug("State loaded: %s", self.data)

    def _apply_gateway(self, gateway):
        """Merge gateway (IoT module) info into self.data."""
        if gateway.firmware_version_code:
            self.data["fw_version"] = gateway.firmware_version_code
        if gateway.HasField("serial_number"):
            self.data["serial_number"] = gateway.serial_number
        if gateway.HasField("connection"):
            connection = gateway.connection
            if connection.HasField("wifi"):
                self.data["connection_type"] = "WiFi"
                if connection.wifi.HasField("network"):
                    self.data["wifi_ssid"] = connection.wifi.network.ssid
                    self.data["wifi_rssi"] = connection.wifi.network.rssi
            elif connection.HasField("ethernet"):
                self.data["connection_type"] = "Ethernet"

    async def _listen_events(self):
        """Listen to the home's event stream in the background."""
        _LOGGER.info("Starting event listener for home %s", self.home_id)

        retry_delay = 5  # Start with 5 seconds
        max_retry_delay = 60  # Max 60 seconds between retries
        request = pb.SubscribeEventsRequest(home_id=uuid.UUID(self.home_id).bytes)

        while True:
            token = self.token
            try:
                _LOGGER.debug("Subscribing to home events...")
                async for event in self.stub.SubscribeEvents(request, metadata=self._metadata()):
                    self._process_event(event)
                    # Reset retry delay on successful event processing
                    retry_delay = 5
                _LOGGER.debug("Event stream ended by server")

            except asyncio.CancelledError:
                _LOGGER.info("Event listener cancelled")
                raise
            except Exception as err:
                if _is_auth_error(err):
                    try:
                        # Reconnect with the new token after the (backed-off) delay below,
                        # so a server that keeps rejecting tokens doesn't cause a login storm
                        await self._async_renew_token(token)
                    except ConfigEntryAuthFailed as auth_err:
                        _LOGGER.error("Event stream stopped: %s", auth_err)
                        self.entry.async_start_reauth(self.hass)
                        return
                    except UpdateFailed as renew_err:
                        _LOGGER.warning("%s", renew_err)
                else:
                    _LOGGER.error("Event stream error: %s", err, exc_info=True)

            _LOGGER.info("Reconnecting to event stream in %d seconds...", retry_delay)
            await asyncio.sleep(retry_delay)
            # Exponential backoff with max limit
            retry_delay = min(retry_delay * 2, max_retry_delay)

    def _process_event(self, event: pb.Event):
        """Apply an event for our device node to self.data."""
        if event.WhichOneof("type") != "device":
            return
        device = event.device
        if device.mac_address != self._mac_bytes or device.node_id != self.node_id:
            return

        ev = device.event
        kind = ev.WhichOneof("type")
        _LOGGER.debug("Received event: %s", ev)

        if kind == "system":
            system = ev.system.WhichOneof("type")
            if system == "connection_lost":
                self.data["online"] = False
            elif system == "connection_established":
                self.data["online"] = True
                # The device may have changed while offline; re-sync the full state
                self.hass.async_create_task(self.async_request_refresh())
            else:
                return
        elif kind == "device":
            node_kind = ev.device.WhichOneof("type")
            if node_kind not in CLIMATE_NODE_TYPES:
                return
            e = getattr(ev.device, node_kind)

            if e.HasField("power"):
                self.data["power_state"] = e.power
            if e.HasField("air_temperature"):
                self.data["current_temp"] = round(e.air_temperature, 1)
            if e.HasField("temperature_setpoint"):
                sp = e.temperature_setpoint
                if sp.HasField("value"):
                    self.data["target_temp"] = round(sp.value, 1)
                if sp.HasField("min") and sp.min:
                    self.data["min_temp"] = sp.min
                if sp.HasField("max") and sp.max:
                    self.data["max_temp"] = sp.max
                if sp.HasField("step") and sp.step:
                    self.data["target_temp_step"] = sp.step
            if e.HasField("hvac_mode"):
                self.data["hvac_mode"] = e.hvac_mode
                # Events don't carry the actual mode; outside AUTO it equals the set mode,
                # in AUTO the next full state poll fills it in
                self.data["hvac_mode_actual"] = e.hvac_mode if e.hvac_mode != HVAC_MODE_AUTO else None
            if e.HasField("fan_speed"):
                self.data["fan_speed"] = e.fan_speed
            if e.HasField("flap_swing"):
                self.data["flap_swing"] = e.flap_swing
            if e.HasField("air_humidity"):
                self.data["humidity"] = round(e.air_humidity, 1)
            if e.HasField("operation_mode"):
                self.data["calendar_active"] = e.operation_mode.active == OPERATION_MODE_CALENDAR
            if e.HasField("alarms"):
                self.data["alarms"] = e.alarms
            self.data["online"] = True
        else:
            return

        # Create a new dict copy to ensure Home Assistant detects the change
        self.async_set_updated_data(dict(self.data))

    async def _async_update_data(self):
        """Fetch the full device state; real-time changes arrive via the event stream."""
        if self.channel is None:
            await self._async_setup_channel()

        await self._async_resolve_device()

        try:
            await self._fetch_status()
        except grpc.aio.AioRpcError as err:
            raise UpdateFailed(f"Failed to fetch device state: {err.code().name} {err.details()}") from err
        except InnovaApiError as err:
            raise UpdateFailed(f"Failed to fetch device state: {err}") from err

        if self._event_task is None or self._event_task.done():
            self._event_task = self.entry.async_create_background_task(
                self.hass, self._listen_events(), f"{DOMAIN}_events_{self.mac_address}"
            )

        return dict(self.data)

    async def _async_set_state(self, optimistic: dict, **fields) -> None:
        """Send a set_state command, optimistically applying `optimistic` to self.data.

        If the command fails the optimistic update is rolled back, so HA does not
        show a state the device never received.
        """
        node_type = self.node_type or "fancoil"
        request = pb.DeviceRequest(
            **{node_type: pb.ClimateRequest(set_state=pb.ClimateRequest.SetState(**fields))}
        )

        old_state = {key: self.data.get(key) for key in optimistic}
        self.data.update(optimistic)
        self.async_set_updated_data(dict(self.data))

        try:
            await self._async_send(request)
        except Exception as err:
            self.data.update(old_state)
            self.async_set_updated_data(dict(self.data))
            if isinstance(err, ConfigEntryAuthFailed):
                self.entry.async_start_reauth(self.hass)
            raise HomeAssistantError(f"Innova Cloud command {fields} failed: {err}") from err

        _LOGGER.debug("Sent set_state %s", fields)

    async def async_set_temperature(self, temperature: float) -> None:
        """Set target temperature."""
        await self._async_set_state({"target_temp": temperature}, temperature_setpoint=temperature)

    async def async_set_power(self, power_on: bool) -> None:
        """Set power state."""
        await self._async_set_state({"power_state": power_on}, power=power_on)

    async def async_set_hvac_mode(self, mode: int) -> None:
        """Turn on and set the HVAC mode (HVAC_MODE_*) in a single command."""
        await self._async_set_state(
            {"power_state": True, "hvac_mode": mode, "hvac_mode_actual": None if mode == HVAC_MODE_AUTO else mode},
            power=True,
            hvac_mode=mode,
        )

    async def async_set_fan_speed(self, speed: int) -> None:
        """Set fan speed (FAN_SPEED_*)."""
        await self._async_set_state({"fan_speed": speed}, fan_speed=speed)

    async def async_set_flap_swing(self, swing: bool) -> None:
        """Turn the air flap swing on or off."""
        await self._async_set_state({"flap_swing": swing}, flap_swing=swing)

    async def async_reboot(self) -> None:
        """Reboot the device."""
        try:
            await self._async_send(
                pb.DeviceRequest(system=pb.SystemRequest(reboot=pb.SystemRequest.Reboot()))
            )
        except Exception as err:
            raise HomeAssistantError(f"Innova Cloud reboot failed: {err}") from err

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
