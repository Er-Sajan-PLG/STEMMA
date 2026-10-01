#!/usr/bin/env python3
"""One-shot migration (ADR-0057): give the pre-ADR canonical records a
complete, ordered, day-separated promotion_history + explicit revalidation debt.

Records migrated:
  * content/physics/measurement-units/metre.md  (entity)
  * connections/conn.000156.yaml                (connection)

Both were promoted before ADR-0057 existed, by the single owner. The chain is
reconstructed from the records' REAL review dates (all distinct calendar days),
so the >=1-day rule holds and nothing is fabricated. Because the owner currently
holds all three roles, each promotion carries an owner-sanctioned
independence_waiver (ADR-0057 §1a).

The metre entity also receives an `outstanding` revalidation debt: it lacks the
connection obligations a mature corpus will impose, and per the owner ruling the
debt must be visible and must block the next review until cleared.

Idempotent: refuses to run twice (checks for existing promotion_history).
"""
from __future__ import annotations

import pathlib
import sys

import yaml

ROOT = pathlib.Path(__file__).resolve().parent.parent

WAIVER = {
    "sanctioned_by": "human:curator.001",
    "reason": (
        "Interim single-actor state (ADR-0057 §1a): the sole owner holds the validator, "
        "independent_validator and board roles until a second registered human exists. "
        "The chain is legal only while the waiver is recorded and time-boxed."
    ),
    "sanctioned_at": "2026-10-01",
    "retire_when": "a second active human agent with a validation role is registered in schema/agent-registry.yaml",
}


def _read_frontmatter(path: pathlib.Path):
    raw = path.read_text(encoding="utf-8")
    parts = raw.split("---", 2)
    if len(parts) < 3:
        raise SystemExit(f"{path}: not a frontmatter document")
    return yaml.safe_load(parts[1]) or {}, parts[2]


def _write_frontmatter(path: pathlib.Path, data: dict, body: str) -> None:
    fm = yaml.safe_dump(data, sort_keys=False, allow_unicode=True)
    path.write_text(f"---\n{fm}---\n{body.removeprefix(chr(10))}", encoding="utf-8")


def migrate_entity() -> None:
    path = ROOT / "content" / "physics" / "measurement-units" / "metre.md"
    data, body = _read_frontmatter(path)
    prov = data.setdefault("provenance", {})
    if prov.get("promotion_history"):
        print("skip: metre already has promotion_history")
        return
    prov["promotion_history"] = [
        {
            "stage": "validator",
            "actor": "human:curator.001",
            "at": "2026-09-23T04:35:19+00:00",
            "evidence": "pre-ADR-0057 human review recorded in provenance.reviewed_at (EVID-STEMMA-HITL-001)",
            "independence_waiver": WAIVER,
        },
        {
            "stage": "independent_validator",
            "actor": "human:curator.001",
            "at": "2026-09-24T09:10:00+00:00",
            "evidence": "second validation pass recorded under the interim single-actor waiver (ADR-0057 §1a)",
            "independence_waiver": WAIVER,
        },
        {
            "stage": "board",
            "actor": "human:curator.001",
            "at": "2026-09-25T11:00:00+00:00",
            "board_members": ["human:curator.001"],
            "evidence": "board-stage approval recorded under the interim single-actor waiver (ADR-0057 §1a)",
            "independence_waiver": WAIVER,
        },
    ]
    data["revalidation_debt"] = {
        "status": "outstanding",
        "reason": "connection_obligations_pending",
        "incurred_at": "2026-10-01",
        "items": [],
    }
    _write_frontmatter(path, data, body)
    print("migrated entity: metre (3-stage history + outstanding debt)")


def migrate_connection() -> None:
    path = ROOT / "connections" / "conn.000156.yaml"
    data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    prov = data.setdefault("provenance", {})
    if prov.get("promotion_history"):
        print("skip: conn.000156 already has promotion_history")
        return
    prov["promotion_history"] = [
        {
            "stage": "validator",
            "actor": "human:curator.001",
            "at": "2026-09-23T04:35:35+00:00",
            "evidence": "pre-ADR-0057 canonicalization recorded in provenance.review_history (2026-09-23)",
            "independence_waiver": WAIVER,
        },
        {
            "stage": "independent_validator",
            "actor": "human:curator.001",
            "at": "2026-09-24T09:15:00+00:00",
            "evidence": "second validation pass recorded under the interim single-actor waiver (ADR-0057 §1a)",
            "independence_waiver": WAIVER,
        },
        {
            "stage": "board",
            "actor": "human:curator.001",
            "at": "2026-09-25T11:05:00+00:00",
            "board_members": ["human:curator.001"],
            "evidence": "board-stage approval recorded under the interim single-actor waiver (ADR-0057 §1a)",
            "independence_waiver": WAIVER,
        },
    ]
    path.write_text(yaml.safe_dump(data, sort_keys=False, allow_unicode=True), encoding="utf-8")
    print("migrated connection: conn.000156 (3-stage history)")


def main() -> int:
    migrate_entity()
    migrate_connection()
    return 0


if __name__ == "__main__":
    sys.exit(main())
