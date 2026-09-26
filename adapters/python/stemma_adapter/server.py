from __future__ import annotations

"""Read-only local JSON API for STEMMA exports — comprehensive all-STEM with embeddings, RAG, consumer export"""

import json
import pathlib
import sys
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from typing import Any
from urllib.parse import parse_qs, unquote, urlsplit

from .client import BadRequestError, NotFoundError, Stemma
from .loader import ExportError

ADAPTER_VERSION = "0.3.0"

ROOT = pathlib.Path(__file__).resolve().parent.parent.parent.parent

class _Server(ThreadingHTTPServer):
    daemon_threads = True

class StemmaServer:
    """Small wrapper around ThreadingHTTPServer with a bound client."""

    def __init__(self, client: Stemma, host: str = "127.0.0.1", port: int = 8000) -> None:
        self.client = client
        self._server = _Server((host, port), self._handler_factory(client))

    @property
    def host(self) -> str:
        return str(self._server.server_address[0])

    @property
    def port(self) -> int:
        return int(self._server.server_address[1])

    def serve_forever(self) -> None:
        self._server.serve_forever()

    def shutdown(self) -> None:
        self._server.shutdown()

    def server_close(self) -> None:
        self._server.server_close()

    @staticmethod
    def _handler_factory(client: Stemma) -> type[BaseHTTPRequestHandler]:
        class Handler(BaseHTTPRequestHandler):
            adapter_client = client

            def do_OPTIONS(self) -> None:  # noqa: N802
                self.send_response(204)
                self._send_common_headers()
                self.end_headers()

            def do_GET(self) -> None:  # noqa: N802
                try:
                    payload = self._dispatch_get()
                    self._send_json(200, payload)
                except NotFoundError as exc:
                    self._send_json(404, {"error": str(exc)})
                except (BadRequestError, ExportError, ValueError) as exc:
                    self._send_json(400, {"error": str(exc)})

            def do_POST(self) -> None:  # noqa: N802
                try:
                    payload = self._dispatch_post()
                    self._send_json(200, payload)
                except NotFoundError as exc:
                    self._send_json(404, {"error": str(exc)})
                except (BadRequestError, ExportError, ValueError) as exc:
                    self._send_json(400, {"error": str(exc)})

            def log_message(self, format: str, *args: Any) -> None:  # noqa: A003
                return

            def _dispatch_get(self) -> Any:
                parsed = urlsplit(self.path)
                path = parsed.path.rstrip("/") or "/"
                query = parse_qs(parsed.query, keep_blank_values=True)

                if path == "/":
                    return {
                        "adapter": "stemma-adapter",
                        "version": ADAPTER_VERSION,
                        "content_hash": self.adapter_client.export["content_hash"],
                        "domains": ["physics", "chemistry", "biology", "earth-science", "astronomy", "computer-science", "engineering", "mathematics"],
                        "description": "STEMMA comprehensive all-STEM knowledge foundation with embeddings, RAG, consumer export for LearningHub, PROFESSOR-J",
                        "endpoints": [
                            "/",
                            "/v2/stats",
                            "/v2/entities",
                            "/v2/entities/{id}",
                            "/v2/resolve/{id}",
                            "/v2/connections",
                            "/v2/neighbors/{id}",
                            "/v2/prerequisites/{id}",
                            "/v2/values/{id}",
                            "/v2/search?q=...",
                            "/v2/external/{scheme}/{value}",
                            "/v2/relations",
                            "/v2/relations/{name}",
                            "/v2/vocabularies",
                            "/v2/embeddings?model=...&id=...&domain=... (NEW — embeddings with model selector like DeepSeek harness (local + frontier models))",
                            "/v2/rag/search?q=...&top_k=...&model=... (NEW — vector search for RAG)",
                            "/v2/export?consumer=...&format=... (NEW — consumer-specific export for LearningHub, PROFESSOR-J)",
                            "/openapi.yaml (NEW — OpenAPI schema)",
                        ],
                        "consumers": ["learninghub", "professor-j", "general", "stemma-explorer"],
                        "embedding_models": ["sentence-transformers/all-MiniLM-L6-v2", "BAAI/bge-large-en-v1.5", "openai/text-embedding-3-large", "nvidia/nv-embed-v1"],
                        "llm_models": ["deepseek/deepseek-r1:free", "anthropic/claude-3.5-sonnet", "openai/gpt-4o", "google/gemini-2.5-pro", "meta-llama/llama-3.3-70b-instruct:free"],
                        "stats": self.adapter_client.stats,
                    }

                if path == "/v2/stats":
                    return self.adapter_client.stats

                if path == "/v2/entities":
                    return self.adapter_client.entities(
                        domain=self._query_value(query, "domain"),
                        type=self._query_value(query, "type"),
                        status=self._query_value(query, "status"),
                        include_retired=self._query_bool(query, "include_retired", False),
                        limit=self._query_int(query, "limit"),
                    )

                if path.startswith("/v2/entities/"):
                    entity_id = unquote(path.removeprefix("/v2/entities/"))
                    return self.adapter_client.entity(
                        entity_id,
                        include_retired=self._query_bool(query, "include_retired", False),
                    )

                if path.startswith("/v2/resolve/"):
                    entity_id = unquote(path.removeprefix("/v2/resolve/"))
                    return self.adapter_client.resolve(entity_id)

                if path == "/v2/connections":
                    return self.adapter_client.connections(
                        source=self._query_value(query, "source"),
                        target=self._query_value(query, "target"),
                        relation=self._query_value(query, "relation"),
                        review=self._query_value(query, "review"),
                        policy=self._query_value(query, "policy"),
                        limit=self._query_int(query, "limit"),
                    )

                if path.startswith("/v2/neighbors/"):
                    entity_id = unquote(path.removeprefix("/v2/neighbors/"))
                    return self.adapter_client.neighbors(
                        entity_id,
                        direction=self._query_value(query, "direction") or "both",
                        relation=self._query_value(query, "relation"),
                        review=self._query_value(query, "review"),
                        policy=self._query_value(query, "policy"),
                        include_retired=self._query_bool(query, "include_retired", False),
                        limit=self._query_int(query, "limit"),
                    )

                if path.startswith("/v2/values/"):
                    entity_id = unquote(path.removeprefix("/v2/values/"))
                    return self.adapter_client.values(
                        entity_id,
                        relation=self._query_value(query, "relation"),
                        review=self._query_value(query, "review"),
                        policy=self._query_value(query, "policy"),
                        include_retired=self._query_bool(query, "include_retired", False),
                    )

                if path.startswith("/v2/prerequisites/"):
                    entity_id = unquote(path.removeprefix("/v2/prerequisites/"))
                    return self.adapter_client.prerequisites(
                        entity_id,
                        policy=self._query_value(query, "policy"),
                        include_retired=self._query_bool(query, "include_retired", False),
                    )

                if path == "/v2/search":
                    query_text = self._query_value(query, "q")
                    if query_text is None:
                        raise BadRequestError("missing required query parameter: q")
                    return self.adapter_client.search(
                        query_text,
                        domain=self._query_value(query, "domain"),
                        include_retired=self._query_bool(query, "include_retired", False),
                        limit=self._query_int(query, "limit"),
                    )

                if path == "/v2/relations":
                    return self.adapter_client.relations()

                if path.startswith("/v2/relations/"):
                    name = unquote(path.removeprefix("/v2/relations/"))
                    return self.adapter_client.relation(name)

                if path == "/v2/vocabularies":
                    return self.adapter_client.vocabularies or {}

                if path.startswith("/v2/external/"):
                    remainder = path.removeprefix("/v2/external/")
                    parts = remainder.split("/", 1)
                    if len(parts) != 2:
                        raise BadRequestError("external lookup path must be /v2/external/{scheme}/{value}")
                    scheme = unquote(parts[0])
                    value = unquote(parts[1])
                    return self.adapter_client.by_external_id(
                        scheme,
                        value,
                        include_retired=self._query_bool(query, "include_retired", False),
                    )

                # NEW — Embeddings endpoint
                if path == "/v2/embeddings":
                    return self._handle_embeddings(query)

                # NEW — RAG search endpoint (GET for simple search)
                if path == "/v2/rag/search":
                    return self._handle_rag_search(query)

                # NEW — Export for consumer
                if path == "/v2/export":
                    return self._handle_export(query)

                # NEW — OpenAPI
                if path == "/openapi.yaml" or path == "/v2/openapi.yaml":
                    return self._handle_openapi()

                raise NotFoundError(f"unknown route: {path}")

            def _dispatch_post(self) -> Any:
                parsed = urlsplit(self.path)
                path = parsed.path.rstrip("/") or "/"
                # query = parse_qs(parsed.query, keep_blank_values=True)

                if path == "/v2/rag/query":
                    return self._handle_rag_query()

                raise NotFoundError(f"unknown POST route: {path}")

            def _handle_embeddings(self, query: dict[str, list[str]]) -> Any:
                """Handle /v2/embeddings — with model selector like DeepSeek harness (local + frontier models)"""
                model_id = self._query_value(query, "model") or "sentence-transformers/all-MiniLM-L6-v2"
                entity_id = self._query_value(query, "id")
                domain = self._query_value(query, "domain")
                limit = self._query_int(query, "limit") or 100

                # Try to load embeddings file
                embeddings_path = ROOT / "exports/embeddings.jsonl"
                if not embeddings_path.exists():
                    return {
                        "error": "embeddings not generated yet, run python3 scripts/embed.py",
                        "model": model_id,
                        "hint": "python3 scripts/embed.py --model sentence-transformers/all-MiniLM-L6-v2",
                        "available_models": [
                            "sentence-transformers/all-MiniLM-L6-v2 (FREE LOCAL 384 dim)",
                            "BAAI/bge-large-en-v1.5 (FREE LOCAL SOTA 1024 dim)",
                            "openai/text-embedding-3-large (FRONTIER 3072 dim)",
                            "nvidia/nv-embed-v1 (FRONTIER SOTA 4096 dim)"
                        ]
                    }

                results = []
                with open(embeddings_path, 'r', encoding='utf-8') as f:
                    for line in f:
                        try:
                            emb = json.loads(line)
                        except:
                            continue
                        if model_id and emb.get('model') != model_id:
                            # If model filter but no match, skip unless no embeddings for that model
                            pass
                        if entity_id and emb.get('entity_id') != entity_id:
                            continue
                        # Domain filter needs entity lookup
                        if domain:
                            # Quick check via entity id prefix or via export
                            ent = self.adapter_client.export.get('entities', [])
                            # For simplicity, check if domain in entity_id or via lookup
                            found = False
                            for e in self.adapter_client.export.get('entities', []):
                                if e['id'] == emb.get('entity_id') and e.get('domain') == domain:
                                    found = True
                                    break
                            if not found:
                                continue
                        results.append({
                            'entity_id': emb.get('entity_id'),
                            'model': emb.get('model'),
                            'dimensions': emb.get('dimensions'),
                            'content_hash': emb.get('content_hash'),
                            # Don't return full vector by default for size, unless ?full=true
                            'vector_preview': emb.get('vector', [])[:5] if emb.get('vector') else [],
                            'content': emb.get('content','')[:200],
                        })
                        if len(results) >= limit:
                            break

                # If no results for model, try without model filter
                if not results and model_id:
                    with open(embeddings_path, 'r', encoding='utf-8') as f:
                        for line in f:
                            emb = json.loads(line)
                            if entity_id and emb.get('entity_id') != entity_id:
                                continue
                            results.append({
                                'entity_id': emb.get('entity_id'),
                                'model': emb.get('model'),
                                'dimensions': emb.get('dimensions'),
                                'content_hash': emb.get('content_hash'),
                                'vector_preview': emb.get('vector', [])[:5],
                                'content': emb.get('content','')[:200],
                            })
                            if len(results) >= limit:
                                break

                return {
                    'model': model_id,
                    'count': len(results),
                    'embeddings': results,
                    'hint': 'Use ?full=true to get full vectors (large), or /v2/rag/search for vector search',
                    'available_models': 'See /openapi.yaml and schema/embedding-registry.yaml — local free BGE, All-MiniLM + frontier OpenAI, Cohere, Gemini, NVIDIA'
                }

            def _handle_rag_search(self, query: dict[str, list[str]]) -> Any:
                """Handle /v2/rag/search — vector search"""
                q = self._query_value(query, "q")
                if not q:
                    raise BadRequestError("missing q")
                top_k = self._query_int(query, "top_k") or self._query_int(query, "limit") or 5
                model_id = self._query_value(query, "model")
                domain = self._query_value(query, "domain")

                # Use scripts/rag.py vector_search if available
                try:
                    sys.path.insert(0, str(ROOT / "scripts"))
                    import rag as rag_module
                    results = rag_module.vector_search(q, top_k=top_k, model_id=model_id, domain=domain)
                    return {
                        'query': q,
                        'top_k': top_k,
                        'model': model_id or 'default',
                        'results': results,
                    }
                except Exception as e:
                    # Fallback: simple text search
                    search_results = self.adapter_client.search(q, domain=domain, limit=top_k)
                    return {
                        'query': q,
                        'top_k': top_k,
                        'results': [{'entity': ent, 'score': 0.5, 'content': ent.get('definition','')[:200]} for ent in search_results],
                        'note': f'vector search failed ({e}), fell back to text search — run python3 scripts/embed.py first',
                    }

            def _handle_rag_query(self) -> Any:
                """Handle POST /v2/rag/query — full RAG"""
                content_length = int(self.headers.get('Content-Length', 0))
                body = self.rfile.read(content_length) if content_length > 0 else b'{}'
                try:
                    data = json.loads(body.decode('utf-8')) if body else {}
                except:
                    data = {}

                question = data.get('question') or data.get('q')
                if not question:
                    raise BadRequestError("missing question")

                top_k = data.get('top_k', 5)
                model_id = data.get('model', 'deepseek/deepseek-r1:free')
                embedding_model = data.get('embedding_model')
                domain = data.get('domain')
                consumer = data.get('consumer', 'general')

                try:
                    sys.path.insert(0, str(ROOT / "scripts"))
                    import rag as rag_module
                    result = rag_module.rag_query(question, top_k=top_k, model_id=model_id, embedding_model=embedding_model, domain=domain, consumer=consumer)
                    return result
                except Exception as e:
                    return {
                        'question': question,
                        'answer': f'RAG failed: {e} — run python3 scripts/embed.py first, and configure LLM API key for frontier model {model_id}',
                        'citations': [],
                        'retrieved_entities': [],
                        'model_used': model_id,
                        'error': str(e),
                    }

            def _handle_export(self, query: dict[str, list[str]]) -> Any:
                """Handle /v2/export?consumer=learninghub&format=json"""
                consumer = self._query_value(query, "consumer") or "general"
                fmt = self._query_value(query, "format") or "json"
                review_policy = self._query_value(query, "review_policy")

                # Try to load consumer-specific export if exists
                consumer_export_path = ROOT / f"exports/consumers/{consumer}/knowledge.{consumer}.json"
                if consumer_export_path.exists() and fmt == "json":
                    return json.loads(consumer_export_path.read_text(encoding='utf-8'))

                # Otherwise filter on the fly
                try:
                    sys.path.insert(0, str(ROOT / "schema"))
                    import yaml
                    consumer_registry_path = ROOT / "schema/consumer-registry.yaml"
                    if consumer_registry_path.exists():
                        reg = yaml.safe_load(consumer_registry_path.read_text(encoding='utf-8'))
                        cfg = reg.get('consumers', {}).get(consumer, {})
                        # Filter entities
                        entities = self.adapter_client.export.get('entities', [])
                        domains = cfg.get('domains', [])
                        if domains != 'all' and domains:
                            entities = [e for e in entities if e.get('domain') in domains]
                        policy = review_policy or cfg.get('review_policy', 'all')
                        if policy == 'canonical':
                            entities = [e for e in entities if e.get('status') == 'canonical']
                        elif policy == 'reviewed':
                            entities = [e for e in entities if e.get('status') in ('human_reviewed','canonical')]

                        return {
                            'consumer': consumer,
                            'consumer_label': cfg.get('label', consumer),
                            'format': fmt,
                            'review_policy': policy,
                            'entity_count': len(entities),
                            'entities': entities[:100],  # limit for preview
                            'hint': f'Full export at exports/consumers/{consumer}/knowledge.{consumer}.json — run python3 scripts/export_consumers.py --consumer {consumer} --format {fmt}',
                            'embedding_model': cfg.get('embedding_model'),
                            'api_access': cfg.get('api_access'),
                            'rag': cfg.get('rag'),
                        }
                except Exception as e:
                    pass

                return {
                    'consumer': consumer,
                    'format': fmt,
                    'entities': self.adapter_client.entities(limit=100),
                    'note': f'Consumer export not pre-generated, run python3 scripts/export_consumers.py --consumer {consumer}',
                }

            def _handle_openapi(self) -> Any:
                """Serve OpenAPI YAML as JSON for simplicity, or raw YAML"""
                openapi_path = ROOT / "schema/api.yaml"
                if openapi_path.exists():
                    # Return as text but we must return JSON via _send_json, so return parsed
                    try:
                        import yaml
                        data = yaml.safe_load(openapi_path.read_text(encoding='utf-8'))
                        return data
                    except:
                        return {'openapi': '3.0.3', 'info': {'title': 'STEMMA API', 'version': '2.1.0'}, 'path': str(openapi_path)}
                return {'error': 'OpenAPI not found', 'path': 'schema/api.yaml'}

            def _send_json(self, status: int, payload: Any) -> None:
                etag = self.adapter_client.export.get("content_hash", "unknown")
                if self.headers.get("If-None-Match") in {etag, f'"{etag}"'} and status == 200:
                    self.send_response(304)
                    self._send_common_headers()
                    self.send_header("ETag", f'"{etag}"')
                    self.end_headers()
                    return

                body = json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True).encode("utf-8")
                self.send_response(status)
                self._send_common_headers()
                self.send_header("Content-Length", str(len(body)))
                self.send_header("Content-Type", "application/json; charset=utf-8")
                self.send_header("ETag", f'"{etag}"')
                self.end_headers()
                self.wfile.write(body)

            def _send_common_headers(self) -> None:
                self.send_header("Access-Control-Allow-Origin", "*")
                self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
                self.send_header("Access-Control-Allow-Headers", "Content-Type, If-None-Match")
                self.send_header("Cache-Control", "no-cache")

            @staticmethod
            def _query_value(query: dict[str, list[str]], key: str) -> str | None:
                values = query.get(key)
                if not values:
                    return None
                value = values[-1]
                return value if value != "" else None

            @classmethod
            def _query_bool(cls, query: dict[str, list[str]], key: str, default: bool) -> bool:
                value = cls._query_value(query, key)
                if value is None:
                    return default
                normalized = value.casefold()
                if normalized in {"1", "true", "yes", "on"}:
                    return True
                if normalized in {"0", "false", "no", "off"}:
                    return False
                raise BadRequestError(f"query parameter {key} must be boolean")

            @classmethod
            def _query_int(cls, query: dict[str, list[str]], key: str) -> int | None:
                value = cls._query_value(query, key)
                if value is None:
                    return None
                try:
                    parsed = int(value)
                except ValueError as exc:
                    raise BadRequestError(f"query parameter {key} must be an integer") from exc
                if parsed <= 0:
                    raise BadRequestError(f"query parameter {key} must be positive")
                return parsed

        return Handler


def serve(client: Stemma, host: str = "127.0.0.1", port: int = 8000) -> StemmaServer:
    return StemmaServer(client=client, host=host, port=port)
