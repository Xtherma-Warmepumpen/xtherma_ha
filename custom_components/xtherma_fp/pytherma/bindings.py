"""Transport bindings of the Xtherma FP heat pump.

A binding says *where a transport reads or writes a* :class:`Quantity`:
:class:`ModbusBinding` carries the holding-register address and writability,
:class:`RestBinding` the Fernportal REST wire key. Availability per transport
is binding existence, not absence of an address sentinel.

Both tables below are pure *reference* tables: they name quantities authored
in ``quantities_settings`` / ``quantities_telemetry`` and add only the
transport placement (address/writability, wire key). The REST table is the
single place that absorbs Fernportal wire-key renames via ``api_key``.
"""

from .data_model import ModbusBinding, RestBinding
from .quantities import QUANTITY_BY_KEY

__all__ = [
    "MODBUS_BINDINGS",
    "MODBUS_BINDING_BY_ADDRESS",
    "MODBUS_BINDING_BY_KEY",
    "REST_BINDINGS",
    "REST_BINDING_BY_API_KEY",
    "ModbusBinding",
    "RestBinding",
]

# --- Modbus bindings (address-ascending: settings area, then telemetry area)

#: Which quantities the Modbus transport binds:
#: ``(quantity key, holding-register address, writable)``, in table order.
_MODBUS_ROWS: tuple[tuple[str, int, bool], ...] = (
    # --- general
    ("001", 0, True),
    ("002", 1, True),
    ("003", 2, True),
    # --- heating curve 1
    ("310", 10, True),
    ("311", 11, True),
    ("312", 12, True),
    ("315", 13, True),
    ("316", 14, True),
    ("320", 15, True),
    # --- cooling curve 1
    ("350", 20, True),
    ("351", 21, True),
    ("352", 22, True),
    ("355", 23, True),
    ("356", 24, True),
    ("360", 25, True),
    # --- heating curve 2
    ("410", 30, True),
    ("411", 31, True),
    ("412", 32, True),
    ("415", 33, True),
    ("416", 34, True),
    ("420", 35, True),
    # --- cooling curve 2
    ("450", 40, True),
    ("451", 41, True),
    ("452", 42, True),
    ("455", 43, True),
    ("456", 44, True),
    ("460", 45, True),
    # --- hot water
    ("501", 50, True),
    ("522", 51, True),
    # --- network
    ("808", 60, True),
    ("811", 61, True),
    ("812", 62, True),
    ("813", 63, True),
    ("815", 64, True),
    # --- surplus
    ("x2400", 70, True),
    ("x2401", 71, True),
    # --- general
    ("controller_v", 100, False),
    ("mode", 101, False),
    ("error", 102, False),
    ("14a", 103, False),
    ("sg", 104, False),
    ("evu", 105, False),
    # --- target values
    ("h_target", 110, False),
    ("h1_target", 111, False),
    ("h2_target", 112, False),
    ("c_target", 113, False),
    ("c1_target", 114, False),
    ("c2_target", 115, False),
    ("hw_target", 116, False),
    # --- temperature sensors
    ("tk", 120, False),
    ("tk1", 121, False),
    ("tk2", 122, False),
    ("tw", 123, False),
    ("tr", 124, False),
    ("trl", 125, False),
    ("tvl", 126, False),
    # --- pumps and actors
    ("v", 130, False),
    ("pk", 131, False),
    ("pkl", 132, False),
    ("pk1", 133, False),
    ("pk2", 134, False),
    ("pww", 135, False),
    ("vf", 136, False),
    ("ld1", 137, False),
    ("ld2", 138, False),
    # --- outside temperatures
    ("ta", 140, False),
    ("ta1", 141, False),
    ("ta4", 142, False),
    ("ta8", 143, False),
    ("ta24", 144, False),
    # --- performance live
    ("out_hp", 170, False),
    ("in_hp", 171, False),
    ("efficiency_hp", 172, False),
    ("efficiency_total", 173, False),
    ("out_backup", 174, False),
    ("in_backup", 175, False),
    ("out_total", 176, False),
    ("in_total", 177, False),
    # --- per day energy
    ("day_hp_out_h", 180, False),
    ("day_hp_in_h", 181, False),
    ("day_hp_out_c", 182, False),
    ("day_hp_in_c", 183, False),
    ("day_hp_out_hw", 184, False),
    ("day_hp_in_hw", 185, False),
    ("day_backup3_out_h", 186, False),
    ("day_backup3_in_h", 187, False),
    ("day_backup3_out_hw", 188, False),
    ("day_backup3_in_hw", 189, False),
    ("day_backup6_out_h", 190, False),
    ("day_backup6_in_h", 191, False),
    ("day_backup6_out_hw", 192, False),
    ("day_backup6_in_hw", 193, False),
)

MODBUS_BINDINGS: tuple[ModbusBinding, ...] = tuple(
    ModbusBinding(quantity=QUANTITY_BY_KEY[key], address=address, writable=writable)
    for key, address, writable in _MODBUS_ROWS
)

MODBUS_BINDING_BY_KEY: dict[str, ModbusBinding] = {
    binding.quantity.key: binding for binding in MODBUS_BINDINGS
}

MODBUS_BINDING_BY_ADDRESS: dict[int, ModbusBinding] = {
    binding.address: binding for binding in MODBUS_BINDINGS
}

# --- REST bindings

#: Keys of the quantities the Fernportal REST API currently serves, in
#: entity-creation order; wire-key renames are absorbed via
#: :attr:`RestBinding.api_key` without touching the quantity.
_REST_QUANTITY_KEYS: tuple[str, ...] = (
    "001",
    "002",
    "003",
    "310",
    "311",
    "312",
    "315",
    "316",
    "320",
    "350",
    "351",
    "352",
    "355",
    "356",
    "360",
    "410",
    "411",
    "412",
    "415",
    "416",
    "420",
    "450",
    "451",
    "452",
    "455",
    "456",
    "460",
    "501",
    "522",
    "811",
    "812",
    "813",
    "controller_v",
    "mode",
    "error_2",
    "error_1",
    "14a",
    "sg",
    "evu",
    "h_target",
    "h1_target",
    "h2_target",
    "c_target",
    "c1_target",
    "c2_target",
    "hw_target",
    "tk",
    "tk1",
    "tk2",
    "tw",
    "tr",
    "trl",
    "tvl",
    "v",
    "pk",
    "pkl",
    "pk1",
    "pk2",
    "pww",
    "vf",
    "ld1",
    "ld2",
    "ta",
    "ta1",
    "ta4",
    "ta8",
    "ta24",
    "out_hp",
    "in_hp",
    "efficiency_hp",
    "efficiency_total",
    "out_backup",
    "in_backup",
    "day_hp_out_h",
    "day_hp_in_h",
    "day_hp_out_c",
    "day_hp_in_c",
    "day_hp_out_hw",
    "day_hp_in_hw",
    "day_backup3_out_h",
    "day_backup3_in_h",
    "day_backup3_out_hw",
    "day_backup6_in_hw",
    "day_backup6_out_h",
    "day_backup6_in_h",
    "day_backup6_out_hw",
    "day_backup3_in_hw",
)

REST_BINDINGS: tuple[RestBinding, ...] = tuple(
    RestBinding(quantity=QUANTITY_BY_KEY[key]) for key in _REST_QUANTITY_KEYS
)

#: REST bindings indexed by their *resolved* wire key.
REST_BINDING_BY_API_KEY: dict[str, RestBinding] = {
    binding.resolved_api_key: binding for binding in REST_BINDINGS
}
