"""Shared fixtures for the pytherma test suite."""

import pytest
from fake_unit import FakeUnit, provide_modbus_image


@pytest.fixture
def fake_unit() -> FakeUnit:
    """Return a :class:`FakeUnit` preloaded with the standard register image."""
    return FakeUnit(image=provide_modbus_image())
