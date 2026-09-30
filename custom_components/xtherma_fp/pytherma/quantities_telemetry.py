"""Telemetry quantities of the Xtherma FP (read-only area, addresses 100-193).

Transport-neutral rows: *where a transport reads or writes each value*
lives in the binding tables (``bindings.py``); row order preserves the
historical table order.
"""

from .data_model import Quantity

TELEMETRY_QUANTITIES: tuple[Quantity, ...] = (
    # --- general
    Quantity(key="controller_v", name="Controller version", factor="/100"),
    Quantity(
        key="mode",
        name="Current operating mode",
        options=("standby", "heating", "cooling", "water", "auto"),
        signed=False,
    ),
    Quantity(key="error", name="System ok", signed=False),
    Quantity(key="14a", name="§14a EnWG state", signed=False),
    Quantity(
        key="sg",
        name="SG-Ready Status",
        options=("off", "normal", "block", "raise", "start"),
        signed=False,
    ),
    Quantity(key="evu", name="EVU status", signed=False),
    # --- target values
    Quantity(
        key="h_target",
        name="Target heating operation",
        unit="°C",
        factor="/10",
    ),
    Quantity(
        key="h1_target",
        name="Target heating 1",
        unit="°C",
        factor="/10",
    ),
    Quantity(
        key="h2_target",
        name="Target heating 2",
        unit="°C",
        factor="/10",
    ),
    Quantity(
        key="c_target",
        name="Target cooling operation",
        unit="°C",
        factor="/10",
    ),
    Quantity(
        key="c1_target",
        name="Target cooling 1",
        unit="°C",
        factor="/10",
    ),
    Quantity(
        key="c2_target",
        name="Target cooling 2",
        unit="°C",
        factor="/10",
    ),
    Quantity(key="hw_target", name="Target hot water production (current)", unit="°C"),
    # --- temperature sensors
    Quantity(
        key="tk",
        name="[TK] Heating / Cooling temperature",
        unit="°C",
        factor="/10",
    ),
    Quantity(
        key="tk1",
        name="[TK1] Circuit 1 temperature",
        unit="°C",
        factor="/10",
    ),
    Quantity(
        key="tk2",
        name="[TK2] Circuit 2 temperature",
        unit="°C",
        factor="/10",
    ),
    Quantity(
        key="tw",
        name="[TW] Hot water temperature",
        unit="°C",
        factor="/10",
    ),
    Quantity(
        key="tr",
        name="[TR] Room temperature",
        unit="°C",
        factor="/10",
    ),
    Quantity(
        key="trl",
        name="[TRL] Return temperature",
        unit="°C",
        factor="/10",
    ),
    Quantity(
        key="tvl",
        name="[TVL] Flow temperature",
        unit="°C",
        factor="/10",
    ),
    # --- pumps and actors
    Quantity(
        key="v",
        name="[V] Volume flow",
        unit="L/min",
        factor="/10",
    ),
    Quantity(key="pk", name="[PK] Circulation pump enabled", signed=False),
    Quantity(
        key="pkl",
        name="[PKL] Circulation pump performance",
        unit="%",
        factor="/10",
    ),
    Quantity(key="pk1", name="[PK1] Circulation pump circuit 1 enabled", signed=False),
    Quantity(key="pk2", name="[PK2] Circulation pump circuit 2 enabled", signed=False),
    Quantity(key="pww", name="[PWW] Circulation pump hot water enabled", signed=False),
    Quantity(key="vf", name="Compressor frequency", unit="Hz"),
    Quantity(key="ld1", name="[LD1] Fan 1 speed", unit="rpm"),
    Quantity(key="ld2", name="[LD2] Fan 2 speed", unit="rpm"),
    # --- outside temperatures
    Quantity(
        key="ta",
        name="[TA] Outdoor temperature",
        unit="°C",
        factor="/10",
    ),
    Quantity(
        key="ta1",
        name="[TA1] Outdoor temperature average (1h)",
        unit="°C",
        factor="/10",
    ),
    Quantity(
        key="ta4",
        name="[TA4] Outdoor temperature average (4h)",
        unit="°C",
        factor="/10",
    ),
    Quantity(
        key="ta8",
        name="[TA8] Outdoor temperature average (8h)",
        unit="°C",
        factor="/10",
    ),
    Quantity(
        key="ta24",
        name="[TA24] Outdoor temperature average (24h)",
        unit="°C",
        factor="/10",
    ),
    # --- performance live
    Quantity(
        key="out_hp",
        name="Heat output heat pump (thermal)",
        unit="W",
        factor="*10",
    ),
    Quantity(
        key="in_hp",
        name="Power consumption heat pump (electric)",
        unit="W",
        factor="*10",
    ),
    Quantity(
        key="efficiency_hp",
        name="Coefficient of performance heat pump",
        factor="/100",
    ),
    Quantity(
        key="efficiency_total",
        name="Overall coefficient of performance (incl. auxiliary heating)",
        factor="/100",
    ),
    Quantity(
        key="out_backup",
        name="Heat output auxiliary/emergency heating (thermal)",
        unit="W",
        factor="*10",
    ),
    Quantity(
        key="in_backup",
        name="Power consumption auxiliary/emergency heating (electric)",
        unit="W",
        factor="*10",
    ),
    Quantity(
        key="out_total",
        name="Overall system heat output (thermal)",
        unit="W",
        factor="*10",
    ),
    Quantity(
        key="in_total",
        name="Overall system power consumption (electric)",
        unit="W",
        factor="*10",
    ),
    # --- per day energy
    Quantity(
        key="day_hp_out_h",
        name="Daily heating operation thermal output",
        unit="kWh",
        factor="/100",
    ),
    Quantity(
        key="day_hp_in_h",
        name="Daily heating operation electric power consumption",
        unit="kWh",
        factor="/100",
    ),
    Quantity(
        key="day_hp_out_c",
        name="Daily cooling operation thermal output",
        unit="kWh",
        factor="/100",
    ),
    Quantity(
        key="day_hp_in_c",
        name="Daily cooling operation electric power consumption",
        unit="kWh",
        factor="/100",
    ),
    Quantity(
        key="day_hp_out_hw",
        name="Daily hot water operation thermal output",
        unit="kWh",
        factor="/100",
    ),
    Quantity(
        key="day_hp_in_hw",
        name="Daily DHW operation electric power consumption",
        unit="kWh",
        factor="/100",
    ),
    Quantity(
        key="day_backup3_out_h",
        name="Daily heating auxiliary stage 1 (3 kW) thermal output",
        unit="kWh",
        factor="/100",
    ),
    Quantity(
        key="day_backup3_in_h",
        name="Daily heating auxiliary stage 1 (3 kW) electric power consumption",
        unit="kWh",
        factor="/100",
    ),
    Quantity(
        key="day_backup3_out_hw",
        name="Daily DHW auxiliary stage 1 (3 kW) thermal output",
        unit="kWh",
        factor="/100",
    ),
    Quantity(
        key="day_backup3_in_hw",
        name="Daily DHW auxiliary stage 1 (3 kW) electric power consumption",
        unit="kWh",
        factor="/100",
    ),
    Quantity(
        key="day_backup6_out_h",
        name="Daily heating auxiliary stage 2 (6 kW) thermal output",
        unit="kWh",
        factor="/100",
    ),
    Quantity(
        key="day_backup6_in_h",
        name="Daily heating auxiliary stage 2 (6 kW) electric power consumption",
        unit="kWh",
        factor="/100",
    ),
    Quantity(
        key="day_backup6_out_hw",
        name="Daily DHW auxiliary stage 2 (6 kW) thermal output",
        unit="kWh",
        factor="/100",
    ),
    Quantity(
        key="day_backup6_in_hw",
        name="Daily DHW auxiliary stage 2 (6 kW) electric power consumption",
        unit="kWh",
        factor="/100",
    ),
)
