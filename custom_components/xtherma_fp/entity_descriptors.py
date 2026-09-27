"""Entity description composition.

The ``pytherma`` library owns the *device semantics* (quantities) and the
*transport bindings* of every value. This module composes concrete ``Xt*``
entity descriptions by cross-joining the binding tables with the per-key
rendering table in :mod:`entity_mapping`. The integration owns only HA
*rendering* (device class, state class, icon, number mode, display precision,
step).
"""

from collections.abc import Callable
from dataclasses import dataclass
from datetime import date, datetime
from decimal import Decimal
from typing import cast

from homeassistant.components.binary_sensor import (
    BinarySensorDeviceClass,
    BinarySensorEntityDescription,
)
from homeassistant.components.number import (
    NumberDeviceClass,
    NumberEntityDescription,
)
from homeassistant.components.select import (
    SelectEntityDescription,
)
from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntityDescription,
)
from homeassistant.components.switch import (
    SwitchEntityDescription,
)
from homeassistant.const import (
    PERCENTAGE,
    REVOLUTIONS_PER_MINUTE,
    UnitOfEnergy,
    UnitOfFrequency,
    UnitOfPower,
    UnitOfTemperature,
    UnitOfVolumeFlowRate,
)
from homeassistant.helpers.entity import EntityDescription
from homeassistant.helpers.typing import StateType

from .entity_mapping import RENDERINGS, Render
from .pytherma.bindings import MODBUS_BINDINGS, REST_BINDINGS
from .pytherma.data_model import Quantity


@dataclass(kw_only=True, frozen=True)
class XtBinaryEntityDescription:
    """A switchable entity."""

    icon_provider: Callable[[bool | None], str] | None = None


@dataclass(kw_only=True, frozen=True)
class XtSwitchEntityDescription(
    SwitchEntityDescription,
    XtBinaryEntityDescription,
):
    """A switchable input entity."""


@dataclass(kw_only=True, frozen=True)
class XtBinarySensorEntityDescription(
    BinarySensorEntityDescription,
    XtBinaryEntityDescription,
):
    """A binary value sensor."""


@dataclass(kw_only=True, frozen=True)
class XtNumericEntityDescription:
    """A numeric value entity."""

    factor: str | None = None
    icon_provider: Callable[[StateType | date | datetime | Decimal], str] | None = None


@dataclass(kw_only=True, frozen=True)
class XtSelectEntityDescription(SelectEntityDescription):
    """A selectable state input entity."""

    icon_provider: Callable[[str | None], str] | None = None


@dataclass(kw_only=True, frozen=True)
class XtNumberEntityDescription(NumberEntityDescription, XtNumericEntityDescription):
    """A numeric input entity."""


@dataclass(kw_only=True, frozen=True)
class XtSensorEntityDescription(SensorEntityDescription, XtNumericEntityDescription):
    """A numeric value sensor."""


@dataclass(kw_only=True, frozen=True)
class XtVersionSensorEntityDescription(XtSensorEntityDescription):
    """A version value sensor."""


# Map library unit strings to HA unit constants/enums so that the
# snapshot (which serialises via ``repr``) stays byte-identical.
_UNIT_MAP: dict[
    str,
    str
    | UnitOfTemperature
    | UnitOfFrequency
    | UnitOfEnergy
    | UnitOfPower
    | UnitOfVolumeFlowRate,
] = {
    "°C": UnitOfTemperature.CELSIUS,
    "K": UnitOfTemperature.KELVIN,
    "Hz": UnitOfFrequency.HERTZ,
    "L/min": UnitOfVolumeFlowRate.LITERS_PER_MINUTE,
    "W": UnitOfPower.WATT,
    "kWh": UnitOfEnergy.KILO_WATT_HOUR,
    "rpm": REVOLUTIONS_PER_MINUTE,
    "%": PERCENTAGE,
}


def _map_unit(quantity: Quantity) -> str | None:
    """Map a library unit string to its HA constant/enum value."""
    if quantity.unit is None:
        return None
    mapped = _UNIT_MAP.get(quantity.unit)
    if mapped is None:
        msg = f"Unmapped unit {quantity.unit!r} for quantity {quantity.key!r}"
        raise ValueError(msg)
    return mapped


def _compose(quantity: Quantity, render: Render) -> EntityDescription:
    """Compose an ``Xt*`` entity description from a quantity and a rendering."""
    unit = _map_unit(quantity)
    options = list(quantity.options) if quantity.options else None

    if render.descriptor_type == "switch":
        return XtSwitchEntityDescription(
            key=quantity.key,
            icon=render.icon,
            icon_provider=render.icon_provider,
        )

    if render.descriptor_type == "select":
        return XtSelectEntityDescription(
            key=quantity.key,
            options=options,
            icon_provider=render.icon_provider,
        )

    if render.descriptor_type == "binary":
        return XtBinarySensorEntityDescription(
            key=quantity.key,
            device_class=cast("BinarySensorDeviceClass | None", render.device_class),
            icon_provider=render.icon_provider,
        )

    if render.descriptor_type == "number":
        return XtNumberEntityDescription(
            key=quantity.key,
            native_unit_of_measurement=unit,
            device_class=cast("NumberDeviceClass | None", render.device_class),
            icon=render.icon,
            mode=render.mode,
            native_min_value=quantity.minimum,
            native_max_value=quantity.maximum,
            native_step=render.native_step,
            factor=quantity.factor,
            icon_provider=render.icon_provider,
        )

    if render.descriptor_type == "version":
        return XtVersionSensorEntityDescription(
            key=quantity.key,
            icon=render.icon,
            factor=quantity.factor,
        )

    # all remaining descriptor types are sensors
    return XtSensorEntityDescription(
        key=quantity.key,
        native_unit_of_measurement=unit,
        device_class=cast("SensorDeviceClass | None", render.device_class),
        state_class=render.state_class,
        icon=render.icon,
        options=options,
        suggested_display_precision=render.suggested_display_precision,
        factor=quantity.factor,
        icon_provider=render.icon_provider,
    )


# Flat list of all Modbus entity descriptions, ordered by register address
# (``MODBUS_BINDINGS`` preserves that order).
MODBUS_DESCRIPTORS: list[EntityDescription] = [
    _compose(binding.quantity, RENDERINGS[binding.quantity.key])
    for binding in MODBUS_BINDINGS
]

# Entity descriptions for the values the Fernportal REST API serves, one per
# ``REST_BINDINGS`` row (creation order fixes entity order for stable diffs;
# membership is the contract).
ENTITY_DESCRIPTIONS: list[EntityDescription] = [
    _compose(binding.quantity, RENDERINGS[binding.quantity.key])
    for binding in REST_BINDINGS
]
