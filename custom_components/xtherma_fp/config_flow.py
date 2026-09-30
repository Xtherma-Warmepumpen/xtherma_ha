"""Config flow for the xtherma integration."""

from __future__ import annotations

import logging
from typing import Any

import voluptuous as vol

try:
    from homeassistant.components.modbus import async_get_temporary_unit
except ImportError:
    # Importing the modbus component transitively imports its Modbus
    # backends (pymodbus / tmodbus), which Home Assistant only installs
    # when the modbus integration is present. This integration does not
    # depend on them (it also supports read-only REST), so the import is
    # guarded: the temporary-unit factory is left as None and re-imported
    # lazily when a Modbus connection is validated.
    async_get_temporary_unit = None

from homeassistant.config_entries import (
    ConfigEntry,
    ConfigFlow,
    ConfigFlowResult,
    OptionsFlow,
)
from homeassistant.const import (
    CONF_ADDRESS,
    CONF_API_KEY,
    CONF_HOST,
    CONF_NAME,
    CONF_PORT,
)
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers import aiohttp_client
from homeassistant.helpers.selector import (
    BooleanSelector,
    BooleanSelectorConfig,
    NumberSelector,
    NumberSelectorConfig,
    NumberSelectorMode,
    SelectSelector,
    SelectSelectorConfig,
    SelectSelectorMode,
)
from modbus_connection import ModbusTcpParams

from .const import (
    CONF_CONNECTION,
    CONF_CONNECTION_MODBUSTCP,
    CONF_CONNECTION_RESTAPI,
    CONF_DETECT_EMPTY_MODBUS_DATA,
    CONF_SERIAL_NUMBER,
    DOMAIN,
    FERNPORTAL_URL,
    VERSION,
)
from .pytherma.exceptions import XthermaNotConnectedError
from .xtherma_client_common import (
    XthermaError,
    XthermaRestBusyError,
    XthermaTimeoutError,
)
from .xtherma_client_modbus import XthermaClientModbus
from .xtherma_client_rest import XthermaClientRest

_LOGGER = logging.getLogger(__name__)

_DEF_MODBUS_PORT = 502
_DEF_MODBUS_ADDRESS = 1
_DEF_DETECT_EMPTY_MODBUS_DATA = True


CONNECTION_DATA = {
    vol.Required(
        CONF_SERIAL_NUMBER,
        msg="Serial Number (FP-XX-XXXXXX)",
    ): str,
    vol.Required(CONF_CONNECTION): SelectSelector(
        SelectSelectorConfig(
            options=[
                CONF_CONNECTION_RESTAPI,
                CONF_CONNECTION_MODBUSTCP,
            ],
            mode=SelectSelectorMode.LIST,
            translation_key=CONF_CONNECTION,
        ),
    ),
}


USER_DATA = {
    vol.Required(
        CONF_NAME,
        msg="Entry name",
    ): str,
    **CONNECTION_DATA,
}

BOOLEAN_SELECTOR = BooleanSelector(BooleanSelectorConfig())

OPTIONS_DATA = {
    vol.Optional(
        CONF_DETECT_EMPTY_MODBUS_DATA,
        default=_DEF_DETECT_EMPTY_MODBUS_DATA,
    ): BOOLEAN_SELECTOR,
}


CONNECTION_SCHEMA = vol.Schema(CONNECTION_DATA)

USER_SCHEMA = vol.Schema(USER_DATA)

REST_API_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_API_KEY, msg="API Key"): str,
    },
)

MODBUS_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_HOST, default=""): str,
        vol.Required(CONF_PORT, default=_DEF_MODBUS_PORT): vol.All(
            vol.Coerce(int),
            vol.Range(min=0, max=65535),
        ),
        vol.Required(CONF_ADDRESS, default=_DEF_MODBUS_ADDRESS): vol.All(
            vol.Coerce(int),
            NumberSelector(
                NumberSelectorConfig(
                    min=1,
                    max=255,
                    mode=NumberSelectorMode.BOX,
                ),
            ),
        ),
    },
)

OPTIONS_SCHEMA = vol.Schema(OPTIONS_DATA)


async def _validate_connection(
    data: dict[str, Any],
) -> dict[str, str]:
    _LOGGER.debug("validate connection settings")
    errors = {}

    serial_number = data.get(CONF_SERIAL_NUMBER)
    if serial_number is None or not serial_number.startswith("FP-"):
        errors["base"] = "bad_arguments"

    return errors


