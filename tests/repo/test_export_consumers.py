"""Consumer-shaped exports (scripts/export_consumers.py) — release file contract (ADR-0054)."""
from __future__ import annotations

import copy
import json
import pathlib
import subprocess
import sys

import yaml

ROOT = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))
sys.path.insert(0, str(ROOT / "adapters" / "python"))

import export_consumers as ec  # noqa: E402
from stemma_adapter import load_export  # noqa: E402

VERSIONS = yaml.safe_load((ROOT / "schema" / "VERSION.yaml").read_text(encoding="utf-8"))


def _conn(cid: str, source: str, target: str | None, review: str, asserted: str = "human", value=None) -> dict:
    return {
        "id": cid, "type": "connection", "source": source, "relation": "related_to",
        "target": target, "value": value,
        "assertion": {"status": "active", "type": "asserted", "review": {"status": review}},
        "provenance": {"asserted_by": {"type": asserted, "id": f"{asserted}:x"}, "generated_by": "t", "method": "t"},
        "evidence": [],
    }


def _entity(eid: str, status: str, domain: str = "physics") -> dict:
    return {"id": eid, "type": "concept", "name": eid, "domain": domain, "subdomain": "mechanics",
            "status": status, "definition": "d", "provenance": {}, "source_refs": []}


def _base() -> dict:
    return {
        "export_version": VERSIONS["export_version"], "schema_version": VERSIONS["schema_version"],
        "content_hash": "sha256:" + "0" * 64, "source": "test",
        "entities": [_entity("stemma:phys.a", "canonical"), _entity("stemma:phys.b", "human_reviewed"),
                     _entity("stemma:phys.c", "draft"), _entity("stemma:chem.d", "canonical", "chemistry")],
        "connections": [
            _conn("stemma:conn.000001", "stemma:phys.a", "stemma:phys.b", "reviewed", asserted="llm"),
            _conn("stemma:conn.000002", "stemma:phys.a", "stemma:phys.b", "reviewed", asserted="human"),
            _conn("stemma:conn.000003", "stemma:phys.a", "stemma:phys.c", "canonical"),
            _conn("stemma:conn.000004", "stemma:phys.a", None, "canonical",
                  value={"amount": "1", "lowerBound": None, "upperBound": None, "unit": "1"}),
            _conn("stemma:conn.000005", "stemma:phys.a", "stemma:phys.b", "unreviewed"),
        ],
        "sources": [],
    }


def _ids(bundle: dict, key: str) -> list[str]:
    return [x["id"] for x in bundle[key]]


def test_trust_tiers_differ_and_cover_both_axes() -> None:
    base, profile = _base(), {"domains": ["physics"]}
    b = {p: ec.build_consumer_export("t", profile, base, VERSIONS, p) for p in ec.POLICIES}
    assert _ids(b["all"], "entities") == ["stemma:phys.a", "stemma:phys.b", "stemma:phys.c"]
    assert _ids(b["reviewed"], "entities") == ["stemma:phys.a", "stemma:phys.b"]
    assert _ids(b["canonical"], "entities") == ["stemma:phys.a"]
    # connection review axis — trusted drops the LLM-asserted merely-reviewed edge
    assert _ids(b["reviewed"], "connections") == ["stemma:conn.000001", "stemma:conn.000002", "stemma:conn.000004"]
    assert _ids(b["trusted"], "connections") == ["stemma:conn.000002", "stemma:conn.000004"]
    assert _ids(b["canonical"], "connections") == ["stemma:conn.000004"]  # valued claim kept; 000003 loses its draft target
    assert "stemma:conn.000005" in _ids(b["all"], "connections")
    assert b["trusted"]["connections"] != b["reviewed"]["connections"]


def test_bundles_are_valid_exports_and_deterministic() -> None:
    base = _base()
    first = ec.render(ec.build_consumer_export("t", {"domains": "all"}, base, VERSIONS, "all"))
    shuffled = copy.deepcopy(base)
    shuffled["entities"].reverse()
    shuffled["connections"].reverse()
    assert ec.render(ec.build_consumer_export("t", {"domains": "all"}, shuffled, VERSIONS, "all")) == first
    load_export(json.loads(first))  # fail-closed consumer contract


def test_version_mismatch_fails_closed() -> None:
    base = _base()
    base["export_version"] = "2.1.0"
    try:
        ec.build_consumer_export("t", {}, base, {**VERSIONS, "export_version": "2.2.0"})
    except ec.ConsumerExportError as exc:
        assert "export_version" in str(exc)
    else:
        raise AssertionError("stale base export must be refused")


def test_every_registry_consumer_has_a_fresh_committed_bundle() -> None:
    registry = ec.load_registry()
    for cid in registry:
        path = ec.bundle_path(cid)
        assert path.exists(), f"missing {path.relative_to(ROOT)}"
        bundle = json.loads(path.read_text(encoding="utf-8"))
        assert bundle["export_version"] == VERSIONS["export_version"]
        assert bundle["consumer_profile"]["review_policy"] == (registry[cid].get("review_policy") or "all")
        load_export(bundle)
    proc = subprocess.run([sys.executable, str(ROOT / "scripts" / "export_consumers.py"), "--all", "--check"],
                          capture_output=True, text=True)
    assert proc.returncode == 0, proc.stderr
