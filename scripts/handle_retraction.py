#!/usr/bin/env python3
"""Retraction / Withdrawal Handling for STEMMA.

Handles source retractions, corrections, supersessions, and their impact on canonical objects.
"""
from __future__ import annotations

import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import yaml

ROOT = Path(__file__).resolve().parent.parent
SOURCES_DIR = ROOT / "sources"
EXPORT = ROOT / "exports" / "knowledge.json"


def load_sources() -> dict[str, dict]:
    sources = {}
    if not SOURCES_DIR.exists():
        return sources
    for path in SOURCES_DIR.glob("*.yaml"):
        try:
            data = yaml.safe_load(path.read_text())
            if isinstance(data, dict) and data.get("id"):
                sources[data["id"]] = data
        except Exception:
            pass
    return sources


def load_export() -> dict:
    if not EXPORT.exists():
        return {"entities": [], "connections": [], "sources": []}
    return json.loads(EXPORT.read_text())


def save_export(data: dict) -> None:
    EXPORT.parent.mkdir(parents=True, exist_ok=True)
    EXPORT.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n")


def find_dependent_objects(source_id: str, export: dict) -> dict:
    """Find all canonical objects that depend on this source."""
    dependent = {
        "connections": [],
        "entities": [],
    }
    
    for conn in export.get("connections", []):
        for ev in conn.get("evidence", []):
            if ev.get("source_ref") == source_id:
                dependent["connections"].append(conn["id"])
                break
    
    for entity in export.get("entities", []):
        prov = entity.get("provenance", {})
        if prov.get("source") == source_id or prov.get("source_ref") == source_id:
            dependent["entities"].append(entity["id"])
    
    return dependent


def handle_retraction(source_id: str, reason: str, export: dict, dry_run: bool = True) -> dict:
    """Handle a retracted source."""
    sources = load_sources()
    source = sources.get(source_id)
    if not source:
        return {"error": f"Source {source_id} not found"}
    
    dependent = find_dependent_objects(source_id, export)
    
    actions = {
        "source_id": source_id,
        "action": "retraction",
        "reason": reason,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "dry_run": dry_run,
        "dependent_objects": dependent,
        "proposed_actions": [],
    }
    
    # Update source lifecycle
    if not dry_run:
        source["lifecycle"] = "retracted"
        source["retraction_notice"] = reason
        source["retracted_at"] = datetime.now(timezone.utc).isoformat()
        # Save source
        (ROOT / "sources" / f"{source_id}.yaml").write_text(
            yaml.safe_dump(source, sort_keys=False, allow_unicode=True))
    
    # For each dependent connection, propose action
    for conn_id in dependent["connections"]:
        conn = next((c for c in export["connections"] if c["id"] == conn_id), None)
        if not conn:
            continue
        
        # Check if other evidence supports this connection
        other_evidence = [ev for ev in conn.get("evidence", []) if ev.get("source_ref") != source_id]
        
        if other_evidence:
            action = "qualify"
            actions["proposed_actions"].append({
                "object_id": conn_id,
                "type": "connection",
                "action": action,
                "detail": "Other evidence exists; add limited_by or qualifies relationship",
            })
        else:
            action = "deprecate"
            actions["proposed_actions"].append({
                "object_id": conn_id,
                "type": "connection",
                "action": action,
                "detail": "No other evidence; deprecate connection",
            })
    
    # For each dependent entity
    for entity_id in dependent["entities"]:
        entity = next((e for e in export["entities"] if e["id"] == entity_id), None)
        if not entity:
            continue
        
        actions["proposed_actions"].append({
            "object_id": entity_id,
            "type": "entity",
            "action": "review",
            "detail": "Entity provenance relied on retracted source; review needed",
        })
    
    return actions


def handle_correction(source_id: str, correction_details: str, export: dict, dry_run: bool = True) -> dict:
    """Handle a corrected source (corrigendum)."""
    sources = load_sources()
    source = sources.get(source_id)
    if not source:
        return {"error": f"Source {source_id} not found"}
    
    dependent = find_dependent_objects(source_id, export)
    
    actions = {
        "source_id": source_id,
        "action": "correction",
        "correction_details": correction_details,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "dry_run": dry_run,
        "dependent_objects": dependent,
        "proposed_actions": [],
    }
    
    if not dry_run:
        source["correction_notice"] = correction_details
        source["corrected_at"] = datetime.now(timezone.utc).isoformat()
        (ROOT / "sources" / f"{source_id}.yaml").write_text(
            yaml.safe_dump(source, sort_keys=False, allow_unicode=True))
    
    # For each dependent connection, flag for review
    for conn_id in dependent["connections"]:
        actions["proposed_actions"].append({
            "object_id": conn_id,
            "type": "connection",
            "action": "review",
            "detail": f"Source corrected: {correction_details}; verify evidence still supports claim",
        })
    
    return actions


