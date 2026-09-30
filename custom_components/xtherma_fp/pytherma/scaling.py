"""Scaling factor utilities for register values.

A factor is a string like ``"/10"`` describing how to convert between a raw
register value and its scaled value. :data:`FACTORS` converts a raw value to
its scaled representation (used on read), :data:`RFACTORS` converts back
(used on write).
"""

from collections.abc import Callable

Factor = Callable[[int | float], float | int]

#: Supported factor strings mapped to ``(numerator, denominator)`` with
#: ``scaled = raw * numerator / denominator``. Exactly one of the two is
#: ``1`` for every supported factor, which keeps integer factors on pure
#: integer arithmetic (matching the previous hand-written tables exactly).
_FACTORS: dict[str, tuple[int, int]] = {
    "*1000": (1000, 1),
    "*100": (100, 1),
    "*10": (10, 1),
    "1000": (1000, 1),
    "100": (100, 1),
    "10": (10, 1),
    "/1000": (1, 1000),
    "/100": (1, 100),
    "/10": (1, 10),
}


def _make(numerator: int, denominator: int) -> Factor:
    """Build a scaling function, keeping integer-only ops on ``int`` math."""
    if denominator == 1:
        return lambda value: value * numerator
    return lambda value: value / denominator


FACTORS: dict[str, Factor] = {
    factor: _make(num, den) for factor, (num, den) in _FACTORS.items()
}

RFACTORS: dict[str, Factor] = {
    factor: _make(den, num) for factor, (num, den) in _FACTORS.items()
}


def apply_factor(value: int, factor: str | None) -> int | float:
    """Apply a scaling factor to a raw register value."""
    if not factor:
        return value
    function = FACTORS.get(factor, lambda value: value)
    return function(value)


def reverse_factor(value: int | float, factor: str | None) -> int:
    """Reverse a scaling factor to recover the raw register value."""
    if not isinstance(factor, str):
        return int(value)
    function = RFACTORS.get(factor, lambda value: value)
    return round(function(value))
