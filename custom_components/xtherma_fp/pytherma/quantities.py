"""Transport-neutral quantities of the Xtherma FP heat pump.

A :class:`Quantity` captures *what a value means* (name, unit, scaling,
range, enumeration). *Where a transport reads or writes that value* is a
separate concern held by the binding tables in :mod:`bindings` and is
deliberately absent here.

Rows are authored in ``quantities_settings`` / ``quantities_telemetry``;
quantities without any Modbus binding (REST-only) are authored as plain
rows below.
"""

from .data_model import Quantity
from .quantities_settings import SETTINGS_QUANTITIES
from .quantities_telemetry import TELEMETRY_QUANTITIES

__all__ = ["QUANTITIES", "QUANTITY_BY_KEY", "Quantity"]

#: Quantities without a Modbus binding (Fernportal REST only).
_REST_ONLY_QUANTITIES: tuple[Quantity, ...] = (
    Quantity(key="error_1", name="System fault", signed=False),
    Quantity(key="error_2", name="System ok", signed=False),
)

#: All quantities, in table order (settings, telemetry, REST-only).
QUANTITIES: tuple[Quantity, ...] = (
    *SETTINGS_QUANTITIES,
    *TELEMETRY_QUANTITIES,
    *_REST_ONLY_QUANTITIES,
)

#: Quick lookup of a :class:`Quantity` by its key.
QUANTITY_BY_KEY: dict[str, Quantity] = {qty.key: qty for qty in QUANTITIES}
