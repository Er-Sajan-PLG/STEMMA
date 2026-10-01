#!/usr/bin/env python3
"""Emit a hash-only review manifest — portable HITL provenance, no excerpts.

Why this exists (UNRES-STEMMA-HITL-001, owner ruling 2026-10-01, option (c)):

The HITL audit trail lives in a git-ignored `workflow/` directory, so a fresh
clone cannot verify that a canonical record was human-reviewed. Committing the
raw trail is not an option: it may contain verbatim textbook excerpts, which is
the separate legal question in UNRES-STEMMA-OPS-001.

This script produces the middle path. For every reviewed record it writes a
COMMITTED manifest carrying only:

  * the record id,
  * the provenance the corpus already declares (writer, reviewer, reviewed_at),
  * the ordered promotion history (stage, actor, timestamp, board waiver),
  * a CONTENT HASH of the reviewed file.

What it deliberately never emits: any definition text, any source excerpt, any
`workflow/` payload. Only ids, metadata, and sha256 digests — so the manifest is
safe to commit under any licensing position (EU/UK/US alike), and it lets a
fresh clone answer "was this reviewed by a named human, and is the reviewed
artifact still byte-identical?" without seeing the artifact's text.

The hash is what makes the manifest meaningful: it ties the claim
"human:curator.001 reviewed X at time T" to a specific artifact state. If the
file changes afterwards, the digest stops matching and the claim is visibly
stale.

Usage:
  python3 scripts/review_manifest.py                 # write the manifest
  python3 scripts/review_manifest.py --check         # verify, exit 1 on drift
  python3 scripts/review_manifest.py --stdout        # print, write nothing

  --check re-hashes the live records and fails if any digest in the committed
  manifest no longer matches, so a silent post-review edit cannot pass.

Deterministic: sorted keys and ids; no wall clock (the manifest carries the
records' own timestamps, never "now").
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
CONTENT_DIR = ROOT / "content"
CONNECTIONS_DIR = ROOT / "connections"
OUT_PATH = ROOT / "spec" / "machine-readable" / "review_manifest.json"
MANIFEST_VERSION = "1.0.0"


def _sha256(path: Path) -> str:
    return "sha256:" + hashlib.sha256(path.read_bytes()).hexdigest()


def _load(path: Path) -> dict:
    """Parse a record's YAML frontmatter.

    Entities are markdown (`---` fenced frontmatter + prose body); connections are
    plain YAML. Both reduce to the frontmatter mapping here.
    """
    text = path.read_text(encoding="utf-8")
    if text.lstrip().startswith("---"):
        # Frontmatter block: everything between the first two `---` fences.
        body = text.lstrip()[3:]
        end = body.find("\n---")
        if end != -1:
            body = body[:end]
        return yaml.safe_load(body) or {}
    return yaml.safe_load(text) or {}


def _record_entry(path: Path, kind: str) -> dict | None:
    """Build one manifest entry from a canonical record, or None if unreviewed."""
    data = _load(path)
    prov = data.get("provenance") or {}
    history = prov.get("promotion_history") or []
    reviewer = prov.get("reviewer")
    reviewed_at = prov.get("reviewed_at")

    # Only reviewed records belong in the manifest: a draft has no review claim
    # to make portable, and listing it would dilute the signal.
    if not (reviewer or history):
        return None

    entry: dict = {
        "id": data.get("id", path.stem),
        "kind": kind,
        "relpath": str(path.relative_to(ROOT)),
        "content_hash": _sha256(path),
        "writer": prov.get("writer"),
        "status": data.get("status"),
    }
    if reviewer:
        entry["reviewer"] = reviewer
    if reviewed_at:
        entry["reviewed_at"] = str(reviewed_at)
    if history:
        entry["promotion_history"] = sorted(
            history,
            key=lambda h: str(h.get("at", "")),
        )
    return entry


def collect() -> dict:
    entries: list[dict] = []
    for path in sorted(CONTENT_DIR.rglob("*.md")):
        e = _record_entry(path, "entity")
        if e:
            entries.append(e)
    for path in sorted(CONNECTIONS_DIR.rglob("*.yaml")):
        e = _record_entry(path, "connection")
        if e:
            entries.append(e)
    entries.sort(key=lambda e: (e["kind"], e["id"]))
    return {
        "_note": (
            "Hash-only HITL provenance (UNRES-STEMMA-HITL-001 option (c)). "
            "Ids, declared provenance, promotion history, and content digests only — "
            "NO definition text and NO source excerpts. Safe to commit under any "
            "licensing position. Regenerate with scripts/review_manifest.py; verify "
            "with --check."
        ),
        "manifest_version": MANIFEST_VERSION,
        "entry_count": len(entries),
        "entries": entries,
    }


def check() -> int:
    if not OUT_PATH.exists():
        print(f"FAIL: no committed manifest at {OUT_PATH.relative_to(ROOT)}", file=sys.stderr)
        return 1
    committed = json.loads(OUT_PATH.read_text(encoding="utf-8"))
    live = collect()
    by_id = {e["id"]: e for e in committed.get("entries", [])}
    live_by_id = {e["id"]: e for e in live["entries"]}

    problems: list[str] = []
    for rid, entry in sorted(live_by_id.items()):
        if rid not in by_id:
            problems.append(f"{rid}: reviewed but absent from the committed manifest")
            continue
        if by_id[rid]["content_hash"] != entry["content_hash"]:
            problems.append(
                f"{rid}: content changed after review "
                f"(committed {by_id[rid]['content_hash'][:19]}…, live {entry['content_hash'][:19]}…) — "
                "the review claim is stale"
            )
    for rid in sorted(set(by_id) - set(live_by_id)):
        problems.append(f"{rid}: in the manifest but no longer a reviewed record")

    if problems:
        for p in problems:
            print(f"FAIL: {p}", file=sys.stderr)
        print(f"FAIL: {len(problems)} review-manifest drift(s)", file=sys.stderr)
        return 1
    print(f"OK: review manifest matches — {len(live_by_id)} reviewed record(s), all digests current")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    parser.add_argument("--check", action="store_true", help="verify the committed manifest; exit 1 on drift")
    parser.add_argument("--stdout", action="store_true", help="print the manifest, write nothing")
    args = parser.parse_args()

    if args.check:
        return check()

    manifest = collect()
    if args.stdout:
        print(json.dumps(manifest, indent=2, sort_keys=True, ensure_ascii=False))
        return 0

    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUT_PATH.write_text(
        json.dumps(manifest, indent=2, sort_keys=True, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    print(f"OK: wrote {OUT_PATH.relative_to(ROOT)} — {manifest['entry_count']} reviewed record(s), hash-only")
    return 0


if __name__ == "__main__":
    sys.exit(main())
