"""Versioning & determinism tests (plan v2 E5.1/E5.2, ADR-0022; audit F5/F8)."""
import sys
import json
import pathlib
import subprocess

import yaml

ROOT = pathlib.Path(__file__).resolve().parents[2]


def _versions():
    return yaml.safe_load((ROOT / "schema" / "VERSION.yaml").read_text())


def test_version_source_exists_and_matches_export():
    versions = _versions()
    export = json.loads((ROOT / "exports" / "knowledge.json").read_text())
    assert export["schema_version"] == versions["schema_version"], \
        f"export schema_version != VERSION.yaml ({export['schema_version']} vs {versions['schema_version']})"
    assert export["export_version"] == versions["export_version"], \
        f"export export_version != VERSION.yaml ({export['export_version']} vs {versions['export_version']})"
    print(f"PASS: export versions come from the single source "
          f"(schema {versions['schema_version']}, contract {versions['export_version']})")


def test_no_version_literals_in_exporters():
    for script in ("validate.py", "export_review_aware.py", "graph_analysis.py"):
        src = (ROOT / "scripts" / script).read_text()
        assert '"export_version": "0.1"' not in src and "'export_version': '0.1'" not in src, \
            f"{script} hardcodes export_version (ADR-0022 forbids version literals)"
        assert '"generated_at":' not in src and "'generated_at':" not in src, \
            f"{script} stamps wall-clock generated_at (ADR-0022 requires deterministic content_hash)"
    print("PASS: no version literals or wall-clock stamps in exporters")


def test_export_regeneration_is_byte_identical():
    exports = sorted((ROOT / "exports").glob("*.json"))
    before = {p.name: p.read_bytes() for p in exports}
    for script in ("validate.py", "export_review_aware.py", "graph_analysis.py"):
        r = subprocess.run([sys.executable, str(ROOT / "scripts" / script)], capture_output=True, text=True)
        assert r.returncode == 0, f"{script} failed: {r.stderr[-400:]}"
    after = {p.name: p.read_bytes() for p in exports}
    assert before == after, "regeneration changed derived exports — not deterministic (E5.2)"
    print(f"PASS: full export regeneration is byte-identical ({len(exports)} artifacts)")


def test_content_hash_tracks_canonical_content():
    export = json.loads((ROOT / "exports" / "knowledge.json").read_text())
    assert export.get("content_hash", "").startswith("sha256:"), "export missing deterministic content_hash"
    print(f"PASS: export stamped with deterministic content_hash ({export['content_hash'][:19]}…)")


def test_export_contract_required_members():
    """ADR-0023 / gate G-A: connections + sources are required contract members."""
    import jsonschema
    schema = json.loads((ROOT / "schema" / "export.schema.json").read_text())
    export = json.loads((ROOT / "exports" / "knowledge.json").read_text())
    jsonschema.Draft202012Validator(schema).validate(export)
    assert export["export_version"].startswith("2."), export["export_version"]
    assert export["connection_count"] == len(export["connections"]) > 0
    assert export["source_count"] == len(export["sources"]) > 0
    broken = dict(export); broken.pop("connections")
    errs = list(jsonschema.Draft202012Validator(schema).iter_errors(broken))
    assert errs, "contract must reject an export without connections"
    print(f"PASS: export conforms to contract v{export['export_version']} (connections/sources required)")


def test_export_publishes_relation_registry_and_vocabularies():
    """ADR-0032 / contract v2.1: the export publishes producer-side relation
    semantics + controlled vocabularies so consumers can introspect without
    cloning the producer repo. The relation_registry_version must match the
    single source of truth in schema/VERSION.yaml."""
    import jsonschema

    versions = _versions()
    schema = json.loads((ROOT / "schema" / "export.schema.json").read_text())
    export = json.loads((ROOT / "exports" / "knowledge.json").read_text())

    assert export["export_version"] == versions["export_version"]
    assert export["export_version"] == "2.1.0"

    assert export["relation_registry_version"] == versions["relation_registry_version"]
    registry = export["relation_registry"]
    assert isinstance(registry, dict) and registry
    required = {
        "mathematically_requires",
        "logically_requires",
        "related_to",
        "part_of",
        "applies_to",
    }
    assert required <= set(registry), f"registry missing adopted relations: {required - set(registry)}"
    for name, entry in registry.items():
        for field in ("family", "transitive", "symmetric", "domain", "range", "status"):
            assert field in entry, f"relation_registry[{name!r}] missing {field}"

    vocabularies = export["vocabularies"]
    assert "physics" in vocabularies["domains"]
    assert "mathematics" in vocabularies["domains"]
    assert "mechanics" in vocabularies["subdomains"]["physics"]
    assert "inquiry-observation" in vocabularies["subdomains"]["scientific-practice"]
    assert "classical" in vocabularies["regimes"]

    jsonschema.Draft202012Validator(schema).validate(export)
    print(f"PASS: export contract v{export['export_version']} carries relation registry "
          f"v{export['relation_registry_version']} + controlled vocabularies")


def test_legacy_compat_view_during_co_release_window():
    versions = _versions()
    compat = ROOT / "exports" / "knowledge.compat-0.1.json"
    if versions.get("legacy_export_version"):
        data = json.loads(compat.read_text())
        assert data["export_version"] == versions["legacy_export_version"]
        assert "connections" not in data and data["entity_count"] == len(data["entities"])
        print("PASS: legacy 0.1 compatibility view present for the co-release window")
    else:
        assert not compat.exists(), "legacy_export_version removed but compat artifact still tracked"
        print("PASS: co-release window closed; no compat artifact")


if __name__ == "__main__":
    test_version_source_exists_and_matches_export()
    test_no_version_literals_in_exporters()
    test_export_regeneration_is_byte_identical()
    test_content_hash_tracks_canonical_content()
    test_export_contract_required_members()
    test_legacy_compat_view_during_co_release_window()
    print("ALL DETERMINISTIC EXPORT TESTS PASS")
