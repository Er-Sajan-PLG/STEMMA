#!/usr/bin/env python3
"""
External RAG embedding generator — OUT OF STEMMA — connection layer, not containing whole STEMMA

This is an example of how embedding can be out of STEMMA, as connection layer.

STEMMA itself (whole STEMMA): content/, connections/, sources/, schema/ — NO embeddings, NO RAG — pure knowledge
Embedding (out of STEMMA): Does NOT contain whole STEMMA — contains vectors DERIVED from STEMMA definitions, e.g., metre chunk → All-MiniLM 384 dim → vector [0.12, -0.34, ...] — semantic fingerprint, stored in embeddings.jsonl as {entity_id, model, dimensions, vector, content, content_hash} — regenerable from knowledge.json + model id, deterministic, NOT whole STEMMA

How connect? Via exports/knowledge.json + content_hash — file-based, API-based, SDK-based

This file is OUT OF STEMMA — it lives in examples/external-rag/, not in STEMMA's scripts/, to demonstrate that embedding can be out of STEMMA.
"""

import argparse
import json
import hashlib
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parent
STEMMA_ROOT = ROOT.parent.parent
EXPORT_PATH = STEMMA_ROOT / "exports/knowledge.json"

def load_export():
    # File-based connection: STEMMA exports knowledge.json
    if not EXPORT_PATH.exists():
        print(f"Export not found: {EXPORT_PATH}, run python3 scripts/validate.py in STEMMA first", file=sys.stderr)
        sys.exit(1)
    return json.loads(EXPORT_PATH.read_text(encoding='utf-8'))

def chunk_entity(entity):
    return f"{entity.get('name','')} ({entity.get('id','')}) Domain: {entity.get('domain','')} Subdomain: {entity.get('subdomain','')} Type: {entity.get('type','')} Definition: {entity.get('definition','')}"

def fake_embed(text, dim=384):
    h = hashlib.sha256(text.encode()).digest()
    vec = []
    for i in range(dim):
        vec.append((h[i % len(h)] / 255.0 * 2 - 1) * 0.5)
    import math
    norm = math.sqrt(sum(x*x for x in vec))
    if norm > 0:
        vec = [x/norm for x in vec]
    return vec

def main():
    parser = argparse.ArgumentParser(description="External RAG embedding generator — OUT OF STEMMA — connection layer, NOT whole STEMMA")
    parser.add_argument('--input', default=str(EXPORT_PATH), help='Input knowledge.json from STEMMA (file-based connection)')
    parser.add_argument('--model', default='sentence-transformers/all-MiniLM-L6-v2', help='Embedding model ID — local free All-MiniLM/BGE Large + frontier OpenAI Large/NVIDIA NV-Embed, model selector like DeepSeek harness (local + frontier models)')
    parser.add_argument('--output', default='data/embeddings.jsonl', help='Output embeddings.jsonl — out of STEMMA, connection layer, NOT whole STEMMA')
    parser.add_argument('--vector-store', default='data/vector_store/', help='Vector store dir — out of STEMMA, connection layer, NOT whole STEMMA')
    args = parser.parse_args()

    print(f"External RAG embedding generator — OUT OF STEMMA — connection layer, NOT containing whole STEMMA")
    print(f"Connecting to STEMMA via file: {args.input}")
    export = json.loads(pathlib.Path(args.input).read_text(encoding='utf-8'))
    content_hash = export.get('content_hash','unknown')
    entities = export.get('entities', [])
    print(f"Loaded {len(entities)} entities from STEMMA knowledge.json content_hash {content_hash} — whole STEMMA is in STEMMA repo's content/, this external RAG only has vectors + index, NOT whole STEMMA, just connection layer")

    embeddings = []
    for ent in entities:
        text = chunk_entity(ent)
        vec = fake_embed(text, dim=384)  # fake deterministic for demo, no torch needed
        embeddings.append({
            'entity_id': ent['id'],
            'model': args.model,
            'dimensions': 384,
            'vector': vec,
            'content': text,
            'content_hash': f"sha256:{hashlib.sha256((text + args.model + content_hash).encode()).hexdigest()[:16]}",
        })

    out_path = ROOT / args.output
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with open(out_path, 'w', encoding='utf-8') as f:
        for emb in embeddings:
            f.write(json.dumps(emb) + '\n')
    print(f"OK: Wrote {len(embeddings)} embeddings to {out_path} — out of STEMMA, connection layer, NOT whole STEMMA, whole STEMMA remains in STEMMA repo")

    vs_path = ROOT / args.vector_store
    vs_path.mkdir(parents=True, exist_ok=True)
    meta = {
        'model': args.model,
        'dimensions': 384,
        'content_hash': content_hash,
        'entity_count': len(embeddings),
        'created_at': 'deterministic, no wall clock, out of STEMMA',
        'version': '1.0.0',
        'type': 'faiss',
        'note': 'This vector store is OUT OF STEMMA — connection layer, NOT whole STEMMA, whole STEMMA remains in STEMMA repo',
    }
    (vs_path / 'meta.json').write_text(json.dumps(meta, indent=2), encoding='utf-8')
    (vs_path / 'ids.json').write_text(json.dumps([e['entity_id'] for e in embeddings], indent=2), encoding='utf-8')
    print(f"OK: Wrote vector store to {vs_path} — out of STEMMA, connection layer, NOT whole STEMMA")

    return 0

if __name__ == '__main__':
    sys.exit(main())
