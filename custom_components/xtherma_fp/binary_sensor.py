"""The xtherma integration binary sensors."""

import logging

from homeassistant.components.binary_sensor import (
    BinarySensorEntity,
)
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from . import XthermaConfigEntry
from .entity import XthermaCoordinatorEntity
from .entity_descriptors import XtBinarySensorEntityDescription

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: XthermaConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """HA calls this to initialize binary sensor platform."""
    _LOGGER.debug("Setup binary sensor platform")
    xtherma_data = config_entry.runtime_data
    coordinator = xtherma_data.coordinator

    binary_sensors = []
    for desc in coordinator.get_entity_descriptions():
        if not isinstance(desc, XtBinarySensorEntityDescription):
            continue
        _LOGGER.debug('Adding binary sensor "%s"', desc.key)
        binary_sensors.append(
            XthermaBinarySensor(coordinator, xtherma_data.device_info, desc)
        )

    _LOGGER.debug("Created %d binary sensors", len(binary_sensors))
    async_add_entities(binary_sensors)


class XthermaBinarySensor(XthermaCoordinatorEntity, BinarySensorEntity):
    """Xtherma Binary Sensor."""

    # keep this for type safe access to custom members
    entity_description: XtBinarySensorEntityDescription

    @callback
    def _handle_coordinator_update(self) -> None:
        """Handle updated data from the coordinator."""
        value = self.coordinator.read_value(self.entity_description.key)
        if value is None:
            return
        self._attr_is_on = value != 0
        self.async_write_ha_state()

    @property
    def icon(self) -> str | None:
        """Return the icon to use in the frontend, if any."""
        if self.entity_description.icon_provider:
            return self.entity_description.icon_provider(self.is_on)
        return super().icon
