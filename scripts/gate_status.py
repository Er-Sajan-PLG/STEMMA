#!/usr/bin/env python3
"""Generate the DASHBOARD's Gate Status block (MACP gate design G2 + G3).

**Why this exists.** `state/DASHBOARD.md` carried a hand-written table of six gate
results, stamped with the moment someone last ran them. Nothing re-ran them, and no
guard could tell a fresh row from a nine-hour-old one. Measured on 2026-10-01: the
table's stamp was ~8.5 h stale and the `HEAD` row beside it was **11 commits** stale,
while every mechanically-guarded value in the same file was correct. The guards check
shape; that table was pure assertion.

The fix is not to police the table harder — it is to stop hand-writing it. This script
runs the gates and *generates* the block, in the same spirit as `status_truth.py`
owning the README counts and `review_manifest.py` owning the review manifest. A
generated value cannot be forgotten and cannot go stale: it is either fresh or CI's
freshness diff fails.

**Fail-closed, deliberately.** If any gate fails, nothing is written and the exit code
is 1. The block therefore always describes the *last fully green* run, and a session
that cannot produce one leaves the stamp behind — which is what
`scripts/macp_startup_gate.py` reads to detect a session that skipped its verification.

**What is deliberately NOT here.** The startup check that binds this block to an active
session lives in `scripts/macp_startup_gate.py`, not in the gate list below and not as a
pytest test. Both would deadlock: the artifact it checks is produced by the same run
that would have to pass first.

Usage:

    python3 scripts/gate_status.py            # run the gates, rewrite the block
    python3 scripts/gate_status.py --check    # verify the block is fresh; exit 1 if not
"""
from __future__ import annotations

import argparse
import re
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))

from atomic_write import write_text_atomic  # noqa: E402  (DEC-002: a gate byte-compares this)

DASHBOARD = ROOT / "state" / "DASHBOARD.md"

BEGIN = "<!-- BEGIN GENERATED: gate-status"
END = "<!-- END GENERATED: gate-status -->"


# ── Result extractors ────────────────────────────────────────────────────────
# Each takes (stdout, exit_code) and returns the cell text, or None to fall back to
# a bare `exit N`. A None from an extractor on a *passing* gate is not an error —
# some gates genuinely have nothing to report beyond their exit code.

def _extract_pytest(out: str, code: int) -> str | None:
    failed = re.search(r"(\d+) failed", out)
    passed = re.search(r"(\d+) passed", out)
    if failed:
        return f"**{failed.group(1)} FAILED**"
    return f"**{passed.group(1)} passed**" if passed else None


def _extract_verify_all(out: str, code: int) -> str | None:
    ok = len(re.findall(r"^OK:", out, re.MULTILINE))
    fail = len(re.findall(r"^FAIL:", out, re.MULTILINE))
    if ok or fail:
        return f"**{ok} OK / {fail} FAIL** (exit {code})"
    return None


def _extract_docs_status(out: str, code: int) -> str | None:
    m = re.search(r"^Status:\s*(\w+)", out, re.MULTILINE)
    return f"**{m.group(1)}**" if m else None


def _extract_recovery(out: str, code: int) -> str | None:
    # The validator prints one long line: "RECOVERY VALIDATOR: PASS — 129 ids; 25
    # requirements; ... ; 9/9 checks clean". Match the two facts independently — an
    # earlier version required the checks count to follow the status immediately, so
    # the row silently degraded to a bare `exit 0`.
    status = re.search(r"RECOVERY VALIDATOR:\s*(\w+)", out)
    checks = re.search(r"(\d+)/(\d+) checks", out)
    if not status:
        return None
    if checks:
        return f"**{status.group(1)}** — {checks.group(1)}/{checks.group(2)} checks"
    return f"**{status.group(1)}**"


def _extract_state_tree(out: str, code: int) -> str | None:
    m = re.search(r"^(PASS|FAIL): state tree \((\d+)/(\d+)\)", out, re.MULTILINE)
    return f"**{m.group(1)} — {m.group(2)}/{m.group(3)}**" if m else None


def _extract_exit_only(out: str, code: int) -> str | None:
    return None


# A sandbox shim can intercept `Path.unlink` and enforce a **per-turn delete budget**,
# calling `_exit_bulk_guard_control` (which raises `SystemExit(1)`) once it is exceeded.
# `SystemExit` derives from `BaseException`, so nothing catching `Exception` sees it, and
# the affected gate fails with no ordinary error. Measured 2026-10-01/02: the full suite
# passes as a turn's first command and fails with 2 — then 6 — failures when the same turn
# has already done other work, which is the signature of accumulated budget rather than a
# code change.
#
# DEBT-007's lesson applies directly: a test whose *setup* is blocked must say which of the
# two happened rather than report a false regression. This gate does not get to skip — it
# still fails closed, because an unverifiable gate is not a green one — but it must not
# accuse the code of a defect it does not have.
ENVIRONMENT_BLOCK_MARKER = "SAFE_DELETE_BULK_CONFIRM_REQUIRED"


def _classify(output: str) -> str:
    return "environment-blocked" if ENVIRONMENT_BLOCK_MARKER in output else "red"


# ── The gates ────────────────────────────────────────────────────────────────

def _interpreter_for_pytest() -> str:
    """Use the venv when it exists; in CI there is none and sys.executable is right."""
    venv = ROOT / ".venv" / "bin" / "python"
    return str(venv) if venv.is_file() else sys.executable


