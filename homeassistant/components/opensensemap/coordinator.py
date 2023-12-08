"""Accessing OpenSenseMapApi."""

from datetime import timedelta

from opensensemap_api import _TITLES, OpenSenseMap
from opensensemap_api.exceptions import OpenSenseMapError

from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .const import LOGGER, SensorId


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
        self._sensor_ids: list[SensorId] | None = None
        self.units: dict[str, str] = {}

    async def receive_station_sensor_ids(self) -> list[SensorId]:
        """Fetch data an return which sensors are available."""
        if self._sensor_ids is None:
            try:
                await self.station_api.get_data()
            except OpenSenseMapError as err:
                LOGGER.error("Unable to fetch data: %s", err)
                raise UpdateFailed from err

            self._sensor_ids = [
                sId
                for sId in SensorId
                if self.station_api.get_value(sId.value) is not None
            ]
        return self._sensor_ids

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

        if (name := self.station_api.name) is not None:
            self.name = name

        self.units = {
            sId.value: entry["unit"]
            for sId in SensorId
            for entry in self.station_api.data["sensors"]
            if entry["title"] in _TITLES.get(sId.value, ()) + (sId.value,)
        }

        return {
            sId.value: measure
            for sId in SensorId
            if (measure := self.station_api.get_value(sId.value)) is not None
        }
