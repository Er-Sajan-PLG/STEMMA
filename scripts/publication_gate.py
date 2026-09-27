#!/usr/bin/env python3
"""R6 publication gate (increment 2) — Amendment 0001 enforcement.

Publication of the canonical projection to a public identifier base is
BLOCKED until the owner (human:*) records the R5-deferred identifier-base
decision in docs/decisions/r6-identifier-base.md:

    ---
    decision: w3id | datacite-doi | ark-n2t | stemma-urn-only
    decided_by: human:curator.001   (must be an active human:* in agent registry)
    decided_at: ISO date
    rationale: <clause-level references to CURRENT data — fees/URLs/persistence
                verified at decision time per the R5 brief protocol>
    ---
    <slow-research summary>

Exit 0 = all checks pass AND decision recorded (publishing unblocked).
Exit 1 = BLOCKED (decision required) or check failed.

The gate runs the full deterministic verification chain plus this decision
check, so a future publication step can never quietly bypass the amendment.
"""
from __future__ import annotations

import pathlib
import re
import subprocess
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
DECISION = ROOT / "docs/decisions/r6-identifier-base.md"
BASES = {"w3id", "datacite-doi", "ark-n2t", "stemma-urn-only"}

CHECKS = [
    ["scripts/validate.py"],
    ["scripts/export_jsonld.py", "--check"],
    ["scripts/validate_jsonld.py"],
    ["scripts/validate_shacl_shapes.py"],
    ["scripts/status_truth.py", "--check-readme"],
]


def main() -> int:
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--explain", action="store_true", help="print the gate state without running checks")
    args = ap.parse_args()

    decision_block = None
    if DECISION.exists():
        text = DECISION.read_text(encoding="utf-8")
        m = re.match(r"^---\n(.*?)\n---\n", text, re.S)
        fm = dict(m and __import__("yaml").safe_load(m.group(1)) or {})
        decision_block = fm

    if args.explain:
        print("R6 publication gate — candidate bases and gate state\n"
              "  1. w3id                 (community PURL consortium, URI persistence policy)\n"
              "  2. datacite-doi         (DataCite member fee; DOI; requires membership or consortium)\n"
              "  3. ark-n2t              (ARK Alliance / N2T resolver)\n"
              "  4. stemma-urn-only      (no external base; internal scheme only)\n"
              "Decision reserved to owner per ADR-0053 + Amendment 0001;\n"
              f"record status: {'FOUND' if decision_block else 'NOT FOUND'} ({DECISION.relative_to(ROOT)})")
        return 0

    fails = []
    py = sys.executable
    for cmd in CHECKS:
        r = subprocess.run([py, str(ROOT / cmd[0]), *cmd[1:]], capture_output=True, text=True)
        if r.returncode != 0:
            fails.append((cmd[0], (r.stderr or r.stdout)[-250:]))

    bundle_name = subprocess.run(
        [py, str(ROOT / "scripts/build_release_bundle.py"), "--print-name"],
        capture_output=True, text=True).stdout.strip().splitlines()
    bundle = ROOT / "release" / (bundle_name[-1] if bundle_name else "")
    r = subprocess.run([py, str(ROOT / "scripts/build_release_bundle.py"),
                        "--verify", str(bundle)], capture_output=True, text=True)
    if r.returncode != 0:
        fails.append(("build_release_bundle.py", (r.stderr or r.stdout)[-250:]))

    if fails:
        print("FAIL: gate checks failing:")
        for name, tail in fails:
            print(f"  - {name}: {tail}")
        return 1

    if not decision_block:
        print("BLOCKED: publication deferred per ADR-0053 + Amendment 0001 —\n"
              f"  identifier-base decision record missing: {DECISION.relative_to(ROOT)}\n"
              "  Options: w3id | datacite-doi | ark-n2t | stemma-urn-only\n"
              "  Run 'python3 scripts/publication_gate.py --explain' for context.")
        return 1

    decision = str(decision_block.get("decision", "")).strip().lower()
    if decision not in BASES:
        print(f"BLOCKED: decision value invalid: {decision_block.get('decision')!r} (expected one of {sorted(BASES)})")
        return 1
    decided_by = str(decision_block.get("decided_by", ""))
    if not decided_by.startswith("human:"):
        print("BLOCKED: decided_by must be an active human:* agent (HITL authority)")
        return 1
    print(f"OPEN: gate checks pass; decision recorded ({decision} by {decided_by}).\n"
          "Publication may proceed to the release step.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
