"""REST API helpers for Innova Cloud."""
import logging

from homeassistant.core import HomeAssistant
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .const import API_BASE_URL

_LOGGER = logging.getLogger(__name__)


def normalize_email(email: str) -> str:
    """Normalize an email address the way the Innova app does before logging in."""
    return email.strip().lower()


async def validate_login(hass: HomeAssistant, email: str, password: str) -> dict | None:
    """Log in and return the token and user, or None if the credentials were rejected.

    Network errors (aiohttp.ClientError, TimeoutError) are raised to the caller.
    """
    session = async_get_clientsession(hass)

    async with session.post(
        f"{API_BASE_URL}/users/login",
        json={"email": normalize_email(email), "password": password},
        headers={"Content-Type": "application/json"},
        timeout=10
    ) as response:
        if response.status == 200:
            data = await response.json()
            return {
                "token": data.get("token"),
                "user": data.get("user", {})
            }
        # Bad credentials: HTTP 401 / {"code": 1304, "message": "Invalid credentials"}
        _LOGGER.warning(
            "Login rejected with HTTP status %s: %s",
            response.status,
            (await response.text())[:200],
        )

    return None


async def get_devices(hass: HomeAssistant, token: str) -> list[dict]:
    """Get all devices on the account.

    Raises aiohttp.ClientError/TimeoutError on network errors and
    PermissionError if the token is rejected.
    """
    session = async_get_clientsession(hass)

    async with session.get(
        f"{API_BASE_URL}/homes",
        headers={"Authorization": f"Bearer {token}"},
        timeout=10
    ) as response:
        if response.status == 401:
            raise PermissionError("Innova Cloud rejected the token")
        response.raise_for_status()
        homes = await response.json()

    devices = []
    for home in homes:
        rooms = {room.get("id"): room.get("name") for room in home.get("rooms", [])}
        for device in home.get("devices", []):
            devices.append({
                "mac": device.get("macAddress"),
                "node_id": device.get("nodeId", 0),
                "name": device.get("name"),
                "room": rooms.get(device.get("roomId")),
                "home": home.get("name"),
                "home_id": home.get("id"),
            })
    return devices
