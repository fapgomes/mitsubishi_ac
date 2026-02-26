"""Config flow for Mitsubishi AC."""

from __future__ import annotations

import logging
from typing import Any

import aiohttp
import voluptuous as vol

from homeassistant.config_entries import ConfigFlow, ConfigFlowResult
from homeassistant.const import CONF_HOST

from .const import DOMAIN
from .controller import MitsubishiACController

_LOGGER = logging.getLogger(__name__)

STEP_USER_DATA_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_HOST): str,
    }
)


class MitsubishiACConfigFlow(ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Mitsubishi AC."""

    VERSION = 1

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Handle the initial step."""
        errors: dict[str, str] = {}

        if user_input is not None:
            host = user_input[CONF_HOST]

            await self.async_set_unique_id(host)
            self._abort_if_unique_id_configured()

            controller = MitsubishiACController(host)
            try:
                async with aiohttp.ClientSession() as session:
                    groups = await controller.async_discover_groups(session)
            except (aiohttp.ClientError, TimeoutError):
                errors["base"] = "cannot_connect"
            except Exception:
                _LOGGER.exception("Unexpected error")
                errors["base"] = "unknown"
            else:
                if not groups:
                    errors["base"] = "no_groups"
                else:
                    groups_data = {
                        g.group: g.name for g in groups
                    }
                    return self.async_create_entry(
                        title=f"Mitsubishi AC ({host})",
                        data={CONF_HOST: host, "groups": groups_data},
                    )

        return self.async_show_form(
            step_id="user",
            data_schema=STEP_USER_DATA_SCHEMA,
            errors=errors,
        )
