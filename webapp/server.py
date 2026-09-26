#!/usr/bin/env python3
"""STEMMA ingestion/review webapp server.

A simple, dependency-free HTTP server that exposes the human-in-the-loop
ingestion workflow. It serves a single-page UI and a small JSON API over
``webapp.core.Workflow``. It never writes canonical knowledge.

Run (single-owner admin tool; local by default):
    python3 webapp/server.py                      # http://127.0.0.1:8081

Security model: this is the private curation tool. It binds to 127.0.0.1, sends
no CORS headers, and rejects requests whose Host / Origin is not this server
(blocks cross-site requests and DNS rebinding). For remote access use a private
network (e.g. ``tailscale serve 8081``) and add the name you browse with to
``STEMMA_ALLOWED_HOSTS`` (comma-separated). Never expose it to the internet.
"""
from __future__ import annotations

import argparse
import json
import os
import re
import sys
import uuid
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any
from urllib.parse import parse_qs, unquote, urlsplit

import yaml

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT / "webapp") not in sys.path:
    sys.path.insert(0, str(ROOT / "webapp"))

from core import (  # noqa: E402
    CandidateInvalid,
    ExtractionFailed,
    NotFound,
    ProviderError,
    ProviderNotConfigured,
    WebappError,
    Workflow,
)

STATIC_DIR = Path(__file__).resolve().parent / "static"

# Workflow identifiers (document ids are uuid hex; candidate ids are similar).
# Strict allowlist: no path separators, no leading dot, no "..".
_SAFE_ID_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9_.-]{0,127}$")


_LOCAL_HOSTS = {"localhost", "127.0.0.1", "::1"}
MAX_BODY_BYTES = int(os.environ.get("STEMMA_MAX_BODY_MB", "50")) * 1024 * 1024


def _allowed_hosts() -> set[str]:
    extra = {h.strip().lower() for h in os.environ.get("STEMMA_ALLOWED_HOSTS", "").split(",") if h.strip()}
    return _LOCAL_HOSTS | extra


def _hostname(netloc: str) -> str:
    """Hostname part of a Host header / netloc (handles [::1]:8081 and host:port)."""
    netloc = netloc.strip().lower()
    if netloc.startswith("["):
        return netloc[1:netloc.find("]")] if "]" in netloc else netloc
    return netloc.rsplit(":", 1)[0] if netloc.count(":") == 1 else netloc


def _safe_id(value: Any, label: str = "id") -> str:
    """Return ``value`` if it is a safe single path segment, else raise WebappError."""
    if not isinstance(value, str) or not _SAFE_ID_RE.match(value) or ".." in value:
        raise WebappError(f"invalid {label}: {value!r}")
    return value


class _Server(ThreadingHTTPServer):
    daemon_threads = True


