#!/usr/bin/env python3
"""Deterministic subset exports for STEMMA.

Generates focused exports for specific domains, subdomains, entity types,
or relationship types. Useful for consumers that only need a subset.
"""
import json
import pathlib
import sys
from datetime import datetime, timezone

ROOT = pathlib.Path(__file__).resolve().parent.parent
EXPORT_BASE = ROOT / "exports" / "knowledge.json"


def load_base() -> dict:
    if not EXPORT_BASE.exists():
        print(f"Error: base export not found at {EXPORT_BASE}", file=sys.stderr)
        sys.exit(1)
    return json.loads(EXPORT_BASE.read_text())


def write_export(name: str, payload: dict) -> None:
    path = ROOT / f"exports/knowledge.{name}.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n")
    print(f"OK: {name} -> {payload['entity_count']} entities, {payload['connection_count']} connections -> {path.relative_to(ROOT)}")


def filter_by_domain(base: dict, domain: str) -> dict:
    entities = [e for e in base["entities"] if e["domain"] == domain]
    entity_ids = {e["id"] for e in entities}
    connections = [
        c for c in base.get("connections", [])
        if c["source"] in entity_ids and c["target"] in entity_ids
    ]
    return {
        "export_version": base["export_version"],
        "schema_version": base["schema_version"],
        "policy": f"domain:{domain}",
        "generated_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "source": base["source"],
        "entity_count": len(entities),
        "connection_count": len(connections),
        "entities": entities,
        "connections": connections,
    }


def filter_by_type(base: dict, entity_type: str) -> dict:
    entities = [e for e in base["entities"] if e["type"] == entity_type]
    entity_ids = {e["id"] for e in entities}
    connections = [
        c for c in base.get("connections", [])
        if c["source"] in entity_ids and c["target"] in entity_ids
    ]
    return {
        "export_version": base["export_version"],
        "schema_version": base["schema_version"],
        "policy": f"type:{entity_type}",
        "generated_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "source": base["source"],
        "entity_count": len(entities),
        "connection_count": len(connections),
        "entities": entities,
        "connections": connections,
    }


def filter_by_status(base: dict, status: str) -> dict:
    entities = [e for e in base["entities"] if e["status"] == status]
    entity_ids = {e["id"] for e in entities}
    connections = [
        c for c in base.get("connections", [])
        if c["source"] in entity_ids and c["target"] in entity_ids
    ]
    return {
        "export_version": base["export_version"],
        "schema_version": base["schema_version"],
        "policy": f"status:{status}",
        "generated_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "source": base["source"],
        "entity_count": len(entities),
        "connection_count": len(connections),
        "entities": entities,
        "connections": connections,
    }


def filter_entities_only(base: dict) -> dict:
    """Export without connections - for lightweight consumers."""
    return {
        "export_version": base["export_version"],
        "schema_version": base["schema_version"],
        "policy": "entities-only",
        "generated_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "source": base["source"],
        "entity_count": len(base["entities"]),
        "connection_count": 0,
        "entities": base["entities"],
        "connections": [],
    }


def filter_connections_only(base: dict) -> dict:
    """Export only connections (requires entities to resolve)."""
    # Include minimal entity stubs for resolution
    entity_ids = set()
    for c in base.get("connections", []):
        entity_ids.add(c["source"])
        entity_ids.add(c["target"])
    entities = [e for e in base["entities"] if e["id"] in entity_ids]
    return {
        "export_version": base["export_version"],
        "schema_version": base["schema_version"],
        "policy": "connections-only",
        "generated_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "source": base["source"],
        "entity_count": len(entities),
        "connection_count": len(base.get("connections", [])),
        "entities": entities,
        "connections": base.get("connections", []),
    }


def filter_ai_rag(base: dict) -> dict:
    """AI/RAG-oriented export: entities with definitions, relationships as adjacency."""
    # Create adjacency map for fast traversal
    adj = {}
    for c in base.get("connections", []):
        adj.setdefault(c["source"], []).append({
            "relation": c["relation"],
            "target": c["target"],
            "confidence": c.get("assertion", {}).get("confidence"),
            "context": c.get("context", {}),
        })

    entities = []
    for e in base["entities"]:
        entities.append({
            "id": e["id"],
            "type": e["type"],
            "name": e["name"],
            "domain": e["domain"],
            "status": e["status"],
            "definition": e["definition"],
            "symbol": e.get("symbol"),
            "unit": e.get("unit"),
            "equation": e.get("equation"),
            "relationships": adj.get(e["id"], []),
            "provenance": e.get("provenance"),
        })

    return {
        "export_version": base["export_version"],
        "schema_version": base["schema_version"],
        "policy": "ai-rag",
        "generated_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "source": base["source"],
        "entity_count": len(entities),
        "connection_count": sum(len(v) for v in adj.values()),
        "entities": entities,
        "connections": [],  # relationships embedded in entities
    }


def filter_educational(base: dict) -> dict:
    """Simplified educational export: core concepts with key metadata."""
    # Include only canonical/reviewed entities
    entities = [e for e in base["entities"] if e["status"] in ("canonical", "human_reviewed")]
    entity_ids = {e["id"] for e in entities}
    connections = [
        c for c in base.get("connections", [])
        if c["source"] in entity_ids and c["target"] in entity_ids
        and c.get("assertion", {}).get("review", {}).get("status") in ("canonical", "reviewed")
    ]
    return {
        "export_version": base["export_version"],
        "schema_version": base["schema_version"],
        "policy": "educational",
        "generated_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "source": base["source"],
        "entity_count": len(entities),
        "connection_count": len(connections),
        "entities": entities,
        "connections": connections,
    }


def main():
    base = load_base()

    # Generate standard subset exports
    domains = set(e["domain"] for e in base["entities"])
    for domain in sorted(domains):
        write_export(f"domain-{domain}", filter_by_domain(base, domain))

    types = set(e["type"] for e in base["entities"])
    for t in sorted(types):
        write_export(f"type-{t}", filter_by_type(base, t))

    statuses = set(e["status"] for e in base["entities"])
    for s in sorted(statuses):
        write_export(f"status-{s}", filter_by_status(base, s))

    # Special purpose exports
    write_export("entities-only", filter_entities_only(base))
    write_export("connections-only", filter_connections_only(base))
    write_export("ai-rag", filter_ai_rag(base))
    write_export("educational", filter_educational(base))

    print(f"\nGenerated {len(domains)} domain + {len(types)} type + {len(statuses)} status + 4 special exports")
    return 0


if __name__ == "__main__":
    sys.exit(main())