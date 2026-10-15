"""Tests for the Aprilaire config flow."""

from unittest.mock import AsyncMock, Mock, patch

from pyaprilaire.client import AprilaireClient, NackError, ResponseTimeoutError
from pyaprilaire.const import Attribute, FunctionalDomain, NackStatus
import pytest

from homeassistant.components.aprilaire.config_flow import (
    STEP_USER_DATA_SCHEMA,
    AprilaireConfigFlow,
)
from homeassistant.components.aprilaire.const import DOMAIN
from homeassistant.config_entries import SOURCE_USER, ConfigEntryDisabler
from homeassistant.const import CONF_HOST, CONF_PORT
from homeassistant.core import HomeAssistant
from homeassistant.data_entry_flow import FlowResultType

from tests.common import MockConfigEntry


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


@pytest.mark.parametrize(
    ("side_effect", "return_value", "log_message"),
    [
        pytest.param(
            ResponseTimeoutError(FunctionalDomain.IDENTIFICATION, 2, 30),
            None,
            "Timed out after 30 seconds waiting for the MAC address",
            id="timeout",
        ),
        pytest.param(
            NackError(NackStatus.GENERIC_ERROR, NackStatus.GENERIC_ERROR.value),
            None,
            "Thermostat rejected the MAC address request: Request was NACKed"
            " with status GENERIC_ERROR (0x01)",
            id="nack",
        ),
        pytest.param(
            None,
            {},
            "MAC address missing from the thermostat response",
            id="missing",
        ),
    ],
)
async def test_config_flow_invalid_data(
    client: AprilaireClient,
    caplog: pytest.LogCaptureFixture,
    side_effect: Exception | None,
    return_value: dict[str, str] | None,
    log_message: str,
) -> None:
    """Test that the flow shows an error when the MAC address can't be read."""

    client.read_mac_address_and_wait.side_effect = side_effect
    client.read_mac_address_and_wait.return_value = return_value

    show_form_mock = Mock()
    set_unique_id_mock = AsyncMock()
    async_abort_entries_match_mock = Mock()

    config_flow = AprilaireConfigFlow()
    config_flow.async_show_form = show_form_mock
    config_flow.async_set_unique_id = set_unique_id_mock
    config_flow._async_abort_entries_match = async_abort_entries_match_mock

    with patch("pyaprilaire.client.AprilaireClient", return_value=client):
        await config_flow.async_step_user(
            {
                "host": "localhost",
                "port": 7000,
            }
        )

    client.start_listen.assert_called_once()
    client.read_mac_address_and_wait.assert_called_once_with(30)
    client.read_thermostat_iaq_available_and_wait.assert_not_called()
    client.stop_listen.assert_called_once()
    assert log_message in caplog.text

    show_form_mock.assert_called_once_with(
        step_id="user",
        data_schema=STEP_USER_DATA_SCHEMA,
        errors={"base": "connection_failed"},
    )


async def test_config_flow_data(client: AprilaireClient, hass: HomeAssistant) -> None:
    """Test the config flow with valid data."""

    client.data = {"mac_address": "01:02:03:04:05:06"}

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

    client.read_mac_address_and_wait.return_value = {"mac_address": "01:02:03:04:05:06"}

    with patch("pyaprilaire.client.AprilaireClient", return_value=client):
        await config_flow.async_step_user(
            {
                "host": "localhost",
                "port": 7000,
            }
        )

    client.start_listen.assert_called_once()
    client.read_mac_address_and_wait.assert_not_called()
    client.read_thermostat_iaq_available_and_wait.assert_called_once_with(30)
    client.read_sensors_and_wait.assert_called_once_with(30)
    client.stop_listen.assert_called_once()

    set_unique_id_mock.assert_called_once_with("01:02:03:04:05:06")
    abort_if_unique_id_configured_mock.assert_called_once()

    create_entry_mock.assert_called_once_with(
        title="AprilAire",
        data={
            "host": "localhost",
            "port": 7000,
        },
    )


async def test_config_flow_optional_reads_fail(
    client: AprilaireClient, hass: HomeAssistant
) -> None:
    """Test the flow still succeeds when reads other than the MAC address fail."""

    create_entry_mock = Mock()

    config_flow = AprilaireConfigFlow()
    config_flow.hass = hass
    config_flow.async_set_unique_id = AsyncMock()
    config_flow._abort_if_unique_id_configured = Mock()
    config_flow.async_create_entry = create_entry_mock

    client.data = {"mac_address": "01:02:03:04:05:06"}
    client.read_mac_address_and_wait.return_value = {"mac_address": "01:02:03:04:05:06"}
    client.read_thermostat_iaq_available_and_wait.side_effect = ResponseTimeoutError(
        FunctionalDomain.CONTROL, 7, 30
    )
    client.read_sensors_and_wait.side_effect = NackError(
        NackStatus.GENERIC_ERROR, NackStatus.GENERIC_ERROR.value
    )

    with patch("pyaprilaire.client.AprilaireClient", return_value=client):
        await config_flow.async_step_user({"host": "localhost", "port": 7000})

    client.read_thermostat_status.assert_called_once()
    client.read_iaq_status.assert_called_once()
    create_entry_mock.assert_called_once()


async def test_config_flow_unmigrated_entry(
    hass: HomeAssistant, client: AprilaireClient
) -> None:
    """Test the flow aborts for a disabled entry with an unpadded MAC address."""

    MockConfigEntry(
        domain=DOMAIN,
        unique_id="b4:82:55:0:1a:5",
        data={CONF_HOST: "localhost", CONF_PORT: 7000},
        minor_version=1,
        disabled_by=ConfigEntryDisabler.USER,
    ).add_to_hass(hass)

    client.data = {Attribute.MAC_ADDRESS: "b4:82:55:00:1a:05"}

    result = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": SOURCE_USER}
    )

    with patch("pyaprilaire.client.AprilaireClient", return_value=client):
        result = await hass.config_entries.flow.async_configure(
            result["flow_id"], {CONF_HOST: "localhost", CONF_PORT: 7000}
        )

    assert result["type"] is FlowResultType.ABORT
    assert result["reason"] == "already_configured"
