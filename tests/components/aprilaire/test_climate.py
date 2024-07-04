"""Tests for the Aprilaire climate entity."""

import pytest

from homeassistant.components.aprilaire.climate import (
    AprilaireClimate,
    FAN_CIRCULATE,
    PRESET_VACATION,
)
from homeassistant.components.climate import (
    ATTR_CURRENT_TEMPERATURE,
    ATTR_FAN_MODE,
    ATTR_FAN_MODES,
    ATTR_HVAC_ACTION,
    ATTR_HVAC_MODES,
    ATTR_MAX_TEMP,
    ATTR_MIN_TEMP,
    ATTR_PRESET_MODE,
    ATTR_PRESET_MODES,
    ATTR_TARGET_TEMP_STEP,
    DEFAULT_MAX_TEMP,
    DEFAULT_MIN_TEMP,
    FAN_AUTO,
    FAN_ON,
    PRESET_NONE,
    ClimateEntityFeature,
    HVACAction,
    HVACMode,
)
from homeassistant.const import (
    ATTR_FRIENDLY_NAME,
    ATTR_SUPPORTED_FEATURES,
)
from homeassistant.helpers import entity_registry as er
from homeassistant.core import HomeAssistant
from homeassistant.util.unit_system import METRIC_SYSTEM, US_CUSTOMARY_SYSTEM
from pyaprilaire.const import Attribute
from .common import PlatformSetup

ENTITY_ID = "climate.aprilaire_thermostat"


@pytest.fixture
def platforms() -> list[str]:
    """Fixture to specify platforms to test."""
    return ["climate"]


async def test_climate_device_is_setup(
    hass: HomeAssistant, setup_platform: PlatformSetup
) -> None:
    """Test climate device is returned by the api."""

    await setup_platform()

    climate = hass.states.get(ENTITY_ID)

    assert climate is not None


async def test_basic_attributes(
    hass: HomeAssistant, setup_platform: PlatformSetup
) -> None:
    """Test the climate current fan mode."""

    await setup_platform()

    climate_state = hass.states.get(ENTITY_ID)

    assert climate_state.attributes.get(ATTR_HVAC_MODES) == []
    assert climate_state.attributes.get(ATTR_MIN_TEMP) == DEFAULT_MIN_TEMP
    assert climate_state.attributes.get(ATTR_MAX_TEMP) == DEFAULT_MAX_TEMP
    assert climate_state.attributes.get(ATTR_TARGET_TEMP_STEP) == 0.5
    assert climate_state.attributes.get(ATTR_FAN_MODES) == [
        FAN_AUTO,
        FAN_ON,
        FAN_CIRCULATE,
    ]
    assert climate_state.attributes.get(ATTR_PRESET_MODES) == [
        PRESET_NONE,
        PRESET_VACATION,
    ]
    assert not climate_state.attributes.get(ATTR_CURRENT_TEMPERATURE)
    assert not climate_state.attributes.get(ATTR_FAN_MODE)
    assert climate_state.attributes.get(ATTR_HVAC_ACTION) == HVACAction.IDLE
    assert climate_state.attributes.get(ATTR_PRESET_MODE) == PRESET_NONE
    assert climate_state.attributes.get(ATTR_FRIENDLY_NAME) == "Aprilaire Thermostat"
    assert (
        climate_state.attributes.get(ATTR_SUPPORTED_FEATURES)
        == ClimateEntityFeature.TARGET_TEMPERATURE
        | ClimateEntityFeature.FAN_MODE
        | ClimateEntityFeature.PRESET_MODE
    )


async def test_fan_mode(
    hass: HomeAssistant,
    setup_platform: PlatformSetup,
    entity_registry: er.EntityRegistry,
) -> None:
    """Test the climate current fan mode."""

    await setup_platform()

    climate: AprilaireClimate = entity_registry.async_get(ENTITY_ID)
    pytest.set_trace()

    climate.coordinator.async_set_updated_data({Attribute.FAN_MODE: 1})

    pytest.set_trace()
