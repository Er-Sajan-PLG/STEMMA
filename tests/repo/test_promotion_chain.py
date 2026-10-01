"""ADR-0057 / ENF-STEMMA-HITL-001..004 — promotion chain + revalidation debt gate.

These are the owner's controlling rules (2026-10-01):

  * the validator is NOT the final canonicalizer
  * the chain is recorded, and the owner cannot break the day-separation rule
  * BOARD WAIVER (ENF-003 board_waiver): while the owner is the only validator
    the required chain is validator -> independent_validator and canonical is
    reachable from the independent_validator stage; the board stage is retired,
    not faked
  * DEBT, PILOT SCALE (ENF-002 pilot_scale_block, block_mode=full): an
    outstanding debt makes the record INVALID outright — not just blocked from
    the next forward promotion
  * applies to ALL canonical datasets — entities AND connections

Each guard is tested with an injected violation (mutation discipline): a green
gate is only informative if it can go red. The active rules are also asserted to
be read from the enforcement registry, not hardcoded.
"""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import pytest
import yaml

ROOT = Path(__file__).resolve().parents[2]
VALIDATE = ROOT / "scripts" / "validate.py"
REVIEW = ROOT / "scripts" / "review_entity.py"
ENFORCEMENT = ROOT / "spec" / "machine-readable" / "enforcement_rules.yaml"
METRE = ROOT / "content" / "physics" / "measurement-units" / "metre.md"
CONN = ROOT / "connections" / "conn.000156.yaml"

WAIVED_CHAIN = ["validator", "independent_validator"]


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


def _rules() -> dict:
    return yaml.safe_load(ENFORCEMENT.read_text(encoding="utf-8"))


# Derived artifacts that `scripts/validate.py` rewrites from canonical content.
# Every test in this module that runs validate.py can leave these computed from a
# mutated canonical state, so the module must guarantee it puts them back.
_DERIVED_ARTIFACTS = (
    ROOT / "exports" / "knowledge.json",
    ROOT / "reports" / "validation-report.json",
)


def _snapshot(paths) -> dict:
    return {p: (p.read_bytes() if p.exists() else None) for p in paths}


def _restore(backups: dict) -> None:
    for path, data in backups.items():
        if data is None:
            path.unlink(missing_ok=True)
        else:
            path.write_bytes(data)


@pytest.fixture(scope="module", autouse=True)
def _restore_derived_artifacts_at_module_end():
    """Guarantee this module leaves the derived artifacts exactly as it found them.

    Three tests here call `validate.py` without `restore_records`
    (`test_baseline_gate_is_green`, `test_missing_enforcement_registry_fails_closed`,
    `test_board_waiver_retire_turns_chain_back_on`), and a failing assertion can skip
    a per-test restore anyway. A module-scoped snapshot closes every path at once, so
    this module can never dirty the working tree — or leave a stale export for the
    next run to trip over.
    """
    backups = _snapshot(_DERIVED_ARTIFACTS)
    yield
    _restore(backups)


@pytest.fixture()
def restore_records():
    """Snapshot the two promoted records AND the derived artifacts, then restore.

    These tests mutate the *real* canonical records and then run `validate.py`,
    which regenerates `exports/knowledge.json` and `reports/validation-report.json`
    from whatever canonical state it finds. Restoring only the canonical records
    leaves those derived artifacts computed from the **mutated** state, which then:

    * dirties the working tree, so the pre-push `exports not fresh` gate fails on an
      otherwise clean run; and
    * makes `test_versioning_policy.py::test_content_hash_covers_exactly_the_canonical_sources`
      fail on the **next** run — that test reads `exports/knowledge.json` at import
      time, so it compares the stale export against the restored canonical layer.

    The second symptom is order-dependent (it depends on which test last ran
    validate), which is why it presented as a rare intermittent rather than a
    reproducible failure. Snapshotting the derived artifacts too removes both.
    """
    backups = _snapshot((METRE, CONN, *_DERIVED_ARTIFACTS))
    yield
    _restore(backups)


# ---------------------------------------------------------------- baseline ---

def test_baseline_gate_is_green():
    r = _run_validate()
    assert r.returncode == 0, r.stdout + r.stderr


