#!/usr/bin/env python3
"""MACP startup receipt — run STEP 8's five checks and record that you ran them.

**The gap this closes.** The MACP gates shipped in PR #83 are enforced at PUBLISH time:
the pre-push hook and the ``macp-gates`` CI job. Nothing runs at START time. On
2026-10-02 a session did its reconnaissance, reported numbers it had not measured, and
never registered — and **no gate fired, because it never pushed.** Three of STEP 8's five
checks were run inside ``gate_status.py --check`` rather than by the agent itself, one was
substituted (``gh pr checks`` → ``gh run list``), and the requirement and UNRES counts were
repeated from ``DASHBOARD.md`` without opening ``verification.yaml``. The gates were not
broken; they were in the wrong place.

**What this does.** It runs all five STEP 8 checks *itself*, one subprocess each, and
writes ``state/verification.json`` recording each check's name, command, exit code,
duration and timestamp. Registration, logging and pushing then all require a receipt whose
``ran_at`` is at or after the session's ``Started``.

**The honest limit — read this before trusting the gate.** No tool can force an agent to
run a command. An agent can always ignore this script, and no hook fires at the moment of
*starting*. What this does instead is make an unverified, unregistered session **FAIL EVERY
GATE IT TOUCHES**, rather than making it impossible to begin:

* ``scripts/macp_log.py`` refuses to append without a current receipt, so the moment an
  agent wants to record anything it is forced to verify first;
* ``tests/repo/test_state_tree.py`` fails on any IN-PROGRESS session lacking one;
* ``scripts/macp_sync_gate.py`` refuses the push;
* CI refuses the merge.

That converts "STEP 8 was skipped" from *silence* into *a named failure at the first
enforced surface*. It does not, and cannot, prevent the skip itself.

**Why one JSON file and not a directory.** PROTOCOL.md §2 fixes the structure of ``state/``.
A new *directory* would amend it; a single file keyed by session id does not, and it keeps
every session's receipt in one place a guard can read in one open.

**Environment-blocked is not red.** The sandbox injects a ``sitecustomize.py`` shim that
enforces a per-turn delete budget and raises ``SystemExit(1)`` with
``SAFE_DELETE_BULK_CONFIRM_REQUIRED`` when it is spent. That makes the full suite fail in a
turn that has already done other work, and pass in a fresh one. It is a property of the
environment, not a defect in the repository, so such a run is recorded as
``environment_blocked`` — which gates treat as *not green* without calling the repo red.

Usage::

    python3 scripts/startup_receipt.py                 # run the five checks, write receipt
    python3 scripts/startup_receipt.py --session <id>  # attribute to a specific session
    python3 scripts/startup_receipt.py --check         # is there a current green receipt?
"""
from __future__ import annotations

import argparse
import json
import re
import shutil
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))

from atomic_write import write_text_atomic  # noqa: E402

REGISTRY = ROOT / "state" / "REGISTRY.md"
SESSIONS = ROOT / "state" / "sessions"
RECEIPT = ROOT / "state" / "verification.json"

SCHEMA = "macp-startup-receipt/1"

LIVE_STATUSES = frozenset({"active", "in-progress"})
STARTED_RE = re.compile(r"^\*\*Started:\*\*\s*(\d{4}-\d{2}-\d{2}T\d{2}:\d{2}Z)\s*$", re.MULTILINE)
BRANCH_RE = re.compile(r"^\*\*Branch:\*\*\s*`?([^\s`]+)`?\s*$", re.MULTILINE)
BASE_RE = re.compile(r"^\*\*Base commit:\*\*\s*`?([0-9a-fA-F]{4,40})`?\s*$", re.MULTILINE)

# The sandbox's delete-guard marker. Its presence means the environment refused, not that
# the repository is broken.
ENV_BLOCKED_MARKER = "SAFE_DELETE_BULK_CONFIRM_REQUIRED"


def _stamp(value: str) -> datetime:
    return datetime.strptime(value, "%Y-%m-%dT%H:%MZ")


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%MZ")


