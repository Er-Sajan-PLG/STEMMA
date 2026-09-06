from __future__ import annotations

"""Read-only Python client for STEMMA exports."""

import re
from collections import defaultdict
from typing import Any

from .loader import ExportError, load_export
from .policies import POLICIES, should_include_connection

RETIRED_ENTITY_STATUSES = {"deprecated", "superseded"}
PREREQUISITE_RELATIONS = {
    "requires",
    "mathematically_requires",
    "logically_requires",
    "depends_on",
}
TOKEN_RE = re.compile(r"[a-z0-9]+")


class NotFoundError(KeyError):
    """Raised when a requested entity, source, or connection cannot be found."""


class BadRequestError(ValueError):
    """Raised when query parameters are invalid."""


class Stemma:
    """A zero-dependency, read-only adapter over a validated STEMMA export."""

    def __init__(self, export: dict[str, Any]) -> None:
        self.export = export
        self.entities_by_id: dict[str, dict[str, Any]] = {
            entity["id"]: entity for entity in export["entities"]
        }
        self.all_connections: list[dict[str, Any]] = sorted(
            export["connections"],
            key=lambda item: item["id"],
        )
        self.sources_by_id: dict[str, dict[str, Any]] = {
            source["id"]: source for source in export["sources"]
        }

        self._sorted_entity_ids = sorted(self.entities_by_id)
        self._connections_by_source: dict[str, list[dict[str, Any]]] = defaultdict(list)
        self._connections_by_target: dict[str, list[dict[str, Any]]] = defaultdict(list)
        self._external_id_index: dict[tuple[str, str], list[str]] = defaultdict(list)

        self.relation_registry: dict[str, Any] | None = export.get("relation_registry")
        self.relation_registry_version: str | None = export.get("relation_registry_version")
        if self.relation_registry is not None and not isinstance(self.relation_registry, dict):
            raise ExportError("export.relation_registry must be an object")
        self.vocabularies: dict[str, Any] | None = export.get("vocabularies")
        if self.vocabularies is not None and not isinstance(self.vocabularies, dict):
            raise ExportError("export.vocabularies must be an object")
        self._relation_names = sorted(self.relation_registry) if self.relation_registry else []

        for connection in self.all_connections:
            self._connections_by_source[connection["source"]].append(connection)
            self._connections_by_target[connection["target"]].append(connection)

        for entity in export["entities"]:
            external_ids = entity.get("external_ids") or {}
            if not isinstance(external_ids, dict):
                continue
            for scheme, raw_value in external_ids.items():
                values = raw_value if isinstance(raw_value, list) else [raw_value]
                for value in values:
                    if isinstance(value, str):
                        self._external_id_index[(scheme, value)].append(entity["id"])

    @classmethod
    def from_file(cls, path: str) -> "Stemma":
        return cls(load_export(path))

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "Stemma":
        return cls(load_export(data))

    @property
    def stats(self) -> dict[str, Any]:
        retired_entities = sum(
            1 for entity in self.entities_by_id.values() if self._is_retired_entity(entity)
        )
        active_connections = sum(
            1
            for conn in self.all_connections
            if self._is_active_connection(conn)
            and conn.get("assertion", {}).get("review", {}).get("status") != "rejected"
        )
        rejected_connections = sum(
            1
            for conn in self.all_connections
            if conn.get("assertion", {}).get("review", {}).get("status") == "rejected"
        )
        return {
            "active_connection_count": active_connections,
            "connection_count": self.export["connection_count"],
            "content_hash": self.export["content_hash"],
            "entity_count": self.export["entity_count"],
            "export_version": self.export["export_version"],
            "kernel_version": self.export.get("kernel_version"),
            "rejected_connection_count": rejected_connections,
            "relation_registry_version": self.relation_registry_version,
            "retired_entity_count": retired_entities,
            "schema_version": self.export["schema_version"],
            "source_count": self.export["source_count"],
        }

    def relations(self) -> dict[str, dict[str, Any]]:
        """Return every relation descriptor published in the export.

        Raises ExportError when the producer did not publish a relation
        registry (pre-2.1 exports). Use relation(name) for single lookups.
        """
        if self.relation_registry is None:
            raise ExportError(
                "export does not include a relation registry; re-export with contract v2.1 "
                "or run against a registry-publishing producer"
            )
        return dict(self.relation_registry)

    def relation(self, name: str) -> dict[str, Any]:
        """Return one relation descriptor.

        When a registry is present, an unknown name is a client contract
        violation (fail closed). When no registry is present, lookup is
        unavailable and ExportError is raised.
        """
        if self.relation_registry is None:
            raise ExportError(
                "export does not include a relation registry; re-export with contract v2.1 "
                "or run against a registry-publishing producer"
            )
        descriptor = self.relation_registry.get(name)
        if descriptor is None:
            raise BadRequestError(f"unknown relation: {name}")
        return descriptor

    def entity(self, entity_id: str, *, include_retired: bool = False) -> dict[str, Any]:
        entity = self.entities_by_id.get(entity_id)
        if entity is None:
            raise NotFoundError(f"unknown entity id: {entity_id}")
        if self._is_retired_entity(entity) and not include_retired:
            raise NotFoundError(f"entity is retired and hidden by default: {entity_id}")
        return entity

    def entities(
        self,
        *,
        domain: str | None = None,
        type: str | None = None,
        status: str | None = None,
        include_retired: bool = False,
        limit: int | None = None,
    ) -> list[dict[str, Any]]:
        limit = self._normalize_limit(limit)
        explicit_retired_status = status in RETIRED_ENTITY_STATUSES
        results: list[dict[str, Any]] = []
        for entity_id in self._sorted_entity_ids:
            entity = self.entities_by_id[entity_id]
            if self._is_retired_entity(entity) and not include_retired and not explicit_retired_status:
                continue
            if domain is not None and entity.get("domain") != domain:
                continue
            if type is not None and entity.get("type") != type:
                continue
            if status is not None and entity.get("status") != status:
                continue
            results.append(entity)
            if limit is not None and len(results) >= limit:
                break
        return results

    def resolve(self, entity_id: str) -> dict[str, Any]:
        if entity_id not in self.entities_by_id:
            raise NotFoundError(f"unknown entity id: {entity_id}")
        chain: list[str] = []
        seen: set[str] = set()
        current_id = entity_id
        while True:
            if current_id in seen:
                raise ExportError(f"deprecated_by cycle detected while resolving {entity_id}")
            seen.add(current_id)
            entity = self.entities_by_id[current_id]
            chain.append(current_id)
            next_id = entity.get("deprecated_by")
            if not next_id or next_id == current_id:
                return {
                    "chain": chain,
                    "entity": entity,
                    "requested": entity_id,
                    "resolved": current_id,
                }
            if next_id not in self.entities_by_id:
                raise ExportError(
                    f"deprecated_by points to unknown entity {next_id} while resolving {entity_id}"
                )
            current_id = next_id

    def by_external_id(
        self,
        scheme: str,
        value: str,
        *,
        include_retired: bool = False,
    ) -> dict[str, Any]:
        matches = self._external_id_index.get((scheme, value), [])
        if not matches:
            raise NotFoundError(f"no entity found for external id {scheme}/{value}")
        visible_matches = [
            self.entities_by_id[entity_id]
            for entity_id in sorted(matches)
            if include_retired or not self._is_retired_entity(self.entities_by_id[entity_id])
        ]
        if not visible_matches:
            raise NotFoundError(f"external id {scheme}/{value} resolves only to retired entities")
        if len(visible_matches) > 1:
            raise BadRequestError(f"external id {scheme}/{value} is ambiguous")
        return visible_matches[0]

    def connections(
        self,
        *,
        source: str | None = None,
        target: str | None = None,
        relation: str | None = None,
        review: str | None = None,
        policy: str | None = None,
        limit: int | None = None,
    ) -> list[dict[str, Any]]:
        limit = self._normalize_limit(limit)
        self._validate_policy(policy)
        candidates = self._candidate_connections(source=source, target=target)
        results: list[dict[str, Any]] = []
        for connection in candidates:
            if not self._connection_visible(connection, policy=policy, review=review):
                continue
            if relation is not None and connection.get("relation") != relation:
                continue
            results.append(connection)
            if limit is not None and len(results) >= limit:
                break
        return results

    def neighbors(
        self,
        entity_id: str,
        *,
        direction: str = "both",
        relation: str | None = None,
        review: str | None = None,
        policy: str | None = None,
        include_retired: bool = False,
        limit: int | None = None,
    ) -> list[dict[str, Any]]:
        limit = self._normalize_limit(limit)
        self._validate_policy(policy)
        if direction not in {"out", "in", "both"}:
            raise BadRequestError("direction must be one of: out, in, both")
        self.entity(entity_id, include_retired=include_retired)

        edges: list[dict[str, Any]] = []
        seen: set[tuple[str, str]] = set()

        if direction in {"out", "both"}:
            for connection in self._connections_by_source.get(entity_id, []):
                edge = self._neighbor_edge(
                    connection,
                    entity_id=entity_id,
                    edge_direction="out",
                    relation=relation,
                    review=review,
                    policy=policy,
                    include_retired=include_retired,
                )
                if edge is not None:
                    key = (edge["connection_id"], edge["direction"])
                    if key not in seen:
                        seen.add(key)
                        edges.append(edge)

        if direction in {"in", "both"}:
            for connection in self._connections_by_target.get(entity_id, []):
                edge_direction = "in"
                if connection["source"] == entity_id and connection["target"] == entity_id:
                    edge_direction = "both"
                edge = self._neighbor_edge(
                    connection,
                    entity_id=entity_id,
                    edge_direction=edge_direction,
                    relation=relation,
                    review=review,
                    policy=policy,
                    include_retired=include_retired,
                )
                if edge is not None:
                    key = (edge["connection_id"], edge["direction"])
                    if key not in seen:
                        seen.add(key)
                        edges.append(edge)

        edges.sort(key=lambda item: (item["connection_id"], item["direction"], item["other_entity"]["id"]))
        if limit is not None:
            return edges[:limit]
        return edges

    def prerequisites(
        self,
        entity_id: str,
        *,
        policy: str | None = None,
        include_retired: bool = False,
    ) -> list[dict[str, Any]]:
        self._validate_policy(policy)
        self.entity(entity_id, include_retired=include_retired)

        collected: dict[str, dict[str, Any]] = {}
        seen: set[str] = {entity_id}
        stack = [entity_id]

        while stack:
            current_id = stack.pop()
            for connection in self.connections(source=current_id, policy=policy):
                if connection.get("relation") not in PREREQUISITE_RELATIONS:
                    continue
                target_id = connection["target"]
                if target_id in seen:
                    continue
                target_entity = self.entities_by_id[target_id]
                if self._is_retired_entity(target_entity) and not include_retired:
                    continue
                seen.add(target_id)
                collected[target_id] = target_entity
                stack.append(target_id)

        return [collected[target_id] for target_id in sorted(collected)]

    def search(
        self,
        query: str,
        *,
        domain: str | None = None,
        include_retired: bool = False,
        limit: int | None = None,
    ) -> list[dict[str, Any]]:
        limit = self._normalize_limit(limit)
        normalized_query = self._normalize_text(query)
        if not normalized_query:
            raise BadRequestError("query must not be empty")

        query_tokens = set(self._tokenize(query))
        results: list[tuple[int, str, dict[str, Any]]] = []

        for entity in self.entities(
            domain=domain,
            include_retired=include_retired,
        ):
            name = self._normalize_text(entity.get("name", ""))
            definition = self._normalize_text(entity.get("definition", ""))
            name_tokens = set(self._tokenize(entity.get("name", "")))
            definition_tokens = set(self._tokenize(entity.get("definition", "")))

            rank: int | None = None
            if name.startswith(normalized_query):
                rank = 0
            elif normalized_query in name or query_tokens.issubset(name_tokens):
                rank = 1
            elif normalized_query in definition or query_tokens.issubset(definition_tokens):
                rank = 2

            if rank is not None:
                results.append((rank, entity["id"], entity))

        results.sort(key=lambda item: (item[0], item[1]))
        entities = [entity for _, _, entity in results]
        if limit is not None:
            return entities[:limit]
        return entities

    @staticmethod
    def _is_retired_entity(entity: dict[str, Any]) -> bool:
        return entity.get("status") in RETIRED_ENTITY_STATUSES

    @staticmethod
    def _is_active_connection(connection: dict[str, Any]) -> bool:
        return connection.get("assertion", {}).get("status") == "active"

    @staticmethod
    def _tokenize(value: str) -> list[str]:
        return TOKEN_RE.findall(value.casefold())

    @classmethod
    def _normalize_text(cls, value: str) -> str:
        return " ".join(cls._tokenize(value))

    @staticmethod
    def _normalize_limit(limit: int | None) -> int | None:
        if limit is None:
            return None
        if not isinstance(limit, int) or isinstance(limit, bool) or limit <= 0:
            raise BadRequestError("limit must be a positive integer")
        return limit

    @staticmethod
    def _entity_summary(entity: dict[str, Any]) -> dict[str, Any]:
        return {
            "domain": entity.get("domain"),
            "id": entity.get("id"),
            "name": entity.get("name"),
            "status": entity.get("status"),
            "type": entity.get("type"),
        }

    @staticmethod
    def _validate_policy(policy: str | None) -> None:
        if policy is not None and policy not in POLICIES:
            raise BadRequestError(f"policy must be one of: {', '.join(sorted(POLICIES))}")

    def _connection_visible(
        self,
        connection: dict[str, Any],
        *,
        policy: str | None,
        review: str | None,
    ) -> bool:
        if policy is None:
            # Default consumer view = active and not rejected (ADR-0031). An
            # explicit review filter overrides the rejected exclusion so the
            # audit set remains queryable.
            if not self._is_active_connection(connection):
                return False
            if review is None and connection.get("assertion", {}).get("review", {}).get("status") == "rejected":
                return False
        elif not should_include_connection(connection, policy):
            return False
        if review is not None and connection.get("assertion", {}).get("review", {}).get("status") != review:
            return False
        return True

    def _candidate_connections(
        self,
        *,
        source: str | None,
        target: str | None,
    ) -> list[dict[str, Any]]:
        if source is not None and target is not None:
            return [
                connection
                for connection in self._connections_by_source.get(source, [])
                if connection.get("target") == target
            ]
        if source is not None:
            return list(self._connections_by_source.get(source, []))
        if target is not None:
            return list(self._connections_by_target.get(target, []))
        return self.all_connections

    def _neighbor_edge(
        self,
        connection: dict[str, Any],
        *,
        entity_id: str,
        edge_direction: str,
        relation: str | None,
        review: str | None,
        policy: str | None,
        include_retired: bool,
    ) -> dict[str, Any] | None:
        if relation is not None and connection.get("relation") != relation:
            return None
        if not self._connection_visible(connection, policy=policy, review=review):
            return None

        other_id = connection["target"] if edge_direction == "out" else connection["source"]
        if edge_direction == "both":
            other_id = entity_id
        other_entity = self.entities_by_id[other_id]
        if self._is_retired_entity(other_entity) and not include_retired:
            return None

        return {
            "assertion_status": connection.get("assertion", {}).get("status"),
            "claim_signature": connection.get("claim_signature"),
            "connection_id": connection.get("id"),
            "direction": edge_direction,
            "other_entity": self._entity_summary(other_entity),
            "relation": connection.get("relation"),
            "review": connection.get("assertion", {}).get("review", {}).get("status"),
            "source": connection.get("source"),
            "target": connection.get("target"),
        }