async def _validate_rest_api(
    hass: HomeAssistant,
    previous_data: dict[str, Any],
    data: dict[str, Any],
) -> dict[str, str]:
    _LOGGER.debug("validate REST-API settings")
    errors = {}

    api_key = data.get(CONF_API_KEY)
    if not api_key:
        errors["base"] = "bad_arguments"
        return errors

    serial_number = previous_data.get(CONF_SERIAL_NUMBER, "")

    try:
        session = aiohttp_client.async_get_clientsession(hass)
        client = XthermaClientRest(
            url=FERNPORTAL_URL,
            api_key=api_key,
            serial_number=serial_number,
            session=session,
        )
        await client.connect()
        await client.async_get_data()
        await client.disconnect()
    except XthermaRestBusyError:
        _LOGGER.debug("RateLimitError")
        errors["base"] = "rate_limit"
    except XthermaTimeoutError:
        _LOGGER.debug("TimeoutError")
        errors["base"] = "timeout"
    except XthermaError:
        _LOGGER.debug("GeneralError")
        errors["base"] = "cannot_connect"
    except Exception:  # noqa: BLE001
        _LOGGER.debug("Unexpected exception")
        errors["base"] = "unknown"

    if errors:
        _LOGGER.debug("validation unsuccessful (%s)", errors["base"])
    else:
        _LOGGER.debug("validation successful")

    return errors


async def _validate_modbus_tcp(
    hass: HomeAssistant,
    data: dict[str, Any],
) -> dict[str, str]:
    """Check values in data dict."""
    _LOGGER.debug("validate Modbus/TCP settings")
    errors = {}

    host = data.get(CONF_HOST)
    port = data.get(CONF_PORT)
    address = data.get(CONF_ADDRESS)
    if not (
        host and port and address and int(port) == port and int(address) == address
    ):
        errors["base"] = "bad_arguments"
        return errors

    params = ModbusTcpParams(host=host, port=int(port))
    if async_get_temporary_unit is not None:
        factory = async_get_temporary_unit
    else:
        # the modbus component (and its pymodbus requirement) may
        # have become available since this module was imported;
        # import under an alias so the module global is not shadowed
        try:
            from homeassistant.components.modbus import (  # noqa: PLC0415
                async_get_temporary_unit as _temp_unit_factory,
            )
        except ImportError:
            _LOGGER.debug("Modbus component unavailable; cannot validate")
            errors["base"] = "unknown"
            return errors
        factory = _temp_unit_factory

    try:
        # the temporary unit's connection is closed when the context exits;
        # a conflicting link setting on a shared endpoint raises
        # HomeAssistantError (caught below as a general error)
        async with factory(hass, params, int(address)) as unit:
            client = XthermaClientModbus(unit)
            await client.connect()
            await client.async_get_data()
            await client.disconnect()
    except XthermaTimeoutError:
        _LOGGER.debug("TimeoutError")
        errors["base"] = "timeout"
    except XthermaNotConnectedError:
        errors["base"] = "cannot_connect_modbus"
    except Exception as e:  # noqa: BLE001
        _LOGGER.debug("Unexpected exception %s", e)
        errors["base"] = "unknown"

    if errors:
        _LOGGER.debug("validation unsuccessful (%s)", errors["base"])
    else:
        _LOGGER.debug("validation successful")

    return errors


