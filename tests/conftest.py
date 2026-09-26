"""Set up some common test helper things."""

import asyncio
from typing import Any, cast
from unittest.mock import patch

import pytest
from homeassistant.const import CONF_ADDRESS, CONF_API_KEY, CONF_HOST, CONF_PORT
from homeassistant.setup import async_setup_component
from homeassistant.util.json import (
    JsonValueType,
)
from modbus_connection import (
    ModbusProtocolError,
    ServerDeviceBusyError,
)
from pytest_homeassistant_custom_component.common import (
    MockConfigEntry,
)
from pytest_homeassistant_custom_component.syrupy import HomeAssistantSnapshotExtension
from syrupy.assertion import SnapshotAssertion

from custom_components.xtherma_fp.const import (
    CONF_CONNECTION,
    CONF_CONNECTION_MODBUSTCP,
    CONF_CONNECTION_RESTAPI,
    CONF_SERIAL_NUMBER,
    DOMAIN,
    FERNPORTAL_URL,
    VERSION,
)
from custom_components.xtherma_fp.pytherma.addresses import (
    MODBUS_REGISTER_SIZE,
    REGISTER_RANGES,
)
from custom_components.xtherma_fp.pytherma.testing import FakeUnit
from tests.const import (
    MOCK_API_KEY,
    MOCK_CONFIG_ENTRY_ID,
    MOCK_MODBUS_ADDRESS,
    MOCK_MODBUS_HOST,
    MOCK_MODBUS_PORT,
    MOCK_SERIAL_NUMBER,
)


@pytest.fixture
def snapshot(snapshot: SnapshotAssertion) -> SnapshotAssertion:
    """Return snapshot assertion fixture with the Home Assistant extension."""
    return snapshot.use_extension(HomeAssistantSnapshotExtension)


@pytest.fixture(autouse=True)
def auto_enable_custom_integrations(enable_custom_integrations):
    return


@pytest.fixture(autouse=True)
async def setup_dependencies(hass):
    """Automatically set up core dependencies like modbus for all tests."""
    assert await async_setup_component(hass, "modbus", {"modbus": []})
    await hass.async_block_till_done()


type MockRestParamResponse = JsonValueType
type MockRestParamHttpError = int | None
type MockRestParamTimeoutError = bool | None
# Type of parameter which mock_rest_api_client expects
type MockRestParam = dict[
    str, MockRestParamResponse | MockRestParamHttpError | MockRestParamTimeoutError
]


@pytest.fixture
async def mock_rest_api_client(aioclient_mock, request: pytest.FixtureRequest):
    """Fixture preparing aioclient_mock to return prepared data.

    Used to test REST API connection. The fixture requires a parameter of type MockRestParam
    which allows to define the data to be delivered to the modbus client.

    MockRestParam is dict with the following keys:
    "response" -> Data received from the server
    "http_error" -> HTTP error to be simulated (int, optional)
    "timeout_error" -> timeout to be caused (Boolean, optional)
    """
    assert isinstance(request.param, dict)
    param = cast("MockRestParam", request.param)

    response = param.get("response")
    http_error = param.get("http_error")
    timeout_error = param.get("timeout_error")

    url = f"{FERNPORTAL_URL}/{MOCK_SERIAL_NUMBER}"
    if http_error is not None:
        aioclient_mock.get(url, status=http_error)
    elif timeout_error:

        def raise_timeout(*args, **kwargs):
            raise asyncio.exceptions.TimeoutError

        aioclient_mock.get(url, side_effect=raise_timeout)
    else:
        aioclient_mock.get(url, json=response)


async def init_integration(
    hass,
    mock_rest_api_client,
    config_data: dict[str, Any] | None = None,
    options: dict[str, Any] | None = None,
) -> MockConfigEntry:
    """Integration using REST API."""
    _config_data: dict[str, Any] = {
        CONF_CONNECTION: CONF_CONNECTION_RESTAPI,
        CONF_API_KEY: MOCK_API_KEY,
        CONF_SERIAL_NUMBER: MOCK_SERIAL_NUMBER,
    }
    if config_data:
        _config_data.update(config_data)

    _options: dict[str, Any] = {}
    if options:
        _options.update(options)

    # Create a mock config entry
    entry = MockConfigEntry(
        domain=DOMAIN,
        data=_config_data,
        options=_options,
        entry_id=MOCK_CONFIG_ENTRY_ID,
        version=VERSION,
        title="test_entry_xtherma_config",
        source="user",
    )
    entry.add_to_hass(hass)

    await hass.config_entries.async_setup(entry.entry_id)
    await hass.async_block_till_done()

    return entry


