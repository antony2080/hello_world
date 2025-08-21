import aiohttp
from homeassistant.components.select import SelectEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from .api import CameraLocalAPI
from .const import DOMAIN

IR_MODES = {"day": "Day", "night": "Night", "auto": "Automatic"}


class IrCutSelect(SelectEntity):
    def __init__(self, hass, entry):
        self._hass = hass
        self._entry = entry
        self._attr_name = f"Camera {entry.data['name']} Mode"
        self._attr_unique_id = f"ircut_{entry.entry_id}"
        self._attr_options = list(IR_MODES.values())
        self._current_option = IR_MODES["day"]  # Default, or fetch from device

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

    @property
    def icon(self):
        if self._current_option == IR_MODES["day"]:
            return "mdi:white-balance-sunny"
        elif self._current_option == IR_MODES["night"]:
            return "mdi:weather-night"
        elif self._current_option == IR_MODES["auto"]:
            return "mdi:alpha-a-circle-outline"
        return "mdi:camera"

    async def async_select_option(self, option: str):
        # Find the key for the selected display name
        mode_key = next((k for k, v in IR_MODES.items() if v == option), None)
        if not mode_key:
            return
        data = self._hass.data[DOMAIN][self._entry.entry_id]
        ip = data["ip"]
        username = data.get("username")
        password = data.get("password")
        auth = aiohttp.BasicAuth(username, password)
        headers = {"Content-Type": "application/xml"}
        url = f"http://{ip}/Images/1/IrCutFilter"
        mode_value = "passivity" if mode_key == "auto" else mode_key
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
                    self._current_option = IR_MODES[mode_key]
        self.async_write_ha_state()

    async def async_update(self):
        data = self._hass.data[DOMAIN][self._entry.entry_id]
        ip = data["ip"]
        username = data.get("username")
        password = data.get("password")
        api = CameraLocalAPI(ip, username, password)
        mode = await api.get_ircut_mode()
        if mode is not None:
            if mode == "passivity":
                self._current_option = IR_MODES["auto"]
            elif mode in IR_MODES:
                self._current_option = IR_MODES[mode]
            else:
                self._current_option = mode


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback
):
    async_add_entities([IrCutSelect(hass, entry)])
