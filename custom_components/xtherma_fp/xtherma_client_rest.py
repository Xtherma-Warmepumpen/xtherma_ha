"""Client to access Fernportal REST API."""

import asyncio
import itertools
import logging
from datetime import UTC, datetime, timedelta
from typing import Any

import aiohttp
from homeassistant.helpers.entity import EntityDescription

from .const import (
    FERNPORTAL_RATE_LIMIT_S,
    FERNPORTAL_TIMEOUT_S,
    KEY_ENTRY_KEY,
    KEY_ENTRY_VALUE,
    KEY_SETTINGS,
    KEY_TELEMETRY,
)
from .entity_descriptors import ENTITY_DESCRIPTIONS
from .pytherma.bindings import REST_BINDING_BY_API_KEY
from .pytherma.scaling import apply_factor
from .xtherma_client_common import (
    XthermaClient,
    XthermaError,
    XthermaReadOnlyError,
    XthermaRestApiError,
    XthermaRestBusyError,
    XthermaRestMalformedError,
    XthermaTimeoutError,
)

_LOGGER = logging.getLogger(__name__)


class XthermaClientRest(XthermaClient):
    """REST API access client."""

    def __init__(
        self,
        url: str,
        api_key: str,
        serial_number: str,
        session: aiohttp.ClientSession,
    ) -> None:
        """Class constructor."""
        self._url = f"{url}/{serial_number}"
        self._api_key = api_key
        self._session = session

    def update_interval(self) -> timedelta:
        """Return update interval for data coordinator."""
        return timedelta(seconds=FERNPORTAL_RATE_LIMIT_S)

    async def connect(self) -> None:
        """Not required for REST."""

    async def disconnect(self) -> None:
        """Not required for REST."""

    def _now(self) -> int:
        return int(datetime.now(UTC).timestamp())

    async def async_get_data(self) -> dict[str, int | float]:
        """Obtain fresh data."""
        headers = {"Authorization": f"Bearer {self._api_key}"}
        try:
            timeout = aiohttp.ClientTimeout(total=FERNPORTAL_TIMEOUT_S)
            async with self._session.get(
                self._url, timeout=timeout, headers=headers
            ) as response:
                response.raise_for_status()
                json_data: dict[str, Any] = await response.json()
        except aiohttp.ClientResponseError as err:
            _LOGGER.debug("API error: %s", err)
            if err.status == 429:  # noqa: PLR2004
                raise XthermaRestBusyError from err
            raise XthermaRestApiError(err.status) from err
        except asyncio.exceptions.TimeoutError as err:
            _LOGGER.debug("API request timed out")
            raise XthermaTimeoutError from err
        except Exception as err:
            _LOGGER.debug("Unknown API error %s", err)
            raise XthermaError from err
        return self._parse_payload(json_data)

    def _parse_payload(self, json_data: dict[str, Any]) -> dict[str, int | float]:
        """Convert telemetry and settings entries into a key/value mapping."""
        telemetry = json_data.get(KEY_TELEMETRY)
        settings = json_data.get(KEY_SETTINGS)
        if not isinstance(telemetry, list) or not isinstance(settings, list):
            _LOGGER.error("REST API response malformed")
            raise XthermaRestMalformedError
        result: dict[str, int | float] = {}
        for entry in itertools.chain(telemetry, settings):
            if (key := entry.get(KEY_ENTRY_KEY)) is None:
                continue
            if (raw_value := entry.get(KEY_ENTRY_VALUE)) is None:
                continue
            try:
                value = int(raw_value)
            except ValueError:
                # one unparsable entry must not abort the whole poll
                _LOGGER.warning(
                    'Skipping entry with unparsable value key="%s" value="%s"',
                    key,
                    raw_value,
                )
                continue
            binding = REST_BINDING_BY_API_KEY.get(key)
            factor = binding.quantity.factor if binding else None
            if factor:
                value = apply_factor(value, factor)
            result[key] = value
            _LOGGER.debug(
                'key="%s" raw="%s" value="%s" factor="%s"',
                key,
                raw_value,
                value,
                factor,
            )
        return result

    async def async_put_data(self, value: int | float, desc: EntityDescription) -> None:
        """Write data."""
        del value
        del desc
        _LOGGER.debug("Cannot write values using REST API connection")
        raise XthermaReadOnlyError

    def get_entity_descriptions(self) -> list[EntityDescription]:
        """Get all entity descriptions."""
        return ENTITY_DESCRIPTIONS
