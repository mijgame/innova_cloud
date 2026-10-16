"""Config flow for Innova Cloud integration."""
import logging
from collections.abc import Mapping
from typing import Any

import aiohttp
import voluptuous as vol

from homeassistant import config_entries
from homeassistant.const import CONF_EMAIL, CONF_PASSWORD
from homeassistant.data_entry_flow import FlowResult

from .api import get_devices, validate_login
from .const import (
    DOMAIN,
    CONF_MAC_ADDRESS,
    CONF_DEVICE_TYPE,
    DEVICE_TYPES,
    DEVICE_TYPE_FANCOIL,
)

_LOGGER = logging.getLogger(__name__)


class InnovaHeaterConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Innova Cloud."""

    VERSION = 1

    def __init__(self):
        """Initialize the config flow."""
        self.token = None
        self.email = None
        self.password = None
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
                    self.email = user_input[CONF_EMAIL]
                    self.password = user_input[CONF_PASSWORD]
                    self.devices = await get_devices(self.hass, self.token)

                    if self.devices:
                        return await self.async_step_device()
                    else:
                        errors["base"] = "no_devices"
                else:
                    errors["base"] = "invalid_auth"

            except (aiohttp.ClientError, TimeoutError) as err:
                _LOGGER.error("Cannot connect to Innova Cloud: %s", err)
                errors["base"] = "cannot_connect"
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
                        CONF_EMAIL: self.email,
                        CONF_PASSWORD: self.password,
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

    async def async_step_reauth(self, entry_data: Mapping[str, Any]) -> FlowResult:
        """Start re-authentication when the stored token/credentials stop working."""
        return await self.async_step_reauth_confirm()

    async def async_step_reauth_confirm(self, user_input=None) -> FlowResult:
        """Ask for credentials again and store a fresh token."""
        errors = {}
        reauth_entry = self._get_reauth_entry()

        if user_input is not None:
            try:
                result = await validate_login(
                    self.hass,
                    user_input[CONF_EMAIL],
                    user_input[CONF_PASSWORD]
                )

                if result and result.get("token"):
                    return self.async_update_reload_and_abort(
                        reauth_entry,
                        data_updates={
                            CONF_EMAIL: user_input[CONF_EMAIL],
                            CONF_PASSWORD: user_input[CONF_PASSWORD],
                            "token": result["token"],
                        },
                    )
                errors["base"] = "invalid_auth"

            except (aiohttp.ClientError, TimeoutError) as err:
                _LOGGER.error("Cannot connect to Innova Cloud: %s", err)
                errors["base"] = "cannot_connect"
            except Exception as err:
                _LOGGER.exception("Unexpected exception: %s", err)
                errors["base"] = "unknown"

        return self.async_show_form(
            step_id="reauth_confirm",
            data_schema=vol.Schema({
                vol.Required(
                    CONF_EMAIL, default=reauth_entry.data.get(CONF_EMAIL, "")
                ): str,
                vol.Required(CONF_PASSWORD): str,
            }),
            errors=errors,
        )
