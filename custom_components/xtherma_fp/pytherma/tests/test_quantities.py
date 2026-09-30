"""Tests for the transport-neutral quantity layer (quantity/binding split S1)."""

from dataclasses import FrozenInstanceError, fields

import pytest

from custom_components.xtherma_fp.pytherma.quantities import (
    QUANTITIES,
    QUANTITY_BY_KEY,
    Quantity,
)
from custom_components.xtherma_fp.pytherma.scaling import (
    FACTORS,
    RFACTORS,
)

#: the transport-neutral fields of a ``Quantity``; transport concerns
#: (Modbus address/writability, REST wire key) belong to the bindings
QUANTITY_FIELDS = (
    "key",
    "name",
    "unit",
    "factor",
    "options",
    "minimum",
    "maximum",
    "signed",
)

OPTION_KEYS = {"002", "815", "mode", "sg"}


def test_quantity_count() -> None:
    assert len(QUANTITIES) == 94
    assert len(QUANTITY_BY_KEY) == 94


def test_unique_keys() -> None:
    keys = [qty.key for qty in QUANTITIES]
    assert len(keys) == len(set(keys))


def test_quantity_by_key_consistent() -> None:
    for qty in QUANTITIES:
        assert QUANTITY_BY_KEY[qty.key] is qty


def test_field_set_is_transport_neutral() -> None:
    assert tuple(f.name for f in fields(Quantity)) == QUANTITY_FIELDS
    # the transport fields live on the bindings, never on a quantity
    assert not {"register", "writable", "api_key"} & {f.name for f in fields(Quantity)}


def test_quantity_defaults() -> None:
    qty = Quantity(key="k", name="k")
    assert qty.unit is None
    assert qty.factor is None
    assert qty.options is None
    assert qty.minimum is None
    assert qty.maximum is None
    assert qty.signed is True


def test_quantity_is_frozen() -> None:
    qty = Quantity(key="k", name="k")
    with pytest.raises(FrozenInstanceError):
        setattr(qty, "name", "other")  # noqa: B010 - the assignment must raise


def test_names_non_empty() -> None:
    for qty in QUANTITIES:
        assert qty.name, f"quantity {qty.key} has an empty name"


def test_factors_known() -> None:
    for qty in QUANTITIES:
        if qty.factor is not None:
            assert qty.factor in FACTORS, f"quantity {qty.key}: factor {qty.factor}"
            assert qty.factor in RFACTORS, f"quantity {qty.key}: factor {qty.factor}"


def test_min_max() -> None:
    for qty in QUANTITIES:
        if qty.minimum is None or qty.maximum is None:
            continue
        assert qty.minimum >= -32768, f"quantity {qty.key}: minimum {qty.minimum}"
        assert qty.maximum <= 65535, f"quantity {qty.key}: maximum {qty.maximum}"
        assert qty.minimum <= qty.maximum, f"quantity {qty.key}"


def test_option_quantities() -> None:
    option_keys = {qty.key for qty in QUANTITIES if qty.options is not None}
    assert option_keys == OPTION_KEYS
    assert QUANTITY_BY_KEY["002"].options == QUANTITY_BY_KEY["mode"].options
    options_815 = QUANTITY_BY_KEY["815"].options
    assert options_815 is not None
    assert len(options_815) == 4
    options_sg = QUANTITY_BY_KEY["sg"].options
    assert options_sg is not None
    assert len(options_sg) == 5
