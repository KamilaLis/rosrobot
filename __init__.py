"""
Component to interface with ROS robots.

For more details about this component, please refer to the documentation at
...
"""
import asyncio
import async_timeout

from datetime import timedelta
import logging

import voluptuous as vol

# from homeassistant.components import websocket_api
import homeassistant.helpers.config_validation as cv
from homeassistant.helpers.config_validation import PLATFORM_SCHEMA 
from homeassistant.helpers.entity import Entity
from homeassistant.helpers.entity_component import EntityComponent

DOMAIN = "rosrobot"
DEPENDENCIES = []
# Python libraries or modules that you would normally install using pip
REQUIREMENTS = []

_LOGGER = logging.getLogger(__name__)

SCAN_INTERVAL = timedelta(seconds=30)

ATTR_STATUS = 'status'
ATTR_CONNECTED = 'is_connected'

# CONF_TEXT = 'text'
# DEFAULT_TEXT = 'No text!'

# CONFIG_SCHEMA = vol.Schema({
#     DOMAIN: vol.Schema({
#         # Optional/Required
#       vol.Required(CONF_TEXT): cv.string,
#     })
# }, extra=vol.ALLOW_EXTRA)

# _SERVICE_MAP = {
#     'light_flash': 'trigger_remote_light_flash',
#     'sound_horn': 'trigger_remote_horn',
#     'activate_air_conditioning': 'trigger_remote_air_conditioning',
# }

async def async_setup(hass, config):
#     """Set up ROS robot component."""
    component = hass.data[DOMAIN] = EntityComponent(
        _LOGGER, DOMAIN, hass, SCAN_INTERVAL)
    await component.async_setup(config)

    # # TODO: register services 
    # component.async_register_entity_service(
    #     SERVICE_LOCATE, VACUUM_SERVICE_SCHEMA,
    #     'async_locate'
    # )

    _LOGGER.debug("The rosrobot component is ready!")

    return True


async def async_setup_entry(hass, entry):
    """Set up a config entry."""
    return await hass.data[DOMAIN].async_setup_entry(entry)


async def async_unload_entry(hass, entry):
    """Unload a config entry."""
    return await hass.data[DOMAIN].async_unload_entry(entry)


class RobotROS(Entity):
    """Representation of a robot using ROS."""

    @property
    def status(self):
        """Return the robot status."""
        return None

    @property
    def state_attributes(self):
        """Return the state attributes of the robot."""
        data = {}

        if self.status is not None:
            data[ATTR_STATUS] = self.status

        if self.is_connected is not None:
            data[ATTR_CONNECTED] = self.is_connected

        # if self.battery_level is not None:
        #     data[ATTR_BATTERY_LEVEL] = self.battery_level
        #     data[ATTR_BATTERY_ICON] = self.battery_icon

        return data

def connect_to_rosbridge(host, port):
    """ Start connection with Rosbridge server. """
    import roslibpy
    import threading
    from twisted.internet import reactor

    ros = roslibpy.Ros(host=host, port=port)
    _LOGGER.info("Initializing communication with host %s", host)

    # Start the reactor in a separate thread to avoid blocking main thread
    t = threading.Thread(target=reactor.run, args=(False,))
    t.daemon = True
    t.start() 

    return ros

    # EVENTS
    # # Fire event my_cool_event with event data answer=42
    # hass.bus.fire('my_cool_event', {
    #     'answer': 42
    # })

    # # Listener to handle fired events
    # def handle_event(event):
    #     nonlocal count
    #     count += 1
    #     print('Total events received:', count)

    # # Listen for when my_cool_event is fired
    # hass.bus.listen('my_cool_event', handle_event)

    # SERVICES
    # def handle_hello(call):
    #     name = call.data.get(ATTR_NAME, DEFAULT_NAME)

    #     hass.states.set('hello_service.hello', name)

    # hass.services.register(DOMAIN, 'hello', handle_hello)

