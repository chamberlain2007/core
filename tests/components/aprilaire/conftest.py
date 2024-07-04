"""Fixtures for component."""

from typing import Any
from unittest.mock import AsyncMock, patch

from pyaprilaire.client import AprilaireClient
from pyaprilaire.const import Attribute
import pytest

from homeassistant.components.aprilaire.const import DOMAIN
from homeassistant.const import CONF_HOST, CONF_PORT
from homeassistant.core import HomeAssistant
from homeassistant.setup import async_setup_component

from .common import PlatformSetup, YieldFixture

from tests.common import MockConfigEntry


@pytest.fixture
def mac_address() -> str:
    """Fixture to set ConfigEntry unique id."""
    return "1.2.3.4"


@pytest.fixture
def client(mac_address: str) -> AprilaireClient:
    """Get a client instance."""
    client_mock = AsyncMock(AprilaireClient)
    client_mock.connected = True
    client_mock.stopped = False
    client_mock.reconnecting = True
    client_mock.auto_reconnecting = True
    client_mock.data = {Attribute.MAC_ADDRESS: mac_address, Attribute.CONNECTED: True}

    client_mock.start_listen.return_value = True

    return client_mock


@pytest.fixture
async def setup_platform(
    hass: HomeAssistant,
    platforms: list[str],
    config: dict[str, Any],
    config_entry: MockConfigEntry | None,
    client: AprilaireClient,
) -> YieldFixture[PlatformSetup]:
    """Fixture to setup the integration platform."""
    if config_entry:
        config_entry.add_to_hass(hass)
    with (
        patch("homeassistant.components.aprilaire.PLATFORMS", platforms),
        patch("pyaprilaire.client.AprilaireClient", return_value=client),
    ):

        async def _setup_func() -> bool:
            assert await async_setup_component(hass, DOMAIN, config)
            await hass.async_block_till_done()

        yield _setup_func


@pytest.fixture
async def config(mac_address: str) -> dict[str, Any]:
    return {DOMAIN: {CONF_HOST: mac_address, CONF_PORT: 7000}}


@pytest.fixture
def config_entry(config: dict[str, Any], mac_address: str) -> MockConfigEntry | None:
    """Fixture that sets up the ConfigEntry for the test."""

    data = config[DOMAIN]

    return MockConfigEntry(domain=DOMAIN, data=data, unique_id=mac_address)


@pytest.fixture
def set_data(client: AprilaireClient):
    def _set_data(data: dict[str, Any]) -> None:
        client.data_received_callback(data)

    return _set_data
