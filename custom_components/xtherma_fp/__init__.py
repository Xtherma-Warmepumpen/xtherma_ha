"""The Xtherma integration."""

from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import TYPE_CHECKING

import homeassistant.helpers.device_registry as dr
import homeassistant.helpers.entity_registry as er

try:
    from homeassistant.components.modbus import async_get_unit
except ImportError:
    # Importing the modbus component transitively imports its Modbus
    # backends (pymodbus / tmodbus), which Home Assistant only installs
    # when the modbus integration is present. This integration does not
    # depend on them (it also supports read-only REST), so the import is
    # guarded: the unit factory is left as None and re-imported lazily
    # in async_setup_entry when a Modbus entry is set up.
    async_get_unit = None

from homeassistant.config_entries import ConfigEntryNotReady
from homeassistant.const import (
    CONF_ADDRESS,
    CONF_API_KEY,
    CONF_HOST,
    CONF_PORT,
    Platform,
)
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from modbus_connection import ModbusTcpParams

from .const import (
    CONF_CONNECTION,
    CONF_CONNECTION_RESTAPI,
    CONF_DETECT_EMPTY_MODBUS_DATA,
    CONF_SERIAL_NUMBER,
    DOMAIN,
    FERNPORTAL_URL,
    MANUFACTURER,
    VERSION,
)
from .coordinator import XthermaDataUpdateCoordinator
from .xtherma_client_modbus import XthermaClientModbus
from .xtherma_client_rest import XthermaClientRest

if TYPE_CHECKING:
    from homeassistant.config_entries import ConfigEntry

type XthermaConfigEntry = ConfigEntry[XthermaData]

_LOGGER = logging.getLogger(__name__)

_PLATFORMS = [
    Platform.BINARY_SENSOR,
    Platform.SENSOR,
    Platform.SWITCH,
    Platform.NUMBER,
    Platform.SELECT,
]


@dataclass
class XthermaData:
    """Global data for integration."""

    coordinator: XthermaDataUpdateCoordinator
    serial_fp: str
    device_info: dr.DeviceInfo


async def async_setup_entry(
    hass: HomeAssistant,
    entry: XthermaConfigEntry,
) -> bool:
    """Initialize integration."""
    _LOGGER.debug("Setup integration")
    serial_number = entry.data[CONF_SERIAL_NUMBER]

    # create API client connector
    connection = entry.data.get(CONF_CONNECTION, CONF_CONNECTION_RESTAPI)
    if connection == CONF_CONNECTION_RESTAPI:
        api_key = entry.data[CONF_API_KEY]
        client = XthermaClientRest(
            url=FERNPORTAL_URL,
            api_key=api_key,
            serial_number=serial_number,
            session=async_get_clientsession(hass),
        )
    else:
        host = entry.data[CONF_HOST]
        port = entry.data[CONF_PORT]
        address = entry.data[CONF_ADDRESS]
        # the shared connection is held by the modbus integration and
        # closed when the last holding entry unloads; nothing to register
        # on unload here
        params = ModbusTcpParams(host=host, port=int(port))
        if async_get_unit is not None:
            unit = async_get_unit(hass, entry, params, int(address))
        else:
            # the modbus component (and its pymodbus requirement) may
            # have become available since this module was imported;
            # import under an alias so the module global is not shadowed
            try:
                from homeassistant.components.modbus import (  # noqa: PLC0415
                    async_get_unit as _unit_factory,
                )
            except ImportError as err:
                _LOGGER.exception("Modbus component unavailable")
                raise ConfigEntryNotReady from err
            unit = _unit_factory(hass, entry, params, int(address))
        client = XthermaClientModbus(unit)

    coordinator = XthermaDataUpdateCoordinator(hass, entry, client)
    device_info = dr.DeviceInfo(
        identifiers={(DOMAIN, entry.entry_id)},
        name=entry.title,
        manufacturer=MANUFACTURER,
        model=serial_number,
    )

    entry.runtime_data = XthermaData(coordinator, serial_number, device_info)

    # migrate entities
    await async_migrate_devices(hass, entry)
    await async_migrate_entities(hass, entry)

    # Try updating data from the client. This can fail, and an exception
    # will be thrown, causing HA to retry this entire setup after a while.
    try:
        await coordinator.async_config_entry_first_refresh()
    except Exception:
        await coordinator.close()
        raise

    # initialize platforms
    await hass.config_entries.async_forward_entry_setups(entry, _PLATFORMS)

    # make sure entities immediately have a valid state
    coordinator.async_update_listeners()

    async def update_options_listener(
        hass: HomeAssistant, config_entry: ConfigEntry
    ) -> None:
        """Handle options update."""
        del hass
        if isinstance(client, XthermaClientModbus):
            detect_empty = config_entry.options.get(CONF_DETECT_EMPTY_MODBUS_DATA, True)
            client.detect_empty_modbus_data = detect_empty

    await update_options_listener(hass, entry)

    entry.async_on_unload(entry.add_update_listener(update_options_listener))

    return True


