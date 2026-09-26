"""Tests for the Xtherma switch platform."""

from unittest.mock import patch

import pytest
from homeassistant.components.switch.const import DOMAIN
from homeassistant.const import (
    ATTR_ENTITY_ID,
    SERVICE_TURN_OFF,
    SERVICE_TURN_ON,
    STATE_OFF,
    STATE_ON,
    Platform,
)
from homeassistant.exceptions import HomeAssistantError
from modbus_connection import ModbusConnectionError
from pytest_homeassistant_custom_component.common import snapshot_platform

from custom_components.xtherma_fp.pytherma.exceptions import (
    XthermaNotConnectedError,
)
from custom_components.xtherma_fp.xtherma_client_common import XthermaReadOnlyError
from tests.helpers import provide_modbus_data, provide_rest_data

from .conftest import init_integration, init_modbus_integration

SWITCH_ENTITY_ID_450 = "switch.test_entry_xtherma_config_cooling_curve_2_active"
SWITCH_ENTITY_ID_MODBUS_450 = (
    "switch.test_entry_xtherma_modbus_config_cooling_curve_2_active"
)


@pytest.mark.parametrize("mock_rest_api_client", provide_rest_data(), indirect=True)
async def test_setup_switch_rest_api(
    hass, entity_registry, snapshot, mock_rest_api_client
) -> None:
    """Test the setup of switch platform using REST API."""
    with patch("custom_components.xtherma_fp._PLATFORMS", [Platform.SWITCH]):
        entry = await init_integration(hass, mock_rest_api_client)

    await snapshot_platform(hass, entity_registry, snapshot, entry.entry_id)


@pytest.mark.parametrize("mock_modbus_tcp_client", provide_modbus_data(), indirect=True)
async def test_setup_select_modbus_tcp(
    hass, entity_registry, snapshot, mock_modbus_tcp_client
) -> None:
    """Test the setup of switch platform using MODBUS TCP."""
    with patch("custom_components.xtherma_fp._PLATFORMS", [Platform.SWITCH]):
        entry = await init_modbus_integration(hass, mock_modbus_tcp_client)

    await snapshot_platform(hass, entity_registry, snapshot, entry.entry_id)


@pytest.mark.parametrize("mock_rest_api_client", provide_rest_data(), indirect=True)
async def test_set_switch_rest(hass, mock_rest_api_client):
    await init_integration(hass, mock_rest_api_client)

    # init_integration uses REST-API, which cannot write
    with pytest.raises(HomeAssistantError) as exc_info:
        await hass.services.async_call(
            DOMAIN,
            SERVICE_TURN_OFF,
            {ATTR_ENTITY_ID: SWITCH_ENTITY_ID_450},
            blocking=True,
        )

    assert isinstance(exc_info.value.__cause__, XthermaReadOnlyError)


@pytest.mark.parametrize("mock_modbus_tcp_client", provide_modbus_data(), indirect=True)
async def test_set_switch_modbus(hass, mock_modbus_tcp_client):
    await init_modbus_integration(hass, mock_modbus_tcp_client)

    await hass.services.async_call(
        DOMAIN,
        SERVICE_TURN_OFF,
        {ATTR_ENTITY_ID: SWITCH_ENTITY_ID_MODBUS_450},
        blocking=True,
    )

    assert hass.states.get(SWITCH_ENTITY_ID_MODBUS_450).state == STATE_OFF
    unit_id, address, value = mock_modbus_tcp_client.write_calls[-1]
    # verify arguments passed to write_register()
    assert address == 40
    assert value == 0
    assert unit_id == 1

    await hass.services.async_call(
        DOMAIN,
        SERVICE_TURN_ON,
        {ATTR_ENTITY_ID: SWITCH_ENTITY_ID_MODBUS_450},
        blocking=True,
    )

    assert hass.states.get(SWITCH_ENTITY_ID_MODBUS_450).state == STATE_ON
    unit_id, address, value = mock_modbus_tcp_client.write_calls[-1]
    # verify arguments passed to write_register()
    assert address == 40
    assert value == 1
    assert unit_id == 1


@pytest.mark.parametrize("mock_modbus_tcp_client", provide_modbus_data(), indirect=True)
async def test_set_switch_modbus_not_connected(hass, mock_modbus_tcp_client):
    """Writing while the modbus link is down raises HomeAssistantError."""
    await init_modbus_integration(hass, mock_modbus_tcp_client)

    mock_modbus_tcp_client.queue_write_error(ModbusConnectionError())

    with pytest.raises(HomeAssistantError) as exc_info:
        await hass.services.async_call(
            DOMAIN,
            SERVICE_TURN_ON,
            {ATTR_ENTITY_ID: SWITCH_ENTITY_ID_MODBUS_450},
            blocking=True,
        )

    assert isinstance(exc_info.value.__cause__, XthermaNotConnectedError)
    assert exc_info.value.translation_key == "modbus_write_not_connected_error"
