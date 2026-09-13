"""Sensor descriptions."""

from collections.abc import Callable
from dataclasses import dataclass
from datetime import date, datetime
from decimal import Decimal

from homeassistant.components.binary_sensor import (
    BinarySensorDeviceClass,
    BinarySensorEntityDescription,
)
from homeassistant.components.number import (
    NumberDeviceClass,
    NumberEntityDescription,
    NumberMode,
)
from homeassistant.components.select import (
    SelectEntityDescription,
)
from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntityDescription,
    SensorStateClass,
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


_mode_options = ["standby", "heating", "cooling", "water", "auto"]
_mode_icon_map = {
    0: "mdi:power-standby",
    1: "mdi:heating-coil",
    2: "mdi:snowflake",
    3: "mdi:thermometer-water",
    4: "mdi:brightness-auto",
}


def _mode_icon(state: StateType | date | datetime | Decimal) -> str:
    if isinstance(state, str):
        try:
            index = _mode_options.index(state)
            return _mode_icon_map.get(index, "mdi:cogs")
        except ValueError:
            pass
    return "mdi:cogs"


_002_options = ["standby", "heating", "cooling", "water", "auto"]
_002_icon_map = {
    0: "mdi:power-standby",
    1: "mdi:heating-coil",
    2: "mdi:snowflake",
    3: "mdi:thermometer-water",
    4: "mdi:brightness-auto",
}


def _002_icon(state: StateType) -> str:
    if isinstance(state, str):
        try:
            index = _002_options.index(state)
            return _002_icon_map.get(index, "mdi:cogs")
        except ValueError:
            pass
    return "mdi:cogs"


"""
see also https://www.waermepumpe.de/normen-technik/sg-ready/
0: Nicht aktiviert

1: Betriebszustand 2: Normalbetrieb
   Klemme 0/0
   Anteilige Wärmespeicher-Füllung für die maximal zweistündige EVU-Sperre

2: Betriebszustand 1: Sperre
   Klemme 1/0
   Maximal zwei Stunden „harte“ Sperrzeit

3: Betriebszustand 3: Temperaturen anheben
   Klemme 0/1
   Verstärkter Betrieb für Raumheizung und Warmwasserbereitung

4: Betriebszustand 4: Anlaufbefehl
   Klemme 1/1
   Variante 1: Die Wärmepumpe (Verdichter) wird aktiv eingeschaltet.
   Variante 2: Die Wärmepumpe (Verdichter und elektrische Zusatzheizungen) wird aktiv
               eingeschaltet, optional: höhere Temperatur in den Wärmespeichern
"""

_sgready_options = ["off", "normal", "block", "raise", "start"]
_sgready_icon_map = {
    0: "mdi:cancel",  # "Kein Eingriff
    1: "mdi:circle",  # Normalbetrieb
    2: "mdi:circle-double",  # Sperre
    3: "mdi:thermometer-plus",  # Temperaturen anheben
    4: "mdi:home-thermometer",  # Anlaufbefehl
}


def _sgready_icon(state: StateType | date | datetime | Decimal) -> str:
    if isinstance(state, str):
        try:
            index = _sgready_options.index(state)
            return _sgready_icon_map.get(index, "mdi:cogs")
        except ValueError:
            pass
    return "mdi:cogs"


_815_options = ["off", "normal", "block", "raise"]
_815_icon_map = {
    0: "mdi:cancel",  # "Kein Eingriff
    1: "mdi:circle",  # Normalbetrieb
    2: "mdi:circle-double",  # Sperre
    3: "mdi:thermometer-plus",  # Temperaturen anheben
}


def _815_icon(state: StateType) -> str:
    if isinstance(state, str):
        try:
            index = _815_options.index(state)
            return _815_icon_map.get(index, "mdi:cogs")
        except ValueError:
            pass
    return "mdi:cogs"


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

