"""Smoke tests for the pytherma package."""

from modbus_connection import ModbusUnit

from custom_components.xtherma_fp.pytherma import (
    XthermaFP,
    __version__,
)
from custom_components.xtherma_fp.pytherma.addresses import (
    MODBUS_REGISTER_SIZE,
    REGISTER_RANGES,
)
from custom_components.xtherma_fp.pytherma.testing import FakeUnit


def test_version():
    assert __version__


def test_fake_unit_conforms_to_modbus_unit():
    """The test fake satisfies the modbus-connection ModbusUnit protocol."""
    unit = FakeUnit()
    assert isinstance(unit, ModbusUnit)


def test_addresses():
    assert MODBUS_REGISTER_SIZE == 194
    assert len(REGISTER_RANGES) == 2


async def test_device_constructs_and_updates():
    unit = FakeUnit()
    device = XthermaFP(unit)
    device.detect_empty_modbus_data = False
    # connect/disconnect are no-ops: the shared link is owned by the
    # connection holder and opens lazily on the first request
    await device.async_connect()
    assert unit.connected
    data = await device.async_update()
    assert isinstance(data, dict)
    await device.async_disconnect()
    assert unit.connected
