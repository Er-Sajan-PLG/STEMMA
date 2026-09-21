#!/usr/bin/env python3
"""
Export for consumers like LearningHub, PROFESSOR-J, general, stemma-explorer

Generates consumer-specific exports filtered by domains, review_policy, entity_types, etc.

Supports:
- LearningHub: canonical physics, chemistry, biology, mathematics, high-quality embeddings, REST API
- PROFESSOR-J: reviewed all domains mediocre coverage, offline SOTA embeddings, RAG, all endpoints
- General: all domains, all review policies, fast local embeddings
- Explorer: all entities for 3D graph

Also generates:
- knowledge.json (main deterministic export)
- embeddings.jsonl (via embed.py)
- vector_store/ (FAISS)
- openapi.yaml (API schema)

Usage:
  python3 scripts/export_consumers.py --consumer learninghub --format json
  python3 scripts/export_consumers.py --consumer professor-j --format json --review-policy reviewed
  python3 scripts/export_consumers.py --all
"""

import argparse
import json
import pathlib
import sys
from typing import Dict, Any, List

ROOT = pathlib.Path(__file__).resolve().parent.parent
EXPORT_PATH = ROOT / "exports/knowledge.json"
CONSUMER_REGISTRY_PATH = ROOT / "schema/consumer-registry.yaml"

try:
    import yaml
except ImportError:
    print("Missing pyyaml", file=sys.stderr)
    sys.exit(1)

def load_export():
    return json.loads(EXPORT_PATH.read_text(encoding='utf-8'))

def load_consumer_registry():
    if not CONSUMER_REGISTRY_PATH.exists():
        print(f"Consumer registry not found: {CONSUMER_REGISTRY_PATH}", file=sys.stderr)
        sys.exit(1)
    return yaml.safe_load(CONSUMER_REGISTRY_PATH.read_text(encoding='utf-8'))

def filter_entities(entities: List[Dict[str, Any]], consumer_cfg: Dict[str, Any], review_policy: str = None) -> List[Dict[str, Any]]:
    domains = consumer_cfg.get('domains', [])
    if domains == 'all':
        domains = None
    subdomains = consumer_cfg.get('subdomains', [])
    if subdomains == 'all':
        subdomains = None
    entity_types = consumer_cfg.get('entity_types', [])
    if entity_types == 'all':
        entity_types = None
    policy = review_policy or consumer_cfg.get('review_policy', 'all')

    filtered = entities
    if domains:
        filtered = [e for e in filtered if e.get('domain') in domains]
    if subdomains:
        filtered = [e for e in filtered if e.get('subdomain') in subdomains or e.get('domain') in domains]  # subdomain filter optional
    if entity_types:
        filtered = [e for e in filtered if e.get('type') in entity_types]
    # Review policy filtering
    if policy == 'canonical':
        filtered = [e for e in filtered if e.get('status') == 'canonical']
    elif policy == 'reviewed':
        filtered = [e for e in filtered if e.get('status') in ('human_reviewed','canonical')]
    elif policy == 'trusted':
        filtered = [e for e in filtered if e.get('status') in ('human_reviewed','canonical')]  # simplified
    # all = no filter
    return filtered

