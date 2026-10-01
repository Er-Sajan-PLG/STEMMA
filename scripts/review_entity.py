#!/usr/bin/env python3
"""R6 — Entity review (human-activated) with HITL enforcement.

Promotion ladder (ADR-0057): draft -> machine_validated -> validator_validated
-> independently_validated -> board_approved -> canonical.

The validator is NOT the final canonicalizer: each `promote` call advances the
record by exactly ONE stage, and consecutive stages must be applied on separate
days (ENF-STEMMA-HITL-001). The CLI refuses to record a promotion that would
violate an enforcement rule — the rule lives in
spec/machine-readable/enforcement_rules.yaml, not in prose.

Commands:
  python3 scripts/review_entity.py list [--domain physics]
  python3 scripts/review_entity.py show stemma:phys.newtons-second-law
  python3 scripts/review_entity.py stage stemma:phys.metre --actor human:curator.001
      # advance exactly one stage (validator / independent_validator / board)
  python3 scripts/review_entity.py stage stemma:phys.metre --actor human:curator.001 --at 2026-10-05T10:00:00+00:00
  python3 scripts/review_entity.py clear-debt stemma:phys.metre --actor human:curator.001 --stage validator --evidence "..."
  python3 scripts/review_entity.py defer-debt stemma:phys.metre --until "a second reviewer exists" --before 2026-12-31
  # legacy aliases (kept working): review -> validator stage; canonicalize is REFUSED
  python3 scripts/review_entity.py review stemma:phys.metre --reviewer human:curator.001

Rules (enforced):
  * `--actor`/`--reviewer` must be an active `human:` agent in schema/agent-registry.yaml.
  * `promote`/`stage` advances ONE stage only; there is no direct jump to canonical.
  * Consecutive stages of one record must be >= 1 calendar day apart (ENF-STEMMA-HITL-001).
  * A record with outstanding revalidation debt cannot advance (ENF-STEMMA-HITL-002).
  * HITL: if workflow/ has candidates/proposals for this entity, audit must show a human edit.
"""
from __future__ import annotations

import argparse
import json
import pathlib
import sys
from datetime import date, datetime, timezone

import yaml

ROOT = pathlib.Path(__file__).resolve().parent.parent
CONTENT = ROOT / "content"
AGENTS = ROOT / "schema" / "agent-registry.yaml"
ENFORCEMENT = ROOT / "spec" / "machine-readable" / "enforcement_rules.yaml"

STAGE_ORDER = ("validator", "independent_validator", "board")
STAGE_STATUS = {
    "validator": "validator_validated",
    "independent_validator": "independently_validated",
    "board": "board_approved",
}
FINAL_AFTER = {"board": "canonical"}
STATUSES = {"draft", "machine_validated", "human_reviewed", "validator_validated",
            "independently_validated", "board_approved", "canonical",
            "deprecated", "superseded"}

# Legacy action -> stage mapping. `canonicalize` deliberately has no mapping:
# a single act may not set canonical (ENF-STEMMA-HITL-004).
ENTITY_TRANSITIONS = {
    "review": {"draft", "machine_validated", "human_reviewed"},
    "canonicalize": {"human_reviewed", "canonical"},
}


def _enforcement() -> dict:
    if not ENFORCEMENT.exists():
        raise ValueError(
            "enforcement registry missing — refusing to record a promotion "
            "(spec/machine-readable/enforcement_rules.yaml)")
    return yaml.safe_load(ENFORCEMENT.read_text(encoding="utf-8")) or {}


def _min_stage_gap() -> int:
    for rule in _enforcement().get("rules") or []:
        spec = rule.get("rule") if isinstance(rule, dict) else None
        if isinstance(spec, dict) and spec.get("kind") == "min_stage_gap":
            v = spec.get("min_days")
            if isinstance(v, int):
                return v
    return 1


