"""The xtherma integration switches."""

import logging
from typing import Any

from homeassistant.components.switch import SwitchEntity
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from . import XthermaConfigEntry
from .coordinator import XthermaDataUpdateCoordinator
from .entity import XthermaCoordinatorEntity
from .entity_descriptors import XtSwitchEntityDescription

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: XthermaConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """HA calls this to initialize sensor platform."""
    _LOGGER.debug("Setup switch platform")
    xtherma_data = config_entry.runtime_data
    coordinator = xtherma_data.coordinator

    switches = []
    for desc in coordinator.get_entity_descriptions():
        if not isinstance(desc, XtSwitchEntityDescription):
            continue
        _LOGGER.debug('Adding switch "%s"', desc.key)
        switches.append(
            XthermaSwitchEntity(coordinator, xtherma_data.device_info, desc)
        )

    _LOGGER.debug("Created %d switches", len(switches))
    async_add_entities(switches)


class XthermaSwitchEntity(XthermaCoordinatorEntity, SwitchEntity):
    """Xtherma Switch Input."""

    # keep this for type safe access to custom members
    entity_description: XtSwitchEntityDescription

    def __init__(
        self,
        coordinator: XthermaDataUpdateCoordinator,
        device_info: DeviceInfo,
        description: XtSwitchEntityDescription,
    ) -> None:
        """Class Constructor."""
        super().__init__(coordinator, device_info, description)
        """
        Avoid the "unknown" state which will make the frontend render this as two icon
        buttons in case the coordinator fails to update. Note we also need to
        explicitly initialize _attr_assumed_state as an instance value, even though
        the class default is already False. I think this may have to do with the
        serialization towards the frontend.
        """
        self._attr_is_on = False
        self._attr_assumed_state = False

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

    async def async_turn_on(self, **kwargs: Any) -> None:  # noqa: ANN401
        """Turn the entity on."""
        with self._force_refresh_on_error():
            await self.coordinator.async_write(self, 1)
            self._attr_is_on = True
            self.async_write_ha_state()

    async def async_turn_off(self, **kwargs: Any) -> None:  # noqa: ANN401
        """Turn the entity off."""
        with self._force_refresh_on_error():
            await self.coordinator.async_write(self, 0)
            self._attr_is_on = False
            self.async_write_ha_state()
