"""Config flow for ARPANSA UV Values integration."""
from __future__ import annotations

import logging
from typing import Any

from .pyarpansa import Arpansa, ApiError

import voluptuous as vol

from homeassistant import config_entries
from homeassistant.core import HomeAssistant, callback
from homeassistant.data_entry_flow import FlowResult
from homeassistant.exceptions import HomeAssistantError
import homeassistant.helpers.config_validation as cv
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .const import (
    CONF_LOCATIONS,
    CONF_NAME,
    CONF_POLL_INTERVAL,
    DOMAIN,
    DEFAULT_SCAN_INTERVAL,
    DEFAULT_NAME,
)

_LOGGER = logging.getLogger(__name__)

async def build_schema(
    config_entry: config_entries | None,
    hass: HomeAssistant,
    show_advanced: bool = False,
    step: str = None,
) -> vol.Schema:
    """Build configuration schema.
    :param config_entry: config entry for getting current parameters on None
    :param hass: Home Assistant instance
    :param show_advanced: bool: should we show advanced options?
    :param step: for which step we should build schema
    :return: Configuration schema with default parameters
    """ 
    session = async_get_clientsession(hass)
    arpansa = Arpansa(session)
    try:
        await arpansa.fetchLatestMeasurements()
    except ApiError as err:
        raise CantConnect from err
    locations = arpansa.getAllLocations()
    if step == "config_user":
        return vol.Schema(
            {   
                vol.Required(CONF_NAME,default=DEFAULT_NAME): cv.string,
                vol.Optional(CONF_LOCATIONS): cv.multi_select(locations),
                vol.Optional(CONF_POLL_INTERVAL, default=DEFAULT_SCAN_INTERVAL): cv.positive_int
            }
        )
    if step == "options_user":
        return vol.Schema(
            {   
                vol.Optional(CONF_LOCATIONS): cv.multi_select(locations),
                vol.Optional(CONF_POLL_INTERVAL, default=DEFAULT_SCAN_INTERVAL): cv.positive_int
            }
        )
    if step == None:
        raise UnknownStep


async def validate_input(hass: HomeAssistant, data: dict[str, Any], step_id: str) -> dict[str, Any]:
    """Validate the user input allows us to connect.

    Data has the keys from build_schema() with values provided by the user.
    """
    # TODO validate the data can be used to set up a connection.
    return data


class ConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for ARPANSA UV Values."""

    VERSION = 1
    CONNECTION_CLASS = config_entries.CONN_CLASS_CLOUD_POLL

    def __init__(self):
        """Initialize."""
        self._errors = {}

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Get values from user."""
        try:
            config_schema = await build_schema(
                config_entry=None,
                hass=self.hass,
                show_advanced=self.show_advanced_options,
                step = "config_user",
            )
        except CantConnect:
            _LOGGER.exception("Could not connect")
            self._errors["base"] = "cannot_connect"
        except UnknownStep:
            _LOGGER.exception("No step defined")
            self._errors["base"] = "unknown_step"
        except Exception:  # pylint: disable=broad-except
            _LOGGER.exception("Unexpected exception")
            self._errors["base"] = "unknown"
        finally:
            if user_input is None:
                return self.async_show_form(
                    step_id="user", data_schema=config_schema,errors=self._errors
                )
            else:              
                options = await validate_input(self.hass, data=user_input, step_id="user")
                _LOGGER.debug(f"Creating config with: {user_input}")
                return self.async_create_entry(title=options[CONF_NAME], data=options)
    
    @staticmethod
    @callback
    def async_get_options_flow(
        config_entry: config_entries.ConfigEntry,
    ) -> OptionsFlowHandler:
        return OptionsFlowHandler(config_entry)        

class OptionsFlowHandler(config_entries.OptionsFlow):
    """Handle a options flow for ARPANSA UV Values."""

    def __init__(self, config_entry):
        """Initialize HACS options flow."""
        self.config_entry = config_entry
        self.options = dict(config_entry.options)
        self._errors = {}


    async def async_step_init(self, user_input=None):  # pylint: disable=unused-argument
        """Manage the options."""
        return await self.async_step_user()

    async def async_step_user(self, user_input=None):
        """Handle a flow initialized by the user."""
        try:
            config_schema = await build_schema(
                config_entry=self.config_entry,
                hass=self.hass,
                show_advanced=self.show_advanced_options,
                step = "options_user",
            )
        except CantConnect:
            _LOGGER.exception("Could not connect")
            self._errors["base"] = "cannot_connect"
        except UnknownStep:
            _LOGGER.exception("No step defined")
            self._errors["base"] = "unknown_step"
        except Exception:  # pylint: disable=broad-except
            _LOGGER.exception("Unexpected exception")
            self._errors["base"] = "unknown"
        finally:
            if user_input is None:
                return self.async_show_form(
                    step_id="user", data_schema=config_schema,errors=self._errors
                )
            else:
                self.options.update(user_input)              
                options = await validate_input(self.hass, data=self.options, step_id="user")
                _LOGGER.debug(f"Recreating config for {self.config_entry.data.get(CONF_NAME)} with options: {options}")
                return self.async_create_entry(title=self.config_entry.data.get(CONF_NAME), data=options)

class CantConnect(HomeAssistantError):
    """Error to indicate failure to connect to API."""

class UnknownStep(HomeAssistantError):
    """Error to indicate the config step was not known."""