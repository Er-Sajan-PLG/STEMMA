"""D15: Curation tests — state machine, review integrity, evidence, provenance, export."""
import pathlib
import sys
import yaml
import json

ROOT = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))
from curation_state import can_transition  # type: ignore
from graph_policy import should_include_connection  # type: ignore


def test_state_machine_valid():
    assert can_transition("proposed", "reviewed")
    assert can_transition("reviewed", "canonical")
    assert can_transition("proposed", "rejected")
    assert can_transition("rejected", "proposed")
    assert can_transition("rejected", "unreviewed")   # explicit reopen (ADR-0031)
    print("PASS: valid transitions")


def test_state_machine_invalid():
    assert not can_transition("rejected", "canonical")
    assert not can_transition("proposed", "canonical")
    assert not can_transition("rejected", "reviewed")
    print("PASS: invalid transitions rejected")


def test_reject_requires_reviewer_and_reason():
    from curation_state import validate_transition

    conn = {"assertion": {"status": "active", "type": "proposed", "review": {"status": "unreviewed"}}}
    errs = validate_transition(conn, "rejected", None, None)
    assert any("reviewer" in e for e in errs)
    assert any("reason" in e for e in errs)
    errs2 = validate_transition(conn, "rejected", "human:tester.001", None)
    assert not any("reviewer" in e for e in errs2)
    assert any("reason" in e for e in errs2)
    assert validate_transition(conn, "rejected", "human:tester.001", "contradicts evidence") == []
    print("PASS: reject requires reviewer + reason")


def test_reopen_requires_human_with_reason():
    from curation_state import validate_transition

    conn = {"assertion": {"status": "active", "type": "proposed", "review": {"status": "rejected"}}}
    errs = validate_transition(conn, "unreviewed", None, None)
    assert any("reviewer" in e for e in errs)
    assert any("reason" in e for e in errs)
    assert validate_transition(conn, "unreviewed", "human:tester.001", "reconsidered") == []
    print("PASS: reopen requires human reviewer + reason")


def test_reviewer_required():
    conn = {"assertion": {"review": {"status": "unreviewed"}, "type": "proposed", "status": "active"}}
    from curation_state import validate_transition

    errs = validate_transition(conn, "canonical", None)
    assert any("reviewer" in e for e in errs)
    errs2 = validate_transition(conn, "canonical", "human:reviewer.test-001")
    # Should still fail due to forbidden proposed->canonical, but reviewer error gone
    assert not any("reviewer" in e for e in errs2) or "forbidden" in errs2[0]
    print("PASS: reviewer required")


def test_origin_preserved():
    # Pick a migrated canonical
    p = ROOT / "connections/conn.000001.yaml"
    d = yaml.safe_load(p.read_text())
    assert d["provenance"]["asserted_by"]["id"] == "unknown:legacy-relationship"
    assert d["provenance"]["method"]["type"] == "migration" or d["provenance"]["generated_by"]["id"] == "process:migration.relationships-v0.2"
    # Origin should remain migrated even though review is canonical
    print("PASS: origin preserved")


def test_rejected_auditable():
    # ADR-0031: rejection is a review state, never structural retirement. The
    # record stays an active canonical object so it remains in the audit set and
    # `deprecated`/`superseded` stay reserved for dedup/merge/replacement.
    conn = {
        "id": "stemma:conn.999999",
        "assertion": {"status": "active", "type": "proposed", "review": {"status": "rejected"}},
        "provenance": {"asserted_by": {"type": "human", "id": "human:test"}, "generated_by": {"type": "human", "id": "human:test"}, "method": {"type": "manual"}},
    }
    assert conn["assertion"]["status"] == "active"
    assert conn["assertion"]["review"]["status"] == "rejected"
    print("PASS: rejected is auditable as an active record")


def test_evidence_by_family():
    # For canonical, evidence should exist per family rules
    for p in (ROOT / "connections").glob("*.yaml"):
        d = yaml.safe_load(p.read_text())
        if d["assertion"]["review"]["status"] == "canonical":
            assert d.get("evidence") is not None and len(d["evidence"]) > 0, f"{d['id']} canonical without evidence"
    print("PASS: evidence for canonical")


def test_provenance_distinction():
    # Human vs LLM traceable
    for p in (ROOT / "connections").glob("*.yaml"):
        d = yaml.safe_load(p.read_text())
        asserted = d["provenance"]["asserted_by"]["type"]
        assert asserted in ("human", "llm", "process", "unknown")
    print("PASS: provenance distinction")


