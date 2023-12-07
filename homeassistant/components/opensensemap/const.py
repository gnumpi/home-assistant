"""Constants for opensensemap."""
from enum import StrEnum
import logging

from homeassistant.const import Platform

LOGGER = logging.getLogger(__package__)

CONF_SCAN_INTERVAL_MIN = "scan_interval"
CONF_STATION_ID = "station_id"

DEFAULT_NAME = "openSenseMap"
DEFAULT_SCAN_INTERVAL_MIN = 10
DOMAIN = "opensensemap"

PLATFORMS = [Platform.SENSOR]


class SensorId(StrEnum):
    """Sensors as defined in opensensemap-api."""

    PM25 = "PM2.5"
    PM10 = "PM10"
    TEMPERATURE = "Temperature"
    HUMIDITY = "Humidity"
    VCC = "VCC"
    PRESSURE = "Air pressure"
    ILLUMINANCE = "Illuminance"
    UV = "UV"
    RADIOACTIVITY = "Radioactivity"
