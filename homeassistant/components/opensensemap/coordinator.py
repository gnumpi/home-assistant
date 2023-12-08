"""Accessing OpenSenseMapApi."""
from datetime import datetime, timedelta
from typing import Any, NamedTuple

from opensensemap_api import _TITLES, OpenSenseMap
from opensensemap_api.exceptions import OpenSenseMapError

from homeassistant.core import HomeAssistant
from homeassistant.exceptions import PlatformNotReady
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .const import LOGGER, SensorTypeId


class SensorDescr(NamedTuple):
    """NamedTuple for describing each reported sensor."""

    title: str
    sensor_type: SensorTypeId
    unit: str
    sensor_hw: str | None


class SensorVal(NamedTuple):
    """NamedTuple for storing received sensor valus."""

    value: str
    at: datetime


class OpenSenseMapDataUpdateCoordinator(DataUpdateCoordinator):
    """My custom coordinator."""

    def __init__(self, hass: HomeAssistant, station_api: OpenSenseMap) -> None:
        """Initialize my coordinator."""
        super().__init__(
            hass,
            LOGGER,
            # Name of the data. For logging purposes.
            name="OpenSenseMapStation",
            # Polling interval. Will only be polled if there are subscribers.
            update_interval=timedelta(minutes=10),
        )
        self.station_api = station_api
        self._sensors: dict[str, SensorDescr] | None = None

        self.units: dict[str, str] = {}
        self._last_update: datetime | None = None
        self._exposure: str | None = None
        self._longitude: float | None = None
        self._latitude: float | None = None

    @property
    def sensors(self) -> dict[str, SensorDescr]:
        """Return the sensor description list."""
        if self._sensors is None:
            raise PlatformNotReady("Coordinator accessed before the first data fetch.")
        return self._sensors

    def get_sensor_descr(self, sensor_id: str) -> SensorDescr:
        """Return the description for the given sensor id."""
        if self._sensors is None:
            raise PlatformNotReady("Coordinator accessed before the first data fetch.")
        return self._sensors[sensor_id]

    def init_coordinator_data(self, data: dict[str, Any]) -> None:
        """Initiate coordinator with received data."""

        self.name = data.get("name", None)

        self._exposure = data.get("exporsure", None)
        if (location := data.get("currentLocation", None)) is not None:
            self._longitude = location.get("coordinates")[0]
            self._latitude = location.get("coordinates")[1]

        knownTitlesForSensor = {
            sId: _TITLES.get(sId.value, ()) + (sId.value,) for sId in SensorTypeId
        }

        self._sensors = {
            s["_id"]: SensorDescr(
                title=s["title"],
                sensor_type=foundIds[0],
                unit=s["unit"],
                sensor_hw=s.get("sensorType", None),
            )
            for s in data["sensors"]
            if len(
                foundIds := [
                    sId
                    for sId in SensorTypeId
                    if s["title"] in knownTitlesForSensor[sId]
                ]
            )
            > 0
        }

    async def _async_update_data(self):
        """Fetch data from API endpoint.

        This is the place to pre-process the data to lookup tables
        so entities can quickly look up their data.
        Result is written into self.data by calling function.
        """
        try:
            await self.station_api.get_data()

        except OpenSenseMapError as err:
            LOGGER.error("Unable to fetch data: %s", err)
            raise UpdateFailed from err

        data = self.station_api.data
        if self._sensors is None:
            try:
                self.init_coordinator_data(data)
            except Exception as err:
                raise UpdateFailed from err

        self._last_update = datetime.fromisoformat(data.get("updatedAt", None))

        return {
            s["_id"]: SensorVal(
                value=s["lastMeasurement"]["value"],
                at=datetime.fromisoformat(s["lastMeasurement"]["createdAt"]),
            )
            for s in data["sensors"]
        }
