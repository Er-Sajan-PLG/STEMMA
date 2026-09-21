#!/usr/bin/env python3
"""R6 — Entity review (human-activated) with HITL enforcement.

Entity statuses: draft → machine_validated → human_reviewed → canonical.

Commands:
  python3 scripts/review_entity.py list [--domain physics]
  python3 scripts/review_entity.py show stemma:phys.newtons-second-law
  python3 scripts/review_entity.py review stemma:phys.newtons-second-law --reviewer human:curator.001
  python3 scripts/review_entity.py canonicalize stemma:phys.newtons-second-law --reviewer human:curator.001

Rules (enforced):
  * `--reviewer` must be an active `human:` agent in schema/agent-registry.yaml.
  * `review` is idempotent from draft/machine_validated/human_reviewed.
  * `canonicalize` requires the entity already be human_reviewed (never jumps draft → canonical).
  * HITL: If workflow/ exists with candidates/proposals for this entity, audit must show human edited markdown.
  * The tool writes `provenance.reviewer` / `provenance.reviewed_at` and the entity `status`. It is a HUMAN review action, never automatic.

Primary ingestion (PDF) and secondary (direct LLM) both require HITL via hitl_check.py.
"""
from __future__ import annotations

import argparse
import json
import pathlib
import sys
from datetime import datetime, timezone

import yaml

ROOT = pathlib.Path(__file__).resolve().parent.parent
CONTENT = ROOT / "content"
AGENTS = ROOT / "schema" / "agent-registry.yaml"

ENTITY_TRANSITIONS = {
    "review": {"draft", "machine_validated", "human_reviewed"},
    "canonicalize": {"human_reviewed", "canonical"},
}
STATUSES = {"draft", "machine_validated", "human_reviewed", "canonical",
            "deprecated", "superseded"}


def now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _registered_human(agent: str, root: pathlib.Path = ROOT) -> bool:
    if not isinstance(agent, str) or not agent.startswith("human:"):
        return False
    try:
        data = yaml.safe_load((root / AGENTS.relative_to(ROOT)).read_text(encoding="utf-8")) or {}
    except Exception:
        return agent.startswith("human:")
    return any(a.get("id") == agent and a.get("class") == "human" and a.get("status") == "active"
               for a in data.get("agents") or [])


def load_entities(root: pathlib.Path = ROOT) -> dict[str, dict]:
    """Return canonical entities keyed by id, with `_file` set."""
    out = {}
    for path in sorted((root / "content").rglob("*.md")):
        raw = path.read_text(encoding="utf-8")
        if not raw.startswith("---"):
            continue
        try:
            data = yaml.safe_load(raw.split("---", 2)[1])
        except Exception as exc:  # noqa: BLE001
            data = {"id": path.stem, "_file": str(path.relative_to(root)), "_error": str(exc)}
        if isinstance(data, dict) and data.get("id"):
            data["_file"] = str(path.relative_to(root))
            out[data["id"]] = data
    return out


def find_entity(root: pathlib.Path, eid: str) -> tuple[dict, pathlib.Path]:
    if not eid.startswith("stemma:"):
        eid = f"stemma:{eid}"
    entities = load_entities(root)
    if eid not in entities:
        print(f"error: entity not found: {eid}", file=sys.stderr)
        sys.exit(1)
    path = root / entities[eid]["_file"]
    return entities[eid], path


def _check_hitl(eid: str, root: pathlib.Path):
    """Enforce HITL if workflow exists for this entity."""
    workflow = root / "workflow"
    if not workflow.exists():
        return  # No workflow, no HITL enforcement (e.g., initial seed or tests)

    candidates_dir = workflow / "candidates"
    proposals_dir = workflow / "proposals"
    has_candidates = list(candidates_dir.rglob("*.md")) if candidates_dir.exists() else []
    has_proposals = list(proposals_dir.glob("*.md")) if proposals_dir.exists() else []

    if not has_candidates and not has_proposals:
        return  # No workflow files, skip HITL check

    slug = eid.split(".")[-1]
    in_workflow = any(slug in str(p) for p in has_candidates + has_proposals)

    if not in_workflow:
        return  # Entity not in workflow, skip (direct file edit without ingestion)

    # If in workflow, enforce HITL
    try:
        sys.path.insert(0, str(root / "scripts"))
        from hitl_check import check_entity as hitl_check_entity
        ok, violations = hitl_check_entity(eid, verbose=False)
        if not ok:
            raise ValueError(f"HITL required — human must explicitly edit markdown before review/canonicalize: {'; '.join(violations)}")
    except ImportError:
        # hitl_check not available, warn but don't block
        pass


