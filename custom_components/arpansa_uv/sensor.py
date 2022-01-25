"""Platform for ARPANSA sensors integration"""
from .arpansa import Arpansa
import inflection
import logging
from datetime import timedelta
from typing import Any, Dict, Optional

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorStateClass,
)

from homeassistant.const import (
    ATTR_ATTRIBUTION,
)
from .const import (
    ATTRIBUTION
)

from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.typing import ConfigType, DiscoveryInfoType
from homeassistant.helpers.aiohttp_client import async_get_clientsession
# import homeassistant.helpers.config_validation as cv

_LOGGER = logging.getLogger(__name__)
SCAN_INTERVAL = timedelta(minutes=1)

async def async_setup_platform(
    hass: HomeAssistant,
    config: ConfigType,
    async_add_entities: AddEntitiesCallback,
    discovery_info: DiscoveryInfoType | None = None
) -> None:
    """Set up the sensor platform."""
    session = async_get_clientsession(hass)
    arpansa = Arpansa()
    await arpansa.fetchLatestMeasurements(session)
    sensors = list()
    for measurement in arpansa.getAllLatest():
        sensors += [ArpansaSensor(measurement)]
    async_add_entities(sensors, update_before_add=True)

class ArpansaSensor(SensorEntity):
    """Representation of an ARPANSA sensor."""
    def __init__(self, measurement: Dict[str, str]):
        self.measurement = measurement
        self._state = None
        self._available = True

    @property
    def name(self) -> str:
        """Return the name of the entity."""
        return self.measurement["name"] + " UV Index"

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
        try:
            session = async_get_clientsession(self.hass)
            arpansa = Arpansa()
            await arpansa.fetchLatestMeasurements(session)
            self._state = arpansa.getLatest(self.measurement["name"])
        except:
            self._available = False
            _LOGGER.exception("Error retrieving data.")

    def _createSensorName(self):
        """Format the location name into a sensor name."""
        return "arpansa_uv_" + inflection.underscore(self.measurement["name"])