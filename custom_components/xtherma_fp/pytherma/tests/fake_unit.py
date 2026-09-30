"""Register image builders for tests, re-exporting the shipped :class:`FakeUnit`.

The :class:`~pytherma.testing.FakeUnit` itself lives in the shipped
:mod:`pytherma.testing` module. The image builders here are bound to the
test fixture ``tests/fixtures/rest_response.json`` (which is not shipped in the
wheel) and therefore stay test-only.
"""

import json
from pathlib import Path

from custom_components.xtherma_fp.pytherma.addresses import (
    MODBUS_REGISTER_SIZE,
)
from custom_components.xtherma_fp.pytherma.bindings import (
    MODBUS_BINDING_BY_KEY,
)
from custom_components.xtherma_fp.pytherma.data_model import (
    Quantity,
)
from custom_components.xtherma_fp.pytherma.testing import (
    FakeUnit,
)

__all__ = [
    "FakeUnit",
    "provide_empty_modbus_image",
    "provide_modbus_image",
]

_FIXTURES_DIR = Path(__file__).parent / "fixtures"

_MODBUS_MAX_VALUE: int = 65535


def _encode(quantity: Quantity, value: int) -> int:
    """Encode a signed value two's complement, as a real device transmits it."""
    if quantity.signed and value < 0:
        return ((-value) ^ _MODBUS_MAX_VALUE) + 1
    return value


# convert a REST key to the corresponding Modbus register key,
# or None if there is no equivalent
def _rest_key_to_modbus_key(key: str) -> str | None:
    if key == "error_2":
        return "error"
    if key == "hw_now":
        return "003"
    if key == "h1_active_curve":
        return "310"
    if key == "h2_active_curve":
        return "410"
    if key == "error_1":
        return None
    return key


def provide_modbus_image() -> list[int]:
    """Build a full register image from the standard REST fixture.

    Mirrors the integration's ``provide_modbus_data`` test helper: fixture
    values are written to the matching register addresses. Unlike the
    integration mock (which stored signed values verbatim), negative values
    are stored two's-complement encoded, as a real device would transmit.
    """
    with (_FIXTURES_DIR / "rest_response.json").open() as f:
        mock_data = json.load(f)
    all_values = mock_data["telemetry"] + mock_data["settings"]

    image = [0] * MODBUS_REGISTER_SIZE
    for entry in all_values:
        key = _rest_key_to_modbus_key(entry["key"])
        if key is None:
            continue
        raw_value = entry["value"]
        value = int(raw_value) if isinstance(raw_value, (int, str)) else 0
        binding = MODBUS_BINDING_BY_KEY.get(key)
        if binding is not None:
            image[binding.address] = _encode(binding.quantity, value)

    # the REST fixture does not define these values
    for key, value in (
        ("out_total", 0),
        ("x2400", 1),
        ("x2401", 1234),
        ("error", 1),
    ):
        binding = MODBUS_BINDING_BY_KEY[key]
        image[binding.address] = _encode(binding.quantity, value)

    return image


def provide_empty_modbus_image() -> list[int]:
    """Return a full, but empty (all zeros) register image."""
    return [0] * MODBUS_REGISTER_SIZE
