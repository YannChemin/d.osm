# d.osm

A [GRASS GIS](https://grass.osgeo.org/) addon that fetches OSINT-relevant
OpenStreetMap features -- military installations, checkpoints, power
infrastructure, communications towers -- live from the public
[Overpass API](https://overpass-api.de/) for the current GRASS
computational region, and displays them with pre-baked GRASS vector
symbols shipped with the addon.

Fully independent and fully open source:

- **No local database.** Every run is a live Overpass query against
  whatever region is currently set with `g.region` (reprojected to
  lat/lon automatically regardless of the project's CRS). Nothing is
  cached between runs.
- **No dependency on any other project's code.** Only the Python
  standard library and `grass.script` are used.
- **No live SVG-to-symbol conversion.** GRASS has no native SVG symbol
  support (see NOTES below), so the ten symbol files under `symbols/`
  were converted once, ahead of time, from SVG icons using the
  standalone, public-domain `svg2grasssymbol` converter, and are embedded
  directly in `d.osm.py` as static text -- there is no runtime
  conversion step at all.

## Recognized feature types

| type                    | OSM tag                          |
|-------------------------|-----------------------------------|
| `military_airfield`     | `military=airfield`               |
| `military_base`         | `military=base`                   |
| `bunker`                 | `military=bunker`                 |
| `naval_base`             | `military=naval_base`             |
| `training_area`          | `military=training_area`          |
| `checkpoint`             | `barrier=checkpoint`              |
| `border_control`          | `amenity=border_control`          |
| `power_plant`             | `power=plant`                     |
| `substation`               | `power=substation`                |
| `communications_tower`      | `man_made=communications_tower`   |

## Usage

```sh
g.region region=my_area_of_interest
d.mon start=cairo
d.osm                                              # every recognized type
d.osm types=checkpoint,border_control              # only these
d.osm format=attributes                            # print attributes, don't render
d.osm endpoint=http://localhost:12345/api/interpreter   # a different Overpass instance
```

See `d.osm.md` (or `d.osm --help` once installed) for the full option
reference.

## Installing

```sh
g.extension extension=d.osm url=/path/to/this/directory
```

installs it into `$GRASS_ADDON_BASE`, picked up automatically by any
GRASS session. See `d.osm.md`'s NOTES section, and the standalone
`svg2grasssymbol` tool's `INSTALL.md`, for background on why custom GRASS
symbols specifically need to land under `$GISBASE/etc/symbol/` (a
different location than the addon script itself) to be usable from
`d.vect icon=` -- `d.osm` handles this automatically the first time each
symbol is needed.

## Testing

```sh
pytest tests/
```

Tests run against a local fake Overpass server (`tests/conftest.py`), not
the live API, so they're deterministic and offline-safe. They do require
a GRASS installation (via `grass.script`/`grass.tools`) to actually run
the addon end-to-end, same as any GRASS addon's test suite.

## Data attribution

This tool's own code is public domain (see LICENSE). The **data** it
fetches at runtime is not: OpenStreetMap data is
[ODbL 1.0](https://www.openstreetmap.org/copyright) licensed. If you
publish maps, reports, or datasets built from `d.osm`'s output, you are
responsible for OpenStreetMap attribution ("© OpenStreetMap
contributors") wherever that data is shown, per ODbL's terms -- this
project's public-domain license covers the *code*, not the *OSM data it
queries*.

## Symbol provenance

The ten bundled GRASS symbols were converted from:

- Five [Mapbox Maki](https://github.com/mapbox/maki) icons (CC0):
  `military_airfield` (airfield), `checkpoint` (roadblock),
  `border_control` (gate), `power_plant` (industry, a generic
  stand-in -- Maki has no dedicated power-plant icon), and
  `communications_tower`.
- Five hand-authored icons with no close Maki match: `military_base`,
  `bunker`, `naval_base`, `training_area`, `substation`.

Both the resulting GRASS symbol files and this project's own code are
released to the public domain (Unlicense) -- see LICENSE.

## Related project

`d.osint` is a related, database-backed addon built for a specific
private local OSINTDB rather than live Overpass queries. Unlike `d.osm`,
it is not intended for public distribution.
