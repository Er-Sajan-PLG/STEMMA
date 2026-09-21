#!/usr/bin/env python3
"""
External RAG system — OUT OF STEMMA — connection layer, NOT containing whole STEMMA

This is an example of how RAG can be out of STEMMA, as connection layer.

STEMMA itself (whole STEMMA): content/, connections/, sources/, schema/ — NO embeddings, NO RAG — pure knowledge
RAG (out of STEMMA): Does NOT contain whole STEMMA — contains retrieval logic + generation logic — grounded in STEMMA but doesn't contain whole STEMMA, only references entity IDs as context

How connect? Via exports/knowledge.json + API + SDK + content_hash — file-based, API-based, SDK-based

This file is OUT OF STEMMA — it lives in examples/external-rag/, not in STEMMA's scripts/, to demonstrate that RAG can be out of STEMMA.
"""

import argparse
import json
import hashlib
import pathlib
import sys
import math

ROOT = pathlib.Path(__file__).resolve().parent
STEMMA_ROOT = ROOT.parent.parent

def load_export():
    export_path = STEMMA_ROOT / "exports/knowledge.json"
    return json.loads(export_path.read_text(encoding='utf-8'))

def load_embeddings():
    emb_path = ROOT / "data/embeddings.jsonl"
    if not emb_path.exists():
        print(f"Embeddings not found: {emb_path}, run embed.py first (out of STEMMA)", file=sys.stderr)
        return []
    embeddings = []
    with open(emb_path, 'r', encoding='utf-8') as f:
        for line in f:
            embeddings.append(json.loads(line))
    return embeddings

def cosine_similarity(a, b):
    dot = sum(x*y for x,y in zip(a,b))
    norm_a = math.sqrt(sum(x*x for x in a))
    norm_b = math.sqrt(sum(y*y for y in b))
    if norm_a == 0 or norm_b == 0:
        return 0.0
    return dot / (norm_a * norm_b)

def fake_embed(text, dim=384):
    h = hashlib.sha256(text.encode()).digest()
    vec = []
    for i in range(dim):
        vec.append((h[i % len(h)] / 255.0 * 2 - 1) * 0.5)
    norm = math.sqrt(sum(x*x for x in vec))
    if norm > 0:
        vec = [x/norm for x in vec]
    return vec

def vector_search(query, top_k=5):
    embeddings = load_embeddings()
    if not embeddings:
        return []
    dim = embeddings[0].get('dimensions', 384)
    query_vec = fake_embed(query, dim)
    scored = []
    for emb in embeddings:
        score = cosine_similarity(query_vec, emb['vector'])
        scored.append((score, emb))
    scored.sort(key=lambda x: x[0], reverse=True)
    top = scored[:top_k]
    export = load_export()
    entity_map = {e['id']: e for e in export.get('entities', [])}
    results = []
    for score, emb in top:
        entity = entity_map.get(emb['entity_id'], {'id': emb['entity_id']})
        results.append({
            'entity': entity,
            'score': score,
            'content': emb.get('content',''),
            'entity_id': emb['entity_id'],
        })
    return results

def rag_query(question, top_k=5, model_id="deepseek/deepseek-r1:free"):
    print(f"External RAG query — OUT OF STEMMA — connection layer, NOT whole STEMMA")
    print(f"Question: '{question}' top_k={top_k} model={model_id}")
    print(f"Connecting to STEMMA via file: {STEMMA_ROOT / 'exports/knowledge.json'} + embeddings out of STEMMA: {ROOT / 'data/embeddings.jsonl'}")
    print(f"Whole STEMMA is in STEMMA repo's content/, this external RAG only has vectors + index + retrieval + LLM, NOT whole STEMMA, just connection layer")
    retrieved = vector_search(question, top_k=top_k)
    print(f"Retrieved {len(retrieved)} entities from STEMMA via vector search — connection layer")
    context = "\n".join([f"{r['entity'].get('name','')} ({r['entity_id']}) Domain: {r['entity'].get('domain','')} Definition: {r['entity'].get('definition','')[:200]} Score: {r['score']:.4f}" for r in retrieved])
    answer = f"""Based on STEMMA knowledge foundation (whole STEMMA is in STEMMA repo, this external RAG is out of STEMMA, connection layer, NOT whole STEMMA):

Context retrieved for question: "{question}":
{context[:1000]}

Answer (generated with model {model_id} out of STEMMA, with citations, grounded in STEMMA, but RAG system itself doesn't contain whole STEMMA, only references entity IDs as context):

[Demo RAG answer — in production, LLM {model_id} would generate answer with citations from retrieved entities]

Citations: {', '.join([r['entity_id'] for r in retrieved])} with source_refs and links from STEMMA

Note: This external RAG is OUT OF STEMMA — connection layer, NOT whole STEMMA, whole STEMMA remains in STEMMA repo's content/, connections/, sources/. This demonstrates that embedding and RAG can be out of STEMMA, they connect via exports/knowledge.json + API + SDK + content_hash, they don't contain whole STEMMA, they're just connection layer.
"""
    return {
        'question': question,
        'answer': answer,
        'citations': [{'entity_id': r['entity_id'], 'source_ref': r['entity'].get('source_refs',[''])[0] if r['entity'].get('source_refs') else '', 'link': r['entity'].get('provenance',{}).get('link','')} for r in retrieved],
        'retrieved_entities': retrieved,
        'model_used': model_id,
        'note': 'This external RAG is OUT OF STEMMA — connection layer, NOT whole STEMMA, whole STEMMA remains in STEMMA repo',
    }

def main():
    parser = argparse.ArgumentParser(description="External RAG — OUT OF STEMMA — connection layer, NOT whole STEMMA")
    parser.add_argument('--question', help='Question for RAG query — out of STEMMA')
    parser.add_argument('--search', help='Vector search query — out of STEMMA')
    parser.add_argument('--top-k', type=int, default=5)
    parser.add_argument('--model', default='deepseek/deepseek-r1:free', help='LLM model ID — model selector like DeepSeek harness (local + frontier models)')
    args = parser.parse_args()

    if args.search:
        results = vector_search(args.search, top_k=args.top_k)
        print(f"Search results for '{args.search}' out of STEMMA, connection layer, NOT whole STEMMA:")
        for res in results:
            print(f"- {res['entity_id']} score={res['score']:.4f} {res['entity'].get('name','')}")
        return 0

    if args.question:
        result = rag_query(args.question, top_k=args.top_k, model_id=args.model)
        print(json.dumps(result, indent=2))
        return 0

    parser.print_help()
    return 0

if __name__ == '__main__':
    sys.exit(main())