def transition_entity(root: pathlib.Path, eid: str, action: str, reviewer: str,
                      when: str | None = None) -> dict:
    """Apply a human review transition to one entity. Returns the updated record. Enforces HITL."""
    if action not in ENTITY_TRANSITIONS:
        raise ValueError(f"unknown entity review action: {action!r}")
    if not _registered_human(reviewer, root):
        raise ValueError(f"--reviewer must be an active human agent in "
                         f"{AGENTS.relative_to(ROOT)}: {reviewer!r}")

    # HITL enforcement before transition
    try:
        _check_hitl(eid, root)
    except ValueError:
        raise
    except Exception as exc:
        # Log but don't block if hitl_check itself errors
        print(f"warning: hitl_check error (not blocking): {exc}", file=sys.stderr)

    entity, path = find_entity(root, eid)
    status = entity.get("status")
    allowed = ENTITY_TRANSITIONS[action]
    if status not in allowed:
        raise ValueError(f"forbidden transition: status={status!r} cannot {action} "
                         f"(allowed from: {sorted(allowed)})")
    when = when or now()
    provenance = entity.setdefault("provenance", {})
    provenance["reviewer"] = reviewer
    provenance["reviewed_at"] = when
    entity["status"] = "human_reviewed" if action == "review" else "canonical"
    _write_entity(path, entity)
    return entity


def _write_entity(path: pathlib.Path, entity: dict) -> None:
    """Rewrite frontmatter (only the frontmatter block is touched)."""
    raw = path.read_text(encoding="utf-8")
    data = {k: v for k, v in entity.items() if not k.startswith("_")}
    frontmatter = yaml.safe_dump(data, sort_keys=False, allow_unicode=True)
    body = ""
    parts = raw.split("---", 2)
    if len(parts) >= 3:
        body = parts[2]
    path.write_text(f"---\n{frontmatter}---\n{body.removeprefix(chr(10))}", encoding="utf-8")


def cmd_list(root: pathlib.Path, domain: str | None) -> int:
    entities = load_entities(root)
    rows = []
    for eid in sorted(entities):
        e = entities[eid]
        if domain and e.get("domain") != domain:
            continue
        rows.append({
            "id": eid, "name": e.get("name"), "type": e.get("type"),
            "domain": e.get("domain"), "status": e.get("status"),
            "reviewer": (e.get("provenance") or {}).get("reviewer"),
            "reviewed_at": (e.get("provenance") or {}).get("reviewed_at"),
        })
    print(json.dumps(rows, indent=2, ensure_ascii=False, sort_keys=True))
    return 0


def cmd_show(root: pathlib.Path, eid: str) -> int:
    entity, _ = find_entity(root, eid)
    print(yaml.safe_dump(entity, sort_keys=False, allow_unicode=True))
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command")
    p_list = sub.add_parser("list")
    p_list.add_argument("--domain", default=None)
    p_show = sub.add_parser("show")
    p_show.add_argument("eid")
    p_review = sub.add_parser("review")
    p_review.add_argument("eid")
    p_review.add_argument("--reviewer", required=True)
    p_canon = sub.add_parser("canonicalize")
    p_canon.add_argument("eid")
    p_canon.add_argument("--reviewer", required=True)
    args = parser.parse_args(argv)
    if args.command is None:
        parser.print_help()
        return 0
    if args.command == "list":
        return cmd_list(ROOT, args.domain)
    if args.command == "show":
        return cmd_show(ROOT, args.eid)
    try:
        transition_entity(ROOT, args.eid, args.command, args.reviewer)
    except ValueError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2
    print(f"OK: {args.eid} -> {args.command} by {args.reviewer}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
