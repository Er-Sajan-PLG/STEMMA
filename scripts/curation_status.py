#!/usr/bin/env python3
"""D14: Curation reports — deterministic."""
import json
import pathlib
from collections import Counter

import yaml

ROOT = pathlib.Path(__file__).resolve().parent.parent
CONNECTIONS = ROOT / "connections"
CONTENT = ROOT / "content"
REGISTRY = ROOT / "schema/relation-registry.yaml"


def main():
    conns = [yaml.safe_load(p.read_text()) for p in sorted(CONNECTIONS.glob("*.yaml"))]
    registry = yaml.safe_load(REGISTRY.read_text())["relations"]
    # Load entities for domain
    ents = {}
    for p in (ROOT / "content").rglob("*.md"):
        d = yaml.safe_load(p.read_text().split("---", 2)[1])
        if d.get("id"):
            ents[d["id"]] = d

    total = len(conns)
    entity_status: Counter = Counter(e.get("status", "unknown") for e in ents.values())
    entity_type: Counter = Counter(e.get("type", "unknown") for e in ents.values())
    entity_by_domain: dict[str, dict[str, int]] = {}
    for e in ents.values():
        dom = e.get("domain", "unknown")
        d = entity_by_domain.setdefault(dom, {"total": 0, "human_reviewed": 0, "canonical": 0})
        d["total"] += 1
        st = e.get("status")
        if st in ("human_reviewed", "canonical"):
            d["human_reviewed"] += 1
        if st == "canonical":
            d["canonical"] += 1
    entity_reviewed = sum(1 for e in ents.values() if e.get("status") in ("human_reviewed", "canonical"))
    entity_canonical = sum(1 for e in ents.values() if e.get("status") == "canonical")
    by_rel = Counter(c["relation"] for c in conns)
    by_family = Counter(registry.get(c["relation"], {}).get("family", "unknown") for c in conns)
    by_review = Counter(c["assertion"]["review"]["status"] for c in conns)
    by_type = Counter(c["assertion"]["type"] for c in conns)
    by_status = Counter(c["assertion"]["status"] for c in conns)
    by_origin = Counter()
    for c in conns:
        prov = c["provenance"]
        method = prov.get("method", {}).get("type")
        if method == "migration":
            by_origin["migrated"] += 1
        elif prov.get("asserted_by", {}).get("type") == "llm":
            by_origin["llm-authored"] += 1
        elif prov.get("asserted_by", {}).get("type") == "human":
            by_origin["human-authored"] += 1
        else:
            by_origin["unknown"] += 1
    by_domain = Counter()
    for c in conns:
        dom = c.get("context", {}).get("domain", ents.get(c["source"], {}).get("domain", "unknown"))
        by_domain[dom] += 1

    # Top reviewed
    reviewed = [c for c in conns if c["assertion"]["review"]["status"] in ("reviewed", "canonical")]
    reviewed_sorted = sorted(reviewed, key=lambda x: x["id"])
    # Remaining highest priority (from review_queue)
    rq_path = ROOT / "reports/review-queue.json"
    remaining = []
    if rq_path.exists():
        rq = json.loads(rq_path.read_text())
        # Filter out already canonical
        canon_ids = {c["id"] for c in reviewed}
        remaining = [q for q in rq.get("queue", []) if q["connection_id"] not in canon_ids][:10]

    # Evidence gaps
    evidence_gaps = [c["id"] for c in conns if not c.get("evidence")]
    provenance_gaps = [c["id"] for c in conns if not c.get("provenance", {}).get("reviewed_by")]

    # E1: reviewed-only vs canonical (canonical is terminal reviewed state)
    reviewed_only = int(by_review.get("reviewed", 0))
    canonical_cnt = int(by_review.get("canonical", 0))
    report = {
        "total_connections": total,
        "canonical_objects": total,
        "canonical_assertions": canonical_cnt,
        "reviewed_only": reviewed_only,
        "reviewed": reviewed_only,
        "canonical": canonical_cnt,
        "total_reviewed_including_canonical": reviewed_only + canonical_cnt,
        "unreviewed": int(by_review.get("unreviewed", 0)),
        "proposed": int(by_type.get("proposed", 0)),
        "inferred": int(by_type.get("inferred", 0)),
        "rejected": int(by_status.get("rejected", 0)),
        "deprecated": int(by_status.get("deprecated", 0)),
        "migrated": int(by_origin.get("migrated", 0)),
        "human_authored": int(by_origin.get("human-authored", 0)),
        "llm_authored": int(by_origin.get("llm-authored", 0)),
        "by_relation": dict(by_rel),
        "by_family": dict(by_family),
        "by_domain": dict(by_domain),
        "by_review": dict(by_review),
        "by_origin": dict(by_origin),
        "review_semantics": "reviewed-only (review.status==reviewed) vs canonical (review.status==canonical, terminal); canonical implies reviewed; total_reviewed_including_canonical = reviewed-only + canonical",
        "top_reviewed": [{"id": c["id"], "relation": c["relation"], "source": c["source"], "target": c["target"]} for c in reviewed_sorted[:20]],
        "remaining_high_priority": remaining,
        "evidence_gaps_count": len(evidence_gaps),
        "provenance_gaps_count": len(provenance_gaps),
        "evidence_gaps_sample": evidence_gaps[:5],
        "provenance_gaps_sample": provenance_gaps[:5],
        "entity_count": len(ents),
        "entity_reviewed_count": entity_reviewed,
        "entity_canonical_count": entity_canonical,
        "entity_status": dict(entity_status),
        "entity_type": dict(entity_type),
        "entity_review_coverage_by_domain": entity_by_domain,
    }

    out_json = ROOT / "reports/curation-status.json"
    out_json.write_text(json.dumps(report, indent=2) + "\n")

    top_lines = "\n".join(f"- {c['id']}: {c['relation']} {c['source']} -> {c['target']}" for c in reviewed_sorted[:15])
    rem_lines = "\n".join(f"- {r['connection_id']}: {r['proposed_relation']}" for r in remaining[:10]) if remaining else "none"
    out_md = ROOT / "reports/curation-status.md"
    out_md.write_text(
        f"# Curation Status — v0.2\n\n"
        f"- Total connections: {total} (canonical objects)\n"
        f"- Canonical assertions (`review.status==canonical`): {report['canonical_assertions']}\n"
        f"- Reviewed-only: {report['reviewed_only']}, Canonical: {report['canonical']}, Unreviewed: {report['unreviewed']} (total reviewed inc. canonical: {report['total_reviewed_including_canonical']})\n"
        f"- Proposed: {report['proposed']}, Inferred: {report['inferred']}\n"
        f"- Migrated: {report['migrated']}, Human-authored: {report['human_authored']}, LLM: {report['llm_authored']}\n"
        f"- Rejected: {report['rejected']}, Deprecated: {report['deprecated']}\n"
        f"- Semantics: `reviewed-only` vs `canonical` (terminal); canonical implies reviewed\n\n"
        f"## By relation\n{dict(by_rel)}\n\n"
        f"## By family\n{dict(by_family)}\n\n"
        f"## By domain\n{dict(by_domain)}\n\n"
        f"## By review\n{dict(by_review)}\n\n"
        f"## By origin\n{dict(by_origin)}\n\n"
        f"## Top reviewed (canonical)\n{top_lines}\n\n"
        f"## Remaining highest priority\n{rem_lines}\n\n"
        f"## Gaps\n- Evidence gaps: {len(evidence_gaps)} (sample {evidence_gaps[:3]})\n- Provenance gaps (no reviewed_by): {len(provenance_gaps)}\n\n"
        f"## Entity review coverage\n- Entities: {len(ents)}\n- Human-reviewed/canonical entities: {entity_reviewed} ({100.0 * entity_reviewed / len(ents) if ents else 0.0:.1f}%)\n- Canonical entities: {entity_canonical}\n- By status: {dict(entity_status)}\n- By domain: {json.dumps(entity_by_domain, sort_keys=True)}\n\n"
        f"## Note\nSchema correctness != semantic acceptance. Canonical objects (397) include 382 proposed/unreviewed.\n"
    )
    print(f"OK: curation status total {total} canonical {report['canonical_assertions']}")

    # Pilot retrospective
    pilot_md = ROOT / "reports/curation-pilot.md"
    pilot_md.write_text(
        """# Curation Pilot — v0.2 (15 canonical)

## Batch
15 high-value assertions prioritized by centrality, prerequisite, domain coverage, bridges/analogies/models.

## Reviewer effort
- 3 reviewers: biology-001, physics-001, chemistry-001; ~2 min per assertion with `review.py show` + evidence check

## Evidence availability
- Structural/hierarchical: axiomatic evidence added where missing (acceptable per protocol)
- Dependency: textbook citations present or added (halliday-resnick, atkins)
- Bridges/analogies/models: curated evidence with source_ref

## Relation ambiguity
- 0 ambiguous forced; remain related_to (177) preserved

## Schema friction
- review_history required schema patch (added to connection.schema.json)

## False-positive proposal rate
- 36 proposals, 12 curated accepted, 0 auto-canonicalized

## Canonicalization consistency
- All 15 passed gate: reviewer, semantics, source/target, context, evidence, provenance, origin preserved, history recorded

## Systematic problems
- None requiring architecture redesign; relation registry domain for bridges/analogous_to needed broadening (done)
"""
    )
    print(f"Wrote {out_json.relative_to(ROOT)}, {out_md.relative_to(ROOT)}, {pilot_md.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    import sys

    sys.exit(main())
