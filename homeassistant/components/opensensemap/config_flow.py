"""Config flow for OpenSenseMap."""
from typing import Any

from opensensemap_api import OpenSenseMap
from opensensemap_api.exceptions import OpenSenseMapError
import voluptuous as vol

from homeassistant.config_entries import ConfigFlow
from homeassistant.data_entry_flow import FlowResult
from homeassistant.helpers.aiohttp_client import async_get_clientsession
import homeassistant.helpers.config_validation as cv

from .const import CONF_STATION_ID, DOMAIN


class OpenSenseMapConfigFlowHandler(ConfigFlow, domain=DOMAIN):
    """Config flow handler for OpenSky."""

    VERSION = 1

    def __init__(self) -> None:
        """Initialize flow."""
        self._station_id: str | None = None
        self._station_name: str | None = None

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None, error: str | None = None
    ) -> FlowResult:
        """Handle a flow initialized by the user."""

        if user_input is not None:
            self._station_id = user_input[CONF_STATION_ID]
            return await self._async_try_fetch_station_info()

        errors = {}
        if error is not None:
            errors["base"] = error

        return self.async_show_form(
            step_id="user",
            errors=errors,
            data_schema=vol.Schema({vol.Required(CONF_STATION_ID): cv.string}),
        )

    async def _async_try_fetch_station_info(self) -> FlowResult:
        """Try to fetch station info and return any errors."""
        station_api = OpenSenseMap(self._station_id, async_get_clientsession(self.hass))
        try:
            await station_api.get_data()

        except OpenSenseMapError:
            return self.async_abort(reason="can_not_connect")

        if (name := station_api.data.get("name", None)) is None:
            return await self.async_step_user(user_input=None, error="wrong_id")

        self._station_name = name
        config_data = {CONF_STATION_ID: self._station_id}

        return self.async_create_entry(title=name, data=config_data)
