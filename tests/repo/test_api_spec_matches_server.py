"""schema/api.yaml must describe exactly the routes the adapter serves (ADR-0054).

The docs gate (scripts/docs.py api_surface) keeps spec -> docs in sync; this
test closes the other gap: server -> spec. It reads the dispatch literals in
adapters/python/stemma_adapter/server.py (``path == "..."`` and
``path.startswith("...")``) and compares them with the OpenAPI paths.
"""
from __future__ import annotations

import pathlib
import re

import yaml

ROOT = pathlib.Path(__file__).resolve().parents[2]
SERVER = ROOT / "adapters" / "python" / "stemma_adapter" / "server.py"
SPEC = ROOT / "schema" / "api.yaml"


def _server_routes() -> tuple[set[str], set[str]]:
    src = SERVER.read_text(encoding="utf-8")
    exact = set(re.findall(r'path == "(/[^"]*)"', src)) - {"/"}  # "/" = index document
    prefixes = set(re.findall(r'path\.startswith\("(/[^"]*)"\)', src))
    return exact, prefixes


def _spec_paths() -> set[str]:
    return set((yaml.safe_load(SPEC.read_text(encoding="utf-8")) or {}).get("paths") or {})


def test_every_served_route_is_specified() -> None:
    exact, prefixes = _server_routes()
    spec = _spec_paths()
    templated_prefixes = {p.split("{", 1)[0] for p in spec if "{" in p}
    missing = sorted(r for r in exact if r not in spec)
    missing += sorted(f"{p}{{...}}" for p in prefixes if p not in templated_prefixes)
    assert not missing, f"adapter serves routes absent from schema/api.yaml: {missing}"


def test_every_specified_path_is_served() -> None:
    exact, prefixes = _server_routes()
    phantom = []
    for path in sorted(_spec_paths()):
        if "{" in path:
            if path.split("{", 1)[0] not in prefixes:
                phantom.append(path)
        elif path not in exact:
            phantom.append(path)
    assert not phantom, f"schema/api.yaml documents routes the adapter does not serve: {phantom}"


def test_spec_does_not_claim_webapp_or_hosted_surface() -> None:
    spec = yaml.safe_load(SPEC.read_text(encoding="utf-8"))
    assert not [p for p in spec["paths"] if p.startswith("/api/")], "webapp /api/* is not a consumer API (ADR-0054)"
    for server in spec.get("servers", []):
        assert "example.com" not in server["url"], "no hosted endpoint exists in this phase (ADR-0054)"
