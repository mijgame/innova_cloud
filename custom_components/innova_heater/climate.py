"""Climate platform for Innova Cloud."""
import logging
from typing import Any

from homeassistant.components.climate import (
    ClimateEntity,
    ClimateEntityFeature,
    HVACMode,
    HVACAction,
    FAN_AUTO,
    FAN_LOW,
    FAN_MEDIUM,
    FAN_HIGH,
    SWING_OFF,
    SWING_ON,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import ATTR_TEMPERATURE, UnitOfTemperature
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import (
    DOMAIN,
    DEFAULT_HVAC_MODES,
    HVAC_MODE_AUTO,
    HVAC_MODE_HEAT,
    HVAC_MODE_COOL,
    HVAC_MODE_DRY,
    HVAC_MODE_FAN,
    FAN_SPEED_AUTO,
    FAN_SPEED_MIN,
    FAN_SPEED_MID,
    FAN_SPEED_MAX,
    FAN_SPEED_BOOST,
)
from .coordinator import InnovaHeaterCoordinator

_LOGGER = logging.getLogger(__name__)

FAN_BOOST = "boost"

NODE_TYPE_MODELS = {
    "ac": "Air conditioner",
    "fancoil": "Fancoil",
    "thermostat": "Thermostat",
}

HVAC_MODE_MAP = {
    HVACMode.AUTO: HVAC_MODE_AUTO,
    HVACMode.HEAT: HVAC_MODE_HEAT,
    HVACMode.COOL: HVAC_MODE_COOL,
    HVACMode.DRY: HVAC_MODE_DRY,
    HVACMode.FAN_ONLY: HVAC_MODE_FAN,
}
HVAC_MODE_REVERSE = {v: k for k, v in HVAC_MODE_MAP.items()}

FAN_MODE_MAP = {
    FAN_AUTO: FAN_SPEED_AUTO,
    FAN_LOW: FAN_SPEED_MIN,
    FAN_MEDIUM: FAN_SPEED_MID,
    FAN_HIGH: FAN_SPEED_MAX,
    FAN_BOOST: FAN_SPEED_BOOST,
}
FAN_MODE_REVERSE = {v: k for k, v in FAN_MODE_MAP.items()}


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

    def __init__(
        self,
        coordinator: InnovaHeaterCoordinator,
        entry: ConfigEntry,
    ) -> None:
        """Initialize the climate device."""
        super().__init__(coordinator)
        self._attr_unique_id = f"{entry.data['mac_address']}_climate"

        self._attr_device_info = {
            "identifiers": {(DOMAIN, entry.data["mac_address"])},
            "name": entry.data.get("name", "Innova Cloud"),
            "manufacturer": "Innova",
            "serial_number": entry.data["mac_address"],
        }

    def _update_device_info(self) -> None:
        """Update device info from coordinator data."""
        if self._attr_device_info is None:
            return
        if fw_version := self.coordinator.data.get("fw_version"):
            self._attr_device_info["sw_version"] = str(fw_version)
        if model := NODE_TYPE_MODELS.get(self.coordinator.node_type):
            self._attr_device_info["model"] = model

    async def async_added_to_hass(self) -> None:
        """When entity is added to hass."""
        await super().async_added_to_hass()
        self._update_device_info()

    def _handle_coordinator_update(self) -> None:
        """Handle updated data from the coordinator."""
        self._update_device_info()
        super()._handle_coordinator_update()

    @property
    def supported_features(self) -> ClimateEntityFeature:
        """Return the features supported by the device."""
        features = (
            ClimateEntityFeature.TARGET_TEMPERATURE
            | ClimateEntityFeature.TURN_ON
            | ClimateEntityFeature.TURN_OFF
        )
        if self.fan_modes:
            features |= ClimateEntityFeature.FAN_MODE
        if self.coordinator.data.get("flap_swing") is not None:
            features |= ClimateEntityFeature.SWING_MODE
        return features

    @property
    def hvac_modes(self) -> list[HVACMode]:
        """Return the HVAC modes the device reports it supports."""
        capabilities = self.coordinator.data.get("hvac_modes")
        if not capabilities:
            return DEFAULT_HVAC_MODES
        return [HVACMode.OFF] + [HVAC_MODE_REVERSE[m] for m in capabilities if m in HVAC_MODE_REVERSE]

    @property
    def fan_modes(self) -> list[str] | None:
        """Return the fan speeds the device reports it supports."""
        capabilities = self.coordinator.data.get("fan_speeds")
        if not capabilities:
            return None
        return [FAN_MODE_REVERSE[s] for s in capabilities if s in FAN_MODE_REVERSE]

    @property
    def swing_modes(self) -> list[str]:
        """Return the swing modes (flap swing on/off)."""
        return [SWING_OFF, SWING_ON]

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
        # Available if the last cloud sync succeeded, the device is online and we have data
        return (
            super().available
            and self.coordinator.data.get("online") is not False
            and (
                self.coordinator.data.get("current_temp") is not None
                or self.coordinator.data.get("target_temp") is not None
            )
        )

    @property
    def current_temperature(self) -> float | None:
        """Return the current temperature."""
        return self.coordinator.data.get("current_temp")

    @property
    def current_humidity(self) -> float | None:
        """Return the current humidity, if the device measures it."""
        return self.coordinator.data.get("humidity")

    @property
    def target_temperature(self) -> float | None:
        """Return the temperature we try to reach."""
        return self.coordinator.data.get("target_temp")

    @property
    def hvac_mode(self) -> HVACMode | None:
        """Return current HVAC mode."""
        if self.coordinator.data.get("power_state") is not True:
            return HVACMode.OFF

        mode = self.coordinator.data.get("hvac_mode")
        if mode not in HVAC_MODE_REVERSE:
            if mode is not None:
                _LOGGER.debug("Unknown HVAC mode value from device: %s", mode)
            return None
        return HVAC_MODE_REVERSE[mode]

    @property
    def hvac_action(self) -> HVACAction | None:
        """Return current HVAC action based on what the device is actually doing."""
        if not self.coordinator.data.get("power_state"):
            return HVACAction.OFF

        # In AUTO the device reports whether it is currently heating or cooling
        mode = self.coordinator.data.get("hvac_mode_actual") or self.coordinator.data.get("hvac_mode")
        current_temp = self.current_temperature
        target_temp = self.target_temperature

        if mode == HVAC_MODE_HEAT:
            # Show heating if target is higher than current (with small buffer)
            if current_temp is not None and target_temp is not None and target_temp > current_temp + 0.2:
                return HVACAction.HEATING
            return HVACAction.IDLE
        if mode == HVAC_MODE_COOL:
            # Show cooling if target is lower than current (with small buffer)
            if current_temp is not None and target_temp is not None and target_temp < current_temp - 0.2:
                return HVACAction.COOLING
            return HVACAction.IDLE
        if mode == HVAC_MODE_FAN:
            return HVACAction.FAN
        if mode == HVAC_MODE_DRY:
            return HVACAction.DRYING
        return HVACAction.IDLE

    @property
    def fan_mode(self) -> str | None:
        """Return the current fan mode."""
        return FAN_MODE_REVERSE.get(self.coordinator.data.get("fan_speed"))

    @property
    def swing_mode(self) -> str | None:
        """Return whether the flap is swinging."""
        swing = self.coordinator.data.get("flap_swing")
        if swing is None:
            return None
        return SWING_ON if swing else SWING_OFF

    async def async_set_temperature(self, **kwargs: Any) -> None:
        """Set new target temperature."""
        if (temperature := kwargs.get(ATTR_TEMPERATURE)) is None:
            return

        await self.coordinator.async_set_temperature(temperature)

    async def async_set_hvac_mode(self, hvac_mode: HVACMode) -> None:
        """Set new HVAC mode."""
        if hvac_mode == HVACMode.OFF:
            await self.coordinator.async_set_power(False)
        elif hvac_mode in HVAC_MODE_MAP:
            # Power on and mode change go out as a single command
            await self.coordinator.async_set_hvac_mode(HVAC_MODE_MAP[hvac_mode])

    async def async_set_fan_mode(self, fan_mode: str) -> None:
        """Set new fan mode."""
        if fan_mode in FAN_MODE_MAP:
            await self.coordinator.async_set_fan_speed(FAN_MODE_MAP[fan_mode])

    async def async_set_swing_mode(self, swing_mode: str) -> None:
        """Turn flap swing on or off."""
        await self.coordinator.async_set_flap_swing(swing_mode == SWING_ON)

    async def async_turn_on(self) -> None:
        """Turn the entity on, keeping the device's last mode."""
        await self.coordinator.async_set_power(True)

    async def async_turn_off(self) -> None:
        """Turn the entity off."""
        await self.coordinator.async_set_power(False)
