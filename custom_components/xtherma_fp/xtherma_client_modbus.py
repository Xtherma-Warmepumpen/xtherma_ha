"""Client to access Modbus server on Xtherma FP module."""

from datetime import timedelta

from homeassistant.helpers.entity import EntityDescription
from modbus_connection import ModbusUnit

from .entity_descriptors import (
    MODBUS_DESCRIPTORS,
)
from .pytherma import XthermaFP
from .xtherma_client_common import (
    XthermaClient,
)

_MODBUS_UPDATE_PERIOD_S: int = 30


class XthermaClientModbus(XthermaClient):
    """Modbus access client.

    Thin wrapper around the vendored :mod:`pytherma` library over a
    :class:`modbus_connection.ModbusUnit` handle: it wraps an
    :class:`~pytherma.XthermaFP` device accessor and delegates all
    register access (decoding, scaling, two's-complement, empty-data
    detection, writability) to the library. Library exceptions propagate
    untranslated.

    The unit -- and the shared connection behind it -- is owned by the
    caller: in Home Assistant that is the modbus integration, which
    releases its hold (and closes the connection) when the last holding
    config entry unloads. This client therefore neither connects nor
    disconnects anything.
    """

    def __init__(
        self,
        unit: ModbusUnit,
    ) -> None:
        """Class constructor.

        Args:
            unit: Modbus unit handle, pre-bound to the device's slave id.
        """
        self._fp = XthermaFP(unit)
        self._fp.detect_empty_modbus_data = True

    @property
    def detect_empty_modbus_data(self) -> bool:
        """Whether empty (all-zero) register data is detected and dropped."""
        return self._fp.detect_empty_modbus_data

    @detect_empty_modbus_data.setter
    def detect_empty_modbus_data(self, value: bool) -> None:
        """Set empty-data detection on the underlying device accessor."""
        self._fp.detect_empty_modbus_data = value

    async def connect(self) -> None:
        """Delegate to the device accessor (whose connect is a no-op)."""
        await self._fp.async_connect()

    async def disconnect(self) -> None:
        """Delegate to the device accessor (whose disconnect is a no-op)."""
        await self._fp.async_disconnect()

    def update_interval(self) -> timedelta:
        """Return update interval for data coordinator."""
        return timedelta(seconds=_MODBUS_UPDATE_PERIOD_S)

    async def async_get_data(self) -> dict[str, int | float]:
        """Obtain fresh data."""
        return await self._fp.async_update()

    async def async_put_data(self, value: int | float, desc: EntityDescription) -> None:
        """Write data."""
        await self._fp.async_write(desc.key, value)

    def get_entity_descriptions(self) -> list[EntityDescription]:
        """Get all entity descriptions."""
        return MODBUS_DESCRIPTORS
