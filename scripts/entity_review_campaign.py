#!/usr/bin/env python3
"""R6 — Entity review campaign (human worksheet generator; never auto-reviews).

Produces reports/entity-review-campaign/:
  campaign-schedule.md   dashboard + progress
  batch-NN.md            human-readable worksheet
  batch-NN.yaml          machine-readable worksheet (decision: None)
  campaign-status.json

Prioritisation (deterministic):
  * pending entities = status != human_reviewed/canonical
  * score = pagerank (exports/knowledge.extended.json) + small centrality bonus,
    ties broken by id
  * batch-01 is the "seed concepts" pass: top `--per-domain` (default 5) per domain;
    remaining pending entities follow as later batches of `--batch-size`.

This script NEVER edits status. Applying a worksheet is a HUMAN action via
`scripts/review_entity.py review/canonicalize <id> --reviewer human:...`.
"""
from __future__ import annotations

import argparse
import json
import pathlib
import sys

import yaml

ROOT = pathlib.Path(__file__).resolve().parent.parent
CONTENT = ROOT / "content"
EXTENDED = ROOT / "exports" / "knowledge.extended.json"
OUT = ROOT / "reports" / "entity-review-campaign"
AGENTS = ROOT / "schema" / "agent-registry.yaml"


def load_entities() -> dict[str, dict]:
    out = {}
    for p in sorted(CONTENT.rglob("*.md")):
        raw = p.read_text(encoding="utf-8")
        if not raw.startswith("---"):
            continue
        d = yaml.safe_load(raw.split("---", 2)[1])
        if isinstance(d, dict) and d.get("id"):
            d["_file"] = str(p.relative_to(ROOT))
            out[d["id"]] = d
    return out


def centrality() -> dict[str, dict]:
    if not EXTENDED.exists():
        return {}
    return json.loads(EXTENDED.read_text(encoding="utf-8")).get("derived", {}).get("centrality", {}).get("all", {})


def pending_entities(entities: dict[str, dict]) -> list[dict]:
    return [e for e in entities.values() if e.get("status") not in ("human_reviewed", "canonical")]


def score_entity(e: dict, cent: dict) -> float:
    c = cent.get(e.get("id"), {})
    return round(c.get("pagerank", 0.0) + 0.001 * c.get("degree", 0), 6)


