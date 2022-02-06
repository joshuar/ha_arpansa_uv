"""Sensor platform for ARPANSA."""
from __future__ import annotations

from .pyarpansa import Arpansa
import inflection
import logging
from datetime import (
    date,
    datetime,
    timedelta,
)
from typing import Any, Dict, Optional
from collections.abc import Mapping
import async_timeout
import voluptuous as vol

from homeassistant.components.sensor import (
    SensorEntity,
    SensorStateClass,
    StateType,
)

from .const import (
    DOMAIN,
    ATTRIBUTION,
    CONF_LOCATIONS,
    CONF_API,
    DEFAULT_SCAN_INTERVAL,
)

from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.typing import ConfigType, DiscoveryInfoType
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.config_entries import ConfigEntry
from homeassistant.exceptions import ConfigEntryAuthFailed
from homeassistant.helpers.update_coordinator import (
    CoordinatorEntity,
    DataUpdateCoordinator,
    UpdateFailed,
)
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
    api = hass.data[DOMAIN][config_entry.entry_id].get(CONF_API)

    async def async_update_data():
        """Fetch data from API endpoint.

        This is the place to pre-process the data to lookup tables
        so entities can quickly look up their data.
        """
        session = async_get_clientsession(hass)
        try:
            # Note: asyncio.TimeoutError and aiohttp.ClientError are already
            # handled by the data update coordinator.
            async with async_timeout.timeout(10):
                await api.fetchLatestMeasurements(session)
                return api
        # except ApiAuthError as err:
        #     # Raising ConfigEntryAuthFailed will cancel future updates
        #     # and start a config flow with SOURCE_REAUTH (async_step_reauth)
        #     raise ConfigEntryAuthFailed from err
        except:# ApiError as err:
            #raise UpdateFailed(f"Error communicating with API: {err}")
            raise UpdateFailed(f"Error communicating with API")

    coordinator = DataUpdateCoordinator(
        hass,
        _LOGGER,
        # Name of the data. For logging purposes.
        name="arpansa",
        update_method=async_update_data,
        # Polling interval. Will only be polled if there are subscribers.
        update_interval=SCAN_INTERVAL,
    )

    await coordinator.async_config_entry_first_refresh()

    # session = async_get_clientsession(hass)
    # await api.fetchLatestMeasurements(session)

    sensors = list()
    if config_entry.data[CONF_LOCATIONS] is not None:
        for location in config_entry.data[CONF_LOCATIONS]:
            sensors += [ArpansaSensor(coordinator,coordinator.data.getLatest(location))]
    else: 
        for sensor in coordinator.data.getAllLatest():
            sensors += [ArpansaSensor(coordinator,sensor)]

    async_add_entities(sensors, update_before_add=True)


class ArpansaSensor(CoordinatorEntity,SensorEntity):
    """Representation of an ARPANSA sensor."""
    def __init__(self, coordinator, details: Dict[str, str]):
        self.details = details
        self._name = details["friendlyname"]
        self._state = None
        self._available = True
        """Pass coordinator to CoordinatorEntity."""
        super().__init__(coordinator)

    @property
    def name(self) -> str | None:
        """Return the name of the entity."""
        return self._name + " UV Index"

    @property
    def unique_id(self) -> str | None:
        """Return the unique ID of the sensor."""
        return self._createSensorName()

    @property
    def available(self) -> bool:
        """Return True if entity is available."""
        self.details = self.coordinator.data.getLatest(self._name)
        if self.details["status"] == "ok":
            self._available = True
        else:
            self._available = False
        return self._available

    @property
    def native_value(self) -> StateType | date | datetime:
        """Return the current value of the sensor."""
        self.details = self.coordinator.data.getLatest(self._name)
        self._state = self.details["index"]
        _LOGGER.debug(f"latest value for {self._name} is {self._state}")
        return self._state

    @property
    def icon(self) -> str | None:
        """Return the icon for the entity."""
        return "mdi:sunglasses"

    @property
    def state_class(self) -> SensorStateClass | str | None:
        """Return the state class for the entity."""
        return SensorStateClass.MEASUREMENT

    @property
    def extra_state_attributes(self) -> Mapping[str, Any] | None:
        self.details = self.coordinator.data.getLatest(self._name)
        extra_info = {}
        extra_info["Last Updated (UTC)"] = self.details["utcdatetime"]
        extra_info["Status"] = self.details["status"]
        return extra_info

    @property
    def attribution(self) -> str | None:
        """Return the attribution for the sensor data."""
        return ATTRIBUTION

    async def async_update(self):
        """Retrieve latest state."""
        await self.coordinator.async_request_refresh()

    def _createSensorName(self):
        """Format the location name into a sensor name."""
        return "arpansa_uv_" + inflection.underscore(self.details["name"])