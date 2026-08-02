"""Helpers for tests."""

from typing import Any, cast

import pytest
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import EntityPlatform, async_get_platforms
from homeassistant.util.json import (
    JsonValueType,
)
from pytest_homeassistant_custom_component.common import (
    load_json_value_fixture,
)

from custom_components.xtherma_fp.const import (
    DOMAIN,
    KEY_ENTRY_KEY,
    KEY_ENTRY_VALUE,
    KEY_SETTINGS,
    KEY_TELEMETRY,
)
from custom_components.xtherma_fp.entity_descriptors import (
    MODBUS_ENTITY_DESCRIPTIONS,
    MODBUS_REGISTER_RANGES,
    MODBUS_REGISTER_SIZE,
)
from tests.conftest import (
    MockModbusParam,
    MockModbusParamExceptionCode,
    MockModbusParamReadResult,
    MockModbusParamRegisters,
    MockRestParam,
    MockRestParamHttpError,
    MockRestParamTimeoutError,
)


def get_platform(hass: HomeAssistant, domain: str) -> EntityPlatform:
    platforms = async_get_platforms(hass, DOMAIN)
    for platform in platforms:
        if platform.domain == domain:
            return platform
    pytest.fail(f"We have no platfom {domain}")


def load_mock_data(filename: str) -> JsonValueType:
    """Load mock data from specified JSON file.

    The JSON file is expected to be an exact dump of the REST API response
    as documented on https://github.com/Xtherma/xtherma_api.
    """
    return load_json_value_fixture(filename)


def flatten_mock_data(mock_data: JsonValueType) -> list[dict[str, Any]]:
    """Merge telemetry and settings sections for easier access."""
    mock_data = cast("dict[str, Any]", mock_data)
    telemetry = cast("list[dict[str, int|str]]", mock_data[KEY_TELEMETRY])
    settings = cast("list[dict[str, int|str]]", mock_data[KEY_SETTINGS])
    flattened_mock_data = telemetry
    flattened_mock_data.extend(settings)
    return flattened_mock_data


def provide_rest_data(
    http_error: MockRestParamHttpError = None,
    timeout_error: MockRestParamTimeoutError = None,
) -> list[MockRestParam]:
    """Load and return canned REST response.

    Currently returns only one REST API response.
    """
    response = load_mock_data("rest_response.json")
    result: MockRestParam = {
        "response": response,
        "http_error": http_error,
        "timeout_error": timeout_error,
    }
    return [result]


def get_modbus_register_number(key: str) -> int:
    for reg_desc in MODBUS_ENTITY_DESCRIPTIONS:
        for i, desc in enumerate(reg_desc.descriptors):
            if desc is None:
                continue
            if desc.key == key:
                return reg_desc.base + i
    pytest.fail(f"Unknown key {key}")


def set_modbus_register(param: MockModbusParam, key: str, value: int):
    regno = get_modbus_register_number(key)
    # find corresponding register range and modify value
    for i, r in enumerate(MODBUS_REGISTER_RANGES):
        if regno >= r.first_reg and regno <= r.last_reg:
            offset = regno - r.first_reg
            reg_list: MockModbusParamReadResult = param[i]
            regs = cast("MockModbusParamRegisters", reg_list["registers"])
            regs[offset] = value
            return
    # cannot happen, test_modbus_register_range_coverage verifies
    # all registers are covered by MODBUS_REGISTER_RANGES
    pytest.fail(f"Key {key} not found in range?!")


# convert a REST key to corresponding Modbus key
# return None if there is no equivalent
def rest_key_to_modbus_key(key: str) -> str | None:
    if key == "error_2":
        return "error"
    if key == "hw_now":
        return "003"
    if key == "h1_active_curve":
        return "310"
    if key == "h2_active_curve":
        return "410"
    if key in ("error_1"):
        return None
    return key


def provide_modbus_data(
    exc_code: MockModbusParamExceptionCode = None,
) -> list[MockModbusParam]:
    """Return a list of complete Modbus register read-outs.

    Currently returns only one read-out based on our standard REST API response.
    """
    param = provide_empty_modbus_data(exc_code=exc_code)
    regs_list = param[0]

    # get mock data from file and write it to the correct
    # register positions
    mock_data = load_mock_data("rest_response.json")

    all_values = flatten_mock_data(mock_data)
    for entry in all_values:
        key = entry[KEY_ENTRY_KEY]
        key = rest_key_to_modbus_key(key)
        if key is None:
            continue
        raw_value = entry[KEY_ENTRY_VALUE]
        value = int(raw_value) if isinstance(raw_value, (int, str)) else 0
        set_modbus_register(regs_list, key, value)

    # The rest data does not define these values
    set_modbus_register(regs_list, "out_total", 0)
    set_modbus_register(regs_list, "x2400", 1)
    set_modbus_register(regs_list, "x2401", 1234)
    set_modbus_register(regs_list, "error", 1)

    return param


def provide_empty_modbus_data(
    exc_code: MockModbusParamExceptionCode = None,
) -> list[MockModbusParam]:
    """Return a list of complete, but empty Modbus register read-outs."""
    # flat register map
    raw_registers = [0] * MODBUS_REGISTER_SIZE

    # prepare respsonses for read_holding_registers()
    regs_list: MockModbusParam = []
    for r in MODBUS_REGISTER_RANGES:
        regs_list.append(
            {
                "registers": raw_registers[r.first_reg : r.last_reg + 1],
                "exc_code": exc_code,
            }
        )

    return [regs_list]
