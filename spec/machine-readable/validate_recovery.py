#!/usr/bin/env python3
"""Minimum recovery-registry validator for the STEMMA specification pilot.

Implements the nine mandatory checks of SPECIFICATION RECOVERY PROTOCOL v3.1,
section 22.2, and nothing more (charter forbids tooling beyond the minimum
validator during recovery):

  1. ID syntax            - IDs match <TYPE>-STEMMA-<DOMAIN>-NNN
  2. Registered domain    - DOMAIN part exists in domain_registry.yaml
  3. Duplicate IDs        - no ID twice within or across registries
  4. Reference integrity  - every machine-readable reference resolves
                            (STEMMA-XXX ids -> registries; XC-n -> EXTERNAL_CONSTRAINTS.md;
                             ASM-n -> ASSUMPTIONS.md; ADR-nnnn -> docs/decisions/)
  5. Legal lifecycle      - status values within legal sets; SUPERSEDED implies
                            a successor pointer; OBSOLETE implies none
  6. Approval metadata    - APPROVED => approver + approval_date present;
                            PROPOSED/DRAFT => approver null (no fake approval)
  7. Verification on APPROVED - approved requirements name a verification method
  8. verified => approved - a VERIFIED verification record requires its
                            requirement to be APPROVED
  9. Traceability resolves- every requirement traced exactly once; trace
                            evidence refs exist; implementation paths exist

Exit 0 = all checks pass; exit 1 = one or more violations (printed).
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent          # spec/machine-readable/
SPEC = ROOT.parent                              # spec/
REPO = SPEC.parent                              # repo root

ID_RE = re.compile(r"^(EVID|REQ|IFACE|ADR|UNRES|CONFLICT|VER)-STEMMA-([A-Z]+)-(\d{3})$")
HIST_ADR_RE = re.compile(r"^ADR-\d{4}$")

REQ_STATUSES = {"DRAFT", "PROPOSED", "APPROVED", "REJECTED", "DEFERRED", "SUPERSEDED", "OBSOLETE"}
DECISION_STATUSES = {"PROPOSED", "ACCEPTED", "REJECTED", "SUPERSEDED", "DEPRECATED"}
VER_STATUSES = {"UNVERIFIED", "VERIFIED", "FAILED"}
VER_METHODS = {"UNIT_TEST", "INTEGRATION_TEST", "STATIC_ANALYSIS", "INSPECTION", "MEASUREMENT", "MANUAL"}
REQ_TYPES = {"FUNCTIONAL", "NON_FUNCTIONAL", "DATA", "CONSTRAINT", "INTERFACE", "BEHAVIORAL", "SECURITY", "OPERATIONAL"}
REQ_ORIGINS = {"RECOVERED", "PROPOSED", "DERIVED", "EXTERNAL"}
REQ_PRIORITIES = {"P0", "P1", "P2", "P3"}
REQ_STRENGTH = {"SHALL", "SHALL NOT", "SHOULD", "SHOULD NOT", "MAY"}
VALIDATION_STATUSES = {"SUPPORTED", "PARTIALLY_SUPPORTED", "NEEDS_AUTHORITY", "UNSUPPORTED", "CONTRADICTED"}
EVID_CLASSES = {"FACT", "CLAIM", "INFERENCE"}
CONFLICT_STATUSES = {"OPEN", "RESOLVED"}
OQ_STATUSES = {"OPEN", "CLOSED", "DEFERRED"}

violations: list[str] = []


def fail(check: int, msg: str) -> None:
    violations.append(f"CHECK {check}: {msg}")


def load(name: str):
    with open(ROOT / name, encoding="utf-8") as fh:
        return yaml.safe_load(fh)


def main() -> int:
    domains = set(load("domain_registry.yaml")["domains"].keys())
    evidence = load("evidence.yaml")["evidence"]
    requirements = load("requirements.yaml")["requirements"]
    interfaces = load("interfaces.yaml")["interfaces"]
    decisions = load("decisions.yaml")["decisions"]
    verification = load("verification.yaml")["verification_records"]
    traceability = load("traceability.yaml")["traces"]
    conflicts = load("conflicts.yaml")["conflicts"]
    open_questions = load("open_questions.yaml")["open_questions"]

    ids: dict[str, str] = {}  # id -> origin registry label

    def register(rid, label, check_domain=True):
        m = ID_RE.match(rid or "")
        if not m:
            fail(1, f"{label}: malformed id {rid!r}")
            return
        if check_domain and m.group(2) not in domains:
            fail(2, f"{label}: id {rid} uses unregistered domain {m.group(2)!r}")
        if rid in ids:
            fail(3, f"duplicate id {rid} ({ids[rid]} and {label})")
        ids[rid] = label

    for e in evidence:
        register(e.get("id"), "evidence.yaml")
        if e.get("class") not in EVID_CLASSES:
            fail(5, f"{e.get('id')}: illegal evidence class {e.get('class')!r}")
    for r in requirements:
        register(r.get("id"), "requirements.yaml")
    for i in interfaces:
        register(i.get("id"), "interfaces.yaml")
    for d in decisions:
        register(d.get("id"), "decisions.yaml")
    for c in conflicts:
        register(c.get("id"), "conflicts.yaml")
    for q in open_questions:
        register(q.get("id"), "open_questions.yaml")

    md_caches: dict[str, str] = {}

    def md_text(path: str) -> str:
        if path not in md_caches:
            md_caches[path] = (SPEC / path).read_text(encoding="utf-8")
        return md_caches[path]

    def resolve(ref, owner, check=4):
        if ref is None or not isinstance(ref, str):
            return
        if ID_RE.match(ref):
            if ref not in ids:
                fail(check, f"{owner}: unresolved reference {ref}")
            return
        if HIST_ADR_RE.match(ref):
            n = ref.split("-")[1]  # zero-padded 4-digit number
            candidates = [REPO / "docs" / "decisions", REPO / "archive" / "old-design" / "docs" / "decisions"]
            found = False
            for d in candidates:
                if d.is_dir() and any(f.name.startswith(n + "-") for f in d.iterdir()):
                    found = True
                    break
            if not found:
                fail(check, f"{owner}: historical {ref} found in neither docs/decisions/ nor archive/old-design/docs/decisions/")
            return
        if ref.startswith("XC-"):
        # external constraints live in EXTERNAL_CONSTRAINTS.md (not machine-readable)
            if ref not in md_text("EXTERNAL_CONSTRAINTS.md"):
                fail(check, f"{owner}: {ref} not found in EXTERNAL_CONSTRAINTS.md")
            return
        if ref.startswith("ASM-"):
            if ref not in md_text("ASSUMPTIONS.md"):
                fail(check, f"{owner}: {ref} not found in ASSUMPTIONS.md")
            return
        if ref.startswith(("cmd:", "ci:", "gate:", "inspection:", "note:")):
            return
        p = REPO / ref.split("#", 1)[0].strip()
        if not p.exists():
            fail(check, f"{owner}: file reference {ref} does not exist")

    # ---- requirements: vocabularies, lifecycle, approval metadata ----
    for r in requirements:
        rid = r.get("id")
        if r.get("status") not in REQ_STATUSES:
            fail(5, f"{rid}: illegal status {r.get('status')!r}")
        if r.get("type") not in REQ_TYPES:
            fail(5, f"{rid}: illegal type {r.get('type')!r}")
        if r.get("origin") not in REQ_ORIGINS:
            fail(5, f"{rid}: illegal origin {r.get('origin')!r}")
        if r.get("priority") not in REQ_PRIORITIES:
            fail(5, f"{rid}: illegal priority {r.get('priority')!r}")
        if r.get("normative_strength") not in REQ_STRENGTH:
            fail(5, f"{rid}: illegal normative_strength {r.get('normative_strength')!r}")
        if r.get("validation_status") not in VALIDATION_STATUSES:
            fail(5, f"{rid}: illegal validation_status {r.get('validation_status')!r}")
        status = r.get("status")
        if status == "APPROVED":
            if not r.get("approver") or not r.get("approval_date"):
                fail(6, f"{rid}: APPROVED without approver/approval_date")
            if r.get("revision", 0) < 1:
                fail(6, f"{rid}: APPROVED without positive revision")
        elif status in {"PROPOSED", "DRAFT"}:
            if r.get("approver"):
                fail(6, f"{rid}: {status} must not carry an approver")
        if status == "SUPERSEDED" and not r.get("superseded_by"):
            fail(5, f"{rid}: SUPERSEDED requires superseded_by pointer")
        if status == "OBSOLETE" and r.get("superseded_by"):
            fail(5, f"{rid}: OBSOLETE must not have a successor (SUPERSEDED != OBSOLETE)")
        if status == "APPROVED" and r.get("verification_method") not in VER_METHODS:
            fail(7, f"{rid}: APPROVED without valid verification_method")
        # references
        for ref in r.get("source") or []:
            resolve(ref, rid)
        for ref in r.get("dependencies") or []:
            resolve(ref, rid)
        for ref in r.get("related_adr") or []:
            resolve(ref, rid)
        for ref in r.get("related_implementation") or []:
            resolve(ref, rid)
        for ref in r.get("related_verification") or []:
            resolve(ref, rid)
        for ref in r.get("related_spec") or []:
            resolve(ref, rid)
        parent = r.get("parent")
        if parent is not None:
            resolve(parent, rid)

    # ---- interfaces ----
    for i in interfaces:
        for ref in i.get("related") or []:
            resolve(ref, i.get("id"))
        if i.get("status") not in REQ_STATUSES:
            fail(5, f"{i.get('id')}: illegal status {i.get('status')!r}")

    # ---- decisions ----
    for d in decisions:
        if d.get("status") not in DECISION_STATUSES:
            fail(5, f"{d.get('id')}: illegal decision status {d.get('status')!r}")
        if d.get("status") == "ACCEPTED" and (not d.get("decided_by") or not d.get("date")):
            fail(6, f"{d.get('id')}: ACCEPTED decision needs decided_by + date")
        for ref in d.get("links") or []:
            resolve(ref, d.get("id"))

    # ---- evidence related refs ----
    for e in evidence:
        for ref in e.get("related") or []:
            resolve(ref, e.get("id"))

    # ---- verification: method vocabulary + verified=>approved ----
    req_by_id = {r.get("id"): r for r in requirements}
    seen_ver = set()
    for v in verification:
        req = v.get("requirement")
        if req not in req_by_id:
            fail(4, f"verification.yaml: unknown requirement {req}")
        if req in seen_ver:
            fail(3, f"verification.yaml: requirement {req} verified twice")
        seen_ver.add(req)
        if v.get("method") not in VER_METHODS:
            fail(5, f"{req}: illegal verification method {v.get('method')!r}")
        if v.get("status") not in VER_STATUSES:
            fail(5, f"{req}: illegal verification status {v.get('status')!r}")
        if v.get("status") == "VERIFIED" and req_by_id.get(req, {}).get("status") != "APPROVED":
            fail(8, f"{req}: VERIFIED but requirement is {req_by_id[req].get('status')}, must be APPROVED")
        for ref in v.get("evidence") or []:
            resolve(ref, f"verification[{req}]")

    # ---- traceability: full coverage, resolvable ----
    seen_tr = set()
    for t in traceability:
        req = t.get("requirement")
        if req not in req_by_id:
            fail(9, f"traceability.yaml: unknown requirement {req}")
        if req in seen_tr:
            fail(9, f"traceability.yaml: requirement {req} traced twice")
        seen_tr.add(req)
        for ref in t.get("evidence") or []:
            resolve(ref, f"trace[{req}]", check=9)
        for ref in t.get("implementations") or []:
            resolve(ref, f"trace[{req}]", check=9)
        if t.get("verification") not in VER_STATUSES:
            fail(9, f"trace[{req}]: illegal verification marker {t.get('verification')!r}")
    for rid in req_by_id:
        if rid not in seen_tr:
            fail(9, f"requirement {rid} missing from traceability.yaml")
        if rid not in seen_ver:
            fail(9, f"requirement {rid} missing from verification.yaml")

    # ---- conflicts: no free interpretation field; refs resolve ----
    for c in conflicts:
        if "current_interpretation" in c:
            fail(5, f"{c.get('id')}: forbidden free 'current_interpretation' field (section 22.3)")
        if "observed_behavior_inference" not in c:
            fail(5, f"{c.get('id')}: must carry observed_behavior_inference (INFERENCE-marked)")
        if "authority_required" not in c:
            fail(5, f"{c.get('id')}: must name required authority level")
        if c.get("status") not in CONFLICT_STATUSES:
            fail(5, f"{c.get('id')}: illegal conflict status {c.get('status')!r}")
        if c.get("status") == "RESOLVED" and not c.get("resolution"):
            fail(5, f"{c.get('id')}: RESOLVED conflict needs resolution text")
        if c.get("status") == "OPEN" and c.get("resolution"):
            fail(5, f"{c.get('id')}: OPEN conflict must not carry a resolution")
        for ref in (c.get("requirement_refs") or []) + (c.get("evidence_refs") or []):
            resolve(ref, c.get("id"))

    # ---- open questions ----
    for q in open_questions:
        if q.get("status") not in OQ_STATUSES:
            fail(5, f"{q.get('id')}: illegal open-question status {q.get('status')!r}")
        for ref in q.get("related") or []:
            resolve(ref, q.get("id"))

    if violations:
        print("RECOVERY VALIDATOR: FAIL")
        for vio in violations:
            print(" ", vio)
        return 1
    print(
        "RECOVERY VALIDATOR: PASS — "
        f"{len(ids)} ids; {len(requirements)} requirements; {len(evidence)} evidence; "
        f"{len(interfaces)} interfaces; {len(decisions)} decisions; "
        f"{len(conflicts)} conflicts; {len(open_questions)} open questions; "
        "9/9 checks clean"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
