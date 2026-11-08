"""API-key setup, migration and reconfiguration tests using Home Assistant."""

from __future__ import annotations

import unittest
from unittest.mock import MagicMock, patch

try:
    from homeassistant.const import CONF_API_KEY
    from homeassistant.exceptions import ConfigEntryAuthFailed

    from custom_components.map_layer_osm.config_flow import ConfigFlow
except ModuleNotFoundError as exc:
    if exc.name != "homeassistant":
        raise
    raise unittest.SkipTest("Install Home Assistant to run config-flow tests") from exc

from custom_components.map_layer_osm import async_setup_entry


class ConfigFlowTest(unittest.IsolatedAsyncioTestCase):
    """Exercise the real flow methods without making external tile requests."""

    async def asyncSetUp(self) -> None:
        self.flow = ConfigFlow()
        self.flow.hass = MagicMock()

    async def test_user_form_masks_key_and_rejects_blank_input(self) -> None:
        with patch.object(self.flow, "_async_current_entries", return_value=[]):
            result = await self.flow.async_step_user()
            self.assertEqual(result["step_id"], "user")
            selector = result["data_schema"].schema[CONF_API_KEY]
            self.assertEqual(selector.config["type"], "password")
            result = await self.flow.async_step_user({CONF_API_KEY: "  "})
        self.assertEqual(result["errors"], {CONF_API_KEY: "api_key_required"})

    async def test_user_saves_key_without_whitespace(self) -> None:
        with (
            patch.object(self.flow, "_async_current_entries", return_value=[]),
            patch.object(self.flow, "async_create_entry", return_value={}) as create,
        ):
            await self.flow.async_step_user({CONF_API_KEY: " test-key "})
        create.assert_called_once_with(
            title="Map Layer OpenStreetMap", data={CONF_API_KEY: "test-key"}
        )

    async def test_duplicate_setup_aborts(self) -> None:
        with patch.object(self.flow, "_async_current_entries", return_value=[object()]):
            result = await self.flow.async_step_user()
        self.assertEqual(result["reason"], "single_instance_allowed")

    async def test_reauth_prompts_then_updates_existing_entry(self) -> None:
        result = await self.flow.async_step_reauth({})
        self.assertEqual(result["step_id"], "reauth_confirm")
        entry = MagicMock()
        with (
            patch.object(self.flow, "_get_reauth_entry", return_value=entry),
            patch.object(
                self.flow, "async_update_reload_and_abort", return_value={}
            ) as update,
        ):
            await self.flow.async_step_reauth_confirm({CONF_API_KEY: "replacement"})
        update.assert_called_once_with(
            entry,
            data_updates={CONF_API_KEY: "replacement"},
            reason="reauth_successful",
        )

    async def test_reconfigure_updates_existing_entry(self) -> None:
        result = await self.flow.async_step_reconfigure()
        self.assertEqual(result["step_id"], "reconfigure")
        entry = MagicMock()
        with (
            patch.object(self.flow, "_get_reconfigure_entry", return_value=entry),
            patch.object(
                self.flow, "async_update_reload_and_abort", return_value={}
            ) as update,
        ):
            await self.flow.async_step_reconfigure({CONF_API_KEY: "replacement"})
        update.assert_called_once_with(
            entry,
            data_updates={CONF_API_KEY: "replacement"},
            reason="reconfigure_successful",
        )

    async def test_old_entry_without_key_requests_reauthentication(self) -> None:
        entry = MagicMock()
        entry.data = {}
        with self.assertRaises(ConfigEntryAuthFailed):
            await async_setup_entry(MagicMock(), entry)

    async def test_setup_passes_key_to_provider(self) -> None:
        entry = MagicMock()
        entry.data = {CONF_API_KEY: "test-key"}
        session = MagicMock()
        registry = MagicMock()
        with (
            patch(
                "homeassistant.helpers.aiohttp_client.async_get_clientsession",
                return_value=session,
            ),
            patch(
                "custom_components.map_layer.async_get_registry", return_value=registry
            ),
            patch(
                "custom_components.map_layer_osm.OpenStreetMapDarkProvider"
            ) as provider,
        ):
            self.assertTrue(await async_setup_entry(MagicMock(), entry))
        provider.assert_called_once_with(session, api_key="test-key")
        registry.async_register_provider.assert_called_once_with(provider.return_value)
        entry.async_on_unload.assert_called_once_with(
            registry.async_register_provider.return_value
        )
