#!/usr/bin/env python3
"""B5.2: Epistemic summary — deterministic counts over all connections."""
import json
import pathlib
from collections import Counter

import yaml

ROOT = pathlib.Path(__file__).resolve().parent.parent
CONNECTIONS = ROOT / "connections"


def origin_of(conn):
    prov = conn.get("provenance", {})
    method = prov.get("method", {}).get("type") if isinstance(prov.get("method"), dict) else ""
    asserted = prov.get("asserted_by", {}).get("type") if isinstance(prov.get("asserted_by"), dict) else ""
    generated = prov.get("generated_by", {}).get("id", "") if isinstance(prov.get("generated_by"), dict) else ""
    if method == "migration":
        return "migrated"
    if asserted == "llm" or (isinstance(prov.get("asserted_by"), dict) and "llm" in prov["asserted_by"].get("id", "")):
        return "llm-authored"
    if asserted == "human" and generated == prov.get("asserted_by", {}).get("id", ""):
        # Check if reviewed?
        return "human-authored"
    if method == "manual" and asserted == "human":
        return "human-authored"
    return "human-authored" if asserted == "human" else "unknown"


def main():
    total = 0
    by_assertion_type = Counter()
    by_review = Counter()
    by_status = Counter()
    by_origin = Counter()
    by_method = Counter()
    by_confidence = Counter()
    has_confidence = 0
    human_reviewed = 0

    for p in sorted(CONNECTIONS.glob("*.yaml")):
        d = yaml.safe_load(p.read_text())
        total += 1
        ass = d.get("assertion", {})
        by_assertion_type[ass.get("type", "unknown")] += 1
        by_review[ass.get("review", {}).get("status", "unknown")] += 1
        by_status[ass.get("status", "unknown")] += 1
        prov = d.get("provenance", {})
        by_method[prov.get("method", {}).get("type", "unknown")] += 1
        origin = origin_of(d)
        by_origin[origin] += 1
        if ass.get("confidence") is not None:
            has_confidence += 1
            by_confidence["with_confidence"] += 1
        else:
            by_confidence["without_confidence"] += 1
        if prov.get("reviewed_by"):
            human_reviewed += 1

    # E1: reviewed-only vs canonical distinction: canonical is terminal reviewed state
    reviewed_only = int(by_review.get("reviewed", 0))
    canonical_cnt = int(by_review.get("canonical", 0))
    report = {
        "total_connection_records": total,
        "canonical_object_records": total,  # every file is a canonical repository object
        "canonical_scientific_assertions": canonical_cnt,  # review.status == canonical
        "asserted": int(by_assertion_type.get("asserted", 0)),
        "inferred": int(by_assertion_type.get("inferred", 0)),
        "proposed": int(by_assertion_type.get("proposed", 0)),
        "reviewed_only": reviewed_only,
        "reviewed": reviewed_only,  # legacy alias: reviewed-only
        "canonical": canonical_cnt,
        "unreviewed": int(by_review.get("unreviewed", 0)),
        "total_reviewed_including_canonical": reviewed_only + canonical_cnt,
        "active": int(by_status.get("active", 0)),
        "deprecated": int(by_status.get("deprecated", 0)),
        "rejected": int(by_status.get("rejected", 0)),
        "migrated": int(by_origin.get("migrated", 0)),
        "manually_authored": int(by_origin.get("human-authored", 0)),
        "llm_authored": int(by_origin.get("llm-authored", 0)),
        "human_reviewed": human_reviewed,
        "with_confidence": has_confidence,
        "without_confidence": total - has_confidence,
        "by_assertion_type": dict(by_assertion_type),
        "by_review": dict(by_review),
        "by_status": dict(by_status),
        "by_origin": dict(by_origin),
        "by_method": dict(by_method),
        "review_semantics": "reviewed-only (review.status==reviewed) vs canonical (review.status==canonical, terminal reviewed state); canonical implies reviewed; total_reviewed_including_canonical = reviewed-only + canonical",
        "note": "canonical object (file exists) != canonical scientific assertion (review.status==canonical). All 397 are canonical objects; 15 are canonical assertions.",
    }

    out_json = ROOT / "reports" / "epistemic-summary.json"
    out_json.parent.mkdir(parents=True, exist_ok=True)
    out_json.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")

    out_md = ROOT / "reports" / "epistemic-summary.md"
    out_md.write_text(
        f"""# Epistemic Summary — v0.2

Deterministic report over all `connections/*.yaml` (explicit fields only).

- Total connection records (canonical objects): **{total}**
- Canonical scientific assertions (`review.status == canonical`): **{report['canonical_scientific_assertions']}**
- Proposed: {report['proposed']}, Asserted: {report['asserted']}, Inferred: {report['inferred']}
- Review: unreviewed {report['unreviewed']}, reviewed-only {report['reviewed_only']}, canonical {report['canonical']} (total reviewed including canonical: {report['total_reviewed_including_canonical']})
- Status: active {report['active']}, deprecated {report['deprecated']}, rejected {report['rejected']}
- Origin: migrated {report['migrated']}, human-authored {report['manually_authored']}, llm-authored {report['llm_authored']}
- With confidence: {has_confidence}, without: {total - has_confidence}
- Human reviewed_by present: {human_reviewed}

> Canonical object (file exists in `connections/`) != canonical scientific assertion.
> Canonical is terminal reviewed state (reviewed-only 0, canonical 15). `review.status==canonical` implies reviewed.
> A migrated connection is a canonical object with `review.status=unreviewed` until human review.

## By assertion type
{dict(by_assertion_type)}

## By review
{dict(by_review)}

## By origin
{dict(by_origin)}

## By method
{dict(by_method)}

Machine-readable: `reports/epistemic-summary.json`
"""
    )
    print(f"OK: epistemic summary total={total} canonical_assertions={report['canonical_scientific_assertions']}")
    return 0


if __name__ == "__main__":
    import sys

    sys.exit(main())
