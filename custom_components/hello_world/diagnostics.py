from homeassistant.components.diagnostics import async_redact_data
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.const import CONF_HOST, CONF_PASSWORD, CONF_USERNAME
from .const import DOMAIN
from typing import Any

REDACT_CONFIG = {CONF_HOST, CONF_PASSWORD, CONF_USERNAME}


async def async_get_config_entry_diagnostics(
    hass: HomeAssistant, entry: ConfigEntry
) -> dict[str, Any]:
    """Return diagnostics for a config entry."""
    data = hass.data[DOMAIN][entry.entry_id]
    device_data = {
        "ip": data["ip"],
        "uid": data["uid"],
        "username": data.get("username"),
        "password": data.get("password"),
        "manufacturer": data.get("manufacturer"),
        "model": data.get("model"),
        "fw_version": data.get("fw_version"),
        "mac": data.get("mac"),
    }

    return async_redact_data(
        {
            "entry": {
                "entry_id": entry.entry_id,
                "domain": entry.domain,
                "title": entry.title,
                "data": entry.data,
                "options": entry.options,
            },
            "device": device_data,
        },
        REDACT_CONFIG,
    )
