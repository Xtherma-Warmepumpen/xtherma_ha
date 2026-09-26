"""Tests for the Fernportal REST API client."""

import pytest
from homeassistant.helpers import aiohttp_client

from custom_components.xtherma_fp.const import FERNPORTAL_URL
from custom_components.xtherma_fp.xtherma_client_common import (
    XthermaRestMalformedError,
)
from custom_components.xtherma_fp.xtherma_client_rest import XthermaClientRest
from tests.const import MOCK_API_KEY, MOCK_SERIAL_NUMBER

_URL = f"{FERNPORTAL_URL}/{MOCK_SERIAL_NUMBER}"


def _client(hass) -> XthermaClientRest:
    return XthermaClientRest(
        url=FERNPORTAL_URL,
        api_key=MOCK_API_KEY,
        serial_number=MOCK_SERIAL_NUMBER,
        session=aiohttp_client.async_get_clientsession(hass),
    )


@pytest.mark.parametrize(
    "payload",
    [
        {},  # missing telemetry and settings
        {"telemetry": "not-a-list", "settings": []},
        {"telemetry": [], "settings": None},
    ],
)
async def test_malformed_payload_raises(hass, aioclient_mock, payload):
    """R-1 (D2): a malformed REST payload must fail the update."""
    aioclient_mock.get(_URL, json=payload)
    with pytest.raises(XthermaRestMalformedError, match="malformed REST API response"):
        await _client(hass).async_get_data()


async def test_decimal_string_entry_skipped(hass, aioclient_mock):
    """R-1: an entry with a decimal string value is skipped, not fatal."""
    aioclient_mock.get(
        _URL,
        json={
            "telemetry": [],
            "settings": [
                {"key": "310", "value": 1},
                {"key": "311", "value": "-9.5"},
            ],
        },
    )
    data = await _client(hass).async_get_data()
    assert data == {"310": 1}