def gates() -> tuple[tuple[str, list[str], object], ...]:
    return (
        ("pytest tests/ -q",
         [_interpreter_for_pytest(), "-m", "pytest", "tests/", "-q"], _extract_pytest),
        ("scripts/verify_all.py",
         [sys.executable, "scripts/verify_all.py"], _extract_verify_all),
        ("scripts/docs.py check",
         [sys.executable, "scripts/docs.py", "check"], _extract_docs_status),
        ("spec/machine-readable/validate_recovery.py",
         [sys.executable, "spec/machine-readable/validate_recovery.py"], _extract_recovery),
        ("scripts/verify_strong.py --quick",
         [sys.executable, "scripts/verify_strong.py", "--quick"], _extract_exit_only),
        ("tests/repo/test_state_tree.py",
         [sys.executable, "tests/repo/test_state_tree.py"], _extract_state_tree),
    )


def head_commit() -> str:
    return subprocess.run(
        ["git", "rev-parse", "--short", "HEAD"],
        cwd=ROOT, capture_output=True, text=True, check=True,
    ).stdout.strip()


def run_gates() -> tuple[list[tuple[str, str, int, str]], str]:
    """Run every gate.

    Returns (rows, rendered block). Each row carries the gate's exit code **and the
    tail of its output**, so a red gate is diagnosable from the failure message alone.
    That is not decoration: a previous failure in this repository was misdiagnosed
    twice because the reason had been piped away (`DEBT-007`), and an environment shim
    that fails closed exits the process rather than raising, so the exit code by itself
    says nothing about the cause.
    """
    rows: list[tuple[str, str, int, str]] = []
    for label, argv, extract in gates():
        proc = subprocess.run(argv, cwd=ROOT, capture_output=True, text=True)
        combined = proc.stdout + proc.stderr
        cell = extract(combined, proc.returncode) or f"exit {proc.returncode}"
        rows.append((label, cell, proc.returncode, combined))

    stamp = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%MZ")
    lines = [
        f"{BEGIN} — do not edit by hand; regenerate with `python3 scripts/gate_status.py` -->",
        f"**Measured:** {stamp} · **HEAD:** `{head_commit()}`",
        "",
        "| Gate | Result |",
        "|---|---|",
    ]
    lines += [f"| `{label}` | {cell} |" for label, cell, _, _ in rows]
    lines.append(END)
    return rows, "\n".join(lines) + "\n"


# ── Block surgery ────────────────────────────────────────────────────────────

def _block_bounds(text: str) -> tuple[int, int]:
    start = text.find(BEGIN)
    if start == -1:
        raise SystemExit(
            f"FAIL: {DASHBOARD.relative_to(ROOT)} has no `{BEGIN} ...` marker. The generated "
            "block cannot be located, so it cannot be kept fresh. Add the marker pair."
        )
    end = text.find(END, start)
    if end == -1:
        raise SystemExit(f"FAIL: generated block in {DASHBOARD.relative_to(ROOT)} is not closed by `{END}`")
    return start, end + len(END)


def current_block(text: str) -> str:
    start, end = _block_bounds(text)
    return text[start:end]


def _report_failures(rows: list[tuple[str, str, int, str]],
                     failed: list[tuple[str, int]]) -> None:
    """Print each red gate with the tail of its output — the cause, not just the code."""
    print(f"FAIL: refusing to write the gate block — {len(failed)} gate(s) are red:",
          file=sys.stderr)
    by_label = {label: tail for label, _, _, tail in rows}
    blocked: list[str] = []
    for label, code in failed:
        tail = by_label.get(label, "")
        kind = _classify(tail)
        if kind == "environment-blocked":
            blocked.append(label)
        print(f"\n--- {label} (exit {code}) — {kind} ---", file=sys.stderr)
        lines = tail.strip().splitlines()[-25:]
        print("\n".join(lines) if lines else "(no output)", file=sys.stderr)

    if blocked:
        print(
            "\nNOTE: the failure(s) above carry the sandbox delete-guard marker "
            f"({ENVIRONMENT_BLOCK_MARKER}).\nThat is a per-turn delete budget, not a defect "
            "in the code: the same gate\npasses when it is the first command of a fresh turn. "
            "Re-run before believing it.\nThe block is still not written — an unverifiable "
            "gate is not a green one.",
            file=sys.stderr,
        )


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--check", action="store_true",
                        help="verify the committed block matches a fresh run; exit 1 on drift")
    args = parser.parse_args(argv)

    rows, block = run_gates()
    failed = [(label, code) for label, _, code, _ in rows if code != 0]

    if args.check:
        on_disk = current_block(DASHBOARD.read_text(encoding="utf-8"))
        # The stamp moves every run, so compare everything except that one line.
        strip = lambda t: "\n".join(  # noqa: E731
            ln for ln in t.splitlines() if not ln.startswith("**Measured:**")
        )
        if strip(on_disk) != strip(block):
            print("FAIL: the DASHBOARD gate block is not what a fresh run produces.", file=sys.stderr)
            print("--- committed ---", file=sys.stderr)
            print(strip(on_disk), file=sys.stderr)
            print("--- fresh ---", file=sys.stderr)
            print(strip(block), file=sys.stderr)
            print("\nRegenerate with: python3 scripts/gate_status.py", file=sys.stderr)
            return 1
        if failed:
            _report_failures(rows, failed)
            return 1
        print("OK: DASHBOARD gate block is fresh and every gate is green.")
        return 0

    if failed:
        _report_failures(rows, failed)
        print(
            "\nNothing was written, deliberately: the block must always describe the last\n"
            "fully green run. A red gate therefore leaves the stamp behind, and\n"
            "scripts/macp_startup_gate.py will report the session as unverified.",
            file=sys.stderr,
        )
        return 1

    text = DASHBOARD.read_text(encoding="utf-8")
    start, end = _block_bounds(text)
    write_text_atomic(DASHBOARD, text[:start] + block + text[end:])
    print(f"OK: wrote the gate block ({len(rows)} gates, all green).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
