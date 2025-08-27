from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers import device_registry as dr
import logging

from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry):
    _LOGGER.info("Setting up entry: %s", entry.title)

    device_registry = dr.async_get(hass)
    device = device_registry.async_get_device(identifiers={(DOMAIN, entry.data["uid"])})

    if device:
        _LOGGER.info("Device found in registry: %s", device)
        hass.data.setdefault(DOMAIN, {})
        hass.data[DOMAIN][entry.entry_id] = {
            "ip": entry.data["ip"],
            "uid": entry.data["uid"],
            "username": entry.data["username"],
            "password": entry.data["password"],
            "device_info": {
                "manufacturer": device.manufacturer,
                "model": device.model,
                "sw_version": device.sw_version,
                "connections": device.connections,
            },
        }
    else:
        _LOGGER.warning("Device not found in registry")

    # Forward the entry setup to the camera, button, and select platforms
    await hass.config_entries.async_forward_entry_setups(
        entry, ["camera", "button", "select", "switch"]
    )

    return True
