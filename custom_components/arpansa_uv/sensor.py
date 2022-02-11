"""Sensor platform for ARPANSA."""
from __future__ import annotations

import inflection
import logging
from datetime import (
    date,
    datetime,
)
from typing import Any, Dict
from collections.abc import Mapping

from homeassistant.components.sensor import (
    SensorEntity,
    SensorStateClass,
    StateType,
)

from .const import (
    DOMAIN,
    ATTRIBUTION,
    CONF_LOCATIONS,
)

from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(hass, config_entry, async_add_entities: AddEntitiesCallback):
    """Set up ARPANSA UV."""
    coordinator = hass.data[DOMAIN][config_entry.entry_id]

    sensors = list()
    locations = list()
    if config_entry.data[CONF_LOCATIONS] is not None:
        for location in config_entry.data[CONF_LOCATIONS]:
            _LOGGER.debug(f"Getting latest data for location {location}")
            locations += [coordinator.api.getLatest(location)]
    else: 
        locations = coordinator.api.getAllLatest()

    for details in locations:
        _LOGGER.debug(f"Creating sensor from {details}")
        sensors += [ArpansaSensor(coordinator,details)]

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
    def should_poll(self) -> bool:
        return True

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