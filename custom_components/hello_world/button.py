import aiohttp
import asyncio
from homeassistant.components.button import ButtonEntity, ButtonDeviceClass
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import EntityCategory
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from .const import DOMAIN
from .entity import OnvifBaseEntity
import logging

_LOGGER = logging.getLogger(__name__)


class ZoomButton(OnvifBaseEntity, ButtonEntity):
    def __init__(self, hass, entry, direction):
        super().__init__(hass, entry)
        self._direction = direction  # "ZoomIn" or "ZoomOut"
        self._attr_name = f"Camera {entry.data['name']} {direction}"
        self._attr_unique_id = f"urmet_camera_{entry.data['name']}_{direction.lower()}"
        self._duration = 1.2

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


class RebootButton(OnvifBaseEntity, ButtonEntity):
    _attr_device_class = ButtonDeviceClass.RESTART
    _attr_entity_category = EntityCategory.CONFIG

    def __init__(self, hass, entry):
        super().__init__(hass, entry)
        self._attr_name = f"Camera {entry.data['name']} Reboot"
        self._attr_unique_id = f"reboot_{entry.entry_id}"
        self._client = hass.data[DOMAIN][entry.entry_id]["client"]

    async def async_press(self) -> None:
        """Handle the button press to reboot the camera."""
        try:
            devicemgmt = self._client.create_devicemgmt_service()
            await devicemgmt.SystemReboot()
            _LOGGER.info("Reboot command sent to camera %s", self._entry.data["ip"])
        except Exception as e:
            _LOGGER.error("Failed to reboot camera %s: %s", self._entry.data["ip"], e)


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
