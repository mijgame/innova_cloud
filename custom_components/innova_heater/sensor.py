"""Sensor platform for Innova Cloud."""
import logging

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorStateClass,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import UnitOfTemperature, SIGNAL_STRENGTH_DECIBELS_MILLIWATT
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN
from .coordinator import InnovaHeaterCoordinator

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Innova Cloud sensor platform."""
    coordinator: InnovaHeaterCoordinator = hass.data[DOMAIN][entry.entry_id]
    
    sensors = [
        InnovaHeaterCurrentTempSensor(coordinator, entry),
        InnovaHeaterTargetTempSensor(coordinator, entry),
        InnovaHeaterOperationModeSensor(coordinator, entry),
        InnovaHeaterConnectionTypeSensor(coordinator, entry),
    ]
    
    # Add diagnostic/maintenance sensors
    if coordinator.data.get("fw_version") is not None:
        sensors.append(InnovaHeaterFirmwareVersionSensor(coordinator, entry))
    
    if coordinator.data.get("serial_number") is not None:
        sensors.append(InnovaHeaterSerialNumberSensor(coordinator, entry))
    
    # Add WiFi sensors if WiFi connection is detected
    if coordinator.data.get("connection_type") == "WiFi":
        sensors.extend([
            InnovaHeaterWiFiSSIDSensor(coordinator, entry),
            InnovaHeaterWiFiRSSISensor(coordinator, entry),
        ])
    
    # Add flap sensor if device has flap
    if coordinator.data.get("has_flap"):
        sensors.append(InnovaHeaterFlapSensor(coordinator, entry))
    
    async_add_entities(sensors)


class InnovaHeaterCurrentTempSensor(CoordinatorEntity, SensorEntity):
    """Representation of current temperature sensor."""

    _attr_has_entity_name = True
    _attr_name = "Current Temperature"
    _attr_device_class = SensorDeviceClass.TEMPERATURE
    _attr_state_class = SensorStateClass.MEASUREMENT
    _attr_native_unit_of_measurement = UnitOfTemperature.CELSIUS

    def __init__(
        self,
        coordinator: InnovaHeaterCoordinator,
        entry: ConfigEntry,
    ) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator)
        self._attr_unique_id = f"{entry.data['mac_address']}_current_temp"
        self._attr_device_info = {
            "identifiers": {(DOMAIN, entry.data["mac_address"])},
        }

    @property
    def native_value(self) -> float | None:
        """Return the state of the sensor."""
        return self.coordinator.data.get("current_temp")


class InnovaHeaterTargetTempSensor(CoordinatorEntity, SensorEntity):
    """Representation of target temperature sensor."""

    _attr_has_entity_name = True
    _attr_name = "Target Temperature"
    _attr_device_class = SensorDeviceClass.TEMPERATURE
    _attr_state_class = SensorStateClass.MEASUREMENT
    _attr_native_unit_of_measurement = UnitOfTemperature.CELSIUS

    def __init__(
        self,
        coordinator: InnovaHeaterCoordinator,
        entry: ConfigEntry,
    ) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator)
        self._attr_unique_id = f"{entry.data['mac_address']}_target_temp"
        self._attr_device_info = {
            "identifiers": {(DOMAIN, entry.data["mac_address"])},
        }

    @property
    def native_value(self) -> float | None:
        """Return the state of the sensor."""
        return self.coordinator.data.get("target_temp")


class InnovaHeaterWiFiSSIDSensor(CoordinatorEntity, SensorEntity):
    """Representation of WiFi SSID sensor."""

    _attr_has_entity_name = True
    _attr_name = "WiFi SSID"
    _attr_icon = "mdi:wifi"

    def __init__(
        self,
        coordinator: InnovaHeaterCoordinator,
        entry: ConfigEntry,
    ) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator)
        self._attr_unique_id = f"{entry.data['mac_address']}_wifi_ssid"
        self._attr_device_info = {
            "identifiers": {(DOMAIN, entry.data["mac_address"])},
        }

    @property
    def native_value(self) -> str | None:
        """Return the state of the sensor."""
        return self.coordinator.data.get("wifi_ssid")
    
    @property
    def available(self) -> bool:
        """Return if entity is available."""
        return self.coordinator.data.get("wifi_ssid") is not None


class InnovaHeaterWiFiRSSISensor(CoordinatorEntity, SensorEntity):
    """Representation of WiFi RSSI sensor."""

    _attr_has_entity_name = True
    _attr_name = "WiFi Signal"
    _attr_device_class = SensorDeviceClass.SIGNAL_STRENGTH
    _attr_state_class = SensorStateClass.MEASUREMENT
    _attr_native_unit_of_measurement = SIGNAL_STRENGTH_DECIBELS_MILLIWATT
    _attr_icon = "mdi:wifi-strength-2"

    def __init__(
        self,
        coordinator: InnovaHeaterCoordinator,
        entry: ConfigEntry,
    ) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator)
        self._attr_unique_id = f"{entry.data['mac_address']}_wifi_rssi"
        self._attr_device_info = {
            "identifiers": {(DOMAIN, entry.data["mac_address"])},
        }

    @property
    def native_value(self) -> int | None:
        """Return the state of the sensor."""
        return self.coordinator.data.get("wifi_rssi")
    
    @property
    def available(self) -> bool:
        """Return if entity is available."""
        return self.coordinator.data.get("wifi_rssi") is not None


class InnovaHeaterOperationModeSensor(CoordinatorEntity, SensorEntity):
    """Representation of operation mode sensor."""

    _attr_has_entity_name = True
    _attr_name = "Operation Mode"
    _attr_icon = "mdi:thermostat-auto"
    
    MODE_NAMES = {
        0: "Auto",
        1: "Heat",
        2: "Cool",
        3: "Fan Only",
        4: "Dry",
    }

    def __init__(
        self,
        coordinator: InnovaHeaterCoordinator,
        entry: ConfigEntry,
    ) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator)
        self._attr_unique_id = f"{entry.data['mac_address']}_operation_mode"
        self._attr_device_info = {
            "identifiers": {(DOMAIN, entry.data["mac_address"])},
        }

    @property
    def native_value(self) -> str | None:
        """Return the state of the sensor."""
        mode = self.coordinator.data.get("operation_mode")
        if mode is not None:
            return self.MODE_NAMES.get(mode, f"Unknown ({mode})")
        return None
    
    @property
    def available(self) -> bool:
        """Return if entity is available."""
        return self.coordinator.data.get("operation_mode") is not None


class InnovaHeaterConnectionTypeSensor(CoordinatorEntity, SensorEntity):
    """Representation of connection type sensor."""

    _attr_has_entity_name = True
    _attr_name = "Connection Type"
    _attr_icon = "mdi:connection"

    def __init__(
        self,
        coordinator: InnovaHeaterCoordinator,
        entry: ConfigEntry,
    ) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator)
        self._attr_unique_id = f"{entry.data['mac_address']}_connection_type"
        self._attr_device_info = {
            "identifiers": {(DOMAIN, entry.data["mac_address"])},
        }

    @property
    def native_value(self) -> str | None:
        """Return the state of the sensor."""
        return self.coordinator.data.get("connection_type")
    
    @property
    def available(self) -> bool:
        """Return if entity is available."""
        return self.coordinator.data.get("connection_type") is not None


class InnovaHeaterFlapSensor(CoordinatorEntity, SensorEntity):
    """Representation of flap position sensor."""

    _attr_has_entity_name = True
    _attr_name = "Flap Position"
    _attr_icon = "mdi:window-shutter"

    def __init__(
        self,
        coordinator: InnovaHeaterCoordinator,
        entry: ConfigEntry,
    ) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator)
        self._attr_unique_id = f"{entry.data['mac_address']}_flap"
        self._attr_device_info = {
            "identifiers": {(DOMAIN, entry.data["mac_address"])},
        }

    @property
    def native_value(self) -> int | None:
        """Return the state of the sensor."""
        return self.coordinator.data.get("flap")
    
    @property
    def available(self) -> bool:
        """Return if entity is available."""
        return self.coordinator.data.get("flap") is not None


class InnovaHeaterFirmwareVersionSensor(CoordinatorEntity, SensorEntity):
    """Representation of firmware version sensor."""

    _attr_has_entity_name = True
    _attr_name = "Firmware Version"
    _attr_icon = "mdi:chip"
    _attr_entity_category = "diagnostic"

    def __init__(
        self,
        coordinator: InnovaHeaterCoordinator,
        entry: ConfigEntry,
    ) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator)
        self._attr_unique_id = f"{entry.data['mac_address']}_firmware_version"
        self._attr_device_info = {
            "identifiers": {(DOMAIN, entry.data["mac_address"])},
        }

    @property
    def native_value(self) -> str | None:
        """Return the firmware version."""
        fw_version = self.coordinator.data.get("fw_version")
        if fw_version is not None:
            # Format version number (e.g., 12345 -> "1.23.45")
            if isinstance(fw_version, int):
                return f"{fw_version // 10000}.{(fw_version // 100) % 100}.{fw_version % 100}"
            return str(fw_version)
        return None
    
    @property
    def available(self) -> bool:
        """Return if entity is available."""
        return self.coordinator.data.get("fw_version") is not None


class InnovaHeaterSerialNumberSensor(CoordinatorEntity, SensorEntity):
    """Representation of serial number sensor."""

    _attr_has_entity_name = True
    _attr_name = "Serial Number"
    _attr_icon = "mdi:identifier"
    _attr_entity_category = "diagnostic"

    def __init__(
        self,
        coordinator: InnovaHeaterCoordinator,
        entry: ConfigEntry,
    ) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator)
        self._attr_unique_id = f"{entry.data['mac_address']}_serial_number"
        self._attr_device_info = {
            "identifiers": {(DOMAIN, entry.data["mac_address"])},
        }

    @property
    def native_value(self) -> str | None:
        """Return the serial number."""
        return self.coordinator.data.get("serial_number")
    
    @property
    def available(self) -> bool:
        """Return if entity is available."""
        return self.coordinator.data.get("serial_number") is not None
