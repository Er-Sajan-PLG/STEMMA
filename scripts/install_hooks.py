#!/usr/bin/env python3
import pathlib, os, stat
ROOT = pathlib.Path(__file__).resolve().parent.parent
HOOKS_DIR = ROOT / ".git" / "hooks"
PRE_COMMIT = """#!/bin/bash
set -e
echo "=== Pre-commit Strong ==="
if grep -R -i "api_key\\s*=\\|secret.*=" content/ connections/ sources/ --include="*.md" --include="*.yaml" 2>/dev/null | grep -v "example" | head -n 5; then echo "FAIL: secret"; exit 1; fi
if find content/ -name "*.md" -exec grep -l "\\"vector\\":" {} \\; 2>/dev/null | head -n 1 | grep .; then echo "FAIL: embeddings in canonical"; exit 1; fi
python3 scripts/validate.py
echo "Pre-commit OK"
"""
PRE_PUSH = """#!/bin/bash
set -e
echo "=== Pre-push Strong ==="
python3 scripts/verify_all.py
python3 scripts/verify_strong.py --quick
if ! git diff --exit-code -- exports reports >/dev/null 2>&1; then echo "FAIL: exports not fresh"; exit 1; fi
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
