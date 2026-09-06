#!/usr/bin/env python3
"""E6.1 — Dependency-edge review campaign: batch generator (plan v2 E6.1; audit F2/R14).

Scope: every active `mathematically_requires` / `logically_requires` connection.
This script NEVER changes review status. It produces human worksheets:

  reports/dependency-review-campaign/campaign-schedule.md   overview + progress dashboard
  reports/dependency-review-campaign/batch-NN.md            human-readable worksheet
  reports/dependency-review-campaign/batch-NN.yaml          machine-readable decision sheet

A reviewer fills the `decision:` field of each item in batch-NN.yaml
(accept | canonical | reject | defer), optionally `reason:` and `evidence:`, and
runs `python3 scripts/apply_review_decisions.py <batch-NN.yaml> --reviewer human:...`
which applies the transitions through the curation state machine.

Prioritisation (deterministic, per CURATION-PROTOCOL §9 / plan v2 E6.1):
  score = pagerank(source)+pagerank(target)  (from exports/knowledge.extended.json)
        + 0.02 * (in_degree(target))          (foundational targets first)
        + 0.05 if either endpoint is a law/equation
  ties broken by connection id. Already-reviewed edges are listed for
  completeness but excluded from batches. Batch size default 40 (25–50 window).

Pre-checks per edge (advisory, not decisions):
  * registry domain/range legality for the endpoint types
  * whether the requiring entity's `equation`/`definition` mentions the
    target's `symbol` or `name` (textual support hint)
  * a cycle-free check is already guaranteed by validate.py
  * whether an evidence item exists; if not, the family rule (dependency →
    derivation/definition/prerequisite documentation) is quoted.

Usage: python3 scripts/dependency_review_campaign.py [--batch-size 40] [--reviewer human:reviewer.physics-001]
"""
from __future__ import annotations

import argparse
import json
import pathlib
import re
import sys

import yaml

ROOT = pathlib.Path(__file__).resolve().parent.parent
CONNECTIONS = ROOT / "connections"
CONTENT = ROOT / "content"
EXTENDED = ROOT / "exports" / "knowledge.extended.json"
OUT = ROOT / "reports" / "dependency-review-campaign"
DEP_RELATIONS = ("mathematically_requires", "logically_requires")
FAMILY_RULE = ("dependency family (CURATION-PROTOCOL §3): explicit derivation, definition, "
               "or prerequisite documentation; equation where applicable")


def load_entities() -> dict[str, dict]:
    ents = {}
    for p in sorted(CONTENT.rglob("*.md")):
        d = yaml.safe_load(p.read_text(encoding="utf-8").split("---", 2)[1])
        if d.get("id"):
            d["_file"] = str(p.relative_to(ROOT))
            ents[d["id"]] = d
    return ents


def load_connections() -> list[dict]:
    out = []
    for p in sorted(CONNECTIONS.glob("*.yaml")):
        d = yaml.safe_load(p.read_text(encoding="utf-8"))
        d["_file"] = str(p.relative_to(ROOT))
        out.append(d)
    return out


def centrality() -> dict[str, dict]:
    if not EXTENDED.exists():
        return {}
    return json.loads(EXTENDED.read_text(encoding="utf-8")).get("derived", {}).get("centrality", {}).get("all", {})


def text_support(src: dict, tgt: dict) -> str:
    """Advisory hint: does the source entity's text mention the target?"""
    hay = " ".join(str(src.get(k) or "") for k in ("definition", "equation", "symbol", "notes")).lower()
    hits = []
    name = str(tgt.get("name") or "").lower()
    if name and name in hay:
        hits.append(f"name '{tgt['name']}'")
    sym = tgt.get("symbol")
    if isinstance(sym, str) and sym.strip():
        s = sym.split("(")[0].strip()
        if s and re.search(r"(?<![A-Za-z])" + re.escape(s) + r"(?![A-Za-z])", str(src.get("equation") or "")):
            hits.append(f"symbol '{s}' in equation")
    return "; ".join(hits) if hits else "none found (check definition/derivation manually)"


