"""Fixtures for the d.osm tests.

Since d.osm queries the live public Overpass API, tests use a tiny local
HTTP server that mimics Overpass's request/response shape instead of
hitting the real network -- deterministic, offline-safe, and still
exercises the actual urllib request/response code path (not a mock of
the function itself).
"""

import json
import os
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer
from types import SimpleNamespace

import pytest

import grass.script as gs
from grass.experimental import TemporaryMapsetSession
from grass.tools import Tools

# A handful of node elements covering three feature types, positioned
# inside the test region set up below (n=48.90 s=48.83 e=2.40 w=2.32).
_FAKE_ELEMENTS = [
    {"type": "node", "id": 1, "lat": 48.85, "lon": 2.35, "tags": {"military": "airfield", "name": "Test Airfield"}},
    {"type": "node", "id": 2, "lat": 48.86, "lon": 2.36, "tags": {"barrier": "checkpoint"}},
    {"type": "node", "id": 3, "lat": 48.87, "lon": 2.37, "tags": {"barrier": "checkpoint"}},
    {"type": "way", "id": 4, "center": {"lat": 48.855, "lon": 2.355}, "tags": {"power": "substation"}},
    # Deliberately unmatched tag -- must be classified out, never imported.
    {"type": "node", "id": 5, "lat": 48.858, "lon": 2.358, "tags": {"shop": "bakery"}},
]


class _FakeOverpassHandler(BaseHTTPRequestHandler):
    def do_POST(self):
        length = int(self.headers.get("Content-Length", 0))
        self.rfile.read(length)  # drain the request body (the QL query)
        body = json.dumps({"elements": _FAKE_ELEMENTS}).encode("utf-8")
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, *args):
        pass  # keep test output quiet


@pytest.fixture(scope="module")
def fake_overpass_url():
    server = HTTPServer(("127.0.0.1", 0), _FakeOverpassHandler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    yield f"http://127.0.0.1:{server.server_port}/api/interpreter"
    server.shutdown()
    thread.join()


@pytest.fixture(scope="module")
def base_session(tmp_path_factory):
    project = tmp_path_factory.mktemp("d_osm") / "project"
    gs.create_project(project, epsg="4326")
    with gs.setup.init(project, env=os.environ.copy()) as session:
        yield session


@pytest.fixture
def osm_env(base_session, fake_overpass_url, tmp_path):
    render_file = str(tmp_path / "render.png")
    with TemporaryMapsetSession(env=base_session.env) as session:
        session.env["GRASS_RENDER_IMMEDIATE"] = "cairo"
        session.env["GRASS_RENDER_FILE"] = render_file
        session.env["GRASS_RENDER_WIDTH"] = "400"
        session.env["GRASS_RENDER_HEIGHT"] = "400"
        session.env["GRASS_RENDER_BACKGROUNDCOLOR"] = "FFFFFF"
        with Tools(session=session) as tools:
            tools.g_region(n=48.90, s=48.83, e=2.40, w=2.32)
            yield SimpleNamespace(
                tools=tools,
                endpoint=fake_overpass_url,
                gisbase=session.env["GISBASE"],
                render_file=render_file,
            )
