"""Tests for the d.osm addon (against a local fake Overpass server, see
conftest.py -- no live network access needed)."""

import os

from PIL import Image


def test_imports_all_matching_types_by_default(osm_env):
    tools = osm_env.tools
    tools.d_osm(endpoint=osm_env.endpoint, output="out1", format="attributes")

    info = tools.v_info(map="out1", flags="t", format="json")
    # 4 of the 5 fake elements match a known tag; the shop=bakery one must not.
    assert info["points"] == 4


def test_types_filter_restricts_results(osm_env):
    tools = osm_env.tools
    tools.d_osm(endpoint=osm_env.endpoint, types="checkpoint", output="out2", format="attributes")

    info = tools.v_info(map="out2", flags="t", format="json")
    assert info["points"] == 2

    rows = tools.v_db_select(map="out2", columns="symbol", flags="c").text.strip().splitlines()
    assert set(rows) == {"checkpoint"}


def test_unmatched_type_filter_yields_empty_map_not_an_error(osm_env):
    """bunker never appears in the fake Overpass fixture data -- this must
    not raise, just produce an empty (but valid) vector map."""
    tools = osm_env.tools
    tools.d_osm(endpoint=osm_env.endpoint, types="bunker", output="out3", format="attributes")

    info = tools.v_info(map="out3", flags="t", format="json")
    assert info["points"] == 0


def test_format_symbols_installs_bundled_symbol_and_composites(osm_env):
    """Confirms two things at once: (1) symbols are installed from the
    embedded static text (no network beyond the Overpass call itself),
    and (2) the GRASS_RENDER_FILE_READ compositing fix (carried over from
    the d.osint bug -- see AI_README.md section 6) actually works here
    too, by checking both feature types show up in the final render."""
    tools = osm_env.tools
    tools.d_osm(endpoint=osm_env.endpoint, types="military_airfield,checkpoint", output="out4")

    installed = os.path.join(osm_env.gisbase, "etc", "symbol", "osm", "military_airfield")
    assert os.path.exists(installed)

    img = Image.open(osm_env.render_file).convert("RGB")

    def screen_xy(lon, lat):
        x = int((lon - 2.32) / (2.40 - 2.32) * 400)
        y = int((48.90 - lat) / (48.90 - 48.83) * 400)
        return x, y

    def has_nonwhite_pixel_near(lon, lat, radius=12):
        cx, cy = screen_xy(lon, lat)
        for dx in range(-radius, radius + 1):
            for dy in range(-radius, radius + 1):
                x, y = cx + dx, cy + dy
                if 0 <= x < img.width and 0 <= y < img.height:
                    if img.getpixel((x, y)) != (255, 255, 255):
                        return True
        return False

    assert has_nonwhite_pixel_near(2.35, 48.85), "airfield icon missing from composited render"
    assert has_nonwhite_pixel_near(2.36, 48.86), "checkpoint icon missing from composited render"