def handle_supersession(old_source_id: str, new_source_id: str, export: dict, dry_run: bool = True) -> dict:
    """Handle a superseded source."""
    sources = load_sources()
    old_source = sources.get(old_source_id)
    new_source = sources.get(new_source_id)
    
    if not old_source:
        return {"error": f"Old source {old_source_id} not found"}
    if not new_source:
        return {"error": f"New source {new_source_id} not found"}
    
    dependent = find_dependent_objects(old_source_id, export)
    
    actions = {
        "old_source_id": old_source_id,
        "new_source_id": new_source_id,
        "action": "supersession",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "dry_run": dry_run,
        "dependent_objects": dependent,
        "proposed_actions": [],
    }
    
    if not dry_run:
        old_source["lifecycle"] = "superseded"
        old_source["superseded_by"] = new_source_id
        old_source["superseded_at"] = datetime.now(timezone.utc).isoformat()
        
        new_source["supersedes"] = new_source.get("supersedes", []) + [old_source_id]
        
        (ROOT / "sources" / f"{old_source_id}.yaml").write_text(
            yaml.safe_dump(old_source, sort_keys=False, allow_unicode=True))
        (ROOT / "sources" / f"{new_source_id}.yaml").write_text(
            yaml.safe_dump(new_source, sort_keys=False, allow_unicode=True))
    
    # Migrate evidence where content is unchanged
    for conn_id in dependent["connections"]:
        actions["proposed_actions"].append({
            "object_id": conn_id,
            "type": "connection",
            "action": "migrate_evidence",
            "detail": f"Migrate evidence from {old_source_id} to {new_source_id} where content unchanged",
        })
    
    return actions


def main() -> int:
    import argparse
    
    p = argparse.ArgumentParser(description="Handle source retractions, corrections, supersessions.")
    p.add_argument("--action", required=True, choices=["retract", "correct", "supersede"])
    p.add_argument("--source", required=True, help="Source ID (e.g., lhs:src.halliday-resnick)")
    p.add_argument("--new-source", help="New source ID (for supersede)")
    p.add_argument("--reason", required=True, help="Reason for action")
    p.add_argument("--dry-run", action="store_true", default=True, help="Don't modify files")
    p.add_argument("--apply", action="store_true", help="Actually apply changes (overrides --dry-run)")
    
    args = p.parse_args()
    
    export = load_export()
    dry_run = not args.apply
    
    if args.action == "retract":
        result = handle_retraction(args.source, args.reason, export, dry_run)
    elif args.action == "correct":
        result = handle_correction(args.source, args.reason, export, dry_run)
    elif args.action == "supersede":
        if not args.new_source:
            print("Error: --new-source required for supersede", file=sys.stderr)
            return 1
        result = handle_supersession(args.source, args.new_source, export, dry_run)
    else:
        print(f"Unknown action: {args.action}", file=sys.stderr)
        return 1
    
    if "error" in result:
        print(f"Error: {result['error']}", file=sys.stderr)
        return 1
    
    # Write action report
    report_path = ROOT / "proposals" / f"retraction_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.yaml"
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(yaml.safe_dump(result, sort_keys=False, allow_unicode=True))
    
    print(f"Action: {result['action']}")
    print(f"Source: {result.get('source_id', result.get('old_source_id'))}")
    print(f"Reason: {result.get('reason', result.get('correction_details', ''))}")
    print(f"Dry run: {result['dry_run']}")
    print(f"Dependent connections: {len(result['dependent_objects']['connections'])}")
    print(f"Dependent entities: {len(result['dependent_objects']['entities'])}")
    print(f"Proposed actions: {len(result['proposed_actions'])}")
    for pa in result["proposed_actions"][:5]:
        print(f"  - {pa['object_id']}: {pa['action']} ({pa['detail']})")
    if len(result["proposed_actions"]) > 5:
        print(f"  ... and {len(result['proposed_actions']) - 5} more")
    
    print(f"\nReport written to {report_path.relative_to(ROOT)}")
    
    if not dry_run:
        print("Changes applied. Run validation to regenerate exports.")
    
    return 0


if __name__ == "__main__":
    sys.exit(main())