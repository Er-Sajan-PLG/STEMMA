#!/usr/bin/env python3
"""R4 — Relation triage report (derived; not a gate).

Produces `reports/relation-triage.json` + `.md`.

It groups `related_to` edges that a human might want to reclassify:

  * `dependency_pairs` — related_to-only edges where a dependency-family
    relation (mathematically_requires / requires / logically_requires /
    depends_on / prerequisite_of) has legal domain/range for the endpoints;
  * `already_specific` — related_to edges between a pair that ALSO has a
    non-associative relation (redundant associative fallback);
  * `measurement_candidates` — related_to edges on payloads where a measurement
    relation fits (quantity↔unit, quantity↔quantity, etc.).

This is **advisory**. The tool never relabels a connection. A curator reviews
the suggestions and, if a change is warranted, authors/supersedes connection(s)
through the existing human review flow.
"""
from __future__ import annotations

import json
import pathlib
import sys
from collections import Counter

import yaml

ROOT = pathlib.Path(__file__).resolve().parent.parent
CONTENT = ROOT / "content"
CONNECTIONS = ROOT / "connections"
REGISTRY_PATH = ROOT / "schema" / "relation-registry.yaml"
OUT_JSON = ROOT / "reports" / "relation-triage.json"
OUT_MD = ROOT / "reports" / "relation-triage.md"

DEPENDENCY_RELATIONS = ("mathematically_requires", "requires", "logically_requires",
                        "depends_on", "prerequisite_of")
MEASUREMENT_RELATIONS = ("expressed_in", "has_unit", "measures", "measured_by",
                         "quantifies", "quantified_by")
RECLASS_PRIORITY = DEPENDENCY_RELATIONS + ("causes", "contributes_to", "results_in",
                                           "explains", "applies_to", "governed_by",
                                           "derived_from", "enables", "used_in",
                                           "applied_to", "equivalent_to")


def _fits(info: dict, stype: str, ttype: str) -> bool:
    domain = info.get("domain") or []
    range_ = info.get("range") or []
    return (not domain or stype in domain) and (not range_ or ttype in range_)


def best_reclassification(conn: dict, entities: dict, registry: dict, desired: tuple[str, ...]) -> str | None:
    src, tgt = conn.get("source"), conn.get("target")
    if not isinstance(src, str) or not isinstance(tgt, str):
        return None
    stype = entities.get(src, {}).get("type")
    ttype = entities.get(tgt, {}).get("type")
    if not stype or not ttype:
        return None
    relations = registry.get("relations") or {}
    for name in desired:
        info = relations.get(name) or {}
        if not info or info.get("family") == "associative":
            continue
        if _fits(info, stype, ttype):
            return name
        inverse = info.get("inverse")
        if inverse and _fits(relations.get(inverse) or {}, stype, ttype):
            return inverse
    return None


