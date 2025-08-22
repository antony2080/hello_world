from homeassistant.components.camera import Camera, CameraEntityFeature
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from .const import DOMAIN
import logging
import aiohttp

_LOGGER = logging.getLogger(__name__)


class UrmetCamera(Camera):
    attr_supported_features = CameraEntityFeature.STREAM

    def __init__(self, hass, entry):
        super().__init__()
        self._hass = hass
        self._entry = entry
        data = hass.data[DOMAIN][entry.entry_id]
        self._ip = data["ip"]
        self._uid = data["uid"]
        self._username = data.get("username")
        self._password = data.get("password")
        self._stream_url = f"rtsp://{self._ip}:554/live/0/MAIN"
        self._attr_name = f"Camera {self._entry.data['name']}"
        self._attr_unique_id = f"urmet_camera_{entry.entry_id}"

    @property
    def unique_id(self):
        return self._attr_unique_id

    @property
    def device_info(self):
        return {
            "identifiers": {(DOMAIN, self._entry.data["uid"])},  # 關鍵：唯一標識
            "name": f"Camera {self._entry.data['name']}",
            "manufacturer": "URMET",
            "model": "1099",
            "sw_version": "1.0.0",
        }

    async def async_camera_image(self, width=None, height=None):
        # The width and height parameters are ignored as the camera does not support resizing.
        snapshot_url = f"http://{self._ip}/Snapshot/1/RemoteImageCapture?ImageFormat=2"
        auth = (
            aiohttp.BasicAuth(self._username, self._password)
            if self._username and self._password
            else None
        )

        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(snapshot_url, auth=auth) as response:
                    if response.status == 200:
                        return await response.read()
                    else:
                        _LOGGER.error(
                            "Failed to fetch snapshot image: HTTP %s", response.status
                        )
        except Exception as e:
            _LOGGER.error("Failed to fetch snapshot image: %s", e)
        return None

    async def stream_source(self):
        _LOGGER.info("Providing stream URL: %s", self._stream_url)
        return self._stream_url


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback
):
    """Set up the camera platform."""
    async_add_entities([UrmetCamera(hass, entry)])
