#!/usr/bin/env python3
"""Per-release audit of prose-owned machine COUNTS (REQ-STEMMA-OPS-002).

Why this exists
---------------
REQ-STEMMA-OPS-002 says living documents SHOULD NOT hardcode machine-owned
counts or versions — single sources (`scripts/status_truth.py`,
`schema/VERSION.yaml`) own them. The criterion is a **trend across releases**.

The owner ruled 2026-10-01 (option (a) of spec/UNVERIFIED-DECISIONS.md §2) that
this script IS the measurement instrument, and that the trend **starts at
`v3.0.0`** as its first data point. So this is a probe, not a gate: run it at
each release and compare. The requirement cannot be VERIFIED from one point.

Why counts, not versions
------------------------
A first cut of this script also matched version literals. It was discarded: the
same version string appears as `kernel_version`, `pipeline_version`,
`prompt_version`, third-party `ngraph.merge@1.0.0` lockfile entries and adapter
`1.0` tags, so 96 "hits" were overwhelmingly noise — an instrument that reports
mostly false positives cannot measure a trend. Counting occurrences of a *count*
value such as `9 entities` has no such ambiguity.

Instrument definition
---------------------
For a revision, read the machine-owned counts from the generated README status
block (written and gated by `status_truth.py`, so it is the single source's echo),
then find prose that restates those numbers as a live count:

    <n> entities | <n> connections | <n> sources

Restating a count in prose is exactly the drift the requirement forbids. A file
is exempt when it is the single source, generated from it, or a historical record
that must be allowed to quote values as of its own date (ADR records, MIGRATIONS,
CHANGELOG, session logs).

Offline and deterministic: reads the local git object store only. Writes nothing.
"""
from __future__ import annotations

import argparse
import json
import re
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

# Living documents are the audit surface. These may legitimately quote counts:
#  - ADR / decision records: immutable snapshots of decision time
#  - MIGRATIONS / CHANGELOG / session logs: historical by definition
#  - the single source and everything generated from it
EXEMPT_PREFIXES = (
    "docs/decisions/",
    "spec/DECISIONS/",
    "archive/",
    "prompts/",
    ".agents/",
    ".github/",
)
EXEMPT_EXACT = {
    "README.md",
    "CHANGELOG.md",
    "PROGRESS.md",
    "docs/MIGRATIONS.md",
    "docs/VERSIONING.md",
    "spec/machine-readable/verification.yaml",
    "spec/machine-readable/evidence.yaml",
    "spec/machine-readable/traceability.yaml",
    "spec/machine-readable/open_questions.yaml",
    "spec/machine-readable/requirements.yaml",
    "spec/EVIDENCE_REGISTER.md",
    "spec/UNVERIFIED-DECISIONS.md",
    "spec/VERIFICATION.md",
    "spec/OPEN_QUESTIONS.md",
    "spec/AS_BUILT.md",
    "spec/SPECIFICATION_PROCESS_REVIEW.md",
}
EXEMPT_SUFFIXES = ("lock.yaml", "lock.yml", "pnpm-lock.yaml", "package-lock.json")
TEXT_SUFFIXES = (".md", ".yaml", ".yml")

# A count restated in prose, e.g. "9 entities", "2 connections", "3 sources".
COUNT_PATTERNS = {
    "entities": re.compile(r"(?<![\w.])(\d+)\s+entit(?:y|ies)\b", re.I),
    "connections": re.compile(r"(?<![\w.])(\d+)\s+connections?\b", re.I),
    "sources": re.compile(r"(?<![\w.])(\d+)\s+sources?\b", re.I),
}


def _git(*args: str) -> str:
    r = subprocess.run(["git", *args], cwd=ROOT, capture_output=True, text=True,
                       check=False)
    if r.returncode != 0:
        raise SystemExit(f"git {' '.join(args)} failed: {r.stderr.strip()}")
    return r.stdout


def _is_exempt(path: str) -> bool:
    if path in EXEMPT_EXACT or path.endswith(EXEMPT_SUFFIXES):
        return True
    return any(path.startswith(p) for p in EXEMPT_PREFIXES)


def live_counts_at(rev: str) -> dict[str, int]:
    """Machine-owned counts, from the gated status block at `rev`."""
    try:
        readme = _git("show", f"{rev}:README.md")
    except SystemExit:
        return {}
    m = re.search(r"<!-- status-truth:start -->(.*?)<!-- status-truth:end -->",
                  readme, re.DOTALL)
    if not m:
        return {}
    body = m.group(1)
    counts: dict[str, int] = {}
    for name, pat in (("entities", r"Entities:\s*\*\*(\d+)\*\*"),
                      ("connections", r"Connections[^:]*:\s*\*\*(\d+)\*\*"),
                      ("sources", r"Canonical source records:\s*\*\*(\d+)\*\*")):
        mm = re.search(pat, body)
        if mm:
            counts[name] = int(mm.group(1))
    return counts


def audit(rev: str) -> dict:
    counts = live_counts_at(rev)
    hits: list[dict] = []

    for path in _git("ls-tree", "-r", "--name-only", rev).splitlines():
        if not path.endswith(TEXT_SUFFIXES) or _is_exempt(path):
            continue
        try:
            text = _git("show", f"{rev}:{path}")
        except SystemExit:
            continue
        occ: list[dict] = []
        for i, line in enumerate(text.splitlines(), 1):
            for name, pat in COUNT_PATTERNS.items():
                for m in pat.finditer(line):
                    occ.append({"line": i, "kind": name, "value": int(m.group(1)),
                                "text": line.strip()[:150]})
        if occ:
            hits.append({"path": path, "occurrences": occ})

    stale = [
        {"path": h["path"], "line": o["line"], "kind": o["kind"], "value": o["value"],
         "live": counts.get(o["kind"]), "text": o["text"]}
        for h in hits for o in h["occurrences"]
        if o["kind"] in counts and o["value"] != counts[o["kind"]]
    ]

    return {
        "revision": rev,
        "machine_owned_counts": counts,
        "prose_count_mentions": {
            "files": len(hits),
            "occurrences": sum(len(h["occurrences"]) for h in hits),
        },
        "stale_prose_mentions": {
            "count": len(stale),
            "items": stale,
        },
        "files": hits,
    }


def main() -> int:
    ap = argparse.ArgumentParser(
        description="Audit prose restatements of machine-owned counts at a revision.")
    ap.add_argument("rev", nargs="?", default="HEAD", help="git revision (default HEAD)")
    ap.add_argument("--all-tags", action="store_true",
                    help="audit every release tag, oldest first")
    ap.add_argument("--summary", action="store_true",
                    help="print headline numbers only")
    args = ap.parse_args()

    revs = [args.rev]
    if args.all_tags:
        tags = _git("tag", "--list").splitlines()
        tags.sort(key=lambda t: (_git("log", "-1", "--format=%ct", t).strip(), t))
        revs = tags

    records = [audit(r) for r in revs]

    if args.summary:
        for r in records:
            print(f"{r['revision']:<22} counts={r['machine_owned_counts']} "
                  f"prose={r['prose_count_mentions']['occurrences']} "
                  f"stale={r['stale_prose_mentions']['count']}")
        return 0

    print(json.dumps(records if args.all_tags else records[0], indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