#
# Settings
#
_sensor_001 = XtSwitchEntityDescription(
    key="001",
)
_sensor_002 = XtSelectEntityDescription(
    key="002",
    options=_002_options,
    icon_provider=_002_icon,
)
_sensor_003 = XtSwitchEntityDescription(
    key="003",
    icon=_icon_hot_water,
)
_sensor_310 = XtSwitchEntityDescription(
    key="310",
    icon=_icon_heating,
)
_sensor_311 = XtNumberEntityDescription(
    key="311",
    native_unit_of_measurement=UnitOfTemperature.CELSIUS,
    device_class=NumberDeviceClass.TEMPERATURE,
    icon=_icon_temperature,
    mode=NumberMode.BOX,
    native_min_value=-20,
    native_max_value=25,
    native_step=1,
)
_sensor_312 = XtNumberEntityDescription(
    key="312",
    native_unit_of_measurement=UnitOfTemperature.CELSIUS,
    device_class=NumberDeviceClass.TEMPERATURE,
    icon=_icon_temperature,
    mode=NumberMode.BOX,
    native_min_value=-9,
    native_max_value=25,
    native_step=1,
)
_sensor_315 = XtNumberEntityDescription(
    key="315",
    native_unit_of_measurement=UnitOfTemperature.CELSIUS,
    device_class=NumberDeviceClass.TEMPERATURE,
    icon=_icon_temperature,
    mode=NumberMode.BOX,
    native_min_value=20,
    native_max_value=75,
    native_step=1,
)
_sensor_316 = XtNumberEntityDescription(
    key="316",
    native_unit_of_measurement=UnitOfTemperature.CELSIUS,
    device_class=NumberDeviceClass.TEMPERATURE,
    icon=_icon_temperature,
    mode=NumberMode.BOX,
    native_min_value=20,
    native_max_value=75,
    native_step=1,
)
_sensor_320 = XtNumberEntityDescription(
    key="320",
    native_unit_of_measurement=UnitOfTemperature.CELSIUS,
    device_class=NumberDeviceClass.TEMPERATURE,
    mode=NumberMode.BOX,
    native_min_value=20,
    native_max_value=75,
    native_step=1,
    icon=_icon_temperature,
)
_sensor_350 = XtSwitchEntityDescription(
    key="350",
    icon=_icon_cooling,
)
_sensor_351 = XtNumberEntityDescription(
    key="351",
    native_unit_of_measurement=UnitOfTemperature.CELSIUS,
    device_class=NumberDeviceClass.TEMPERATURE,
    icon=_icon_temperature,
    mode=NumberMode.BOX,
    native_min_value=16,
    native_max_value=32,
    native_step=1,
)
_sensor_352 = XtNumberEntityDescription(
    key="352",
    native_unit_of_measurement=UnitOfTemperature.CELSIUS,
    device_class=NumberDeviceClass.TEMPERATURE,
    icon=_icon_temperature,
    mode=NumberMode.BOX,
    native_min_value=29,
    native_max_value=45,
    native_step=1,
)
_sensor_355 = XtNumberEntityDescription(
    key="355",
    native_unit_of_measurement=UnitOfTemperature.CELSIUS,
    device_class=NumberDeviceClass.TEMPERATURE,
    icon=_icon_temperature,
    mode=NumberMode.BOX,
    native_min_value=7,
    native_max_value=30,
    native_step=1,
)
_sensor_356 = XtNumberEntityDescription(
    key="356",
    native_unit_of_measurement=UnitOfTemperature.CELSIUS,
    device_class=NumberDeviceClass.TEMPERATURE,
    icon=_icon_temperature,
    mode=NumberMode.BOX,
    native_min_value=7,
    native_max_value=30,
    native_step=1,
)
_sensor_360 = XtNumberEntityDescription(
    key="360",
    native_unit_of_measurement=UnitOfTemperature.CELSIUS,
    device_class=NumberDeviceClass.TEMPERATURE,
    icon=_icon_temperature,
    mode=NumberMode.BOX,
    native_min_value=7,
    native_max_value=30,
    native_step=1,
)
_sensor_410 = XtSwitchEntityDescription(
    key="410",
    icon=_icon_heating,
)
_sensor_411 = XtNumberEntityDescription(
    key="411",
    native_unit_of_measurement=UnitOfTemperature.CELSIUS,
    device_class=NumberDeviceClass.TEMPERATURE,
    icon=_icon_temperature,
    mode=NumberMode.BOX,
    native_min_value=-20,
    native_max_value=25,
    native_step=1,
)
_sensor_412 = XtNumberEntityDescription(
    key="412",
    native_unit_of_measurement=UnitOfTemperature.CELSIUS,
    device_class=NumberDeviceClass.TEMPERATURE,
    icon=_icon_temperature,
    mode=NumberMode.BOX,
    native_min_value=-9,
    native_max_value=25,
    native_step=1,
)
_sensor_415 = XtNumberEntityDescription(
    key="415",
    native_unit_of_measurement=UnitOfTemperature.CELSIUS,
    device_class=NumberDeviceClass.TEMPERATURE,
    icon=_icon_temperature,
    mode=NumberMode.BOX,
    native_min_value=20,
    native_max_value=75,
    native_step=1,
)
_sensor_416 = XtNumberEntityDescription(
    key="416",
    native_unit_of_measurement=UnitOfTemperature.CELSIUS,
    device_class=NumberDeviceClass.TEMPERATURE,
    icon=_icon_temperature,
    mode=NumberMode.BOX,
    native_min_value=20,
    native_max_value=75,
    native_step=1,
)
_sensor_420 = XtNumberEntityDescription(
    key="420",
    native_unit_of_measurement=UnitOfTemperature.CELSIUS,
    device_class=NumberDeviceClass.TEMPERATURE,
    icon=_icon_temperature,
    mode=NumberMode.BOX,
    native_min_value=20,
    native_max_value=75,
    native_step=1,
)
_sensor_450 = XtSwitchEntityDescription(
    key="450",
    icon=_icon_cooling,
)
_sensor_451 = XtNumberEntityDescription(
    key="451",
    native_unit_of_measurement=UnitOfTemperature.CELSIUS,
    device_class=NumberDeviceClass.TEMPERATURE,
    icon=_icon_temperature,
    mode=NumberMode.BOX,
    native_min_value=16,
    native_max_value=32,
    native_step=1,
)
_sensor_452 = XtNumberEntityDescription(
    key="452",
    native_unit_of_measurement=UnitOfTemperature.CELSIUS,
    device_class=NumberDeviceClass.TEMPERATURE,
    icon=_icon_temperature,
    mode=NumberMode.BOX,
    native_min_value=29,
    native_max_value=45,
    native_step=1,
)
_sensor_455 = XtNumberEntityDescription(
    key="455",
    native_unit_of_measurement=UnitOfTemperature.CELSIUS,
    device_class=NumberDeviceClass.TEMPERATURE,
    icon=_icon_temperature,
    mode=NumberMode.BOX,
    native_min_value=7,
    native_max_value=30,
    native_step=1,
)
_sensor_456 = XtNumberEntityDescription(
    key="456",
    native_unit_of_measurement=UnitOfTemperature.CELSIUS,
    device_class=NumberDeviceClass.TEMPERATURE,
    icon=_icon_temperature,
    mode=NumberMode.BOX,
    native_min_value=7,
    native_max_value=30,
    native_step=1,
)
_sensor_460 = XtNumberEntityDescription(
    key="460",
    native_unit_of_measurement=UnitOfTemperature.CELSIUS,
    device_class=NumberDeviceClass.TEMPERATURE,
    icon=_icon_temperature,
    mode=NumberMode.BOX,
    native_min_value=7,
    native_max_value=30,
    native_step=1,
)
_sensor_501 = XtNumberEntityDescription(
    key="501",
    native_unit_of_measurement=UnitOfTemperature.CELSIUS,
    device_class=NumberDeviceClass.TEMPERATURE,
    icon=_icon_temperature_target_water,
    mode=NumberMode.BOX,
    native_min_value=25,
    native_max_value=75,
    native_step=1,
)
_sensor_522 = XtNumberEntityDescription(
    key="522",
    native_unit_of_measurement=UnitOfTemperature.CELSIUS,
    device_class=NumberDeviceClass.TEMPERATURE,
    icon=_icon_temperature_target_water,
    mode=NumberMode.BOX,
    native_min_value=30,
    native_max_value=55,
    native_step=1,
)
_sensor_815 = XtSelectEntityDescription(
    key="815",
    options=_815_options,
    icon_provider=_815_icon,
)
_sensor_811 = XtNumberEntityDescription(
    key="811",
    native_unit_of_measurement=UnitOfTemperature.CELSIUS,
    device_class=NumberDeviceClass.TEMPERATURE,
    icon=_icon_temperature_target_heating,
    mode=NumberMode.BOX,
    native_min_value=0,
    native_max_value=30,
    native_step=1,
)