type MockModbusParamRegisters = list[int]
type MockModbusParamExceptionCode = int | None
type MockModbusParamReadResult = dict[
    str, MockModbusParamRegisters | MockModbusParamExceptionCode
]
# Type of parameter which mock_modbus_tcp_client expects
type MockModbusParam = list[MockModbusParamReadResult]

# the modbus component's unit factory; a config flow probe uses
# ``config_flow.async_get_temporary_unit`` (covered by patching the
# ``XthermaClientModbus.connect`` boundary in the validation tests)
# NOTE: patch the package module directly (``xtherma_fp.async_get_unit``);
# the ``.__init__`` spelling resolves to a duplicate module object and the
# patch would silently miss the integration's module
MODBUS_CLIENT_PATH = "custom_components.xtherma_fp.async_get_unit"


@pytest.fixture
async def mock_modbus_tcp_client(request: pytest.FixtureRequest):
    """Fixture patching the Modbus transport unit to return prepared data.

    Used to test Modbus/TCP connection. The fixture requires a parameter of type MockModbusParam
    which allows to define the data to be delivered to the modbus client.

    MockModbusParam is a list of MockModbusParamReadResults. Each read result
    corresponds to one call to read_holding_registers() in the modbus client
    (results repeat in register-range order). A result is a dict with the
    following keys:
    "registers" -> register data
    "exc_code" -> exception to be thrown to the client (optional)

    The fixture builds an in-memory :class:`pytherma.testing.FakeUnit`
    (vendored at ``custom_components.xtherma_fp.pytherma``)
    from the parameter and patches the unit factory used by the client
    (``custom_components.xtherma_fp.async_get_unit``).
    """
    assert isinstance(request.param, list)
    param = request.param

    # Build a flat register image as a fallback; each read result is placed at
    # the offset of the range it belongs to (last write wins).
    image = [0] * MODBUS_REGISTER_SIZE
    for i, read_result in enumerate(param):
        assert isinstance(read_result, dict)
        reg_list = read_result.get("registers")
        if reg_list is None:
            continue
        reg_list = cast("MockModbusParamRegisters", reg_list)
        first_reg = REGISTER_RANGES[i % len(REGISTER_RANGES)].first_reg
        image[first_reg : first_reg + len(reg_list)] = reg_list

    unit = FakeUnit(image=image)
    # Script the per-call read results, in call order.
    for read_result in param:
        exc_code = read_result.get("exc_code")
        reg_list = read_result.get("registers")
        if exc_code is not None:
            # exc_code carries the pymodbus ExcCodes value from the test data
            if exc_code == 6:  # ExcCodes.DEVICE_BUSY
                unit.queue_read_result(ServerDeviceBusyError())
            else:
                unit.queue_read_result(ModbusProtocolError())
        else:
            unit.queue_read_result(
                cast("MockModbusParamRegisters", list(reg_list))
                if reg_list is not None
                else None
            )

    with patch(MODBUS_CLIENT_PATH, return_value=unit):
        yield unit


async def init_modbus_integration(
    hass,
    mock_modbus_tcp_client,
    config_data: dict[str, Any] | None = None,
    options: dict[str, Any] | None = None,
) -> MockConfigEntry:
    """Integration using Modbus."""
    _config_data: dict[str, Any] = {
        CONF_CONNECTION: CONF_CONNECTION_MODBUSTCP,
        CONF_SERIAL_NUMBER: MOCK_SERIAL_NUMBER,
        CONF_HOST: MOCK_MODBUS_HOST,
        CONF_PORT: MOCK_MODBUS_PORT,
        CONF_ADDRESS: MOCK_MODBUS_ADDRESS,
    }
    if config_data:
        _config_data.update(config_data)

    _options: dict[str, Any] = {}
    if options:
        _options.update(options)

    entry = MockConfigEntry(
        domain=DOMAIN,
        data=_config_data,
        options=_options,
        entry_id=MOCK_CONFIG_ENTRY_ID,
        version=VERSION,
        title="test_entry_xtherma_modbus_config",
        source="user",
    )
    entry.add_to_hass(hass)

    # Call async_setup_entry()
    await hass.config_entries.async_setup(entry.entry_id)
    await hass.async_block_till_done()

    return entry
