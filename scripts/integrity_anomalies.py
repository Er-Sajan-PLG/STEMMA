#!/usr/bin/env python3
"""B5.5: Contradiction/anomaly detection — ERROR/WARNING/INFO."""
import json
import pathlib
import sys
from collections import defaultdict

import yaml

ROOT = pathlib.Path(__file__).resolve().parent.parent
CONNECTIONS = ROOT / "connections"
REGISTRY = ROOT / "schema" / "relation-registry.yaml"


def main(argv=None):
    args = argv if argv is not None else sys.argv[1:]
    emit_json = "--json" in args
    strict = "--strict" in args
    conns = [yaml.safe_load(p.read_text()) for p in sorted(CONNECTIONS.glob("*.yaml"))]
    registry = yaml.safe_load(REGISTRY.read_text()).get("relations", {})

    anomalies = []

    # ERROR: duplicate claims with different metadata (same source, relation, target, multiple IDs)
    by_triple = defaultdict(list)
    for c in conns:
        by_triple[(c["source"], c["relation"], c["target"])].append(c["id"])
    for triple, ids in by_triple.items():
        if len(ids) > 1:
            anomalies.append({"level": "ERROR", "type": "duplicate_claim", "message": f"Triple {triple} has {len(ids)} canonical connections: {ids}", "ids": ids})

    # ERROR: contradictory relations (same pair has causes and contradicts, or requires and contradicts)
    by_pair = defaultdict(list)
    for c in conns:
        by_pair[(c["source"], c["target"])].append(c)
        by_pair[(c["target"], c["source"])].append(c)  # symmetric check
    for (a, b), lst in by_pair.items():
        rels = {c["relation"] for c in lst}
        if "causes" in rels and "contradicts" in rels:
            anomalies.append({"level": "ERROR", "type": "contradiction", "message": f"{a} causes and contradicts {b}"})
        if "requires" in rels and "contradicts" in rels:
            anomalies.append({"level": "ERROR", "type": "contradiction", "message": f"{a} requires and contradicts {b}"})

    # WARNING: invalid relation/domain/range already caught by validator; here check for unexpected combos
    for c in conns:
        rel = c.get("relation")
        if rel not in registry:
            anomalies.append({"level": "ERROR", "type": "invalid_relation", "message": f"{c['id']} unknown relation {rel}"})

    # WARNING: confidence without basis or vice versa
    for c in conns:
        conf = c.get("assertion", {}).get("confidence")
        basis = c.get("assertion", {}).get("confidence_basis")
        if (conf is not None and basis is None) or (conf is None and basis is not None):
            anomalies.append({"level": "WARNING", "type": "confidence_basis_mismatch", "message": f"{c['id']} confidence/basis mismatch conf={conf} basis={basis}"})

    # INFO: isolated entities (no connections)
    import pathlib as pl

    entities = set()
    for p in (ROOT / "content").rglob("*.md"):
        d = yaml.safe_load(p.read_text().split("---", 2)[1])
        if d.get("id"):
            entities.add(d["id"])
    connected = set()
    for c in conns:
        connected.add(c["source"])
        connected.add(c["target"])
    isolated = entities - connected
    if isolated:
        anomalies.append({"level": "INFO", "type": "isolated_entities", "message": f"{len(isolated)} entities have no connections", "ids": sorted(list(isolated))[:10]})

    # INFO: duplicate assertion identities with different review states
    for triple, ids in by_triple.items():
        if len(ids) > 1:
            reviews = set()
            for c in conns:
                if (c["source"], c["relation"], c["target"]) == triple:
                    reviews.add(c.get("assertion", {}).get("review", {}).get("status"))
            if len(reviews) > 1:
                anomalies.append({"level": "WARNING", "type": "conflicting_review", "message": f"Triple {triple} has conflicting reviews {reviews}"})

    by_level = {"ERROR": 0, "WARNING": 0, "INFO": 0}
    for a in anomalies:
        by_level[a["level"]] += 1

    out_json = ROOT / "reports" / "integrity-anomalies.json"
    out_json.write_text(json.dumps({"anomalies": anomalies, "counts": by_level, "total": len(anomalies)}, indent=2) + "\n")
    out_md = ROOT / "reports" / "integrity-anomalies.md"
    out_md.write_text(
        f"""# Integrity Anomalies — v0.2

- Total: {len(anomalies)} (ERROR {by_level['ERROR']}, WARNING {by_level['WARNING']}, INFO {by_level['INFO']})

| Level | Type | Message |
|-------|------|---------|
"""
        + "\n".join(f"| {a['level']} | {a['type']} | {a['message']} |" for a in anomalies[:50])
        + "\n\nFull: `reports/integrity-anomalies.json`\n"
    )
    # ADR-0033: this is an ADVISORY report. It always writes the report and
    # returns 0 in the default verify chain (ERRORs are surfaced, not
    # gate-blocking). `--strict` lets a human/CI opt into failing on ERRORs.
    if emit_json:
        print(json.dumps({
            "advisory": True,
            "counts": by_level,
            "total": len(anomalies),
            "anomalies": anomalies,
        }, indent=2, sort_keys=True))
    else:
        print(f"OK: anomalies total={len(anomalies)} ERROR={by_level['ERROR']} WARNING={by_level['WARNING']} INFO={by_level['INFO']}")
    return 1 if strict and by_level["ERROR"] > 0 else 0


if __name__ == "__main__":
    import sys

    sys.exit(main())
