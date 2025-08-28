import aiohttp
from homeassistant.components.switch import SwitchEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from .const import DOMAIN
from .api import CameraLocalAPI
from .entity import OnvifBaseEntity


class AudioAlarmSwitch(OnvifBaseEntity, SwitchEntity):
    def __init__(self, hass, entry):
        super().__init__(hass, entry)
        self._attr_name = f"Camera {entry.data['name']} Alarm"
        self._attr_unique_id = f"alarm_{entry.entry_id}"
        self._is_on = False

    @property
    def is_on(self):
        return self._is_on

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

    async def async_update(self):
        data = self._hass.data[DOMAIN][self._entry.entry_id]
        ip = data["ip"]
        username = data.get("username")
        password = data.get("password")
        api = CameraLocalAPI(ip, username, password)
        enabled = await api.get_alarm_enabled()
        if enabled is not None:
            self._is_on = enabled


class MotionSwitch(SwitchEntity):
    def __init__(self, hass, entry):
        super().__init__(hass, entry)
        self._attr_name = f"Camera {entry.data['name']} Motion"
        self._attr_unique_id = f"motion_{entry.entry_id}"
        self._is_on = False

    @property
    def is_on(self):
        return self._is_on

    async def async_turn_on(self, **kwargs):
        await self._set_motion(True)

    async def async_turn_off(self, **kwargs):
        await self._set_motion(False)

    async def _set_motion(self, enable: bool):
        data = self._hass.data[DOMAIN][self._entry.entry_id]
        ip = data["ip"]
        username = data.get("username")
        password = data.get("password")
        auth = aiohttp.BasicAuth(username, password)
        headers = {"Content-Type": "application/xml"}
        url = f"http://{ip}/Pictures/1/Motion"
        xml = f"""<?xml version="1.0" encoding="UTF-8" ?>
<Motion Version="1.0">
  <Enable>{"true" if enable else "false"}</Enable>
  <Senstive></Senstive>
  <MotionRegionList Version="1.0" />
</Motion>"""
        async with aiohttp.ClientSession() as session:
            async with session.put(url, data=xml, headers=headers, auth=auth) as resp:
                if resp.status == 200:
                    self._is_on = enable
        self.async_write_ha_state()

    async def async_update(self):
        data = self._hass.data[DOMAIN][self._entry.entry_id]
        ip = data["ip"]
        username = data.get("username")
        password = data.get("password")
        api = CameraLocalAPI(ip, username, password)
        enabled = await api.get_motion_enabled()
        if enabled is not None:
            self._is_on = enabled


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback
):
    async_add_entities([AudioAlarmSwitch(hass, entry), MotionSwitch(hass, entry)])