def build_report(root: pathlib.Path = ROOT) -> dict:
    entities = {}
    for p in sorted((root / "content").rglob("*.md")):
        raw = p.read_text(encoding="utf-8")
        if not raw.startswith("---"):
            continue
        d = yaml.safe_load(raw.split("---", 2)[1])
        if isinstance(d, dict) and d.get("id"):
            d["_file"] = str(p.relative_to(root))
            entities[d["id"]] = d

    conns = []
    for p in sorted((root / "connections").glob("*.yaml")):
        d = yaml.safe_load(p.read_text(encoding="utf-8"))
        d["_file"] = str(p.relative_to(root))
        conns.append(d)

    registry = yaml.safe_load(REGISTRY_PATH.read_text(encoding="utf-8"))

    pairs_to_relations: dict[frozenset, list[str]] = {}
    for c in conns:
        if c.get("relation") == "related_to":
            continue
        src, tgt = c.get("source"), c.get("target")
        if isinstance(src, str) and isinstance(tgt, str):
            pairs_to_relations.setdefault(frozenset((src, tgt)), []).append(c["relation"])

    related_to_only = []
    already_specific = []
    dependency_pairs = []
    measurement = []
    for c in sorted(conns, key=lambda x: x["id"]):
        if c.get("relation") != "related_to":
            continue
        if (c.get("assertion") or {}).get("status") != "active":
            continue
        pair = frozenset((c.get("source"), c.get("target")))
        specific = pairs_to_relations.get(pair, [])
        if specific:
            already_specific.append({
                "id": c["id"], "source": c["source"], "target": c["target"],
                "specific_relations": sorted(set(specific)),
            })
            continue
        related_to_only.append({"id": c["id"], "source": c["source"], "target": c["target"]})
        dep = best_reclassification(c, entities, registry, DEPENDENCY_RELATIONS)
        if dep:
            dependency_pairs.append({**related_to_only[-1], "suggested": dep})
        meas = best_reclassification(c, entities, registry, MEASUREMENT_RELATIONS)
        if meas:
            measurement.append({**related_to_only[-1], "suggested": meas})

    return {
        "advisory": True,
        "total_related_to": sum(1 for c in conns if c.get("relation") == "related_to"),
        "related_to_only_count": len(related_to_only),
        "already_specific_count": len(already_specific),
        "dependency_pair_count": len(dependency_pairs),
        "measurement_candidate_count": len(measurement),
        "related_to_only": related_to_only,
        "dependency_pairs": dependency_pairs,
        "already_specific": already_specific,
        "measurement_candidates": measurement,
        "by_suggested": dict(Counter(x["suggested"] for x in dependency_pairs + measurement)),
        "note": "Advisory only. Never bulk-relabel; humans author/supersede through review.",
    }


def write_report(report: dict) -> None:
    OUT_JSON.parent.mkdir(parents=True, exist_ok=True)
    OUT_JSON.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    def _lines(title: str, items: list[dict]) -> list[str]:
        out = [f"## {title}", ""]
        if not items:
            out.append("- none")
            out.append("")
            return out
        for x in items[:200]:
            extra = f" → suggested {x['suggested']}" if "suggested" in x else ""
            if "specific_relations" in x:
                extra = f" → also has {', '.join(x['specific_relations'])}"
            out.append(f"- `{x['id']}` {x['source']} -> {x['target']}{extra}")
        if len(items) > 200:
            out.append(f"- … {len(items) - 200} more (see JSON)")
        out.append("")
        return out

    lines = [
        "# Relation triage — related_to reclassification candidates (advisory)",
        "",
        "Generated by `scripts/relation_triage.py`. This report does **not** change",
        "canonical data and does not gate. Reclassification is human review only.",
        "",
        f"- Total `related_to` edges: **{report['total_related_to']}**",
        f"- `related_to`-only edges: **{report['related_to_only_count']}**",
        f"- Pairs with an existing specific relation: **{report['already_specific_count']}**",
        f"- Dependency-family candidates: **{report['dependency_pair_count']}**",
        f"- Measurement candidates: **{report['measurement_candidate_count']}**",
        f"- By suggested relation: `{report['by_suggested']}`",
        "",
    ]
    lines += _lines("Dependency-family candidates", report["dependency_pairs"])
    lines += _lines("Measurement candidates", report["measurement_candidates"])
    lines += _lines("Already-specific pairs (redundant related_to)", report["already_specific"])
    lines += ["", "## Review rule", "",
               "Do not write a bulk relabel. If a suggestion is right, either update",
               "the existing connection via a human `review.py` decision or author a",
               "new connection with the specific relation and supersede the `related_to`",
               "edge. The triage report is a search aid, not an authority.", ""]
    OUT_MD.write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    report = build_report()
    write_report(report)
    print(
        f"OK: relation triage — {report['related_to_only_count']} related_to-only, "
        f"{report['dependency_pair_count']} dependency candidates, "
        f"{report['measurement_candidate_count']} measurement candidates -> "
        f"{OUT_JSON.relative_to(ROOT)}, {OUT_MD.relative_to(ROOT)}"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
