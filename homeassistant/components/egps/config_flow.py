"""ConfigFlow for EGPS devices."""
import logging
import re
from typing import Any

from pyegps import Device, get_device, search_for_devices
import voluptuous as vol

from homeassistant import config_entries, exceptions
from homeassistant.components import usb
from homeassistant.data_entry_flow import FlowResult
from homeassistant.helpers.selector import selector

from .const import CONF_DEVICE_API_ID, DOMAIN

_LOGGER = logging.getLogger(__name__)


class ConfigFLow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle the config flow for EGPM devices."""

    VERSION = 1

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Initiate user flow."""

        if user_input is not None:
            if "device-id" in user_input:
                mObj = re.search(r"\((.*?)\)", user_input["device-id"])
                if mObj is None:
                    return self.async_abort(reason="incompatible-device-id")

                devId = mObj.group(1)
                dev: Device | None = get_device(device_id=devId)
                if dev is not None:
                    await self.async_set_unique_id(dev.device_id)
                    self._abort_if_unique_id_configured()

                    return self.async_create_entry(
                        title=f"{devId}",
                        data={CONF_DEVICE_API_ID: devId},
                    )
            return self.async_abort(reason="device_not_found")

        currently_configured = self._async_current_ids(include_ignore=True)
        devices = [
            d
            for d in search_for_devices()
            if d.get_device_type() == "PowerStrip"
            and d.device_id not in currently_configured
        ]
        if len(devices) > 0:
            data_schema = {
                "device-id": selector(
                    {
                        "select": {
                            "options": [f"{d.name} ({d.device_id})" for d in devices],
                        }
                    }
                )
            }
        else:
            return self.async_abort(reason="no_device")

        return self.async_show_form(step_id="user", data_schema=vol.Schema(data_schema))

    async def async_step_usb(self, discovery_info: usb.UsbServiceInfo) -> FlowResult:
        """Initiate flow when a device as detected."""
        return self.async_show_form(step_id="user")


class NoDeviceFound(exceptions.HomeAssistantError):
    """Error to indicate there is no supported device connected."""
