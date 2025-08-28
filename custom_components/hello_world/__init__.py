from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from onvif import ONVIFCamera
import logging

from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry):
    _LOGGER.info("Setting up entry: %s", entry.title)

    hass.data.setdefault(DOMAIN, {})
    cam = ONVIFCamera(
        entry.data["ip"],
        80,
        entry.data["username"],
        entry.data["password"],
    )
    hass.data[DOMAIN][entry.entry_id] = {
        "ip": entry.data["ip"],
        "uid": entry.data["uid"],
        "username": entry.data["username"],
        "password": entry.data["password"],
        "manufacturer": entry.data.get("manufacturer"),
        "model": entry.data.get("model"),
        "fw_version": entry.data.get("fw_version"),
        "mac": entry.data.get("mac"),
        "client": cam,
    }

    # Forward the entry setup to the camera, button, and select platforms
    await hass.config_entries.async_forward_entry_setups(
        entry, ["camera", "button", "select", "switch"]
    )

    return True
