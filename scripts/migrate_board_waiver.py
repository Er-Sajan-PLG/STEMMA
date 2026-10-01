#!/usr/bin/env python3
"""One-shot, idempotent migration: retire the board stage from records promoted
under the pre-waiver chain.

Owner ruling 2026-10-01 waived the board stage while the owner is the only
validator (ENF-STEMMA-HITL-003 board_waiver). Records that already carry a board
stage in provenance.promotion_history now violate the required chain
validator -> independent_validator, so this script removes the board entry and
records the act as a board_stage_retired note for the audit trail.

Run:  .venv/bin/python scripts/migrate_board_waiver.py [--check]

Idempotent: a record with no board stage is left untouched.
"""
from __future__ import annotations

import argparse
import pathlib
import sys

import yaml

ROOT = pathlib.Path(__file__).resolve().parent.parent
CONTENT = ROOT / "content"
CONNECTIONS = ROOT / "connections"

RETIRE_NOTE = (
    "board stage retired 2026-10-01 under the owner board waiver "
    "(ENF-STEMMA-HITL-003 board_waiver) — the owner is the sole validator, so the "
    "required chain is validator -> independent_validator; the earlier board entry "
    "was a formality and is removed, not re-dated"
)


def _load(path: pathlib.Path) -> tuple[dict, str]:
    """Return (data, kind) where kind is 'frontmatter' or 'plain'."""
    raw = path.read_text(encoding="utf-8")
    if raw.startswith("---"):
        parts = raw.split("---", 2)
        if len(parts) < 3:
            raise ValueError(f"{path}: malformed frontmatter")
        return yaml.safe_load(parts[1]) or {}, "frontmatter"
    return yaml.safe_load(raw) or {}, "plain"


def _dump(path: pathlib.Path, data: dict, kind: str) -> None:
    clean = {k: v for k, v in data.items() if not k.startswith("_")}
    dumped = yaml.safe_dump(clean, sort_keys=False, allow_unicode=True)
    if kind == "frontmatter":
        raw = path.read_text(encoding="utf-8")
        body = raw.split("---", 2)[2]
        path.write_text(f"---\n{dumped}---{body}", encoding="utf-8")
    else:
        path.write_text(dumped, encoding="utf-8")


def _migrate(path: pathlib.Path, check: bool) -> bool:
    data, kind = _load(path)
    prov = data.get("provenance")
    if not isinstance(prov, dict):
        return False
    hist = prov.get("promotion_history")
    if not isinstance(hist, list) or not hist:
        return False
    kept = [e for e in hist if not (isinstance(e, dict) and e.get("stage") == "board")]
    if len(kept) == len(hist):
        return False  # nothing to do — idempotent
    prov["promotion_history"] = kept
    # Record the act on the terminal entry so the audit trail explains the gap
    # without inventing a new provenance key (the schema is closed there).
    if kept and isinstance(kept[-1], dict):
        kept[-1]["board_waived"] = True
        kept[-1]["board_waived_reason"] = RETIRE_NOTE
    if not check:
        _dump(path, data, kind)
    return True


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--check", action="store_true",
                    help="report what would change without writing")
    args = ap.parse_args()

    targets = sorted(CONTENT.rglob("*.md")) + sorted(CONNECTIONS.glob("*.yaml"))
    changed = 0
    for p in targets:
        try:
            if _migrate(p, args.check):
                changed += 1
                print(f"{'WOULD RETIRE' if args.check else 'RETIRED'} board stage: "
                      f"{p.relative_to(ROOT)}")
        except Exception as exc:  # noqa: BLE001 — report and continue
            print(f"skip {p.relative_to(ROOT)}: {exc}", file=sys.stderr)
    print(f"{changed} record(s) {'to update' if args.check else 'updated'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
