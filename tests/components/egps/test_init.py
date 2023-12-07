"""Tests for setting up egps integration."""

from typing import Final

from homeassistant.components.egps.const import CONF_DEVICE_API_ID, DOMAIN
from homeassistant.config_entries import ConfigEntryState
from homeassistant.const import CONF_NAME
from homeassistant.core import HomeAssistant

from tests.common import MockConfigEntry

DEMO_CONFIG_ENTRY: Final = {
    CONF_NAME: "Unite Test",
    CONF_DEVICE_API_ID: "DYPS:00:11:22",
}


async def test_load_unload_entry(hass: HomeAssistant) -> None:
    """Test loading and unloading the integration."""
    entry = MockConfigEntry(domain=DOMAIN, data=DEMO_CONFIG_ENTRY)
    entry.add_to_hass(hass)
    await hass.config_entries.async_setup(entry.entry_id)
    await hass.async_block_till_done()

    assert entry.state == ConfigEntryState.LOADED
    assert entry.entry_id in hass.data[DOMAIN]

    assert await hass.config_entries.async_unload(entry.entry_id)
    await hass.async_block_till_done()

    assert entry.state is ConfigEntryState.NOT_LOADED
    assert entry.entry_id not in hass.data[DOMAIN]
