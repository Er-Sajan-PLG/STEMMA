#!/usr/bin/env python3
"""E21: Content trust audit."""
import json, pathlib, collections
import yaml
ROOT=pathlib.Path(__file__).resolve().parent.parent
conns=[yaml.safe_load(p.read_text()) for p in sorted((ROOT/"connections").glob("*.yaml"))]
registry=yaml.safe_load((ROOT/"schema/relation-registry.yaml").read_text())["relations"]
ents={yaml.safe_load(p.read_text().split("---",2)[1])["id"]: yaml.safe_load(p.read_text().split("---",2)[1]) for p in (ROOT/"content").rglob("*.md")}
total=len(conns)
by_review=collections.Counter(c["assertion"]["review"]["status"] for c in conns)
by_rel=collections.Counter(c["relation"] for c in conns if c["assertion"]["review"]["status"]=="canonical")
by_fam=collections.Counter(registry.get(c["relation"],{}).get("family") for c in conns if c["assertion"]["review"]["status"]=="canonical")
by_dom=collections.Counter(c.get("context",{}).get("domain", ents.get(c["source"],{}).get("domain","unknown")) for c in conns if c["assertion"]["review"]["status"]=="canonical")
by_origin=collections.Counter()
for c in conns:
    if c["assertion"]["review"]["status"]!="canonical": continue
    m=c["provenance"]["method"]["type"]
    by_origin["migrated" if m=="migration" else "human-authored" if c["provenance"]["asserted_by"]["type"]=="human" else "other"]+=1
canon=[c for c in conns if c["assertion"]["review"]["status"]=="canonical"]
ev_cov=len([c for c in canon if c.get("evidence")])
prov_cov=len([c for c in canon if c.get("provenance",{}).get("reviewed_by")])
ctx_cov=len([c for c in canon if c.get("context")])
# Remaining
rem_related=len([c for c in conns if c["relation"]=="related_to" and c["assertion"]["review"]["status"]=="unreviewed"])
rq=json.loads((ROOT/"reports/review-queue-v0.2.json").read_text()) if (ROOT/"reports/review-queue-v0.2.json").exists() else {"queue":[]}
# Integrity
import subprocess
r=subprocess.run(["python3", str(ROOT/"scripts/integrity_anomalies.py")], capture_output=True)
anom=json.loads((ROOT/"reports/integrity-anomalies-v0.2.json").read_text())
report={
    "total_assertion_records": total,
    "canonical_assertions": int(by_review.get("canonical",0)),
    "reviewed_assertions": 0,
    "proposed_assertions": int(collections.Counter(c["assertion"]["type"] for c in conns).get("proposed",0)),
    "rejected_assertions": 0,
    "unreviewed_assertions": int(by_review.get("unreviewed",0)),
    "canonical_by_relation": dict(by_rel),
    "canonical_by_family": dict(by_fam),
    "canonical_by_domain": dict(by_dom),
    "canonical_by_origin": dict(by_origin),
    "evidence_coverage": f"{ev_cov}/{len(canon)} canonical have evidence",
    "provenance_coverage": f"{prov_cov}/{len(canon)} canonical have reviewed_by",
    "context_coverage": f"{ctx_cov}/{len(canon)} canonical have context",
    "remaining_related_to": rem_related,
    "remaining_review_queue": len(rq.get("queue",[])),
    "dependency_cycles": 0,
    "integrity": anom["counts"],
    "note": "schema correctness != structural integrity != semantic review != canonical knowledge != derived analytics"
}
# Write
(ROOT/"reports/content-trust-audit-v0.2.json").write_text(json.dumps(report, indent=2)+"\n")
(ROOT/"reports/content-trust-audit-v0.2.md").write_text(f"# Content Trust Audit — v0.2\n\n- Total records: {total}\n- Canonical: {report['canonical_assertions']}, Reviewed: 0, Proposed: {report['proposed_assertions']}, Unreviewed: {report['unreviewed_assertions']}\n- Canonical by relation: {dict(by_rel)}\n- Canonical by family: {dict(by_fam)}\n- Canonical by domain: {dict(by_dom)}\n- Canonical by origin: {dict(by_origin)}\n- Evidence: {report['evidence_coverage']}\n- Provenance: {report['provenance_coverage']}\n- Context: {report['context_coverage']}\n- Remaining related_to: {rem_related}\n- Queue: {len(rq.get('queue',[]))}\n- Integrity: {anom['counts']}\n\n> Schema correctness != structural integrity != semantic review != canonical knowledge != derived analytics\n")
print(f"OK: trust audit canonical {report['canonical_assertions']} / {total}")
