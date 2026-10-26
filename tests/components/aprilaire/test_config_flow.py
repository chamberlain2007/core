"""Tests for the Aprilaire config flow."""

from unittest.mock import AsyncMock, Mock, patch

from pyaprilaire.client import AprilaireClient
from pyaprilaire.const import FunctionalDomain
import pytest

from homeassistant.components.aprilaire.config_flow import (
    STEP_USER_DATA_SCHEMA,
    AprilaireConfigFlow,
)
from homeassistant.components.aprilaire.const import DOMAIN
from homeassistant.config_entries import SOURCE_USER
from homeassistant.const import CONF_HOST, CONF_PORT
from homeassistant.core import HomeAssistant
from homeassistant.data_entry_flow import FlowResultType


@pytest.fixture
def client() -> AprilaireClient:
    """Return a mock client."""
    return AsyncMock(AprilaireClient)


async def test_user_input_step() -> None:
    """Test the user input step."""

    show_form_mock = Mock()

    config_flow = AprilaireConfigFlow()
    config_flow.async_show_form = show_form_mock

    await config_flow.async_step_user(None)

    show_form_mock.assert_called_once_with(
        step_id="user", data_schema=STEP_USER_DATA_SCHEMA
    )


async def test_config_flow_failure_keeps_user_input(
    client: AprilaireClient, hass: HomeAssistant
) -> None:
    """Test the form keeps the entered host and port after a failed connection."""

    with patch("pyaprilaire.client.AprilaireClient", return_value=client):
        result = await hass.config_entries.flow.async_init(
            DOMAIN, context={"source": SOURCE_USER}
        )
        result = await hass.config_entries.flow.async_configure(
            result["flow_id"], {CONF_HOST: "localhost", CONF_PORT: 8000}
        )

    assert result["type"] is FlowResultType.FORM
    assert result["errors"] == {"base": "connection_failed"}
    suggested_values = {
        str(key): key.description["suggested_value"]
        for key in result["data_schema"].schema
    }
    assert suggested_values == {CONF_HOST: "localhost", CONF_PORT: 8000}

    client.data = {"mac_address": "1:2:3:4:5:6"}
    client.wait_for_response = AsyncMock(return_value={"mac_address": "1:2:3:4:5:6"})

    with (
        patch("pyaprilaire.client.AprilaireClient", return_value=client),
        patch(
            "homeassistant.components.aprilaire.async_setup_entry", return_value=True
        ),
    ):
        result = await hass.config_entries.flow.async_configure(
            result["flow_id"], {CONF_HOST: "localhost", CONF_PORT: 8000}
        )

    assert result["type"] is FlowResultType.CREATE_ENTRY
    assert result["data"] == {CONF_HOST: "localhost", CONF_PORT: 8000}


async def test_config_flow_data(client: AprilaireClient, hass: HomeAssistant) -> None:
    """Test the config flow with valid data."""

    client.data = {"mac_address": "1:2:3:4:5:6"}

    show_form_mock = Mock()
    set_unique_id_mock = AsyncMock()
    abort_if_unique_id_configured_mock = Mock()
    create_entry_mock = Mock()

    config_flow = AprilaireConfigFlow()
    config_flow.hass = hass
    config_flow.async_show_form = show_form_mock
    config_flow.async_set_unique_id = set_unique_id_mock
    config_flow._abort_if_unique_id_configured = abort_if_unique_id_configured_mock
    config_flow.async_create_entry = create_entry_mock

    client.wait_for_response = AsyncMock(return_value={"mac_address": "1:2:3:4:5:6"})

    with patch("pyaprilaire.client.AprilaireClient", return_value=client):
        await config_flow.async_step_user(
            {
                "host": "localhost",
                "port": 7000,
            }
        )

    client.start_listen.assert_called_once()
    client.wait_for_response.assert_any_call(FunctionalDomain.CONTROL, 7, 30)
    client.wait_for_response.assert_any_call(FunctionalDomain.SENSORS, 2, 30)
    client.stop_listen.assert_called_once()

    set_unique_id_mock.assert_called_once_with("1:2:3:4:5:6")
    abort_if_unique_id_configured_mock.assert_called_once()

    create_entry_mock.assert_called_once_with(
        title="AprilAire",
        data={
            "host": "localhost",
            "port": 7000,
        },
    )
