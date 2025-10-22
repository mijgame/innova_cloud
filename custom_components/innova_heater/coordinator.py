"""Data coordinator for Innova Cloud."""
import asyncio
import logging
import struct
from datetime import timedelta

import grpc
from google.protobuf import empty_pb2

from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed
from homeassistant.config_entries import ConfigEntry

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
)
from . import controls_pb2, controls_pb2_grpc

_LOGGER = logging.getLogger(__name__)


class InnovaHeaterCoordinator(DataUpdateCoordinator):
    """Coordinator to manage Innova Cloud data."""

    def __init__(self, hass: HomeAssistant, entry: ConfigEntry) -> None:
        """Initialize coordinator."""
        _LOGGER.info("Initializing InnovaHeaterCoordinator for MAC: %s", entry.data.get("mac_address"))
        
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
            "hotel_mode": None,
            "temperature_unit": None,
            "wifi_ssid": None,
            "wifi_rssi": None,
            "connection_type": None,
            "fw_version": None,
            "serial_number": None,
        }
        
        _LOGGER.info("Coordinator initialized with MAC: %s, Token: %s...", self.mac_address, self.token[:20] if self.token else "None")

    async def _async_setup(self):
        """Set up the gRPC connection."""
        try:
            credentials = grpc.ssl_channel_credentials()
            self.channel = grpc.aio.secure_channel(
                f"{GRPC_HOST}:{GRPC_PORT}",
                credentials
            )
            self.stub = controls_pb2_grpc.ControlsStub(self.channel)
            
            # Fetch initial device status using blocking call (like the app does)
            await self._fetch_initial_status()
            
            # Start event listener for real-time updates
            self._event_task = asyncio.create_task(self._listen_events())
            
        except Exception as err:
            _LOGGER.error("Failed to setup gRPC connection: %s", err)
            raise UpdateFailed(f"Setup failed: {err}")
    
    async def _fetch_initial_status(self):
        """Fetch initial device status."""
        try:
            metadata = [
                ("mac_address", self.mac_address),
                ("authorization", f"Bearer {self.token}"),
            ]
            
            _LOGGER.info("Fetching initial device status for MAC: %s", self.mac_address)
            empty = empty_pb2.Empty()
            
            # Call GetDeviceStatus
            status = await self.stub.GetDeviceStatus(empty, metadata=metadata)
            
            if not status.HasField('main_status'):
                _LOGGER.warning("No main_status in response")
                return
            
            main = status.main_status
            
            # Store serial number
            if main.serial_number:
                self.data["serial_number"] = main.serial_number
                _LOGGER.info("Device serial: %s", main.serial_number)
            
            _LOGGER.info("Device FW version: %s", main.fw_version if hasattr(main, 'fw_version') else "unknown")
            
            # Check which device type (using oneof field)
            device_status = None
            device_type = main.WhichOneof('device_status')
            
            if device_type == 'fancoil_status':
                device_status = main.fancoil_status
            elif device_type == 'm7_status':
                device_status = main.m7_status
            elif device_type == 'duepuntozero_status':
                device_status = main.duepuntozero_status
            elif device_type == 'waterloop_status':
                device_status = main.waterloop_status
            
            if device_status:
                _LOGGER.info("Device type: %s", device_type)
                
                # Parse available fields
                if hasattr(device_status, 'power_state'):
                    self.data["power_state"] = device_status.power_state
                    _LOGGER.debug("Initial power state: %s", self.data["power_state"])
                
                if hasattr(device_status, 'room_temperature') and device_status.room_temperature > 0:
                    self.data["current_temp"] = device_status.room_temperature / 10.0
                    _LOGGER.debug("Initial current temp: %s°C", self.data["current_temp"])
                    self._initial_data_received = True
                
                if hasattr(device_status, 'temperature_setpoint') and device_status.HasField('temperature_setpoint'):
                    setpoint = device_status.temperature_setpoint
                    self.data["target_temp"] = setpoint.value / 10.0
                    self.data["min_temp"] = setpoint.min / 10.0 if setpoint.min > 0 else 5.0
                    self.data["max_temp"] = setpoint.max / 10.0 if setpoint.max > 0 else 40.0
                    self.data["target_temp_step"] = setpoint.step / 10.0 if setpoint.step > 0 else 0.5
                    _LOGGER.debug("Initial target temp: %s°C (range: %s-%s°C, step: %s°C)", 
                                self.data["target_temp"], self.data["min_temp"], 
                                self.data["max_temp"], self.data["target_temp_step"])
                
                if hasattr(device_status, 'operation_mode'):
                    self.data["operation_mode"] = device_status.operation_mode
                    _LOGGER.debug("Initial operation mode: %s", self.data["operation_mode"])
                
                if hasattr(device_status, 'fan_speed'):
                    self.data["fan_speed"] = device_status.fan_speed
                    _LOGGER.debug("Initial fan speed: %s", self.data["fan_speed"])
                
                # Additional device features
                if hasattr(device_status, 'flap'):
                    self.data["flap"] = device_status.flap
                    _LOGGER.debug("Initial flap position: %s", self.data["flap"])
                
                if hasattr(device_status, 'has_flap'):
                    self.data["has_flap"] = device_status.has_flap
                
                if hasattr(device_status, 'keyboard_lock'):
                    self.data["keyboard_lock"] = device_status.keyboard_lock
                    _LOGGER.debug("Keyboard lock: %s", self.data["keyboard_lock"])
                
                if hasattr(device_status, 'hotel_mode'):
                    self.data["hotel_mode"] = device_status.hotel_mode
                    _LOGGER.debug("Hotel mode: %s", self.data["hotel_mode"])
                
                if hasattr(device_status, 'temperature_unit'):
                    self.data["temperature_unit"] = device_status.temperature_unit
                    _LOGGER.debug("Temperature unit: %s", self.data["temperature_unit"])
                
                # Calendar status
                if hasattr(device_status, 'calendar') and device_status.HasField('calendar'):
                    calendar = device_status.calendar
                    self.data["calendar_active"] = calendar.is_active
                    _LOGGER.debug("Calendar active: %s", self.data["calendar_active"])
                
                _LOGGER.debug("Initial status loaded: %s", self.data)
            else:
                _LOGGER.debug("GetDeviceStatus returned minimal data, waiting for events...")
            
            # Parse IoT status (WiFi, firmware, etc.)
            if status.HasField('iot_status'):
                iot = status.iot_status
                
                if iot.fw_version:
                    self.data["fw_version"] = iot.fw_version
                    _LOGGER.debug("IoT FW version: %s", iot.fw_version)
                
                # Check connection type
                if iot.HasField('wifi'):
                    self.data["connection_type"] = "WiFi"
                    self.data["wifi_ssid"] = iot.wifi.ssid
                    self.data["wifi_rssi"] = iot.wifi.rssi
                    _LOGGER.debug("WiFi: %s (RSSI: %d dBm)", iot.wifi.ssid, iot.wifi.rssi)
                elif iot.HasField('ethernet'):
                    self.data["connection_type"] = "Ethernet"
                    _LOGGER.debug("Connection: Ethernet")
                elif iot.HasField('thread'):
                    self.data["connection_type"] = "Thread"
                    _LOGGER.debug("Connection: Thread")
                
        except Exception as err:
            _LOGGER.error("Failed to fetch initial status: %s", err)
            import traceback
            _LOGGER.error("Traceback: %s", traceback.format_exc())

    async def _listen_events(self):
        """Listen to device events in background."""
        metadata = [
            ("mac_address", self.mac_address),
            ("authorization", f"Bearer {self.token}"),
        ]
        
        _LOGGER.info("Starting event listener for MAC: %s", self.mac_address)
        
        retry_delay = 5  # Start with 5 seconds
        max_retry_delay = 60  # Max 60 seconds between retries
        
        while True:
            try:
                _LOGGER.debug("Subscribing to device events...")
                empty = empty_pb2.Empty()
                async for event in self.stub.SubscribeToDeviceEvents(empty, metadata=metadata):
                    await self._process_event(event)
                    # Reset retry delay on successful event processing
                    retry_delay = 5
                    
            except asyncio.CancelledError:
                _LOGGER.info("Event listener cancelled")
                break
            except Exception as err:
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
        """Fetch data from device - data comes from initial fetch + event stream."""
        _LOGGER.debug("_async_update_data called, channel=%s", "initialized" if self.channel else "None")
        
        if self.channel is None:
            _LOGGER.debug("Channel not initialized, calling _async_setup...")
            await self._async_setup()
            _LOGGER.debug("_async_setup completed")
        
        # Data is fetched during setup and updated via event stream
        # Just return current data
        _LOGGER.debug("Returning current coordinator data: %s", self.data)
        return self.data

    async def async_set_temperature(self, temperature: float) -> None:
        """Set target temperature."""
        try:
            metadata = [
                ("mac_address", self.mac_address),
                ("authorization", f"Bearer {self.token}"),
            ]
            
            temp_value = int(temperature * 10)
            
            request = controls_pb2.SetDeviceValueRequest(
                type=OP_TYPE_SETPOINT,
                value=temp_value
            )
            
            # Optimistic update - immediately update local state
            self.data["target_temp"] = temperature
            self.async_set_updated_data(dict(self.data))
            _LOGGER.debug("Optimistically updated target temp to %.1f°C", temperature)
            
            await self.stub.SetDeviceValue(request, metadata=metadata)
            _LOGGER.info("Set temperature to %.1f°C (value=%d)", temperature, temp_value)
            
        except Exception as err:
            _LOGGER.error("Failed to set temperature: %s", err)
            raise

    async def async_set_power(self, power_on: bool) -> None:
        """Set power state."""
        try:
            metadata = [
                ("mac_address", self.mac_address),
                ("authorization", f"Bearer {self.token}"),
            ]
            
            request = controls_pb2.SetDeviceValueRequest(
                type=OP_TYPE_POWER_STATE,
                value=1 if power_on else 0
            )
            
            # Optimistic update - immediately update local state
            self.data["power_state"] = power_on
            self.async_set_updated_data(dict(self.data))
            _LOGGER.debug("Optimistically updated power state to %s", power_on)
            
            await self.stub.SetDeviceValue(request, metadata=metadata)
            _LOGGER.info("Set power state to %s", "ON" if power_on else "OFF")
            
        except Exception as err:
            _LOGGER.error("Failed to set power: %s", err)
            raise

    async def async_set_operation_mode(self, mode: int) -> None:
        """Set operation mode (0=Auto, 1=Heat, 2=Cool, 3=Fan, 4=Dry)."""
        try:
            metadata = [
                ("mac_address", self.mac_address),
                ("authorization", f"Bearer {self.token}"),
            ]
            
            request = controls_pb2.SetDeviceValueRequest(
                type=OP_TYPE_OPERATION_MODE,
                value=mode
            )
            
            # Optimistic update - immediately update local state
            self.data["operation_mode"] = mode
            self.async_set_updated_data(dict(self.data))
            _LOGGER.debug("Optimistically updated operation mode to %d", mode)
            
            await self.stub.SetDeviceValue(request, metadata=metadata)
            _LOGGER.info("Set operation mode to %d", mode)
            
        except Exception as err:
            _LOGGER.error("Failed to set operation mode: %s", err)
            raise
    
    async def async_set_fan_speed(self, speed: int) -> None:
        """Set fan speed (device-dependent values)."""
        try:
            metadata = [
                ("mac_address", self.mac_address),
                ("authorization", f"Bearer {self.token}"),
            ]
            
            request = controls_pb2.SetDeviceValueRequest(
                type=OP_TYPE_FAN_SPEED,
                value=speed
            )
            
            # Optimistic update - immediately update local state
            self.data["fan_speed"] = speed
            self.async_set_updated_data(dict(self.data))
            _LOGGER.debug("Optimistically updated fan speed to %d", speed)
            
            await self.stub.SetDeviceValue(request, metadata=metadata)
            _LOGGER.info("Set fan speed to %d", speed)
            
        except Exception as err:
            _LOGGER.error("Failed to set fan speed: %s", err)
            raise
    
    async def async_set_flap(self, position: int) -> None:
        """Set flap position (if device has flap support)."""
        try:
            if not self.data.get("has_flap"):
                _LOGGER.warning("Device does not support flap control")
                return
            
            metadata = [
                ("mac_address", self.mac_address),
                ("authorization", f"Bearer {self.token}"),
            ]
            
            request = controls_pb2.SetDeviceValueRequest(
                type=OP_TYPE_FLAP,
                value=position
            )
            
            # Optimistic update - immediately update local state
            self.data["flap"] = position
            self.async_set_updated_data(dict(self.data))
            _LOGGER.debug("Optimistically updated flap position to %d", position)
            
            await self.stub.SetDeviceValue(request, metadata=metadata)
            _LOGGER.info("Set flap position to %d", position)
            
        except Exception as err:
            _LOGGER.error("Failed to set flap: %s", err)
            raise

    async def async_shutdown(self):
        """Shutdown coordinator."""
        _LOGGER.info("Shutting down coordinator for MAC: %s", self.mac_address)
        
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
