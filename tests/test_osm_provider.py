"""Tests for the OpenStreetMap map-layer provider."""

from __future__ import annotations

import asyncio
import unittest

from custom_components.map_layer_osm.provider import (
    OSM_DARK_ATTRIBUTION,
    OSM_DARK_LAYER_ID,
    OSM_DARK_PROVIDER_ID,
    OpenStreetMapDarkProvider,
    osm_dark_tile_url,
)


class FakeResponse:
    """Async context manager response for provider tests."""

    def __init__(
        self,
        *,
        status: int = 200,
        body: bytes = b"tile",
        content_type: str = "image/png",
    ) -> None:
        self.status = status
        self._body = body
        self.headers = {"Content-Type": content_type}

    async def __aenter__(self) -> "FakeResponse":
        return self

    async def __aexit__(self, exc_type: object, exc: object, tb: object) -> None:
        return None

    async def read(self) -> bytes:
        return self._body


class FakeSession:
    """Fake client session that records requested URLs."""

    def __init__(self, response: FakeResponse) -> None:
        self.response = response
        self.urls: list[str] = []
        self.headers: list[dict[str, str]] = []

    def get(self, url: str, **kwargs: object) -> FakeResponse:
        self.urls.append(url)
        self.headers.append(dict(kwargs.get("headers", {})))
        return self.response


class OpenStreetMapDarkProviderTest(unittest.TestCase):
    """OpenStreetMap provider behavior."""

    def test_metadata_exposes_dark_gray_xyz_layer(self) -> None:
        provider = OpenStreetMapDarkProvider(FakeSession(FakeResponse()))

        layers = asyncio.run(provider.async_list_layers())

        self.assertEqual(len(layers), 1)
        layer = layers[0]
        self.assertEqual(layer.provider_id, OSM_DARK_PROVIDER_ID)
        self.assertEqual(layer.layer_id, OSM_DARK_LAYER_ID)
        self.assertEqual(layer.title, "OpenStreetMap Dark Gray")
        self.assertEqual(layer.kind, "xyz_tile")
        self.assertEqual(layer.projection, "EPSG:3857")
        self.assertEqual(layer.tile_scheme, "xyz")
        self.assertEqual(layer.min_zoom, 0)
        self.assertEqual(layer.max_zoom, 20)
        self.assertEqual(layer.max_native_zoom, 20)
        self.assertEqual(layer.attribution, OSM_DARK_ATTRIBUTION)
        self.assertEqual(layer.content_type, "image/png")
        self.assertIsNone(layer.dimensions)

    def test_fetches_tile_from_cartodb_dark_matter(self) -> None:
        session = FakeSession(FakeResponse(body=b"\x89PNG\r\n\x1a\n"))
        provider = OpenStreetMapDarkProvider(session)

        tile = asyncio.run(
            provider.async_get_tile(
                OSM_DARK_LAYER_ID,
                z=3,
                x=4,
                y=2,
                dimensions={},
                options={},
            )
        )

        self.assertEqual(session.urls, [osm_dark_tile_url(z=3, x=4, y=2)])
        self.assertIn("User-Agent", session.headers[0])
        self.assertEqual(tile.status, 200)
        self.assertEqual(tile.content, b"\x89PNG\r\n\x1a\n")
        self.assertEqual(tile.content_type, "image/png")
        self.assertEqual(tile.cache_seconds, 300)

    def test_upstream_404_returns_empty_tile_response(self) -> None:
        provider = OpenStreetMapDarkProvider(FakeSession(FakeResponse(status=404)))

        tile = asyncio.run(
            provider.async_get_tile(
                OSM_DARK_LAYER_ID,
                z=3,
                x=4,
                y=2,
                dimensions={},
                options={},
            )
        )

        self.assertEqual(tile.status, 204)

    def test_upstream_error_returns_bad_gateway(self) -> None:
        provider = OpenStreetMapDarkProvider(FakeSession(FakeResponse(status=500)))

        tile = asyncio.run(
            provider.async_get_tile(
                OSM_DARK_LAYER_ID,
                z=3,
                x=4,
                y=2,
                dimensions={},
                options={},
            )
        )

        self.assertEqual(tile.status, 502)


class OpenStreetMapDarkUrlTest(unittest.TestCase):
    """URL construction behavior."""

    def test_uses_cartodb_dark_all_xyz_template(self) -> None:
        self.assertEqual(
            osm_dark_tile_url(z=3, x=4, y=2),
            "https://a.basemaps.cartocdn.com/dark_all/3/4/2.png",
        )


if __name__ == "__main__":
    unittest.main()

