import aiohttp
import xml.etree.ElementTree as ET
from homeassistant.components.switch import SwitchEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from .api import CameraLocalAPI
from .const import DOMAIN


class AudioAlarmSwitch(SwitchEntity):
    def __init__(self, hass, entry):
        self._hass = hass
        self._entry = entry
        self._attr_name = f"Camera {entry.data['name']} Alarm"
        self._attr_unique_id = f"alarm_{entry.entry_id}"
        self._device_info = self._entry.data.get("device_info", {})
        self._is_on = False

    @property
    def is_on(self):
        return self._is_on

    @property
    def device_info(self):
        return {
            "identifiers": {(DOMAIN, self._entry.data["uid"])},
            "name": f"Camera {self._entry.data['name']}",
            "manufacturer": self._device_info.get("manufacturer", "URMET"),
            "model": self._device_info.get("model", "1099"),
            "sw_version": self._device_info.get("sw_version", "1.0.0"),
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
        self._hass = hass
        self._entry = entry
        self._attr_name = f"Camera {entry.data['name']} Motion"
        self._attr_unique_id = f"motion_{entry.entry_id}"
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
        auth = aiohttp.BasicAuth(username, password)
        url = f"http://{ip}/Pictures/1/Motion"
        async with aiohttp.ClientSession() as session:
            async with session.get(url, auth=auth) as resp:
                if resp.status == 200:
                    xml = await resp.text()
                    try:
                        root = ET.fromstring(xml)
                        enable = root.findtext("Enable")
                        self._is_on = enable and enable.lower() == "true"
                    except Exception:
                        pass


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback
):
    async_add_entities([AudioAlarmSwitch(hass, entry), MotionSwitch(hass, entry)])
