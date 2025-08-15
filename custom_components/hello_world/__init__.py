from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
import logging

from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry):
    _LOGGER.info("Setting up entry: %s", entry.title)

    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN][entry.entry_id] = {
        "ip": entry.data["ip"],
        "uid": entry.data["uid"],
        "username": entry.data["username"],
        "password": entry.data["password"],
    }

    # Forward the entry setup to the camera, button, and select platforms
    await hass.config_entries.async_forward_entry_setups(
        entry, ["camera", "button", "select", "switch"]
    )

    return True
