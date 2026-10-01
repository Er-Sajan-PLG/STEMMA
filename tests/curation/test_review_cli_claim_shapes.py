"""Review CLI — claim-shape coverage (value-slot vs relational).

Regression pin for the dormant bug class R4 fixed across validate.py,
graph_analysis.py, check_id_immutability.py, relation_triage.py,
integrity_anomalies.py, export_subsets.py and curation_status.py:
`review.py` was missed, so `list` crashed with KeyError: 'target' on a
corpus containing any value-slot claim (ADR-0045).

A claim is EITHER an entity->entity edge (has `target`) OR a value-slot claim
(has `value`). These tests run the real CLI against the real corpus so the
value-slot path can never silently regress again.
"""
import json
import subprocess
import sys
import pathlib

import yaml

ROOT = pathlib.Path(__file__).resolve().parents[2]
REVIEW = ROOT / "scripts" / "review.py"
CONNECTIONS = ROOT / "connections"


def _run(*args):
    return subprocess.run(
        [sys.executable, str(REVIEW), *args],
        capture_output=True, text=True, cwd=ROOT,
    )


def _corpus_has_both_shapes():
    """The corpus must exercise BOTH shapes for these tests to mean anything."""
    has_value = has_target = False
    for p in CONNECTIONS.glob("*.yaml"):
        d = yaml.safe_load(p.read_text())
        if d.get("value") is not None:
            has_value = True
        if d.get("target") is not None:
            has_target = True
    return has_value, has_target


def test_corpus_exercises_both_claim_shapes():
    has_value, has_target = _corpus_has_both_shapes()
    assert has_value, "no value-slot claim in corpus — regression pin is vacuous"
    assert has_target, "no relational claim in corpus — regression pin is vacuous"
    print("PASS: corpus exercises both claim shapes")


def test_list_does_not_crash_on_value_slot():
    r = _run("list")
    assert r.returncode == 0, f"review.py list failed:\n{r.stderr}"
    rows = json.loads(r.stdout)
    assert rows, "expected at least one connection"
    print("PASS: review.py list handles value-slot claims")


def test_list_reports_both_shapes_faithfully():
    rows = {r["id"]: r for r in json.loads(_run("list").stdout)}
    value_rows = [r for r in rows.values() if r["value"] is not None]
    target_rows = [r for r in rows.values() if r["target"] is not None]
    assert value_rows and target_rows
    for r in value_rows:
        assert r["target"] is None
        assert r["claim"] == f"value:{r['value']}"
    for r in target_rows:
        assert r["claim"] == r["target"]
    print("PASS: list reports both claim shapes faithfully")


def test_show_renders_value_slot_without_target():
    for p in sorted(CONNECTIONS.glob("*.yaml")):
        d = yaml.safe_load(p.read_text())
        if d.get("value") is None:
            continue
        r = _run("show", d["id"])
        assert r.returncode == 0, f"show {d['id']} failed:\n{r.stderr}"
        payload = yaml.safe_load(r.stdout)
        assert payload["target"] is None
        assert payload["value"] == d["value"]
        print(f"PASS: show renders value-slot {d['id']}")
        return
    raise AssertionError("no value-slot claim found")


def test_show_renders_relational_with_target():
    for p in sorted(CONNECTIONS.glob("*.yaml")):
        d = yaml.safe_load(p.read_text())
        if d.get("target") is None:
            continue
        r = _run("show", d["id"])
        assert r.returncode == 0, f"show {d['id']} failed:\n{r.stderr}"
        payload = yaml.safe_load(r.stdout)
        assert payload["target"]["id"] == d["target"]
        assert payload["value"] is None
        assert payload["target"]["name"], "target entity should be enriched from content/"
        print(f"PASS: show renders relational {d['id']}")
        return
    raise AssertionError("no relational claim found")
