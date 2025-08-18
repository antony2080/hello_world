import aiohttp
from homeassistant.components.select import SelectEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from .api import CameraLocalAPI
from .const import DOMAIN

IR_MODES = ["day", "night", "auto"]


class IrCutSelect(SelectEntity):
    def __init__(self, hass, entry):
        self._hass = hass
        self._entry = entry
        self._attr_name = f"Camera {entry.data['name']} Mode"
        self._attr_unique_id = f"ircut_{entry.entry_id}"
        self._attr_options = IR_MODES
        self._current_option = "day"  # Default, or fetch from device

    @property
    def current_option(self):
        return self._current_option

    @property
    def device_info(self):
        return {
            "identifiers": {(DOMAIN, self._entry.data["uid"])},
            "name": f"Camera {self._entry.data['name']}",
            "manufacturer": "URMET",
            "model": "1099",
            "sw_version": "1.0.0",
        }

    async def async_select_option(self, option: str):
        data = self._hass.data[DOMAIN][self._entry.entry_id]
        ip = data["ip"]
        username = data.get("username")
        password = data.get("password")
        auth = aiohttp.BasicAuth(username, password)
        headers = {"Content-Type": "application/xml"}
        url = f"http://{ip}/Images/1/IrCutFilter"
        mode_value = "passivity" if option == "auto" else option
        xml = f"""<?xml version='1.0' encoding='UTF-8' ?>
<IrCutFillter Version='1.0'>
    <Mode>{mode_value}</Mode>
    <DayStartTime></DayStartTime>
    <DayEndTime></DayEndTime>
    <Sensitivity></Sensitivity>
    <SwitchTime></SwitchTime>
</IrCutFillter>
"""
        async with aiohttp.ClientSession() as session:
            async with session.put(url, data=xml, headers=headers, auth=auth) as resp:
                if resp.status == 200:
                    self._current_option = option
        self.async_write_ha_state()

    async def async_update(self):
        data = self._hass.data[DOMAIN][self._entry.entry_id]
        ip = data["ip"]
        username = data.get("username")
        password = data.get("password")
        api = CameraLocalAPI(ip, username, password)
        option = await api.get_ircut_mode()
        if option is not None:
            self._current_option = option


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback
):
    async_add_entities([IrCutSelect(hass, entry)])
