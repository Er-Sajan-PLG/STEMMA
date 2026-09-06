#!/usr/bin/env python3
"""D13: Review-aware exports — all/reviewed/canonical/proposed/rejected/trusted.

Uses graph_policy.should_include_connection as single source.
Preserves backward compatibility of exports/knowledge.json (all active).
"""
import json
import pathlib

import yaml

ROOT = pathlib.Path(__file__).resolve().parent.parent
EXPORT_BASE = ROOT / "exports" / "knowledge.json"
VERSION_SOURCE = ROOT / "schema" / "VERSION.yaml"  # ADR-0022: no version literals


def _versions() -> dict:
    return yaml.safe_load(VERSION_SOURCE.read_text(encoding="utf-8"))

from graph_policy import should_include_connection  # type: ignore
from validate import claim_signature  # type: ignore — derived claim identity (E4.3 / ADR-0026)


def _relation_registry() -> dict:
    return yaml.safe_load((ROOT / "schema" / "relation-registry.yaml").read_text(encoding="utf-8")).get("relations", {})


def _vocabularies() -> dict:
    def _load(name: str) -> dict:
        return yaml.safe_load((ROOT / "schema" / "vocabularies" / name).read_text(encoding="utf-8")) or {}

    return {
        "domains": _load("domains.yaml").get("domains", []),
        "subdomains": _load("subdomains.yaml"),
        "regimes": _load("regimes.yaml").get("regimes", []),
        "scales": _load("regimes.yaml").get("scales", []),
    }


def main():
    import yaml as _yaml

    conns = [yaml.safe_load(p.read_text()) for p in sorted((ROOT / "connections").glob("*.yaml"))]
    base = json.loads(EXPORT_BASE.read_text()) if EXPORT_BASE.exists() else {}
    versions = _versions()
    registry = _relation_registry()
    vocabularies = _vocabularies()
    for policy in ["all", "reviewed", "canonical", "trusted", "proposed", "rejected"]:
        if policy == "proposed":
            filtered = [c for c in conns if c["assertion"]["review"]["status"] == "unreviewed" and c["assertion"]["type"] == "proposed"]
        elif policy == "rejected":
            filtered = [c for c in conns if c["assertion"]["review"]["status"] == "rejected"]
        else:
            filtered = [c for c in conns if should_include_connection(c, policy)]

        out = {
            "export_version": versions["export_version"],
            "schema_version": versions["schema_version"],
            "content_hash": base.get("content_hash", "sha256:unknown"),
            "kernel_version": base.get("kernel_version"),
            "relation_registry_version": versions.get("relation_registry_version"),
            "relation_registry": registry,
            "vocabularies": vocabularies,
            "policy": policy,
            "count": len(filtered),
            # `claim_signature` is derived (ADR-0026): identity of the asserted
            # proposition, so a consumer can deduplicate claims across views.
            "connections": [
                {**c, "claim_signature": claim_signature(c)}
                for c in sorted(filtered, key=lambda x: x["id"])
            ],
        }
        path = ROOT / f"exports/knowledge.{policy}.json"
        path.write_text(json.dumps(out, indent=2, ensure_ascii=False) + "\n")
        print(f"OK: {policy} -> {len(filtered)} connections -> {path.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    import sys

    sys.exit(main())