_sensor_812 = XtNumberEntityDescription(
    key="812",
    native_unit_of_measurement=UnitOfTemperature.CELSIUS,
    device_class=NumberDeviceClass.TEMPERATURE,
    icon=_icon_temperature_target_water,
    mode=NumberMode.BOX,
    native_min_value=0,
    native_max_value=30,
    native_step=1,
)

_sensor_813 = XtNumberEntityDescription(
    key="813",
    native_unit_of_measurement=UnitOfTemperature.CELSIUS,
    device_class=NumberDeviceClass.TEMPERATURE,
    icon=_icon_temperature_target_cooling,
    mode=NumberMode.BOX,
    native_min_value=0,
    native_max_value=30,
    native_step=1,
)

_sensor_808 = XtSwitchEntityDescription(
    key="808",
)

_sensor_x2400 = XtSwitchEntityDescription(
    key="x2400",
)

_sensor_x2401 = XtNumberEntityDescription(
    key="x2401",
    native_unit_of_measurement=UnitOfPower.WATT,
    device_class=NumberDeviceClass.POWER,
    icon=_icon_electric_power,
    mode=NumberMode.BOX,
    native_min_value=0,
    native_max_value=65000,
    native_step=1,
)

#
# Telemetry
#
_sensor_tvl = XtSensorEntityDescription(
    key="tvl",
    native_unit_of_measurement=UnitOfTemperature.CELSIUS,
    device_class=SensorDeviceClass.TEMPERATURE,
    state_class=SensorStateClass.MEASUREMENT,
    factor="/10",
    icon=_icon_heating_in,
)
_sensor_trl = XtSensorEntityDescription(
    key="trl",
    native_unit_of_measurement=UnitOfTemperature.CELSIUS,
    device_class=SensorDeviceClass.TEMPERATURE,
    state_class=SensorStateClass.MEASUREMENT,
    factor="/10",
    icon=_icon_heating_out,
)
_sensor_tw = XtSensorEntityDescription(
    key="tw",
    native_unit_of_measurement=UnitOfTemperature.CELSIUS,
    device_class=SensorDeviceClass.TEMPERATURE,
    state_class=SensorStateClass.MEASUREMENT,
    factor="/10",
    icon=_icon_temperature_water,
)
_sensor_tk = XtSensorEntityDescription(
    key="tk",
    native_unit_of_measurement=UnitOfTemperature.CELSIUS,
    device_class=SensorDeviceClass.TEMPERATURE,
    state_class=SensorStateClass.MEASUREMENT,
    factor="/10",
    icon=_icon_temperature,
)
_sensor_tk1 = XtSensorEntityDescription(
    key="tk1",
    native_unit_of_measurement=UnitOfTemperature.CELSIUS,
    device_class=SensorDeviceClass.TEMPERATURE,
    state_class=SensorStateClass.MEASUREMENT,
    factor="/10",
    icon=_icon_temperature,
)
_sensor_tk2 = XtSensorEntityDescription(
    key="tk2",
    native_unit_of_measurement=UnitOfTemperature.CELSIUS,
    device_class=SensorDeviceClass.TEMPERATURE,
    state_class=SensorStateClass.MEASUREMENT,
    factor="/10",
    icon=_icon_temperature,
)
_sensor_vf = XtSensorEntityDescription(
    key="vf",
    native_unit_of_measurement=UnitOfFrequency.HERTZ,
    device_class=SensorDeviceClass.FREQUENCY,
    state_class=SensorStateClass.MEASUREMENT,
    suggested_display_precision=0,
    icon=_icon_frequency,
)
_sensor_ta = XtSensorEntityDescription(
    key="ta",
    native_unit_of_measurement=UnitOfTemperature.CELSIUS,
    device_class=SensorDeviceClass.TEMPERATURE,
    state_class=SensorStateClass.MEASUREMENT,
    factor="/10",
    icon=_icon_temperature,
)
_sensor_ta1 = XtSensorEntityDescription(
    key="ta1",
    native_unit_of_measurement=UnitOfTemperature.CELSIUS,
    device_class=SensorDeviceClass.TEMPERATURE,
    state_class=SensorStateClass.MEASUREMENT,
    factor="/10",
    icon=_icon_temperature_average,
)
_sensor_ta4 = XtSensorEntityDescription(
    key="ta4",
    native_unit_of_measurement=UnitOfTemperature.CELSIUS,
    device_class=SensorDeviceClass.TEMPERATURE,
    state_class=SensorStateClass.MEASUREMENT,
    factor="/10",
    icon=_icon_temperature_average,
)
_sensor_ta24 = XtSensorEntityDescription(
    key="ta24",
    native_unit_of_measurement=UnitOfTemperature.CELSIUS,
    device_class=SensorDeviceClass.TEMPERATURE,
    state_class=SensorStateClass.MEASUREMENT,
    factor="/10",
    icon=_icon_temperature_average,
)
_sensor_ld1 = XtSensorEntityDescription(
    key="ld1",
    native_unit_of_measurement=REVOLUTIONS_PER_MINUTE,
    state_class=SensorStateClass.MEASUREMENT,
    suggested_display_precision=0,
    icon=_icon_fan,
)
_sensor_ld2 = XtSensorEntityDescription(
    key="ld2",
    native_unit_of_measurement=REVOLUTIONS_PER_MINUTE,
    state_class=SensorStateClass.MEASUREMENT,
    suggested_display_precision=0,
    icon=_icon_fan,
)
_sensor_tr = XtSensorEntityDescription(
    key="tr",
    native_unit_of_measurement=UnitOfTemperature.CELSIUS,
    device_class=SensorDeviceClass.TEMPERATURE,
    state_class=SensorStateClass.MEASUREMENT,
    factor="/10",
    icon=_icon_temperature,
)
_sensor_pk = XtBinarySensorEntityDescription(
    key="pk",
    device_class=BinarySensorDeviceClass.RUNNING,
    icon_provider=_pump_on_off_icon,
)
_sensor_pkl = XtSensorEntityDescription(
    key="pkl",
    factor="/10",
    native_unit_of_measurement=PERCENTAGE,
    device_class=None,
    state_class=SensorStateClass.MEASUREMENT,
    icon=_icon_pump,
)
_sensor_pk1 = XtBinarySensorEntityDescription(
    key="pk1",
    device_class=BinarySensorDeviceClass.RUNNING,
    icon_provider=_pump_on_off_icon,
)
_sensor_pk2 = XtBinarySensorEntityDescription(
    key="pk2",
    device_class=BinarySensorDeviceClass.RUNNING,
    icon_provider=_pump_on_off_icon,
)
_sensor_pww = XtBinarySensorEntityDescription(
    key="pww",
    device_class=BinarySensorDeviceClass.RUNNING,
    icon_provider=_pump_on_off_icon,
)
_sensor_h_target = XtSensorEntityDescription(
    key="h_target",
    native_unit_of_measurement=UnitOfTemperature.CELSIUS,
    device_class=SensorDeviceClass.TEMPERATURE,
    state_class=SensorStateClass.MEASUREMENT,
    factor="/10",
    icon=_icon_temperature_target_heating,
)
_sensor_h1_target = XtSensorEntityDescription(
    key="h1_target",
    native_unit_of_measurement=UnitOfTemperature.CELSIUS,
    device_class=SensorDeviceClass.TEMPERATURE,
    state_class=SensorStateClass.MEASUREMENT,
    factor="/10",
    icon=_icon_temperature_target_heating,
)
_sensor_h2_target = XtSensorEntityDescription(
    key="h2_target",
    native_unit_of_measurement=UnitOfTemperature.CELSIUS,
    device_class=SensorDeviceClass.TEMPERATURE,
    state_class=SensorStateClass.MEASUREMENT,
    factor="/10",
    icon=_icon_temperature_target_heating,
)
_sensor_c_target = XtSensorEntityDescription(
    key="c_target",
    native_unit_of_measurement=UnitOfTemperature.CELSIUS,
    device_class=SensorDeviceClass.TEMPERATURE,
    state_class=SensorStateClass.MEASUREMENT,
    factor="/10",
    icon=_icon_temperature_target_cooling,
)
_sensor_c1_target = XtSensorEntityDescription(
    key="c1_target",
    native_unit_of_measurement=UnitOfTemperature.CELSIUS,
    device_class=SensorDeviceClass.TEMPERATURE,
    state_class=SensorStateClass.MEASUREMENT,
    factor="/10",
    icon=_icon_temperature_target_cooling,
)
_sensor_c2_target = XtSensorEntityDescription(
    key="c2_target",
    native_unit_of_measurement=UnitOfTemperature.CELSIUS,
    device_class=SensorDeviceClass.TEMPERATURE,
    state_class=SensorStateClass.MEASUREMENT,
    factor="/10",
    icon=_icon_temperature_target_cooling,
)
_sensor_hw_target = XtSensorEntityDescription(
    key="hw_target",
    native_unit_of_measurement=UnitOfTemperature.CELSIUS,
    device_class=SensorDeviceClass.TEMPERATURE,
    state_class=SensorStateClass.MEASUREMENT,
    icon=_icon_temperature_target_water,
)
_sensor_in_hp = XtSensorEntityDescription(
    key="in_hp",
    native_unit_of_measurement=UnitOfPower.WATT,
    device_class=SensorDeviceClass.POWER,
    state_class=SensorStateClass.MEASUREMENT,
    factor="*10",
    icon=_icon_electric_power,
)
_sensor_v = XtSensorEntityDescription(
    key="v",
    native_unit_of_measurement=UnitOfVolumeFlowRate.LITERS_PER_MINUTE,
    device_class=SensorDeviceClass.VOLUME_FLOW_RATE,
    state_class=SensorStateClass.MEASUREMENT,
    factor="/10",
    icon=_icon_volume_rate,
)
_sensor_out_hp = XtSensorEntityDescription(
    key="out_hp",
    native_unit_of_measurement=UnitOfPower.WATT,
    device_class=SensorDeviceClass.POWER,
    state_class=SensorStateClass.MEASUREMENT,
    factor="*10",
    icon=_icon_thermal_power,
)
_sensor_efficiency_hp = XtSensorEntityDescription(
    key="efficiency_hp",
    state_class=SensorStateClass.MEASUREMENT,
    factor="/100",
    icon=_icon_performance,
)
_sensor_efficiency_total = XtSensorEntityDescription(
    key="efficiency_total",
    state_class=SensorStateClass.MEASUREMENT,
    factor="/100",
    icon=_icon_performance,
)
_sensor_in_backup = XtSensorEntityDescription(
    key="in_backup",
    native_unit_of_measurement=UnitOfPower.WATT,
    device_class=SensorDeviceClass.POWER,
    state_class=SensorStateClass.MEASUREMENT,
    factor="*10",
    icon=_icon_electric_power,
)
_sensor_out_backup = XtSensorEntityDescription(
    key="out_backup",
    native_unit_of_measurement=UnitOfPower.WATT,
    device_class=SensorDeviceClass.POWER,
    state_class=SensorStateClass.MEASUREMENT,
    factor="*10",
    icon=_icon_thermal_power,
)
_sensor_in_total = XtSensorEntityDescription(
    key="in_total",
    native_unit_of_measurement=UnitOfPower.WATT,
    device_class=SensorDeviceClass.POWER,
    state_class=SensorStateClass.MEASUREMENT,
    factor="*10",
    icon=_icon_electric_power,
)
_sensor_out_total = XtSensorEntityDescription(
    key="out_total",
    native_unit_of_measurement=UnitOfPower.WATT,
    device_class=SensorDeviceClass.POWER,
    state_class=SensorStateClass.MEASUREMENT,
    factor="*10",
    icon=_icon_thermal_power,
)
_sensor_ta8 = XtSensorEntityDescription(
    key="ta8",
    native_unit_of_measurement=UnitOfTemperature.CELSIUS,
    device_class=SensorDeviceClass.TEMPERATURE,
    state_class=SensorStateClass.MEASUREMENT,
    factor="/10",
    icon=_icon_temperature_average,
)
_sensor_day_hp_out_h = XtSensorEntityDescription(
    key="day_hp_out_h",
    native_unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR,
    device_class=SensorDeviceClass.ENERGY,
    state_class=SensorStateClass.TOTAL_INCREASING,
    icon=_icon_thermal_power,
    factor="/100",
)
_sensor_day_hp_out_c = XtSensorEntityDescription(
    key="day_hp_out_c",
    native_unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR,
    device_class=SensorDeviceClass.ENERGY,
    state_class=SensorStateClass.TOTAL_INCREASING,
    icon=_icon_thermal_power,
    factor="/100",
)
_sensor_day_hp_out_hw = XtSensorEntityDescription(
    key="day_hp_out_hw",
    native_unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR,
    device_class=SensorDeviceClass.ENERGY,
    state_class=SensorStateClass.TOTAL_INCREASING,
    icon=_icon_thermal_power,
    factor="/100",
)
_sensor_day_backup3_out_h = XtSensorEntityDescription(
    key="day_backup3_out_h",
    native_unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR,
    device_class=SensorDeviceClass.ENERGY,
    state_class=SensorStateClass.TOTAL_INCREASING,
    icon=_icon_thermal_power,
    factor="/100",
)
_sensor_day_backup6_out_h = XtSensorEntityDescription(
    key="day_backup6_out_h",
    native_unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR,
    device_class=SensorDeviceClass.ENERGY,
    state_class=SensorStateClass.TOTAL_INCREASING,
    icon=_icon_thermal_power,
    factor="/100",
)
_sensor_day_backup6_out_hw = XtSensorEntityDescription(
    key="day_backup6_out_hw",
    native_unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR,
    device_class=SensorDeviceClass.ENERGY,
    state_class=SensorStateClass.TOTAL_INCREASING,
    icon=_icon_thermal_power,
    factor="/100",
)
_sensor_day_backup3_out_hw = XtSensorEntityDescription(
    key="day_backup3_out_hw",
    native_unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR,
    device_class=SensorDeviceClass.ENERGY,
    state_class=SensorStateClass.TOTAL_INCREASING,
    icon=_icon_thermal_power,
    factor="/100",
)
_sensor_day_hp_in_h = XtSensorEntityDescription(
    key="day_hp_in_h",
    native_unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR,
    device_class=SensorDeviceClass.ENERGY,
    state_class=SensorStateClass.TOTAL_INCREASING,
    icon=_icon_electric_power,
    factor="/100",
)
_sensor_day_hp_in_c = XtSensorEntityDescription(
    key="day_hp_in_c",
    native_unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR,
    device_class=SensorDeviceClass.ENERGY,
    state_class=SensorStateClass.TOTAL_INCREASING,
    icon=_icon_electric_power,
    factor="/100",
)
_sensor_day_hp_in_hw = XtSensorEntityDescription(
    key="day_hp_in_hw",
    native_unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR,
    device_class=SensorDeviceClass.ENERGY,
    state_class=SensorStateClass.TOTAL_INCREASING,
    icon=_icon_electric_power,
    factor="/100",
)
_sensor_day_backup3_in_hw = XtSensorEntityDescription(
    key="day_backup3_in_hw",
    native_unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR,
    device_class=SensorDeviceClass.ENERGY,
    state_class=SensorStateClass.TOTAL_INCREASING,
    icon=_icon_electric_power,
    factor="/100",
)
_sensor_day_backup6_in_hw = XtSensorEntityDescription(
    key="day_backup6_in_hw",
    native_unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR,
    device_class=SensorDeviceClass.ENERGY,
    state_class=SensorStateClass.TOTAL_INCREASING,
    icon=_icon_electric_power,
    factor="/100",
)
_sensor_day_backup3_in_h = XtSensorEntityDescription(
    key="day_backup3_in_h",
    native_unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR,
    device_class=SensorDeviceClass.ENERGY,
    state_class=SensorStateClass.TOTAL_INCREASING,
    icon=_icon_electric_power,
    factor="/100",
)
_sensor_day_backup6_in_h = XtSensorEntityDescription(
    key="day_backup6_in_h",
    native_unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR,
    device_class=SensorDeviceClass.ENERGY,
    state_class=SensorStateClass.TOTAL_INCREASING,
    icon=_icon_electric_power,
    factor="/100",
)
_sensor_controller_v = XtVersionSensorEntityDescription(
    key="controller_v",
    icon="mdi:information-outline",
    factor="/100",
)
_sensor_mode = XtSensorEntityDescription(
    key="mode",
    device_class=SensorDeviceClass.ENUM,
    options=_mode_options,
    icon_provider=_mode_icon,
)
_sensor_error = XtBinarySensorEntityDescription(
    key="error",
    device_class=BinarySensorDeviceClass.RUNNING,
    icon_provider=_error_icon,
)
_sensor_error_2 = XtBinarySensorEntityDescription(
    key="error_2",
    device_class=BinarySensorDeviceClass.RUNNING,
    icon_provider=_error_icon,
)
_sensor_error_1 = XtBinarySensorEntityDescription(
    key="error_1",
    device_class=BinarySensorDeviceClass.PROBLEM,
    icon_provider=_error_1_icon,
)
_sensor_sg = XtSensorEntityDescription(
    key="sg",
    device_class=SensorDeviceClass.ENUM,
    options=_sgready_options,
    icon_provider=_sgready_icon,
)
_sensor_14a = XtBinarySensorEntityDescription(
    key="14a",
)
_sensor_evu = XtBinarySensorEntityDescription(
    key="evu",
    icon_provider=_electric_switch_icon,
)


