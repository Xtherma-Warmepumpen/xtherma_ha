"""The xtherma integration sensors."""

import logging

from homeassistant.components.sensor import SensorDeviceClass, SensorEntity
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from . import XthermaConfigEntry
from .coordinator import XthermaDataUpdateCoordinator
from .entity import XthermaCoordinatorEntity
from .entity_descriptors import (
    XtSensorEntityDescription,
    XtVersionSensorEntityDescription,
)

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: XthermaConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """HA calls this to initialize sensor platform."""
    _LOGGER.debug("Setup sensor platform")
    xtherma_data = config_entry.runtime_data
    coordinator = xtherma_data.coordinator

    sensors = []
    descriptions = coordinator.get_entity_descriptions()
    for desc in descriptions:
        if not isinstance(desc, XtSensorEntityDescription):
            continue

        if desc.device_class == SensorDeviceClass.ENUM:
            sensor = XthermaEnumSensor(coordinator, xtherma_data.device_info, desc)
        elif isinstance(desc, XtVersionSensorEntityDescription):
            sensor = XthermaVersionSensor(coordinator, xtherma_data.device_info, desc)
        else:
            sensor = XthermaSensor(coordinator, xtherma_data.device_info, desc)

        _LOGGER.debug('Adding sensor "%s"', desc.key)
        sensors.append(sensor)

    _LOGGER.debug("Created %d sensors", len(sensors))
    async_add_entities(sensors)


class XthermaSensor(XthermaCoordinatorEntity, SensorEntity):
    """Xtherma Value Sensor."""

    # keep this for type safe access to custom members
    entity_description: XtSensorEntityDescription

    def __init__(
        self,
        coordinator: XthermaDataUpdateCoordinator,
        device_info: DeviceInfo,
        description: XtSensorEntityDescription,
    ) -> None:
        """Class Constructor."""
        super().__init__(coordinator, device_info, description)
        self._attr_native_unit_of_measurement = description.native_unit_of_measurement
        self._attr_state_class = description.state_class
        self._attr_options = description.options
        self._factor = description.factor

    @callback
    def _handle_coordinator_update(self) -> None:
        """Handle updated data from the coordinator."""
        value = self.coordinator.read_value(self.entity_description.key)
        if value is None:
            return
        self._attr_native_value = value
        self.async_write_ha_state()

    @property
    def icon(self) -> str | None:
        """Return the icon to use in the frontend, if any."""
        if self.entity_description.icon_provider:
            return self.entity_description.icon_provider(self.native_value)
        return super().icon


class XthermaEnumSensor(XthermaSensor):
    """Xtherma Enum Value Sensor."""

    @callback
    def _handle_coordinator_update(self) -> None:
        options = self._attr_options
        if options is None:
            return
        value = self.coordinator.read_value(self.entity_description.key)
        if value is None:
            return
        index = int(value)
        if not 0 <= index < len(options):
            _LOGGER.warning(
                'Enum value "%s" for %s out of range (options: %d)',
                value,
                self.entity_description.key,
                len(options),
            )
            self._attr_native_value = None
            self.async_write_ha_state()
            return
        self._attr_native_value = options[index]
        self.async_write_ha_state()


class XthermaVersionSensor(XthermaSensor):
    """Xtherma Version Value Sensor."""

    @callback
    def _handle_coordinator_update(self) -> None:
        """Handle updated data from the coordinator."""
        value = self.coordinator.read_value(self.entity_description.key)
        if value is None:
            return
        # note: input factor (assume: /100) has already been applied
        major = int(value)
        minor = round((value - major) * 100)
        self._attr_native_value = f"{major}.{minor:02d}"
        self.async_write_ha_state()
