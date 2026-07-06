"""OpenStreetMap-based map-layer provider."""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any, Protocol

from custom_components.map_layer import MapLayerMetadata, TileResponse


class ClientSession(Protocol):
    """Small subset of the aiohttp client session used by this provider."""

    def get(self, url: str, **kwargs: Any) -> Any:
        """Return an async context manager for an HTTP GET request."""


OSM_DARK_PROVIDER_ID = "osm"
OSM_DARK_LAYER_ID = "dark_gray"
OSM_DARK_TITLE = "OpenStreetMap Dark Gray"
OSM_DARK_ATTRIBUTION = "OpenStreetMap contributors; CARTO"
OSM_DARK_SUBDOMAINS = ("a", "b", "c")
OSM_DARK_USER_AGENT = "homeassistant-map-layer-osm/0.0.1"


class OpenStreetMapDarkProvider:
    """Provider for CARTO Dark Matter raster tiles using OpenStreetMap data."""

    provider_id = OSM_DARK_PROVIDER_ID

    def __init__(self, session: ClientSession) -> None:
        """Initialize the provider with a Home Assistant HTTP client session."""

        self._session = session

    async def async_list_layers(self) -> list[MapLayerMetadata]:
        """Return the public dark-gray OpenStreetMap layer metadata."""

        return [
            MapLayerMetadata(
                provider_id=self.provider_id,
                layer_id=OSM_DARK_LAYER_ID,
                title=OSM_DARK_TITLE,
                kind="xyz_tile",
                projection="EPSG:3857",
                tile_scheme="xyz",
                tile_size=256,
                min_zoom=0,
                max_zoom=20,
                max_native_zoom=20,
                attribution=OSM_DARK_ATTRIBUTION,
                content_type="image/png",
            )
        ]

    async def async_get_tile(
        self,
        layer_id: str,
        *,
        z: int,
        x: int,
        y: int,
        dimensions: Mapping[str, Any],
        options: Mapping[str, Any],
    ) -> TileResponse:
        """Fetch one upstream raster tile."""

        if layer_id != OSM_DARK_LAYER_ID:
            return TileResponse(status=404)

        url = osm_dark_tile_url(z=z, x=x, y=y)
        try:
            async with self._session.get(
                url, headers={"User-Agent": OSM_DARK_USER_AGENT}
            ) as response:
                if response.status == 404:
                    return TileResponse(status=204)
                if response.status != 200:
                    return TileResponse(status=502)

                content = await response.read()
                content_type = response.headers.get("Content-Type", "image/png").split(
                    ";", 1
                )[0]
                return TileResponse(
                    content=content,
                    content_type=content_type or "image/png",
                    cache_seconds=300,
                )
        except Exception:
            return TileResponse(status=502)


def osm_dark_tile_url(*, z: int, x: int, y: int) -> str:
    """Return the upstream CARTO Dark Matter tile URL for XYZ coordinates."""

    subdomain = OSM_DARK_SUBDOMAINS[(z + x + y) % len(OSM_DARK_SUBDOMAINS)]
    return f"https://{subdomain}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}.png"