@dataclass(kw_only=True, frozen=True)
class ModbusRegisterSet:
    """Register set."""

    base: int
    descriptors: list[
        XtSensorEntityDescription
        | XtBinarySensorEntityDescription
        | XtSwitchEntityDescription
        | XtNumberEntityDescription
        | XtSelectEntityDescription
        | None
    ]


_MODBUS_SETTINGS_GENERAL = ModbusRegisterSet(
    base=0,
    descriptors=[
        _sensor_001,
        _sensor_002,
        _sensor_003,
    ],
)

_MODBUS_SETTINGS_HEATING_CURVE_1 = ModbusRegisterSet(
    base=10,
    descriptors=[
        _sensor_310,
        _sensor_311,
        _sensor_312,
        _sensor_315,
        _sensor_316,
        _sensor_320,
    ],
)

_MODBUS_SETTINGS_COOLING_CURVE_1 = ModbusRegisterSet(
    base=20,
    descriptors=[
        _sensor_350,
        _sensor_351,
        _sensor_352,
        _sensor_355,
        _sensor_356,
        _sensor_360,
    ],
)

_MODBUS_SETTINGS_HEATING_CURVE_2 = ModbusRegisterSet(
    base=30,
    descriptors=[
        _sensor_410,
        _sensor_411,
        _sensor_412,
        _sensor_415,
        _sensor_416,
        _sensor_420,
    ],
)

