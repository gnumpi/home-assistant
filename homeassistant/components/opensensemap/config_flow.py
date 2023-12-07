"""Config flow for OpenSenseMap."""
from typing import Any

import voluptuous as vol

from homeassistant.config_entries import ConfigFlow
from homeassistant.data_entry_flow import FlowResult
import homeassistant.helpers.config_validation as cv

from .const import (
    CONF_SCAN_INTERVAL_MIN,
    CONF_STATION_ID,
    DEFAULT_NAME,
    DEFAULT_SCAN_INTERVAL_MIN,
    DOMAIN,
)


class OpenSenseMapConfigFlowHandler(ConfigFlow, domain=DOMAIN):
    """Config flow handler for OpenSky."""

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Initialize user input."""
        if user_input is not None:
            return self.async_create_entry(
                title=DEFAULT_NAME,
                data={
                    CONF_STATION_ID: user_input[CONF_STATION_ID],
                },
                options={
                    CONF_SCAN_INTERVAL_MIN: user_input[CONF_SCAN_INTERVAL_MIN],
                },
            )

        return self.async_show_form(
            step_id="user",
            data_schema=self.add_suggested_values_to_schema(
                vol.Schema(
                    {
                        vol.Required(CONF_STATION_ID): cv.string,
                        vol.Required(CONF_SCAN_INTERVAL_MIN): cv.positive_int,
                    }
                ),
                {CONF_SCAN_INTERVAL_MIN: DEFAULT_SCAN_INTERVAL_MIN},
            ),
        )
