#!/usr/bin/env python3
import pathlib, os, stat
ROOT = pathlib.Path(__file__).resolve().parent.parent
HOOKS_DIR = ROOT / ".git" / "hooks"
PRE_COMMIT = """#!/bin/bash
set -e
echo "=== Pre-commit Strong ==="
PYTHON_BIN="${VIRTUAL_ENV:+$VIRTUAL_ENV/bin/python}"
PYTHON_BIN="${PYTHON_BIN:-python3}"
LEAK=$(grep -R -i "api_key\\s*=\\|secret.*=" content/ connections/ sources/ --include="*.md" --include="*.yaml" 2>/dev/null | grep -v "example" || true)
if [ -n "$LEAK" ]; then echo "$LEAK" | head -n 5; echo "FAIL: secret"; exit 1; fi
if find content/ -name "*.md" -exec grep -l "\\"vector\\":" {} \\; 2>/dev/null | head -n 1 | grep .; then echo "FAIL: embeddings in canonical"; exit 1; fi
"$PYTHON_BIN" scripts/validate.py
echo "--- docs impact (affected surface, advisory) ---"
"$PYTHON_BIN" scripts/docs.py impact || true
"$PYTHON_BIN" scripts/docs.py validate
echo "Pre-commit OK"
"""
PRE_PUSH = """#!/bin/bash
set -e
echo "=== Pre-push Strong ==="
PYTHON_BIN="${VIRTUAL_ENV:+$VIRTUAL_ENV/bin/python}"
PYTHON_BIN="${PYTHON_BIN:-python3}"
"$PYTHON_BIN" scripts/verify_all.py
"$PYTHON_BIN" scripts/verify_strong.py --quick
if ! git diff --exit-code -- exports reports >/dev/null 2>&1; then echo "FAIL: exports not fresh"; exit 1; fi
"$PYTHON_BIN" scripts/docs.py sync
if ! git diff --exit-code >/dev/null 2>&1; then echo "FAIL: docs sync produced changes (review and commit them)"; git status --porcelain | head -n 10; exit 1; fi
"$PYTHON_BIN" scripts/docs.py check
echo "Pre-push OK"
"""
def main():
    HOOKS_DIR.mkdir(parents=True, exist_ok=True)
    for name, content in [("pre-commit", PRE_COMMIT), ("pre-push", PRE_PUSH)]:
        p = HOOKS_DIR / name
        p.write_text(content, encoding='utf-8')
        p.chmod(p.stat().st_mode | stat.S_IEXEC)
        print(f"Installed {name}")
if __name__ == "__main__": main()
