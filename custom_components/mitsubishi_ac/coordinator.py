"""DataUpdateCoordinator for Mitsubishi AC."""

from __future__ import annotations

from datetime import timedelta
import logging

import aiohttp

from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .const import DOMAIN, SCAN_INTERVAL_SECONDS
from .controller import GroupState, MitsubishiACController

_LOGGER = logging.getLogger(__name__)


class MitsubishiACCoordinator(DataUpdateCoordinator[dict[str, GroupState]]):
    """Coordinator that polls all AC groups."""

    def __init__(
        self,
        hass: HomeAssistant,
        controller: MitsubishiACController,
        groups: dict[str, str],
    ) -> None:
        """Initialize the coordinator.

        groups is a dict of group_number -> group_name.
        """
        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=timedelta(seconds=SCAN_INTERVAL_SECONDS),
        )
        self.controller = controller
        self.groups = groups

    async def _async_update_data(self) -> dict[str, GroupState]:
        """Fetch state for all groups."""
        data: dict[str, GroupState] = {}
        try:
            async with aiohttp.ClientSession() as session:
                for group in self.groups:
                    state = await self.controller.async_get_group_state(
                        session, group
                    )
                    data[group] = state
        except (aiohttp.ClientError, TimeoutError) as err:
            raise UpdateFailed(f"Error communicating with controller: {err}") from err
        return data
