from homeassistant.components.switch import SwitchEntity
from homeassistant.helpers.device_registry import DeviceInfo

DOMAIN = "hello_world"


async def async_setup_entry(hass, entry, async_add_entities):
    async_add_entities([HelloWorldSwitch()])


class HelloWorldSwitch(SwitchEntity):
    def __init__(self):
        self._attr_name = "Hello World Switch"
        self._attr_is_on = False
        self._attr_unique_id = "hello_world_switch"

    @property
    def device_info(self) -> DeviceInfo:
        return DeviceInfo(
            identifiers={(DOMAIN, "hello_world_device")},
            name="Hello World",
            manufacturer="Antony Inc.",
            model="HW-1",
        )

    async def async_turn_on(self, **kwargs):
        self._attr_is_on = True
        self.async_write_ha_state()

    async def async_turn_off(self, **kwargs):
        self._attr_is_on = False
        self.async_write_ha_state()
