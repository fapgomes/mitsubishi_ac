"""Climate platform for Mitsubishi AC."""

from __future__ import annotations

import aiohttp

from homeassistant.components.climate import (
    ClimateEntity,
    ClimateEntityFeature,
    HVACMode,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import ATTR_TEMPERATURE, UnitOfTemperature
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import (
    DOMAIN,
    HVAC_TO_MODE,
    MAX_TEMP,
    MIN_TEMP,
    MODE_TO_HVAC,
    SUPPORTED_HVAC_MODES,
    TEMP_STEP,
)
from .coordinator import MitsubishiACCoordinator
from .controller import GroupState


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up climate entities from a config entry."""
    coordinator: MitsubishiACCoordinator = entry.runtime_data
    entities = [
        MitsubishiACClimate(coordinator, group, name)
        for group, name in coordinator.groups.items()
    ]
    async_add_entities(entities)


class MitsubishiACClimate(
    CoordinatorEntity[MitsubishiACCoordinator], ClimateEntity
):
    """Climate entity for a single Mitsubishi AC group."""

    _attr_has_entity_name = True
    _attr_temperature_unit = UnitOfTemperature.CELSIUS
    _attr_supported_features = (
        ClimateEntityFeature.TARGET_TEMPERATURE
        | ClimateEntityFeature.TURN_ON
        | ClimateEntityFeature.TURN_OFF
    )
    _attr_hvac_modes = SUPPORTED_HVAC_MODES
    _attr_min_temp = MIN_TEMP
    _attr_max_temp = MAX_TEMP
    _attr_target_temperature_step = TEMP_STEP
    _enable_turn_on_off_backwards_compat = False

    def __init__(
        self, coordinator: MitsubishiACCoordinator, group: str, name: str
    ) -> None:
        """Initialize the climate entity."""
        super().__init__(coordinator)
        self._group = group
        self._attr_unique_id = f"{DOMAIN}_{group}"
        self._attr_name = name if name else f"AC Group {group}"

    @property
    def _state(self) -> GroupState | None:
        """Get the current state from coordinator data."""
        if self.coordinator.data is None:
            return None
        return self.coordinator.data.get(self._group)

    @property
    def hvac_mode(self) -> HVACMode | None:
        """Return the current HVAC mode."""
        state = self._state
        if state is None:
            return None
        if state.drive == "OFF":
            return HVACMode.OFF
        return MODE_TO_HVAC.get(state.mode, HVACMode.HEAT_COOL)

    @property
    def current_temperature(self) -> float | None:
        """Return the current temperature."""
        state = self._state
        if state is None:
            return None
        return state.inlet_temp

    @property
    def target_temperature(self) -> float | None:
        """Return the target temperature."""
        state = self._state
        if state is None:
            return None
        return state.set_temp

    async def async_set_hvac_mode(self, hvac_mode: HVACMode) -> None:
        """Set the HVAC mode."""
        async with aiohttp.ClientSession() as session:
            if hvac_mode == HVACMode.OFF:
                await self.coordinator.controller.async_set_drive(
                    session, self._group, "OFF"
                )
            else:
                mode = HVAC_TO_MODE.get(hvac_mode)
                if mode is None:
                    return
                # Turn on if currently off, then set mode
                state = self._state
                if state and state.drive == "OFF":
                    await self.coordinator.controller.async_set_drive(
                        session, self._group, "ON"
                    )
                await self.coordinator.controller.async_set_mode(
                    session, self._group, mode
                )
        await self.coordinator.async_request_refresh()

    async def async_set_temperature(self, **kwargs) -> None:
        """Set the target temperature."""
        temperature = kwargs.get(ATTR_TEMPERATURE)
        if temperature is None:
            return
        async with aiohttp.ClientSession() as session:
            await self.coordinator.controller.async_set_temperature(
                session, self._group, temperature
            )
        await self.coordinator.async_request_refresh()

    async def async_turn_on(self) -> None:
        """Turn the AC on."""
        async with aiohttp.ClientSession() as session:
            await self.coordinator.controller.async_set_drive(
                session, self._group, "ON"
            )
        await self.coordinator.async_request_refresh()

    async def async_turn_off(self) -> None:
        """Turn the AC off."""
        async with aiohttp.ClientSession() as session:
            await self.coordinator.controller.async_set_drive(
                session, self._group, "OFF"
            )
        await self.coordinator.async_request_refresh()
