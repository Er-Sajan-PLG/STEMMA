#!/usr/bin/env python3
"""MACP sync gate — is the session record in sync with the state files and with git?

**The question this answers.** *"Is the work done in this session recorded in state?"*
Until now, nothing checked. A session could do substantial work and leave the record
silently incomplete, and every existing guard would still pass — because they check the
*shape* of `state/`, not whether the record matches what actually happened.

**What it checks.** Six properties, all tied to git reality rather than to prose:

| | Property | Gameable? |
|---|---|---|
| 1 | State-tree invariants hold (`tests/repo/test_state_tree.py`, 18 checks) | no — structural |
| 2 | STEP 8 verification happened this session (`scripts/macp_startup_gate.py`) | no — the stamp is a by-product |
| 3 | Every file the session changed is **named** in its session log | **yes** — completeness only |
| 4 | Every commit since `Base commit` is **listed** in its session log | **yes** — completeness only |
| 5 | The DASHBOARD's agent note agrees with REGISTRY about who is live | no |
| 6 | The DASHBOARD was **reconciled** during the session (`Last Reconciled` ≥ `Started`) | no |

**Read the "gameable" column, and read it as a warning.** Checks 3 and 4 are
*completeness* checks: they force enumeration, and an agent could satisfy them by listing
paths it never touched. That is the strongest form available — correctness is not
mechanically decidable, and the protocol's own P7 says so — but it means **a green sync
gate proves the record is complete, not that it is accurate.** The value is that it makes
silence impossible: the failure this closes is *"substantial work, nothing recorded"*,
which is exactly what the record exists to prevent.

**Why the HEAD commit is exempt from check 4.** The commit that writes the commit list
cannot contain its own sha. The gate therefore requires every commit in
`<base>..HEAD~1`, and says so when it fails.

**Why this runs pre-push *and* in CI.** Hooks are not cloned, so a contributor without
them — or a push made through the web UI — is ungated (DEBT-006). The hook gives the
author a fast, local refusal; CI is what actually makes it unbypassable.

Usage:

    python3 scripts/macp_sync_gate.py
"""
from __future__ import annotations

import argparse
import re
import subprocess
import sys
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
REGISTRY = ROOT / "state" / "REGISTRY.md"
DASHBOARD = ROOT / "state" / "DASHBOARD.md"
INDEX = ROOT / "state" / "INDEX.md"
SESSIONS = ROOT / "state" / "sessions"

LIVE_STATUSES = frozenset({"active", "in-progress"})

STAMP_RE = re.compile(r"\*\*Measured:\*\*\s*(\d{4}-\d{2}-\d{2}T\d{2}:\d{2}Z)")
RECONCILED_RE = re.compile(r"\*\*Last Reconciled:\*\*\s*(\d{4}-\d{2}-\d{2}T\d{2}:\d{2}Z)")
STARTED_RE = re.compile(r"^\*\*Started:\*\*\s*(\d{4}-\d{2}-\d{2}T\d{2}:\d{2}Z)\s*$", re.MULTILINE)
BASE_RE = re.compile(r"^\*\*Base commit:\*\*\s*`?([0-9a-f]{7,40})`?\s*$", re.MULTILINE)

NO_AGENT_PHRASE = "No agent is active"


