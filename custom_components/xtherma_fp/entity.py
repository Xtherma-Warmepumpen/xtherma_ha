"Xtherma parent entity class."

import logging
from collections.abc import Iterator
from contextlib import contextmanager

from homeassistant.exceptions import HomeAssistantError
from homeassistant.helpers.device_registry import (
    DeviceInfo,
)
from homeassistant.helpers.entity import EntityDescription
from homeassistant.helpers.update_coordinator import (
    CoordinatorEntity,
)

from .const import EXTRA_STATE_ATTRIBUTE_PARAMETER
from .coordinator import XthermaDataUpdateCoordinator

_LOGGER = logging.getLogger(__name__)


class XthermaCoordinatorEntity(CoordinatorEntity[XthermaDataUpdateCoordinator]):
    """Parent class for all entities associated with the Xtherma component that use a coordinator."""

    def __init__(
        self,
        coordinator: XthermaDataUpdateCoordinator,
        device_info: DeviceInfo,
        description: EntityDescription,
    ) -> None:
        """Initialize the Xtherma coordinator entity."""
        super().__init__(coordinator)
        self.entity_description = description
        self._attr_has_entity_name = True
        self._attr_device_info = device_info
        self._attr_unique_id = (
            f"{self.coordinator.config_entry.entry_id}-{description.key}"
        )
        self._attr_extra_state_attributes = {
            EXTRA_STATE_ATTRIBUTE_PARAMETER: description.key,
        }
        self._attr_translation_key = description.key

    @contextmanager
    def _force_refresh_on_error(self) -> Iterator[None]:
        """Force a state refresh when the wrapped write fails, then re-raise.

        A failed write leaves the optimistic state pushed to the frontend
        out of sync with the device; emitting one forced update restores
        the device state in the UI before the error surfaces.
        """
        try:
            yield
        except HomeAssistantError:
            self._attr_force_update = True
            self.async_write_ha_state()
            self._attr_force_update = False
            raise
