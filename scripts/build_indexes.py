#!/usr/bin/env python3
"""Retrieval/Indexing Strategy for STEMMA.

Generates derived search indexes from canonical exports.
Indexes are NEVER the canonical source — they are regenerable artifacts.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

import yaml

ROOT = Path(__file__).resolve().parent.parent
EXPORT = ROOT / "exports" / "knowledge.json"
INDEX_DIR = ROOT / "indexes"

INDEX_DIR.mkdir(parents=True, exist_ok=True)


def load_export() -> dict:
    if not EXPORT.exists():
        print(f"Export not found: {EXPORT}", file=sys.stderr)
        sys.exit(1)
    return json.loads(EXPORT.read_text())


def build_lexical_index(entities: list[dict]) -> dict:
    """Build simple lexical index for BM25-style search."""
    index = {}
    for entity in entities:
        eid = entity["id"]
        name = entity.get("name", "").lower()
        definition = entity.get("definition", "").lower()
        domain = entity.get("domain", "").lower()
        etype = entity.get("type", "").lower()
        
        # Tokenize
        tokens = set()
        for text in [name, definition, domain, etype]:
            for token in text.split():
                # Simple tokenization
                clean = "".join(c for c in token if c.isalnum() or c in "-_")
                if len(clean) > 2:
                    tokens.add(clean)
        
        for token in tokens:
            index.setdefault(token, []).append(eid)
    
    return index


def build_structural_index(entities: list[dict], connections: list[dict]) -> dict:
    """Build structural navigation index."""
    # Entity by domain
    by_domain = {}
    for e in entities:
        by_domain.setdefault(e.get("domain", "unknown"), []).append(e["id"])
    
    # Entity by type
    by_type = {}
    for e in entities:
        by_type.setdefault(e.get("type", "unknown"), []).append(e["id"])
    
    # Entity by status
    by_status = {}
    for e in entities:
        by_status.setdefault(e.get("status", "unknown"), []).append(e["id"])
    
    # Connection adjacency
    outgoing = {}
    incoming = {}
    for c in connections:
        src = c["source"]
        tgt = c["target"]
        rel = c["relation"]
        outgoing.setdefault(src, []).append({"relation": rel, "target": tgt, "id": c["id"]})
        incoming.setdefault(tgt, []).append({"relation": rel, "source": src, "id": c["id"]})
    
    return {
        "by_domain": by_domain,
        "by_type": by_type,
        "by_status": by_status,
        "outgoing": outgoing,
        "incoming": incoming,
    }


def build_citation_index(sources: list[dict], connections: list[dict]) -> dict:
    """Build citation/source index."""
    # Source metadata lookup
    source_by_id = {s["id"]: s for s in sources}
    
    # Evidence -> source mapping
    evidence_to_source = {}
    for c in connections:
        for ev in c.get("evidence", []):
            src_ref = ev.get("source_ref")
            if src_ref:
                evidence_to_source.setdefault(src_ref, []).append({
                    "connection_id": c["id"],
                    "stance": ev.get("stance"),
                    "type": ev.get("type"),
                })
    
    return {
        "source_metadata": source_by_id,
        "evidence_to_source": evidence_to_source,
    }


def build_semantic_index(entities: list[dict]) -> dict:
    """Build semantic index placeholder for embeddings."""
    # This is a placeholder for future embedding-based search
    # In practice, you'd compute embeddings here and store them
    return {
        "note": "Semantic index requires embedding model. Run embedding generation separately.",
        "entities": {e["id"]: {"name": e.get("name"), "domain": e.get("domain")} for e in entities},
    }


def main() -> int:
    data = load_export()
    entities = data.get("entities", [])
    connections = data.get("connections", [])
    sources = data.get("sources", [])
    
    print(f"Building indexes for {len(entities)} entities, {len(connections)} connections, {len(sources)} sources")
    
    # Build indexes
    lexical = build_lexical_index(entities)
    structural = build_structural_index(entities, connections)
    citation = build_citation_index(sources, connections)
    semantic = build_semantic_index(entities)
    
    # Write indexes
    (INDEX_DIR / "lexical_index.json").write_text(json.dumps(lexical, indent=2))
    print(f"  lexical_index.json: {len(lexical)} tokens")
    
    (INDEX_DIR / "structural_index.json").write_text(json.dumps(structural, indent=2))
    print(f"  structural_index.json: {len(structural['by_domain'])} domains, {len(structural['by_type'])} types")
    
    (INDEX_DIR / "citation_index.json").write_text(json.dumps(citation, indent=2))
    print(f"  citation_index.json: {len(citation['source_metadata'])} sources")
    
    (INDEX_DIR / "semantic_index.json").write_text(json.dumps(semantic, indent=2))
    print(f"  semantic_index.json: placeholder")
    
    # Master index manifest
    manifest = {
        "generated_at": __import__("datetime").datetime.now(__import__("datetime").timezone.utc).isoformat(),
        "source_export_hash": __import__("hashlib").sha256(EXPORT.read_bytes()).hexdigest()[:16],
        "indexes": {
            "lexical_index.json": {"type": "lexical", "token_count": len(lexical)},
            "structural_index.json": {"type": "structural", "domains": len(structural["by_domain"])},
            "citation_index.json": {"type": "citation", "sources": len(citation["source_metadata"])},
            "semantic_index.json": {"type": "semantic", "status": "placeholder"},
        },
    }
    (INDEX_DIR / "index_manifest.yaml").write_text(yaml.safe_dump(manifest, sort_keys=False))
    print(f"  index_manifest.yaml: written")
    
    print(f"\nAll indexes written to {INDEX_DIR.relative_to(ROOT)}")
    print("Remember: Indexes are DERIVED artifacts — regenerate from canonical export.")
    return 0


if __name__ == "__main__":
    sys.exit(main())