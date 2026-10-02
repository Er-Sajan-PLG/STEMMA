#!/usr/bin/env python3
"""MACP log — record a work unit immediately, with the changed files filled in for you.

**Why a tool and not a rule.** "Log continuously" has been a protocol instruction since
v1.0 and it is the instruction most often skipped, because at the moment work finishes the
log entry feels like paperwork for later. The rule is unenforceable in the only place it
matters — the moment of writing. So make the correct action the cheapest one:

    python3 scripts/macp_log.py PROGRESS "Repaired the ownership guard; it now accepts IN-PROGRESS."

That appends a stamped entry to the live session's log and **lists the changed files for
you**, computed from git. You supply the meaning; the tool supplies the facts. An agent
that logs this way cannot leave a file unrecorded, because it never enumerates them by
hand — which is what makes `scripts/macp_sync_gate.py`'s completeness check pass for the
right reason instead of by remembering.

**Append-only.** The session log is opened in append mode and never rewritten (protocol
Rule 2). The timestamp is read from the clock, never composed.

**Refuses when there is no live session.** Logging into a closed session would falsify a
boundary the protocol treats as final (N4), so the tool stops and says so.

Usage:

    python3 scripts/macp_log.py TAG "one or more lines of meaning"
    python3 scripts/macp_log.py --list-tags
"""
from __future__ import annotations

import argparse
import re
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
REGISTRY = ROOT / "state" / "REGISTRY.md"
SESSIONS = ROOT / "state" / "sessions"

LIVE_STATUSES = frozenset({"active", "in-progress"})
BASE_RE = re.compile(r"^\*\*Base commit:\*\*\s*`?([0-9a-f]{7,40})`?\s*$", re.MULTILINE)

# protocol §2, "Write Isolation During Work" — the event-tag vocabulary
TAGS = (
    "START", "PROGRESS", "DISCOVERY", "PIVOT", "DECISION", "BLOCKER", "COORDINATION",
    "DEBT", "BUG FOUND", "SECURITY", "SCOPE EXPANSION", "DISCREPANCY",
)


def _run(*argv: str) -> str:
    return subprocess.run(argv, cwd=ROOT, capture_output=True, text=True).stdout


def live_session_id() -> str | None:
    for line in REGISTRY.read_text(encoding="utf-8").splitlines():
        if not line.startswith("|"):
            continue
        cells = [c.strip().strip("*").strip("`").strip()
                 for c in line.strip().strip("|").split("|")]
        if len(cells) < 6:
            continue
        if re.fullmatch(r"[A-Za-z0-9]{4}", cells[0]) and cells[1].startswith("20"):
            if cells[5].lower() in LIVE_STATUSES:
                return cells[1]
    return None


def changed_paths(base: str) -> list[str]:
    committed = _run("git", "diff", "--name-only", f"{base}..HEAD").split("\n")
    dirty = [ln[3:].strip() for ln in _run("git", "status", "--porcelain").split("\n")
             if len(ln) > 3 and ln[2] == " "]
    return sorted({p for p in (committed + dirty) if p.strip()})


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("tag", nargs="?", help="event tag, e.g. PROGRESS")
    parser.add_argument("text", nargs="?", help="what happened, in your words")
    parser.add_argument("--list-tags", action="store_true")
    args = parser.parse_args(argv)

    if args.list_tags:
        print("\n".join(TAGS))
        return 0
    if not args.tag or not args.text:
        parser.error("both TAG and TEXT are required (or use --list-tags)")

    tag = args.tag.upper()
    if tag not in TAGS:
        print(f"FAIL: {args.tag!r} is not a protocol event tag. Known tags:\n  "
              + "\n  ".join(TAGS), file=sys.stderr)
        return 1

    session_id = live_session_id()
    if not session_id:
        print("FAIL: no live session in state/REGISTRY.md, so there is nowhere to log.\n"
              "Register a session first (state/STARTUP.md step 9). Logging into a closed\n"
              "session would falsify a boundary the protocol treats as final (N4).",
              file=sys.stderr)
        return 1

    session_path = SESSIONS / f"{session_id}.md"
    if not session_path.is_file():
        print(f"FAIL: {session_id} is live but has no session file at {session_path}",
              file=sys.stderr)
        return 1

    text = session_path.read_text(encoding="utf-8")
    base_match = BASE_RE.search(text)
    files = changed_paths(base_match.group(1)) if base_match else []

    stamp = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%MZ")
    entry = [f"\n## [{tag}] — {stamp}\n", args.text.rstrip(), ""]
    if files:
        entry.append("**Files touched so far (auto-recorded from git):** "
                     + ", ".join(f"`{p}`" for p in files))
        entry.append("")
    else:
        entry.append("**Files touched so far:** none yet.")
        entry.append("")

    with session_path.open("a", encoding="utf-8") as handle:
        handle.write("\n".join(entry) + "\n")

    print(f"OK: appended a [{tag}] entry to {session_path.name} "
          f"({len(files)} file(s) auto-recorded).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
