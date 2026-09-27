#!/usr/bin/env python3
"""Ecosystem independence invariant (ADR-0027; un-stubbed per ADR-0051 R3).

STEMMA is an independent foundation. Tracked living files must not:
  - reference retired design documents (NORTHSTAR.md, STEMMA-SPECIFICATION.md,
    the deleted docs/force.md target of the old Quick Start),
  - reference sibling ecosystem products as controllers (STEM-TUITION, JARVIS)
    — consumer *names* like LearningHub/PROFESSOR-J are allowed because the
    consumer registry speaks about consumers, never grants control,
  - use the retired `lhs:` ID namespace (ADR-0027: replaced by `stemma:`).

Exempt by design (history, per ADR-0027 §3 and ADR-0051):
  - docs/decisions/**   ADR documents are immutable history
  - archive/**          archived old design is immutable history
"""
from __future__ import annotations

import pathlib
import re
import subprocess
import sys

ROOT = pathlib.Path(__file__).resolve().parents[2]

EXEMPT_PREFIXES = ("docs/decisions/", "archive/")
# Enforcement points must *name* the forbidden patterns to reject them
# (guards against the retired namespace, doc-consistency RETIRED list, this checker).
EXEMPT_FILES = {
    "tests/repo/test_independence.py",
    "tests/repo/test_docs_consistency.py",
    "scripts/validate.py",
    "scripts/check_id_immutability.py",
}

# (label, compiled pattern) — matched against text content of tracked files.
FORBIDDEN = [
    ("retired doc NORTHSTAR.md", re.compile(r"NORTHSTAR\.md")),
    ("retired doc STEMMA-SPECIFICATION.md", re.compile(r"STEMMA-SPECIFICATION\.md")),
    ("dead quick-start target force.md", re.compile(r"(?:content/physics/mechanics/|docs/)force\.md")),
    ("ecosystem controller reference STEM-TUITION", re.compile(r"STEM-TUITION")),
    ("ecosystem reference JARVIS", re.compile(r"JARVIS")),
    ("retired ID namespace lhs:", re.compile(r"\blhs:")),
]


def tracked_files() -> list[pathlib.Path]:
    out = subprocess.run(
        ["git", "ls-files"], cwd=ROOT, capture_output=True, text=True, check=True
    ).stdout.splitlines()
    files = []
    for rel in out:
        if rel.startswith(EXEMPT_PREFIXES) or rel in EXEMPT_FILES:
            continue
        p = ROOT / rel
        if p.suffix.lower() not in {".md", ".py", ".yaml", ".yml", ".json", ".toml", ".txt", ".sh", ".cjs", ".ts", ".js", ".html", ".css"}:
            continue
        files.append(p)
    return files


def main() -> int:
    problems = []
    for p in tracked_files():
        try:
            text = p.read_text(encoding="utf-8", errors="replace")
        except OSError:
            continue
        rel = p.relative_to(ROOT).as_posix()
        for label, pat in FORBIDDEN:
            for i, line in enumerate(text.splitlines(), start=1):
                if pat.search(line):
                    problems.append(f"{rel}:{i}: {label} ({line.strip()[:80]})")
    if problems:
        print("INDEPENDENCE FAILURES:")
        for prob in problems:
            print(f"  - {prob}")
        return 1
    print("PASS: no retired-doc references, no ecosystem controller references, no lhs: namespace outside history")
    return 0


if __name__ == "__main__":
    sys.exit(main())
