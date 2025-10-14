"""Config flow for Innova Cloud integration."""
import logging
import voluptuous as vol

from homeassistant import config_entries
from homeassistant.const import CONF_EMAIL, CONF_PASSWORD
from homeassistant.core import HomeAssistant
from homeassistant.data_entry_flow import FlowResult
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .const import (
    DOMAIN,
    CONF_MAC_ADDRESS,
    CONF_DEVICE_TYPE,
    API_BASE_URL,
    DEVICE_TYPES,
    DEVICE_TYPE_FANCOIL,
)

_LOGGER = logging.getLogger(__name__)


async def validate_login(hass: HomeAssistant, email: str, password: str) -> dict:
    """Validate login credentials."""
    session = async_get_clientsession(hass)
    
    try:
        async with session.post(
            f"{API_BASE_URL}/users/login",
            json={"email": email, "password": password},
            headers={"Content-Type": "application/json"},
            timeout=10
        ) as response:
            if response.status == 200:
                data = await response.json()
                return {
                    "token": data.get("token"),
                    "user": data.get("user", {})
                }
    except Exception as err:
        _LOGGER.error("Login failed: %s", err)
    
    return None


async def get_devices(hass: HomeAssistant, token: str) -> list:
    """Get list of devices from API."""
    session = async_get_clientsession(hass)
    
    try:
        async with session.get(
            f"{API_BASE_URL}/homes",
            headers={"Authorization": f"Bearer {token}"},
            timeout=10
        ) as response:
            if response.status == 200:
                devices = []
                homes = await response.json()
                for home in homes:
                    for room in home.get("rooms", []):
                        for device in room.get("devices", []):
                            devices.append({
                                "mac": device.get("macAddress"),
                                "name": device.get("name"),
                                "room": room.get("name"),
                                "home": home.get("name")
                            })
                return devices
    except Exception as err:
        _LOGGER.error("Failed to get devices: %s", err)
    
    return []


class InnovaHeaterConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Innova Cloud."""

    VERSION = 1

    def __init__(self):
        """Initialize the config flow."""
        self.token = None
        self.devices = []

    async def async_step_user(self, user_input=None) -> FlowResult:
        """Handle the initial step."""
        errors = {}

        if user_input is not None:
            try:
                result = await validate_login(
                    self.hass,
                    user_input[CONF_EMAIL],
                    user_input[CONF_PASSWORD]
                )
                
                if result and result.get("token"):
                    self.token = result["token"]
                    self.devices = await get_devices(self.hass, self.token)
                    
                    if self.devices:
                        return await self.async_step_device()
                    else:
                        errors["base"] = "no_devices"
                else:
                    errors["base"] = "invalid_auth"
                    
            except Exception as err:
                _LOGGER.exception("Unexpected exception: %s", err)
                errors["base"] = "unknown"

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema({
                vol.Required(CONF_EMAIL): str,
                vol.Required(CONF_PASSWORD): str,
            }),
            errors=errors,
        )

    async def async_step_device(self, user_input=None) -> FlowResult:
        """Handle device selection."""
        if user_input is not None:
            mac_address = user_input[CONF_MAC_ADDRESS]
            device_type = user_input.get(CONF_DEVICE_TYPE, DEVICE_TYPE_FANCOIL)
            device = next((d for d in self.devices if d["mac"] == mac_address), None)
            
            if device:
                await self.async_set_unique_id(mac_address)
                self._abort_if_unique_id_configured()
                
                return self.async_create_entry(
                    title=f"{device['name']} ({device['room']})",
                    data={
                        CONF_MAC_ADDRESS: mac_address,
                        CONF_DEVICE_TYPE: device_type,
                        "token": self.token,
                        "name": device["name"],
                    },
                )

        device_options = {d["mac"]: f"{d['name']} - {d['room']} ({d['home']})" 
                         for d in self.devices}

        return self.async_show_form(
            step_id="device",
            data_schema=vol.Schema({
                vol.Required(CONF_MAC_ADDRESS): vol.In(device_options),
                vol.Required(CONF_DEVICE_TYPE, default=DEVICE_TYPE_FANCOIL): vol.In(DEVICE_TYPES),
            }),
        )
