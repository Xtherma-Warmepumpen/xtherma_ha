"""Test config flow."""

import asyncio
from contextlib import asynccontextmanager
from typing import TYPE_CHECKING, cast
from unittest.mock import patch

import pytest
from homeassistant.config_entries import (
    SOURCE_USER,
    ConfigEntryState,
)
from homeassistant.const import (
    CONF_ADDRESS,
    CONF_API_KEY,
    CONF_HOST,
    CONF_NAME,
    CONF_PORT,
)
from homeassistant.data_entry_flow import FlowResultType

from custom_components.xtherma_fp import DOMAIN, XthermaData
from custom_components.xtherma_fp.config_flow import (
    _validate_connection,
    _validate_modbus_tcp,
    _validate_rest_api,
)
from custom_components.xtherma_fp.const import (
    CONF_CONNECTION,
    CONF_CONNECTION_MODBUSTCP,
    CONF_CONNECTION_RESTAPI,
    CONF_DETECT_EMPTY_MODBUS_DATA,
    CONF_SERIAL_NUMBER,
    FERNPORTAL_URL,
)
from custom_components.xtherma_fp.pytherma.exceptions import (
    XthermaNotConnectedError,
)
from custom_components.xtherma_fp.pytherma.testing import FakeUnit
from custom_components.xtherma_fp.xtherma_client_common import (
    XthermaError,
    XthermaRestApiError,
    XthermaRestBusyError,
    XthermaTimeoutError,
)
from tests.conftest import init_integration, init_modbus_integration
from tests.const import (
    MOCK_API_KEY,
    MOCK_MODBUS_ADDRESS,
    MOCK_MODBUS_HOST,
    MOCK_MODBUS_PORT,
    MOCK_NAME,
    MOCK_SERIAL_NUMBER,
)
from tests.helpers import load_mock_data, provide_modbus_data, provide_rest_data

if TYPE_CHECKING:
    from custom_components.xtherma_fp.coordinator import XthermaDataUpdateCoordinator
    from custom_components.xtherma_fp.xtherma_client_modbus import XthermaClientModbus

MOCK_REST_DATA = {CONF_NAME: MOCK_NAME, CONF_API_KEY: MOCK_API_KEY}

MOCK_MODBUS_DATA = {
    CONF_NAME: MOCK_NAME,
    CONF_HOST: MOCK_MODBUS_HOST,
    CONF_PORT: MOCK_MODBUS_PORT,
    CONF_ADDRESS: MOCK_MODBUS_ADDRESS,
}


@asynccontextmanager
async def _temporary_unit_context(unit):
    """Yield a prepared unit as a temporary unit."""
    yield unit


def _temporary_unit_factory(hass, params, address):
    """Stand-in for the modbus component's temporary unit factory.

    Yields a zero-image unit; the validation probe raises in the
    patched ``XthermaClientModbus.connect`` before any data is read.
    """
    return _temporary_unit_context(FakeUnit())


async def test_config_common_bad_arguments(hass):
    """Test giving bad config dat to REST API config flow."""
    result = await hass.config_entries.flow.async_init(
        "xtherma_fp",
        context={"source": SOURCE_USER},
    )

    assert result["type"] is FlowResultType.FORM
    assert result["step_id"] == SOURCE_USER

    result = await hass.config_entries.flow.async_configure(
        result["flow_id"],
        user_input={
            CONF_NAME: MOCK_NAME,
            CONF_SERIAL_NUMBER: "SerialNumbersMustBeginWithFP",
            CONF_CONNECTION: CONF_CONNECTION_RESTAPI,
        },
    )

    assert result["type"] is FlowResultType.FORM
    assert result["step_id"] == SOURCE_USER
    assert result["errors"] == {"base": "bad_arguments"}


async def test_rest_api_good_serial_number(hass, aioclient_mock):
    """Test giving an valid data to REST API config flow."""
    mock_data = load_mock_data("rest_response.json")
    aioclient_mock.get(
        f"{FERNPORTAL_URL}/{MOCK_SERIAL_NUMBER}",
        json=mock_data,
    )

    result = await hass.config_entries.flow.async_init(
        "xtherma_fp",
        context={"source": SOURCE_USER},
    )

    assert result["type"] is FlowResultType.FORM
    assert result["step_id"] == SOURCE_USER

    result = await hass.config_entries.flow.async_configure(
        result["flow_id"],
        user_input={
            CONF_CONNECTION: CONF_CONNECTION_RESTAPI,
            CONF_NAME: MOCK_NAME,
            CONF_SERIAL_NUMBER: MOCK_SERIAL_NUMBER,
        },
    )

    assert result["type"] is FlowResultType.FORM
    assert result["step_id"] == "rest_api"

    result = await hass.config_entries.flow.async_configure(
        result["flow_id"],
        user_input={CONF_API_KEY: MOCK_API_KEY},
    )

    assert result["type"] is FlowResultType.CREATE_ENTRY


