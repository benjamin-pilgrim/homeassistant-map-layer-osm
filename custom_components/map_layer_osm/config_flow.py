"""Config flow for the OpenStreetMap map-layer provider."""

from __future__ import annotations

from typing import Any

import voluptuous as vol
from homeassistant import config_entries
from homeassistant.const import CONF_API_KEY
from homeassistant.helpers import selector

from .const import DOMAIN


class ConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Configure the server-side CARTO Basemaps API key."""

    VERSION = 1

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> config_entries.ConfigFlowResult:
        """Create the single OpenStreetMap-provider config entry."""
        if self._async_current_entries():
            return self.async_abort(reason="single_instance_allowed")
        return await self._async_key_step("user", user_input)

    async def async_step_reauth(
        self, entry_data: dict[str, Any]
    ) -> config_entries.ConfigFlowResult:
        """Request a key for an existing installation without one."""
        return await self.async_step_reauth_confirm()

    async def async_step_reauth_confirm(
        self, user_input: dict[str, Any] | None = None
    ) -> config_entries.ConfigFlowResult:
        """Save the key without replacing the existing config entry."""
        return await self._async_key_step("reauth_confirm", user_input)

    async def async_step_reconfigure(
        self, user_input: dict[str, Any] | None = None
    ) -> config_entries.ConfigFlowResult:
        """Allow replacing a revoked or expired key."""
        return await self._async_key_step("reconfigure", user_input)

    async def _async_key_step(
        self, step_id: str, user_input: dict[str, Any] | None
    ) -> config_entries.ConfigFlowResult:
        errors = {}
        if user_input is not None:
            api_key = user_input.get(CONF_API_KEY, "").strip()
            if api_key:
                data = {CONF_API_KEY: api_key}
                if step_id == "user":
                    return self.async_create_entry(
                        title="Map Layer OpenStreetMap", data=data
                    )
                entry = (
                    self._get_reauth_entry()
                    if step_id == "reauth_confirm"
                    else self._get_reconfigure_entry()
                )
                return self.async_update_reload_and_abort(
                    entry,
                    data_updates=data,
                    reason=(
                        "reauth_successful"
                        if step_id == "reauth_confirm"
                        else "reconfigure_successful"
                    ),
                )
            errors[CONF_API_KEY] = "api_key_required"

        return self.async_show_form(
            step_id=step_id,
            data_schema=vol.Schema(
                {
                    vol.Required(CONF_API_KEY): selector.TextSelector(
                        selector.TextSelectorConfig(
                            type=selector.TextSelectorType.PASSWORD
                        )
                    ),
                }
            ),
            errors=errors,
        )
