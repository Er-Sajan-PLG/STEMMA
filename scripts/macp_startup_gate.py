#!/usr/bin/env python3
"""MACP startup gate — did each live session actually verify during its own session?

**The gap this closes.** MACP v1.2's STEP 8 ("VERIFY STATE AGAINST REALITY") is mandatory
and entirely unenforced. Nothing checked that an agent ran the chain or the suite; the
step rested on discipline. On 2026-10-01 that failed twice in one repository: a session
left `DASHBOARD.md`'s `HEAD` line 11 commits stale, and a later session carried a gate
result into its notes as *verified* without ever running the command. Both passed every
existing guard, because the guards check **shape**, not **truthfulness**.

**How it is enforced without a new artifact.** `scripts/gate_status.py` writes the
DASHBOARD's gate block, and it writes it **only when every gate is green**. So a fresh
stamp on that block is a *by-product of having run the gates and passed them* — the
agent cannot assert it, only produce it. This script then checks the cheap, decisive
property:

    every session whose status is live must have started **at or before** the block's
    `Measured` stamp

A session that skipped STEP 8 leaves the previous run's stamp in place, and the stamp
predates the session — so the check fails, and the failure names the session.

**Why this is not a pytest test, and not in `gate_status.py`'s gate list.** Both would
deadlock. The artifact this checks is produced by the run that would have to pass first:
`gate_status.py` runs the suite, the suite would run this check, and the check would fail
against the stale stamp that the very same run has not yet replaced. It therefore lives
in its own script, invoked by CI (and usable by the pre-push hook) as a step *after*
generation.

**Scope.** Completeness only. It asserts that verification happened; it cannot assert
that the work verified was correct — that is not mechanically decidable, and pretending
otherwise is how a gate becomes compliant-looking rot.

Usage:

    python3 scripts/macp_startup_gate.py
"""
from __future__ import annotations

import re
import sys
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
REGISTRY = ROOT / "state" / "REGISTRY.md"
DASHBOARD = ROOT / "state" / "DASHBOARD.md"
SESSIONS = ROOT / "state" / "sessions"

LIVE_STATUSES = frozenset({"active", "in-progress"})
STAMP_RE = re.compile(r"\*\*Measured:\*\*\s*(\d{4}-\d{2}-\d{2}T\d{2}:\d{2}Z)")
STARTED_RE = re.compile(r"^\*\*Started:\*\*\s*(\d{4}-\d{2}-\d{2}T\d{2}:\d{2}Z)\s*$", re.MULTILINE)


def _parse_stamp(value: str) -> datetime:
    return datetime.strptime(value, "%Y-%m-%dT%H:%MZ")


def live_sessions(registry_text: str) -> list[tuple[str, str]]:
    """(session_id, status) for every row whose status is live.

    Parsed positionally rather than by regex: the registry is a markdown table, and
    the columns before the status one are free text that can contain anything.
    """
    out: list[tuple[str, str]] = []
    for line in registry_text.splitlines():
        if not line.startswith("|"):
            continue
        cells = [c.strip().strip("*").strip("`").strip() for c in line.strip().strip("|").split("|")]
        if len(cells) < 6:
            continue
        agent_id, session_id, status = cells[0], cells[1], cells[5]
        if re.fullmatch(r"[A-Za-z0-9]{4}", agent_id) and session_id.startswith("20"):
            if status.lower() in LIVE_STATUSES:
                out.append((session_id, status))
    return out


def main() -> int:
    registry_text = REGISTRY.read_text(encoding="utf-8")
    dashboard_text = DASHBOARD.read_text(encoding="utf-8")

    # Non-vacuity: a parse that finds no rows means the table shape changed, not that
    # nobody is working. Both cases must be distinguishable, or this gate silently
    # passes forever the first time someone edits the table.
    if not re.search(r"^\|\s*`[A-Za-z0-9]{4}`\s*\|\s*`20", registry_text, re.MULTILINE):
        print("FAIL: parsed no agent rows from state/REGISTRY.md — the table shape changed, "
              "so this gate can no longer see who is working.", file=sys.stderr)
        return 1

    match = STAMP_RE.search(dashboard_text)
    if not match:
        print("FAIL: state/DASHBOARD.md has no generated gate block with a `Measured` stamp. "
              "Run: python3 scripts/gate_status.py", file=sys.stderr)
        return 1
    measured = _parse_stamp(match.group(1))

    live = live_sessions(registry_text)
    if not live:
        print(f"OK: no live session; gate block measured {match.group(1)} (nothing to verify).")
        return 0

    problems: list[str] = []
    for session_id, status in live:
        path = SESSIONS / f"{session_id}.md"
        if not path.is_file():
            problems.append(f"{session_id}: live in REGISTRY.md but has no session file")
            continue
        started_match = STARTED_RE.search(path.read_text(encoding="utf-8"))
        if not started_match:
            problems.append(f"{session_id}: session header has no parseable `Started` stamp")
            continue
        started = _parse_stamp(started_match.group(1))
        if measured < started:
            problems.append(
                f"{session_id} (status {status}) started {started.strftime('%Y-%m-%dT%H:%MZ')} "
                f"but the DASHBOARD gate block was last measured "
                f"{measured.strftime('%Y-%m-%dT%H:%MZ')} — the gates were not run during this "
                "session, so STEP 8 (verify state against reality) was skipped"
            )

    if problems:
        print("FAIL: MACP startup verification is missing or stale:", file=sys.stderr)
        for problem in problems:
            print(f"  - {problem}", file=sys.stderr)
        print("\nFix: run `python3 scripts/gate_status.py` (it refuses to write unless every "
              "gate is green), then commit the regenerated block.", file=sys.stderr)
        return 1

    print(f"OK: every live session started at or before the gate block's measurement "
          f"({match.group(1)}); STEP 8 is satisfied for {len(live)} live session(s).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
