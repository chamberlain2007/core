"""Tests for the Aprilaire humidifier/dehumidifier entity."""

import logging
from unittest.mock import AsyncMock, Mock, patch

from pyaprilaire.client import AprilaireClient
from pyaprilaire.const import Attribute
import pytest

from homeassistant.components.aprilaire.const import DOMAIN, MAX_HUMIDITY, MIN_HUMIDITY
from homeassistant.components.aprilaire.coordinator import AprilaireCoordinator
from homeassistant.components.aprilaire.humidifier import (
    AprilaireDehumidifier,
    AprilaireHumidifier,
    async_setup_entry,
)
from homeassistant.components.humidifier.const import HumidifierAction
from homeassistant.config_entries import ConfigEntries, ConfigEntry
from homeassistant.core import Config, EventBus, HomeAssistant
from homeassistant.util import uuid as uuid_util


@pytest.fixture
def logger() -> logging.Logger:
    """Return a logger."""
    logger = logging.getLogger()
    logger.propagate = False

    return logger


@pytest.fixture
def client() -> AprilaireClient:
    """Return a mock client."""
    return AsyncMock(AprilaireClient)


@pytest.fixture
def coordinator(
    client: AprilaireClient, logger: logging.Logger
) -> AprilaireCoordinator:
    """Return a mock coordinator."""
    coordinator_mock = AsyncMock(AprilaireCoordinator)
    coordinator_mock.data = {}
    coordinator_mock.client = client
    coordinator_mock.logger = logger

    return coordinator_mock


@pytest.fixture
def entry_id() -> str:
    """Return a random ID."""
    return uuid_util.random_uuid_hex()


@pytest.fixture
def hass(coordinator: AprilaireCoordinator, entry_id: str) -> HomeAssistant:
    """Return a mock HomeAssistant instance."""
    hass_mock = AsyncMock(HomeAssistant)
    hass_mock.data = {DOMAIN: {entry_id: coordinator}}
    hass_mock.config_entries = AsyncMock(ConfigEntries)
    hass_mock.bus = AsyncMock(EventBus)
    hass_mock.config = Mock(Config)

    return hass_mock


@pytest.fixture
def config_entry(entry_id: str) -> ConfigEntry:
    """Return a mock config entry."""
    config_entry_mock = AsyncMock(ConfigEntry)
    config_entry_mock.data = {"host": "test123", "port": 123}
    config_entry_mock.entry_id = entry_id

    return config_entry_mock


@pytest.fixture
async def humidifier(
    config_entry: ConfigEntry, coordinator: AprilaireCoordinator, hass: HomeAssistant
) -> AprilaireHumidifier:
    """Return a climate instance."""

    coordinator.data[Attribute.HUMIDIFICATION_AVAILABLE] = 2

    async_add_entities_mock = Mock()
    async_get_current_platform_mock = Mock()

    with patch(
        "homeassistant.helpers.entity_platform.async_get_current_platform",
        new=async_get_current_platform_mock,
    ):
        await async_setup_entry(hass, config_entry, async_add_entities_mock)

    humidifiers_list = async_add_entities_mock.call_args_list[0][0]

    humidifier = next(
        x for x in humidifiers_list[0] if isinstance(x, AprilaireHumidifier)
    )
    humidifier._attr_available = True
    humidifier.hass = hass

    return humidifier


@pytest.fixture
async def dehumidifier(
    config_entry: ConfigEntry, coordinator: AprilaireCoordinator, hass: HomeAssistant
) -> AprilaireDehumidifier:
    """Return a climate instance."""

    coordinator.data[Attribute.DEHUMIDIFICATION_AVAILABLE] = 1

    async_add_entities_mock = Mock()
    async_get_current_platform_mock = Mock()

    with patch(
        "homeassistant.helpers.entity_platform.async_get_current_platform",
        new=async_get_current_platform_mock,
    ):
        await async_setup_entry(hass, config_entry, async_add_entities_mock)

    humidifiers_list = async_add_entities_mock.call_args_list[0][0]

    dehumidifier = next(
        x for x in humidifiers_list[0] if isinstance(x, AprilaireDehumidifier)
    )
    dehumidifier._attr_available = True
    dehumidifier.hass = hass

    return dehumidifier


def test_humidifier_current_humidity(
    coordinator: AprilaireCoordinator, humidifier: AprilaireHumidifier
):
    """Test the humidifier's current humidity."""

    coordinator.data[Attribute.INDOOR_HUMIDITY_CONTROLLING_SENSOR_VALUE] = 20

    assert humidifier.current_humidity == 20