async def test_rest_error_404(hass, aioclient_mock):
    """Test forcing network errors to REST API config flow."""
    mock_data = load_mock_data("rest_response.json")
    aioclient_mock.get(
        f"{FERNPORTAL_URL}/{MOCK_SERIAL_NUMBER}",
        json=mock_data,
        status=404,
    )

    result = await hass.config_entries.flow.async_init(
        "xtherma_fp",
        context={"source": SOURCE_USER},
    )

    assert result["type"] is FlowResultType.FORM
    assert result["step_id"] == SOURCE_USER

    result = await hass.config_entries.flow.async_configure(
        result["flow_id"],
        user_input={
            CONF_CONNECTION: CONF_CONNECTION_RESTAPI,
            CONF_NAME: MOCK_NAME,
            CONF_SERIAL_NUMBER: MOCK_SERIAL_NUMBER,
        },
    )

    assert result["type"] is FlowResultType.FORM
    assert result["step_id"] == "rest_api"

    result = await hass.config_entries.flow.async_configure(
        result["flow_id"],
        user_input={CONF_API_KEY: MOCK_API_KEY},
    )
    assert result["type"] is FlowResultType.FORM
    assert result["step_id"] == "rest_api"
    # R-4: XthermaRestApiError derives from the unified XthermaError
    # base, so a 404 maps to cannot_connect instead of unknown
    assert result["errors"] == {"base": "cannot_connect"}


async def test_rest_error_429(hass, aioclient_mock):
    """Test forcing network errors to REST API config flow."""
    mock_data = load_mock_data("rest_response.json")
    aioclient_mock.get(
        f"{FERNPORTAL_URL}/{MOCK_SERIAL_NUMBER}",
        json=mock_data,
        status=429,
    )

    result = await hass.config_entries.flow.async_init(
        "xtherma_fp",
        context={"source": SOURCE_USER},
    )

    assert result["type"] is FlowResultType.FORM
    assert result["step_id"] == SOURCE_USER

    result = await hass.config_entries.flow.async_configure(
        result["flow_id"],
        user_input={
            CONF_CONNECTION: CONF_CONNECTION_RESTAPI,
            CONF_NAME: MOCK_NAME,
            CONF_SERIAL_NUMBER: MOCK_SERIAL_NUMBER,
        },
    )

    assert result["type"] is FlowResultType.FORM
    assert result["step_id"] == "rest_api"

    result = await hass.config_entries.flow.async_configure(
        result["flow_id"],
        user_input={CONF_API_KEY: MOCK_API_KEY},
    )
    assert result["type"] is FlowResultType.FORM
    assert result["step_id"] == "rest_api"
    assert result["errors"] == {"base": "rate_limit"}


async def test_rest_error_timeout(hass, aioclient_mock):
    """Test forcing network errors to REST API config flow."""
    aioclient_mock.get(
        f"{FERNPORTAL_URL}/{MOCK_SERIAL_NUMBER}",
        exc=asyncio.exceptions.TimeoutError,
    )

    result = await hass.config_entries.flow.async_init(
        "xtherma_fp",
        context={"source": SOURCE_USER},
    )

    assert result["type"] is FlowResultType.FORM
    assert result["step_id"] == SOURCE_USER

    result = await hass.config_entries.flow.async_configure(
        result["flow_id"],
        user_input={
            CONF_CONNECTION: CONF_CONNECTION_RESTAPI,
            CONF_NAME: MOCK_NAME,
            CONF_SERIAL_NUMBER: MOCK_SERIAL_NUMBER,
        },
    )

    assert result["type"] is FlowResultType.FORM
    assert result["step_id"] == "rest_api"

    result = await hass.config_entries.flow.async_configure(
        result["flow_id"],
        user_input={CONF_API_KEY: MOCK_API_KEY},
    )
    assert result["type"] is FlowResultType.FORM
    assert result["step_id"] == "rest_api"
    assert result["errors"] == {"base": "timeout"}


