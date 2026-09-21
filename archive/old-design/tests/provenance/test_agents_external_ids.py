"""Identity & provenance hardening tests (plan v2 E4.1/E4.2; ADR-0023; audit F2/F6)."""
import pathlib
import re
import subprocess
import sys

import yaml

ROOT = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))
import validate as v  # noqa: E402

AGENT_RE = re.compile(r"\b(human|process|llm|unknown):[A-Za-z0-9][A-Za-z0-9._/@-]*")


def _agents():
    return yaml.safe_load((ROOT / "schema" / "agent-registry.yaml").read_text())["agents"]


def test_agent_registry_well_formed():
    ids = [a["id"] for a in _agents()]
    assert len(ids) == len(set(ids)), "duplicate agent ids"
    for a in _agents():
        assert a["class"] == a["id"].split(":")[0], a
        assert a["status"] in ("active", "retired", "test"), a
        assert a.get("display_name"), a
    print(f"PASS: agent registry well-formed ({len(ids)} agents)")


def test_every_canonical_agent_reference_resolves():
    known = {a["id"] for a in _agents()}
    used = set()
    for p in list((ROOT / "connections").glob("*.yaml")) + list((ROOT / "content").rglob("*.md")):
        used.update(m.group(0) for m in AGENT_RE.finditer(p.read_text(encoding="utf-8")))
    for e in yaml.safe_load((ROOT / "schema" / "extension-registry.yaml").read_text())["extensions"]:
        used.add(e["registered_by"])
    missing = sorted(used - known)
    assert not missing, f"agent ids used in canonical files but unregistered: {missing}"
    print(f"PASS: all {len(used)} referenced agent ids resolve in schema/agent-registry.yaml")


def test_validator_rejects_unregistered_agent():
    errors = []
    conn = {"_file": "x", "provenance": {
        "asserted_by": {"type": "human", "id": "human:nobody"},
        "generated_by": {"type": "process", "id": "process:migration.relationships-v0.2"},
        "method": {"type": "manual"}}}
    v.check_connection_agents(conn, v.load_agent_registry(), errors)
    assert any("human:nobody" in e for e in errors), errors
    print("PASS: validator rejects an unregistered agent id")


def test_validator_rejects_unknown_agent_on_new_assertion():
    errors = []
    conn = {"_file": "x", "provenance": {
        "asserted_by": {"type": "unknown", "id": "unknown:legacy-relationship"},
        "generated_by": {"type": "human", "id": "human:curator.001"},
        "method": {"type": "manual"}}}
    v.check_connection_agents(conn, v.load_agent_registry(), errors)
    assert any("unknown: agent" in e for e in errors), errors
    print("PASS: non-migrated assertion cannot be attributed to unknown:")


def test_validator_rejects_type_prefix_mismatch():
    errors = []
    conn = {"_file": "x", "provenance": {
        "asserted_by": {"type": "llm", "id": "human:curator.001"},
        "generated_by": {"type": "human", "id": "human:curator.001"},
        "method": {"type": "manual"}}}
    v.check_connection_agents(conn, v.load_agent_registry(), errors)
    assert any("prefix != type" in e for e in errors), errors
    print("PASS: agent id prefix must match declared type")


def test_external_ids_format_checks():
    errors = []
    v.check_external_ids({"external_ids": {"wd": "Q11402", "orcid": "0000-0002-1825-0097"}}, errors, "ok:")
    assert not errors, errors
    v.check_external_ids({"external_ids": {"wd": "11402"}}, errors, "bad:")
    v.check_external_ids({"external_ids": {"wd": ["Q1", "Q1"]}}, errors, "dup:")
    v.check_external_ids({"external_ids": {"doi": "not-a-doi"}}, errors, "doi:")
    assert len(errors) == 3, errors
    print("PASS: external_ids format checks (wd/orcid/doi/dup)")


# Entities deliberately left without a QID because no faithful Wikidata item exists
# (a wrong anchor is worse than none). Re-check when Wikidata gains an item.
NO_FAITHFUL_WIKIDATA_ITEM = {
    "stemma:phys.equations-of-motion",  # constant-acceleration (SUVAT) set; Q215007 is the general ODE sense
}


def test_mechanics_batch_seeded_with_wikidata():
    missing = []
    for p in sorted((ROOT / "content" / "physics" / "mechanics").glob("*.md")):
        d = yaml.safe_load(p.read_text().split("---", 2)[1])
        wd = (d.get("external_ids") or {}).get("wd")
        if not wd and d["id"] not in NO_FAITHFUL_WIKIDATA_ITEM:
            missing.append(d["id"])
    assert not missing, f"mechanics entities without wd external id: {missing}"
    print("PASS: every mechanics entity carries a Wikidata QID (E4.1 seed)")


def test_no_hardcoded_export_version_in_contract_docs():
    """Consumer-facing docs must not claim a stale contract version."""
    versions = yaml.safe_load((ROOT / "schema" / "VERSION.yaml").read_text())
    seam = (ROOT / "docs" / "CONSUMERS.md").read_text()
    assert f"export_version: {versions['export_version']}" in seam, \
        "docs/CONSUMERS.md does not state the current export_version"
    print(f"PASS: consumer seam documents export_version {versions['export_version']}")


def test_campaign_generator_is_deterministic_and_readonly():
    before = {p: p.read_bytes() for p in (ROOT / "connections").glob("*.yaml")}
    r = subprocess.run([sys.executable, str(ROOT / "scripts" / "dependency_review_campaign.py")], capture_output=True, text=True)
    assert r.returncode == 0, r.stderr
    out = ROOT / "reports" / "dependency-review-campaign"
    first = {p.name: p.read_bytes() for p in out.iterdir()}
    r = subprocess.run([sys.executable, str(ROOT / "scripts" / "dependency_review_campaign.py")], capture_output=True, text=True)
    second = {p.name: p.read_bytes() for p in out.iterdir()}
    assert first == second, "campaign worksheets are not deterministic"
    after = {p: p.read_bytes() for p in (ROOT / "connections").glob("*.yaml")}
    assert before == after, "campaign generator modified canonical connections"
    print("PASS: E6.1 campaign generator is deterministic and never touches connections/")


def test_apply_decisions_refuses_non_human_reviewer():
    try:
        sheet = next((ROOT / "reports" / "dependency-review-campaign").glob("batch-01.yaml"))
    except StopIteration:
        print("SKIP: apply_review_decisions test (campaign file batch-01.yaml not found - empty knowledge base)")
        return
    r = subprocess.run([sys.executable, str(ROOT / "scripts" / "apply_review_decisions.py"), str(sheet),
                        "--reviewer", "process:e61.dependency-campaign", "--dry-run"], capture_output=True, text=True)
    assert r.returncode == 2, r.stdout + r.stderr
    print("PASS: apply_review_decisions refuses a non-human reviewer")


if __name__ == "__main__":
    for name, fn in sorted(globals().items()):
        if name.startswith("test_") and callable(fn):
            fn()
    print("ALL PROVENANCE / E6.1 TOOLING TESTS PASS")
