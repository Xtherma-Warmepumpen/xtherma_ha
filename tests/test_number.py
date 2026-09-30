"""Tests for the Xtherma number platform."""

from unittest.mock import patch

import pytest
from homeassistant.components.number import DOMAIN
from homeassistant.components.number.const import ATTR_VALUE, SERVICE_SET_VALUE
from homeassistant.const import ATTR_ENTITY_ID, Platform
from homeassistant.exceptions import HomeAssistantError
from pytest_homeassistant_custom_component.common import snapshot_platform

from custom_components.xtherma_fp.xtherma_client_common import XthermaReadOnlyError
from tests.helpers import provide_modbus_data, provide_rest_data

from .conftest import init_integration, init_modbus_integration

NUMBER_ENTITY_ID_451 = (
    "number.test_entry_xtherma_config_cooling_curve_2_outside_temperature_low_p1"
)
NUMBER_ENTITY_ID_MODBUS_451 = (
    "number.test_entry_xtherma_modbus_config_cooling_curve_2_outside_temperature_low_p1"
)
NUMBER_ENTITY_ID_MODBUS_411 = (
    "number.test_entry_xtherma_modbus_config_heating_curve_2_outside_temperature_low_p1"
)


@pytest.mark.parametrize("mock_rest_api_client", provide_rest_data(), indirect=True)
async def test_setup_number_rest_api(
    hass, entity_registry, snapshot, mock_rest_api_client
) -> None:
    """Test the setup of number platform using REST API."""
    with patch("custom_components.xtherma_fp._PLATFORMS", [Platform.NUMBER]):
        entry = await init_integration(hass, mock_rest_api_client)

    await snapshot_platform(hass, entity_registry, snapshot, entry.entry_id)


@pytest.mark.parametrize("mock_modbus_tcp_client", provide_modbus_data(), indirect=True)
async def test_setup_number_modbus_tcp(
    hass, entity_registry, snapshot, mock_modbus_tcp_client
) -> None:
    """Test the setup of number platform using MODBUS TCP."""
    with patch("custom_components.xtherma_fp._PLATFORMS", [Platform.NUMBER]):
        entry = await init_modbus_integration(hass, mock_modbus_tcp_client)

    await snapshot_platform(hass, entity_registry, snapshot, entry.entry_id)


@pytest.mark.parametrize("mock_rest_api_client", provide_rest_data(), indirect=True)
async def test_set_number_rest_error(hass, mock_rest_api_client):
    await init_integration(hass, mock_rest_api_client)

    # init_integration uses REST-API, which cannot write
    with pytest.raises(HomeAssistantError) as exc_info:
        await hass.services.async_call(
            DOMAIN,
            SERVICE_SET_VALUE,
            {
                ATTR_ENTITY_ID: NUMBER_ENTITY_ID_451,
                ATTR_VALUE: 16.0,
            },
            blocking=True,
        )
    assert isinstance(exc_info.value.__cause__, XthermaReadOnlyError)


@pytest.mark.parametrize("mock_modbus_tcp_client", provide_modbus_data(), indirect=True)
# check writing positive values
async def test_set_number_modbus(hass, mock_modbus_tcp_client):
    await init_modbus_integration(hass, mock_modbus_tcp_client)

    await hass.services.async_call(
        DOMAIN,
        SERVICE_SET_VALUE,
        {
            ATTR_ENTITY_ID: NUMBER_ENTITY_ID_MODBUS_451,
            ATTR_VALUE: 16.0,
        },
        blocking=True,
    )

    unit_id, address, value = mock_modbus_tcp_client.write_calls[-1]
    # verify arguments passed to write_register()
    assert address == 41
    assert hass.states.get(NUMBER_ENTITY_ID_MODBUS_451).state == "16"
    assert value == 16
    assert unit_id == 1


# check writing negative values as 2s complement
@pytest.mark.parametrize("mock_modbus_tcp_client", provide_modbus_data(), indirect=True)
async def test_set_negative_number_modbus(hass, mock_modbus_tcp_client):
    await init_modbus_integration(hass, mock_modbus_tcp_client)

    await hass.services.async_call(
        DOMAIN,
        SERVICE_SET_VALUE,
        {
            ATTR_ENTITY_ID: NUMBER_ENTITY_ID_MODBUS_411,
            ATTR_VALUE: -20.0,
        },
        blocking=True,
    )

    unit_id, address, value = mock_modbus_tcp_client.write_calls[-1]
    # verify arguments passed to write_register()
    assert address == 31
    assert hass.states.get(NUMBER_ENTITY_ID_MODBUS_411).state == "-20"
    assert value == (20 ^ 65535) + 1
    assert unit_id == 1