@pytest.mark.parametrize("mock_rest_api_client", provide_rest_data(), indirect=True)
async def test_step_user_abort_entries_match(hass, mock_rest_api_client):
    """Test for matching configuration parameters in step_user."""
    entry = await init_integration(hass, mock_rest_api_client)
    config_data = entry.data.copy()

    result = await hass.config_entries.flow.async_init(
        DOMAIN,
        context={"source": SOURCE_USER},
        data=config_data,
    )

    assert result["type"] == FlowResultType.ABORT
    assert result["reason"] == "already_configured"


@pytest.mark.parametrize("mock_modbus_tcp_client", provide_modbus_data(), indirect=True)
async def test_step_modbus_tcp_abort_entries_match(hass, mock_modbus_tcp_client):
    """Test for matching configuration parameters in step_modbus_tcp."""
    entry = await init_modbus_integration(hass, mock_modbus_tcp_client)
    config_data = entry.data.copy()

    result = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": "modbus_tcp"}, data=config_data
    )
    assert result["type"] == FlowResultType.ABORT
    assert result["reason"] == "already_configured"


@pytest.mark.parametrize("mock_rest_api_client", provide_rest_data(), indirect=True)
async def test_step_reconfigure_rest_api(hass, mock_rest_api_client):
    """Test for reconfiguring to rest api."""
    entry = await init_integration(hass, mock_rest_api_client)
    assert entry.state is ConfigEntryState.LOADED
    assert entry.data == entry.data | {
        CONF_CONNECTION: CONF_CONNECTION_RESTAPI,
        CONF_API_KEY: MOCK_API_KEY,
    }

    reconfigure_result = await entry.start_reconfigure_flow(hass)
    assert reconfigure_result["type"] is FlowResultType.FORM
    assert reconfigure_result["step_id"] == "reconfigure"

    reconfigure_result = await hass.config_entries.flow.async_configure(
        reconfigure_result["flow_id"],
        {
            CONF_SERIAL_NUMBER: MOCK_SERIAL_NUMBER,
            CONF_CONNECTION: CONF_CONNECTION_RESTAPI,
        },
    )
    assert reconfigure_result["type"] is FlowResultType.FORM

    with patch(
        "custom_components.xtherma_fp.config_flow._validate_rest_api", return_value={}
    ):
        reconfigure_result = await hass.config_entries.flow.async_configure(
            reconfigure_result["flow_id"],
            {
                CONF_API_KEY: MOCK_API_KEY + "_changed",
            },
        )
    assert reconfigure_result["type"] is FlowResultType.ABORT
    assert reconfigure_result["reason"] == "reconfigure_successful"

    assert entry.data == entry.data | {
        CONF_CONNECTION: CONF_CONNECTION_RESTAPI,
        CONF_API_KEY: MOCK_API_KEY + "_changed",
    }


@pytest.mark.parametrize("mock_rest_api_client", provide_rest_data(), indirect=True)
async def test_step_reconfigure_rest_api_errors(hass, mock_rest_api_client):
    """Test for reconfiguring to rest api with errors."""
    errors = {"base": "any_error"}

    entry = await init_integration(hass, mock_rest_api_client)
    assert entry.state is ConfigEntryState.LOADED
    assert entry.data == entry.data | {
        CONF_CONNECTION: CONF_CONNECTION_RESTAPI,
        CONF_API_KEY: MOCK_API_KEY,
    }

    reconfigure_result = await entry.start_reconfigure_flow(hass)
    assert reconfigure_result["type"] is FlowResultType.FORM
    assert reconfigure_result["step_id"] == "reconfigure"

    reconfigure_result = await hass.config_entries.flow.async_configure(
        reconfigure_result["flow_id"],
        {
            CONF_SERIAL_NUMBER: MOCK_SERIAL_NUMBER,
            CONF_CONNECTION: CONF_CONNECTION_RESTAPI,
        },
    )
    assert reconfigure_result["type"] is FlowResultType.FORM

    with patch(
        "custom_components.xtherma_fp.config_flow._validate_rest_api",
        return_value=errors,
    ):
        reconfigure_result = await hass.config_entries.flow.async_configure(
            reconfigure_result["flow_id"],
            {
                CONF_API_KEY: MOCK_API_KEY + "_changed",
            },
        )
    assert reconfigure_result["type"] is FlowResultType.FORM
    assert reconfigure_result["errors"] == errors