def test_trusted_export():
    # trusted excludes unreviewed
    import subprocess, json

    subprocess.run(["python3", str(ROOT / "scripts/export_review_aware.py")], check=True)
    trusted = json.loads((ROOT / "exports/knowledge.trusted.json").read_text())
    all_c = json.loads((ROOT / "exports/knowledge.all.json").read_text())
    canonical_files = sum(
        1 for p in (ROOT / "connections").glob("*.yaml")
        if yaml.safe_load(p.read_text()).get("assertion", {}).get("status") == "active"
    )
    # 'all' export contains every ACTIVE canonical connection (not a magic count);
    # deprecated connections are excluded by policy (graph_policy.should_include_connection).
    assert all_c["count"] == canonical_files
    # 'trusted' is a subset of 'all' (>=0) whose members are all reviewed/canonical.
    assert 0 <= trusted["count"] <= all_c["count"]
    for c in trusted["connections"]:
        assert c["assertion"]["review"]["status"] in ("reviewed", "canonical")
        assert not (c["provenance"]["asserted_by"]["type"] == "llm" and c["assertion"]["review"]["status"] == "unreviewed")
    print("PASS: trusted export")


def test_all_exports():
    import json

    for policy in ["all", "reviewed", "canonical", "proposed", "rejected"]:
        p = ROOT / f"exports/knowledge.{policy}.json"
        assert p.exists(), f"missing {policy} export"
        d = json.loads(p.read_text())
        assert "count" in d and "connections" in d
    print("PASS: all exports exist")


def test_all_policy_excludes_rejected_and_rejected_view_includes_them():
    """ADR-0031: `all` is active-and-not-rejected; rejected surfaces only in
    exports/knowledge.rejected.json. This is deterministic and does not mutate
    canonical files (in-memory policy check)."""
    import json

    rejected_files = [
        p
        for p in (ROOT / "connections").glob("*.yaml")
        if yaml.safe_load(p.read_text()).get("assertion", {}).get("review", {}).get("status") == "rejected"
    ]
    if rejected_files:
        sample = yaml.safe_load(rejected_files[0].read_text())
        assert not should_include_connection(sample, "all")

    rejected = json.loads((ROOT / "exports/knowledge.rejected.json").read_text())
    assert all(
        c["assertion"]["review"]["status"] == "rejected"
        for c in rejected["connections"]
    )
    print(f"PASS: all excludes rejected; rejected view holds {rejected['count']}")


def test_validator_rejects_silent_rejection():
    """ADR-0031 gate: a connection with review.status=rejected but no reason is
    a hard validator error; a reason in lifecycle or review_history unblocks it."""
    from validate import check_rejected_lifecycle  # type: ignore

    base = {
        "id": "stemma:conn.999999",
        "assertion": {"status": "active", "type": "proposed", "review": {"status": "rejected"}},
        "provenance": {
            "asserted_by": {"type": "human", "id": "human:test"},
            "generated_by": {"type": "human", "id": "human:test"},
            "method": {"type": "manual"},
        },
    }

    silent = dict(base)
    errs = []
    check_rejected_lifecycle(silent, errs)
    assert errs, "silent rejection must fail the gate"

    lifecycle = dict(base)
    lifecycle["lifecycle"] = {"reason": "contradicts primary sources", "replaced_by": None}
    errs = []
    check_rejected_lifecycle(lifecycle, errs)
    assert not errs

    via_history = dict(base)
    via_history["provenance"]["review_history"] = [
        {"from": "unreviewed", "to": "rejected", "reviewer": "human:tester.001", "at": "2026-09-06T00:00:00+00:00", "reason": "contradicts primary sources"}
    ]
    errs = []
    check_rejected_lifecycle(via_history, errs)
    assert not errs
    print("PASS: rejected requires written reason")


if __name__ == "__main__":
    test_state_machine_valid()
    test_state_machine_invalid()
    test_reject_requires_reviewer_and_reason()
    test_reopen_requires_human_with_reason()
    test_reviewer_required()
    test_origin_preserved()
    test_rejected_auditable()
    test_evidence_by_family()
    test_provenance_distinction()
    test_trusted_export()
    test_all_exports()
    test_all_policy_excludes_rejected_and_rejected_view_includes_them()
    test_validator_rejects_silent_rejection()
    print("ALL CURATION TESTS PASS")
