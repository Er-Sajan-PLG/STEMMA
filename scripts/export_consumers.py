#!/usr/bin/env python3
"""Consumer-shaped exports — one deterministic bundle per consumer in
schema/consumer-registry.yaml (LearningHub, PROFESSOR-J, STEMMA Explorer, general).

Each bundle is a *valid STEMMA export* (it loads with `stemma_adapter.load_export`)
that has been narrowed to one consumer's profile. Published as part of the release
file contract (ADR-0054). Rules:

- Versions come from schema/VERSION.yaml (ADR-0022) and must equal the base
  export's; the base `content_hash` identifies the canonical snapshot the bundle
  was derived from, and `payload_sha256` identifies the bundle's own payload.
- Trust tiers (review_policy) apply to BOTH axes:
    entity status        all: any · reviewed/trusted: human_reviewed|canonical · canonical: canonical
    connection review    graph_policy.should_include_connection (same single source
                         as exports/knowledge.<policy>.json); `trusted` additionally
                         requires LLM-asserted connections to be canonical.
- A relational connection is kept only if both endpoints survive; a valued claim
  (ADR-0045, target=null) is kept if its source entity survives.
- Deterministic: sorted by id, no timestamps; `--check` fails if committed bundles
  are stale (used by CI).
- No embeddings: derived vectors are a consumer concern (ADR-0054).

Usage:
  python3 scripts/export_consumers.py --all              # write all bundles
  python3 scripts/export_consumers.py --consumer learninghub
  python3 scripts/export_consumers.py --all --check      # CI: verify committed bundles are fresh
"""
from __future__ import annotations

import argparse
import hashlib
import json
import pathlib
import sys
from typing import Any

import yaml

ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))
from graph_policy import should_include_connection  # noqa: E402  (single policy source)

EXPORT_PATH = ROOT / "exports" / "knowledge.json"
VERSION_PATH = ROOT / "schema" / "VERSION.yaml"
CONSUMER_REGISTRY_PATH = ROOT / "schema" / "consumer-registry.yaml"
OUT_DIR = ROOT / "exports" / "consumers"

POLICIES = ("all", "reviewed", "trusted", "canonical")
ENTITY_STATUSES_FOR_POLICY: dict[str, set[str] | None] = {
    "all": None,  # no entity-status filter
    "reviewed": {"human_reviewed", "canonical"},
    "trusted": {"human_reviewed", "canonical"},
    "canonical": {"canonical"},
}
# Copied verbatim from the base export so each bundle is self-describing.
PASSTHROUGH_KEYS = ("source", "kernel_version", "relation_registry_version", "relation_registry", "vocabularies")


class ConsumerExportError(RuntimeError):
    pass


def load_registry() -> dict[str, dict[str, Any]]:
    data = yaml.safe_load(CONSUMER_REGISTRY_PATH.read_text(encoding="utf-8")) or {}
    consumers = data.get("consumers") or {}
    if not consumers:
        raise ConsumerExportError(f"no consumers defined in {CONSUMER_REGISTRY_PATH.relative_to(ROOT)}")
    return consumers


def _as_filter(value: Any) -> set[str] | None:
    """Registry fields are either 'all' / missing (no filter) or a list."""
    if value in (None, "all", []):
        return None
    if isinstance(value, list):
        return set(value)
    raise ConsumerExportError(f"expected 'all' or a list, got {value!r}")


def entity_passes(entity: dict[str, Any], profile: dict[str, Any], policy: str) -> bool:
    domains = _as_filter(profile.get("domains"))
    subdomains = _as_filter(profile.get("subdomains"))
    types = _as_filter(profile.get("entity_types"))
    statuses = ENTITY_STATUSES_FOR_POLICY[policy]
    if domains is not None and entity.get("domain") not in domains:
        return False
    if subdomains is not None and entity.get("subdomain") not in subdomains:
        return False
    if types is not None and entity.get("type") not in types:
        return False
    if statuses is not None and entity.get("status") not in statuses:
        return False
    return True


def connection_passes(conn: dict[str, Any], kept_ids: set[str], policy: str) -> bool:
    if not should_include_connection(conn, policy):
        return False
    if conn.get("source") not in kept_ids:
        return False
    target = conn.get("target")
    if target is None:  # ADR-0045 valued claim: only the source must survive
        return conn.get("value") is not None
    return target in kept_ids


def _payload_sha256(entities: list, connections: list, sources: list) -> str:
    canonical = json.dumps(
        {"entities": entities, "connections": connections, "sources": sources},
        sort_keys=True, ensure_ascii=False, separators=(",", ":"),
    )
    return "sha256:" + hashlib.sha256(canonical.encode("utf-8")).hexdigest()


