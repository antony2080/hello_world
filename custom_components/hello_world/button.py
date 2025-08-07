import asyncio
import aiohttp
from homeassistant.components.button import ButtonEntity
from .const import DOMAIN
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback


class ZoomButton(ButtonEntity):
    def __init__(self, hass, entry, direction):
        self._hass = hass
        self._direction = direction  # "ZoomIn" or "ZoomOut"
        self._attr_name = f"Camera {direction}"
        self._attr_unique_id = f"urmet_camera_{direction.lower()}"
        self._entry = entry
        self._duration = 0.8

    async def async_press(self):
        data = self._hass.data[DOMAIN][self._entry.entry_id]
        ip = data["ip"]
        username = data.get("username")
        password = data.get("password")
        auth = aiohttp.BasicAuth(username, password)
        headers = {"Content-Type": "application/x-www-form-urlencoded"}
        url = f"http://{ip}/PTZ/1/{self._direction}"
        payload_start = "Param1=1&Param2=5"
        payload_stop = "Param1=0&Param2=5"
        async with aiohttp.ClientSession() as session:
            await session.put(url, data=payload_start, headers=headers, auth=auth)
            await asyncio.sleep(self._duration)
            await session.put(url, data=payload_stop, headers=headers, auth=auth)


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback
):
    """Set up the button platform."""
    async_add_entities(
        [
            ZoomButton(hass, entry, "ZoomIn"),
            ZoomButton(hass, entry, "ZoomOut"),
        ]
    )
