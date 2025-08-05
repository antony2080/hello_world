import asyncio
import aiohttp
from homeassistant.components.button import ButtonEntity
from .const import DOMAIN


class ZoomButton(ButtonEntity):
    def __init__(self, entry, direction):
        self._direction = direction  # "ZoomIn" or "ZoomOut"
        self._attr_name = f"Camera {direction}"
        self._attr_unique_id = f"urmet_camera_{direction.lower()}"
        self._entry = entry

    async def async_press(self):
        data = self.hass.data[DOMAIN][self._entry.entry_id]
        host = data["host"]
        auth = aiohttp.BasicAuth(data["username"], data["password"])
        headers = {"Content-Type": "application/x-www-form-urlencoded"}
        url = f"http://{host}/PTZ/1/{self._direction}"

        async with aiohttp.ClientSession() as session:
            await session.put(url, data="Param1=1&Param2=5", headers=headers, auth=auth)
            await asyncio.sleep(0.4)
            await session.put(url, data="Param1=0&Param2=5", headers=headers, auth=auth)
