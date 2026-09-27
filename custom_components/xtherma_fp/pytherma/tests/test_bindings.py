"""Tests for the transport binding tables (quantity/binding split S2)."""

from dataclasses import FrozenInstanceError

import pytest

from custom_components.xtherma_fp.pytherma.bindings import (
    MODBUS_BINDING_BY_ADDRESS,
    MODBUS_BINDING_BY_KEY,
    MODBUS_BINDINGS,
    REST_BINDING_BY_API_KEY,
    REST_BINDINGS,
    ModbusBinding,
    RestBinding,
)
from custom_components.xtherma_fp.pytherma.quantities import QUANTITY_BY_KEY

#: quantities reachable only via Modbus (no Fernportal REST wire key)
MODBUS_ONLY_KEYS = {"808", "815", "error", "out_total", "x2400", "x2401"}

#: quantities reachable only via REST (no Modbus address)
REST_ONLY_KEYS = {"error_1", "error_2"}


def test_modbus_binding_count() -> None:
    assert len(MODBUS_BINDINGS) == 92
    assert len(MODBUS_BINDING_BY_KEY) == 92
    assert len(MODBUS_BINDING_BY_ADDRESS) == 92


def test_modbus_addresses_sorted() -> None:
    # descriptor order (pinned by the entity-description snapshots) follows
    # the address-ascending table layout: settings range, then telemetry range
    addresses = [b.address for b in MODBUS_BINDINGS]
    assert addresses == sorted(addresses)


def test_modbus_address_uniqueness() -> None:
    addresses = [b.address for b in MODBUS_BINDINGS]
    assert len(addresses) == len(set(addresses))


def test_modbus_quantity_reference_is_shared() -> None:
    # one-hop access: bindings reference the canonical Quantity objects
    for binding in MODBUS_BINDINGS:
        assert binding.quantity is QUANTITY_BY_KEY[binding.quantity.key]


def test_modbus_dict_consistency() -> None:
    for binding in MODBUS_BINDINGS:
        assert MODBUS_BINDING_BY_KEY[binding.quantity.key] is binding
        assert MODBUS_BINDING_BY_ADDRESS[binding.address] is binding


def test_modbus_only_quantities() -> None:
    rest_keys = {b.quantity.key for b in REST_BINDINGS}
    assert set(MODBUS_BINDING_BY_KEY) - rest_keys == MODBUS_ONLY_KEYS


def test_rest_binding_count() -> None:
    assert len(REST_BINDINGS) == 88
    assert len(REST_BINDING_BY_API_KEY) == 88


def test_rest_api_key_baseline() -> None:
    # isolation seam baseline: today every wire key equals the quantity key
    for binding in REST_BINDINGS:
        assert binding.api_key is None
        assert binding.resolved_api_key == binding.quantity.key


def test_rest_binding_by_api_key_consistent() -> None:
    for binding in REST_BINDINGS:
        assert REST_BINDING_BY_API_KEY[binding.resolved_api_key] is binding


def test_rest_quantity_reference_is_shared() -> None:
    for binding in REST_BINDINGS:
        assert binding.quantity is QUANTITY_BY_KEY[binding.quantity.key]


def test_rest_only_quantities() -> None:
    assert {b.quantity.key for b in REST_BINDINGS} - set(MODBUS_BINDING_BY_KEY) == (
        REST_ONLY_KEYS
    )


def test_rest_explicit_api_key_override() -> None:
    # the api_key seam: a rename on the wire never touches the quantity key
    quantity = QUANTITY_BY_KEY["001"]
    binding = RestBinding(quantity=quantity, api_key="renamed_on_wire")
    assert binding.resolved_api_key == "renamed_on_wire"
    assert RestBinding(quantity=quantity).resolved_api_key == "001"


def test_bindings_are_frozen() -> None:
    quantity = QUANTITY_BY_KEY["001"]
    modbus = ModbusBinding(quantity=quantity, address=0)
    rest = RestBinding(quantity=quantity)
    for binding, field in ((modbus, "address"), (rest, "api_key")):
        with pytest.raises(FrozenInstanceError):
            setattr(binding, field, 1)


def test_every_quantity_has_a_binding() -> None:
    # availability per transport is binding existence, not a None sentinel
    rest_keys = {b.quantity.key for b in REST_BINDINGS}
    for key, quantity in QUANTITY_BY_KEY.items():
        assert key in MODBUS_BINDING_BY_KEY or key in rest_keys, quantity.name
