# Map Layer OpenStreetMap

Home Assistant custom integration that registers a public OpenStreetMap-based
XYZ raster layer with the generic `map_layer` integration.

This provider exposes CARTO Dark Matter tiles using OpenStreetMap data through
the `map_layer` tile proxy. It does not store private coordinates, dashboard
configuration, provider secrets, or upstream URLs in client-visible tokens.

## Installation

1. Install the `Map Layer` integration first.
2. In HACS, add this repository as a custom repository with category
   `Integration`.
3. Install `Map Layer OpenStreetMap`.
4. Restart Home Assistant.
5. Add `Map Layer OpenStreetMap` from Settings > Devices & services.

## Development

Run tests with the core map-layer repo on `PYTHONPATH`:

```sh
PYTHONPATH=/path/to/homeassistant-map-layer:/path/to/homeassistant-map-layer-osm \
  python -m unittest discover -s tests
```
