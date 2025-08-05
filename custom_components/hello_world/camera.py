from homeassistant.components.camera import Camera
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from .const import DOMAIN


class UrmetCamera(Camera):
    def __init__(self, hass, entry):
        super().__init__()
        data = hass.data[DOMAIN][entry.entry_id]
        host = data["host"]

        self._attr_name = "Urmet Camera Stream"
        self._attr_unique_id = f"urmet_camera_{entry.entry_id}"
        self._stream_url = f"rtsp://{host}:554/live/0/MAIN"

    @property
    def unique_id(self):
        return self._attr_unique_id

    async def async_camera_image(self):
        # Placeholder for fetching a snapshot image from the camera
        return None

    async def stream_source(self):
        return self._stream_url


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback
):
    """Set up the camera platform."""
    async_add_entities([UrmetCamera(hass, entry)])