_MODBUS_SETTINGS_COOLING_CURVE_2 = ModbusRegisterSet(
    base=40,
    descriptors=[
        _sensor_450,
        _sensor_451,
        _sensor_452,
        _sensor_455,
        _sensor_456,
        _sensor_460,
    ],
)

_MODBUS_SETTINGS_HOT_WATER = ModbusRegisterSet(
    base=50,
    descriptors=[
        _sensor_501,
        _sensor_522,
    ],
)

_MODBUS_SETTINGS_NETWORK = ModbusRegisterSet(
    base=60,
    descriptors=[
        _sensor_808,
        _sensor_811,
        _sensor_812,
        _sensor_813,
        _sensor_815,
    ],
)

_MODBUS_SETTINGS_NETWORK = ModbusRegisterSet(
    base=60,
    descriptors=[
        _sensor_808,
        _sensor_811,
        _sensor_812,
        _sensor_813,
        _sensor_815,
    ],
)

_MODBUS_SETTINGS_SURPLUS = ModbusRegisterSet(
    base=70,
    descriptors=[
        _sensor_x2400,
        _sensor_x2401,
    ],
)

_MODBUS_TELEMETRY_GENERAL = ModbusRegisterSet(
    base=100,
    descriptors=[
        _sensor_controller_v,
        _sensor_mode,
        _sensor_error,
        _sensor_14a,
        _sensor_sg,
        _sensor_evu,
    ],
)

