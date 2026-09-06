#!/usr/bin/env python3
"""Apply a human-filled E6.1 decision sheet (plan v2 E6.1).

  python3 scripts/apply_review_decisions.py reports/dependency-review-campaign/batch-01.yaml \
          --reviewer human:reviewer.physics-001 [--dry-run]

Rules (all enforced, none bypassable):
  * --reviewer must be a `human:` agent registered in schema/agent-registry.yaml.
  * decision ∈ {accept, canonical, reject, defer, null}. null/defer = no change.
  * transitions go through scripts/curation_state.validate_transition —
    `canonical` is applied as unreviewed→reviewed→canonical (protocol §2).
  * `canonical` requires evidence (sheet `evidence:` list or existing evidence on
    the connection); every evidence item must be a dict with a `type`.
  * `reject` requires a reason; the connection keeps assertion.status: active and
    review.status becomes `rejected` (schema 1.1.0, ADR-0031). Rejection is a
    review state, never structural retirement; deprecated/superseded stay reserved
    for dedup/merge/replacement.
  * `reopen` (rejected → proposed/unreviewed) is human-only and requires a reason.
  * asserted_by / generated_by are never rewritten (origin preserved, protocol §6).
  * review_history receives one entry per transition with the HUMAN reviewer.

After applying, run `python3 scripts/sync_relationships.py && python3 scripts/verify_all.py`.
"""
from __future__ import annotations

import argparse
import pathlib
import sys
from datetime import datetime, timezone

import yaml

ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))
from curation_state import validate_transition  # noqa: E402

CONNECTIONS = ROOT / "connections"
AGENTS = ROOT / "schema" / "agent-registry.yaml"
DECISIONS = {"accept", "canonical", "reject", "defer", None}


def now() -> str:
    return datetime.now(timezone.utc).isoformat()


def registered_human(agent: str) -> bool:
    data = yaml.safe_load(AGENTS.read_text(encoding="utf-8")) or {}
    return any(a.get("id") == agent and a.get("class") == "human" and a.get("status") == "active"
               for a in data.get("agents") or [])


def add_reviewer(prov: dict, reviewer: str) -> None:
    prov.setdefault("reviewed_by", [])
    if {"type": "human", "id": reviewer} not in prov["reviewed_by"]:
        prov["reviewed_by"].append({"type": "human", "id": reviewer})


def transition(conn: dict, to: str, reviewer: str, reason: str) -> None:
    errs = validate_transition(conn, to, reviewer, reason)
    if errs:
        raise ValueError(f"{conn['id']}: forbidden transition -> {to}: {errs}")
    prov = conn["provenance"]
    add_reviewer(prov, reviewer)
    prov.setdefault("review_history", []).append({
        "from": conn["assertion"]["review"]["status"], "to": to,
        "reviewer": reviewer, "at": now(), "reason": reason,
    })
    conn["assertion"]["review"]["status"] = to


def apply_item(item: dict, reviewer: str, dry: bool) -> str:
    decision = item.get("decision")
    if decision not in DECISIONS:
        raise ValueError(f"{item.get('id')}: unknown decision {decision!r}")
    if decision in (None, "defer"):
        return "skip"
    path = CONNECTIONS / f"{item['id']}.yaml"
    conn = yaml.safe_load(path.read_text(encoding="utf-8"))
    # Sheet must match the file (guards against stale sheets).
    for k in ("source", "relation", "target"):
        if conn[k] != item[k]:
            raise ValueError(f"{item['id']}: sheet {k}={item[k]} != file {conn[k]} (stale worksheet — regenerate)")
    reason = item.get("reason") or f"E6.1 dependency-edge review: {decision}"
    cur = conn["assertion"]["review"]["status"]

    if decision == "reject":
        if not item.get("reason"):
            raise ValueError(f"{item['id']}: reject requires a reason")
        if conn["assertion"]["status"] != "active":
            return "skip"
        # ADR-0031 / rejected lifecycle: review.status -> rejected, record stays
        # active. Structural retirement (deprecated/superseded) stays separate.
        transition(conn, "rejected", reviewer, item["reason"])
    else:
        if cur == "canonical":
            return "skip"
        if cur == "unreviewed":
            transition(conn, "reviewed", reviewer, reason)
        if decision == "canonical":
            new_ev = item.get("evidence") or []
            if new_ev:
                if not all(isinstance(e, dict) and e.get("type") for e in new_ev):
                    raise ValueError(f"{item['id']}: every evidence item needs a type")
                conn["evidence"] = (conn.get("evidence") or []) + new_ev
            if not conn.get("evidence"):
                raise ValueError(f"{item['id']}: canonical requires evidence (protocol §3, dependency family)")
            transition(conn, "canonical", reviewer, reason)
    if not dry:
        path.write_text(yaml.safe_dump(conn, sort_keys=False, allow_unicode=True), encoding="utf-8")
    return decision


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("sheet")
    ap.add_argument("--reviewer", required=True)
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()
    if not args.reviewer.startswith("human:") or not registered_human(args.reviewer):
        print(f"error: --reviewer must be an active human agent in schema/agent-registry.yaml: {args.reviewer}", file=sys.stderr)
        return 2
    sheet = yaml.safe_load(pathlib.Path(args.sheet).read_text(encoding="utf-8"))
    counts: dict[str, int] = {}
    try:
        # Two passes: validate every item without writing (atomic sheet — one bad
        # item rejects the whole batch), then apply.
        for item in sheet.get("items") or []:
            apply_item(item, args.reviewer, True)
        for item in sheet.get("items") or []:
            r = apply_item(item, args.reviewer, args.dry_run)
            counts[r] = counts.get(r, 0) + 1
    except ValueError as exc:
        print(f"error: {exc} — no changes written", file=sys.stderr)
        return 1
    print(f"OK{' (dry-run)' if args.dry_run else ''}: {counts} — now run python3 scripts/verify_all.py")
    return 0


if __name__ == "__main__":
    sys.exit(main())
