## DESCRIPTION

*d.osm* fetches OSINT-relevant OpenStreetMap features -- military
installations, checkpoints, power infrastructure, communications towers --
live from the public [Overpass API](https://overpass-api.de/) for the
*current GRASS computational region*, and displays them with pre-baked
GRASS symbols shipped with this addon.

Ten feature types are recognized, each an OpenStreetMap tag:

| type                    | OSM tag                             |
|-------------------------|--------------------------------------|
| military_airfield       | `military=airfield`                  |
| military_base           | `military=base`                      |
| bunker                  | `military=bunker`                    |
| naval_base               | `military=naval_base`                |
| training_area            | `military=training_area`             |
| checkpoint               | `barrier=checkpoint`                 |
| border_control            | `amenity=border_control`             |
| power_plant               | `power=plant`                        |
| substation                 | `power=substation`                   |
| communications_tower        | `man_made=communications_tower`      |

Unlike the *d.osint* addon, *d.osm* has **no local database** -- every run
queries Overpass live for whatever region is currently set with
*g.region* (reprojected to lat/lon automatically, regardless of the
current project's CRS), and nothing is cached between runs. It also has
**no dependency on any other project's code**: only the Python standard
library and `grass.script` are used, and all ten GRASS symbol files are
embedded as static text generated once, ahead of time -- there is no
live SVG-to-symbol conversion step at runtime.

## NOTES

- Query results depend entirely on how thoroughly the current region has
  been mapped in OpenStreetMap -- absence of a symbol on the map is not
  evidence of absence in reality.
- Be considerate of the shared public Overpass endpoint: avoid very large
  regions or tight repeated polling. Use *endpoint=* to point at a
  different Overpass mirror or a self-hosted instance if you need heavier
  use.
- With **format=symbols**, one *d.vect* call is issued per distinct
  feature type present in the result set, so mixed-type results render
  with the correct icon per point.
- If Overpass returns nothing for the current region, an empty vector map
  is still created (so subsequent commands referencing *output=* don't
  fail), and a warning is printed rather than treating "found nothing" as
  an error.

## EXAMPLES

Show every recognized feature type in the current region:

```sh
g.region region=my_area_of_interest
d.mon start=cairo
d.osm
```

Only checkpoints and border crossings, as an attribute table:

```sh
d.osm types=checkpoint,border_control format=attributes
```

Query against a self-hosted Overpass instance:

```sh
d.osm endpoint=http://localhost:12345/api/interpreter
```

## SEE ALSO

*[v.in.ogr](https://grass.osgeo.org/grass-stable/manuals/v.in.ogr.html),
[d.vect](https://grass.osgeo.org/grass-stable/manuals/d.vect.html),
[g.region](https://grass.osgeo.org/grass-stable/manuals/g.region.html)*

The private *d.osint* addon is a related, database-backed companion to
this tool, built for a specific local OSINTDB rather than live queries.

## AUTHORS

Yann Chemin
