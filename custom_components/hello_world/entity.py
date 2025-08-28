from homeassistant.helpers.entity import Entity
from homeassistant.helpers.device_registry import CONNECTION_NETWORK_MAC
from .const import DOMAIN


class OnvifBaseEntity(Entity):
    """Base class for Onvif entities."""

    def __init__(self, hass, entry):
        self._hass = hass
        self._entry = entry

    @property
    def device_info(self):
        return {
            "identifiers": {(DOMAIN, self._entry.data["uid"])},
            "connections": {(CONNECTION_NETWORK_MAC, self._entry.data.get("mac"))},
            "name": f"Camera {self._entry.data['name']}",
            "manufacturer": self._entry.data.get("manufacturer", "Urmet"),
            "model": self._entry.data.get("model", "Camera"),
            "sw_version": self._entry.data.get("fw_version", "1.0.0"),
        }
