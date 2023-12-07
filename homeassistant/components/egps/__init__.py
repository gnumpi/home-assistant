"""Energenie Power-Management integration."""
import pyegps

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant

from .const import CONF_DEVICE_API_ID, DOMAIN

pyegps.use_dummy_devices()


PLATFORMS: list[str] = ["switch"]


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Energenie Powerstrip."""

    if DOMAIN in hass.data and entry.entry_id in hass.data[DOMAIN]:
        return False

    config = entry.data
    powerstrip = pyegps.get_device(config[CONF_DEVICE_API_ID])
    hass.data.setdefault(DOMAIN, {})[entry.entry_id] = powerstrip
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload config entry."""
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)

    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id)

    return unload_ok