async def async_unload_entry(hass: HomeAssistant, entry: XthermaConfigEntry) -> bool:
    """Unload integration."""
    _LOGGER.debug("Unload integration")
    xtherma_data: XthermaData = entry.runtime_data
    if xtherma_data and xtherma_data.coordinator:
        _LOGGER.debug("Close data coordinator")
        await xtherma_data.coordinator.close()
    return await hass.config_entries.async_unload_platforms(entry, _PLATFORMS)


async def async_migrate_entry(
    _: HomeAssistant, config_entry: XthermaConfigEntry
) -> bool:
    """Migrate config entry."""
    if config_entry.version > VERSION:
        _LOGGER.error("Downgrade not supported")
        return False

    if config_entry.version < VERSION:
        _LOGGER.debug(
            "Migrating configuration from version %s.%s",
            config_entry.version,
            config_entry.minor_version,
        )

    return True


async def async_migrate_devices(
    hass: HomeAssistant,
    config_entry: XthermaConfigEntry,
) -> None:
    """Migrate device registry."""
    registry = dr.async_get(hass)
    for device_entry in dr.async_entries_for_config_entry(
        registry, config_entry.entry_id
    ):
        if device_entry.identifiers != {(DOMAIN, config_entry.entry_id)}:
            registry.async_update_device(
                device_entry.id, new_identifiers={(DOMAIN, config_entry.entry_id)}
            )


async def async_migrate_entities(
    hass: HomeAssistant,
    config_entry: XthermaConfigEntry,
) -> None:
    """Migrate entity registry."""

    @callback
    def update_unique_id(entity_entry: er.RegistryEntry) -> dict[str, str] | None:
        """Update unique ID of entity entry."""
        if entity_entry.unique_id.startswith(DOMAIN):
            return {
                "new_unique_id": entity_entry.unique_id.replace(
                    f"{DOMAIN}_",
                    f"{config_entry.entry_id}-",
                ),
            }

        return None

    await er.async_migrate_entries(hass, config_entry.entry_id, update_unique_id)

    registry = er.async_get(hass)
    for entity_entry in er.async_entries_for_config_entry(
        registry,
        config_entry.entry_id,
    ):
        # In Home Assistant, suggested_object_id is an internal Entity Registry
        # property that integrations use to propose a default object ID when an
        # entity is first created. We don't do that. Early versions of this
        # integration used bad entity creation leading to having this value
        # set, preventing HA's standard automated naming. suggested_object_id
        # is quite sticky: the only way to ever get rid of it is to delete and
        # quickly re-created the entity, which is what we do here.
        if entity_entry.suggested_object_id is not None:
            _LOGGER.debug(
                "remove suggested_object_id from entity entry %s",
                entity_entry.unique_id,
            )
            registry.async_remove(entity_entry.entity_id)
            registry.async_get_or_create(
                entity_entry.domain,
                entity_entry.platform,
                entity_entry.unique_id,
                config_entry=config_entry,
                device_id=entity_entry.device_id,
            )
