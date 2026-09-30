"""HA-free record data model for the Xtherma FP.

This leaf module holds the record shapes only; the tables (rows) are authored
in ``quantities_settings`` / ``quantities_telemetry`` (quantities) and
``bindings`` (transport placement) and assembled in :mod:`quantities` /
:mod:`bindings`.

* :class:`Quantity` — *what a value means* (transport-neutral semantics).
* :class:`ModbusBinding` / :class:`RestBinding` — *where a transport reads or
  writes that value*; availability per transport is binding existence.

Rendering concerns (HA device class, state class, icon, number mode)
intentionally live outside this library and are resolved by ``key`` in the
consuming application.
"""

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class Quantity:
    """Transport-neutral device semantics for a single measured/settable value."""

    #: unique quantity key (matches the integration's entity key)
    key: str
    #: quantity name
    name: str
    #: unit of measurement (e.g. ``"°C"``)
    unit: str | None = None
    #: scaling factor string (e.g. ``"/10"``), see :mod:`scaling`
    factor: str | None = None
    #: enum options if the quantity holds an enumerated state
    options: tuple[str, ...] | None = None
    #: minimum value of the scaled quantity value
    minimum: int | None = None
    #: maximum value of the scaled quantity value
    maximum: int | None = None
    #: whether the raw value uses two's complement for negative numbers
    signed: bool = True


@dataclass(frozen=True, slots=True)
class ModbusBinding:
    """Where the Modbus transport reads/writes one :class:`Quantity`."""

    #: the transport-neutral value this binding exposes
    quantity: Quantity
    #: absolute holding register address
    address: int
    #: whether the address can be written
    writable: bool = False


@dataclass(frozen=True, slots=True)
class RestBinding:
    """Where the Fernportal REST transport reads one :class:`Quantity`."""

    #: the transport-neutral value this binding exposes
    quantity: Quantity
    #: REST wire key, or ``None`` when it equals the quantity key
    api_key: str | None = None

    @property
    def resolved_api_key(self) -> str:
        """REST wire key actually used on the wire."""
        return self.api_key if self.api_key is not None else self.quantity.key
