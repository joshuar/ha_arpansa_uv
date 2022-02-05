"""Sensor platform for ARPANSA."""
from __future__ import annotations

from .pyarpansa import Arpansa
import inflection
import logging
from datetime import timedelta
from typing import Any, Dict, Optional
import voluptuous as vol

from homeassistant.components.sensor import (
    SensorEntity,
    SensorStateClass,
)

from .const import (
    ATTRIBUTION,
    CONF_LOCATIONS,
    DEFAULT_SCAN_INTERVAL,
)

from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.typing import ConfigType, DiscoveryInfoType
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.config_entries import ConfigEntry
# import homeassistant.helpers.config_validation as cv

_LOGGER = logging.getLogger(__name__)
SCAN_INTERVAL = timedelta(minutes=DEFAULT_SCAN_INTERVAL)

async def async_setup_platform(
    hass: HomeAssistant,
    config: ConfigType,
    async_add_entities: AddEntitiesCallback,
    discovery_info: DiscoveryInfoType | None = None
) -> None:
   """Deprecated setup."""
   pass


async def async_setup_entry(hass, config_entry, async_add_entities: AddEntitiesCallback):
    """Set up ARPANSA UV."""
    sensors = list()

    session = async_get_clientsession(hass)
    arpansa = Arpansa()
    await arpansa.fetchLatestMeasurements(session)

    if config_entry.data[CONF_LOCATIONS] is not None:
        for location in config_entry.data[CONF_LOCATIONS]:
            sensors += [ArpansaSensor(arpansa.getLatest(location))]
    else: 
        for sensor in arpansa.getAllLatest():
            sensors += [ArpansaSensor(sensor)]

    async_add_entities(sensors, update_before_add=True)


class ArpansaSensor(SensorEntity):
    """Representation of an ARPANSA sensor."""
    def __init__(self, details: Dict[str, str]):
        self.details = details
        self._name = details["friendlyname"]
        self._state = None
        self._available = True

    @property
    def name(self) -> str:
        """Return the name of the entity."""
        return self._name + " UV Index"

    @property
    def unique_id(self) -> str:
        """Return the unique ID of the sensor."""
        return self._createSensorName()

    @property
    def available(self) -> bool:
        """Return True if entity is available."""
        return self._available

    @property
    def native_value(self) -> Optional[float]:
        """Return the current value of the sensor."""
        return self._state

    @property
    def icon(self) -> str:
        """Return the icon for the entity."""
        return "mdi:sunglasses"

    @property
    def state_class(self):
        """Return the state class for the entity."""
        return SensorStateClass.MEASUREMENT

    @property
    def attribution(self) -> str:
        """Return the attribution for the sensor data."""
        return ATTRIBUTION

    async def async_update(self):
        """Retrieve latest state."""
        try:
            session = async_get_clientsession(self.hass)
            arpansa = Arpansa()
            await arpansa.fetchLatestMeasurements(session)
            self.details = arpansa.getLatest(self._name)
            if self.details["status"] == "ok":
                self._available = True
                self._state = self.details["index"]
            else:
                self._available = False
        except:
            self._available = False
            _LOGGER.exception("Error retrieving data.")

    def _createSensorName(self):
        """Format the location name into a sensor name."""
        return "arpansa_uv_" + inflection.underscore(self.details["name"])