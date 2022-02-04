"""Config flow for ARPANSA UV Values integration."""
from __future__ import annotations
from ast import Str
from gc import callbacks

import logging
from typing import Any
from wsgiref import validate

import voluptuous as vol

from homeassistant import config_entries
from homeassistant.core import (
    HomeAssistant,
    callback
)
from homeassistant.data_entry_flow import FlowResult
from homeassistant.exceptions import HomeAssistantError

from .const import (
    DOMAIN,
    DEFAULT_SCAN_INTERVAL,
    DEFAULT_NAME,
)

_LOGGER = logging.getLogger(__name__)

def build_config_schema(
    config_entry: config_entries | None,
    hass: HomeAssistant,
    show_advanced: bool = False,
    step: str = "user",
) -> vol.Schema:
    """Build configuration schema.
    :param config_entry: config entry for getting current parameters on None
    :param hass: Home Assistant instance
    :param show_advanced: bool: should we show advanced options?
    :param step: for which step we should build schema
    :return: Configuration schema with default parameters
    """ 
    schema = vol.Schema(
        {   
            vol.Required("name",description={"suggested_value": DEFAULT_NAME}): str,
        }
    )

    # if show_advanced:

    return schema

def build_options_schema(
    config_entry: config_entries | None,
    hass: HomeAssistant,
    show_advanced: bool = False,
    step: str = "user",
) -> vol.Schema:
    """Build configuration schema.
    :param config_entry: config entry for getting current parameters on None
    :param hass: Home Assistant instance
    :param show_advanced: bool: should we show advanced options?
    :param step: for which step we should build schema
    :return: Configuration schema with default parameters
    """
    return vol.Schema(
            {
                vol.Required("poll_interval", description={"suggested_value": DEFAULT_SCAN_INTERVAL}): vol.Range(min=1),
            }
        )



# class PlaceholderHub:
#     """Placeholder class to make tests pass.

#     TODO Remove this placeholder class and replace with things from your PyPI package.
#     """

#     def __init__(self, poll_interval: int) -> None:
#         """Initialize."""
#         self.poll_interval = poll_interval

#     # async def authenticate(self, username: str, password: str) -> bool:
#     #     """Test if we can authenticate with the host."""
#     #     return True


async def validate_input(hass: HomeAssistant, data: dict[str, Any], step_id: str) -> dict[str, Any]:
    """Validate the user input allows us to connect.

    Data has the keys from build_schema() with values provided by the user.
    """
    # TODO validate the data can be used to set up a connection.
    validated_input = {}

    # If your PyPI package is not built with async, pass your methods
    # to the executor:
    # await hass.async_add_executor_job(
    #     your_validate_func, data["username"], data["password"]
    # )

    # hub = PlaceholderHub(data["poll_interval"])

    # if not await hub.authenticate(data["username"], data["password"]):
    #     raise InvalidAuth

    # If you cannot connect:
    # throw CannotConnect
    # If the authentication is wrong:
    # InvalidAuth
    _LOGGER.info(f"Input to validate is {data}")

    validated_input = data

    # Return info that you want to store in the config entry.
    return validated_input


class ConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for ARPANSA UV Values."""

    VERSION = 1

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Get values from user."""
        info = {}
        errors = {}

        config_schema = build_config_schema(
            config_entry=None,
            hass=self.hass,
            show_advanced=self.show_advanced_options,
        )

        if user_input is None:
            return self.async_show_form(
                step_id="user", data_schema=config_schema
            )
        try:
            info = await validate_input(self.hass, data=user_input, step_id="user")
        except CannotConnect:
            errors["base"] = "cannot_connect"
        except InvalidAuth:
            errors["base"] = "invalid_auth"
        except Exception:  # pylint: disable=broad-except
            _LOGGER.exception("Unexpected exception")
            errors["base"] = "unknown"
        else:
            return self.async_create_entry(title=info["name"], data=user_input)

        return self.async_show_form(
            step_id="user", data_schema=config_schema, errors=errors
        )

    @staticmethod
    @callback
    def async_get_options_flow(config_entry):
        return OptionsFlowHandler(config_entry)        

class OptionsFlowHandler(config_entries.OptionsFlow):
    def __init__(self, config_entry):
        """Initialize options flow."""
        self.config_entry = config_entry

    async def async_step_init(self, user_input=None):
        """Manage the options."""
        errors = {}

        options_schema = build_options_schema(
            config_entry=None,
            hass=self.hass,
        )

        if user_input is None:
            return self.async_show_form(
                step_id="init", data_schema=options_schema
            )

        try:
            await validate_input(self.hass, data=user_input, step_id="init")
        except Exception:  # pylint: disable=broad-except
            _LOGGER.exception("Unexpected exception")
            errors["base"] = "unknown"
        else:
            return self.async_create_entry(title="", data=user_input)

        return self.async_show_form(
            step_id="init", data_schema=options_schema, errors=errors
        )


class CannotConnect(HomeAssistantError):
    """Error to indicate we cannot connect."""


class InvalidAuth(HomeAssistantError):
    """Error to indicate there is invalid auth."""
