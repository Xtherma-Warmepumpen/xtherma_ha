"""Per-quantity HA rendering for the Xtherma FP integration.

The ``pytherma`` library owns the *device semantics* of every quantity
(unit, scaling factor, enum options, min/max) and where each transport
reads/writes it (Modbus address + writability, REST wire key). This module owns
only the *Home Assistant rendering* of each quantity, resolved by quantity
``key``: which ``Xt*`` entity-description class to instantiate and the
presentation fields (device class, state class, icon, icon provider, number
mode, display precision, step).

``entity_descriptors.py`` composes the concrete ``Xt*`` entity descriptions by
cross-joining the library binding tables (``pytherma.bindings``) with the
per-key :data:`RENDERINGS` table defined here. The :data:`RENDERINGS` mapping
is curated by hand.
"""

from collections.abc import Callable
from dataclasses import dataclass

from homeassistant.components.binary_sensor import BinarySensorDeviceClass
from homeassistant.components.number import NumberDeviceClass, NumberMode
from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorStateClass,
)

from .pytherma.quantities import QUANTITY_BY_KEY


def _electric_switch_icon(state: bool | None) -> str:
    if state:
        return "mdi:electric-switch"
    return "mdi:electric-switch-closed"


def _pump_on_off_icon(state: bool | None) -> str:
    if state:
        return "mdi:pump"
    return "mdi:pump-off"


def _error_icon(state: bool | None) -> str:
    if state:
        return "mdi:check"
    return "mdi:alert"


def _error_1_icon(state: bool | None) -> str:
    if state:
        return "mdi:alert"
    return "mdi:check"


_ENUM_FALLBACK_ICON = "mdi:cogs"


def _enum_icon_provider(
    quantity_key: str, icons: tuple[str, ...]
) -> Callable[..., str]:
    """Build the dynamic icon provider for an enum quantity.

    ``icons`` is index-aligned with the library ``Quantity.options`` (the
    single source of truth for option names and order), so the option
    strings are never repeated here. Unknown or non-string states fall
    back to :data:`_ENUM_FALLBACK_ICON`.
    """
    options = QUANTITY_BY_KEY[quantity_key].options
    if options is None or len(options) != len(icons):
        msg = f"icon tuple does not match options of quantity {quantity_key!r}"
        raise ValueError(msg)
    icon_by_option = dict(zip(options, icons, strict=True))

    def _icon(state: object) -> str:
        if isinstance(state, str):
            return icon_by_option.get(state, _ENUM_FALLBACK_ICON)
        return _ENUM_FALLBACK_ICON

    return _icon


# index-aligned with Quantity.options of "002"/"mode"
_OPERATING_MODE_ICONS = (
    "mdi:power-standby",
    "mdi:heating-coil",
    "mdi:snowflake",
    "mdi:thermometer-water",
    "mdi:brightness-auto",
)

# SG-Ready operating states,
# see also https://www.waermepumpe.de/normen-technik/sg-ready/
# 0: Nicht aktiviert
# 1: Betriebszustand 2: Normalbetrieb (Klemme 0/0, anteilige Wärmespeicher-
#    füllung für die maximal zweistündige EVU-Sperre)
# 2: Betriebszustand 1: Sperre (Klemme 1/0, maximal zwei Stunden „harte“
#    Sperrzeit)
# 3: Betriebszustand 3: Temperaturen anheben (Klemme 0/1, verstärkter Betrieb
#    für Raumheizung und Warmwasserbereitung)
# 4: Betriebszustand 4: Anlaufbefehl (Klemme 1/1, Verdichter bzw. Verdichter
#    und elektrische Zusatzheizungen werden aktiv eingeschaltet)
# index-aligned with Quantity.options of "sg"; "815" uses the first four
_SGREADY_ICONS = (
    "mdi:cancel",  # Kein Eingriff
    "mdi:circle",  # Normalbetrieb
    "mdi:circle-double",  # Sperre
    "mdi:thermometer-plus",  # Temperaturen anheben
    "mdi:home-thermometer",  # Anlaufbefehl
)


