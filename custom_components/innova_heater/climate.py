"""Climate platform for Innova Cloud."""
import logging
from typing import Any

from homeassistant.components.climate import (
    ClimateEntity,
    ClimateEntityFeature,
    HVACMode,
    HVACAction,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import ATTR_TEMPERATURE, UnitOfTemperature
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN, CONF_DEVICE_TYPE, DEVICE_TYPE_MODES, DEVICE_TYPE_FANCOIL
from .coordinator import InnovaHeaterCoordinator

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Innova Cloud climate platform."""
    coordinator: InnovaHeaterCoordinator = hass.data[DOMAIN][entry.entry_id]
    
    async_add_entities([InnovaHeaterClimate(coordinator, entry)])


class InnovaHeaterClimate(CoordinatorEntity, ClimateEntity):
    """Representation of an Innova Cloud climate device."""

    _attr_has_entity_name = True
    _attr_name = None
    _attr_temperature_unit = UnitOfTemperature.CELSIUS
    _attr_supported_features = (
        ClimateEntityFeature.TARGET_TEMPERATURE |
        ClimateEntityFeature.TURN_ON |
        ClimateEntityFeature.TURN_OFF |
        ClimateEntityFeature.FAN_MODE
    )
    _attr_min_temp = 5.0  # Will be updated from device
    _attr_max_temp = 40.0  # Will be updated from device
    _attr_target_temperature_step = 0.5  # Will be updated from device
    
    # Operation mode mapping (from APK)
    OPERATION_MODE_MAP = {
        HVACMode.AUTO: 0,
        HVACMode.HEAT: 1,
        HVACMode.COOL: 2,
        HVACMode.FAN_ONLY: 3,
        HVACMode.DRY: 4,
    }
    
    OPERATION_MODE_REVERSE = {v: k for k, v in OPERATION_MODE_MAP.items()}
    
    # Fan modes (Fancoil: Auto=0, Night=1, Max=2)
    _attr_fan_modes = ["auto", "night", "max"]

    def __init__(
        self,
        coordinator: InnovaHeaterCoordinator,
        entry: ConfigEntry,
    ) -> None:
        """Initialize the climate device."""
        super().__init__(coordinator)
        self._attr_unique_id = f"{entry.data['mac_address']}_climate"
        
        # Get device type and set supported modes
        device_type = entry.data.get(CONF_DEVICE_TYPE, DEVICE_TYPE_FANCOIL)
        self._attr_hvac_modes = DEVICE_TYPE_MODES.get(device_type, DEVICE_TYPE_MODES[DEVICE_TYPE_FANCOIL])
        
        self._attr_device_info = {
            "identifiers": {(DOMAIN, entry.data["mac_address"])},
            "name": entry.data.get("name", "Innova Cloud"),
            "manufacturer": "Innova",
            "model": device_type.replace("_", " ").title(),
            "serial_number": entry.data["mac_address"],
        }
    
    def _update_device_info(self) -> None:
        """Update device info with firmware version from coordinator."""
        if fw_version := self.coordinator.data.get("fw_version"):
            if self._attr_device_info:
                self._attr_device_info["sw_version"] = str(fw_version)
    
    async def async_added_to_hass(self) -> None:
        """When entity is added to hass."""
        await super().async_added_to_hass()
        self._update_device_info()
    
    def _handle_coordinator_update(self) -> None:
        """Handle updated data from the coordinator."""
        self._update_device_info()
        super()._handle_coordinator_update()

    @property
    def min_temp(self) -> float:
        """Return the minimum temperature."""
        return self.coordinator.data.get("min_temp", 5.0)
    
    @property
    def max_temp(self) -> float:
        """Return the maximum temperature."""
        return self.coordinator.data.get("max_temp", 40.0)
    
    @property
    def target_temperature_step(self) -> float:
        """Return the supported step of target temperature."""
        return self.coordinator.data.get("target_temp_step", 0.5)

    @property
    def available(self) -> bool:
        """Return if entity is available."""
        # Entity is available if the last cloud sync succeeded and we have any temperature data
        return super().available and (
            self.coordinator.data.get("current_temp") is not None
            or self.coordinator.data.get("target_temp") is not None
        )

    @property
    def current_temperature(self) -> float | None:
        """Return the current temperature."""
        return self.coordinator.data.get("current_temp")

    @property
    def target_temperature(self) -> float | None:
        """Return the temperature we try to reach."""
        return self.coordinator.data.get("target_temp")

    @property
    def hvac_mode(self) -> HVACMode:
        """Return current HVAC mode."""
        power_state = self.coordinator.data.get("power_state")
        
        # If power state is not True, device is off
        if power_state is not True:
            return HVACMode.OFF
        
        # Device is on - get operation mode and map to HVAC mode
        operation_mode = self.coordinator.data.get("operation_mode")
        if operation_mode is not None:
            return self.OPERATION_MODE_REVERSE.get(operation_mode, HVACMode.HEAT)
        
        # Default to HEAT if mode is unknown
        return HVACMode.HEAT
    
    @property
    def hvac_action(self) -> HVACAction | None:
        """Return current HVAC action based on mode and temperature."""
        if not self.coordinator.data.get("power_state"):
            return HVACAction.OFF
        
        operation_mode = self.coordinator.data.get("operation_mode")
        current_temp = self.current_temperature
        target_temp = self.target_temperature
        
        # Determine action based on operation mode
        if operation_mode == 1:  # Heat mode
            # Show heating if target is higher than current (with small buffer)
            if current_temp is not None and target_temp is not None:
                if target_temp > current_temp + 0.2:
                    return HVACAction.HEATING
            return HVACAction.IDLE
            
        elif operation_mode == 2:  # Cool mode
            # Show cooling if target is lower than current (with small buffer)
            if current_temp is not None and target_temp is not None:
                if target_temp < current_temp - 0.2:
                    return HVACAction.COOLING
            return HVACAction.IDLE
            
        elif operation_mode == 3:  # Fan only
            return HVACAction.FAN
            
        elif operation_mode == 4:  # Dry mode
            return HVACAction.DRYING
        
        # Auto mode or unknown - show idle
        return HVACAction.IDLE

    async def async_set_temperature(self, **kwargs: Any) -> None:
        """Set new target temperature."""
        if (temperature := kwargs.get(ATTR_TEMPERATURE)) is None:
            return

        await self.coordinator.async_set_temperature(temperature)

    async def async_set_hvac_mode(self, hvac_mode: HVACMode) -> None:
        """Set new HVAC mode."""
        if hvac_mode == HVACMode.OFF:
            await self.coordinator.async_set_power(False)
        else:
            # Turn on if off
            if not self.coordinator.data.get("power_state"):
                await self.coordinator.async_set_power(True)
            
            # Set operation mode
            if hvac_mode in self.OPERATION_MODE_MAP:
                operation_mode = self.OPERATION_MODE_MAP[hvac_mode]
                await self.coordinator.async_set_operation_mode(operation_mode)
    
    @property
    def fan_mode(self) -> str | None:
        """Return the current fan mode."""
        fan_speed = self.coordinator.data.get("fan_speed")
        if fan_speed is None:
            return None
        
        # Map numeric fan speed to mode names (Fancoil: Auto=0, Night=1, Max=2)
        fan_mode_map = {
            0: "auto",
            1: "night",
            2: "max",
        }
        return fan_mode_map.get(fan_speed, "auto")
    
    async def async_set_fan_mode(self, fan_mode: str) -> None:
        """Set new fan mode."""
        # Map fan mode names to numeric values (Fancoil: Auto=0, Night=1, Max=2)
        fan_speed_map = {
            "auto": 0,
            "night": 1,
            "max": 2,
        }
        
        if fan_mode in fan_speed_map:
            await self.coordinator.async_set_fan_speed(fan_speed_map[fan_mode])

    async def async_turn_on(self) -> None:
        """Turn the entity on."""
        # Restore last mode or default to AUTO
        last_mode = self.coordinator.data.get("operation_mode")
        if last_mode in self.OPERATION_MODE_REVERSE:
            hvac_mode = self.OPERATION_MODE_REVERSE[last_mode]
        else:
            hvac_mode = HVACMode.AUTO
        await self.async_set_hvac_mode(hvac_mode)

    async def async_turn_off(self) -> None:
        """Turn the entity off."""
        await self.async_set_hvac_mode(HVACMode.OFF)
