#!/usr/bin/env python3
"""Verify STEMMA repository.

Usage:
  python3 scripts/verify.py
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent


def main() -> int:
    cmd = [sys.executable, str(REPO_ROOT / "scripts" / "validate.py")]
    print(f"→ Verifying STEMMA: {' '.join(cmd)}")
    result = subprocess.run(cmd, cwd=REPO_ROOT)
    if result.returncode == 0:
        print("✓ STEMMA verification PASS")
    else:
        print(f"✗ STEMMA verification FAIL (exit {result.returncode})", file=sys.stderr)
    return result.returncode


if __name__ == "__main__":
    sys.exit(main())