_icon_electric_power = "mdi:lightning-bolt"
_icon_thermal_power = "mdi:heat-wave"
_icon_temperature = "mdi:thermometer"
_icon_temperature_water = "mdi:thermometer-water"
_icon_temperature_average = "mdi:thermometer-auto"
_icon_frequency = "mdi:sine-wave"
_icon_heating_in = "mdi:thermometer-chevron-up"
_icon_heating_out = "mdi:thermometer-chevron-down"
_icon_fan = "mdi:fan"
_icon_temperature_target_water = "mdi:thermometer-water"
_icon_temperature_target_heating = "mdi:home-thermometer-outline"
_icon_temperature_target_cooling = "mdi:snowflake-thermometer"
_icon_volume_rate = "mdi:waves-arrow-right"
_icon_performance = "mdi:poll"
_icon_pump = "mdi:pump"
_icon_hot_water = "mdi:water-boiler"
_icon_heating = "mdi:heating-coil"
_icon_cooling = "mdi:snowflake"


@dataclass(frozen=True)
class Render:
    """HA rendering for one quantity, resolved by quantity key."""

    #: which ``Xt*`` entity-description class to instantiate
    descriptor_type: str
    #: presentation device class (number / sensor / binary sensor)
    device_class: (
        NumberDeviceClass | SensorDeviceClass | BinarySensorDeviceClass | None
    ) = None
    #: sensor state class
    state_class: SensorStateClass | None = None
    #: static icon
    icon: str | None = None
    #: dynamic icon provider (receives the raw register value)
    icon_provider: Callable[..., str] | None = None
    #: number input mode
    mode: NumberMode | None = None
    #: sensor display precision
    suggested_display_precision: int | None = None
    #: number step
    native_step: int | None = None


