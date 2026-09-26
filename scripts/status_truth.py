#!/usr/bin/env python3
"""Status-truth gate (plan v2 E0.4; audit F2).

The README carries a machine-checkable status block (between
`<!-- status-truth:start -->` and `<!-- status-truth:end -->`). This script
recomputes the live counts from canonical content and fails if the README
claims different numbers — status honesty is enforced, not hoped for.

Usage: python3 scripts/status_truth.py [--write]
  --write  regenerate the README status block from live counts (then review
           the diff like any other change).
"""
from __future__ import annotations

import pathlib
import re
import sys

import yaml

ROOT = pathlib.Path(__file__).resolve().parent.parent
README = ROOT / "README.md"
START = "<!-- status-truth:start -->"
END = "<!-- status-truth:end -->"


def live_counts() -> dict:
    entities = [yaml.safe_load(p.read_text(encoding="utf-8").split("---", 2)[1])
                for p in sorted(ROOT.glob("content/**/*.md"))]
    conns = [yaml.safe_load(p.read_text(encoding="utf-8"))
             for p in sorted((ROOT / "connections").glob("*.yaml"))]
    sources = list((ROOT / "sources").glob("*.yaml"))
    return {
        "entities": len(entities),
        "entities_reviewed": sum(1 for e in entities if e.get("status") in ("human_reviewed", "canonical")),
        "entities_draft": sum(1 for e in entities if e.get("status") == "draft"),
        "connections": len(conns),
        "connections_canonical": sum(1 for c in conns if c.get("assertion", {}).get("review", {}).get("status") == "canonical"),
        "connections_unreviewed": sum(1 for c in conns if c.get("assertion", {}).get("review", {}).get("status") == "unreviewed"),
        "sources": len(sources),
    }


def block(counts: dict) -> str:
    pct = (100.0 * counts["connections_canonical"] / counts["connections"]) if counts["connections"] else 0.0
    return (
        f"{START}\n"
        f"## Status: live foundation in early curation\n\n"
        f"Machine-checkable live counts — `scripts/status_truth.py` (CI) fails if this\n"
        f"block drifts from canonical content (audit F2: status honesty is a gate):\n\n"
        f"- Entities: **{counts['entities']}** — human-reviewed/canonical: **{counts['entities_reviewed']}**, draft: **{counts['entities_draft']}**\n"
        f"- Connections (first-class assertions): **{counts['connections']}** — review-canonical: **{counts['connections_canonical']}** ({pct:.1f}%), unreviewed: **{counts['connections_unreviewed']}**\n"
        f"- Canonical source records: **{counts['sources']}**\n"
        f"{END}"
    )


def main() -> int:
    counts = live_counts()
    text = README.read_text(encoding="utf-8")

    if "--write" in sys.argv:
        if START in text and END in text:
            pattern = re.compile(re.escape(START) + r".*?" + re.escape(END), re.DOTALL)
            text = pattern.sub(lambda _: block(counts), text, count=1)
        else:
            text = text.rstrip("\n") + "\n\n" + block(counts) + "\n"
        README.write_text(text, encoding="utf-8")
        print(f"README status block written from live counts: {counts}")
        return 0

    if START not in text or END not in text:
        print("FAIL: README has no status-truth block; run: python3 scripts/status_truth.py --write", file=sys.stderr)
        return 1

    section = text.split(START, 1)[1].split(END, 1)[0]
    expected = {
        "entities": counts["entities"],
        "entities_reviewed": counts["entities_reviewed"],
        "entities_draft": counts["entities_draft"],
        "connections": counts["connections"],
        "connections_canonical": counts["connections_canonical"],
        "connections_unreviewed": counts["connections_unreviewed"],
        "sources": counts["sources"],
    }
    mismatches = []
    pairs = [
        (r"Entities: \*\*(\d+)\*\*", "entities"),
        (r"human-reviewed/canonical: \*\*(\d+)\*\*", "entities_reviewed"),
        (r"draft: \*\*(\d+)\*\*", "entities_draft"),
        (r"Connections \(first-class assertions\): \*\*(\d+)\*\*", "connections"),
        (r"review-canonical: \*\*(\d+)\*\*", "connections_canonical"),
        (r"unreviewed: \*\*(\d+)\*\*", "connections_unreviewed"),
        (r"source records: \*\*(\d+)\*\*", "sources"),
    ]
    for pattern, key in pairs:
        m = re.search(pattern, section)
        if not m:
            mismatches.append(f"status line missing for {key}")
        elif int(m.group(1)) != expected[key]:
            mismatches.append(f"{key}: README says {m.group(1)}, live is {expected[key]}")

    if mismatches:
        print("FAIL: README status claims diverge from canonical content (audit F2):", file=sys.stderr)
        for m in mismatches:
            print(f"  - {m}", file=sys.stderr)
        print("Fix: python3 scripts/status_truth.py --write  (then review the diff)", file=sys.stderr)
        return 1
    print(f"OK: README status block matches live counts ({counts['entities']} entities, "
          f"{counts['connections']} connections, {counts['connections_canonical']} canonical assertions)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
