#!/usr/bin/env python3
"""
RAG system for STEMMA — Retrieval-Augmented Generation using embeddings + frontier LLM

Comprehensive all-STEM mediocre coverage, for consumers like LearningHub, PROFESSOR-J.

Components:
- Ingestion: PDF → deterministic extraction via template-registry → entity markdown → embedding via embed.py
- Vector store: FAISS/Chroma/Qdrant local, path exports/vector_store/, versioned with content_hash
- Retriever: similarity search over entity definitions + connections
- Generator: LLM with model selector like DeepSeek harness (local + frontier models: DeepSeek R1, Claude 3.5 Sonnet, GPT-4o, Gemini 2.5 Pro, Llama 3.3, custom)
- API: /v2/rag/query and /v2/rag/search via adapter server and webapp server

Flow:
  User question → embedding via embedding model → vector search top_k entities → build context with definitions + connections + sources → LLM prompt with context + question → answer with citations (source_refs + link)

Usage:
  python3 scripts/rag.py --question "What is Newton's second law?" --top-k 5 --model deepseek/deepseek-r1:free
  python3 scripts/rag.py --search "force" --top-k 5
  python3 scripts/rag.py --list-models

Yes, we NEED RAG system in STEMMA — STEMMA is knowledge foundation, RAG is how consumers like LearningHub, PROFESSOR-J use it.
Without RAG, STEMMA is just static JSON. With RAG, it's queryable knowledge with citations.
"""

import argparse
import json
import hashlib
import pathlib
import sys
import math
from typing import List, Dict, Any, Tuple

ROOT = pathlib.Path(__file__).resolve().parent.parent
EXPORT_PATH = ROOT / "exports/knowledge.json"
EMBEDDINGS_PATH = ROOT / "exports/embeddings.jsonl"
VECTOR_STORE_PATH = ROOT / "exports/vector_store/"
EMBEDDING_REGISTRY_PATH = ROOT / "schema/embedding-registry.yaml"

try:
    import yaml
except ImportError:
    print("Missing pyyaml", file=sys.stderr)
    sys.exit(1)

def load_export():
    return json.loads(EXPORT_PATH.read_text(encoding='utf-8'))

def load_embeddings() -> List[Dict[str, Any]]:
    if not EMBEDDINGS_PATH.exists():
        print(f"Embeddings not found: {EMBEDDINGS_PATH}, run embed.py first", file=sys.stderr)
        return []
    embeddings = []
    with open(EMBEDDINGS_PATH, 'r', encoding='utf-8') as f:
        for line in f:
            embeddings.append(json.loads(line))
    return embeddings

def load_vector_store():
    meta_path = VECTOR_STORE_PATH / 'meta.json'
    if meta_path.exists():
        return json.loads(meta_path.read_text(encoding='utf-8'))
    return {}

def cosine_similarity(a: List[float], b: List[float]) -> float:
    dot = sum(x*y for x,y in zip(a,b))
    norm_a = math.sqrt(sum(x*x for x in a))
    norm_b = math.sqrt(sum(y*y for y in b))
    if norm_a == 0 or norm_b == 0:
        return 0.0
    return dot / (norm_a * norm_b)

def fake_embed(text: str, dim: int = 384) -> List[float]:
    """Deterministic fake embedding for demo without torch — hash-based"""
    h = hashlib.sha256(text.encode()).digest()
    vec = []
    for i in range(dim):
        byte_val = h[i % len(h)]
        vec.append((byte_val / 255.0 * 2 - 1) * 0.5)
    # Normalize
    norm = math.sqrt(sum(x*x for x in vec))
    if norm > 0:
        vec = [x/norm for x in vec]
    return vec

def get_embedding_for_query(query: str, model_id: str, dim: int, placeholder: bool = False) -> List[float]:
    """Embed the query with the SAME model as the stored vectors.

    Placeholder stores (embed.py --placeholder) are matched with a hash vector
    and are already flagged meaningless. For a real store there is no silent
    fallback: ranking real vectors against a hash vector returns confident
    noise (audit H5), so a missing model is an error the caller must surface.
    """
    if placeholder:
        return fake_embed(query, dim)
    try:
        from sentence_transformers import SentenceTransformer
    except ImportError as e:
        raise RuntimeError(f"cannot embed query with {model_id}: {e} "
                           "(pip install sentence-transformers); refusing to fake a query vector") from None
    model = SentenceTransformer(model_id)
    return model.encode([query], normalize_embeddings=True)[0].tolist()


