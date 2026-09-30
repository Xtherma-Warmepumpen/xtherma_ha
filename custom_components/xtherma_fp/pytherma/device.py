"""Async device accessor for the Xtherma FP heat pump."""

import logging

from modbus_connection import (
    ModbusConnectionError,
    ModbusUnit,
    ServerDeviceBusyError,
)

from .addresses import (
    MODBUS_REGISTER_SIZE,
    REGISTER_RANGES,
)
from .bindings import MODBUS_BINDING_BY_KEY, MODBUS_BINDINGS
from .data_model import Quantity
from .exceptions import (
    XthermaError,
    XthermaModbusBusyError,
    XthermaModbusEmptyDataError,
    XthermaModbusError,
    XthermaModbusReadOnlyError,
    XthermaNotConnectedError,
)
from .scaling import apply_factor, reverse_factor

_LOGGER = logging.getLogger(__name__)

_MODBUS_MAX_VALUE: int = 65535
#: lowest raw value whose two's complement interpretation is negative
_MODBUS_SIGN_BIT: int = 0x8000

# exceptions the library raises itself, passed through from unit
# implementations unchanged (e.g. fakes that script them directly)
_XTHERMA_ERRORS: tuple[type[XthermaError], ...] = (XthermaError,)


def _translate(err: Exception) -> Exception:
    """Map a neutral ``modbus-connection`` error onto the Xtherma contract.

    Both backends (tmodbus, pymodbus) map their native errors into the
    neutral ``modbus_connection`` exception hierarchy; this translates that
    hierarchy onto the stable :mod:`pytherma.exceptions` contract.

    Args:
        err: exception raised by the unit.

    Returns:
        The exception to raise instead: an already-Xtherma exception
        (passed through unchanged), :class:`XthermaModbusBusyError` for
        ``ServerDeviceBusyError``, :class:`XthermaNotConnectedError` for
        ``ModbusConnectionError`` (incl. ``ClientClosedError``), or
        :class:`XthermaModbusError` for anything else.
    """
    if isinstance(err, _XTHERMA_ERRORS):
        return err
    if isinstance(err, ServerDeviceBusyError):
        _LOGGER.debug("Modbus device busy")
        return XthermaModbusBusyError()
    if isinstance(err, ModbusConnectionError):
        _LOGGER.debug("Modbus connection error: %s", err)
        return XthermaNotConnectedError()
    _LOGGER.debug("Modbus error: %s", err)
    return XthermaModbusError()


class XthermaFP:
    """Async accessor for Xtherma FP Modbus registers.

    Args:
        unit: a :class:`modbus_connection.ModbusUnit` handle, pre-bound to
            the device's slave (unit) id by its connection (in Home
            Assistant via ``homeassistant.components.modbus.async_get_unit``;
            standalone via ``ModbusConnection(params).for_unit(id)``).
    """

    def __init__(self, unit: ModbusUnit) -> None:
        """Class constructor."""
        self._unit = unit
        self._read_buffer: list[int] = [0] * MODBUS_REGISTER_SIZE
        self._data: dict[str, int | float] = {}
        #: whether to detect and drop empty (all-zero) register data
        self.detect_empty_modbus_data = True

    @property
    def data(self) -> dict[str, int | float]:
        """Last successfully read register values, keyed by register key."""
        return self._data

    async def async_connect(self) -> None:
        """No-op.

        The unit's link is shared and owned by the connection holder (in
        Home Assistant the ``modbus`` integration). It opens lazily on the
        first request and self-heals after a drop; Home Assistant retries
        entry setup when the first refresh fails, so there is nothing for
        the device to connect here.
        """

    async def async_disconnect(self) -> None:
        """No-op.

        The shared connection is owned by the connection holder and is
        closed when the last holding entry unloads. A unit holder must not
        close or ``disconnect()`` the link out from under its owner.
        """

    async def async_update(self) -> dict[str, int | float]:
        """Read all register ranges and return the decoded register values."""
        await self.async_connect()
        self._data = {}
        for r in REGISTER_RANGES:
            try:
                regs = await self._unit.read_holding_registers(
                    address=int(r.first_reg),
                    count=int(r.length),
                )
            except Exception as err:
                raise _translate(err) from err
            self._read_buffer[r.first_reg : r.first_reg + r.length] = regs
            # we know that no single register range can ever be empty, so
            # throw an exception if we just read empty data.
            # see also test_device.py::test_update_empty_data_detected
            if (
                self.detect_empty_modbus_data
                and self._read_buffer[r.non_empty_reg] == 0
            ):
                raise XthermaModbusEmptyDataError
        for binding in MODBUS_BINDINGS:
            raw_value = self._read_buffer[binding.address]
            key = binding.quantity.key
            self._data[key] = self._decode(binding.quantity, raw_value)
            _LOGGER.debug(
                'key="%s" raw="%s" value="%s"',
                key,
                raw_value,
                self._data[key],
            )
        return self._data

    async def async_write(self, key: str, value: int | float) -> None:
        """Write ``value`` (scaled) to the quantity identified by ``key``."""
        binding = MODBUS_BINDING_BY_KEY.get(key)
        if binding is None:
            _LOGGER.error("Unknown register %s", key)
            raise XthermaModbusError
        if not binding.writable:
            raise XthermaModbusReadOnlyError
        await self.async_connect()
        int_value = reverse_factor(value, binding.quantity.factor)
        encoded_value = self._encode(binding.quantity, int_value)
        _LOGGER.debug(
            'Writing "%s" = %d @ address %d',
            key,
            encoded_value,
            binding.address,
        )
        try:
            await self._unit.write_register(
                address=binding.address,
                value=encoded_value,
            )
        except Exception as err:
            raise _translate(err) from err

    @staticmethod
    def _decode(quantity: Quantity, raw_value: int) -> int | float:
        """Decode a raw register value (two's complement + scaling factor)."""
        if quantity.signed and raw_value >= _MODBUS_SIGN_BIT:
            decoded_value = -((raw_value - 1) ^ _MODBUS_MAX_VALUE)
        else:
            decoded_value = raw_value
        if quantity.factor:
            return apply_factor(decoded_value, quantity.factor)
        return decoded_value

    @staticmethod
    def _encode(quantity: Quantity, signed_value: int) -> int:
        """Encode a register value with two's complement for negatives."""
        if quantity.signed and signed_value < 0:
            return ((-signed_value) ^ _MODBUS_MAX_VALUE) + 1
        return signed_value
