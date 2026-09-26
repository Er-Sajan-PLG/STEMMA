"""Every fenced webapp start command in the docs shows the operator identity first.

The webapp has no login: human edits/staging are attributed to STEMMA_REVIEWER_ID
and refused without it, so a copy-pasted start command must carry it.
"""
from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DOCS = [ROOT / "README.md", ROOT / "AGENTS.md", *sorted((ROOT / "docs").glob("*.md"))]


def _is_start(line: str) -> bool:
    """`[VAR=value ...] python3 webapp/server.py ...` (token scan, no regex)."""
    tokens = line.split()
    while tokens and "=" in tokens[0] and not tokens[0].startswith("python"):
        tokens.pop(0)
    return tokens[:2] == ["python3", "webapp/server.py"]


def _fenced_blocks(text: str) -> list[list[str]]:
    """Lines inside ``` fences (linear scan; no backtracking regex)."""
    blocks, current = [], None
    for line in text.splitlines():
        if line.lstrip().startswith("```"):
            if current is None:
                current = []
            else:
                blocks.append(current)
                current = None
        elif current is not None:
            current.append(line)
    return blocks


def test_fenced_webapp_start_commands_set_reviewer_id():
    missing, seen = [], 0
    for doc in DOCS:
        for lines in _fenced_blocks(doc.read_text(encoding="utf-8")):
            for i, line in enumerate(lines):
                if _is_start(line):
                    seen += 1
                    before = "\n".join(lines[:i])
                    if "STEMMA_REVIEWER_ID=human:" not in before and "STEMMA_REVIEWER_ID=human:" not in line:
                        missing.append(f"{doc.relative_to(ROOT)}: {line.strip()}")
    assert seen >= 3, "expected README, AGENTS.md and docs/WEBAPP.md start blocks"
    assert missing == [], missing
