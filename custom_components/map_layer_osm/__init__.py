"""OpenStreetMap-based provider for the Map Layer integration."""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from .provider import OpenStreetMapDarkProvider


async def async_setup(hass: Any, config: Mapping[str, Any]) -> bool:
    """Set up the OpenStreetMap provider package."""

    return True


async def async_setup_entry(hass: Any, entry: Any) -> bool:
    """Register the OpenStreetMap map-layer provider."""

    from custom_components.map_layer import async_get_registry
    from homeassistant.const import CONF_API_KEY
    from homeassistant.exceptions import ConfigEntryAuthFailed
    from homeassistant.helpers.aiohttp_client import async_get_clientsession

    api_key = entry.data.get(CONF_API_KEY, "").strip()
    if not api_key:
        raise ConfigEntryAuthFailed("A CARTO Basemaps API key is now required")

    session = async_get_clientsession(hass)
    unregister = async_get_registry(hass).async_register_provider(
        OpenStreetMapDarkProvider(session, api_key=api_key)
    )
    entry.async_on_unload(unregister)
    return True


async def async_unload_entry(hass: Any, entry: Any) -> bool:
    """Unload the OpenStreetMap provider config entry."""

    return True
