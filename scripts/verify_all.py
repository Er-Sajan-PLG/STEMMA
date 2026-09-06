#!/usr/bin/env python3
"""The authoritative verification chain — what CI runs, what you run.

Stages: gate (validate + export, machine-readable report + `--json`) →
status truth → derived analyses → advisory integrity anomalies → review-aware
exports → domain/boundary invariants → registry coherence →
validation-report/contract + determinism tests → curation + generality →
identity immutability (present-tree + git-history) → provenance/claim-identity
→ connection-triple immutability → campaign determinism → repository
integrity (independence, docs consistency).
"""
import pathlib
import subprocess
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent

steps = [
    ["python3", str(ROOT / "scripts/validate.py")],
    ["python3", str(ROOT / "scripts/status_truth.py")],
    ["python3", str(ROOT / "scripts/epistemic_summary.py")],
    # ADR-0033: integrity_anomalies is advisory (surfaces anomalies, never fails
    # the chain by itself; use `--strict` for opt-in ERROR gating).
    ["python3", str(ROOT / "scripts/integrity_anomalies.py")],
    ["python3", str(ROOT / "scripts/graph_analysis.py")],
    ["python3", str(ROOT / "scripts/export_review_aware.py")],
    ["python3", str(ROOT / "scripts/curation_status.py")],
    ["python3", str(ROOT / "tests/phase-b/test_phase_b.py")],
    ["python3", str(ROOT / "tests/phase-b/test_boundary.py")],
    ["python3", str(ROOT / "tests/registry/test_registry_coherence.py")],
    ["python3", str(ROOT / "tests/versioning/test_validation_report.py")],
    ["python3", str(ROOT / "tests/versioning/test_deterministic_export.py")],
    ["python3", str(ROOT / "tests/curation/test_curation.py")],
    ["python3", str(ROOT / "tests/curation/test_generality.py")],
    ["python3", str(ROOT / "tests/curation/test_id_immutability.py")],
    ["python3", str(ROOT / "tests/metadata/test_metadata_semantics.py")],
    ["python3", str(ROOT / "tests/metadata/test_metadata_urgent.py")],
    ["python3", str(ROOT / "tests/provenance/test_agents_external_ids.py")],
    ["python3", str(ROOT / "tests/provenance/test_claim_identity.py")],
    ["python3", str(ROOT / "tests/curation/test_connection_immutability.py")],
    ["python3", str(ROOT / "scripts/dependency_review_campaign.py")],
    ["python3", str(ROOT / "scripts/check_id_immutability.py")],
    ["python3", str(ROOT / "adapters/python/tests/test_adapter.py")],
    ["python3", str(ROOT / "tests/repo/test_independence.py")],
    ["python3", str(ROOT / "tests/repo/test_docs_consistency.py")],
]


def main() -> int:
    for cmd in steps:
        print(f"RUN: {' '.join(cmd)}")
        r = subprocess.run(cmd)
        if r.returncode != 0:
            print(f"FAIL: {' '.join(cmd)}", file=sys.stderr)
            return 1
    print("OK: all verify steps pass")
    return 0


if __name__ == "__main__":
    sys.exit(main())
