"""Tests for the XthermaFP device accessor."""

import pytest
from fake_unit import (
    FakeUnit,
    provide_empty_modbus_image,
    provide_modbus_image,
)
from modbus_connection import ModbusConnectionError

from custom_components.xtherma_fp.pytherma import XthermaFP
from custom_components.xtherma_fp.pytherma.addresses import (
    REGISTER_RANGES,
)
from custom_components.xtherma_fp.pytherma.bindings import (
    MODBUS_BINDING_BY_KEY,
    MODBUS_BINDINGS,
)
from custom_components.xtherma_fp.pytherma.exceptions import (
    XthermaModbusBusyError,
    XthermaModbusEmptyDataError,
    XthermaModbusError,
    XthermaModbusReadOnlyError,
    XthermaNotConnectedError,
)

#: keys of all quantities which have a modbus binding
MODBUS_KEYS = {binding.quantity.key for binding in MODBUS_BINDINGS}


async def test_update_decodes_all_registers(fake_unit) -> None:
    """Update decodes all modbus registers from the standard image."""
    device = XthermaFP(fake_unit)
    data = await device.async_update()
    assert set(data) == MODBUS_KEYS
    # spot values, derived from tests/fixtures/rest_response.json
    assert data["tvl"] == 26.1
    assert data["tk2"] == -98.9
    assert data["311"] == -9
    assert data["h_target"] == 22.9
    assert data["controller_v"] == 2.43
    assert data["day_hp_out_h"] == 14.28
    assert data["mode"] == 3
    assert data["002"] == 4
    assert data["pww"] == 1
    assert data["hw_target"] == 50
    assert data["808"] == 0
    assert data["815"] == 0
    assert data["x2400"] == 1
    assert data["x2401"] == 1234
    assert data["error"] == 1
    assert data["in_total"] == 0


async def test_update_empty_data_detected() -> None:
    """An all-zero image is detected as empty data."""
    unit = FakeUnit(image=provide_empty_modbus_image())
    device = XthermaFP(unit)
    with pytest.raises(XthermaModbusEmptyDataError):
        await device.async_update()


async def test_update_empty_data_detection_off() -> None:
    """With detection disabled, an empty image yields all-zero data."""
    unit = FakeUnit(image=provide_empty_modbus_image())
    device = XthermaFP(unit)
    device.detect_empty_modbus_data = False
    data = await device.async_update()
    assert set(data) == MODBUS_KEYS
    assert all(value == 0 for value in data.values())


@pytest.mark.parametrize("error_cls", [XthermaModbusBusyError, XthermaModbusError])
@pytest.mark.parametrize("range_index", [0, 1])
async def test_update_read_error(error_cls, range_index) -> None:
    """A read error in any range aborts the update."""
    unit = FakeUnit(image=provide_modbus_image())
    for i in range(len(REGISTER_RANGES)):
        unit.queue_read_result(error_cls() if i == range_index else None)
    device = XthermaFP(unit)
    with pytest.raises(error_cls):
        await device.async_update()


async def test_update_connect_error() -> None:
    """A connection error on the first request aborts the update."""
    unit = FakeUnit(image=provide_modbus_image())
    unit.queue_read_result(ModbusConnectionError())
    device = XthermaFP(unit)
    with pytest.raises(XthermaNotConnectedError):
        await device.async_update()


async def test_update_propagates_unit_id() -> None:
    """The unit id the handle is bound to is recorded on every range read."""
    unit = FakeUnit(unit_id=7, image=provide_modbus_image())
    device = XthermaFP(unit)
    await device.async_update()
    expected = [(7, r.first_reg, r.length) for r in REGISTER_RANGES]
    assert unit.read_calls == expected


@pytest.mark.parametrize(
    ("raw_value", "decoded_value"),
    [
        (32767, 32767),  # highest positive must NOT be decoded as negative
        (32768, -32768),  # lowest negative
        (65535, -1),
    ],
)
def test_decode_signed_boundaries(raw_value: int, decoded_value: int) -> None:
    """Signed decode uses the 0x8000 threshold; _decode/_encode stay inverse."""
    quantity = MODBUS_BINDING_BY_KEY["311"].quantity
    assert quantity.signed
    assert quantity.factor is None
    assert XthermaFP._decode(quantity, raw_value) == decoded_value  # noqa: SLF001
    assert XthermaFP._encode(quantity, decoded_value) == raw_value  # noqa: SLF001


async def test_write_negative_value(fake_unit) -> None:
    """Negative values are written two's complement encoded."""
    device = XthermaFP(fake_unit)
    await device.async_write("311", -9)
    assert fake_unit.write_calls == [(1, 11, 65527)]


async def test_write_switch(fake_unit) -> None:
    """Switch values are written to their register address."""
    device = XthermaFP(fake_unit)
    await device.async_write("450", 1)
    assert fake_unit.write_calls == [(1, 40, 1)]


async def test_write_float_coerced_to_int(fake_unit) -> None:
    """Float values are coerced to int on write."""
    device = XthermaFP(fake_unit)
    await device.async_write("501", 50.0)
    assert fake_unit.write_calls == [(1, 50, 50)]


async def test_write_readonly_register(fake_unit) -> None:
    """Writing a read-only register is rejected."""
    device = XthermaFP(fake_unit)
    with pytest.raises(XthermaModbusReadOnlyError):
        await device.async_write("tvl", 25.0)
    assert fake_unit.write_calls == []


async def test_write_readonly_sensor_with_factor(fake_unit) -> None:
    """Writing a read-only sensor is rejected, even if it has a factor."""
    device = XthermaFP(fake_unit)
    with pytest.raises(XthermaModbusReadOnlyError):
        await device.async_write("tk", 22.0)
    assert fake_unit.write_calls == []


async def test_write_unknown_key(fake_unit) -> None:
    """Writing an unknown key is rejected."""
    device = XthermaFP(fake_unit)
    with pytest.raises(XthermaModbusError):
        await device.async_write("no_such_key", 1)
    assert fake_unit.write_calls == []


async def test_write_rest_only_key(fake_unit) -> None:
    """Writing a REST-only register is rejected."""
    device = XthermaFP(fake_unit)
    with pytest.raises(XthermaModbusError):
        await device.async_write("error_1", 1)
    assert fake_unit.write_calls == []


@pytest.mark.parametrize("error_cls", [XthermaModbusBusyError, XthermaModbusError])
async def test_write_error(fake_unit, error_cls) -> None:
    """A transport error on write is propagated."""
    fake_unit.queue_write_error(error_cls())
    device = XthermaFP(fake_unit)
    with pytest.raises(error_cls):
        await device.async_write("450", 1)


async def test_write_then_update_roundtrip(fake_unit) -> None:
    """A written value is read back on the next update."""
    device = XthermaFP(fake_unit)
    await device.async_write("311", -5)
    data = await device.async_update()
    assert data["311"] == -5