def pytest_argv() -> tuple[str, ...]:
    """An interpreter that actually owns pytest, else the one running this script.

    ``/usr/bin/python3`` has numpy but no pytest, and ``.venv/bin/python`` has pytest but
    no numpy. Invoking the wrong one makes the suite exit non-zero for a reason that has
    nothing to do with the code, which would read as a red gate.
    """
    venv = ROOT / ".venv" / "bin" / "python"
    for candidate in (str(venv), sys.executable):
        if not candidate or not shutil.which(candidate) and not Path(candidate).is_file():
            continue
        probe = subprocess.run([candidate, "-c", "import pytest"],
                               cwd=ROOT, capture_output=True, text=True)
        if probe.returncode == 0:
            return (candidate, "-m", "pytest", "tests/", "-q")
    return (sys.executable, "-m", "pytest", "tests/", "-q")


def checks_for(branch: str) -> tuple[tuple[str, tuple[str, ...]], ...]:
    """The five STEP 8 checks, each as its own subprocess.

    (name, argv) pairs. Nothing here is wrapped: one subprocess per check, so a single
    command reporting five results is impossible.
    """
    # `ci` reads `main`, not the session's branch: the question STEP 8 asks is whether the
    # integration branch is green. A freshly cut branch has no runs at all, so checking it
    # would pass on an empty result — a vacuous green, which is worse than no check.
    return (
        ("pr-list", ("gh", "pr", "list", "--state", "open")),
        ("ci", ("gh", "run", "list", "--branch", "main", "--limit", "5")),
        ("chain", (sys.executable, "scripts/verify_all.py")),
        ("suite", pytest_argv()),
        ("state-tree", (sys.executable, "tests/repo/test_state_tree.py")),
    )


def live_session_ids(registry_text: str) -> list[str]:
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


