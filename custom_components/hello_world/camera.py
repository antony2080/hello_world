from homeassistant.components.camera import Camera
from .const import DOMAIN


class UrmetCamera(Camera):
    def __init__(self, entry):
        super().__init__()
        data = entry.hass.data[DOMAIN][entry.entry_id]
        host = data["host"]

        self._attr_name = "Urmet Camera Stream"
        self._stream_url = f"rtsp://{host}:554/live/0/MAIN"

    async def stream_source(self):
        return self._stream_url
