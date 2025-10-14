"""Number platform for Innova Cloud."""
import logging

from homeassistant.components.number import NumberEntity, NumberMode
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
    """Set up Innova Cloud number platform."""
    coordinator: InnovaHeaterCoordinator = hass.data[DOMAIN][entry.entry_id]
    
    entities = []
    
    # Add flap control if device has flap support
    if coordinator.data.get("has_flap"):
        entities.append(InnovaHeaterFlapNumber(coordinator, entry))
    
    if entities:
        async_add_entities(entities)


class InnovaHeaterFlapNumber(CoordinatorEntity, NumberEntity):
    """Representation of flap position control."""

    _attr_has_entity_name = True
    _attr_name = "Flap Position"
    _attr_icon = "mdi:window-shutter"
    _attr_mode = NumberMode.SLIDER
    _attr_native_min_value = 0
    _attr_native_max_value = 7  # Most devices have 0-7 flap positions
    _attr_native_step = 1

    def __init__(
        self,
        coordinator: InnovaHeaterCoordinator,
        entry: ConfigEntry,
    ) -> None:
        """Initialize the number entity."""
        super().__init__(coordinator)
        self._attr_unique_id = f"{entry.data['mac_address']}_flap_control"
        self._attr_device_info = {
            "identifiers": {(DOMAIN, entry.data["mac_address"])},
        }

    @property
    def native_value(self) -> float | None:
        """Return the current flap position."""
        return self.coordinator.data.get("flap")
    
    @property
    def available(self) -> bool:
        """Return if entity is available."""
        return self.coordinator.data.get("has_flap", False)
    
    async def async_set_native_value(self, value: float) -> None:
        """Set new flap position."""
        await self.coordinator.async_set_flap(int(value))
        await self.coordinator.async_request_refresh()