RENDERINGS: dict[str, Render] = {
    "001": Render(descriptor_type="switch"),
    "002": Render(
        descriptor_type="select",
        icon_provider=_enum_icon_provider("002", _OPERATING_MODE_ICONS),
    ),
    "003": Render(descriptor_type="switch", icon="mdi:water-boiler"),
    "14a": Render(descriptor_type="binary"),
    "310": Render(descriptor_type="switch", icon="mdi:heating-coil"),
    "311": Render(
        descriptor_type="number",
        device_class=NumberDeviceClass.TEMPERATURE,
        icon="mdi:thermometer",
        mode=NumberMode.BOX,
        native_step=1,
    ),
    "312": Render(
        descriptor_type="number",
        device_class=NumberDeviceClass.TEMPERATURE,
        icon="mdi:thermometer",
        mode=NumberMode.BOX,
        native_step=1,
    ),
    "315": Render(
        descriptor_type="number",
        device_class=NumberDeviceClass.TEMPERATURE,
        icon="mdi:thermometer",
        mode=NumberMode.BOX,
        native_step=1,
    ),
    "316": Render(
        descriptor_type="number",
        device_class=NumberDeviceClass.TEMPERATURE,
        icon="mdi:thermometer",
        mode=NumberMode.BOX,
        native_step=1,
    ),
    "320": Render(
        descriptor_type="number",
        device_class=NumberDeviceClass.TEMPERATURE,
        icon="mdi:thermometer",
        mode=NumberMode.BOX,
        native_step=1,
    ),
    "350": Render(descriptor_type="switch", icon="mdi:snowflake"),
    "351": Render(
        descriptor_type="number",
        device_class=NumberDeviceClass.TEMPERATURE,
        icon="mdi:thermometer",
        mode=NumberMode.BOX,
        native_step=1,
    ),
    "352": Render(
        descriptor_type="number",
        device_class=NumberDeviceClass.TEMPERATURE,
        icon="mdi:thermometer",
        mode=NumberMode.BOX,
        native_step=1,
    ),
    "355": Render(
        descriptor_type="number",
        device_class=NumberDeviceClass.TEMPERATURE,
        icon="mdi:thermometer",
        mode=NumberMode.BOX,
        native_step=1,
    ),
    "356": Render(
        descriptor_type="number",
        device_class=NumberDeviceClass.TEMPERATURE,
        icon="mdi:thermometer",
        mode=NumberMode.BOX,
        native_step=1,
    ),
    "360": Render(
        descriptor_type="number",
        device_class=NumberDeviceClass.TEMPERATURE,
        icon="mdi:thermometer",
        mode=NumberMode.BOX,
        native_step=1,
    ),
    "410": Render(descriptor_type="switch", icon="mdi:heating-coil"),
    "411": Render(
        descriptor_type="number",
        device_class=NumberDeviceClass.TEMPERATURE,
        icon="mdi:thermometer",
        mode=NumberMode.BOX,
        native_step=1,
    ),
    "412": Render(
        descriptor_type="number",
        device_class=NumberDeviceClass.TEMPERATURE,
        icon="mdi:thermometer",
        mode=NumberMode.BOX,
        native_step=1,
    ),
    "415": Render(
        descriptor_type="number",
        device_class=NumberDeviceClass.TEMPERATURE,
        icon="mdi:thermometer",
        mode=NumberMode.BOX,
        native_step=1,
    ),
    "416": Render(
        descriptor_type="number",
        device_class=NumberDeviceClass.TEMPERATURE,
        icon="mdi:thermometer",
        mode=NumberMode.BOX,
        native_step=1,
    ),
    "420": Render(
        descriptor_type="number",
        device_class=NumberDeviceClass.TEMPERATURE,
        icon="mdi:thermometer",
        mode=NumberMode.BOX,
        native_step=1,
    ),
    "450": Render(descriptor_type="switch", icon="mdi:snowflake"),
    "451": Render(
        descriptor_type="number",
        device_class=NumberDeviceClass.TEMPERATURE,
        icon="mdi:thermometer",
        mode=NumberMode.BOX,
        native_step=1,
    ),
    "452": Render(
        descriptor_type="number",
        device_class=NumberDeviceClass.TEMPERATURE,
        icon="mdi:thermometer",
        mode=NumberMode.BOX,
        native_step=1,
    ),
    "455": Render(
        descriptor_type="number",
        device_class=NumberDeviceClass.TEMPERATURE,
        icon="mdi:thermometer",
        mode=NumberMode.BOX,
        native_step=1,
    ),
    "456": Render(
        descriptor_type="number",
        device_class=NumberDeviceClass.TEMPERATURE,
        icon="mdi:thermometer",
        mode=NumberMode.BOX,
        native_step=1,
    ),
    "460": Render(
        descriptor_type="number",
        device_class=NumberDeviceClass.TEMPERATURE,
        icon="mdi:thermometer",
        mode=NumberMode.BOX,
        native_step=1,
    ),
    "501": Render(
        descriptor_type="number",
        device_class=NumberDeviceClass.TEMPERATURE,
        icon="mdi:thermometer-water",
        mode=NumberMode.BOX,
        native_step=1,
    ),
    "522": Render(
        descriptor_type="number",
        device_class=NumberDeviceClass.TEMPERATURE,
        icon="mdi:thermometer-water",
        mode=NumberMode.BOX,
        native_step=1,
    ),
    "808": Render(descriptor_type="switch"),
    "811": Render(
        descriptor_type="number",
        device_class=NumberDeviceClass.TEMPERATURE,
        icon="mdi:home-thermometer-outline",
        mode=NumberMode.BOX,
        native_step=1,
    ),
    "812": Render(
        descriptor_type="number",
        device_class=NumberDeviceClass.TEMPERATURE,
        icon="mdi:thermometer-water",
        mode=NumberMode.BOX,
        native_step=1,
    ),
    "813": Render(
        descriptor_type="number",
        device_class=NumberDeviceClass.TEMPERATURE,
        icon="mdi:snowflake-thermometer",
        mode=NumberMode.BOX,
        native_step=1,
    ),
    "815": Render(
        descriptor_type="select",
        icon_provider=_enum_icon_provider("815", _SGREADY_ICONS[:4]),
    ),
    "c1_target": Render(
        descriptor_type="sensor",
        device_class=SensorDeviceClass.TEMPERATURE,
        state_class=SensorStateClass.MEASUREMENT,
        icon="mdi:snowflake-thermometer",
    ),
    "c2_target": Render(
        descriptor_type="sensor",
        device_class=SensorDeviceClass.TEMPERATURE,
        state_class=SensorStateClass.MEASUREMENT,
        icon="mdi:snowflake-thermometer",
    ),
    "c_target": Render(
        descriptor_type="sensor",
        device_class=SensorDeviceClass.TEMPERATURE,
        state_class=SensorStateClass.MEASUREMENT,
        icon="mdi:snowflake-thermometer",
    ),
    "controller_v": Render(descriptor_type="version", icon="mdi:information-outline"),
    "day_backup3_in_h": Render(
        descriptor_type="sensor",
        device_class=SensorDeviceClass.ENERGY,
        state_class=SensorStateClass.TOTAL_INCREASING,
        icon="mdi:lightning-bolt",
    ),
    "day_backup3_in_hw": Render(
        descriptor_type="sensor",
        device_class=SensorDeviceClass.ENERGY,
        state_class=SensorStateClass.TOTAL_INCREASING,
        icon="mdi:lightning-bolt",
    ),
    "day_backup3_out_h": Render(
        descriptor_type="sensor",
        device_class=SensorDeviceClass.ENERGY,
        state_class=SensorStateClass.TOTAL_INCREASING,
        icon="mdi:heat-wave",
    ),
    "day_backup3_out_hw": Render(
        descriptor_type="sensor",
        device_class=SensorDeviceClass.ENERGY,
        state_class=SensorStateClass.TOTAL_INCREASING,
        icon="mdi:heat-wave",
    ),
    "day_backup6_in_h": Render(
        descriptor_type="sensor",
        device_class=SensorDeviceClass.ENERGY,
        state_class=SensorStateClass.TOTAL_INCREASING,
        icon="mdi:lightning-bolt",
    ),
    "day_backup6_in_hw": Render(
        descriptor_type="sensor",
        device_class=SensorDeviceClass.ENERGY,
        state_class=SensorStateClass.TOTAL_INCREASING,
        icon="mdi:lightning-bolt",
    ),
    "day_backup6_out_h": Render(
        descriptor_type="sensor",
        device_class=SensorDeviceClass.ENERGY,
        state_class=SensorStateClass.TOTAL_INCREASING,
        icon="mdi:heat-wave",
    ),
    "day_backup6_out_hw": Render(
        descriptor_type="sensor",
        device_class=SensorDeviceClass.ENERGY,
        state_class=SensorStateClass.TOTAL_INCREASING,
        icon="mdi:heat-wave",
    ),
    "day_hp_in_c": Render(
        descriptor_type="sensor",
        device_class=SensorDeviceClass.ENERGY,
        state_class=SensorStateClass.TOTAL_INCREASING,
        icon="mdi:lightning-bolt",
    ),
    "day_hp_in_h": Render(
        descriptor_type="sensor",
        device_class=SensorDeviceClass.ENERGY,
        state_class=SensorStateClass.TOTAL_INCREASING,
        icon="mdi:lightning-bolt",
    ),
    "day_hp_in_hw": Render(
        descriptor_type="sensor",
        device_class=SensorDeviceClass.ENERGY,
        state_class=SensorStateClass.TOTAL_INCREASING,
        icon="mdi:lightning-bolt",
    ),
    "day_hp_out_c": Render(
        descriptor_type="sensor",
        device_class=SensorDeviceClass.ENERGY,
        state_class=SensorStateClass.TOTAL_INCREASING,
        icon="mdi:heat-wave",
    ),
    "day_hp_out_h": Render(
        descriptor_type="sensor",
        device_class=SensorDeviceClass.ENERGY,
        state_class=SensorStateClass.TOTAL_INCREASING,
        icon="mdi:heat-wave",
    ),
    "day_hp_out_hw": Render(
        descriptor_type="sensor",
        device_class=SensorDeviceClass.ENERGY,
        state_class=SensorStateClass.TOTAL_INCREASING,
        icon="mdi:heat-wave",
    ),
    "efficiency_hp": Render(
        descriptor_type="sensor",
        state_class=SensorStateClass.MEASUREMENT,
        icon="mdi:poll",
    ),
    "efficiency_total": Render(
        descriptor_type="sensor",
        state_class=SensorStateClass.MEASUREMENT,
        icon="mdi:poll",
    ),
    "error": Render(
        descriptor_type="binary",
        device_class=BinarySensorDeviceClass.RUNNING,
        icon_provider=_error_icon,
    ),
    "error_1": Render(
        descriptor_type="binary",
        device_class=BinarySensorDeviceClass.PROBLEM,
        icon_provider=_error_1_icon,
    ),
    "error_2": Render(
        descriptor_type="binary",
        device_class=BinarySensorDeviceClass.RUNNING,
        icon_provider=_error_icon,
    ),
    "evu": Render(descriptor_type="binary", icon_provider=_electric_switch_icon),
    "h1_target": Render(
        descriptor_type="sensor",
        device_class=SensorDeviceClass.TEMPERATURE,
        state_class=SensorStateClass.MEASUREMENT,
        icon="mdi:home-thermometer-outline",
    ),
    "h2_target": Render(
        descriptor_type="sensor",
        device_class=SensorDeviceClass.TEMPERATURE,
        state_class=SensorStateClass.MEASUREMENT,
        icon="mdi:home-thermometer-outline",
    ),
    "h_target": Render(
        descriptor_type="sensor",
        device_class=SensorDeviceClass.TEMPERATURE,
        state_class=SensorStateClass.MEASUREMENT,
        icon="mdi:home-thermometer-outline",
    ),
    "hw_target": Render(
        descriptor_type="sensor",
        device_class=SensorDeviceClass.TEMPERATURE,
        state_class=SensorStateClass.MEASUREMENT,
        icon="mdi:thermometer-water",
    ),
    "in_backup": Render(
        descriptor_type="sensor",
        device_class=SensorDeviceClass.POWER,
        state_class=SensorStateClass.MEASUREMENT,
        icon="mdi:lightning-bolt",
    ),
    "in_hp": Render(
        descriptor_type="sensor",
        device_class=SensorDeviceClass.POWER,
        state_class=SensorStateClass.MEASUREMENT,
        icon="mdi:lightning-bolt",
    ),
    "in_total": Render(
        descriptor_type="sensor",
        device_class=SensorDeviceClass.POWER,
        state_class=SensorStateClass.MEASUREMENT,
        icon="mdi:lightning-bolt",
    ),
    "ld1": Render(
        descriptor_type="sensor",
        state_class=SensorStateClass.MEASUREMENT,
        icon="mdi:fan",
        suggested_display_precision=0,
    ),
    "ld2": Render(
        descriptor_type="sensor",
        state_class=SensorStateClass.MEASUREMENT,
        icon="mdi:fan",
        suggested_display_precision=0,
    ),
    "mode": Render(
        descriptor_type="sensor",
        device_class=SensorDeviceClass.ENUM,
        icon_provider=_enum_icon_provider("mode", _OPERATING_MODE_ICONS),
    ),
    "out_backup": Render(
        descriptor_type="sensor",
        device_class=SensorDeviceClass.POWER,
        state_class=SensorStateClass.MEASUREMENT,
        icon="mdi:heat-wave",
    ),
    "out_hp": Render(
        descriptor_type="sensor",
        device_class=SensorDeviceClass.POWER,
        state_class=SensorStateClass.MEASUREMENT,
        icon="mdi:heat-wave",
    ),
    "out_total": Render(
        descriptor_type="sensor",
        device_class=SensorDeviceClass.POWER,
        state_class=SensorStateClass.MEASUREMENT,
        icon="mdi:heat-wave",
    ),
    "pk": Render(
        descriptor_type="binary",
        device_class=BinarySensorDeviceClass.RUNNING,
        icon_provider=_pump_on_off_icon,
    ),
    "pk1": Render(
        descriptor_type="binary",
        device_class=BinarySensorDeviceClass.RUNNING,
        icon_provider=_pump_on_off_icon,
    ),
    "pk2": Render(
        descriptor_type="binary",
        device_class=BinarySensorDeviceClass.RUNNING,
        icon_provider=_pump_on_off_icon,
    ),
    "pkl": Render(
        descriptor_type="sensor",
        state_class=SensorStateClass.MEASUREMENT,
        icon="mdi:pump",
    ),
    "pww": Render(
        descriptor_type="binary",
        device_class=BinarySensorDeviceClass.RUNNING,
        icon_provider=_pump_on_off_icon,
    ),
    "sg": Render(
        descriptor_type="sensor",
        device_class=SensorDeviceClass.ENUM,
        icon_provider=_enum_icon_provider("sg", _SGREADY_ICONS),
    ),
    "ta": Render(
        descriptor_type="sensor",
        device_class=SensorDeviceClass.TEMPERATURE,
        state_class=SensorStateClass.MEASUREMENT,
        icon="mdi:thermometer",
    ),
    "ta1": Render(
        descriptor_type="sensor",
        device_class=SensorDeviceClass.TEMPERATURE,
        state_class=SensorStateClass.MEASUREMENT,
        icon="mdi:thermometer-auto",
    ),
    "ta24": Render(
        descriptor_type="sensor",
        device_class=SensorDeviceClass.TEMPERATURE,
        state_class=SensorStateClass.MEASUREMENT,
        icon="mdi:thermometer-auto",
    ),
    "ta4": Render(
        descriptor_type="sensor",
        device_class=SensorDeviceClass.TEMPERATURE,
        state_class=SensorStateClass.MEASUREMENT,
        icon="mdi:thermometer-auto",
    ),
    "ta8": Render(
        descriptor_type="sensor",
        device_class=SensorDeviceClass.TEMPERATURE,
        state_class=SensorStateClass.MEASUREMENT,
        icon="mdi:thermometer-auto",
    ),
    "tk": Render(
        descriptor_type="sensor",
        device_class=SensorDeviceClass.TEMPERATURE,
        state_class=SensorStateClass.MEASUREMENT,
        icon="mdi:thermometer",
    ),
    "tk1": Render(
        descriptor_type="sensor",
        device_class=SensorDeviceClass.TEMPERATURE,
        state_class=SensorStateClass.MEASUREMENT,
        icon="mdi:thermometer",
    ),
    "tk2": Render(
        descriptor_type="sensor",
        device_class=SensorDeviceClass.TEMPERATURE,
        state_class=SensorStateClass.MEASUREMENT,
        icon="mdi:thermometer",
    ),
    "tr": Render(
        descriptor_type="sensor",
        device_class=SensorDeviceClass.TEMPERATURE,
        state_class=SensorStateClass.MEASUREMENT,
        icon="mdi:thermometer",
    ),
    "trl": Render(
        descriptor_type="sensor",
        device_class=SensorDeviceClass.TEMPERATURE,
        state_class=SensorStateClass.MEASUREMENT,
        icon="mdi:thermometer-chevron-down",
    ),
    "tvl": Render(
        descriptor_type="sensor",
        device_class=SensorDeviceClass.TEMPERATURE,
        state_class=SensorStateClass.MEASUREMENT,
        icon="mdi:thermometer-chevron-up",
    ),
    "tw": Render(
        descriptor_type="sensor",
        device_class=SensorDeviceClass.TEMPERATURE,
        state_class=SensorStateClass.MEASUREMENT,
        icon="mdi:thermometer-water",
    ),
    "v": Render(
        descriptor_type="sensor",
        device_class=SensorDeviceClass.VOLUME_FLOW_RATE,
        state_class=SensorStateClass.MEASUREMENT,
        icon="mdi:waves-arrow-right",
    ),
    "vf": Render(
        descriptor_type="sensor",
        device_class=SensorDeviceClass.FREQUENCY,
        state_class=SensorStateClass.MEASUREMENT,
        icon="mdi:sine-wave",
        suggested_display_precision=0,
    ),
    "x2400": Render(descriptor_type="switch"),
    "x2401": Render(
        descriptor_type="number",
        device_class=NumberDeviceClass.POWER,
        icon="mdi:lightning-bolt",
        mode=NumberMode.BOX,
        native_step=1,
    ),
}
