#!/usr/bin/env python3
"""Register an adaptive metadata extension dimension (ADR-0017).

One-command way to add a NEW knowledge-layer metadata dimension to the canonical
foundation "on the spot" — the operating contract for adaptive schema growth.
A dimension must exist here before it can be used as an `extensions` key on an
entity/connection/source object (validated by scripts/validate.py).

Usage:
    python3 scripts/register_extension.py add \
        --name symbol_set \
        --applies-to entity \
        --value-type string \
        [--enum a,b,c] \
        [--description "some text"] \
        [--registered-by process:x]

Exit codes: 0 ok (created or idempotent), 1 invalid usage/declaration.
"""
from __future__ import annotations

import argparse
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

try:
    import yaml
except ImportError:  # pragma: no cover
    print("error: PyYAML required (python3 -m pip install pyyaml)", file=sys.stderr)
    sys.exit(2)

ROOT = Path(__file__).resolve().parent.parent
REGISTRY = ROOT / "schema" / "extension-registry.yaml"

VALID_VALUE_TYPES = {"string", "number", "boolean"}
VALID_APPLIES_TO = {"entity", "connection", "source"}
VALID_STATUSES = {"proposed", "adopted"}


def load_registry() -> dict[str, Any]:
    if not REGISTRY.exists():
        raise FileNotFoundError(f"registry not found: {REGISTRY}")
    data = yaml.safe_load(REGISTRY.read_text(encoding="utf-8")) or {}
    return data


def get_dimension(extensions: list[dict], name: str) -> dict | None:
    for e in extensions:
        if e.get("name") == name:
            return e
    return None


def add(args: argparse.Namespace) -> int:
    registry = load_registry()
    extensions = registry.setdefault("extensions", [])

    if args.value_type not in VALID_VALUE_TYPES:
        print(f"error: value_type must be one of {sorted(VALID_VALUE_TYPES)}", file=sys.stderr)
        return 1
    for target in args.applies_to:
        if target not in VALID_APPLIES_TO:
            print(f"error: applies_to entries must be from {sorted(VALID_APPLIES_TO)}", file=sys.stderr)
            return 1

    existing = get_dimension(extensions, args.name)
    now = datetime.now(timezone.utc).isoformat(timespec="seconds")

    if existing is not None:
        if existing.get("status") == "adopted" and args.status == "proposed":
            print(f"error: '{args.name}' is adopted; refusing to downgrade to proposed", file=sys.stderr)
            return 1
        # Idempotent re-registration: update metadata but do not duplicate.
        existing["applies_to"] = sorted(set(args.applies_to))
        existing["value_type"] = args.value_type
        if args.enum is not None:
            existing["enum"] = args.enum
        if args.description:
            existing["description"] = args.description
        existing["status"] = args.status
        existing["registered_by"] = args.registered_by or existing.get("registered_by")
        existing["registered_at"] = now
        print(f"updated existing dimension: {args.name}")
    else:
        entry: dict[str, Any] = {
            "name": args.name,
            "applies_to": sorted(set(args.applies_to)),
            "value_type": args.value_type,
            "enum": args.enum,
            "description": args.description or "",
            "status": args.status,
            "registered_by": args.registered_by or "process:manual",
            "registered_at": now,
        }
        extensions.append(entry)
        print(f"registered new dimension: {args.name}")

    # Stable serialization
    registry["extensions"] = sorted(extensions, key=lambda e: str(e.get("name", "")))
    _write(registry)
    print(f"registry updated: {REGISTRY.relative_to(ROOT)}")
    return 0


def _write(registry: dict) -> None:
    """Serialize, preserving the human header comment above the `extensions:` key."""
    header = _read_header()
    body = yaml.safe_dump(registry, sort_keys=False, allow_unicode=True, default_flow_style=False)
    REGISTRY.write_text(header + body, encoding="utf-8")


def _read_header() -> str:
    """Preserve only the human comment lines above the first data key.

    `version:` and `extensions:` are data keys serialized by yaml.safe_dump in
    _write(); keeping them in the header as well caused the `version:` key to
    accumulate on every re-registration (duplicate-key bug, Q1.2). Stop at the
    first top-level mapping key (version/extensions) and return only the leading
    comment block — the body re-emits the single authoritative `version:`.
    """
    text = REGISTRY.read_text(encoding="utf-8")
    lines = text.splitlines()
    out = []
    for ln in lines:
        stripped = ln.strip()
        if not stripped:
            # keep blank lines that separate the comment block
            if out:
                out.append(ln)
            continue
        if stripped.startswith("#"):
            out.append(ln)
            continue
        # First non-comment, non-blank line is a data key — stop.
        break
    return "\n".join(out).rstrip() + "\n\n"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)

    p_add = sub.add_parser("add", help="register a new extension dimension")
    p_add.add_argument("--name", required=True)
    p_add.add_argument("--applies-to", nargs="+", required=True)
    p_add.add_argument("--value-type", required=True, choices=sorted(VALID_VALUE_TYPES))
    p_add.add_argument("--enum", default=None, help="comma-separated controlled values")
    p_add.add_argument("--description", default="")
    p_add.add_argument("--registered-by", default="process:manual")
    p_add.add_argument("--status", default="proposed", choices=sorted(VALID_STATUSES))
    p_add.set_defaults(func=add)

    args = parser.parse_args(argv)
    if args.enum is not None:
        args.enum = [v.strip() for v in args.enum.split(",") if v.strip()]
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())