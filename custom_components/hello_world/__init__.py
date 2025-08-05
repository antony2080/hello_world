from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import async_get_platforms

from .camera import UrmetCamera
from .button import ZoomButton
from .const import DOMAIN


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry):
    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN][entry.entry_id] = {
        "host": entry.data["host"],
        "username": entry.data["username"],
        "password": entry.data["password"],
    }

    platforms = async_get_platforms(hass, DOMAIN)
    for platform in platforms:
        platform.async_add_entities(
            [
                UrmetCamera(entry),
                ZoomButton(entry, "ZoomIn"),
                ZoomButton(entry, "ZoomOut"),
            ]
        )
    return True