def build_batches(entities: dict[str, dict], *, per_domain: int = 5, batch_size: int = 40) -> list[list[dict]]:
    pend = pending_entities(entities)
    cent = centrality()
    pend.sort(key=lambda e: (-score_entity(e, cent), e.get("id", "")))
    by_domain: dict[str, list[dict]] = {}
    for e in pend:
        by_domain.setdefault(e.get("domain", "unknown"), []).append(e)
    seeds = []
    for domain in sorted(by_domain):
        seeds.extend(by_domain[domain][:per_domain])
    # Re-sort the deterministic seed set.
    seeds.sort(key=lambda e: (-score_entity(e, cent), e.get("id", "")))
    seen = {e.get("id") for e in seeds}
    remaining = [e for e in pend if e.get("id") not in seen]
    batches = []
    if seeds:
        batches.append(seeds)
    for i in range(0, len(remaining), batch_size):
        batches.append(remaining[i:i + batch_size])
    return batches


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--per-domain", type=int, default=5)
    ap.add_argument("--batch-size", type=int, default=40)
    ap.add_argument("--reviewer", default="human:reviewer.physics-001")
    args = ap.parse_args()
    if not 1 <= args.per_domain <= 10:
        print("--per-domain must be 1..10", file=sys.stderr)
        return 2
    if not 10 <= args.batch_size <= 60:
        print("--batch-size must be 10..60", file=sys.stderr)
        return 2

    entities = load_entities()
    cent = centrality()
    batches = build_batches(entities, per_domain=args.per_domain, batch_size=args.batch_size)
    pend = pending_entities(entities)
    done = [e for e in entities.values() if e.get("status") in ("human_reviewed", "canonical")]

    OUT.mkdir(parents=True, exist_ok=True)
    for old in OUT.glob("batch-*"):
        old.unlink()

    for bi, batch in enumerate(batches, start=1):
        rows = []
        lines = [
            f"# Entity review — Batch {bi:02d}", "",
            f"{len(batch)} entities · reviewer: `{args.reviewer}` · seed pass: {bi == 1}", "",
            "Use a human reviewer, then run:",
            "",
            "```bash",
            f"python3 scripts/review_entity.py review <id> --reviewer {args.reviewer}",
            f"python3 scripts/review_entity.py canonicalize <id> --reviewer {args.reviewer}",
            "```",
            "",
            "Decision field in the YAML is informational (the CLI is the authority).",
            "",
            "| # | Entity | Domain | Type | Status | Score |",
            "|---|--------|--------|------|--------|-------|",
        ]
        for i, e in enumerate(batch, start=1):
            score = score_entity(e, cent)
            lines.append(f"| {i} | `{e.get('id')}` | {e.get('domain')} | {e.get('type')} | {e.get('status')} | {score} |")
            rows.append({
                "id": e.get("id"), "name": e.get("name"), "domain": e.get("domain"),
                "type": e.get("type"), "status": e.get("status"), "definition": (e.get("definition") or "")[:500],
                "score": score, "decision": None, "reviewer": None, "evidence_notes": None,
            })
        (OUT / f"batch-{bi:02d}.md").write_text("\n".join(lines), encoding="utf-8")
        (OUT / f"batch-{bi:02d}.yaml").write_text(
            yaml.safe_dump({"batch": bi, "campaign": "R6 entity review", "reviewer": args.reviewer,
                            "seed_pass": bi == 1, "items": rows},
                           sort_keys=False, allow_unicode=True, width=110),
            encoding="utf-8")

    by_domain: dict[str, dict[str, int]] = {}
    for e in entities.values():
        d = by_domain.setdefault(e.get("domain", "unknown"), {"total": 0, "reviewed": 0})
        d["total"] += 1
        if e.get("status") in ("human_reviewed", "canonical"):
            d["reviewed"] += 1
    pct = 100.0 * len(done) / len(entities) if entities else 0.0
    lines = [
        "# R6 — Entity review campaign", "",
        "Generated by `scripts/entity_review_campaign.py` (never edits review status).", "",
        f"- Entities: **{len(entities)}** · reviewed/canonical: **{len(done)}** ({pct:.1f}%)",
        f"- Pending: **{len(pend)}** · batches: **{len(batches)}**",
        f"- Seed pass: top {args.per_domain} per domain · batch size: {args.batch_size}",
        "",
        "## Progress by domain", "",
        "| Domain | Reviewed | Total | % |",
        "|--------|----------|-------|---|",
    ]
    for dom in sorted(by_domain):
        d = by_domain[dom]
        lines.append(f"| {dom} | {d['reviewed']} | {d['total']} | {100.0 * d['reviewed'] / d['total']:.0f}% |")
    lines += ["", "## Schedule", "", "| Batch | Entities | Top entity | Worksheet |", "|-------|----------|------------|-----------|"]
    for bi, batch in enumerate(batches, start=1):
        lines.append(f"| {bi:02d} | {len(batch)} | `{batch[0].get('id')}` | `batch-{bi:02d}.md` / `.yaml` |")
    lines.append("")
    (OUT / "campaign-schedule.md").write_text("\n".join(lines), encoding="utf-8")
    (OUT / "campaign-status.json").write_text(json.dumps({
        "total": len(entities), "reviewed": len(done), "pending": len(pend),
        "percent_reviewed": round(pct, 1), "batches": len(batches),
        "per_domain": args.per_domain, "batch_size": args.batch_size, "by_domain": by_domain,
    }, indent=2) + "\n", encoding="utf-8")
    print(f"OK: entity review campaign — {len(entities)} entities, {len(done)} reviewed "
          f"({pct:.1f}%), {len(pend)} pending in {len(batches)} batches -> {OUT.relative_to(ROOT)}/")
    return 0


if __name__ == "__main__":
    sys.exit(main())
