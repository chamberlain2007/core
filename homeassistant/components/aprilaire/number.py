"""The Aprilaire number component."""

from __future__ import annotations

from collections.abc import Awaitable, Callable
from dataclasses import dataclass

from pyaprilaire.const import Attribute

from homeassistant.components.number import NumberEntity, NumberEntityDescription
from homeassistant.const import UnitOfTemperature
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .coordinator import AprilaireConfigEntry, AprilaireCoordinator
from .entity import BaseAprilaireEntity


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: AprilaireConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Aprilaire number devices."""

    coordinator = config_entry.runtime_data

    assert config_entry.unique_id is not None

    descriptions: list[AprilaireNumberDescription] = [
        AprilaireNumberDescription(
            key="written_outdoor_temperature_value",
            translation_key="written_outdoor_temperature_value",
            native_value_key=Attribute.OUTDOOR_SENSOR,
            set_native_value_fn=coordinator.client.set_written_outdoor_temperature_value,
            native_min_value=-40,
            native_max_value=55,
            native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        )
    ]

    async_add_entities(
        AprilaireNumberEntity(coordinator, description, config_entry.unique_id)
        for description in descriptions
    )


@dataclass(frozen=True, kw_only=True)
class AprilaireNumberDescription(NumberEntityDescription):
    """Class describing Aprilaire number entities."""

    native_value_key: str
    set_native_value_fn: Callable[[float], Awaitable]


class AprilaireNumberEntity(BaseAprilaireEntity, NumberEntity):
    """Base number entity for Aprilaire."""

    entity_description: AprilaireNumberDescription

    def __init__(
        self,
        coordinator: AprilaireCoordinator,
        description: AprilaireNumberDescription,
        unique_id: str,
    ) -> None:
        """Initialize a number for an Aprilaire device."""

        self.entity_description = description

        super().__init__(coordinator, unique_id)

    @property
    def native_value(self) -> float | None:
        """Get the native value."""

        current_value = self.coordinator.data.get(
            self.entity_description.native_value_key
        )

        if current_value is None:
            return None

        return float(current_value)

    async def async_set_native_value(self, value: float) -> None:
        """Set the native value."""

        await self.entity_description.set_native_value_fn(value)
