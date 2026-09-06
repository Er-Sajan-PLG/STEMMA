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
    [sys.executable, str(ROOT / "scripts/validate.py")],
    [sys.executable, str(ROOT / "scripts/status_truth.py")],
    [sys.executable, str(ROOT / "scripts/epistemic_summary.py")],
    # ADR-0033: integrity_anomalies is advisory (surfaces anomalies, never fails
    # the chain by itself; use `--strict` for opt-in ERROR gating).
    [sys.executable, str(ROOT / "scripts/integrity_anomalies.py")],
    [sys.executable, str(ROOT / "scripts/graph_analysis.py")],
    [sys.executable, str(ROOT / "scripts/export_review_aware.py")],
    [sys.executable, str(ROOT / "scripts/curation_status.py")],
    [sys.executable, str(ROOT / "tests/phase-b/test_phase_b.py")],
    [sys.executable, str(ROOT / "tests/phase-b/test_boundary.py")],
    [sys.executable, str(ROOT / "tests/registry/test_registry_coherence.py")],
    [sys.executable, str(ROOT / "tests/registry/test_domain_identity.py")],
    [sys.executable, str(ROOT / "tests/versioning/test_validation_report.py")],
    [sys.executable, str(ROOT / "tests/versioning/test_deterministic_export.py")],
    [sys.executable, str(ROOT / "tests/curation/test_curation.py")],
    [sys.executable, str(ROOT / "tests/curation/test_curation_pipeline.py")],
    [sys.executable, str(ROOT / "tests/curation/test_ingest.py")],
    [sys.executable, str(ROOT / "tests/curation/test_ingest_to_proposals.py")],
    [sys.executable, str(ROOT / "tests/webapp/test_webapp_core.py")],
    [sys.executable, str(ROOT / "tests/curation/test_generality.py")],
    [sys.executable, str(ROOT / "tests/curation/test_id_immutability.py")],
    [sys.executable, str(ROOT / "tests/metadata/test_metadata_semantics.py")],
    [sys.executable, str(ROOT / "tests/metadata/test_metadata_urgent.py")],
    [sys.executable, str(ROOT / "tests/provenance/test_agents_external_ids.py")],
    [sys.executable, str(ROOT / "tests/provenance/test_claim_identity.py")],
    [sys.executable, str(ROOT / "tests/curation/test_connection_immutability.py")],
    [sys.executable, str(ROOT / "scripts/dependency_review_campaign.py")],
    [sys.executable, str(ROOT / "scripts/entity_review_campaign.py")],
    [sys.executable, str(ROOT / "scripts/academic_sources.py")],
    [sys.executable, str(ROOT / "scripts/relation_triage.py")],
    [sys.executable, str(ROOT / "tests/curation/test_phase_b_integrity.py")],
    [sys.executable, str(ROOT / "scripts/check_id_immutability.py")],
    [sys.executable, str(ROOT / "adapters/python/tests/test_adapter.py")],
    [sys.executable, str(ROOT / "tests/repo/test_independence.py")],
    [sys.executable, str(ROOT / "tests/repo/test_docs_consistency.py")],
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