_MODBUS_TELEMETRY_TARGET_VALUES = ModbusRegisterSet(
    base=110,
    descriptors=[
        _sensor_h_target,
        _sensor_h1_target,
        _sensor_h2_target,
        _sensor_c_target,
        _sensor_c1_target,
        _sensor_c2_target,
        _sensor_hw_target,
    ],
)

_MODBUS_TELEMETRY_TEMPERATURE_SENSORS = ModbusRegisterSet(
    base=120,
    descriptors=[
        _sensor_tk,
        _sensor_tk1,
        _sensor_tk2,
        _sensor_tw,
        _sensor_tr,
        _sensor_trl,
        _sensor_tvl,
    ],
)

_MODBUS_TELEMETRY_PUMPS_AND_ACTORS = ModbusRegisterSet(
    base=130,
    descriptors=[
        _sensor_v,
        _sensor_pk,
        _sensor_pkl,
        _sensor_pk1,
        _sensor_pk2,
        _sensor_pww,
        _sensor_vf,
        _sensor_ld1,
        _sensor_ld2,
    ],
)

_MODBUS_TELEMETRY_OUTSIDE_TEMPERATURES = ModbusRegisterSet(
    base=140,
    descriptors=[
        _sensor_ta,
        _sensor_ta1,
        _sensor_ta4,
        _sensor_ta8,
        _sensor_ta24,
    ],
)

