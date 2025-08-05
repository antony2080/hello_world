from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import async_get_platforms
import logging

from .camera import UrmetCamera
from .button import ZoomButton
from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry):
    _LOGGER.info("Setting up entry: %s", entry.title)

    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN][entry.entry_id] = {
        "host": entry.data["host"],
        "username": entry.data["username"],
        "password": entry.data["password"],
    }

    platforms = async_get_platforms(hass, DOMAIN)
    for platform in platforms:
        _LOGGER.info("Adding entities to platform: %s", platform.domain)
        platform.async_add_entities(
            [
                UrmetCamera(entry),
                ZoomButton(entry, "ZoomIn"),
                ZoomButton(entry, "ZoomOut"),
            ]
        )
    return True