def test_metre_has_waived_chain():
    data, _ = _read_md(METRE)
    stages = [e["stage"] for e in data["provenance"]["promotion_history"]]
    assert stages == WAIVED_CHAIN


def test_connection_has_waived_chain():
    data = yaml.safe_load(CONN.read_text(encoding="utf-8"))
    stages = [e["stage"] for e in data["provenance"]["promotion_history"]]
    assert stages == WAIVED_CHAIN


def test_terminal_stage_marks_board_waived():
    data, _ = _read_md(METRE)
    last = data["provenance"]["promotion_history"][-1]
    assert last.get("board_waived") is True


# ------------------------------------------------------- rules are data -----

def test_board_waiver_is_active_in_registry():
    rules = _rules()
    waivers = [r["board_waiver"] for r in rules["rules"] if r.get("board_waiver")]
    assert len(waivers) == 1
    assert waivers[0]["active"] is True
    assert waivers[0]["required_stages_while_waived"] == WAIVED_CHAIN


def test_debt_blocks_fully_in_registry():
    rules = _rules()
    for r in rules["rules"]:
        spec = r.get("rule") or {}
        if spec.get("kind") == "debt_blocks_status":
            assert spec.get("block_mode") == "full"
            assert r["pilot_scale_block"]["active"] is True
            break
    else:
        pytest.fail("no debt_blocks_status rule in the enforcement registry")


def test_time_gate_is_data_driven():
    """The gap is read from the enforcement registry, not hardcoded."""
    rules = _rules()
    gaps = [r["rule"]["min_days"] for r in rules["rules"]
            if r.get("rule", {}).get("kind") == "min_stage_gap"]
    assert gaps == [1]


def test_missing_enforcement_registry_fails_closed():
    backup = ENFORCEMENT.read_text(encoding="utf-8")
    try:
        ENFORCEMENT.unlink()
        r = _run_validate()
        assert r.returncode != 0
        assert "enforcement" in (r.stdout + r.stderr).lower()
    finally:
        ENFORCEMENT.write_text(backup, encoding="utf-8")


# --------------------------------------------------- board waiver mutation --

def test_board_stage_while_waived_fails(restore_records):
    """Recording a board stage while the board is waived must go red."""
    data, body = _read_md(METRE)
    hist = data["provenance"]["promotion_history"]
    hist.append({"stage": "board", "actor": "human:curator.001",
                 "at": "2026-09-25T11:00:00+00:00",
                 "board_members": ["human:curator.001"],
                 "independence_waiver": {"sanctioned_by": "human:curator.001",
                                         "reason": "x", "retire_when": "y"}})
    _write_md(METRE, data, body)
    r = _run_validate()
    assert r.returncode == 1
    assert "waived" in (r.stdout + r.stderr)


def test_board_waiver_retire_turns_chain_back_on():
    """With the waiver retired, the two-stage chain must fail (board required)."""
    backup = ENFORCEMENT.read_text(encoding="utf-8")
    try:
        rules = _rules()
        for rule in rules["rules"]:
            if "board_waiver" in rule:
                rule["board_waiver"]["active"] = False
        ENFORCEMENT.write_text(yaml.safe_dump(rules, sort_keys=False, allow_unicode=True),
                               encoding="utf-8")
        r = _run_validate()
        assert r.returncode == 1
        out = r.stdout + r.stderr
        # The chain (excluding board) no longer matches the required three stages.
        assert "do not match the required ordered chain" in out or "board" in out
    finally:
        ENFORCEMENT.write_text(backup, encoding="utf-8")


# ------------------------------------------------------ debt mutation (full) -

def test_outstanding_debt_full_block_rejects_reviewed_status(restore_records):
    """At pilot scale, ANY reviewed status with outstanding debt is invalid."""
    data, body = _read_md(METRE)
    data["revalidation_debt"] = {
        "status": "outstanding",
        "reason": "connection_obligations_pending",
        "incurred_at": "2026-10-01",
        "items": [],
    }
    _write_md(METRE, data, body)
    r = _run_validate()
    assert r.returncode == 1
    out = r.stdout + r.stderr
    assert "DEBT BLOCKS VALIDATION" in out
    assert "revalidation_debt.status is 'outstanding'" in out