def export_for_consumer(consumer_id: str, fmt: str = 'json', review_policy: str = None):
    registry = load_consumer_registry()
    consumer_cfg = registry.get('consumers', {}).get(consumer_id)
    if not consumer_cfg:
        print(f"Consumer {consumer_id} not found", file=sys.stderr)
        sys.exit(1)

    export = load_export()
    entities = export.get('entities', [])
    connections = export.get('connections', [])
    sources = export.get('sources', [])

    filtered_entities = filter_entities(entities, consumer_cfg, review_policy)
    # Filter connections to only those where source and target are in filtered entities
    filtered_ids = set(e['id'] for e in filtered_entities)
    filtered_connections = [c for c in connections if c.get('source') in filtered_ids and c.get('target') in filtered_ids]
    # Filter sources to only those referenced by filtered entities
    referenced_source_refs = set()
    for e in filtered_entities:
        for ref in e.get('source_refs', []):
            referenced_source_refs.add(ref)
    for c in filtered_connections:
        for ev in c.get('evidence', []):
            if ev.get('source_ref'):
                referenced_source_refs.add(ev['source_ref'])
    filtered_sources = [s for s in sources if s.get('id') in referenced_source_refs]

    print(f"Consumer {consumer_id} ({consumer_cfg.get('label')}): {len(entities)} -> {len(filtered_entities)} entities, {len(connections)} -> {len(filtered_connections)} connections, {len(sources)} -> {len(filtered_sources)} sources")
    print(f"Domains: {consumer_cfg.get('domains')} Review policy: {review_policy or consumer_cfg.get('review_policy')} Formats: {consumer_cfg.get('export_formats')}")

    # Build export
    consumer_export = {
        'export_version': export.get('export_version'),
        'schema_version': export.get('schema_version'),
        'content_hash': export.get('content_hash'),
        'consumer': consumer_id,
        'consumer_label': consumer_cfg.get('label'),
        'review_policy': review_policy or consumer_cfg.get('review_policy'),
        'entity_count': len(filtered_entities),
        'connection_count': len(filtered_connections),
        'source_count': len(filtered_sources),
        'entities': filtered_entities,
        'connections': filtered_connections,
        'sources': filtered_sources,
        'embedding_model': consumer_cfg.get('embedding_model'),
        'api_access': consumer_cfg.get('api_access'),
        'rag': consumer_cfg.get('rag'),
    }

    # Write file
    out_dir = ROOT / f"exports/consumers/{consumer_id}"
    out_dir.mkdir(parents=True, exist_ok=True)

    if fmt == 'json':
        out_path = out_dir / f"knowledge.{consumer_id}.json"
        out_path.write_text(json.dumps(consumer_export, indent=2), encoding='utf-8')
        print(f"OK: Wrote {out_path} — {len(filtered_entities)} entities, content_hash {export.get('content_hash')}")
    elif fmt == 'jsonl':
        out_path = out_dir / f"knowledge.{consumer_id}.jsonl"
        with open(out_path, 'w', encoding='utf-8') as f:
            for e in filtered_entities:
                f.write(json.dumps(e) + '\n')
        print(f"OK: Wrote {out_path} — JSONL {len(filtered_entities)} entities")
    elif fmt == 'embeddings':
        # Generate embeddings for this consumer's entities
        import subprocess
        model = consumer_cfg.get('embedding_model', 'sentence-transformers/all-MiniLM-L6-v2')
        cmd = [sys.executable, str(ROOT / "scripts/embed.py"), '--model', model, '--for-consumer', consumer_id, '--output', str(out_dir / f"embeddings.{consumer_id}.jsonl")]
        print(f"Running: {' '.join(cmd)}")
        subprocess.run(cmd, check=False)
    elif fmt == 'vector_store':
        import subprocess
        model = consumer_cfg.get('embedding_model', 'sentence-transformers/all-MiniLM-L6-v2')
        cmd = [sys.executable, str(ROOT / "scripts/embed.py"), '--model', model, '--for-consumer', consumer_id, '--output', str(out_dir / f"embeddings.{consumer_id}.jsonl"), '--vector-store', str(out_dir / "vector_store")]
        print(f"Running: {' '.join(cmd)}")
        subprocess.run(cmd, check=False)
    else:
        print(f"Unknown format {fmt}", file=sys.stderr)
        sys.exit(1)

    return consumer_export

def main():
    parser = argparse.ArgumentParser(description="STEMMA export for consumers — LearningHub, PROFESSOR-J, etc.")
    parser.add_argument('--consumer', choices=['learninghub', 'professor-j', 'general', 'stemma-explorer'], help='Consumer ID')
    parser.add_argument('--format', default='json', choices=['json', 'jsonl', 'embeddings', 'vector_store'], help='Export format')
    parser.add_argument('--review-policy', choices=['all', 'canonical', 'reviewed', 'trusted'], help='Review policy override')
    parser.add_argument('--all', action='store_true', help='Export for all consumers')
    args = parser.parse_args()

    if args.all:
        for cid in ['learninghub', 'professor-j', 'general', 'stemma-explorer']:
            export_for_consumer(cid, fmt=args.format, review_policy=args.review_policy)
        return 0

    if not args.consumer:
        print("Need --consumer or --all", file=sys.stderr)
        parser.print_help()
        return 1

    export_for_consumer(args.consumer, fmt=args.format, review_policy=args.review_policy)
    return 0

if __name__ == '__main__':
    sys.exit(main())
