"""Every fenced webapp start command in the docs shows the operator identity first.

The webapp has no login: human edits/staging are attributed to STEMMA_REVIEWER_ID
and refused without it, so a copy-pasted start command must carry it.
"""
from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DOCS = [ROOT / "README.md", ROOT / "AGENTS.md", *sorted((ROOT / "docs").glob("*.md"))]
FENCE = re.compile(r"^```.*?$(.*?)^```", re.S | re.M)
START = re.compile(r"^\s*(?:\S+=\S+\s+)*python3 webapp/server\.py\b")


def test_fenced_webapp_start_commands_set_reviewer_id():
    missing, seen = [], 0
    for doc in DOCS:
        for block in FENCE.findall(doc.read_text(encoding="utf-8")):
            lines = block.splitlines()
            for i, line in enumerate(lines):
                if START.match(line):
                    seen += 1
                    before = "\n".join(lines[:i])
                    if "STEMMA_REVIEWER_ID=human:" not in before and "STEMMA_REVIEWER_ID=human:" not in line:
                        missing.append(f"{doc.relative_to(ROOT)}: {line.strip()}")
    assert seen >= 3, "expected README, AGENTS.md and docs/WEBAPP.md start blocks"
    assert missing == [], missing
