import aiohttp
from homeassistant.components.switch import SwitchEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from .const import DOMAIN


class AudioAlarmSwitch(SwitchEntity):
    def __init__(self, hass, entry):
        self._hass = hass
        self._entry = entry
        self._attr_name = f"Camera {entry.data['name']} Alarm"
        self._attr_unique_id = f"alarm_{entry.entry_id}"
        self._is_on = False

    @property
    def is_on(self):
        return self._is_on

    @property
    def device_info(self):
        return {
            "identifiers": {(DOMAIN, self._entry.data["uid"])},
            "name": f"Camera {self._entry.data['name']}",
            "manufacturer": "URMET",
            "model": "1099",
            "sw_version": "1.0.0",
        }

    async def async_turn_on(self, **kwargs):
        await self._set_alarm(True)

    async def async_turn_off(self, **kwargs):
        await self._set_alarm(False)

    async def _set_alarm(self, enable: bool):
        data = self._hass.data[DOMAIN][self._entry.entry_id]
        ip = data["ip"]
        username = data.get("username")
        password = data.get("password")
        auth = aiohttp.BasicAuth(username, password)
        headers = {"Content-Type": "application/xml"}
        url = f"http://{ip}/System/AudioAlarmConfig"
        xml = f"""<?xml version='1.0' encoding='UTF-8' ?>
<AudioAlarm Version='1.0'>
    <Enable>{"true" if enable else "false"}</Enable>
    <Type></Type>
    <Delay>5</Delay>
    <Volume>50</Volume>
</AudioAlarm>
"""
        async with aiohttp.ClientSession() as session:
            async with session.put(url, data=xml, headers=headers, auth=auth) as resp:
                if resp.status == 200:
                    self._is_on = enable
        self.async_write_ha_state()


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback
):
    async_add_entities([AudioAlarmSwitch(hass, entry)])
