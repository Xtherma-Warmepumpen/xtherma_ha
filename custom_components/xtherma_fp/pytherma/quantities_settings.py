"""Settings quantities of the Xtherma FP (set-value area, addresses 0-71).

Transport-neutral rows: *where a transport reads or writes each value*
lives in the binding tables (``bindings.py``); row order preserves the
historical table order.
"""

from .data_model import Quantity

SETTINGS_QUANTITIES: tuple[Quantity, ...] = (
    # --- general
    Quantity(key="001", name="Heat pump turned on", signed=False),
    Quantity(
        key="002",
        name="Operating mode",
        options=("standby", "heating", "cooling", "water", "auto"),
        signed=False,
    ),
    Quantity(key="003", name="Hot water now", signed=False),
    # --- heating curve 1
    Quantity(key="310", name="Heating curve 1 enabled", signed=False),
    Quantity(
        key="311",
        name="Heating curve 1 outside temperature low (P1)",
        unit="°C",
        minimum=-20,
        maximum=25,
    ),
    Quantity(
        key="312",
        name="Heating curve 1 outside temperature high (P2)",
        unit="°C",
        minimum=-9,
        maximum=25,
    ),
    Quantity(
        key="315",
        name="Heating curve 1 heating temperature low (P1)",
        unit="°C",
        minimum=20,
        maximum=75,
    ),
    Quantity(
        key="316",
        name="Heating curve 1 heating temperature high (P2)",
        unit="°C",
        minimum=20,
        maximum=75,
    ),
    Quantity(
        key="320",
        name="Heating curve 1 constant heating temperature",
        unit="°C",
        minimum=20,
        maximum=75,
    ),
    # --- cooling curve 1
    Quantity(key="350", name="Cooling curve 1 active", signed=False),
    Quantity(
        key="351",
        name="Cooling curve 1 outside temperature low (P1)",
        unit="°C",
        minimum=16,
        maximum=32,
    ),
    Quantity(
        key="352",
        name="Cooling curve 1 outside temperature high (P2)",
        unit="°C",
        minimum=29,
        maximum=45,
    ),
    Quantity(
        key="355",
        name="Cooling curve 1 cooling temperature low (P1)",
        unit="°C",
        minimum=7,
        maximum=30,
    ),
    Quantity(
        key="356",
        name="Cooling curve 1 cooling temperature high (P2)",
        unit="°C",
        minimum=7,
        maximum=30,
    ),
    Quantity(
        key="360",
        name="Cooling curve 1 constant cooling temperature",
        unit="°C",
        minimum=7,
        maximum=30,
    ),
    # --- heating curve 2
    Quantity(key="410", name="Heating curve 2 enabled", signed=False),
    Quantity(
        key="411",
        name="Heating curve 2 outside temperature low (P1)",
        unit="°C",
        minimum=-20,
        maximum=25,
    ),
    Quantity(
        key="412",
        name="Heating curve 2 outside temperature high (P2)",
        unit="°C",
        minimum=-9,
        maximum=25,
    ),
    Quantity(
        key="415",
        name="Heating curve 2 heating temperature low (P1)",
        unit="°C",
        minimum=20,
        maximum=75,
    ),
    Quantity(
        key="416",
        name="Heating curve 2 heating temperature high (P2)",
        unit="°C",
        minimum=20,
        maximum=75,
    ),
    Quantity(
        key="420",
        name="Heating curve 2 constant heating temperature",
        unit="°C",
        minimum=20,
        maximum=75,
    ),
    # --- cooling curve 2
    Quantity(key="450", name="Cooling curve 2 active", signed=False),
    Quantity(
        key="451",
        name="Cooling curve 2 outside temperature low (P1)",
        unit="°C",
        minimum=16,
        maximum=32,
    ),
    Quantity(
        key="452",
        name="Cooling curve 2 outside temperature high (P2)",
        unit="°C",
        minimum=29,
        maximum=45,
    ),
    Quantity(
        key="455",
        name="Cooling curve 2 cooling temperature low (P1)",
        unit="°C",
        minimum=7,
        maximum=30,
    ),
    Quantity(
        key="456",
        name="Cooling curve 2 cooling temperature high (P2)",
        unit="°C",
        minimum=7,
        maximum=30,
    ),
    Quantity(
        key="460",
        name="Cooling curve 2 constant cooling temperature",
        unit="°C",
        minimum=7,
        maximum=30,
    ),
    # --- hot water
    Quantity(
        key="501",
        name="Target warm water production",
        unit="°C",
        minimum=25,
        maximum=75,
    ),
    Quantity(
        key="522",
        name="Target keep water warm",
        unit="°C",
        minimum=30,
        maximum=55,
    ),
    # --- network
    Quantity(key="808", name="§14a EnWG request", signed=False),
    Quantity(
        key="811",
        name="SG-Ready raise heating temperature by",
        unit="K",
        minimum=0,
        maximum=30,
    ),
    Quantity(
        key="812",
        name="SG-Ready raise warm water temperature by",
        unit="K",
        minimum=0,
        maximum=30,
    ),
    Quantity(
        key="813",
        name="SG-Ready lower cooling temperature by",
        unit="K",
        minimum=0,
        maximum=30,
    ),
    Quantity(
        key="815",
        name="SG-Ready request",
        options=("off", "normal", "block", "raise"),
        signed=False,
    ),
    # --- surplus
    Quantity(key="x2400", name="Surplus managment enable", signed=False),
    Quantity(
        key="x2401",
        name="Available surplus in watts",
        unit="W",
        minimum=0,
        maximum=65000,
    ),
)
