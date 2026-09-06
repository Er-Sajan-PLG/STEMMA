#!/usr/bin/env python3
"""ADR-0033: machine-readable validator report contract + CLI --json.

The report is the single place CI/agents read validation state:
  results[] (severity/rule/focus/message), errors[]/warnings[]/info[],
  severity_counts, versions, content_hash, valid/ok/conforms.
"""
import json
import pathlib
import subprocess
import sys

ROOT = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))
from validate import build_validation_results  # noqa: E402


def test_build_validation_results_severity_mapping():
    results = build_validation_results(
        ["content/phys.md: bad domain"],
        ["connections/conn.000001.yaml: confidence and basis must be paired"],
    )
    assert len(results) == 2
    assert results[0] == {
        "severity": "ERROR",
        "rule": "validator",
        "focus": "content/phys.md",
        "message": "bad domain",
    }
    assert results[1]["severity"] == "WARNING"
    assert results[1]["focus"] == "connections/conn.000001.yaml"
    no_focus = build_validation_results(["bare problem"], [])
    assert no_focus[0]["focus"] == "unknown"
    assert no_focus[0]["message"] == "bare problem"
    print("PASS: severity mapping")


def test_validate_json_contract():
    proc = subprocess.run(
        [sys.executable, str(ROOT / "scripts/validate.py"), "--json"],
        cwd=str(ROOT),
        capture_output=True,
        text=True,
    )
    assert proc.returncode == 0, proc.stderr[-500:]
    report = json.loads(proc.stdout)
    assert report["valid"] is True
    assert report["ok"] is True
    assert report["conforms"] is True
    assert report["schema_version"] == "1.1.0"
    assert report["export_version"] == "2.1.0"
    assert report["relation_registry_version"] == "1.0.0"
    assert report["content_hash"].startswith("sha256:")
    # Phase B (R2/R4) added advisory validator WARNINGs for active empty-evidence
    # and related_to-only edges. The gate stays ERROR-free but the report is no
    # longer warning-free on the current tree.
    assert report["severity_counts"]["ERROR"] == 0
    assert report["severity_counts"]["WARNING"] > 0
    assert report["severity_counts"]["INFO"] == 0
    assert len(report["results"]) == report["severity_counts"]["ERROR"] + report["severity_counts"]["WARNING"] + report["severity_counts"]["INFO"]
    assert report["errors"] == []
    assert len(report["warnings"]) > 0
    assert report["info"] == []

    # The tracked report file matches the emitted JSON (same shape, same content).
    on_disk = json.loads((ROOT / "reports" / "validation-report.json").read_text(encoding="utf-8"))
    assert on_disk == report
    print("PASS: --json emits the structured report and report file matches")


def test_integrity_anomalies_advisory():
    # Default verify-chain call is advisory: returncode 0 even if anomalies exist.
    proc = subprocess.run(
        [sys.executable, str(ROOT / "scripts/integrity_anomalies.py")],
        cwd=str(ROOT),
        capture_output=True,
        text=True,
    )
    assert proc.returncode == 0, proc.stderr

    proc_json = subprocess.run(
        [sys.executable, str(ROOT / "scripts/integrity_anomalies.py"), "--json"],
        cwd=str(ROOT),
        capture_output=True,
        text=True,
    )
    assert proc_json.returncode == 0, proc_json.stderr
    report = json.loads(proc_json.stdout)
    assert report["advisory"] is True
    assert set(report["counts"]) == {"ERROR", "WARNING", "INFO"}
    assert isinstance(report["anomalies"], list)
    print("PASS: integrity anomalies are advisory with structured --json")


def main() -> int:
    test_build_validation_results_severity_mapping()
    test_validate_json_contract()
    test_integrity_anomalies_advisory()
    print("ALL VALIDATION REPORT TESTS PASS")
    return 0


if __name__ == "__main__":
    sys.exit(main())
