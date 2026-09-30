"""Constants for the Xtherma integration."""

DOMAIN = "xtherma_fp"

# current version of the config entry (single source; used by the config
# flow class body and async_migrate_entry)
VERSION = 1

MANUFACTURER = "Xtherma"

# configuration keys.
# CONF_API_KEY is already defined by homeassistant.const
CONF_CONNECTION = "connection"
CONF_SERIAL_NUMBER = "serial_number"

# connection variants
CONF_CONNECTION_RESTAPI = "rest_api"
CONF_CONNECTION_MODBUSTCP = "modbus_tcp"

# options keys
CONF_DETECT_EMPTY_MODBUS_DATA = "detect_empty_modbus_data"

FERNPORTAL_URL = "https://fernportal.xtherma.de/api/device"

# Fernportal is rate limited to 1500 requests per day, one per minute
FERNPORTAL_RATE_LIMIT_S = 61

# timeout in seconds before we stop trying to get a response
FERNPORTAL_TIMEOUT_S = 10

# keys in the response data

# element on top level
KEY_SERNO = "serial_number"
KEY_TELEMETRY = "telemetry"
KEY_SETTINGS = "settings"

# data entry keys in data and db_data
KEY_ENTRY_KEY = "key"
KEY_ENTRY_NAME = "name"
KEY_ENTRY_VALUE = "value"
KEY_ENTRY_MIN = "min"
KEY_ENTRY_MAX = "max"
KEY_ENTRY_MAPPING = "mapping"
KEY_ENTRY_UNIT = "unit"
KEY_ENTRY_OUTPUT_FACTOR = "output_factor"
KEY_ENTRY_INPUT_FACTOR = "input_factor"

# additional entity state attributes
EXTRA_STATE_ATTRIBUTE_PARAMETER = "parameter"
