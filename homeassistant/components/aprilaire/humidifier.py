"""The Aprilaire humidifier component."""

from __future__ import annotations

from typing import Any

from pyaprilaire.const import Attribute

from homeassistant.components.humidifier import (
    HumidifierAction,
    HumidifierDeviceClass,
    HumidifierEntity,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN, MAX_HUMIDITY, MIN_HUMIDITY
from .coordinator import AprilaireCoordinator
from .entity import BaseAprilaireEntity

DEHUMIDIFICATION_STATUS_MAP = {
    0: HumidifierAction.IDLE,
    1: HumidifierAction.IDLE,
    2: HumidifierAction.DRYING,
    3: HumidifierAction.DRYING,
    4: HumidifierAction.OFF,
}

HUMIDIFICATION_STATUS_MAP = {
    0: HumidifierAction.IDLE,
    1: HumidifierAction.IDLE,
    2: HumidifierAction.HUMIDIFYING,
    3: HumidifierAction.OFF,
}


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Add humidifiers for passed config_entry in HA."""

    coordinator: AprilaireCoordinator = hass.data[DOMAIN][config_entry.entry_id]

    if coordinator.data.get(Attribute.HUMIDIFICATION_AVAILABLE) == 2:
        async_add_entities([AprilaireHumidifier(coordinator)])

    if coordinator.data.get(Attribute.DEHUMIDIFICATION_AVAILABLE) == 1:
        async_add_entities([AprilaireDehumidifier(coordinator)])


class BaseAprilaireHumidifier(BaseAprilaireEntity, HumidifierEntity):
    """Base entity for Aprilaire humidifier/dehumidifier."""

    _attr_is_on = True
    _attr_max_humidity = MAX_HUMIDITY
    _attr_min_humidity = MIN_HUMIDITY

    @property
    def current_humidity(self) -> int | None:
        """Get current humidity."""
        return self._coordinator.data.get(
            Attribute.INDOOR_HUMIDITY_CONTROLLING_SENSOR_VALUE
        )

    def turn_on(self, **kwargs: Any) -> None:
        """Ignore requests to turn on the humidifier as this is not controllable."""

    def turn_off(self, **kwargs: Any) -> None:
        """Ignore requests to turn off the humidifier as this is not controllable."""


class AprilaireHumidifier(BaseAprilaireHumidifier):
    """An Aprilaire humidifier."""

    _attr_device_class = HumidifierDeviceClass.HUMIDIFIER
    _attr_name = "Humidifier"

    @property
    def action(self) -> HumidifierAction | None:
        """Return the current action."""

        humidification_status: int | None = self._coordinator.data.get(
            Attribute.HUMIDIFICATION_STATUS
        )

        if humidification_status is None:
            return None

        if humidification_status_value := HUMIDIFICATION_STATUS_MAP.get(
            humidification_status
        ):
            return humidification_status_value

        return None

    @property
    def target_humidity(self) -> int | None:
        """Get current target humidity."""
        return self._coordinator.data.get(Attribute.HUMIDIFICATION_SETPOINT)

    async def async_set_humidity(self, humidity: int) -> None:
        """Set the target humidification setpoint."""

        await self._coordinator.client.set_humidification_setpoint(humidity)


class AprilaireDehumidifier(BaseAprilaireHumidifier):
    """An Aprilaire dehumidifier."""

    _attr_device_class = HumidifierDeviceClass.DEHUMIDIFIER
    _attr_name = "Dehumidifier"

    @property
    def action(self) -> HumidifierAction | None:
        """Return the current action."""

        dehumidification_status: int | None = self._coordinator.data.get(
            Attribute.DEHUMIDIFICATION_STATUS
        )

        if dehumidification_status is None:
            return None

        if dehumidification_status_value := DEHUMIDIFICATION_STATUS_MAP.get(
            dehumidification_status
        ):
            return dehumidification_status_value

        return None

    @property
    def target_humidity(self) -> int | None:
        """Get current target humidity."""
        return self._coordinator.data.get(Attribute.DEHUMIDIFICATION_SETPOINT)

    async def async_set_humidity(self, humidity: int) -> None:
        """Set the target humidification setpoint."""

        await self._coordinator.client.set_dehumidification_setpoint(humidity)
