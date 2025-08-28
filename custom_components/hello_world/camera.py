import aiohttp
from homeassistant.components.camera import Camera, CameraEntityFeature
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from haffmpeg.camera import CameraMjpeg
from homeassistant.components.ffmpeg import CONF_EXTRA_ARGUMENTS, get_ffmpeg_manager
from homeassistant.helpers.aiohttp_client import async_aiohttp_proxy_stream
from .const import DOMAIN
from .entity import OnvifBaseEntity
import logging

_LOGGER = logging.getLogger(__name__)


class UrmetCamera(OnvifBaseEntity, Camera):
    attr_supported_features = CameraEntityFeature.STREAM

    def __init__(self, hass, entry):
        super().__init__(hass, entry)
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

    async def handle_async_mjpeg_stream(self, request):
        """Generate an HTTP MJPEG stream from the camera."""
        _LOGGER.debug("Handling MJPEG stream from camera '%s'", self._attr_name)
        ffmpeg_manager = get_ffmpeg_manager(self._hass)
        stream = CameraMjpeg(ffmpeg_manager.binary)

        try:
            await stream.open_camera(
                self._stream_url,
                extra_cmd=self._entry.options.get(CONF_EXTRA_ARGUMENTS),
            )
            stream_reader = await stream.get_reader()
            return await async_aiohttp_proxy_stream(
                self._hass,
                request,
                stream_reader,
                ffmpeg_manager.ffmpeg_stream_content_type,
            )
        finally:
            await stream.close()


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback
):
    """Set up the camera platform."""
    async_add_entities([UrmetCamera(hass, entry)])