class _Handler(BaseHTTPRequestHandler):
    workflow: Workflow

    def _request_allowed(self) -> bool:
        """Same-origin + Host allowlist guard (CSRF / cross-site / DNS rebinding).

        - Host header must name this server (localhost or STEMMA_ALLOWED_HOSTS).
        - If the browser sends Origin, it must be exactly this server's origin.
        - State-changing requests must be JSON (forces a CORS preflight, which
          this server never approves).
        Sends the error response itself and returns False when blocked.
        """
        host = self.headers.get("Host") or ""
        if _hostname(host) not in _allowed_hosts():
            self._send_json(403, {"error": f"host {host!r} not allowed; add it to STEMMA_ALLOWED_HOSTS "
                                           "if you intentionally browse via that name"})
            return False
        origin = self.headers.get("Origin")
        if origin is not None:
            origin_netloc = urlsplit(origin).netloc.lower()
            if origin == "null" or origin_netloc != host.strip().lower():
                self._send_json(403, {"error": "cross-origin request blocked"})
                return False
        if self.command in ("POST", "PATCH", "PUT"):
            ctype = (self.headers.get("Content-Type") or "").split(";")[0].strip().lower()
            if ctype != "application/json":
                self._send_json(415, {"error": "Content-Type must be application/json"})
                return False
        return True

    def do_OPTIONS(self) -> None:  # noqa: N802
        # No CORS: the UI is same-origin, so preflights are never approved.
        self.send_response(405)
        self.send_header("Allow", "GET, POST, PATCH, DELETE")
        self.send_header("Content-Length", "0")
        self.end_headers()

    def do_GET(self) -> None:  # noqa: N802
        if not self._request_allowed():
            return
        parsed = urlsplit(self.path)
        path = parsed.path.rstrip("/") or "/"
        if path == "/" or path.startswith("/static/"):
            self._serve_page(path)
            return
        try:
            status, payload = self._dispatch_get()
        except (NotFound, WebappError) as exc:
            self._send_json(404 if isinstance(exc, NotFound) else 400, {"error": str(exc)})
            return
        self._send_json(status, payload)

    def _serve_page(self, path: str) -> None:
        name = "index.html" if path == "/" else path.removeprefix("/static/").split("?")[0]
        try:
            content, content_type = self._read_asset(name)
        except (NotFound, WebappError) as exc:
            self._send_json(404 if isinstance(exc, NotFound) else 400, {"error": str(exc)})
            return
        self.send_response(200)
        self._send_common_headers()
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(content)))
        self.end_headers()
        self.wfile.write(content)

    @staticmethod
    def _read_asset(name: str) -> tuple[bytes, str]:
        # lgtm[py/path-injection]
        # `Path(name).name` strips all directory components — traversal impossible.
        # Defense-in-depth: resolved path must live strictly inside STATIC_DIR.
        safe = Path(name).name
        try:
            resolved = (STATIC_DIR / safe).resolve()
        except OSError:
            raise NotFound(f"static asset not found: {name}") from None
        if not resolved.is_file() or resolved.parent != STATIC_DIR.resolve():
            raise NotFound(f"static asset not found: {name}")
        suffix = resolved.suffix.lower()
        content_type = {
            ".html": "text/html; charset=utf-8",
            ".css": "text/css; charset=utf-8",
            ".js": "application/javascript; charset=utf-8",
            ".json": "application/json; charset=utf-8",
        }.get(suffix, "application/octet-stream")
        return resolved.read_bytes(), content_type

    def do_POST(self) -> None:  # noqa: N802
        if not self._request_allowed():
            return
        try:
            status, payload = self._dispatch_post()
        except ProviderNotConfigured as exc:
            self._send_json(409, {"error": str(exc), "code": "provider_not_configured"})
            return
        except (CandidateInvalid, ExtractionFailed, ProviderError, WebappError, NotFound) as exc:
            self._send_json(
                404 if isinstance(exc, NotFound) else 400,
                {"error": str(exc), "code": type(exc).__name__},
            )
            return
        self._send_json(status, payload)

    def do_PATCH(self) -> None:  # noqa: N802
        if not self._request_allowed():
            return
        try:
            status, payload = self._dispatch_patch()
        except NotFound as exc:
            self._send_json(404, {"error": str(exc)})
            return
        except (WebappError, ValueError) as exc:
            self._send_json(400, {"error": str(exc)})
            return
        self._send_json(status, payload)

    def do_DELETE(self) -> None:  # noqa: N802
        if not self._request_allowed():
            return
        try:
            status, payload = self._dispatch_delete()
        except NotFound as exc:
            self._send_json(404, {"error": str(exc)})
            return
        self._send_json(status, payload)

    # ------------------------------------------------------------------ #
    # Routing
    # ------------------------------------------------------------------ #
    def _dispatch_get(self) -> tuple[int, Any]:
        parsed = urlsplit(self.path)
        path = parsed.path.rstrip("/") or "/"
        query = parse_qs(parsed.query, keep_blank_values=True)
        wf = self.workflow

        if path == "/api/config":
            return 200, wf.read_llm_config(mask=True)
        if path == "/api/models":
            provider = self._query_value(query, "provider") or wf.read_llm_config().get("provider", "antigravity")
            free_only = self._query_value(query, "free_only") != "false"
            import providers
            models = providers.fetch_provider_models(provider, free_only=free_only)
            return 200, {"models": models}
        if path == "/api/models/embedding":
            # Embedding models — model selector like DeepSeek harness (local + frontier models) for embeddings
            try:
                emb_path = ROOT / "schema/embedding-registry.yaml"
                if emb_path.exists():
                    data = yaml.safe_load(emb_path.read_text(encoding="utf-8"))
                    return 200, {"models": data.get("models", []), "default": data.get("default_model")}
            except Exception as e:
                pass
            return 200, {"models": [], "default": "sentence-transformers/all-MiniLM-L6-v2"}
        if path == "/api/documents":
            return 200, {"documents": wf.list_documents()}
        if path == "/api/candidates":
            doc_id = self._query_value(query, "doc_id")
            return 200, {"candidates": wf.list_candidates(doc_id)}
        if path == "/api/proposals":
            return 200, {"proposals": wf.list_proposals()}
        if path == "/api/audit":
            return 200, {"events": wf.read_audit()}
        # NEW — RAG search (GET)
        if path == "/api/rag/search":
            q = self._query_value(query, "q")
            if not q:
                raise WebappError("missing q")
            top_k = int(self._query_value(query, "top_k") or self._query_value(query, "limit") or "5")
            model = self._query_value(query, "model")
            domain = self._query_value(query, "domain")
            try:
                sys.path.insert(0, str(ROOT / "scripts"))
                import rag as rag_module
                results = rag_module.vector_search(q, top_k=top_k, model_id=model, domain=domain)
                return 200, {"query": q, "top_k": top_k, "results": results}
            except Exception as e:
                return 200, {"query": q, "error": str(e), "hint": "run python3 scripts/embed.py first", "results": []}
        # NEW — Embeddings
        if path == "/api/embeddings":
            model_id = self._query_value(query, "model") or "sentence-transformers/all-MiniLM-L6-v2"
            emb_path = ROOT / "exports/embeddings.jsonl"
            if not emb_path.exists():
                return 200, {"model": model_id, "error": "embeddings not generated, run python3 scripts/embed.py", "count": 0, "embeddings": []}
            results=[]
            limit = int(self._query_value(query, "limit") or "20")
            with open(emb_path, 'r', encoding='utf-8') as f:
                for line in f:
                    try:
                        emb=json.loads(line)
                    except:
                        continue
                    if emb.get('model') != model_id:
                        continue
                    results.append({k: v for k,v in emb.items() if k != 'vector'})
                    if len(results)>=limit:
                        break
            return 200, {"model": model_id, "count": len(results), "embeddings": results}
        # NEW — Export for consumer
        if path == "/api/export":
            # Preview of a consumer bundle, built by the same code that writes the
            # published bundles (scripts/export_consumers.py) so tiers match exactly.
            consumer = self._query_value(query, "consumer") or "general"
            if str(ROOT / "scripts") not in sys.path:
                sys.path.insert(0, str(ROOT / "scripts"))
            import export_consumers as _ec
            registry = _ec.load_registry()
            if consumer not in registry:
                raise WebappError(f"unknown consumer {consumer!r}; known: {', '.join(sorted(registry))}")
            base = json.loads((ROOT / "exports" / "knowledge.json").read_text(encoding="utf-8"))
            versions = yaml.safe_load((ROOT / "schema" / "VERSION.yaml").read_text(encoding="utf-8"))
            try:
                bundle = _ec.build_consumer_export(consumer, registry[consumer], base, versions)
            except _ec.ConsumerExportError as exc:
                raise WebappError(str(exc)) from None
            return 200, {
                "consumer": consumer,
                "config": bundle["consumer_profile"],
                "entity_count": bundle["entity_count"],
                "connection_count": bundle["connection_count"],
                "source_count": bundle["source_count"],
                "payload_sha256": bundle["payload_sha256"],
                "entities": bundle["entities"][:20],
            }
        # NEW — Semantic Acquisition Pipeline GET endpoints
        if path == "/api/semantic/claims":
            doc_id = self._query_value(query, "doc_id")
            if not doc_id:
                raise WebappError("doc_id required")
            doc_id = _safe_id(doc_id, "doc_id")
            try:
                wf = self.workflow
                candidates_dir = wf.root / f"candidates/{doc_id}"
                possible = [
                    candidates_dir / "semantic_claims.json",
                    candidates_dir / "semantic_claims_verified.json",
                    candidates_dir / "semantic_claims_resolved.json"
                ]
                for pf in possible:
                    if pf.exists():
                        import json as js
                        data = js.loads(pf.read_text())
                        return 200, data
                return 200, {"doc_id": doc_id, "claims": [], "message": "no semantic claims yet, run /api/semantic/extract"}
            except (WebappError, NotFound):
                raise
            except Exception as e:
                return 200, {"error": str(e), "claims": []}

        if path == "/api/semantic/proposals/list":
            try:
                proposals_dir = ROOT / "proposals"
                import json as js
                proposals=[]
                for f in list(proposals_dir.glob("*.yaml"))[:20] + list(proposals_dir.glob("*.json"))[:20]:
                    try:
                        if f.suffix==".yaml":
                            data=yaml.safe_load(f.read_text())
                        else:
                            data=js.loads(f.read_text())
                        proposals.append({"proposal_id": data.get("proposal_id"), "claim": data.get("claim"), "evidence": {"text_span": data.get("evidence",{}).get("text_span","")[:100]}, "verification": data.get("verification",{}).get("status")})
                    except:
                        continue
                return 200, {"proposals": proposals, "count": len(proposals)}
            except (WebappError, NotFound):
                raise
            except Exception as e:
                return 200, {"error": str(e), "proposals": []}

        if path == "/api/semantic/registries":
            try:
                result={}
                for name in ["template-registry", "embedding-registry", "consumer-registry", "llm-registry"]:
                    rp = ROOT / f"schema/{name}.yaml"
                    if rp.exists():
                        data=yaml.safe_load(rp.read_text())
                        result[name] = {"version": data.get("version"), "count": len(data.get("domains",{}) or data.get("models",{}) or data.get("consumers",{}) or data.get("roles",{}))}
                return 200, result
            except (WebappError, NotFound):
                raise
            except Exception as e:
                return 200, {"error": str(e)}

        # NEW — OpenAPI
        if path == "/api/openapi" or path == "/openapi.yaml":
            try:
                api_path = ROOT / "schema/api.yaml"
                if api_path.exists():
                    return 200, yaml.safe_load(api_path.read_text(encoding='utf-8'))
            except (WebappError, NotFound):
                raise
            except Exception as e:
                return 200, {"error": str(e)}
        if path.endswith("/text") and path.startswith("/api/documents/"):
            doc_id = self._id_from_path(path, "/api/documents/", suffix="/text")
            doc = wf.get_document(doc_id)
            text_path = (doc.get("extraction") or {}).get("text_path")
            if not text_path:
                return 200, {"text": "", "message": "no extracted text yet"}
            text = (wf.root / text_path).read_text(encoding="utf-8")
            return 200, {"text": text, "message": "ok"}
        if path.startswith("/api/documents/"):
            doc_id = self._id_from_path(path, "/api/documents/")
            return 200, wf.get_document(doc_id)
        raise NotFound(f"unknown route: {path}")

    def _dispatch_post(self) -> tuple[int, Any]:
        parsed = urlsplit(self.path)
        path = parsed.path.rstrip("/")
        wf = self.workflow

        if path == "/api/config":
            body = self._read_json_body()
            return 200, wf.save_llm_config(
                provider=str(body.get("provider") or "antigravity"),
                base_url=str(body.get("base_url") or ""),
                model=str(body.get("model") or ""),
                api_key=str(body.get("api_key") or ""),
                project=str(body.get("project") or ""),
                location=str(body.get("location") or ""),
                transport=str(body.get("transport") or ""),
                effort=str(body.get("effort") or ""),
                agent=str(body.get("agent") or ""),
            )
        if path == "/api/config/test":
            return 200, wf.test_llm_provider()
        if path == "/api/config/models":
            body = self._read_json_body()
            return 200, wf.list_provider_models(
                provider=str(body.get("provider") or "") or None,
                base_url=str(body.get("base_url") or "") or None,
                api_key=str(body.get("api_key") or "") or None,
            )
        if path == "/api/config/login":
            body = self._read_json_body()
            return 200, wf.provider_login(
                provider=str(body.get("provider") or "") or None,
                base_url=str(body.get("base_url") or "") or None,
                api_key=str(body.get("api_key") or "") or None,
            )
        if path == "/api/documents":
            body = self._read_json_body()
            try:
                data = _decode_base64(str(body.get("data_base64") or ""))
            except ValueError as exc:
                raise WebappError(f"invalid base64 upload: {exc}") from exc
            return 201, wf.accept_upload(
                original_name=str(body.get("filename") or "upload"),
                mime=str(body.get("mime") or ""),
                data=data,
            )
        if path.startswith("/api/documents/") and path.endswith("/extract"):
            doc_id = self._id_from_path(path, "/api/documents/", suffix="/extract")
            return 200, wf.extract_document(doc_id)
        if path.startswith("/api/documents/") and path.endswith("/generate"):
            doc_id = self._id_from_path(path, "/api/documents/", suffix="/generate")
            body = self._read_json_body()
            return 200, wf.generate_candidates(doc_id, target_kinds=body.get("target_kinds"))
        if path.startswith("/api/documents/") and path.endswith("/deterministic-draft"):
            doc_id = self._id_from_path(path, "/api/documents/", suffix="/deterministic-draft")
            # Deterministic draft — no LLM, uses evolvable templates, scales
            try:
                sys.path.insert(0, str(ROOT / "scripts"))
                from evolvable_template import deterministic_extract, build_markdown, load_registry
                registry = load_registry()
                text_path = wf.root / f"extraction/{doc_id}.txt"
                if not text_path.exists():
                    raise Exception(f"Extraction not found for {doc_id}, run Extract first")
                text = text_path.read_text(encoding="utf-8")
                entities = deterministic_extract(text, registry)
                # Build candidates deterministically
                from datetime import datetime, timezone
                now = datetime.now(timezone.utc).isoformat()
                candidates_dir = wf.root / f"candidates/{doc_id}"
                candidates_dir.mkdir(parents=True, exist_ok=True)
                candidates=[]
                for ent in entities:
                    md = build_markdown(ent, registry)
                    md_path = candidates_dir / f"{ent['slug']}.md"
                    md_path.write_text(md, encoding="utf-8")
                    candidates.append({
                        "id": f"cand-{ent['slug']}-001",
                        "doc_id": doc_id,
                        "kind": "entity",
                        "proposal": {
                            "id": ent["id"],
                            "type": ent["type"],
                            "name": ent["name"],
                            "domain": ent["domain"],
                            "subdomain": ent["subdomain"],
                            "status": "draft",
                            "definition": ent["pdf_definition"] if ent.get("has_exact") else f"{ent['name']} defined per SI Brochure with exact constants",
                            "symbol": ent.get("symbol",""),
                            "unit": ent.get("unit",""),
                            "governed_by": ent.get("governed_by",[]),
                            "provenance": {
                                "ai_drafted": False,
                                "writer": "human:curator.001",
                                "source_kind": "standards-or-specification",
                                "source": f"Deterministic from {doc_id} + SI Brochure constants",
                                "link": "https://www.bipm.org/en/publications/si-brochure",
                                "original_author": "BIPM & Halliday, Resnick, Walker",
                                "retrieved_at": now[:10]
                            },
                            "source_refs": ent.get("source_refs",[]),
                            "external_ids": {"wd": "Q0"}
                        },
                        "findings": [],
                        "markdown_path": f"candidates/{doc_id}/{ent['slug']}.md",
                        "human_edited": False,
                        "created_at": now,
                        "updated_at": now
                    })
                # Write candidates json
                cand_json_path = wf.root / f"candidates/{doc_id}.json"
                # Merge with existing if any
                existing = {}
                if cand_json_path.exists():
                    try:
                        existing = json.loads(cand_json_path.read_text())
                    except:
                        existing = {}
                existing_cands = existing.get("candidates", [])
                # Deduplicate by id
                existing_ids = {c["proposal"]["id"] for c in existing_cands}
                for c in candidates:
                    if c["proposal"]["id"] not in existing_ids:
                        existing_cands.append(c)
                out = {"doc_id": doc_id, "generated_at": now, "candidates": existing_cands or candidates}
                cand_json_path.write_text(json.dumps(out, indent=2), encoding="utf-8")
                wf.log("candidates_generated", doc_id=doc_id, detail={"count": len(out["candidates"]), "deterministic": True, "markdown_previews": [c["markdown_path"] for c in out["candidates"]]})
                return 200, out
            except Exception as e:
                raise Exception(f"Deterministic draft failed: {e}")
        if path.startswith("/api/candidates/") and path.endswith("/stage"):
            candidate_id = self._id_from_path(path, "/api/candidates/", suffix="/stage")
            body = self._read_json_body()
            reviewer = str(body.get("reviewer") or "")
            if not reviewer:
                raise WebappError("reviewer is required to stage a proposal")
            return 201, wf.stage_candidate(candidate_id, reviewer=reviewer, note=str(body.get("note") or ""))
        # NEW — RAG query POST
        if path == "/api/rag/query":
            body = self._read_json_body()
            question = body.get("question") or body.get("q")
            if not question:
                raise WebappError("missing question")
            top_k = int(body.get("top_k") or 5)
            model_id = body.get("model") or "deepseek/deepseek-r1:free"
            embedding_model = body.get("embedding_model")
            domain = body.get("domain")
            consumer = body.get("consumer") or "general"
            try:
                sys.path.insert(0, str(ROOT / "scripts"))
                import rag as rag_module
                result = rag_module.rag_query(question, top_k=top_k, model_id=model_id, embedding_model=embedding_model, domain=domain, consumer=consumer)
                return 200, result
            except Exception as e:
                return 200, {"question": question, "answer": f"RAG failed: {e} — run python3 scripts/embed.py first", "error": str(e), "citations": [], "retrieved_entities": []}

        # NEW — Semantic Acquisition Pipeline endpoints
        if path == "/api/semantic/extract":
            body = self._read_json_body()
            doc_id = body.get("doc_id")
            if doc_id is not None:
                doc_id = _safe_id(doc_id, "doc_id")
            text = body.get("text")
            source_id = body.get("source_id") or "stemma:src.test"
            model_id = body.get("model") or "deterministic"
            provider = body.get("provider") or "deterministic"
            try:
                sys.path.insert(0, str(ROOT / "scripts"))
                import semantic_extract
                if doc_id:
                    # Load from workflow
                    wf = self.workflow
                    meta_path = wf.root / "meta" / f"{doc_id}.json"
                    if not meta_path.exists():
                        raise NotFound(f"document not found: {doc_id}")
                    meta = json.loads(meta_path.read_text())
                    extraction = meta.get("extraction", {})
                    text_path = extraction.get("text_path")
                    if text_path:
                        full_text = (wf.root / text_path).read_text(encoding="utf-8")
                    else:
                        full_text = (wf.root / "documents" / f"{doc_id}.txt").read_text(encoding="utf-8")
                    claims = semantic_extract.semantic_extract(full_text, source_id=source_id, model_id=model_id, provider=provider)
                    # Save to candidates
                    from datetime import datetime, timezone
                    candidates_dir = wf.root / f"candidates/{doc_id}"
                    candidates_dir.mkdir(parents=True, exist_ok=True)
                    out_path = candidates_dir / "semantic_claims.json"
                    out_data = {
                        "document_id": doc_id,
                        "source_id": source_id,
                        "extraction": {"model_provider": provider, "model_id": model_id, "created_at": datetime.now(timezone.utc).isoformat()},
                        "claims": claims,
                        "count": len(claims)
                    }
                    out_path.write_text(json.dumps(out_data, indent=2), encoding="utf-8")
                    return 200, out_data
                elif text:
                    claims = semantic_extract.semantic_extract(text, source_id=source_id, model_id=model_id, provider=provider)
                    return 200, {"source_id": source_id, "claims": claims, "count": len(claims)}
                else:
                    raise WebappError("doc_id or text required")
            except (WebappError, NotFound):
                raise
            except Exception as e:
                return 200, {"error": str(e), "claims": [], "hint": "run pdf_ingest_primary.py --check-registries first"}

        if path == "/api/semantic/verify":
            body = self._read_json_body()
            claims_file = body.get("claims_file")
            verifier_model = body.get("verifier_model") or "anthropic/claude-3-haiku"
            provider = body.get("provider") or "openrouter"
            try:
                sys.path.insert(0, str(ROOT / "scripts"))
                import verify_claim
                if claims_file:
                    p = self._confined_claims_file(claims_file)
                    data = json.loads(p.read_text())
                    result = verify_claim.verify_claims(data, verifier_model_id=verifier_model, verifier_provider=provider)
                    return 200, result
                else:
                    raise WebappError("claims_file required")
            except (WebappError, NotFound):
                raise
            except Exception as e:
                return 200, {"error": str(e)}

        if path == "/api/semantic/conflicts":
            body = self._read_json_body()
            claims_file = body.get("claims_file")
            try:
                sys.path.insert(0, str(ROOT / "scripts"))
                import conflict_analysis
                if claims_file:
                    p = self._confined_claims_file(claims_file)
                    data = json.loads(p.read_text())
                    result = conflict_analysis.analyze_conflicts(data)
                    return 200, result
                else:
                    raise WebappError("claims_file required")
            except (WebappError, NotFound):
                raise
            except Exception as e:
                return 200, {"error": str(e)}

        if path == "/api/semantic/proposals":
            body = self._read_json_body()
            doc_id = body.get("doc_id") or "test-doc"
            claims_file = body.get("claims_file")
            try:
                sys.path.insert(0, str(ROOT / "scripts"))
                import proposal_generate
                if claims_file:
                    p = self._confined_claims_file(claims_file)
                    data = json.loads(p.read_text())
                    proposals = proposal_generate.generate_proposals(data, doc_id=doc_id)
                    written = proposal_generate.write_proposals(proposals, doc_id)
                    return 200, {"doc_id": doc_id, "proposals": proposals[:5], "count": len(proposals), "written": written}
                else:
                    raise WebappError("claims_file required")
            except (WebappError, NotFound):
                raise
            except Exception as e:
                return 200, {"error": str(e)}

        if path == "/api/semantic/resolve":
            body = self._read_json_body()
            claims_file = body.get("claims_file")
            threshold = float(body.get("threshold") or 0.85)
            try:
                sys.path.insert(0, str(ROOT / "scripts"))
                import entity_resolution
                if claims_file:
                    p = self._confined_claims_file(claims_file)
                    data = json.loads(p.read_text())
                    resolved = entity_resolution.resolve_claim_entities(data, threshold=threshold)
                    return 200, {"claims": resolved[:5], "count": len(resolved)}
                else:
                    raise WebappError("claims_file required")
            except (WebappError, NotFound):
                raise
            except Exception as e:
                return 200, {"error": str(e)}

        raise NotFound(f"unknown route: {path}")

    def _dispatch_patch(self) -> tuple[int, Any]:
        parsed = urlsplit(self.path)
        path = parsed.path.rstrip("/")
        if path.startswith("/api/candidates/"):
            candidate_id = self._id_from_path(path, "/api/candidates/")
            body = self._read_json_body()
            proposal = body.get("proposal")
            if not isinstance(proposal, dict):
                raise WebappError("proposal object is required")
            # HITL: support explicit markdown edit
            edited_markdown = body.get("edited_markdown")
            human_edited = bool(body.get("human_edited") or edited_markdown)
            return 200, self.workflow.update_candidate(candidate_id, proposal=proposal, edited_markdown=edited_markdown, human_edited=human_edited)
        raise NotFound(f"unknown route: {path}")

    def _dispatch_delete(self) -> tuple[int, Any]:
        parsed = urlsplit(self.path)
        path = parsed.path.rstrip("/")
        if path.startswith("/api/candidates/"):
            candidate_id = self._id_from_path(path, "/api/candidates/")
            self.workflow.delete_candidate(candidate_id)
            return 200, {"ok": True}
        raise NotFound(f"unknown route: {path}")

    # ------------------------------------------------------------------ #
    # Helpers
    # ------------------------------------------------------------------ #
    def _id_from_path(self, path: str, prefix: str, suffix: str = "") -> str:
        remainder = path
        if suffix and remainder.endswith(suffix):
            remainder = remainder[: -len(suffix)]
        if remainder.startswith(prefix):
            remainder = remainder[len(prefix):]
        value = unquote(remainder.strip("/"))
        if not value or "/" in value or not _SAFE_ID_RE.match(value) or ".." in value:
            raise NotFound(f"invalid id fragment in path: {path}")
        return value

    def _confined_claims_file(self, raw: Any) -> Path:
        """Resolve a client-supplied claims file, confined to the workflow directory.

        Accepts workflow-relative (``candidates/<doc>/semantic_claims.json``) or
        repo-relative (``workflow/candidates/...``) paths. Anything that resolves
        outside the workflow root (absolute paths elsewhere, ``..``, symlinks out)
        or is not a ``.json`` file is rejected.
        """
        if not isinstance(raw, str) or not raw.strip():
            raise WebappError("claims_file required")
        root = self.workflow.root.resolve()
        given = Path(raw)
        candidates = [given] if given.is_absolute() else [root / given, ROOT / given]
        for cand in candidates:
            resolved = cand.resolve()
            if resolved.is_relative_to(root) and resolved.suffix == ".json" and resolved.is_file():
                return resolved
        raise WebappError("claims_file must be an existing .json file inside the workflow directory")

    def _read_json_body(self) -> dict:
        try:
            length = int(self.headers.get("Content-Length") or "0")
        except ValueError:
            raise WebappError("invalid Content-Length") from None
        if length <= 0:
            raise WebappError("request body is required")
        if length > MAX_BODY_BYTES:
            raise WebappError(f"request body too large (max {MAX_BODY_BYTES // (1024 * 1024)} MB)")
        raw = self.rfile.read(length).decode("utf-8")
        try:
            payload = json.loads(raw)
        except json.JSONDecodeError as exc:
            raise WebappError(f"invalid JSON body: {exc}") from exc
        if not isinstance(payload, dict):
            raise WebappError("JSON body must be an object")
        return payload

    def _send_json(self, status: int, payload: Any) -> None:
        body = json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True).encode("utf-8")
        self.send_response(status)
        self._send_common_headers()
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.end_headers()
        self.wfile.write(body)

    def _send_common_headers(self) -> None:
        self.send_header("Cache-Control", "no-cache")
        self.send_header("X-Content-Type-Options", "nosniff")
        self.send_header("Referrer-Policy", "no-referrer")

    def log_message(self, format: str, *args: Any) -> None:  # noqa: A003
        return

    @staticmethod
    def _query_value(query: dict[str, list[str]], key: str) -> str | None:
        values = query.get(key)
        if not values:
            return None
        value = values[-1]
        return value if value != "" else None


