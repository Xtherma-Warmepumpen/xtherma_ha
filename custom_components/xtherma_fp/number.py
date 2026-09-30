"""The xtherma integration numbers."""

import functools
import logging

from homeassistant.components.number import NumberEntity
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from . import XthermaConfigEntry
from .entity import XthermaCoordinatorEntity
from .entity_descriptors import XtNumberEntityDescription

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: XthermaConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """HA calls this to initialize sensor platform."""
    _LOGGER.debug("Setup number platform")
    xtherma_data = config_entry.runtime_data
    coordinator = xtherma_data.coordinator

    numbers = []
    for desc in coordinator.get_entity_descriptions():
        if not isinstance(desc, XtNumberEntityDescription):
            continue
        _LOGGER.debug('Adding number "%s"', desc.key)
        numbers.append(XthermaNumberEntity(coordinator, xtherma_data.device_info, desc))

    _LOGGER.debug("Created %d numbers", len(numbers))
    async_add_entities(numbers)


class XthermaNumberEntity(XthermaCoordinatorEntity, NumberEntity):
    """Xtherma Number Input."""

    # keep this for type safe access to custom members
    entity_description: XtNumberEntityDescription

    @callback
    def _handle_coordinator_update(self) -> None:
        """Handle updated data from the coordinator."""
        value = self.coordinator.read_value(self.entity_description.key)
        if value is None:
            return
        self._attr_native_value = self._align_native_value_type(value)
        self.async_write_ha_state()

    @property
    def icon(self) -> str | None:
        """Return the icon to use in the frontend, if any."""
        if self.entity_description.icon_provider:
            return self.entity_description.icon_provider(self.native_value)
        return super().icon

    async def async_set_native_value(self, value: float) -> None:
        """Set value."""
        with self._force_refresh_on_error():
            native_value = self._align_native_value_type(value)
            await self.coordinator.async_write(self, value=native_value)
            self._attr_native_value = native_value
            self.async_write_ha_state()

    @functools.cached_property
    def native_type_is_int(self) -> bool:
        """Tell if native values are of type int."""
        return isinstance(
            self.entity_description.native_min_value,
            int,
        ) and isinstance(self.entity_description.native_step, int)

    def _align_native_value_type(self, value: float | int) -> float | int:
        # enforce internal type, so frontend will show decimal places only
        # when relevant.
        return int(value) if self.native_type_is_int else value
