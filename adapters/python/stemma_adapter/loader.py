from __future__ import annotations

"""Export loader and lightweight contract validation for STEMMA consumers."""

import json
import pathlib
import re
from collections.abc import Mapping
from typing import Any

SUPPORTED_EXPORT_MAJOR = 2

SEMVER_RE = re.compile(r"^(?P<major>0|[1-9][0-9]*)\.(?P<minor>0|[1-9][0-9]*)\.(?P<patch>0|[1-9][0-9]*)$")
HASH_RE = re.compile(r"^sha256:[0-9a-f]{64}$")
ENTITY_ID_RE = re.compile(r"^stemma:[a-z][a-z0-9-]*\.[a-z0-9][a-z0-9-]*$")
CONNECTION_ID_RE = re.compile(r"^stemma:conn\.[0-9]{6}$")
SOURCE_ID_RE = re.compile(r"^stemma:src\.[a-z0-9][a-z0-9-]*$")

TOP_LEVEL_REQUIRED = (
    "export_version",
    "schema_version",
    "content_hash",
    "source",
    "entity_count",
    "connection_count",
    "source_count",
    "entities",
    "connections",
    "sources",
)
ENTITY_REQUIRED = ("id", "type", "name", "domain", "status", "definition", "provenance")
CONNECTION_REQUIRED = ("id", "type", "source", "relation", "target", "assertion", "provenance")
SOURCE_REQUIRED = ("id", "type", "citation")


class ExportError(ValueError):
    """Raised when an export cannot be loaded or fails validation."""


def _require_mapping(value: Any, label: str) -> dict[str, Any]:
    if not isinstance(value, Mapping):
        raise ExportError(f"{label} must be an object")
    return dict(value)


def _require_list(value: Any, label: str) -> list[Any]:
    if not isinstance(value, list):
        raise ExportError(f"{label} must be an array")
    return value


def _require_members(obj: Mapping[str, Any], members: tuple[str, ...] | list[str], label: str) -> None:
    missing = [member for member in members if member not in obj]
    if missing:
        missing_csv = ", ".join(missing)
        raise ExportError(f"{label} missing required member(s): {missing_csv}")


def _require_semver(value: Any, label: str) -> tuple[int, int, int]:
    if not isinstance(value, str):
        raise ExportError(f"{label} must be a semver string")
    match = SEMVER_RE.fullmatch(value)
    if not match:
        raise ExportError(f"{label} must match MAJOR.MINOR.PATCH")
    return (int(match.group("major")), int(match.group("minor")), int(match.group("patch")))


def _require_non_negative_int(value: Any, label: str) -> int:
    if not isinstance(value, int) or isinstance(value, bool) or value < 0:
        raise ExportError(f"{label} must be a non-negative integer")
    return value


def _require_pattern(value: Any, pattern: re.Pattern[str], label: str) -> str:
    if not isinstance(value, str) or not pattern.fullmatch(value):
        raise ExportError(f"{label} has invalid format: {value!r}")
    return value


def _read_json(path: pathlib.Path) -> dict[str, Any]:
    try:
        raw = path.read_text(encoding="utf-8")
    except OSError as exc:
        raise ExportError(f"unable to read export {path}: {exc}") from exc
    try:
        data = json.loads(raw)
    except json.JSONDecodeError as exc:
        raise ExportError(f"invalid JSON in export {path}: {exc}") from exc
    return _require_mapping(data, "export")


