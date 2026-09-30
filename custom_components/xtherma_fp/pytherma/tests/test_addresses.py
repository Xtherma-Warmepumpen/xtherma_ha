"""Tests for the Modbus address layout (ranges, coverage, empty-data anchors)."""

from custom_components.xtherma_fp.pytherma.addresses import (
    MODBUS_REGISTER_SIZE,
    REGISTER_RANGES,
)
from custom_components.xtherma_fp.pytherma.bindings import (
    MODBUS_BINDING_BY_KEY,
    MODBUS_BINDINGS,
)


def test_register_ranges() -> None:
    # exactly two ranges, so this test must be updated when the layout changes
    assert len(REGISTER_RANGES) == 2
    for r in REGISTER_RANGES:
        # the modbus protocol only allows reading up to 125 registers at once
        assert r.length <= 125, f"range {r} exceeds the modbus read limit"
        assert r.first_reg <= r.non_empty_reg <= r.last_reg, f"range {r}"
    assert MODBUS_REGISTER_SIZE == 194


def test_all_binding_addresses_covered_by_ranges() -> None:
    def is_address_covered(address: int) -> bool:
        return any(r.first_reg <= address <= r.last_reg for r in REGISTER_RANGES)

    for binding in MODBUS_BINDINGS:
        assert is_address_covered(binding.address), (
            f"quantity {binding.quantity.key} @ {binding.address} "
            "is not covered by REGISTER_RANGES"
        )


def test_non_empty_anchor_addresses() -> None:
    # range #0: the 501 quantity can never be empty
    assert REGISTER_RANGES[0].non_empty_reg == MODBUS_BINDING_BY_KEY["501"].address
    # range #1: the controller_v quantity can never be empty
    assert REGISTER_RANGES[1].non_empty_reg == (
        MODBUS_BINDING_BY_KEY["controller_v"].address
    )
