"""Sensor for openSenseMap."""

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorStateClass,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.device_registry import DeviceEntryType, DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import CONF_STATION_ID, DOMAIN, SensorId
from .coordinator import OpenSenseMapDataUpdateCoordinator

DEVICE_CLASS_MAPPING = {
    SensorId.PM25: SensorDeviceClass.PM25,
    SensorId.PM10: SensorDeviceClass.PM10,
    SensorId.TEMPERATURE: SensorDeviceClass.TEMPERATURE,
    SensorId.HUMIDITY: SensorDeviceClass.HUMIDITY,
    # SENSOR_ID_VCC: SensorDeviceClass.VCC, # check what is correct here
    SensorId.PRESSURE: SensorDeviceClass.ATMOSPHERIC_PRESSURE,
    SensorId.ILLUMINANCE: SensorDeviceClass.ILLUMINANCE,
    # SENSOR_ID_UV: SensorDeviceClass.UV, # not present in HA
    # SENSOR_ID_RADIOACT:
}


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Initialize the entries."""

    coordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities(
        [
            OpenSenseMapSensor(coordinator, entry, sensor_id)
            for sensor_id in await coordinator.receive_station_sensor_ids()
        ],
    )


class OpenSenseMapSensor(
    CoordinatorEntity[OpenSenseMapDataUpdateCoordinator], SensorEntity
):
    """OpenSenseMap Sensor."""

    _attr_attribution = (
        "Information provided by the openSenseMap (https://opensensemap.org/)"
    )
    _attr_has_entity_name = True
    _attr_state_class = SensorStateClass.MEASUREMENT

    def __init__(
        self,
        coordinator: OpenSenseMapDataUpdateCoordinator,
        config_entry: ConfigEntry,
        sensor_id: SensorId,
    ) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator)
        self._config_entry = config_entry
        self._station_id: str = config_entry.data[CONF_STATION_ID]
        self._sensor_id = sensor_id

    @property
    def unique_id(self) -> str:
        """Return a unique id for the sensor."""
        return self._station_id + "_" + self._sensor_id

    @property
    def name(self) -> str:
        """Return a sensor name."""
        return self._sensor_id

    @property
    def device_class(self) -> SensorDeviceClass:
        """Return the sensors device class."""
        return DEVICE_CLASS_MAPPING[self._sensor_id]

    @property
    def device_info(self) -> DeviceInfo:
        """Return the OpenSenseMap station as a device."""
        return DeviceInfo(
            identifiers={
                # Serial numbers are unique identifiers within a specific domain
                (DOMAIN, f"{self._config_entry.entry_id}")
            },
            name=self.coordinator.name,
            model=self.coordinator.name,
            manufacturer="opensensemap.org",
            entry_type=DeviceEntryType.SERVICE,
        )

    @property
    def attribution(self) -> str:
        """Return link to source as attribution."""
        return f"https://opensensemap.org/explore/{self._station_id}"

    @property
    def native_value(self) -> float | None:
        """Return the sensor value."""
        return self.coordinator.data[self._sensor_id]

    @property
    def native_unit_of_measurement(self) -> str:
        """Return the unit of the native value."""
        return self.coordinator.units[self._sensor_id]

    @callback
    def _handle_coordinator_update(self) -> None:
        """Handle updated data from the coordinator."""
        self.async_write_ha_state()
