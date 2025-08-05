from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from .camera import UrmetCamera
from .button import ZoomButton

DOMAIN = "hello_world"


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry):
    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN][entry.entry_id] = {
        "host": entry.data["host"],
        "username": entry.data["username"],
        "password": entry.data["password"],
    }

    async_add_entities = hass.helpers.entity_platform.async_add_entities
    async_add_entities(
        [UrmetCamera(entry), ZoomButton(entry, "ZoomIn"), ZoomButton(entry, "ZoomOut")]
    )
    return True