def load_receipt() -> dict:
    if not RECEIPT.is_file():
        return {}
    try:
        return json.loads(RECEIPT.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return {}


def session_started(session_id: str) -> datetime | None:
    path = SESSIONS / f"{session_id}.md"
    if not path.is_file():
        return None
    match = STARTED_RE.search(path.read_text(encoding="utf-8"))
    return _stamp(match.group(1)) if match else None


def session_branch(session_id: str) -> str:
    path = SESSIONS / f"{session_id}.md"
    if not path.is_file():
        return "main"
    match = BRANCH_RE.search(path.read_text(encoding="utf-8"))
    return match.group(1) if match else "main"


def phase_b_complete(session_id: str) -> tuple[bool, str]:
    """Whether the live session has finished registration phase B.

    Phase A (step 1) writes identity only; phase B (step 2) fills ``Branch``,
    ``Base commit`` and ``files_owned`` from recon. The sync gate derives both the
    changed-file set and the commit list from ``Base commit``, so a guessed value
    makes every downstream guard measure the wrong repository. This returns the truth
    of "phase B is present and resolves in git" plus a reason fit for a refusal.
    """
    path = SESSIONS / f"{session_id}.md"
    if not path.is_file():
        return False, f"{session_id} has no session file, so phase B cannot exist"
    text = path.read_text(encoding="utf-8")
    branch_m = BRANCH_RE.search(text)
    base_m = BASE_RE.search(text)
    if not branch_m:
        return False, f"{session_id}: header has no `Branch` field (phase B not run)"
    if not base_m:
        return False, f"{session_id}: header has no `Base commit` field (phase B not run)"
    branch, base = branch_m.group(1), base_m.group(1)
    if not _branch_resolves_in_git(branch):
        return False, f"{session_id}: `Branch: {branch}` does not resolve in git"
    if subprocess.run(["git", "rev-parse", "--verify", "--quiet", base],
                      cwd=ROOT, capture_output=True, text=True).returncode != 0:
        return False, f"{session_id}: `Base commit: {base}` does not resolve in git"
    return True, f"{session_id} phase B complete (branch {branch}, base {base})"


def status_for(session_id: str, *, now: datetime | None = None) -> tuple[str, str]:
    """(status, reason) for one session: ok | stale | missing | environment_blocked | red.

    ``ok`` requires a receipt whose ``ran_at`` is at or after the session's ``Started`` —
    an old receipt means the checks were run before this session existed.
    """
    started = session_started(session_id)
    if started is None:
        return "missing", f"{session_id} has no session file or no parseable `Started` stamp"
    entry = load_receipt().get("sessions", {}).get(session_id)
    if not entry:
        return "missing", (
            f"{session_id} has no STEP 8 receipt — STEP 8 was never run for this session"
        )
    ran_at = _stamp(entry["ran_at"])
    if ran_at < started:
        return "stale", (
            f"{session_id} started {started.strftime('%Y-%m-%dT%H:%MZ')} but its receipt was "
            f"written {ran_at.strftime('%Y-%m-%dT%H:%MZ')} — the checks predate the session"
        )
    status = entry.get("status", "red")
    if status == "ok":
        return "ok", f"{session_id} verified at {entry['ran_at']}"
    if status == "environment_blocked":
        blocked = [c["name"] for c in entry.get("checks", []) if c["status"] != "ok"]
        return "environment_blocked", (
            f"{session_id}: receipt at {entry['ran_at']} is not green — "
            f"{blocked} could not run ({ENV_BLOCKED_MARKER}); re-run in a fresh turn"
        )
    failed = [c["name"] for c in entry.get("checks", []) if c["status"] == "red"]
    return "red", f"{session_id}: receipt at {entry['ran_at']} reports red: {failed}"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--session", help="session id to attribute the receipt to")
    parser.add_argument("--check", action="store_true",
                        help="report whether a current green receipt exists; do not run checks")
    args = parser.parse_args(argv)

    session_id = args.session or (live_session_ids(REGISTRY.read_text(encoding="utf-8")) or [None])[0]
    if not session_id:
        print("FAIL: no live session in state/REGISTRY.md to attribute a receipt to.\n"
              "A receipt proves that *this* session verified; with no session there is\n"
              "nothing to prove. Register first (state/STARTUP.md step 1), or pass "
              "--session <id>.", file=sys.stderr)
        return 3
    if not (SESSIONS / f"{session_id}.md").is_file():
        print(f"FAIL: {session_id} has no session file, so it cannot hold a `Started` stamp.",
              file=sys.stderr)
        return 3

    # Phase B gate. Registration is two-phase: step 1 writes identity only, step 2 runs
    # recon and fills Branch/Base commit. Verification cannot run until phase B is complete
    # and the values actually resolve in git — a session that skipped recon cannot obtain a
    # receipt, and without a receipt nothing downstream accepts its work.
    ok, reason = phase_b_complete(session_id)
    if not ok:
        print(f"FAIL: {reason}", file=sys.stderr)
        print("Run git recon and fill Branch/Base commit (state/STARTUP.md step 2) "
              "before verifying.", file=sys.stderr)
        return 3

    if args.check:
        status, reason = status_for(session_id)
        if status == "ok":
            print(f"OK: {reason}")
            return 0
        print(f"FAIL: {reason}", file=sys.stderr)
        print("\nFix: python3 scripts/startup_receipt.py", file=sys.stderr)
        return 1

    branch = session_branch(session_id)
    ran_at = _now()
    results: list[dict] = []
    print(f"STEP 8 receipt for {session_id} (branch {branch}) — {ran_at}\n")

    for name, command in checks_for(branch):
        started = time.monotonic()
        proc = subprocess.run(command, cwd=ROOT, capture_output=True, text=True)
        elapsed = round(time.monotonic() - started, 2)
        blob = proc.stdout + proc.stderr
        if proc.returncode == 0:
            status = "ok"
        elif ENV_BLOCKED_MARKER in blob:
            status = "environment_blocked"
        else:
            status = "red"
        results.append({
            "name": name,
            "command": " ".join(command),
            "exit_code": proc.returncode,
            "duration_s": elapsed,
            "status": status,
        })
        print(f"  {status:>19}  {name:<11} exit={proc.returncode}  {elapsed}s"
              + ("  " + command[-1] if name != "suite" else ""))

    if any(r["status"] == "red" for r in results):
        overall = "red"
    elif any(r["status"] == "environment_blocked" for r in results):
        overall = "environment_blocked"
    else:
        overall = "ok"

    receipt = load_receipt()
    receipt["schema"] = SCHEMA
    receipt.setdefault("sessions", {})[session_id] = {
        "ran_at": ran_at,
        "branch": branch,
        "status": overall,
        "checks": results,
    }
    receipt["sessions"] = dict(sorted(receipt["sessions"].items()))
    write_text_atomic(RECEIPT, json.dumps(receipt, indent=2) + "\n")

    print(f"\nWrote {RECEIPT.relative_to(ROOT)} — overall status: {overall}")
    if overall == "red":
        print("The checks above are red. Fix them; STEP 8 is mandatory.", file=sys.stderr)
        return 1
    if overall == "environment_blocked":
        print(f"Not green: the environment refused ({ENV_BLOCKED_MARKER}), which is a "
              "per-turn delete budget rather than a defect. Re-run as the first command "
              "of a fresh turn.", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