def test_debt_cleared_is_accepted(restore_records):
    """The same record with the debt cleared validates cleanly."""
    data, body = _read_md(METRE)
    data["revalidation_debt"] = {
        "status": "cleared",
        "reason": "connection_obligations_pending",
        "incurred_at": "2026-10-01",
        "cleared_by": "human:curator.001",
        "cleared_stage": "validator",
        "cleared_at": "2026-10-01T09:00:00+00:00",
        "clearance_evidence": "conn.000156 satisfied the obligation",
    }
    _write_md(METRE, data, body)
    r = _run_validate()
    assert r.returncode == 0, r.stdout + r.stderr


def test_connection_debt_full_block(restore_records):
    """Debt blocks connections too (all datasets)."""
    data = yaml.safe_load(CONN.read_text(encoding="utf-8"))
    data["revalidation_debt"] = {
        "status": "outstanding",
        "reason": "endpoint_revalidated",
        "incurred_at": "2026-10-01",
        "items": [],
    }
    CONN.write_text(yaml.safe_dump(data, sort_keys=False, allow_unicode=True), encoding="utf-8")
    r = _run_validate()
    assert r.returncode == 1
    assert "DEBT BLOCKS VALIDATION" in (r.stdout + r.stderr)


def test_connection_empty_history_blocks(restore_records):
    data = yaml.safe_load(CONN.read_text(encoding="utf-8"))
    data["provenance"]["promotion_history"] = []
    CONN.write_text(yaml.safe_dump(data, sort_keys=False, allow_unicode=True), encoding="utf-8")
    r = _run_validate()
    assert r.returncode == 1


# ------------------------------------------------------------------ time -----

def test_time_gate_same_day_stages_fail(restore_records):
    data, body = _read_md(METRE)
    # Collapse stage 2 onto stage 1's day.
    data["provenance"]["promotion_history"][1]["at"] = "2026-09-23T09:10:00+00:00"
    _write_md(METRE, data, body)
    r = _run_validate()
    assert r.returncode == 1
    assert "same day" in (r.stdout + r.stderr)


# ------------------------------------------------------------------- CLI -----

def test_cli_refuses_direct_canonicalize():
    r = subprocess.run(
        [sys.executable, str(REVIEW), "canonicalize",
         "stemma:phys.metre", "--reviewer", "human:curator.001"],
        cwd=ROOT, capture_output=True, text=True)
    assert r.returncode == 2
    out = (r.stdout + r.stderr).lower()
    assert "final canonicalizer" in out or "no longer a single step" in out


def test_cli_refuses_same_day_second_stage(restore_records):
    """A fresh draft cannot complete two stages on the same day via the CLI."""
    force = ROOT / "content" / "physics" / "mechanics" / "force.md"
    backup = force.read_text(encoding="utf-8")
    try:
        r1 = subprocess.run(
            [sys.executable, str(REVIEW), "stage",
             "stemma:phys.force", "--actor", "human:curator.001",
             "--at", "2026-10-01T10:00:00+00:00"],
            cwd=ROOT, capture_output=True, text=True)
        assert r1.returncode == 0, r1.stdout + r1.stderr
        r2 = subprocess.run(
            [sys.executable, str(REVIEW), "stage",
             "stemma:phys.force", "--actor", "human:curator.001",
             "--at", "2026-10-01T11:00:00+00:00"],
            cwd=ROOT, capture_output=True, text=True)
        assert r2.returncode == 2
        assert "TIME GATE" in (r2.stdout + r2.stderr)
    finally:
        force.write_text(backup, encoding="utf-8")


def test_cli_refuses_board_stage_while_waived(restore_records):
    """`--stage board` must be refused while the board waiver is active."""
    force = ROOT / "content" / "physics" / "mechanics" / "force.md"
    backup = force.read_text(encoding="utf-8")
    try:
        r = subprocess.run(
            [sys.executable, str(REVIEW), "stage",
             "stemma:phys.force", "--actor", "human:curator.001", "--stage", "board"],
            cwd=ROOT, capture_output=True, text=True)
        assert r.returncode == 2
        assert "not part of the current chain" in (r.stdout + r.stderr) or \
               "waived" in (r.stdout + r.stderr)
    finally:
        force.write_text(backup, encoding="utf-8")
