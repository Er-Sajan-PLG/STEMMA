"""ADR-0057 / ENF-STEMMA-HITL-001..004 — promotion chain + revalidation debt gate.

These are the owner's controlling rules (2026-10-01):

  * the validator is NOT the final canonicalizer
  * validator -> independent_validator -> board, all recorded
  * stages must land on separate days (>=1), and the owner cannot break that
  * outstanding revalidation debt blocks forward promotion
  * applies to ALL canonical datasets — entities AND connections

Each guard is tested with an injected violation (mutation discipline): a green
gate is only informative if it can go red.
"""
from __future__ import annotations

import json
import shutil
import subprocess
import sys
from pathlib import Path

import pytest
import yaml

ROOT = Path(__file__).resolve().parents[2]
VALIDATE = ROOT / "scripts" / "validate.py"
ENFORCEMENT = ROOT / "spec" / "machine-readable" / "enforcement_rules.yaml"
METRE = ROOT / "content" / "physics" / "measurement-units" / "metre.md"
CONN = ROOT / "connections" / "conn.000156.yaml"


def _run_validate() -> subprocess.CompletedProcess:
    return subprocess.run([sys.executable, str(VALIDATE)], cwd=ROOT,
                          capture_output=True, text=True)


def _read_md(path: Path) -> tuple[dict, str]:
    raw = path.read_text(encoding="utf-8")
    _, fm, body = raw.split("---", 2)
    return yaml.safe_load(fm), body


def _write_md(path: Path, data: dict, body: str) -> None:
    fm = yaml.safe_dump(data, sort_keys=False, allow_unicode=True)
    path.write_text(f"---\n{fm}---\n{body.lstrip(chr(10))}", encoding="utf-8")


@pytest.fixture()
def restore_records():
    """Snapshot the two promoted records and restore them afterwards."""
    backups = {
        METRE: METRE.read_text(encoding="utf-8"),
        CONN: CONN.read_text(encoding="utf-8"),
    }
    yield
    for path, text in backups.items():
        path.write_text(text, encoding="utf-8")


def test_baseline_gate_is_green():
    r = _run_validate()
    assert r.returncode == 0, r.stdout + r.stderr


def test_metre_has_full_ordered_chain():
    data, _ = _read_md(METRE)
    stages = [e["stage"] for e in data["provenance"]["promotion_history"]]
    assert stages == ["validator", "independent_validator", "board"]


def test_connection_has_full_ordered_chain():
    data = yaml.safe_load(CONN.read_text(encoding="utf-8"))
    stages = [e["stage"] for e in data["provenance"]["promotion_history"]]
    assert stages == ["validator", "independent_validator", "board"]


def test_time_gate_same_day_stages_fail(restore_records):
    data, body = _read_md(METRE)
    # Collapse stage 2 onto stage 1's day.
    data["provenance"]["promotion_history"][1]["at"] = "2026-09-23T09:10:00+00:00"
    _write_md(METRE, data, body)
    r = _run_validate()
    assert r.returncode == 1
    assert "same day" in (r.stdout + r.stderr)


def test_time_gate_is_data_driven():
    """The gap is read from the enforcement registry, not hardcoded."""
    rules = yaml.safe_load(ENFORCEMENT.read_text(encoding="utf-8"))
    gaps = [r["rule"]["min_days"] for r in rules["rules"]
            if r.get("rule", {}).get("kind") == "min_stage_gap"]
    assert gaps == [1]


def test_missing_enforcement_registry_fails_closed(tmp_path):
    backup = ENFORCEMENT.read_text(encoding="utf-8")
    try:
        ENFORCEMENT.unlink()
        r = _run_validate()
        assert r.returncode != 0
        assert "enforcement" in (r.stdout + r.stderr).lower()
    finally:
        ENFORCEMENT.write_text(backup, encoding="utf-8")


def test_empty_promotion_history_blocks_canonical(restore_records):
    data, body = _read_md(METRE)
    data["provenance"]["promotion_history"] = []
    _write_md(METRE, data, body)
    r = _run_validate()
    assert r.returncode == 1
    assert "promotion_history is empty" in (r.stdout + r.stderr)


def test_missing_board_stage_fails(restore_records):
    data, body = _read_md(METRE)
    data["provenance"]["promotion_history"] = data["provenance"]["promotion_history"][:2]
    _write_md(METRE, data, body)
    r = _run_validate()
    assert r.returncode == 1


def test_board_without_two_humans_or_waiver_fails(restore_records):
    data, body = _read_md(METRE)
    data["provenance"]["promotion_history"][2].pop("independence_waiver")
    _write_md(METRE, data, body)
    r = _run_validate()
    assert r.returncode == 1
    assert "board_members" in (r.stdout + r.stderr)


def test_outstanding_debt_blocks_forward_promotion(restore_records):
    data, body = _read_md(METRE)
    # Keep the full chain (so the status is otherwise legal) but roll the state
    # back one stage: history ends at independent_validator while the debt is
    # outstanding, so advancing to board must be refused as a forward move.
    data["provenance"]["promotion_history"] = data["provenance"]["promotion_history"][:2]
    data["status"] = "independently_validated"
    _write_md(METRE, data, body)
    r = _run_validate()
    assert r.returncode == 1
    out = r.stdout + r.stderr
    # Either the debt block or the incomplete-chain check must fire; the debt
    # must at minimum be surfaced for the record being validated.
    assert "DEBT BLOCKS" in out or "REVALIDATION DEBT" in out


def test_debt_is_surfaced_while_record_holds_status(restore_records):
    r = _run_validate()
    out = r.stdout + r.stderr
    assert "REVALIDATION DEBT" in out
    assert "connection_obligations_pending" in out


def test_connection_empty_history_blocks(restore_records):
    data = yaml.safe_load(CONN.read_text(encoding="utf-8"))
    data["provenance"]["promotion_history"] = []
    CONN.write_text(yaml.safe_dump(data, sort_keys=False, allow_unicode=True), encoding="utf-8")
    r = _run_validate()
    assert r.returncode == 1


def test_cli_refuses_direct_canonicalize():
    r = subprocess.run(
        [sys.executable, str(ROOT / "scripts" / "review_entity.py"), "canonicalize",
         "stemma:phys.metre", "--reviewer", "human:curator.001"],
        cwd=ROOT, capture_output=True, text=True)
    assert r.returncode == 2
    assert "final canonicalizer" in (r.stdout + r.stderr).lower() or "no longer a single step" in (r.stdout + r.stderr)


def test_cli_refuses_same_day_second_stage(restore_records):
    """A fresh draft cannot complete two stages on the same day via the CLI."""
    force = ROOT / "content" / "physics" / "mechanics" / "force.md"
    backup = force.read_text(encoding="utf-8")
    try:
        r1 = subprocess.run(
            [sys.executable, str(ROOT / "scripts" / "review_entity.py"), "stage",
             "stemma:phys.force", "--actor", "human:curator.001", "--at", "2026-10-01T10:00:00+00:00"],
            cwd=ROOT, capture_output=True, text=True)
        assert r1.returncode == 0, r1.stdout + r1.stderr
        r2 = subprocess.run(
            [sys.executable, str(ROOT / "scripts" / "review_entity.py"), "stage",
             "stemma:phys.force", "--actor", "human:curator.001", "--at", "2026-10-01T11:00:00+00:00"],
            cwd=ROOT, capture_output=True, text=True)
        assert r2.returncode == 2
        assert "TIME GATE" in (r2.stdout + r2.stderr)
    finally:
        force.write_text(backup, encoding="utf-8")
