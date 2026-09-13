"""Common tests."""

import pytest
from homeassistant.helpers.entity import EntityDescription
from pytest_homeassistant_custom_component.common import load_json_value_fixture

from custom_components.xtherma_fp.const import (
    KEY_ENTRY_INPUT_FACTOR,
    KEY_ENTRY_KEY,
    KEY_ENTRY_OUTPUT_FACTOR,
)
from custom_components.xtherma_fp.entity_descriptors import (
    MODBUS_ENTITY_DESCRIPTIONS,
    XtNumericEntityDescription,
)
from tests.helpers import (
    flatten_mock_data,
    load_mock_data,
)


def test_json_load_value_fixture():
    data = load_json_value_fixture("rest_response.json")
    assert isinstance(data, dict)
    assert len(data) == 3
    assert data.get("serial_number") == "FP-04-123456"
    settings = data.get("settings")
    assert isinstance(settings, list)
    assert len(settings) == 36
    telemetry = data.get("telemetry")
    assert isinstance(telemetry, list)
    assert len(telemetry) == 55
    t0 = telemetry[0]
    assert isinstance(t0, dict)
    assert t0.get("key") == "tvl"
    assert t0.get("output_factor") == "/10"
    tlast = telemetry[53]
    assert isinstance(tlast, dict)
    assert tlast.get("key") == "mode"
    assert tlast.get("value") == 3


# disable this for now. Should we decide to use the factors embedded
# in the REST API response, we can enable this
@pytest.mark.skip(reason="Disabling test_input_factors")
def test_input_factors():  # noqa: C901
    """Verify that input_factors in REST response match Modbus descriptors."""
    """Verify that input_factors in REST response match Modbus descriptors."""
    mock_data = load_mock_data("rest_response.json")
    flattened_mock_data = flatten_mock_data(mock_data)

    def find_desc_by_key(key: str) -> EntityDescription | None:
        for reg_desc in MODBUS_ENTITY_DESCRIPTIONS:
            for desc in reg_desc.descriptors:
                if desc is None:
                    continue
                if desc.key == key:
                    return desc
        pytest.fail(f"Unknown key {key}")

    for entry in flattened_mock_data:
        key = entry[KEY_ENTRY_KEY]
        input_factor = entry.get(KEY_ENTRY_INPUT_FACTOR)
        output_factor = entry.get(KEY_ENTRY_OUTPUT_FACTOR)
        factor = ""
        if output_factor:
            factor = output_factor
        if input_factor:
            factor = input_factor
        desc = find_desc_by_key(key)
        if not isinstance(desc, XtNumericEntityDescription):
            assert not factor
            continue
        if factor != desc.factor:
            assert (not factor and not desc.factor) or (factor == desc.factor), (
                f"Factor mismatch for key '{key}' '{key}'"
            )
