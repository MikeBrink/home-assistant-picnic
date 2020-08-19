"""Support for Picnic sensors"""

import logging
from datetime import datetime, timedelta
import voluptuous as vol

import homeassistant.helpers.config_validation as cv
from homeassistant.components.sensor import PLATFORM_SCHEMA
from homeassistant.helpers.entity import Entity
from homeassistant.util import Throttle
from homeassistant.const import (
    CONF_PASSWORD,
    CONF_USERNAME,
)

from python_picnic_api import PicnicAPI

MIN_TIME_BETWEEN_UPDATES = timedelta(minutes=15)

_LOGGER = logging.getLogger(__name__)

SLOT_TIMES = ["window_start", "window_end", "cut_off_time"]

COUNTRY_CODE = "country_code"

CART_ICON = "mdi:cart"
CART_NAME = "picnic_cart"

DELIVERY_ICON = "mdi:truck-delivery"
DELIVERY_NAME = "picnic_delivery"

DELIVERY_TIME_SLOT_ICON = "mdi:calendar-clock"
DELIVERY_TIME_SLOT_NAME = "picnic_delivery_time_slots"

ATTRIBUTION = "Information provided by Picnic.app"

ATTR_ATTRIBUTION = "attribution"
ATTR_DELIVERIES = "deliveries"
ATTR_TIME_SLOTS = "time_slots"
ATTR_PRICE = "price"

PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend(
    {
        vol.Required(CONF_USERNAME): cv.string,
        vol.Required(CONF_PASSWORD): cv.string,
        vol.Optional(COUNTRY_CODE, default="NL"): cv.string,
    }
)


async def async_setup_platform(hass, config, async_add_entities, discovery_info=None):
    """Set up the Picnic sensor"""

    username = config.get(CONF_USERNAME)
    password = config.get(CONF_PASSWORD)
    country_code = config.get(COUNTRY_CODE)

    api = PicnicAPI(username=username, password=password, country_code=country_code)
    data = PicnicData(hass, config, api)

    entities = [CartSensor(data), DeliverySensor(data), DeliveryTimeSlotSensor(data)]
    async_add_entities(entities, True)


class PicnicData:
    """Handle Picnic data object"""

    def __init__(self, hass, config, api):
        """Initialize the data object"""
        self._api = api
        self.hass = hass
        self.cart = None
        self.open_deliveries = {}
        self.open_delivery_time_slots = {}

    @Throttle(MIN_TIME_BETWEEN_UPDATES)
    async def async_update(self):
        """Update data"""
        await self.hass.async_add_executor_job(self._get_data)

    def _get_data(self):
        #        try:
        self.cart = self._api.get_cart()
        self.current_deliveries = self._api.get_current_deliveries()
        self.open_delivery_time_slots = self.cart["delivery_slots"]
        _LOGGER.debug("Updated data from Picnic")


#       Not yet implemented in python_picnic_api
#        except UnauthorizedException:
#            _LOGGER.error("Can't connect to the Picnic API. Is your username/password valid?")


class CartSensor(Entity):
    """Cart Sensor class"""

    def __init__(self, data):
        self.attr = {}
        self._state = None
        self._data = data
        self._attributes = {
            ATTR_ATTRIBUTION: ATTRIBUTION,
            ATTR_PRICE: None,
        }

    async def async_update(self):
        """Update the sensor"""
        await self._data.async_update()

        if self._data.cart is None:
            return

        self._state = self._data.cart["total_count"]
        self._attributes[ATTR_PRICE] = self._data.cart["total_price"]

    @property
    def name(self):
        """Return the name of the sensor"""
        return CART_NAME

    @property
    def state(self):
        """Return the state of the sensor"""
        return self._state

    @property
    def icon(self):
        """Return the icon of the sensor"""
        return CART_ICON

    @property
    def device_state_attributes(self):
        """Return the state attributes"""
        return self._attributes


class DeliverySensor(Entity):
    """Delivery Sensor class"""

    def __init__(self, data):
        self.attr = {}
        self._state = None
        self._data = data
        self._attributes = {
            ATTR_ATTRIBUTION: ATTRIBUTION,
            ATTR_DELIVERIES: [],
        }

    # updaten met current_delivery
    # self.id = data.get("id")
    # self.status = data.get("status").lower()
    # self.date = date.strftime("%Y-%m-%d")
    # self.time = data.get("delivery").get("time")
    # self.start_time = datetime.fromtimestamp(int(data.get("delivery").get("startDateTime")) / 1000)
    # self.end_time = datetime.fromtimestamp(int(data.get("delivery").get("endDateTime")) / 1000)
    # self.cut_off_date = datetime.fromtimestamp(int(details.get("orderCutOffDate")) / 1000)
    # self.price = Price(data.get("prices").get("total"))
    async def async_update(self):
        """Update the sensor"""
        await self._data.async_update()

        self._attributes[ATTR_DELIVERIES] = []
        self._state = None

        deliveries = self._data.current_deliveries

        for delivery in deliveries:
            # TODO: Not happy with this solution
            if not isinstance(delivery.price, dict):
                p = vars(delivery.price)
                delivery.price = p
            self._attributes[ATTR_DELIVERIES].append(vars(delivery))

        if len(deliveries) > 0:
            first = next(iter(deliveries))
            self._state = first.status.lower()
        else:
            self._state = None

    @property
    def name(self):
        """Return the name of the sensor"""
        return DELIVERY_NAME

    @property
    def state(self):
        """Return the state of the sensor"""
        return self._state

    @property
    def icon(self):
        """Return the icon of the sensor"""
        return DELIVERY_ICON

    @property
    def device_state_attributes(self):
        """Return the state attributes"""
        return self._attributes


class DeliveryTimeSlotSensor(Entity):
    """Delivery Time Slot Sensor class"""

    def __init__(self, data):
        self.attr = {}
        self._state = None
        self._data = data
        self._attributes = {
            ATTR_ATTRIBUTION: ATTRIBUTION,
            ATTR_TIME_SLOTS: [],
        }

    async def async_update(self):
        """Update the sensor"""
        await self._data.async_update()

        self._attributes[ATTR_TIME_SLOTS] = self._data.open_delivery_time_slots
        self._state = None

        for time in SLOT_TIMES:
            self._attributes[ATTR_TIME_SLOTS][time] = datetime.fromisoformat(
                self.attributes[ATTR_TIME_SLOTS][time]
            )

        if len(self._attributes[ATTR_TIME_SLOTS]) > 0:
            self._state = self._attributes[ATTR_TIME_SLOTS][0]["window_start"]
        else:
            self._state = None

    @property
    def name(self):
        """Return the name of the sensor"""
        return DELIVERY_TIME_SLOT_NAME

    @property
    def state(self):
        """Return the state of the sensor"""
        return self._state

    @property
    def icon(self):
        """Return the icon of the sensor"""
        return DELIVERY_TIME_SLOT_ICON

    @property
    def device_state_attributes(self):
        """Return the state attributes"""
        return self._attributes
