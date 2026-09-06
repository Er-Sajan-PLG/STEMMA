from __future__ import annotations

"""Read-only local JSON API for STEMMA exports."""

import json
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from typing import Any
from urllib.parse import parse_qs, unquote, urlsplit

from .client import BadRequestError, NotFoundError, Stemma
from .loader import ExportError

ADAPTER_VERSION = "0.1.0"


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
                    payload = self._dispatch()
                    self._send_json(200, payload)
                except NotFoundError as exc:
                    self._send_json(404, {"error": str(exc)})
                except (BadRequestError, ExportError, ValueError) as exc:
                    self._send_json(400, {"error": str(exc)})

            def log_message(self, format: str, *args: Any) -> None:  # noqa: A003
                return

            def _dispatch(self) -> Any:
                parsed = urlsplit(self.path)
                path = parsed.path.rstrip("/") or "/"
                query = parse_qs(parsed.query, keep_blank_values=True)

                if path == "/":
                    return {
                        "adapter": "stemma-adapter",
                        "content_hash": self.adapter_client.export["content_hash"],
                        "endpoints": [
                            "/",
                            "/v2/stats",
                            "/v2/entities",
                            "/v2/entities/{id}",
                            "/v2/resolve/{id}",
                            "/v2/connections",
                            "/v2/neighbors/{id}",
                            "/v2/prerequisites/{id}",
                            "/v2/search?q=...",
                            "/v2/external/{scheme}/{value}",
                            "/v2/relations",
                            "/v2/relations/{name}",
                            "/v2/vocabularies",
                        ],
                        "stats": self.adapter_client.stats,
                        "version": ADAPTER_VERSION,
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

                raise NotFoundError(f"unknown route: {path}")

            def _send_json(self, status: int, payload: Any) -> None:
                etag = self.adapter_client.export["content_hash"]
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
                self.send_header("Access-Control-Allow-Methods", "GET, OPTIONS")
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
