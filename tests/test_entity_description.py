"""Tests for entitiy description."""

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntityDescription,
    SensorStateClass,
)
from homeassistant.const import (
    UnitOfTemperature,
)

from custom_components.xtherma_fp.entity_descriptors import (
    ENTITY_DESCRIPTIONS,
    XtSensorEntityDescription,
)


def test_xt_sensor_entity_description():
    desc_tvl = ENTITY_DESCRIPTIONS[52]
    assert desc_tvl is not None
    assert isinstance(desc_tvl, SensorEntityDescription)
    assert desc_tvl.key == "tvl"
    assert desc_tvl.native_unit_of_measurement == UnitOfTemperature.CELSIUS
    assert desc_tvl.device_class == SensorDeviceClass.TEMPERATURE
    assert desc_tvl.state_class == SensorStateClass.MEASUREMENT
    assert isinstance(desc_tvl, XtSensorEntityDescription)
    assert desc_tvl.factor == "/10"
