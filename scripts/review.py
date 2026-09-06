#!/usr/bin/env python3
"""D2: Lightweight review interface — CLI/report-driven.

Commands:
  python3 scripts/review.py list
  python3 scripts/review.py show stemma:conn.000042
  python3 scripts/review.py accept stemma:conn.000042 --reviewer human:reviewer.physics-001
  python3 scripts/review.py canonicalize stemma:conn.000042 --reviewer human:reviewer.physics-001
  python3 scripts/review.py reject stemma:conn.000042 --reviewer human:reviewer.physics-001 --reason "..."
"""
from __future__ import annotations

import json
import pathlib
import sys
from datetime import datetime, timezone

import yaml

ROOT = pathlib.Path(__file__).resolve().parent.parent
CONNECTIONS = ROOT / "connections"

from curation_state import validate_transition  # type: ignore


def load_conn(cid):
    # Accept with or without prefix
    if not cid.startswith("stemma:conn."):
        cid = f"stemma:conn.{cid}"
    p = CONNECTIONS / f"{cid}.yaml"
    if not p.exists():
        print(f"not found: {cid}", file=sys.stderr)
        sys.exit(1)
    return p, yaml.safe_load(p.read_text())


def cmd_list():
    import json as _j

    conns = []
    for p in sorted(CONNECTIONS.glob("*.yaml")):
        d = yaml.safe_load(p.read_text())
        conns.append(
            {
                "id": d["id"],
                "relation": d["relation"],
                "source": d["source"],
                "target": d["target"],
                "review": d["assertion"]["review"]["status"],
                "type": d["assertion"]["type"],
                "origin": d["provenance"]["method"]["type"],
            }
        )
    print(_j.dumps(conns, indent=2))


def cmd_show(cid):
    p, d = load_conn(cid)
    # Enrich with entity descriptions
    ents = {}
    for ep in (ROOT / "content").rglob("*.md"):
        dd = yaml.safe_load(ep.read_text().split("---", 2)[1])
        if dd.get("id"):
            ents[dd["id"]] = dd
    src = ents.get(d["source"], {})
    tgt = ents.get(d["target"], {})
    print(yaml.safe_dump(
        {
            "connection": d["id"],
            "relation": d["relation"],
            "relation_family": __import__("yaml").safe_load(open(ROOT / "schema/relation-registry.yaml").read()).get("relations", {}).get(d["relation"], {}).get("family"),
            "source": {"id": d["source"], "name": src.get("name"), "definition": src.get("definition", "")[:200]},
            "target": {"id": d["target"], "name": tgt.get("name"), "definition": tgt.get("definition", "")[:200]},
            "assertion": d["assertion"],
            "context": d.get("context"),
            "evidence": d.get("evidence"),
            "provenance": d.get("provenance"),
        },
        sort_keys=False,
        allow_unicode=True,
    ))


def apply_transition(cid, to_review, reviewer, reason=None):
    p, d = load_conn(cid)
    errs = validate_transition(d, to_review, reviewer, reason)
    if errs:
        print(f"transition forbidden: {errs}", file=sys.stderr)
        sys.exit(1)
    # Gate checks (D17)
    if to_review == "canonical":
        # Must be reviewed already or transitioning from reviewed
        cur = d["assertion"]["review"]["status"]
        if cur not in ("reviewed", "canonical"):
            # Also need evidence per family — basic check: at least one evidence or documented why
            if not d.get("evidence"):
                print(f"warning: canonicalizing {cid} without evidence (ensure family allows)", file=sys.stderr)
        if not reviewer:
            print("reviewer required for canonical", file=sys.stderr)
            sys.exit(1)
        d["provenance"].setdefault("reviewed_by", [])
        if {"type": "human", "id": reviewer} not in d["provenance"]["reviewed_by"]:
            d["provenance"]["reviewed_by"].append({"type": "human", "id": reviewer})
        # Preserve origin: do not overwrite asserted_by
        # Add review_history
        hist = d["provenance"].setdefault("review_history", [])
        hist.append(
            {
                "from": d["assertion"]["review"]["status"],
                "to": to_review,
                "reviewer": reviewer,
                "at": datetime.now(timezone.utc).isoformat(),
                "reason": reason or "pilot canonicalization",
            }
        )
    else:
        # reviewed/rejected
        if reviewer:
            d["provenance"].setdefault("reviewed_by", [])
            if {"type": "human", "id": reviewer} not in d["provenance"]["reviewed_by"]:
                d["provenance"]["reviewed_by"].append({"type": "human", "id": reviewer})
        hist = d["provenance"].setdefault("review_history", [])
        hist.append(
            {
                "from": d["assertion"]["review"]["status"],
                "to": to_review,
                "reviewer": reviewer,
                "at": datetime.now(timezone.utc).isoformat(),
                "reason": reason or f"transition to {to_review}",
            }
        )
    d["assertion"]["review"]["status"] = to_review
    # Scientific rejection is a review state only: the record stays an active
    # canonical object. Structural retirement (deprecated/superseded) is separate.
    # If moving to reviewed/canonical, ensure type is not proposed? Keep as is but allow asserted->reviewed
    p.write_text(yaml.safe_dump(d, sort_keys=False, allow_unicode=True))
    print(f"OK: {cid} -> {to_review} by {reviewer}")


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(0)
    cmd = sys.argv[1]
    if cmd == "list":
        cmd_list()
    elif cmd == "show" and len(sys.argv) >= 3:
        cmd_show(sys.argv[2])
    elif cmd in ("accept", "reviewed") and len(sys.argv) >= 3:
        reviewer = None
        for i, a in enumerate(sys.argv):
            if a == "--reviewer" and i + 1 < len(sys.argv):
                reviewer = sys.argv[i + 1]
        apply_transition(sys.argv[2], "reviewed", reviewer)
    elif cmd in ("canonicalize", "canonical") and len(sys.argv) >= 3:
        reviewer = None
        for i, a in enumerate(sys.argv):
            if a == "--reviewer" and i + 1 < len(sys.argv):
                reviewer = sys.argv[i + 1]
        apply_transition(sys.argv[2], "canonical", reviewer)
    elif cmd == "reject" and len(sys.argv) >= 3:
        reviewer = None
        reason = None
        for i, a in enumerate(sys.argv):
            if a == "--reviewer" and i + 1 < len(sys.argv):
                reviewer = sys.argv[i + 1]
            if a == "--reason" and i + 1 < len(sys.argv):
                reason = sys.argv[i + 1]
        apply_transition(sys.argv[2], "rejected", reviewer, reason)
    else:
        print(f"unknown command {cmd}", file=sys.stderr)
        sys.exit(1)
    return 0


if __name__ == "__main__":
    sys.exit(main())
