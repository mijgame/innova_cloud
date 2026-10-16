"""Button platform for Innova Cloud."""
import logging

from homeassistant.components.button import ButtonEntity, ButtonDeviceClass
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
    """Set up Innova Cloud button platform."""
    coordinator: InnovaHeaterCoordinator = hass.data[DOMAIN][entry.entry_id]
    
    async_add_entities([
        InnovaHeaterRebootButton(coordinator, entry),
    ])


class InnovaHeaterRebootButton(CoordinatorEntity, ButtonEntity):
    """Representation of device reboot button."""

    _attr_has_entity_name = True
    _attr_name = "Reboot Device"
    _attr_device_class = ButtonDeviceClass.RESTART
    _attr_icon = "mdi:restart"

    def __init__(
        self,
        coordinator: InnovaHeaterCoordinator,
        entry: ConfigEntry,
    ) -> None:
        """Initialize the button entity."""
        super().__init__(coordinator)
        self._attr_unique_id = f"{entry.data['mac_address']}_reboot"
        self._attr_device_info = {
            "identifiers": {(DOMAIN, entry.data["mac_address"])},
        }

    async def async_press(self) -> None:
        """Handle button press - reboot the device."""
        await self.coordinator.async_reboot()
        _LOGGER.info("Device reboot initiated")