_MODBUS_TELEMETRY_PERFORMANCE_LIVE = ModbusRegisterSet(
    base=170,
    descriptors=[
        _sensor_out_hp,
        _sensor_in_hp,
        _sensor_efficiency_hp,
        _sensor_efficiency_total,
        _sensor_out_backup,
        _sensor_in_backup,
        _sensor_out_total,
        _sensor_in_total,
    ],
)

_MODBUS_TELEMETRY_PER_DAY_ENERGY = ModbusRegisterSet(
    base=180,
    descriptors=[
        _sensor_day_hp_out_h,
        _sensor_day_hp_in_h,
        _sensor_day_hp_out_c,
        _sensor_day_hp_in_c,
        _sensor_day_hp_out_hw,
        _sensor_day_hp_in_hw,
        _sensor_day_backup3_out_h,
        _sensor_day_backup3_in_h,
        _sensor_day_backup3_out_hw,
        _sensor_day_backup3_in_hw,
        _sensor_day_backup6_out_h,
        _sensor_day_backup6_in_h,
        _sensor_day_backup6_out_hw,
        _sensor_day_backup6_in_hw,
    ],
)

MODBUS_ENTITY_DESCRIPTIONS: list[ModbusRegisterSet] = [
    _MODBUS_SETTINGS_GENERAL,
    _MODBUS_SETTINGS_HEATING_CURVE_1,
    _MODBUS_SETTINGS_COOLING_CURVE_1,
    _MODBUS_SETTINGS_HEATING_CURVE_2,
    _MODBUS_SETTINGS_COOLING_CURVE_2,
    _MODBUS_SETTINGS_HOT_WATER,
    _MODBUS_SETTINGS_NETWORK,
    _MODBUS_SETTINGS_SURPLUS,
    _MODBUS_TELEMETRY_GENERAL,
    _MODBUS_TELEMETRY_TARGET_VALUES,
    _MODBUS_TELEMETRY_TEMPERATURE_SENSORS,
    _MODBUS_TELEMETRY_PUMPS_AND_ACTORS,
    _MODBUS_TELEMETRY_OUTSIDE_TEMPERATURES,
    _MODBUS_TELEMETRY_PERFORMANCE_LIVE,
    _MODBUS_TELEMETRY_PER_DAY_ENERGY,
]


