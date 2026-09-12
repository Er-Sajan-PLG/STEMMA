#!/usr/bin/env python3
"""STEMMA ingestion/review webapp server.

A simple, dependency-free HTTP server that exposes the human-in-the-loop
ingestion workflow. It serves a single-page UI and a small JSON API over
``webapp.core.Workflow``. It never writes canonical knowledge.

Run:
    python3 webapp/server.py --host 0.0.0.0 --port 8081
"""
from __future__ import annotations

import argparse
import json
import sys
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any
from urllib.parse import parse_qs, unquote, urlsplit

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


class _Server(ThreadingHTTPServer):
    daemon_threads = True


class _Handler(BaseHTTPRequestHandler):
    workflow: Workflow

    def do_OPTIONS(self) -> None:  # noqa: N802
        self.send_response(204)
        self._send_common_headers()
        self.end_headers()

    def do_GET(self) -> None:  # noqa: N802
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
        safe = Path(name).name
        path = STATIC_DIR / safe
        if not path.exists():
            raise NotFound(f"static asset not found: {name}")
        suffix = path.suffix.lower()
        content_type = {
            ".html": "text/html; charset=utf-8",
            ".css": "text/css; charset=utf-8",
            ".js": "application/javascript; charset=utf-8",
            ".json": "application/json; charset=utf-8",
        }.get(suffix, "application/octet-stream")
        return path.read_bytes(), content_type

    def do_POST(self) -> None:  # noqa: N802
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
        if path == "/api/documents":
            return 200, {"documents": wf.list_documents()}
        if path == "/api/candidates":
            doc_id = self._query_value(query, "doc_id")
            return 200, {"candidates": wf.list_candidates(doc_id)}
        if path == "/api/proposals":
            return 200, {"proposals": wf.list_proposals()}
        if path == "/api/audit":
            return 200, {"events": wf.read_audit()}
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
        if path.endswith("/extract"):
            doc_id = self._id_from_path(path, "/api/documents/", suffix="/extract")
            return 200, wf.extract_document(doc_id)
        if path.endswith("/generate"):
            doc_id = self._id_from_path(path, "/api/documents/", suffix="/generate")
            body = self._read_json_body()
            return 200, wf.generate_candidates(doc_id, target_kinds=body.get("target_kinds"))
        if path.endswith("/stage"):
            candidate_id = self._id_from_path(path, "/api/candidates/", suffix="/stage")
            body = self._read_json_body()
            reviewer = str(body.get("reviewer") or "")
            if not reviewer:
                raise WebappError("reviewer is required to stage a proposal")
            return 201, wf.stage_candidate(candidate_id, reviewer=reviewer, note=str(body.get("note") or ""))
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
            return 200, self.workflow.update_candidate(candidate_id, proposal=proposal)
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
        if not value or "/" in value:
            raise NotFound(f"invalid id fragment in path: {path}")
        return value

    def _read_json_body(self) -> dict:
        length = int(self.headers.get("Content-Length") or "0")
        if length <= 0:
            raise WebappError("request body is required")
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
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, PATCH, DELETE, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.send_header("Cache-Control", "no-cache")

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


def serve(*, host: str = "0.0.0.0", port: int = 8081, workflow: Workflow | None = None) -> _Server:
    wf = workflow or Workflow()
    handler = type("StemmaWebHandler", (_Handler,), {"workflow": wf})
    return _Server((host, port), handler)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="STEMMA ingestion/review webapp")
    parser.add_argument("--host", default="0.0.0.0")
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
