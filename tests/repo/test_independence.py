#!/usr/bin/env python3
"""Repository independence invariant (ADR-0027 §6, GOVERNANCE §12).

STEMMA must be understandable and useful with zero knowledge of the creator's
other projects. This gate fails if any living artifact — canonical data,
schemas, scripts, tests, CI, or the core documentation set — references a
private-ecosystem name.

Allowances (deliberate, bounded):
  * docs/decisions/** and docs/MIGRATIONS.md — historical record, explicitly
    grandfathered (decisions/README.md "Historical note").
  * scripts/check_id_immutability.py — contains the one documented namespace
    alias rule (`lhs:` → `stemma:`, ADR-0027) whose literal is load-bearing.
"""
from __future__ import annotations

import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parents[2]

# Ecosystem names that must never appear in living artifacts.
PATTERNS = re.compile(
    r"(?i)\b(jarvis|professor-?j|stem-?tuition|learninghub(?:stem)?|lhs|"
    r"3d-?ludo|stem-game|sajan|/home/[a-z]+/projects|ncdn)\b"
)

# Paths checked (everything that is "living architecture").
CHECKED = [
    "content",
    "connections",
    "sources",
    "schema",
    "scripts",
    "tests",
    "adapters",
    "explorer/src",
    "explorer/scripts",
    "explorer/package.json",
    ".github",
    "AGENTS.md",
    "README.md",
    "VERSION",
    "CONTRIBUTING.md",
    "commitlint.config.cjs",
    *[
        str(p.relative_to(ROOT))
        for p in (ROOT / "docs").glob("*.md")
    ],
]

# Explicit, bounded allowances.
ALLOWED_SUBSTRINGS = {
    # the one documented alias rule + its tests (ADR-0027)
    "scripts/check_id_immutability.py",
    # the migration-completeness guard must name the retired prefix to detect it
    "scripts/validate.py",
    "tests/curation/test_connection_immutability.py",  # pure-logic fixtures may use the old prefix
    "tests/repo/test_independence.py",                 # this file's own patterns
    # append-only historical log (pre-refoundation entries name the old identity)
    "docs/MIGRATIONS.md",
}


def violations() -> list[str]:
    found: list[str] = []
    for rel in CHECKED:
        base = ROOT / rel
        paths = (
            sorted(base.rglob("*") if base.is_dir() else [base])
        )
        for path in paths:
            if not path.is_file():
                continue
            rel_path = path.relative_to(ROOT).as_posix()
            if any(rel_path.startswith(a) or rel_path == a for a in ALLOWED_SUBSTRINGS):
                continue
            if path.suffix not in {".md", ".yaml", ".yml", ".json", ".py", ".ts",
                                   ".tsx", ".mjs", ".cjs", ".txt", ".toml", ""}:
                continue
            try:
                text = path.read_text(encoding="utf-8")
            except (UnicodeDecodeError, ValueError):
                continue  # binary
            for m in PATTERNS.finditer(text):
                line = text[: m.start()].count("\n") + 1
                found.append(f"{rel_path}:{line}: ecosystem reference {m.group(0)!r}")
    return found


def main() -> int:
    bad = violations()
    if bad:
        print("INDEPENDENCE FAILURES:")
        for b in bad:
            print(f"  - {b}")
        return 1
    print("ALL INDEPENDENCE TESTS PASS")
    return 0


if __name__ == "__main__":
    sys.exit(main())
