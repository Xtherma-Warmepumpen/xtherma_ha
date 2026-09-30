"""Tests for the scaling factor utilities."""

import pytest

from custom_components.xtherma_fp.pytherma.scaling import (
    FACTORS,
    RFACTORS,
    apply_factor,
    reverse_factor,
)


@pytest.mark.parametrize(
    ("factor", "raw", "scaled"),
    [
        ("*1000", 1, 1000),
        ("*100", 1, 100),
        ("*10", 23, 230),
        ("1000", 1, 1000),
        ("100", 1, 100),
        ("10", 23, 230),
        ("/1000", 1000, 1),
        ("/100", 150, 1.5),
        ("/10", 230, 23),
        (None, 42, 42),
        ("", 42, 42),
        ("unknown", 42, 42),
    ],
)
def test_apply_factor(factor: str | None, raw: int, scaled: int | float) -> None:
    assert apply_factor(raw, factor) == scaled


@pytest.mark.parametrize(
    ("factor", "scaled", "raw"),
    [
        ("*1000", 1000, 1),
        ("*100", 100, 1),
        ("*10", 230, 23),
        ("1000", 1000, 1),
        ("100", 100, 1),
        ("10", 230, 23),
        ("/1000", 1, 1000),
        ("/100", 1.5, 150),
        ("/10", 23, 230),
        # floats whose product is off by an ulp must round, not truncate
        ("/10", 0.7, 7),
        ("/10", -0.3, -3),
        ("/10", -0.7, -7),
        ("/100", 1.15, 115),
        ("/100", -0.3, -30),
        (None, 42, 42),
        ("unknown", 42, 42),
    ],
)
def test_reverse_factor(factor: str | None, scaled: float, raw: int) -> None:
    assert reverse_factor(scaled, factor) == raw
    assert isinstance(reverse_factor(scaled, factor), int)


def test_factor_tables_are_inverses() -> None:
    for factor in FACTORS:
        assert factor in RFACTORS
        # raw values chosen so the float round trip is exact or within
        # an ulp (reverse_factor rounds, so off-by-ulp stays lossless)
        for raw in (-7, -5, -3, 0, 1, 7, 10, 100, 1000):
            assert reverse_factor(apply_factor(raw, factor), factor) == raw