def load_export(path_or_dict: str | pathlib.Path | Mapping[str, Any]) -> dict[str, Any]:
    """Load and validate a full STEMMA export.

    The adapter deliberately validates the consumer-facing contract itself so a
    consumer can fail closed on malformed or unsupported exports without
    depending on the producer repository's validator stack.
    """

    if isinstance(path_or_dict, (str, pathlib.Path)):
        export = _read_json(pathlib.Path(path_or_dict))
    elif isinstance(path_or_dict, Mapping):
        export = _require_mapping(path_or_dict, "export")
    else:
        raise ExportError("export must be a filesystem path or a mapping")

    _require_members(export, TOP_LEVEL_REQUIRED, "export")

    export_version = _require_semver(export["export_version"], "export.export_version")
    _require_semver(export["schema_version"], "export.schema_version")
    kernel_version = export.get("kernel_version")
    if kernel_version is not None:
        _require_semver(kernel_version, "export.kernel_version")
    if export_version[0] != SUPPORTED_EXPORT_MAJOR:
        raise ExportError(
            "unsupported export major version "
            f"{export_version[0]}; supported major is {SUPPORTED_EXPORT_MAJOR}"
        )

    if not isinstance(export["source"], str) or not export["source"].strip():
        raise ExportError("export.source must be a non-empty string")
    if not isinstance(export["content_hash"], str) or not HASH_RE.fullmatch(export["content_hash"]):
        raise ExportError("export.content_hash must match sha256:<64 lowercase hex>")

    entity_count = _require_non_negative_int(export["entity_count"], "export.entity_count")
    connection_count = _require_non_negative_int(export["connection_count"], "export.connection_count")
    source_count = _require_non_negative_int(export["source_count"], "export.source_count")

    entities = _require_list(export["entities"], "export.entities")
    connections = _require_list(export["connections"], "export.connections")
    sources = _require_list(export["sources"], "export.sources")

    if entity_count != len(entities):
        raise ExportError(
            f"export.entity_count={entity_count} does not match len(entities)={len(entities)}"
        )
    if connection_count != len(connections):
        raise ExportError(
            "export.connection_count="
            f"{connection_count} does not match len(connections)={len(connections)}"
        )
    if source_count != len(sources):
        raise ExportError(
            f"export.source_count={source_count} does not match len(sources)={len(sources)}"
        )

    entity_ids: set[str] = set()
    source_ids: set[str] = set()
    connection_ids: set[str] = set()

    for index, entity in enumerate(entities):
        entity_obj = _require_mapping(entity, f"export.entities[{index}]")
        _require_members(entity_obj, ENTITY_REQUIRED, f"export.entities[{index}]")
        entity_id = _require_pattern(entity_obj["id"], ENTITY_ID_RE, f"export.entities[{index}].id")
        if entity_id in entity_ids:
            raise ExportError(f"duplicate entity id: {entity_id}")
        entity_ids.add(entity_id)
        deprecated_by = entity_obj.get("deprecated_by")
        if deprecated_by is not None:
            _require_pattern(
                deprecated_by,
                ENTITY_ID_RE,
                f"export.entities[{index}].deprecated_by",
            )
        aliases = entity_obj.get("aliases")
        if aliases is not None:
            if not isinstance(aliases, list):
                raise ExportError(f"export.entities[{index}].aliases must be an array")
            for alias_index, alias in enumerate(aliases):
                alias_id = _require_pattern(
                    alias,
                    ENTITY_ID_RE,
                    f"export.entities[{index}].aliases[{alias_index}]",
                )
                if alias_id == entity_id:
                    raise ExportError(f"export.entities[{index}].aliases must not repeat its own id")

    for index, source in enumerate(sources):
        source_obj = _require_mapping(source, f"export.sources[{index}]")
        _require_members(source_obj, SOURCE_REQUIRED, f"export.sources[{index}]")
        source_id = _require_pattern(source_obj["id"], SOURCE_ID_RE, f"export.sources[{index}].id")
        if source_id in source_ids:
            raise ExportError(f"duplicate source id: {source_id}")
        source_ids.add(source_id)

    # ADR-0032 / export v2.1: if the producer publishes its relation registry,
    # consumers fail closed on any connection whose relation is not declared.
    relation_registry = export.get("relation_registry")
    if relation_registry is not None:
        if not isinstance(relation_registry, Mapping):
            raise ExportError("export.relation_registry must be an object")
        if not isinstance(export.get("relation_registry_version"), str):
            raise ExportError("export.relation_registry_version must be a string when relation_registry is present")
        _require_semver(
            export["relation_registry_version"],
            "export.relation_registry_version",
        )
        known_relations = set(relation_registry)

    for index, connection in enumerate(connections):
        conn_obj = _require_mapping(connection, f"export.connections[{index}]")
        _require_members(conn_obj, CONNECTION_REQUIRED, f"export.connections[{index}]")
        conn_id = _require_pattern(conn_obj["id"], CONNECTION_ID_RE, f"export.connections[{index}].id")
        if conn_id in connection_ids:
            raise ExportError(f"duplicate connection id: {conn_id}")
        connection_ids.add(conn_id)

        relation = conn_obj.get("relation")
        if not isinstance(relation, str) or not relation:
            raise ExportError(f"export.connections[{index}].relation must be a non-empty string")
        if relation_registry is not None and relation not in known_relations:
            raise ExportError(
                f"export.connections[{index}].relation '{relation}' is not declared in "
                "export.relation_registry; refusing to load unknown relation"
            )

        source_id = _require_pattern(conn_obj["source"], ENTITY_ID_RE, f"export.connections[{index}].source")
        target_id = _require_pattern(conn_obj["target"], ENTITY_ID_RE, f"export.connections[{index}].target")
        if source_id not in entity_ids:
            raise ExportError(
                f"export.connections[{index}].source refers to unknown entity {source_id}"
            )
        if target_id not in entity_ids:
            raise ExportError(
                f"export.connections[{index}].target refers to unknown entity {target_id}"
            )

        assertion = _require_mapping(conn_obj["assertion"], f"export.connections[{index}].assertion")
        _require_members(assertion, ("status", "type", "review"), f"export.connections[{index}].assertion")
        review = _require_mapping(assertion["review"], f"export.connections[{index}].assertion.review")
        _require_members(review, ("status",), f"export.connections[{index}].assertion.review")
        provenance = _require_mapping(
            conn_obj["provenance"],
            f"export.connections[{index}].provenance",
        )
        _require_members(
            provenance,
            ("asserted_by", "generated_by", "method"),
            f"export.connections[{index}].provenance",
        )

        lifecycle = conn_obj.get("lifecycle")
        if lifecycle is not None:
            lifecycle_obj = _require_mapping(lifecycle, f"export.connections[{index}].lifecycle")
            replaced_by = lifecycle_obj.get("replaced_by")
            if replaced_by is not None:
                _require_pattern(
                    replaced_by,
                    CONNECTION_ID_RE,
                    f"export.connections[{index}].lifecycle.replaced_by",
                )

        evidence = conn_obj.get("evidence", [])
        if evidence is None:
            raise ExportError(f"export.connections[{index}].evidence must be an array or absent")
        evidence_list = _require_list(evidence, f"export.connections[{index}].evidence")
        for evidence_index, evidence_item in enumerate(evidence_list):
            evidence_obj = _require_mapping(
                evidence_item,
                f"export.connections[{index}].evidence[{evidence_index}]",
            )
            source_ref = evidence_obj.get("source_ref")
            if source_ref is not None:
                source_ref_id = _require_pattern(
                    source_ref,
                    SOURCE_ID_RE,
                    f"export.connections[{index}].evidence[{evidence_index}].source_ref",
                )
                if source_ref_id not in source_ids:
                    raise ExportError(
                        "export.connections"
                        f"[{index}].evidence[{evidence_index}].source_ref refers to unknown source "
                        f"{source_ref_id}"
                    )

    for index, entity in enumerate(entities):
        deprecated_by = entity.get("deprecated_by")
        if deprecated_by is not None and deprecated_by not in entity_ids:
            raise ExportError(
                f"export.entities[{index}].deprecated_by refers to unknown entity {deprecated_by}"
            )

    for index, connection in enumerate(connections):
        lifecycle = connection.get("lifecycle") or {}
        replaced_by = lifecycle.get("replaced_by")
        if replaced_by is not None and replaced_by not in connection_ids:
            raise ExportError(
                f"export.connections[{index}].lifecycle.replaced_by refers to unknown connection {replaced_by}"
            )

    return export
