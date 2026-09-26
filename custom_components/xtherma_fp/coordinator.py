"""DataUpdater for Xtherma Fernportal cloud integration."""

import logging
import time
from collections.abc import Callable
from dataclasses import dataclass
from typing import TYPE_CHECKING, cast

from homeassistant.core import HomeAssistant
from homeassistant.exceptions import HomeAssistantError
from homeassistant.helpers.entity import Entity, EntityDescription
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .const import (
    DOMAIN,
)
from .pytherma.exceptions import (
    XthermaModbusBusyError,
    XthermaModbusEmptyDataError,
    XthermaModbusError,
    XthermaModbusReadOnlyError,
    XthermaNotConnectedError,
)
from .xtherma_client_common import (
    XthermaClient,
    XthermaReadOnlyError,
    XthermaRestApiError,
    XthermaRestBusyError,
    XthermaTimeoutError,
)

if TYPE_CHECKING:
    from . import XthermaConfigEntry

_LOGGER = logging.getLogger(__name__)

# Time in seconds the device needs to process a write request.
# During this time, we block reads which would potentially restore
# the old value.
_WRITE_SETTLE_TIME_S = 30


@dataclass
class _PendingWrite:
    value: int | float
    blocked_until: float


@dataclass(frozen=True)
class _ErrorRule:
    """Maps an exception type to an HA translation key."""

    exc_type: type[Exception]
    translation_key: str
    extra_placeholders: Callable[[Exception], dict[str, str]] | None = None


def _error_str(err: Exception) -> dict[str, str]:
    return {"error": str(err)}


def _error_code(err: Exception) -> dict[str, str]:
    return {"error": str(cast("XthermaRestApiError", err).code)}


# Ordered read-path error rules; first isinstance match wins, so more
# specific exception types must precede their base types.
_READ_ERROR_RULES: tuple[_ErrorRule, ...] = (
    _ErrorRule(XthermaModbusBusyError, "modbus_read_busy_error"),
    _ErrorRule(XthermaRestBusyError, "rest_read_busy_error"),
    _ErrorRule(XthermaTimeoutError, "timeout_error"),
    _ErrorRule(XthermaNotConnectedError, "not_connected_error"),
    _ErrorRule(XthermaRestApiError, "rest_api_error", _error_code),
    _ErrorRule(XthermaModbusError, "modbus_read_error", _error_str),
    _ErrorRule(XthermaModbusEmptyDataError, "modbus_data_empty_error"),
)
_GENERAL_READ_ERROR = _ErrorRule(Exception, "general_error", _error_str)

# Ordered write-path error rules; all write placeholders carry entity_id.
_WRITE_ERROR_RULES: tuple[_ErrorRule, ...] = (
    _ErrorRule(XthermaReadOnlyError, "rest_read_only_error"),
    _ErrorRule(XthermaModbusReadOnlyError, "modbus_read_only_error"),
    _ErrorRule(XthermaModbusBusyError, "modbus_write_busy_error"),
    _ErrorRule(XthermaNotConnectedError, "modbus_write_not_connected_error"),
    _ErrorRule(XthermaModbusError, "modbus_write_error", _error_str),
)


def _match_error(err: Exception, rules: tuple[_ErrorRule, ...]) -> _ErrorRule | None:
    for rule in rules:
        if isinstance(err, rule.exc_type):
            return rule
    return None


class XthermaDataUpdateCoordinator(DataUpdateCoordinator[dict[str, int | float]]):
    """Regularly Fetches data from API client."""

    _client: XthermaClient

    def __init__(
        self,
        hass: HomeAssistant,
        config_entry: "XthermaConfigEntry",
        client: XthermaClient,
    ) -> None:
        """Class constructor."""
        self._client = client
        update_interval = client.update_interval()
        self._pending_writes: dict[str, _PendingWrite] = {}
        super().__init__(
            hass=hass,
            logger=_LOGGER,
            config_entry=config_entry,
            name=DOMAIN,
            update_interval=update_interval,
        )

    async def close(self) -> None:
        """Terminate usage."""
        _LOGGER.debug("Coordinator close")
        await self._client.disconnect()

    async def _async_setup(self) -> None:
        """Set up the coordinator."""
        _LOGGER.debug("Coordinator _async_setup")
        await self._client.connect()

    async def _async_update_data(self) -> dict[str, int | float]:
        result: dict[str, int | float] = {}
        try:
            _LOGGER.debug("Coordinator requesting new data")
            client_data = await self._client.async_get_data()
            for key, value in client_data.items():
                pending_write = self._is_blocked(key)
                if pending_write is not None:
                    result[key] = pending_write
                    _LOGGER.debug(
                        'Skipping update of key="%s" due to pending write',
                        key,
                    )
                else:
                    result[key] = value
        except Exception as err:
            rule = _match_error(err, _READ_ERROR_RULES) or _GENERAL_READ_ERROR
            raise UpdateFailed(
                translation_domain=DOMAIN,
                translation_key=rule.translation_key,
                translation_placeholders=(
                    rule.extra_placeholders(err) if rule.extra_placeholders else {}
                ),
            ) from err
        _LOGGER.debug(
            "coordinator processed %d/%d values",
            len(result),
            len(client_data),
        )
        return result

    def get_entity_descriptions(self) -> list[EntityDescription]:
        """Get all entity descriptions."""
        return self._client.get_entity_descriptions()

    def _block_for(self, key: str, seconds: int, value: int | float) -> None:
        """Block reads for a specific register for N seconds."""
        _LOGGER.debug("Block reads of key %s for %d seconds", key, seconds)
        self._pending_writes[key] = _PendingWrite(
            blocked_until=time.monotonic() + seconds,
            value=value,
        )

    def _is_blocked(self, key: str) -> int | float | None:
        """Test if device-side processing for key is in progress."""
        # check if any keys are blocked
        if not self._pending_writes:
            return None
        # check if our key might be blocked
        pending = self._pending_writes.get(key)
        if pending is None:
            return None
        now = time.monotonic()
        if now > pending.blocked_until:
            # block time expired, delete key
            self._pending_writes.pop(key)
            return None
        # key is actually blocked
        return pending.value

    async def async_write(self, entity: Entity, value: int | float) -> None:
        """Add a write request to the queue."""
        desc = entity.entity_description
        try:
            await self._client.async_put_data(desc=desc, value=value)
            self._block_for(key=desc.key, seconds=_WRITE_SETTLE_TIME_S, value=value)
        except Exception as err:
            rule = _match_error(err, _WRITE_ERROR_RULES)
            if rule is None:
                raise
            raise HomeAssistantError(
                translation_domain=DOMAIN,
                translation_key=rule.translation_key,
                translation_placeholders={
                    **(rule.extra_placeholders(err) if rule.extra_placeholders else {}),
                    "entity_id": entity.entity_id,
                },
            ) from err

    def read_value(self, key: str) -> int | float | None:
        """Read a value from us."""
        if self.data is None:
            return None
        if not self.last_update_success:
            return None
        value = self.data.get(key)
        if value is None:
            msg = f"Missing data in coordinator key={key}"
            _LOGGER.error(msg)
        return value
