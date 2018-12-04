"""
Support for TIAGo.
"""
import asyncio
import logging
import async_timeout

import voluptuous as vol

from custom_components.rosrobot import (RobotROS, connect_to_rosbridge,
    PLATFORM_SCHEMA)
from homeassistant.const import (CONF_NAME, CONF_HOST, CONF_PORT)
import homeassistant.helpers.config_validation as cv

from homeassistant.exceptions import PlatformNotReady
from homeassistant.util.async_ import run_coroutine_threadsafe

import roslibpy

REQUIREMENTS = ['roslibpy==0.3.0']

_LOGGER = logging.getLogger(__name__)

PLATFORM = 'tiago'
DEFAULT_NAME = 'TIAGo'

PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend({
    vol.Optional(CONF_NAME, default=DEFAULT_NAME): cv.string,
    vol.Required(CONF_HOST): cv.string,
    vol.Required(CONF_PORT): int,
}, extra=vol.ALLOW_EXTRA)


async def async_setup_platform(hass, config, async_add_entities,
                               discovery_info=None):
    """Set up TIAGo platform."""
    if PLATFORM not in hass.data:
        hass.data[PLATFORM] = {}

    host = config.get(CONF_HOST)
    port = config.get(CONF_PORT)
    name = config.get(CONF_NAME)

    ros = await hass.async_add_executor_job(
            connect_to_rosbridge, host, port)

    # while not ros.is_connected:
    #     await asyncio.sleep(1)

    tiago = Tiago(name,ros)
    hass.data[PLATFORM][host] = tiago
    # ros.on_ready
    async_add_entities([tiago], update_before_add=True)


    # # Create handler
    # ros = roslibpy.Ros(host=host, port=port)
    # _LOGGER.info("Initializing communication with host %s", host)

    # # Start the reactor in a separate thread to avoid blocking main thread
    # t = threading.Thread(target=reactor.run, args=(False,))
    # t.daemon = True
    # t.start() 

    # # try:
    # #     with async_timeout.timeout(9):
    # #         while not ros.is_connected:
    # #             await asyncio.sleep(1)
    # # except asyncio.TimeoutError:
    # #     raise PlatformNotReady


class Tiago(RobotROS):
    """Representation of TIAGo robot."""

    def __init__(self, name, ros):
        """Initialize the Tiago handler."""
        self._name = name
        self._ros = ros
        self._state = None
        self._is_connected = None
        self._speed = None
        self._state_attrs = {}

        self.setup_listeners()
        

    @property
    def name(self):
        """Return the name of the sensor."""
        return self._name

    @property
    def state(self):
        """Return the state of the sensor."""
        return self._state

    @property
    def is_connected(self):
        """Return the name of the sensor."""
        return self._is_connected

    @property
    def speed(self):
        """Return the speed of the robot."""
        return self._speed

    @property
    def device_state_attributes(self):
        """Return the state attributes of the device."""
        return self._state_attrs

    def setup_listeners(self):
        _LOGGER.debug("in setup_listeners")
        listener = roslibpy.Topic(self._ros, '/rosout', 'rosgraph_msgs/Log')
        def receive_message(message):
            self._state = message['msg']
        listener.subscribe(receive_message)

# All data has to be fetched inside the update method and cached on the entity.
    async def async_update(self):
        """Retrieve latest state."""
        self._is_connected = self._ros.is_connected
        if not self._ros.is_connected:
            _LOGGER.warning("ROSbridge connection closed")
            self._ros.on_ready(self.setup_listeners)

        state = self.hass.states.get('sun.sun')
        _LOGGER.info(state)
        # pass