def _decode_base64(value: str) -> bytes:
    import base64

    return base64.b64decode(value, validate=True)


def serve(*, host: str = "127.0.0.1", port: int = 8081, workflow: Workflow | None = None) -> _Server:
    wf = workflow or Workflow()
    handler = type("StemmaWebHandler", (_Handler,), {"workflow": wf})
    return _Server((host, port), handler)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="STEMMA ingestion/review webapp")
    parser.add_argument("--host", default="127.0.0.1",
                        help="bind address (default 127.0.0.1; use a private network like Tailscale for remote access)")
    parser.add_argument("--port", type=int, default=8081)
    parser.add_argument("--workflow", default=None, help="workflow dir (default: workflow/ under repo)")
    parser.add_argument("--open-and-exit", action="store_true", help="smoke-test then exit")
    args = parser.parse_args(argv)

    wf = Workflow(Path(args.workflow) if args.workflow else None)
    httpd = serve(host=args.host, port=args.port, workflow=wf)
    print(f"STEMMA webapp listening on http://{args.host}:{args.port} (workflow: {wf.root})", flush=True)
    if args.open_and_exit:
        print("smoke test complete", flush=True)
        httpd.server_close()
        return 0
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        httpd.server_close()
    return 0


if __name__ == "__main__":
    sys.exit(main())