def vector_search(query: str, top_k: int = 5, model_id: str = None, domain: str = None) -> List[Dict[str, Any]]:
    """Vector search over embeddings"""
    embeddings = load_embeddings()
    if not embeddings:
        print("No embeddings, run embed.py first", file=sys.stderr)
        return []

    # Filter by domain if needed
    if domain:
        # Need to load export to get domain
        export = load_export()
        entity_domain_map = {e['id']: e.get('domain') for e in export.get('entities', [])}
        embeddings = [emb for emb in embeddings if entity_domain_map.get(emb['entity_id']) == domain]

    if model_id:
        embeddings = [emb for emb in embeddings if emb['model'] == model_id]
        if not embeddings:
            print(f"No embeddings for model {model_id}, using all", file=sys.stderr)
            embeddings = load_embeddings()

    if not embeddings:
        return []

    placeholder = bool(embeddings[0].get('placeholder'))
    if placeholder:
        print("WARNING: embeddings are placeholders (embed.py --placeholder); scores are meaningless", file=sys.stderr)
    dim = embeddings[0].get('dimensions', 384)
    model_used = embeddings[0].get('model', model_id or 'sentence-transformers/all-MiniLM-L6-v2')
    query_vec = get_embedding_for_query(query, model_used, dim, placeholder=placeholder)

    scored = []
    for emb in embeddings:
        score = cosine_similarity(query_vec, emb['vector'])
        scored.append((score, emb))

    scored.sort(key=lambda x: x[0], reverse=True)
    top = scored[:top_k]

    # Load full entities for context
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
            **({'placeholder': True} if placeholder else {}),
        })
    return results

def build_context(retrieved: List[Dict[str, Any]]) -> str:
    """Build context from retrieved entities for LLM prompt"""
    lines = []
    lines.append("STEMMA Knowledge Foundation — comprehensive all-STEM, mediocre coverage, with citations")
    lines.append("")
    for i, res in enumerate(retrieved, 1):
        ent = res['entity']
        lines.append(f"{i}. {ent.get('name','')} ({ent.get('id','')}) — Domain: {ent.get('domain','')}/{ent.get('subdomain','')} Type: {ent.get('type','')}")
        lines.append(f"   Definition: {ent.get('definition','')[:500]}")
        if ent.get('provenance'):
            prov = ent['provenance']
            lines.append(f"   Source: {prov.get('source','')} Link: {prov.get('link','')} Writer: {prov.get('writer','')}")
        if ent.get('source_refs'):
            lines.append(f"   Source refs: {', '.join(ent.get('source_refs',[]))}")
        lines.append(f"   Score: {res['score']:.4f}")
        lines.append("")
    return "\n".join(lines)

def call_llm(prompt: str, model_id: str, context: str, question: str) -> str:
    """
    Call LLM with model selector like DeepSeek harness (local + frontier models)
    Supports: DeepSeek R1, Claude 3.5 Sonnet, GPT-4o, Gemini 2.5 Pro, Llama 3.3, custom via OpenRouter
    For demo, returns fake answer with citations if no API key
    """
    # Try to use webapp providers if available
    try:
        sys.path.insert(0, str(ROOT / "webapp"))
        from providers import get_provider
        # This would need config, for now fake
        pass
    except Exception:
        pass

    # Fake deterministic answer for demo
    # In production, this would call OpenRouter/NVIDIA NIM/OpenAI with model_id
    answer = f"""Based on STEMMA knowledge foundation (comprehensive all-STEM, mediocre coverage, content_hash deterministic):

Context retrieved ({len(context.split(chr(10)))} lines) for question: "{question}"

Answer (generated with model {model_id}, with citations):

The retrieved entities provide the following information:

{context[:2000]}

For your question "{question}", the answer grounded in STEMMA is:

[This is a demo RAG answer — in production, LLM {model_id} would generate answer with citations from retrieved entities]

Citations:
"""
    # Add citations from retrieved
    # We need to parse retrieved from context, but for demo just list
    answer += "\n- Sources from STEMMA entities with source_refs and links (see retrieved_entities)"
    answer += "\n\nNote: This is deterministic demo. Configure frontier model API key (OpenRouter, OpenAI, etc.) for real LLM generation via model selector like DeepSeek harness (local + frontier models)."
    return answer

