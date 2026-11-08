# Map Layer OpenStreetMap

Home Assistant custom integration that registers an OpenStreetMap-based
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
5. Get a [CARTO Basemaps API key](https://www.carto.com/basemaps/apikey/).
6. Add `Map Layer OpenStreetMap` from Settings > Devices & services and enter
   the key.

## Existing installations

CARTO now requires an API key. Without one, its tiles display “API KEY REQUIRED”.
After updating and restarting Home Assistant, an existing installation without
a key will ask you to reauthenticate. Enter the key there. To replace a key later,
use **Reconfigure** on the integration. No dashboard changes are needed: the layer
remains `osm/dark_gray`.

The key is stored in the integration config entry and added only to server-side
requests to CARTO. Do not put it in dashboard YAML or frontend tile URLs.

## Development

Run tests with the core map-layer repo on `PYTHONPATH`:

```sh
PYTHONPATH=/path/to/homeassistant-map-layer:/path/to/homeassistant-map-layer-osm \
  python -m unittest discover -s tests
```

To include config-flow and setup tests against Home Assistant:

```sh
PYTHONPATH=../homeassistant-map-layer:. \
  uv run --with homeassistant python -m unittest discover -s tests
```
