from __future__ import annotations

"""Command-line interface for the read-only STEMMA adapter."""

import argparse
import json
import sys
from typing import Any

from .client import BadRequestError, NotFoundError, Stemma
from .loader import ExportError, load_export
from .server import serve

ADAPTER_VERSION = "0.1.0"


class UsageError(Exception):
    """Raised when CLI arguments are invalid."""


class ArgumentParser(argparse.ArgumentParser):
    def error(self, message: str) -> None:
        raise UsageError(message)


def build_parser() -> ArgumentParser:
    parser = ArgumentParser(prog="stemma-adapter", description="Read-only STEMMA consumer adapter")
    parser.add_argument("--version", action="version", version=f"%(prog)s {ADAPTER_VERSION}")
    subparsers = parser.add_subparsers(dest="command", required=True)

    validate = subparsers.add_parser("validate", help="validate an export")
    validate.add_argument("export", help="path to exports/knowledge.json")

    stats = subparsers.add_parser("stats", help="print export stats")
    stats.add_argument("export", help="path to exports/knowledge.json")

    get_cmd = subparsers.add_parser("get", help="get an entity by id")
    get_cmd.add_argument("export", help="path to exports/knowledge.json")
    get_cmd.add_argument("id", help="entity id")
    get_cmd.add_argument("--include-retired", action="store_true", help="include deprecated/superseded entities")

    resolve_cmd = subparsers.add_parser("resolve", help="resolve deprecated_by chains")
    resolve_cmd.add_argument("export", help="path to exports/knowledge.json")
    resolve_cmd.add_argument("id", help="entity id")

    neighbors = subparsers.add_parser("neighbors", help="list neighboring edges")
    neighbors.add_argument("export", help="path to exports/knowledge.json")
    neighbors.add_argument("id", help="entity id")
    neighbors.add_argument("--direction", choices=["out", "in", "both"], default="both")
    neighbors.add_argument("--relation")
    neighbors.add_argument("--review")
    neighbors.add_argument("--policy", choices=["all", "reviewed", "canonical", "trusted"])
    neighbors.add_argument("--include-retired", action="store_true")
    neighbors.add_argument("--limit", type=int)

    prereqs = subparsers.add_parser("prereqs", help="compute prerequisite closure")
    prereqs.add_argument("export", help="path to exports/knowledge.json")
    prereqs.add_argument("id", help="entity id")
    prereqs.add_argument("--policy", choices=["all", "reviewed", "canonical", "trusted"])
    prereqs.add_argument("--include-retired", action="store_true")

    search = subparsers.add_parser("search", help="search entities by token")
    search.add_argument("export", help="path to exports/knowledge.json")
    search.add_argument("query", help="search query")
    search.add_argument("--domain")
    search.add_argument("--include-retired", action="store_true")
    search.add_argument("--limit", type=int)

    connections = subparsers.add_parser("connections", help="query connections")
    connections.add_argument("export", help="path to exports/knowledge.json")
    connections.add_argument("--source")
    connections.add_argument("--target")
    connections.add_argument("--relation")
    connections.add_argument("--review")
    connections.add_argument("--policy", choices=["all", "reviewed", "canonical", "trusted"])
    connections.add_argument("--limit", type=int)

    relations = subparsers.add_parser("relations", help="list relation registry semantics")
    relations.add_argument("export", help="path to exports/knowledge.json")

    relation = subparsers.add_parser("relation", help="look up one relation")
    relation.add_argument("export", help="path to exports/knowledge.json")
    relation.add_argument("name", help="relation name")

    vocabularies = subparsers.add_parser("vocabularies", help="print controlled vocabularies")
    vocabularies.add_argument("export", help="path to exports/knowledge.json")

    serve_cmd = subparsers.add_parser("serve", help="serve a local read-only JSON API")
    serve_cmd.add_argument("export", help="path to exports/knowledge.json")
    serve_cmd.add_argument("--host", default="127.0.0.1")
    serve_cmd.add_argument("--port", default=8000, type=int)

    return parser


def emit_json(payload: Any) -> None:
    sys.stdout.write(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True))
    sys.stdout.write("\n")


def entrypoint() -> None:
    raise SystemExit(main())


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    try:
        args = parser.parse_args(argv)
        if args.command == "validate":
            export = load_export(args.export)
            emit_json(
                {
                    "connection_count": export["connection_count"],
                    "entity_count": export["entity_count"],
                    "ok": True,
                    "source_count": export["source_count"],
                }
            )
            return 0

        client = Stemma.from_file(args.export)

        if args.command == "stats":
            emit_json(client.stats)
            return 0
        if args.command == "get":
            emit_json(client.entity(args.id, include_retired=args.include_retired))
            return 0
        if args.command == "resolve":
            emit_json(client.resolve(args.id))
            return 0
        if args.command == "neighbors":
            emit_json(
                client.neighbors(
                    args.id,
                    direction=args.direction,
                    relation=args.relation,
                    review=args.review,
                    policy=args.policy,
                    include_retired=args.include_retired,
                    limit=args.limit,
                )
            )
            return 0
        if args.command == "prereqs":
            emit_json(
                client.prerequisites(
                    args.id,
                    policy=args.policy,
                    include_retired=args.include_retired,
                )
            )
            return 0
        if args.command == "search":
            emit_json(
                client.search(
                    args.query,
                    domain=args.domain,
                    include_retired=args.include_retired,
                    limit=args.limit,
                )
            )
            return 0
        if args.command == "connections":
            emit_json(
                client.connections(
                    source=args.source,
                    target=args.target,
                    relation=args.relation,
                    review=args.review,
                    policy=args.policy,
                    limit=args.limit,
                )
            )
            return 0
        if args.command == "relations":
            emit_json(client.relations())
            return 0
        if args.command == "relation":
            emit_json(client.relation(args.name))
            return 0
        if args.command == "vocabularies":
            emit_json(client.vocabularies or {})
            return 0
        if args.command == "serve":
            server = serve(client, host=args.host, port=args.port)
            emit_json(
                {
                    "content_hash": client.export["content_hash"],
                    "host": server.host,
                    "port": server.port,
                    "status": "serving",
                }
            )
            try:
                server.serve_forever()
            except KeyboardInterrupt:
                pass
            finally:
                server.server_close()
            return 0

        raise UsageError(f"unknown command: {args.command}")
    except ExportError as exc:
        print(str(exc), file=sys.stderr)
        return 2
    except (BadRequestError, NotFoundError, UsageError) as exc:
        print(str(exc), file=sys.stderr)
        return 1
    except SystemExit as exc:
        return 0 if exc.code in (None, 0) else 1
