#!/usr/bin/env python3
"""Source Update / Drift Detection for STEMMA.

Monitors sources for changes and identifies affected canonical objects.
"""
from __future__ import annotations

import hashlib
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import yaml

ROOT = Path(__file__).resolve().parent.parent
SOURCES_DIR = ROOT / "sources"
EXPORT = ROOT / "exports" / "knowledge.json"
STATE_FILE = ROOT / "indexes" / "source_state.yaml"


def load_sources() -> dict[str, dict]:
    """Load all source records."""
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


def load_state() -> dict:
    if not STATE_FILE.exists():
        return {"sources": {}, "last_check": None}
    return yaml.safe_load(STATE_FILE.read_text()) or {"sources": {}, "last_check": None}


def save_state(state: dict) -> None:
    state["last_check"] = datetime.now(timezone.utc).isoformat()
    STATE_FILE.parent.mkdir(parents=True, exist_ok=True)
    STATE_FILE.write_text(yaml.safe_dump(state, sort_keys=False, allow_unicode=True))


def compute_source_hash(source: dict) -> str:
    """Compute content hash for source record."""
    # Hash key fields that indicate content changes
    content = {
        "citation": source.get("citation"),
        "title": source.get("title"),
        "year": source.get("year"),
        "publication_date": source.get("publication_date"),
        "url": source.get("url"),
        "doi": source.get("doi"),
        "checksum": source.get("checksum"),
        "lifecycle": source.get("lifecycle"),
    }
    return hashlib.sha256(json.dumps(content, sort_keys=True).encode()).hexdigest()


def find_affected_objects(source_id: str, export: dict) -> dict:
    """Find canonical objects that depend on this source."""
    affected = {
        "connections": [],
        "entities": [],
    }
    
    # Check connections for evidence referencing this source
    for conn in export.get("connections", []):
        for ev in conn.get("evidence", []):
            if ev.get("source_ref") == source_id:
                affected["connections"].append({
                    "id": conn["id"],
                    "relation": conn["relation"],
                    "source": conn["source"],
                    "target": conn["target"],
                })
                break
    
    # Check entities for provenance referencing this source
    for entity in export.get("entities", []):
        prov = entity.get("provenance", {})
        if prov.get("source") == source_id or prov.get("source_ref") == source_id:
            affected["entities"].append({
                "id": entity["id"],
                "name": entity.get("name"),
                "type": entity.get("type"),
            })
    
    return affected


def main() -> int:
    sources = load_sources()
    export = load_export()
    state = load_state()
    
    print(f"Checking {len(sources)} sources for updates...")
    
    changes = {
        "new_sources": [],
        "modified_sources": [],
        "removed_sources": [],
        "lifecycle_changes": [],
        "checksum_changes": [],
        "affected_objects": {},
    }
    
    current_hashes = {}
    
    for sid, source in sources.items():
        current_hash = compute_source_hash(source)
        current_hashes[sid] = current_hash
        
        if sid not in state["sources"]:
            changes["new_sources"].append(sid)
            print(f"  NEW source: {sid}")
        else:
            old_hash = state["sources"][sid].get("content_hash")
            if old_hash and old_hash != current_hash:
                changes["modified_sources"].append(sid)
                print(f"  MODIFIED source: {sid}")
                changes["checksum_changes"].append(sid)
            
            # Check lifecycle changes
            old_lifecycle = state["sources"][sid].get("lifecycle")
            new_lifecycle = source.get("lifecycle", "active")
            if old_lifecycle and old_lifecycle != new_lifecycle:
                changes["lifecycle_changes"].append({
                    "source_id": sid,
                    "from": old_lifecycle,
                    "to": new_lifecycle,
                })
                print(f"  LIFECYCLE CHANGE: {sid} {old_lifecycle} -> {new_lifecycle}")
        
        # Find affected canonical objects
        affected = find_affected_objects(sid, export)
        if affected["connections"] or affected["entities"]:
            changes["affected_objects"][sid] = affected
            print(f"  {sid} affects {len(affected['connections'])} connections, {len(affected['entities'])} entities")
    
    # Check for removed sources
    for sid in state["sources"]:
        if sid not in sources:
            changes["removed_sources"].append(sid)
            print(f"  REMOVED source: {sid}")
    
    # Update state
    for sid, source in sources.items():
        state["sources"][sid] = {
            "content_hash": current_hashes[sid],
            "lifecycle": source.get("lifecycle", "active"),
            "last_seen": datetime.now(timezone.utc).isoformat(),
        }
    
    save_state(state)
    
    # Write change report
    report = {
        "checked_at": datetime.now(timezone.utc).isoformat(),
        "total_sources": len(sources),
        "changes": changes,
    }
    
    report_path = ROOT / "proposals" / f"source_drift_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.yaml"
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(yaml.safe_dump(report, sort_keys=False, allow_unicode=True))
    
    print(f"\nDrift report written to {report_path.relative_to(ROOT)}")
    print(f"Summary: {len(changes['new_sources'])} new, {len(changes['modified_sources'])} modified, {len(changes['removed_sources'])} removed, {len(changes['lifecycle_changes'])} lifecycle changes")
    
    if changes["affected_objects"]:
        print("\nAffected canonical objects:")
        for sid, affected in changes["affected_objects"].items():
            print(f"  {sid}: {len(affected['connections'])} connections, {len(affected['entities'])} entities")
            for c in affected["connections"][:3]:
                print(f"    - {c['id']}: {c['relation']} ({c['source']} -> {c['target']})")
            for e in affected["entities"][:3]:
                print(f"    - {e['id']}: {e['name']} ({e['type']})")
    
    return 0


if __name__ == "__main__":
    sys.exit(main())