@pytest.mark.parametrize("mock_rest_api_client", provide_rest_data(), indirect=True)
@pytest.mark.parametrize("mock_modbus_tcp_client", provide_modbus_data(), indirect=True)
async def test_step_reconfigure_modbus(
    hass, mock_rest_api_client, mock_modbus_tcp_client
):
    """Test for reconfiguring to modbus."""
    entry = await init_integration(hass, mock_rest_api_client)
    assert entry.state is ConfigEntryState.LOADED
    assert entry.data[CONF_CONNECTION] == CONF_CONNECTION_RESTAPI

    reconfigure_result = await entry.start_reconfigure_flow(hass)
    assert reconfigure_result["type"] is FlowResultType.FORM
    assert reconfigure_result["step_id"] == "reconfigure"

    reconfigure_result = await hass.config_entries.flow.async_configure(
        reconfigure_result["flow_id"],
        {
            CONF_SERIAL_NUMBER: MOCK_SERIAL_NUMBER,
            CONF_CONNECTION: CONF_CONNECTION_MODBUSTCP,
        },
    )
    assert reconfigure_result["type"] is FlowResultType.FORM

    with (
        patch(
            "custom_components.xtherma_fp.config_flow._validate_modbus_tcp",
            return_value={},
        ),
        patch(
            "custom_components.xtherma_fp.xtherma_client_modbus.XthermaClientModbus.connect",
            return_value=None,
        ),
    ):
        reconfigure_result = await hass.config_entries.flow.async_configure(
            reconfigure_result["flow_id"],
            {
                CONF_HOST: MOCK_MODBUS_HOST,
                CONF_PORT: MOCK_MODBUS_PORT,
                CONF_ADDRESS: MOCK_MODBUS_ADDRESS,
            },
        )
    assert reconfigure_result["type"] is FlowResultType.ABORT
    assert reconfigure_result["reason"] == "reconfigure_successful"

    assert entry.data == entry.data | {
        CONF_CONNECTION: CONF_CONNECTION_MODBUSTCP,
        CONF_HOST: MOCK_MODBUS_HOST,
        CONF_PORT: MOCK_MODBUS_PORT,
        CONF_ADDRESS: MOCK_MODBUS_ADDRESS,
    }


@pytest.mark.parametrize("mock_rest_api_client", provide_rest_data(), indirect=True)
async def test_step_reconfigure_modbus_errors(hass, mock_rest_api_client):
    """Test for reconfiguring to modbus with errors."""
    errors = {"base": "any_error"}

    entry = await init_integration(hass, mock_rest_api_client)
    assert entry.state is ConfigEntryState.LOADED
    assert entry.data[CONF_CONNECTION] == CONF_CONNECTION_RESTAPI

    reconfigure_result = await entry.start_reconfigure_flow(hass)
    assert reconfigure_result["type"] is FlowResultType.FORM
    assert reconfigure_result["step_id"] == "reconfigure"

    reconfigure_result = await hass.config_entries.flow.async_configure(
        reconfigure_result["flow_id"],
        {
            CONF_SERIAL_NUMBER: MOCK_SERIAL_NUMBER,
            CONF_CONNECTION: CONF_CONNECTION_MODBUSTCP,
        },
    )
    assert reconfigure_result["type"] is FlowResultType.FORM

    with patch(
        "custom_components.xtherma_fp.config_flow._validate_modbus_tcp",
        return_value=errors,
    ):
        reconfigure_result = await hass.config_entries.flow.async_configure(
            reconfigure_result["flow_id"],
            {
                CONF_HOST: MOCK_MODBUS_HOST,
                CONF_PORT: MOCK_MODBUS_PORT,
                CONF_ADDRESS: MOCK_MODBUS_ADDRESS,
            },
        )
    assert reconfigure_result["type"] is FlowResultType.FORM
    assert reconfigure_result["errors"] == errors


@pytest.mark.parametrize(
    ("data", "expected_errors"),
    [
        ({CONF_SERIAL_NUMBER: "FP-04-123456"}, {}),
        (
            {CONF_SERIAL_NUMBER: "SerialNumbersMustBeginWithFP"},
            {"base": "bad_arguments"},
        ),
    ],
)
async def test_validate_connection(data, expected_errors):
    """Test for general connection validation."""
    assert await _validate_connection(data) == expected_errors