# The modbus protocol only allows reading up to 125 registers at once.
# Therefore, we need to split the entire register range into
# manageable sub ranges.
@dataclass(kw_only=True, frozen=True)
class ModbusRegisterRange:
    """Definition of a register range which is read in one call."""

    # first and last register of this range
    first_reg: int
    last_reg: int

    # a register in this range which cannot ever be empty
    # this is used to detect bogus reads where the device sends us
    # empty data instead of, for instance, a busy response.
    non_empty_reg: int

    @property
    def length(self) -> int:
        """Number of registers in this range."""
        return self.last_reg - self.first_reg + 1


MODBUS_REGISTER_RANGES: list[ModbusRegisterRange] = [
    ModbusRegisterRange(first_reg=0, last_reg=71, non_empty_reg=50),
    ModbusRegisterRange(first_reg=100, last_reg=193, non_empty_reg=100),
]

# The total size of the modbus register space used.
MODBUS_REGISTER_SIZE = MODBUS_REGISTER_RANGES[-1].last_reg + 1

ENTITY_DESCRIPTIONS: list[EntityDescription] = [
    # ------- general system state
    _sensor_001,
    _sensor_002,
    _sensor_003,
    # ------- heating curve 1
    _sensor_310,
    _sensor_311,
    _sensor_312,
    _sensor_315,
    _sensor_316,
    _sensor_320,
    # ------- cooling curve 1
    _sensor_350,
    _sensor_351,
    _sensor_352,
    _sensor_355,
    _sensor_356,
    _sensor_360,
    # ------- heating curve 2
    _sensor_410,
    _sensor_411,
    _sensor_412,
    _sensor_415,
    _sensor_416,
    _sensor_420,
    # ------- cooling curve 2
    _sensor_450,
    _sensor_451,
    _sensor_452,
    _sensor_455,
    _sensor_456,
    _sensor_460,
    # ------- warm water
    _sensor_501,
    _sensor_522,
    # ------- network
    _sensor_811,
    _sensor_812,
    _sensor_813,
    # ------- general
    _sensor_controller_v,
    _sensor_mode,
    _sensor_error_2,
    _sensor_error_1,
    _sensor_14a,
    _sensor_sg,
    _sensor_evu,
    # ------- target values
    _sensor_h_target,
    _sensor_h1_target,
    _sensor_h2_target,
    _sensor_c_target,
    _sensor_c1_target,
    _sensor_c2_target,
    _sensor_hw_target,
    # ------- temperature sensors
    _sensor_tk,
    _sensor_tk1,
    _sensor_tk2,
    _sensor_tw,
    _sensor_tr,
    _sensor_trl,
    _sensor_tvl,
    # ------- pumps and actors
    _sensor_v,
    _sensor_pk,
    _sensor_pkl,
    _sensor_pk1,
    _sensor_pk2,
    _sensor_pww,
    _sensor_vf,
    _sensor_ld1,
    _sensor_ld2,
    # ------- outside temperatures
    _sensor_ta,
    _sensor_ta1,
    _sensor_ta4,
    _sensor_ta8,
    _sensor_ta24,
    # ------- performance live
    _sensor_out_hp,
    _sensor_in_hp,
    _sensor_efficiency_hp,
    _sensor_efficiency_total,
    _sensor_out_backup,
    _sensor_in_backup,
    # ------- per day energy values
    _sensor_day_hp_out_h,
    _sensor_day_hp_in_h,
    _sensor_day_hp_out_c,
    _sensor_day_hp_in_c,
    _sensor_day_hp_out_hw,
    _sensor_day_hp_in_hw,
    _sensor_day_backup3_out_h,
    _sensor_day_backup3_in_h,
    _sensor_day_backup3_out_hw,
    _sensor_day_backup6_in_hw,
    _sensor_day_backup6_out_h,
    _sensor_day_backup6_in_h,
    _sensor_day_backup6_out_hw,
    _sensor_day_backup3_in_hw,
]