def domain_range_ok(conn: dict, ents: dict, registry: dict) -> str:
    info = registry.get(conn["relation"], {})
    st = ents.get(conn["source"], {}).get("type")
    tt = ents.get(conn["target"], {}).get("type")
    problems = []
    if info.get("domain") and st not in info["domain"]:
        problems.append(f"source type {st} not in domain")
    if info.get("range") and tt not in info["range"]:
        problems.append(f"target type {tt} not in range")
    return "ok" if not problems else "; ".join(problems)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--batch-size", type=int, default=40)
    ap.add_argument("--reviewer", default="human:reviewer.physics-001")
    args = ap.parse_args()
    if not 25 <= args.batch_size <= 50:
        print("batch size must be within 25–50 (plan v2 E6.1)", file=sys.stderr)
        return 2

    ents = load_entities()
    conns = load_connections()
    cent = centrality()
    registry = yaml.safe_load((ROOT / "schema/relation-registry.yaml").read_text(encoding="utf-8"))["relations"]

    edges = [c for c in conns if c["relation"] in DEP_RELATIONS and c["assertion"]["status"] == "active"]
    total = len(edges)
    done = [c for c in edges if c["assertion"]["review"]["status"] in ("reviewed", "canonical")]
    pending = [c for c in edges if c["assertion"]["review"]["status"] == "unreviewed"]

    def score(c: dict) -> float:
        s = cent.get(c["source"], {}); t = cent.get(c["target"], {})
        val = s.get("pagerank", 0.0) + t.get("pagerank", 0.0) + 0.02 * t.get("in_degree", 0)
        if ents.get(c["source"], {}).get("type") in ("law", "equation") or ents.get(c["target"], {}).get("type") in ("law", "equation"):
            val += 0.05
        return round(val, 6)

    pending.sort(key=lambda c: (-score(c), c["id"]))
    batches = [pending[i:i + args.batch_size] for i in range(0, len(pending), args.batch_size)]

    OUT.mkdir(parents=True, exist_ok=True)
    # Remove stale batch files so the directory is a pure function of the tree.
    for old in OUT.glob("batch-*"):
        old.unlink()

    for bi, batch in enumerate(batches, start=1):
        items = []
        md = [f"# E6.1 Dependency-edge review — Batch {bi:02d}", "",
              f"{len(batch)} edges · reviewer: `{args.reviewer}` · relations: {', '.join(DEP_RELATIONS)}", "",
              "Decision vocabulary: **accept** (→ reviewed), **canonical** (→ reviewed → canonical, evidence required),",
              "**reject** (reason required), **defer**. Fill `decision:` in the companion YAML, then run:",
              "", f"```bash", f"python3 scripts/apply_review_decisions.py reports/dependency-review-campaign/batch-{bi:02d}.yaml --reviewer {args.reviewer}", "```", "",
              "| # | Connection | Assertion | Types | Domain/range | Text support | Evidence | Score |",
              "|---|-----------|-----------|-------|--------------|--------------|----------|-------|"]
        for i, c in enumerate(batch, start=1):
            s = ents.get(c["source"], {}); t = ents.get(c["target"], {})
            dr = domain_range_ok(c, ents, registry)
            ts = text_support(s, t)
            ev = c.get("evidence") or []
            ev_txt = f"{len(ev)} item(s)" if ev else "none — " + FAMILY_RULE
            md.append(f"| {i} | `{c['id']}` | **{s.get('name', c['source'])}** {c['relation'].replace('_', ' ')} **{t.get('name', c['target'])}** | {s.get('type')}→{t.get('type')} | {dr} | {ts} | {ev_txt} | {score(c)} |")
            items.append({
                "id": c["id"],
                "claim": f"{s.get('name', c['source'])} {c['relation']} {t.get('name', c['target'])}",
                "source": c["source"], "relation": c["relation"], "target": c["target"],
                "source_definition": (s.get("definition") or "")[:300],
                "target_definition": (t.get("definition") or "")[:300],
                "source_equation": s.get("equation"),
                "prechecks": {"domain_range": dr, "text_support": ts, "has_evidence": bool(ev)},
                "decision": None,
                "reason": None,
                "evidence": None,
            })
        md += ["", "## Reviewer notes", "",
               "- A schema-valid edge is not a scientifically accepted prerequisite (protocol §1).",
               "- `mathematically_requires`: the target appears in the source's defining equation/derivation.",
               "- `logically_requires`: the source cannot be defined/understood without the target concept.",
               "- If the true relation is weaker, **reject** with reason `should be related_to` (do not silently relabel; a new connection is authored instead).",
               "- Migrated origin (`asserted_by: unknown:legacy-relationship`) is preserved on acceptance (protocol §6).", ""]
        (OUT / f"batch-{bi:02d}.md").write_text("\n".join(md), encoding="utf-8")
        (OUT / f"batch-{bi:02d}.yaml").write_text(yaml.safe_dump({
            "batch": bi, "campaign": "E6.1 dependency-edge review", "reviewer": args.reviewer,
            "instructions": "Set decision to accept|canonical|reject|defer per item. canonical requires evidence "
                            "(list of {type, description, source_ref?, locator?}). reject requires reason.",
            "items": items,
        }, sort_keys=False, allow_unicode=True, width=110), encoding="utf-8")

    # Dashboard / schedule (E6.7 slice: dependency-edge review % per domain)
    by_domain: dict[str, dict[str, int]] = {}
    for c in edges:
        dom = (c.get("context") or {}).get("domain") or ents.get(c["source"], {}).get("domain", "unknown")
        d = by_domain.setdefault(dom, {"total": 0, "reviewed": 0})
        d["total"] += 1
        if c["assertion"]["review"]["status"] in ("reviewed", "canonical"):
            d["reviewed"] += 1
    pct = 100.0 * len(done) / total if total else 0.0
    lines = ["# E6.1 — Dependency-edge review campaign", "",
             "Generated by `scripts/dependency_review_campaign.py` (deterministic; never edits review status).", "",
             f"- Scope: **{total}** active dependency edges ({', '.join(DEP_RELATIONS)})",
             f"- Reviewed or canonical: **{len(done)}** ({pct:.1f}%) · pending: **{len(pending)}**",
             f"- Batches pending: **{len(batches)}** × ≤{args.batch_size} (weekly cadence per plan v2 E6.1)",
             f"- Target (plan v2 §4): 188 → 100% reviewed", "",
             "## Progress by domain", "", "| Domain | Reviewed | Total | % |", "|--------|----------|-------|---|"]
    for dom in sorted(by_domain):
        d = by_domain[dom]
        lines.append(f"| {dom} | {d['reviewed']} | {d['total']} | {100.0 * d['reviewed'] / d['total']:.0f}% |")
    lines += ["", "## Schedule", "", "| Batch | Edges | Top edge | Worksheet |", "|-------|-------|----------|-----------|"]
    for bi, batch in enumerate(batches, start=1):
        top = batch[0]
        lines.append(f"| {bi:02d} | {len(batch)} | {ents.get(top['source'], {}).get('name')} → {ents.get(top['target'], {}).get('name')} | `batch-{bi:02d}.md` / `.yaml` |")
    lines += ["", "## Already reviewed (excluded from batches)", ""]
    for c in sorted(done, key=lambda c: c["id"]):
        lines.append(f"- `{c['id']}` {ents.get(c['source'], {}).get('name')} {c['relation']} {ents.get(c['target'], {}).get('name')} — {c['assertion']['review']['status']}")
    lines.append("")
    (OUT / "campaign-schedule.md").write_text("\n".join(lines), encoding="utf-8")
    (OUT / "campaign-status.json").write_text(json.dumps({
        "total": total, "reviewed": len(done), "pending": len(pending), "percent_reviewed": round(pct, 1),
        "batches": len(batches), "batch_size": args.batch_size, "by_domain": by_domain,
    }, indent=2) + "\n", encoding="utf-8")
    print(f"OK: E6.1 campaign — {total} dependency edges, {len(done)} reviewed ({pct:.1f}%), "
          f"{len(pending)} pending in {len(batches)} batches -> {OUT.relative_to(ROOT)}/")
    return 0


if __name__ == "__main__":
    sys.exit(main())
