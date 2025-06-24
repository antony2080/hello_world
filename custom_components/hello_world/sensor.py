from homeassistant.helpers.entity import Entity


async def async_setup_platform(hass, config, async_add_entities, discovery_info=None):
    async_add_entities([HelloWorldSensor()])


class HelloWorldSensor(Entity):
    def __init__(self):
        self._state = "Hello World!"

    @property
    def name(self):
        return "Hello World Sensor test"

    @property
    def state(self):
        return self._state