def now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _registered_human(agent: str, root: pathlib.Path = ROOT) -> bool:
    if not isinstance(agent, str) or not agent.startswith("human:"):
        return False
    try:
        data = yaml.safe_load((root / AGENTS.relative_to(ROOT)).read_text(encoding="utf-8")) or {}
    except Exception:
        return False  # fail closed: an unreadable registry verifies nobody (H1)
    return any(a.get("id") == agent and a.get("class") == "human" and a.get("status") == "active"
               and a.get("type") != "institution"
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
    sys.path.insert(0, str(root / "scripts"))
    from hitl_check import check_entity as hitl_check_entity  # in-repo; ImportError blocks
    ok, violations = hitl_check_entity(eid, verbose=False)
    if not ok:
        raise ValueError(f"HITL required — human must explicitly edit markdown before review/canonicalize: {'; '.join(violations)}")


def _last_stage_entry(entity: dict) -> dict | None:
    """Most advanced promotion_history entry, or None."""
    prov = entity.get("provenance") or {}
    hist = [e for e in (prov.get("promotion_history") or []) if isinstance(e, dict)
            and e.get("stage") in STAGE_ORDER]
    if not hist:
        return None
    return max(hist, key=lambda e: STAGE_ORDER.index(e["stage"]))


def _next_stage(entity: dict) -> str:
    last = _last_stage_entry(entity)
    if last is None:
        return "validator"
    idx = STAGE_ORDER.index(last["stage"])
    if idx + 1 >= len(STAGE_ORDER):
        raise ValueError("record has already completed the board stage; it is canonical")
    return STAGE_ORDER[idx + 1]


def _parse_ts(value: str) -> datetime:
    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError as exc:
        raise ValueError(f"invalid --at timestamp {value!r} (need ISO8601)") from exc


def _enforce_time_gate(entity: dict, when: str) -> None:
    """ENF-STEMMA-HITL-001: consecutive stages must be >= min_gap days apart."""
    last = _last_stage_entry(entity)
    if last is None:
        return
    prev = _parse_ts(str(last.get("at"))).date()
    cur = _parse_ts(when).date()
    gap = (cur - prev).days
    min_gap = _min_stage_gap()
    if gap < min_gap:
        raise ValueError(
            f"TIME GATE (ENF-STEMMA-HITL-001): previous stage '{last['stage']}' was applied "
            f"{prev}, and this stage would land {cur} — only {gap} day(s) apart, minimum is "
            f"{min_gap}. The validator, independent validator and board must act on separate "
            f"days or the canonicalization is biased. The rule is data in "
            f"spec/machine-readable/enforcement_rules.yaml and cannot be bypassed here.")


def _enforce_debt(entity: dict) -> None:
    """ENF-STEMMA-HITL-002: outstanding debt blocks forward promotion."""
    debt = entity.get("revalidation_debt")
    if isinstance(debt, dict) and debt.get("status") == "outstanding":
        raise ValueError(
            f"DEBT BLOCKS PROMOTION (ENF-STEMMA-HITL-002): revalidation_debt.status is "
            f"'outstanding' — reason {debt.get('reason')!r}. Clear the debt "
            f"(clear-debt) or have the owner defer it (defer-debt) before promoting.")


def promote(root: pathlib.Path, eid: str, actor: str, when: str | None = None,
            stage: str | None = None) -> dict:
    """Advance ONE promotion stage. Records the act in promotion_history.

    Refuses: non-human actor, outstanding debt, same-day stage advance, and any
    attempt to skip a stage. The board stage also writes board_members; under the
    interim single-actor waiver the CLI records the waiver automatically so the
    act is legal AND visible."""
    if not _registered_human(actor, root):
        raise ValueError(f"--actor must be an active human agent in "
                         f"{AGENTS.relative_to(ROOT)}: {actor!r}")
    entity, path = find_entity(root, eid)

    try:
        _check_hitl(eid, root)
    except ValueError:
        raise
    except Exception as exc:
        raise ValueError(f"HITL check could not run ({exc!r}); refusing promotion") from exc

    _enforce_debt(entity)
    target = stage or _next_stage(entity)
    if target not in STAGE_ORDER:
        raise ValueError(f"unknown stage {target!r} (validator|independent_validator|board)")
    expected = _next_stage(entity)
    if target != expected:
        raise ValueError(
            f"stages must be applied in order: expected '{expected}', got '{target}' "
            f"(ENF-STEMMA-HITL-004: no stage skipping, no direct canonical)")
    when = when or now()
    _enforce_time_gate(entity, when)

    prov = entity.setdefault("provenance", {})
    entry: dict = {"stage": target, "actor": actor, "at": when}
    if target == "board":
        entry["board_members"] = [actor]
        entry["independence_waiver"] = {
            "sanctioned_by": "human:curator.001",
            "reason": ("interim single-actor state (ADR-0057 §1a): the sole owner holds all "
                       "three roles until a second registered human exists"),
            "sanctioned_at": str(date.today()),
            "retire_when": "a second active human agent with a validation role is registered",
        }
    history = prov.setdefault("promotion_history", [])
    history.append(entry)
    prov["reviewer"] = actor
    prov["reviewed_at"] = when
    entity["status"] = STAGE_STATUS[target]
    if target == "board":
        # canonical is the terminal state reachable from board_approved; record
        # it only when the caller explicitly finalizes (see `finalize`).
        pass
    _write_entity(path, entity)
    return entity


def clear_debt(root: pathlib.Path, eid: str, actor: str, stage: str, evidence: str) -> dict:
    """Clear revalidation debt, attributably (ENF-STEMMA-HITL-002)."""
    if not _registered_human(actor, root):
        raise ValueError(f"--actor must be an active human agent: {actor!r}")
    if stage not in STAGE_ORDER:
        raise ValueError(f"--stage must be one of {STAGE_ORDER}")
    entity, path = find_entity(root, eid)
    debt = entity.get("revalidation_debt")
    if not isinstance(debt, dict) or debt.get("status") != "outstanding":
        raise ValueError("no outstanding revalidation_debt to clear")
    debt["status"] = "cleared"
    debt["cleared_by"] = actor
    debt["cleared_stage"] = stage
    debt["cleared_at"] = now()
    debt["clearance_evidence"] = evidence
    _write_entity(path, entity)
    return entity


def defer_debt(root: pathlib.Path, eid: str, actor: str, until: str) -> dict:
    """Owner-sanctioned deferral of revalidation debt."""
    if not _registered_human(actor, root):
        raise ValueError(f"--actor must be an active human agent: {actor!r}")
    entity, path = find_entity(root, eid)
    debt = entity.get("revalidation_debt")
    if not isinstance(debt, dict) or debt.get("status") != "outstanding":
        raise ValueError("no outstanding revalidation_debt to defer")
    debt["status"] = "deferred"
    debt["deferred_by"] = actor
    debt["deferred_until"] = until
    _write_entity(path, entity)
    return entity


def transition_entity(root: pathlib.Path, eid: str, action: str, reviewer: str,
                      when: str | None = None) -> dict:
    """Legacy action shim. `review` maps to the validator stage; `canonicalize`
    is refused (ENF-STEMMA-HITL-004: the validator is not the final canonicalizer)."""
    if action == "canonicalize":
        raise ValueError(
            "canonicalize is no longer a single step — canonical is reached only after "
            "validator -> independent_validator -> board (ENF-STEMMA-HITL-004). Use "
            "`stage` to advance one stage at a time.")
    if action not in ENTITY_TRANSITIONS:
        raise ValueError(f"unknown entity review action: {action!r}")
    return promote(root, eid, reviewer, when, stage="validator")


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
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = parser.add_subparsers(dest="command")
    p_list = sub.add_parser("list")
    p_list.add_argument("--domain", default=None)
    p_show = sub.add_parser("show")
    p_show.add_argument("eid")

    p_stage = sub.add_parser("stage", help="advance exactly one promotion stage")
    p_stage.add_argument("eid")
    p_stage.add_argument("--actor", required=True)
    p_stage.add_argument("--at", default=None, help="ISO8601 timestamp of the act")
    p_stage.add_argument("--stage", default=None,
                         help="explicit stage (must equal the next expected stage)")

    p_clear = sub.add_parser("clear-debt", help="clear outstanding revalidation debt")
    p_clear.add_argument("eid")
    p_clear.add_argument("--actor", required=True)
    p_clear.add_argument("--stage", required=True, choices=list(STAGE_ORDER))
    p_clear.add_argument("--evidence", required=True)

    p_defer = sub.add_parser("defer-debt", help="owner-sanctioned debt deferral")
    p_defer.add_argument("eid")
    p_defer.add_argument("--actor", required=True)
    p_defer.add_argument("--until", required=True)

    # legacy aliases
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
        if args.command == "stage":
            promote(ROOT, args.eid, args.actor, args.at, args.stage)
            msg = f"{args.eid} -> stage {args.stage or 'next'}"
        elif args.command == "clear-debt":
            clear_debt(ROOT, args.eid, args.actor, args.stage, args.evidence)
            msg = f"{args.eid} debt cleared"
        elif args.command == "defer-debt":
            defer_debt(ROOT, args.eid, args.actor, args.until)
            msg = f"{args.eid} debt deferred"
        else:
            transition_entity(ROOT, args.eid, args.command, args.reviewer)
            msg = f"{args.eid} -> {args.command}"
    except ValueError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2
    print(f"OK: {msg}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
