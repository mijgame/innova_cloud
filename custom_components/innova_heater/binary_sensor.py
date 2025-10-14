"""Binary sensor platform for Innova Cloud."""
import logging

from homeassistant.components.binary_sensor import (
    BinarySensorEntity,
    BinarySensorDeviceClass,
)
from homeassistant.config_entries import ConfigEntry
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
    """Set up Innova Cloud binary sensor platform."""
    coordinator: InnovaHeaterCoordinator = hass.data[DOMAIN][entry.entry_id]
    
    sensors = []
    
    # Add calendar sensor if calendar data is available
    if coordinator.data.get("calendar_active") is not None:
        sensors.append(InnovaHeaterCalendarSensor(coordinator, entry))
    
    # Add keyboard lock sensor if available
    if coordinator.data.get("keyboard_lock") is not None:
        sensors.append(InnovaHeaterKeyboardLockSensor(coordinator, entry))
    
    # Add hotel mode sensor if available
    if coordinator.data.get("hotel_mode") is not None:
        sensors.append(InnovaHeaterHotelModeSensor(coordinator, entry))
    
    if sensors:
        async_add_entities(sensors)


class InnovaHeaterCalendarSensor(CoordinatorEntity, BinarySensorEntity):
    """Representation of calendar active sensor."""

    _attr_has_entity_name = True
    _attr_name = "Calendar Active"
    _attr_icon = "mdi:calendar-clock"

    def __init__(
        self,
        coordinator: InnovaHeaterCoordinator,
        entry: ConfigEntry,
    ) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator)
        self._attr_unique_id = f"{entry.data['mac_address']}_calendar_active"
        self._attr_device_info = {
            "identifiers": {(DOMAIN, entry.data["mac_address"])},
        }

    @property
    def is_on(self) -> bool | None:
        """Return true if calendar is active."""
        return self.coordinator.data.get("calendar_active")
    
    @property
    def available(self) -> bool:
        """Return if entity is available."""
        return self.coordinator.data.get("calendar_active") is not None


class InnovaHeaterKeyboardLockSensor(CoordinatorEntity, BinarySensorEntity):
    """Representation of keyboard lock sensor."""

    _attr_has_entity_name = True
    _attr_name = "Keyboard Lock"
    _attr_device_class = BinarySensorDeviceClass.LOCK
    _attr_icon = "mdi:keyboard-off"

    def __init__(
        self,
        coordinator: InnovaHeaterCoordinator,
        entry: ConfigEntry,
    ) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator)
        self._attr_unique_id = f"{entry.data['mac_address']}_keyboard_lock"
        self._attr_device_info = {
            "identifiers": {(DOMAIN, entry.data["mac_address"])},
        }

    @property
    def is_on(self) -> bool | None:
        """Return true if keyboard is locked."""
        return self.coordinator.data.get("keyboard_lock")
    
    @property
    def available(self) -> bool:
        """Return if entity is available."""
        return self.coordinator.data.get("keyboard_lock") is not None


class InnovaHeaterHotelModeSensor(CoordinatorEntity, BinarySensorEntity):
    """Representation of hotel mode sensor."""

    _attr_has_entity_name = True
    _attr_name = "Hotel Mode"
    _attr_icon = "mdi:office-building"

    def __init__(
        self,
        coordinator: InnovaHeaterCoordinator,
        entry: ConfigEntry,
    ) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator)
        self._attr_unique_id = f"{entry.data['mac_address']}_hotel_mode"
        self._attr_device_info = {
            "identifiers": {(DOMAIN, entry.data["mac_address"])},
        }

    @property
    def is_on(self) -> bool | None:
        """Return true if hotel mode is active."""
        return self.coordinator.data.get("hotel_mode")
    
    @property
    def available(self) -> bool:
        """Return if entity is available."""
        return self.coordinator.data.get("hotel_mode") is not None
