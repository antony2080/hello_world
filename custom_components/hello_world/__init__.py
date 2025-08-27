from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers import device_registry as dr
import logging

from .const import DOMAIN
from .model import Camera

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry):
    _LOGGER.info("Setting up entry: %s", entry.title)

    # Retrieve device info and camera details from entry data
    device_info = entry.data["device_info"]
    cam = Camera(
        cam_name=entry.data["name"],
        cam_uid=entry.data["uid"],
        cam_usr=entry.data["username"],
        cam_psw=entry.data["password"],
    )

    # Validate MAC address
    mac_address = device_info.get("mac")
    if not mac_address:
        _LOGGER.warning("MAC address is missing for device: %s", cam.cam_name)
        connections = None
    else:
        connections = {(dr.CONNECTION_NETWORK_MAC, mac_address)}

    # Register the device in the device registry
    device_registry = dr.async_get(hass)
    device_registry.async_get_or_create(
        config_entry_id=entry.entry_id,
        connections=connections,
        identifiers={(DOMAIN, cam.cam_uid)},
        manufacturer=device_info["manufacturer"],
        model=device_info["model"],
        name=cam.cam_name,
        sw_version=device_info["fw_version"],
    )

    # Store entry data in hass.data for use by platforms
    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN][entry.entry_id] = {
        "ip": entry.data["ip"],
        "username": entry.data["username"],
        "password": entry.data["password"],
        "device_info": device_info,
    }

    # Forward the entry setup to the camera, button, and select platforms
    await hass.config_entries.async_forward_entry_setups(
        entry, ["camera", "button", "select", "switch"]
    )

    return True
