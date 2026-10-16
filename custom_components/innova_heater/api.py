"""REST API helpers for Innova Cloud."""
import logging

from homeassistant.core import HomeAssistant
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .const import API_BASE_URL

_LOGGER = logging.getLogger(__name__)


async def validate_login(hass: HomeAssistant, email: str, password: str) -> dict | None:
    """Log in and return the token and user, or None if the credentials were rejected.

    Network errors (aiohttp.ClientError, TimeoutError) are raised to the caller.
    """
    session = async_get_clientsession(hass)

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
        # The API answers bad credentials with HTTP 500 / {"code": 402, ...}
        _LOGGER.warning("Login rejected with HTTP status %s", response.status)

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