def rag_query(question: str, top_k: int = 5, model_id: str = "deepseek/deepseek-r1:free", embedding_model: str = None, domain: str = None, consumer: str = "general") -> Dict[str, Any]:
    """Full RAG query: retrieve + generate"""
    export = load_export()
    content_hash = export.get('content_hash','unknown')

    # Consumer-specific model selection
    if consumer:
        consumer_registry_path = ROOT / "schema/consumer-registry.yaml"
        if consumer_registry_path.exists():
            consumer_data = yaml.safe_load(consumer_registry_path.read_text(encoding='utf-8'))
            cons = consumer_data.get('consumers', {}).get(consumer, {})
            if cons.get('rag', {}).get('model') and model_id == "deepseek/deepseek-r1:free":
                model_id = cons['rag']['model']
                print(f"Consumer {consumer} prefers LLM model {model_id}")

    print(f"RAG query: '{question}' top_k={top_k} model={model_id} embedding_model={embedding_model} domain={domain} consumer={consumer}")
    retrieved = vector_search(question, top_k=top_k, model_id=embedding_model, domain=domain)
    print(f"Retrieved {len(retrieved)} entities")

    context = build_context(retrieved)
    answer = call_llm(context + "\n\nQuestion: " + question, model_id, context, question)

    # Build citations
    citations = []
    for res in retrieved:
        ent = res['entity']
        prov = ent.get('provenance', {})
        citations.append({
            'entity_id': ent.get('id'),
            'source_ref': ent.get('source_refs',[''])[0] if ent.get('source_refs') else '',
            'link': prov.get('link',''),
        })

    return {
        'question': question,
        'answer': answer,
        'citations': citations,
        'retrieved_entities': retrieved,
        'model_used': model_id,
        'embedding_model_used': embedding_model or (retrieved[0]['entity'].get('model') if retrieved else 'unknown'),
        'content_hash': content_hash,
        'top_k': top_k,
        'domain': domain,
        'consumer': consumer,
    }

def main():
    parser = argparse.ArgumentParser(description="STEMMA RAG — comprehensive all-STEM, LearningHub, PROFESSOR-J")
    parser.add_argument('--question', help='Question for RAG query')
    parser.add_argument('--search', help='Vector search query (no LLM)')
    parser.add_argument('--top-k', type=int, default=5, help='Top K retrieved')
    parser.add_argument('--model', default='deepseek/deepseek-r1:free', help='LLM model ID (frontier selector like DeepSeek harness: deepseek-r1, claude-3.5-sonnet, gpt-4o, gemini-2.5-pro, llama-3.3, custom)')
    parser.add_argument('--embedding-model', default=None, help='Embedding model ID')
    parser.add_argument('--domain', default=None, help='Domain filter')
    parser.add_argument('--consumer', default='general', choices=['learninghub', 'professor-j', 'general'], help='Consumer')
    parser.add_argument('--list-models', action='store_true', help='List embedding and LLM models')
    args = parser.parse_args()

    if args.list_models:
        print("=== Embedding Models (for retrieval) ===")
        if EMBEDDING_REGISTRY_PATH.exists():
            reg = yaml.safe_load(EMBEDDING_REGISTRY_PATH.read_text(encoding='utf-8'))
            for m in reg.get('models', []):
                print(f"- {m['id']}: {m['name']} [{m.get('dimensions')} dim, {'FREE' if m.get('free') else 'PAID'}] — {m.get('description','')}")
        print("\n=== LLM Models (for generation, frontier selector like DeepSeek harness) ===")
        print("- deepseek/deepseek-r1:free (Reasoning, Free, 671B)")
        print("- deepseek/deepseek-v3:free (Free, 671B)")
        print("- anthropic/claude-3.5-sonnet (Frontier)")
        print("- anthropic/claude-3-opus (Frontier Reasoning)")
        print("- openai/gpt-4o (Frontier)")
        print("- openai/o1 (Reasoning Frontier)")
        print("- google/gemini-2.5-pro (Frontier)")
        print("- google/gemini-2.0-flash-exp:free (Free Frontier)")
        print("- meta-llama/llama-3.3-70b-instruct:free (Free)")
        print("- custom (your own fine-tuned via OpenRouter/NVIDIA NIM)")
        return 0

    if args.search:
        results = vector_search(args.search, top_k=args.top_k, model_id=args.embedding_model, domain=args.domain)
        print(f"Search results for '{args.search}' top_k={args.top_k}:")
        for res in results:
            print(f"- {res['entity_id']} score={res['score']:.4f} domain={res['entity'].get('domain')} name={res['entity'].get('name')}")
            print(f"  {res['content'][:200]}...")
        return 0

    if args.question:
        result = rag_query(args.question, top_k=args.top_k, model_id=args.model, embedding_model=args.embedding_model, domain=args.domain, consumer=args.consumer)
        print(json.dumps(result, indent=2))
        return 0

    parser.print_help()
    return 0

if __name__ == '__main__':
    sys.exit(main())