def test_humidifier_on(humidifier: AprilaireHumidifier):
    """Test that the humidifier is always on."""
    assert humidifier.is_on is True


def test_humidifier_max_humidity(humidifier: AprilaireHumidifier):
    """Test the humidifier's maximum humidity."""
    assert humidifier.max_humidity == MAX_HUMIDITY


def test_humidifier_min_humidity(humidifier: AprilaireHumidifier):
    """Test the humidifier's minimum humidity."""
    assert humidifier.min_humidity == MIN_HUMIDITY


def test_humidifier_action(
    coordinator: AprilaireCoordinator, humidifier: AprilaireHumidifier
):
    """Test the humidifier's action."""

    assert humidifier.action is None

    coordinator.data[Attribute.HUMIDIFICATION_STATUS] = 0
    assert humidifier.action == HumidifierAction.IDLE

    coordinator.data[Attribute.HUMIDIFICATION_STATUS] = 1
    assert humidifier.action == HumidifierAction.IDLE

    coordinator.data[Attribute.HUMIDIFICATION_STATUS] = 2
    assert humidifier.action == HumidifierAction.HUMIDIFYING

    coordinator.data[Attribute.HUMIDIFICATION_STATUS] = 3
    assert humidifier.action == HumidifierAction.OFF

    coordinator.data[Attribute.HUMIDIFICATION_STATUS] = 4
    assert humidifier.action is None


def test_humidifier_target_humidity(
    coordinator: AprilaireCoordinator, humidifier: AprilaireHumidifier
):
    """Test the humidifier's target humidity."""

    coordinator.data[Attribute.HUMIDIFICATION_SETPOINT] = 20

    assert humidifier.target_humidity == 20


async def test_humidifier_set_humidity(
    client: AprilaireClient,
    humidifier: AprilaireHumidifier,
) -> None:
    """Test setting the humidifier's humidity."""

    await humidifier.async_set_humidity(30)

    client.set_humidification_setpoint.assert_called_with(30)


def test_dehumidifier_current_humidity(
    coordinator: AprilaireCoordinator, dehumidifier: AprilaireDehumidifier
):
    """Test the dehumidifier's current humidity."""

    coordinator.data[Attribute.INDOOR_HUMIDITY_CONTROLLING_SENSOR_VALUE] = 20

    assert dehumidifier.current_humidity == 20


def test_dehumidifier_on(dehumidifier: AprilaireDehumidifier):
    """Test that the dehumidifier is always on."""
    assert dehumidifier.is_on is True


def test_dehumidifier_max_humidity(dehumidifier: AprilaireDehumidifier):
    """Test the dehumidifier's maximum humidity."""
    assert dehumidifier.max_humidity == MAX_HUMIDITY


def test_dehumidifier_min_humidity(dehumidifier: AprilaireDehumidifier):
    """Test the dehumidifier's minimum humidity."""
    assert dehumidifier.min_humidity == MIN_HUMIDITY


def test_dehumidifier_action(
    coordinator: AprilaireCoordinator, dehumidifier: AprilaireDehumidifier
):
    """Test the dehumidifier's action."""

    assert dehumidifier.action is None

    coordinator.data[Attribute.DEHUMIDIFICATION_STATUS] = 0
    assert dehumidifier.action == HumidifierAction.IDLE

    coordinator.data[Attribute.DEHUMIDIFICATION_STATUS] = 1
    assert dehumidifier.action == HumidifierAction.IDLE

    coordinator.data[Attribute.DEHUMIDIFICATION_STATUS] = 2
    assert dehumidifier.action == HumidifierAction.DRYING

    coordinator.data[Attribute.DEHUMIDIFICATION_STATUS] = 3
    assert dehumidifier.action == HumidifierAction.DRYING

    coordinator.data[Attribute.DEHUMIDIFICATION_STATUS] = 4
    assert dehumidifier.action == HumidifierAction.OFF

    coordinator.data[Attribute.DEHUMIDIFICATION_STATUS] = 5
    assert dehumidifier.action is None


def test_dehumidifier_target_humidity(
    coordinator: AprilaireCoordinator, dehumidifier: AprilaireDehumidifier
):
    """Test the dehumidifier's target humidity."""

    coordinator.data[Attribute.DEHUMIDIFICATION_SETPOINT] = 20

    assert dehumidifier.target_humidity == 20


async def test_dehumidifier_set_humidity(
    client: AprilaireClient,
    dehumidifier: AprilaireDehumidifier,
) -> None:
    """Test setting the dehumidifier's humidity."""

    await dehumidifier.async_set_humidity(30)

    client.set_dehumidification_setpoint.assert_called_with(30)