def _run(*argv: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(argv, cwd=ROOT, capture_output=True, text=True)


def _stamp(value: str) -> datetime:
    return datetime.strptime(value, "%Y-%m-%dT%H:%MZ")


def live_rows(registry_text: str) -> list[str]:
    """Session ids whose status is live, parsed positionally from the table."""
    out: list[str] = []
    for line in registry_text.splitlines():
        if not line.startswith("|"):
            continue
        cells = [c.strip().strip("*").strip("`").strip()
                 for c in line.strip().strip("|").split("|")]
        if len(cells) < 6:
            continue
        if re.fullmatch(r"[A-Za-z0-9]{4}", cells[0]) and cells[1].startswith("20"):
            if cells[5].lower() in LIVE_STATUSES:
                out.append(cells[1])
    return out


def changed_paths(base: str) -> list[str]:
    """Committed-since-base plus working-tree changes — the session's real footprint."""
    committed = _run("git", "diff", "--name-only", f"{base}..HEAD").stdout.split("\n")
    dirty = [ln[3:].strip() for ln in _run("git", "status", "--porcelain").stdout.split("\n")
             if len(ln) > 3 and ln[2] == " "]
    return sorted({p for p in (committed + dirty) if p.strip()})


def recording_gaps(session_id: str) -> list[str]:
    """Checks 3 and 4 — *is the session's work recorded in its own log?*

    Shared by the blocking gate and by `--warn-only`, so the advisory pre-commit warning
    and the blocking pre-push refusal can never drift apart in what they consider
    recorded. A warning that checks less than the gate it precedes is worse than no
    warning: it teaches the author that green means safe.
    """
    path = SESSIONS / f"{session_id}.md"
    if not path.is_file():
        return [f"{session_id} is live in REGISTRY.md but has no session file"]
    text = path.read_text(encoding="utf-8")
    base_match = BASE_RE.search(text)
    if not base_match:
        return [f"{session_id}: session header lacks a parseable `Base commit`"]
    base = base_match.group(1)
    gaps: list[str] = []

    # 3: every changed file must be named in the session log's BODY.
    #
    # Deliberately not the whole file. The header carries a `Files owned` line listing
    # the paths the session claims — matching against the whole file makes this check
    # satisfiable by editing one metadata line, with no record of the work at all.
    # Measured while writing this gate: with the header included it PASSED on a session
    # that had recorded nothing about two new scripts. Restricting the search to the body
    # after the append-only notice forces the file to be *discussed*.
    body = text.split("> Append-only", 1)[-1]
    unrecorded = [p for p in changed_paths(base) if p not in body and Path(p).name not in body]
    if unrecorded:
        gaps.append(
            f"{session_id}: {len(unrecorded)} changed file(s) are not named in the session "
            f"log's body (the header's `Files owned` line does not count as a record): "
            f"{unrecorded[:8]}" + (" …" if len(unrecorded) > 8 else "")
        )

    # 4: every commit except HEAD must be listed. HEAD is exempt because the commit that
    # writes the list cannot contain its own sha.
    log = _run("git", "log", "--format=%h %H", f"{base}..HEAD").stdout.split()
    shas = [(log[i], log[i + 1]) for i in range(0, len(log), 2)]
    unlisted = [short for short, full in shas[1:] if short not in text and full not in text]
    if unlisted:
        gaps.append(
            f"{session_id}: {len(unlisted)} commit(s) since Base commit {base} are not listed "
            f"in the session log: {unlisted[:8]}" + (" …" if len(unlisted) > 8 else "")
            + " (HEAD is exempt: the commit that writes the list cannot contain its own sha)"
        )
    return gaps


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument(
        "--warn-only", action="store_true",
        help="advisory mode for the pre-commit hook: report recording gaps, never block",
    )
    args = parser.parse_args(argv)

    if args.warn_only:
        # P7 is explicit that pre-commit hooks must WARN, not block: a blocking hook
        # trains agents to reach for `--no-verify`, or to write minimal records that
        # satisfy it — "both worse than no hook". Blocking enforcement lives in the
        # pre-push hook and in CI, which is where this same check runs for real.
        #
        # It deliberately reuses `recording_gaps`, the function the blocking gate uses.
        # An advisory warning that checks less than the gate it precedes would teach the
        # author that green means safe.
        live = live_rows(REGISTRY.read_text(encoding="utf-8"))
        if not live:
            return 0
        gaps = recording_gaps(live[0])
        if gaps:
            print("WARN (advisory — this does NOT block the commit):")
            for gap in gaps:
                print(f"  - {gap}")
            print("  Record it now:  python3 scripts/macp_log.py PROGRESS \"...\"")
            print("  The push WILL be refused until the record is in sync.")
        else:
            print("OK (advisory): the session record covers the working tree.")
        return 0

    problems: list[str] = []

    # ── 1 + 2: the two existing gates, so the hook has a single entry point ──────
    for label, argv in (("state tree", [sys.executable, "tests/repo/test_state_tree.py"]),
                        ("startup gate", [sys.executable, "scripts/macp_startup_gate.py"])):
        proc = _run(*argv)
        if proc.returncode != 0:
            print(f"FAIL: {label} failed — the sync gate cannot pass while it does.", file=sys.stderr)
            print((proc.stdout + proc.stderr).strip()[-2000:], file=sys.stderr)
            return 1

    registry_text = REGISTRY.read_text(encoding="utf-8")
    dashboard_text = DASHBOARD.read_text(encoding="utf-8")
    index_text = INDEX.read_text(encoding="utf-8")

    if not re.search(r"^\|\s*`[A-Za-z0-9]{4}`\s*\|\s*`20", registry_text, re.MULTILINE):
        print("FAIL: parsed no agent rows from state/REGISTRY.md — the table shape changed.",
              file=sys.stderr)
        return 1

    live = live_rows(registry_text)

    # ── Scope: live sessions, PLUS the most recently started one ─────────────────
    #
    # Live-only would make this gate vacuous at exactly the moment it matters most. A
    # session is normally closed and *then* pushed, so by the time CI runs, no session
    # is live and every per-session check below would be skipped — the gate would pass
    # on an empty set and certify nothing. Including the latest session by `Started`
    # means the record being pushed is always in scope, whichever order the agent uses.
    #
    # MACP runs one session at a time, so "the most recently started" is the session
    # whose commits are in this push.
    def _started_of(session_id: str) -> datetime:
        match = STARTED_RE.search((SESSIONS / f"{session_id}.md").read_text(encoding="utf-8"))
        return _stamp(match.group(1)) if match else datetime.min

    all_sessions = sorted(p.stem for p in SESSIONS.iterdir() if p.is_file() and p.suffix == ".md")
    latest = max(all_sessions, key=_started_of) if all_sessions else None
    in_scope = sorted(set(live) | ({latest} if latest else set()))

    # ── 5: the DASHBOARD and REGISTRY must agree about who is live ───────────────
    if live:
        for sid in live:
            if sid not in dashboard_text:
                problems.append(
                    f"REGISTRY.md has {sid} live, but DASHBOARD.md's agent note never names it — "
                    "the dashboard and the registry disagree about who is working"
                )
    elif NO_AGENT_PHRASE not in dashboard_text:
        problems.append(
            f"no session is live in REGISTRY.md, but DASHBOARD.md does not say "
            f"\"{NO_AGENT_PHRASE}\". The agent note must state the no-agent case explicitly, "
            "or a reader cannot tell a quiet repository from a stale dashboard."
        )

    # ── 6: the dashboard must have been reconciled during the session ────────────
    reconciled_match = RECONCILED_RE.search(dashboard_text)
    if not reconciled_match:
        problems.append("DASHBOARD.md has no parseable `Last Reconciled` stamp")
    reconciled = _stamp(reconciled_match.group(1)) if reconciled_match else None

    for sid in in_scope:
        session_path = SESSIONS / f"{sid}.md"
        if not session_path.is_file():
            problems.append(f"{sid} is in scope but has no session file")
            continue
        text = session_path.read_text(encoding="utf-8")

        started_match = STARTED_RE.search(text)
        base_match = BASE_RE.search(text)
        if not started_match or not base_match:
            problems.append(f"{sid}: session header lacks a parseable `Started` or `Base commit`")
            continue
        started = _stamp(started_match.group(1))
        base = base_match.group(1)

        # 6 (continued)
        if reconciled and reconciled < started:
            problems.append(
                f"{sid}: DASHBOARD.md was last reconciled "
                f"{reconciled.strftime('%Y-%m-%dT%H:%MZ')} but the session started "
                f"{started.strftime('%Y-%m-%dT%H:%MZ')} — the dashboard was never reconciled "
                "during this session"
            )

        # 3 + 4: is the work recorded? Shared with --warn-only, so the advisory warning
        # and the blocking refusal cannot disagree about what "recorded" means.
        problems.extend(recording_gaps(sid))

        if sid not in index_text:
            problems.append(f"{sid} has no INDEX.md row — the session is invisible to history")

    if problems:
        print("FAIL: session record and state files are NOT in sync:", file=sys.stderr)
        for problem in problems:
            print(f"  - {problem}", file=sys.stderr)
        print(
            "\nThe push is refused. Record the work in the session log, reconcile "
            "state/DASHBOARD.md,\nand commit the state changes before pushing again. "
            "MACP's whole purpose is that the\nrepository — not an agent's context window — "
            "is the shared memory.",
            file=sys.stderr,
        )
        return 1

    if not live:
        print(f"OK: no live session, and DASHBOARD.md states the no-agent case. "
              f"The most recent session ({latest}) was still verified against git — "
              f"closing a session does not put its record beyond this check.")
        return 0
    print(f"OK: {len(live)} live session(s) in sync — record, state files and git agree "
          f"(dashboard reconciled {reconciled_match.group(1)}).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