@pytest.mark.parametrize(
    ("data", "side_effect", "expected_errors"),
    [
        ({}, None, {"base": "bad_arguments"}),
        (MOCK_REST_DATA, XthermaRestBusyError, {"base": "rate_limit"}),
        (MOCK_REST_DATA, XthermaTimeoutError, {"base": "timeout"}),
        (MOCK_REST_DATA, XthermaError, {"base": "cannot_connect"}),
        # regression R-4: XthermaRestApiError derives from the unified
        # XthermaError base, so 401 maps to cannot_connect, not unknown
        (MOCK_REST_DATA, XthermaRestApiError(401), {"base": "cannot_connect"}),
        (MOCK_REST_DATA, Exception, {"base": "unknown"}),
    ],
)
async def test_validate_rest_api(hass, data, side_effect, expected_errors):
    """Test for rest api connection validation."""
    with patch(
        "custom_components.xtherma_fp.xtherma_client_rest.XthermaClientRest.connect",
        side_effect=side_effect,
    ):
        previous_data = {CONF_SERIAL_NUMBER: "FP-04-123456"}
        assert await _validate_rest_api(hass, previous_data, data) == expected_errors


@pytest.mark.parametrize(
    ("data", "side_effect", "expected_errors"),
    [
        (MOCK_MODBUS_DATA | {CONF_HOST: None}, None, {"base": "bad_arguments"}),
        (MOCK_MODBUS_DATA | {CONF_PORT: None}, None, {"base": "bad_arguments"}),
        (MOCK_MODBUS_DATA | {CONF_ADDRESS: None}, None, {"base": "bad_arguments"}),
        (MOCK_MODBUS_DATA | {CONF_PORT: 502.1}, None, {"base": "bad_arguments"}),
        (MOCK_MODBUS_DATA | {CONF_ADDRESS: 1.1}, None, {"base": "bad_arguments"}),
        (MOCK_MODBUS_DATA, XthermaTimeoutError, {"base": "timeout"}),
        (MOCK_MODBUS_DATA, XthermaNotConnectedError, {"base": "cannot_connect_modbus"}),
        (MOCK_MODBUS_DATA, Exception, {"base": "unknown"}),
    ],
)
async def test_validate_modbus_tcp(hass, data, side_effect, expected_errors):
    """Test for modbus connection validation."""
    with (
        patch(
            "custom_components.xtherma_fp.xtherma_client_modbus.XthermaClientModbus.connect",
            side_effect=side_effect,
        ),
        patch(
            "custom_components.xtherma_fp.config_flow.async_get_temporary_unit",
            _temporary_unit_factory,
        ),
    ):
        assert await _validate_modbus_tcp(hass, data) == expected_errors


@pytest.mark.parametrize("mock_modbus_tcp_client", provide_modbus_data(), indirect=True)
async def test_options_flow(hass, mock_modbus_tcp_client):
    """Test options flow."""
    entry = await init_modbus_integration(hass, mock_modbus_tcp_client)

    xtherma_data: XthermaData = entry.runtime_data
    assert xtherma_data is not None
    assert xtherma_data.coordinator is not None
    coordinator: XthermaDataUpdateCoordinator = xtherma_data.coordinator
    client = cast("XthermaClientModbus", coordinator._client)  # noqa: SLF001

    # default is not configured, no setting, default is True
    setting = entry.data.get(CONF_DETECT_EMPTY_MODBUS_DATA, None)
    assert setting is None
    assert client.detect_empty_modbus_data

    for value_to_set in [False, True]:
        result = await hass.config_entries.options.async_init(
            entry.entry_id,
        )

        assert result["type"] is FlowResultType.FORM
        assert result["step_id"] == "init"

        result = await hass.config_entries.options.async_configure(
            result["flow_id"],
            user_input={CONF_DETECT_EMPTY_MODBUS_DATA: value_to_set},
        )

        # check config result
        assert result["type"] is FlowResultType.CREATE_ENTRY
        assert result["data"][CONF_DETECT_EMPTY_MODBUS_DATA] == value_to_set

        # check that update_options_listener() was called and has applied
        # the new setting
        assert client.detect_empty_modbus_data == value_to_set