class XthermaConfigFlow(ConfigFlow, domain=DOMAIN):
    """Process config flow."""

    VERSION = VERSION
    MINOR_VERSION = 0

    @staticmethod
    @callback
    def async_get_options_flow(
        config_entry: ConfigEntry,
    ) -> XthermaOptionsFlowHandler:
        """Get the options flow for this handler."""
        return XthermaOptionsFlowHandler()

    _config_data: dict[str, str]
    _reconfigure_data: dict[str, str]

    async def async_step_user(
        self,
        user_input: dict[str, Any] | None = None,
    ) -> ConfigFlowResult:
        """Process user step."""
        self._config_data = {}
        errors: dict[str, str] = {}

        if user_input is not None:
            self._async_abort_entries_match(
                {CONF_SERIAL_NUMBER: user_input[CONF_SERIAL_NUMBER]}
            )

            errors |= await _validate_connection(user_input)
            if not errors:
                self._config_data.update(user_input)
                connection_type = user_input[CONF_CONNECTION]
                if connection_type == CONF_CONNECTION_RESTAPI:
                    return await self.async_step_rest_api()
                if connection_type == CONF_CONNECTION_MODBUSTCP:
                    return await self.async_step_modbus_tcp()

        return self.async_show_form(
            step_id="user", data_schema=USER_SCHEMA, errors=errors
        )

    async def async_step_rest_api(
        self,
        user_input: dict[str, Any] | None = None,
    ) -> ConfigFlowResult:
        """Process rest api config step."""
        errors: dict[str, str] = {}

        if user_input is not None:
            errors |= await _validate_rest_api(
                self.hass,
                self._config_data,
                user_input,
            )
            if not errors:
                self._config_data.update(user_input)
                return self.async_create_entry(
                    title=self._config_data[CONF_NAME],
                    data=self._config_data,
                )

        return self.async_show_form(
            step_id="rest_api",
            data_schema=REST_API_SCHEMA,
            errors=errors,
        )

    async def async_step_modbus_tcp(
        self,
        user_input: dict[str, Any] | None = None,
    ) -> ConfigFlowResult:
        """Process modbus tcp config step."""
        errors: dict[str, str] = {}

        if user_input is not None:
            self._async_abort_entries_match(
                {CONF_HOST: user_input[CONF_HOST], CONF_PORT: user_input[CONF_PORT]}
            )

            errors |= await _validate_modbus_tcp(
                self.hass,
                user_input,
            )
            if not errors:
                self._config_data.update(user_input)
                return self.async_create_entry(
                    title=self._config_data[CONF_NAME],
                    data=self._config_data,
                )

        return self.async_show_form(
            step_id="modbus_tcp",
            data_schema=MODBUS_SCHEMA,
            errors=errors,
        )

    async def async_step_reconfigure(
        self,
        user_input: dict[str, Any] | None = None,
    ) -> ConfigFlowResult:
        """Reconfigure an existing entry."""
        errors: dict[str, str] = {}
        reconfigure_entry = self._get_reconfigure_entry()
        self._reconfigure_data = reconfigure_entry.data.copy()

        if user_input is not None:
            self._async_abort_entries_match(
                {CONF_SERIAL_NUMBER: user_input[CONF_SERIAL_NUMBER]}
            )

            self._reconfigure_data.update(user_input)
            connection_type = user_input[CONF_CONNECTION]
            if connection_type == CONF_CONNECTION_RESTAPI:
                return await self.async_step_reconfigure_rest_api()
            if connection_type == CONF_CONNECTION_MODBUSTCP:
                return await self.async_step_reconfigure_modbus_tcp()

        return self.async_show_form(
            step_id="reconfigure",
            data_schema=self.add_suggested_values_to_schema(
                CONNECTION_SCHEMA, self._reconfigure_data
            ),
            errors=errors,
        )

    async def async_step_reconfigure_rest_api(
        self,
        user_input: dict[str, Any] | None = None,
    ) -> ConfigFlowResult:
        """Process rest api config step."""
        errors: dict[str, str] = {}

        if user_input is not None:
            errors |= await _validate_rest_api(
                self.hass, self._reconfigure_data, user_input
            )
            if not errors:
                self._reconfigure_data.update(user_input)
                return self.async_update_reload_and_abort(
                    self._get_reconfigure_entry(), data_updates=self._reconfigure_data
                )

        return self.async_show_form(
            step_id="reconfigure_rest_api",
            data_schema=self.add_suggested_values_to_schema(
                REST_API_SCHEMA, self._reconfigure_data
            ),
            errors=errors,
        )

    async def async_step_reconfigure_modbus_tcp(
        self,
        user_input: dict[str, Any] | None = None,
    ) -> ConfigFlowResult:
        """Process modbus tcp config step."""
        errors: dict[str, str] = {}
        if user_input is not None:
            self._async_abort_entries_match(
                {CONF_HOST: user_input[CONF_HOST], CONF_PORT: user_input[CONF_PORT]}
            )

            errors |= await _validate_modbus_tcp(self.hass, user_input)
            if not errors:
                self._reconfigure_data.update(user_input)
                return self.async_update_reload_and_abort(
                    self._get_reconfigure_entry(), data_updates=self._reconfigure_data
                )

        return self.async_show_form(
            step_id="reconfigure_modbus_tcp",
            data_schema=self.add_suggested_values_to_schema(
                MODBUS_SCHEMA, self._reconfigure_data
            ),
            errors=errors,
        )


class XthermaOptionsFlowHandler(OptionsFlow):
    """Handle an options flow for xtherma_fp."""

    async def async_step_init(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Manage the options."""
        if user_input is not None:
            return self.async_create_entry(data=user_input)

        return self.async_show_form(
            step_id="init",
            data_schema=self.add_suggested_values_to_schema(
                OPTIONS_SCHEMA, self.config_entry.options
            ),
        )
