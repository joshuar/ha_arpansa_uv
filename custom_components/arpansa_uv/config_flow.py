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
    # match step:
    #     case "user":
    if step == "user":
        arpansa = Arpansa()
        session = async_get_clientsession(hass)
        try:
            await arpansa.fetchLatestMeasurements(session)
        except ApiError as err:
            raise CantConnect from err
        locations = arpansa.getAllLocations()
        return vol.Schema(
            {   
                vol.Required(CONF_NAME,default=DEFAULT_NAME): cv.string,
                vol.Optional(CONF_LOCATIONS): cv.multi_select(locations),
            }
        )
        # case "init":
    if step == "init":
        return vol.Schema(
                {
                    vol.Required(CONF_POLL_INTERVAL, default=DEFAULT_SCAN_INTERVAL): vol.Range(min=1),
                }
            )
        # case None:
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

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Get values from user."""
        errors = {}

        try:
            config_schema = await build_schema(
                config_entry=None,
                hass=self.hass,
                show_advanced=self.show_advanced_options,
                step = "user",
            )
            if user_input is None:
                return self.async_show_form(
                    step_id="user", data_schema=config_schema
                )
            else:              
                info = await validate_input(self.hass, data=user_input, step_id="user")
                _LOGGER.debug(f"Creating config with data: {user_input}")
                return self.async_create_entry(title=info[CONF_NAME], data=user_input)
            # return self.async_show_form(
            #     step_id="user", data_schema=config_schema, errors=errors
            # )
        except CantConnect:
            _LOGGER.exception("Could not connect")
            errors["base"] = "cannot_connect"
        except UnknownStep:
            _LOGGER.exception("No step defined")
            errors["base"] = "unknown_step"
        except Exception:  # pylint: disable=broad-except
            _LOGGER.exception("Unexpected exception")
            errors["base"] = "unknown"

    
    @staticmethod
    @callback
    def async_get_options_flow(
        config_entry: config_entries.ConfigEntry,
    ) -> OptionsFlowHandler:
        return OptionsFlowHandler(config_entry)        

class OptionsFlowHandler(config_entries.OptionsFlow):
    """Handle a options flow for ARPANSA UV Values."""
    def __init__(self, config_entry: config_entries.ConfigEntry) -> None:
        """Initialize options flow."""
        self.config_entry = config_entry

    async def async_step_init(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Manage the options."""
        options_schema = await build_schema(
            config_entry=self.config_entry,
            hass=self.hass,
            step = "init",
        )

        if user_input is None:
            return self.async_show_form(
                step_id="init", data_schema=options_schema)

        _LOGGER.debug(f"Creating options with data: {user_input}")
        return self.async_create_entry(title="", data=user_input)

class CantConnect(HomeAssistantError):
    """Error to indicate failure to connect to API."""

class UnknownStep(HomeAssistantError):
    """Error to indicate the config step was not known."""