def build_consumer_export(consumer_id: str, profile: dict[str, Any], base: dict[str, Any],
                          versions: dict[str, Any], review_policy: str | None = None) -> dict[str, Any]:
    policy = review_policy or profile.get("review_policy") or "all"
    if policy not in POLICIES:
        raise ConsumerExportError(f"{consumer_id}: unknown review_policy {policy!r} (expected one of {POLICIES})")
    for key in ("export_version", "schema_version"):
        if base.get(key) != versions.get(key):
            raise ConsumerExportError(
                f"exports/knowledge.json {key}={base.get(key)!r} != schema/VERSION.yaml {versions.get(key)!r}; "
                "regenerate the base export first (python3 scripts/validate.py)"
            )

    entities = sorted((e for e in base["entities"] if entity_passes(e, profile, policy)), key=lambda e: e["id"])
    kept_ids = {e["id"] for e in entities}
    connections = sorted((c for c in base["connections"] if connection_passes(c, kept_ids, policy)),
                         key=lambda c: c["id"])
    referenced: set[str] = set()
    for e in entities:
        referenced.update(e.get("source_refs") or [])
    for c in connections:
        for ev in c.get("evidence") or []:
            if ev.get("source_ref"):
                referenced.add(ev["source_ref"])
    sources = sorted((s for s in base["sources"] if s.get("id") in referenced), key=lambda s: s["id"])

    bundle: dict[str, Any] = {
        "export_version": versions["export_version"],
        "schema_version": versions["schema_version"],
        "content_hash": base["content_hash"],  # canonical snapshot this bundle derives from
        "payload_sha256": _payload_sha256(entities, connections, sources),
        "consumer": consumer_id,
        "consumer_profile": {
            "label": profile.get("label"),
            "domains": profile.get("domains", "all"),
            "subdomains": profile.get("subdomains", "all"),
            "entity_types": profile.get("entity_types", "all"),
            "review_policy": policy,
            "recommended_embedding_model": profile.get("embedding_model"),
        },
    }
    for key in PASSTHROUGH_KEYS:
        if key in base:
            bundle[key] = base[key]
    bundle.update({
        "entity_count": len(entities),
        "connection_count": len(connections),
        "source_count": len(sources),
        "entities": entities,
        "connections": connections,
        "sources": sources,
    })
    return bundle


def render(bundle: dict[str, Any]) -> str:
    return json.dumps(bundle, indent=2, ensure_ascii=False) + "\n"


def bundle_path(consumer_id: str) -> pathlib.Path:
    return OUT_DIR / consumer_id / f"knowledge.{consumer_id}.json"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="STEMMA consumer-shaped exports (release file contract, ADR-0054)")
    parser.add_argument("--consumer", help="consumer id from schema/consumer-registry.yaml")
    parser.add_argument("--all", action="store_true", help="every consumer in the registry")
    parser.add_argument("--review-policy", choices=POLICIES, help="override the registry policy (not with --check)")
    parser.add_argument("--check", action="store_true", help="verify committed bundles are fresh; write nothing")
    parser.add_argument("--format", choices=["json"], default="json", help=argparse.SUPPRESS)  # legacy flag; json only
    args = parser.parse_args(argv)

    try:
        registry = load_registry()
        if args.all:
            ids = sorted(registry)
        elif args.consumer:
            if args.consumer not in registry:
                raise ConsumerExportError(f"unknown consumer {args.consumer!r}; known: {', '.join(sorted(registry))}")
            ids = [args.consumer]
        else:
            parser.print_help()
            return 1
        if args.check and args.review_policy:
            raise ConsumerExportError("--check verifies registry policies; do not combine with --review-policy")

        base = json.loads(EXPORT_PATH.read_text(encoding="utf-8"))
        versions = yaml.safe_load(VERSION_PATH.read_text(encoding="utf-8"))
        stale: list[str] = []
        for cid in ids:
            bundle = build_consumer_export(cid, registry[cid], base, versions, args.review_policy)
            text = render(bundle)
            path = bundle_path(cid)
            rel = path.relative_to(ROOT)
            if args.check:
                if not path.exists() or path.read_text(encoding="utf-8") != text:
                    stale.append(str(rel))
                continue
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(text, encoding="utf-8")
            print(f"OK: {rel} — policy {bundle['consumer_profile']['review_policy']}, "
                  f"{bundle['entity_count']} entities, {bundle['connection_count']} connections, "
                  f"{bundle['source_count']} sources, {bundle['payload_sha256'][:19]}…")
        if stale:
            print("FAIL: consumer exports are stale or missing — run python3 scripts/export_consumers.py --all",
                  file=sys.stderr)
            for rel in stale:
                print(f"  - {rel}", file=sys.stderr)
            return 1
        if args.check:
            print(f"OK: {len(ids)} consumer export(s) fresh")
        return 0
    except ConsumerExportError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
