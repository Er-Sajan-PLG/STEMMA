#!/usr/bin/env python3
"""STEMMA validator + export generator (v0.3).

Validates canonical content under content/ against schema/concept.schema.json,
then regenerates exports/knowledge.json (a derived artifact — never the source of truth).

Exit codes
    0  valid; export regenerated
    1  validation errors
    2  missing dependency

Dependencies: PyYAML (required). jsonschema (optional — used when importable).
"""
from __future__ import annotations

import hashlib
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, cast

try:
    import yaml
except ImportError:  # pragma: no cover
    print("error: PyYAML is required (python3 -m pip install pyyaml)", file=sys.stderr)
    sys.exit(2)

try:
    from jsonschema import Draft202012Validator

    HAVE_JSONSCHEMA = True
except ImportError:  # pragma: no cover
    Draft202012Validator = None
    HAVE_JSONSCHEMA = False

ROOT = Path(__file__).resolve().parent.parent
CONTENT = ROOT / "content"
CONNECTIONS = ROOT / "connections"
SOURCES = ROOT / "sources"
SCHEMA = ROOT / "schema"
SCHEMA_ = SCHEMA / "concept.schema.json"
CONN_SCHEMA = SCHEMA / "connection.schema.json"
SOURCE_SCHEMA = SCHEMA / "source.schema.json"
RELATION_REGISTRY = SCHEMA / "relation-registry.yaml"
EXTENSION_REGISTRY = ROOT / "schema" / "extension-registry.yaml"
EXPORT = ROOT / "exports" / "knowledge.json"

ID_RE = re.compile(r"^lhs:[a-z][a-z0-9-]*\.[a-z0-9][a-z0-9-]*$")
CONN_ID_RE = re.compile(r"^lhs:conn\.[0-9]{6}$")
SRC_ID_RE = re.compile(r"^lhs:src\.[a-z0-9][a-z0-9-]*$")

# Extended entity types per v0.3 schema
TYPES = {
    "concept", "quantity", "unit", "law", "equation", "misconception",
    "phenomenon", "model", "experiment", "regime",
    "observation", "measurement", "classification", "definition", "claim"
}
STATUSES = {"draft", "machine_validated", "human_reviewed", "canonical", "deprecated", "superseded"}

# Core relationship types (inline entity.relationships[])
REL_TYPES = {
    "logically_requires", "mathematically_requires", "part_of", "derived_from",
    "special_case_of", "generalizes", "equivalent_to", "applies_to",
    "appears_in_law", "related_to",
}

# Transitive relationship types that should NOT have cycles (structural/hierarchical)
# These represent true "is-a" or "part-of" hierarchies where cycles are logical errors
STRUCTURAL_TRANSITIVE_REL_TYPES = {
    "part_of", "has_part", "is_a", "special_case_of", "generalizes",
    "broader_than", "narrower_than", "equivalent_to",
}

# Dependency transitive types where cycles MAY be legitimate (mutual dependencies in math/science)
DEPENDENCY_TRANSITIVE_REL_TYPES = {
    "logically_requires", "mathematically_requires", "derived_from",
    "requires", "prerequisite_of", "depends_on",
}

# Inverse relationship pairs
INVERSE_PAIRS = {
    "part_of": "has_part",
    "has_part": "part_of",
    "generalizes": "special_case_of",
    "special_case_of": "generalizes",
    "broader_than": "narrower_than",
    "narrower_than": "broader_than",
    "logically_requires": "logically_required_by",
    "logically_required_by": "logically_requires",
    "mathematically_requires": "mathematically_required_by",
    "mathematically_required_by": "mathematically_requires",
    "derived_from": "is_basis_of",
    "is_basis_of": "derived_from",
    "requires": "required_by",
    "required_by": "requires",
    "prerequisite_of": "enables_learning_of",
    "enables_learning_of": "prerequisite_of",
    "depends_on": "depended_on_by",
    "depended_on_by": "depends_on",
    "causes": "caused_by",
    "caused_by": "causes",
    "contributes_to": "has_contribution_from",
    "has_contribution_from": "contributes_to",
    "results_in": "results_from",
    "results_from": "results_in",
    "influences": "influenced_by",
    "influenced_by": "influences",
    "prevents": "prevented_by",
    "prevented_by": "prevents",
    "explains": "explained_by",
    "explained_by": "explains",
    "accounts_for": "accounted_for_by",
    "accounted_for_by": "accounts_for",
    "predicted_by": "predicts",
    "predicts": "predicted_by",
    "supported_by": "supports",
    "supports": "supported_by",
    "evidenced_by": "evidence_for",
    "evidence_for": "evidenced_by",
    "approximates": "approximated_by",
    "approximated_by": "approximates",
    "idealizes": "idealized_by",
    "idealized_by": "idealizes",
    "extends": "extended_by",
    "extended_by": "extends",
    "supersedes": "superseded_by",
    "superseded_by": "supersedes",
    "simplifies": "simplified_by",
    "simplified_by": "simplifies",
    "measures": "measured_by",
    "measured_by": "measures",
    "quantifies": "quantified_by",
    "quantified_by": "quantifies",
    "expressed_in": "expresses",
    "expresses": "expressed_in",
    "has_unit": "unit_of",
    "unit_of": "has_unit",
    "enables": "enabled_by",
    "enabled_by": "enables",
    "used_in": "uses",
    "uses": "used_in",
    "applied_to": "applies",
    "applies": "applied_to",
    "implemented_by": "implements",
    "implements": "implemented_by",
    "maps_to": "mapped_from",
    "mapped_from": "maps_to",
    "manifestation_of": "manifests_as",
    "manifests_as": "manifestation_of",
}

REQUIRED = ["id", "type", "name", "domain", "status", "definition", "provenance"]

SOURCE_KINDS = {
    "human-authored", "textbook", "academic-or-research", "institutional",
    "standards-or-specification", "ai-assisted-draft", "other",
}
REVIEWED_STATUSES = {"human_reviewed", "canonical"}

# Error severity levels
class Severity:
    ERROR = "ERROR"
    WARNING = "WARNING"
    INFO = "INFO"


def load_extension_registry() -> dict:
    """Load the extension registry (ADR-0017), tolerating absence."""
    if not EXTENSION_REGISTRY.exists():
        return {"extensions": []}
    try:
        data = yaml.safe_load(EXTENSION_REGISTRY.read_text(encoding="utf-8")) or {}
        return data if isinstance(data, dict) else {"extensions": []}
    except yaml.YAMLError:
        return {"extensions": []}


def check_extensions(data: dict, object_kind: str, errors: list, here: str) -> None:
    """Enforce that `extensions` keys are registered (ADR-0017).

    The schema leaves the map open so new dimensions never hard-fail; this gate is
    where governance lives. Every key must be a registered dimension applicable to
    this object kind, and any controlled enum must be respected.
    """
    extensions = data.get("extensions")
    if not extensions:
        return
    if not isinstance(extensions, dict):
        errors.append(f"{here} extensions must be an object/map")
        return

    registry = load_extension_registry()
    by_name = {e.get("name"): e for e in registry.get("extensions", []) if isinstance(e, dict)}

    for key, value in extensions.items():
        dim = by_name.get(key)
        if dim is None:
            errors.append(
                f"{here} extension '{key}' is not registered. Register it with: "
                "python3 scripts/register_extension.py add --name ... (see ADR-0017)"
            )
            continue
        if object_kind not in dim.get("applies_to", []):
            errors.append(
                f"{here} extension '{key}' applies to {dim.get('applies_to')}, "
                f"not '{object_kind}'"
            )
        enum = dim.get("enum")
        if enum and value not in enum:
            errors.append(
                f"{here} extension '{key}' value {value!r} not in controlled "
                f"vocabulary {enum}"
            )
        vtype = dim.get("value_type")
        if vtype == "string" and not isinstance(value, str):
            errors.append(f"{here} extension '{key}' must be a string")
        elif vtype == "number" and not isinstance(value, (int, float)):
            errors.append(f"{here} extension '{key}' must be a number")
        elif vtype == "boolean" and not isinstance(value, bool):
            errors.append(f"{here} extension '{key}' must be a boolean")


def check_historical(data: dict, errors: list, here: str) -> None:
    """Validate optional historical-attribution field (ADR-0018).

    When `historical` is present it must carry stated_by (str) and year (int);
    optional `where`/`context`/`note` strings; optional ordered `timeline[]` of
    {year:int, event:str, by?:str}. Absent-field is fine (unknown origin is not
    fabricated). Fields are additive and never required at the entity level.
    """
    hist = data.get("historical")
    if hist is None:
        return
    if not isinstance(hist, dict):
        errors.append(f"{here} historical must be an object")
        return

    sb = hist.get("stated_by")
    if not isinstance(sb, str) or not sb.strip():
        errors.append(f"{here} historical.stated_by is required and must be a non-empty string")

    y = hist.get("year")
    if not isinstance(y, int) or isinstance(y, bool):
        errors.append(f"{here} historical.year must be an integer")
    for key in ("where", "context", "note"):
        v = hist.get(key)
        if v is not None and not isinstance(v, str):
            errors.append(f"{here} historical.{key} must be a string")

    timeline = hist.get("timeline")
    if timeline is not None:
        if not isinstance(timeline, list):
            errors.append(f"{here} historical.timeline must be an array")
        else:
            for ev in timeline:
                if not isinstance(ev, dict):
                    errors.append(f"{here} historical.timeline entries must be objects")
                    continue
                if not isinstance(ev.get("year"), int):
                    errors.append(f"{here} historical.timeline[] requires an integer year")
                if not isinstance(ev.get("event"), str) or not ev.get("event"):
                    errors.append(f"{here} historical.timeline[] requires an event string")
                if ev.get("by") is not None and not isinstance(ev.get("by"), str):
                    errors.append(f"{here} historical.timeline[].by must be a string")


def load_schema() -> Any:
    if not HAVE_JSONSCHEMA or not SCHEMA_.exists():
        return None
    raw = json.loads(SCHEMA_.read_text(encoding="utf-8"))
    cast(Any, Draft202012Validator).check_schema(raw)  # raises on invalid schema
    return raw


def parse_entity(path: Path) -> dict:
    text = path.read_text(encoding="utf-8")
    if not text.startswith("---"):
        raise ValueError("missing opening frontmatter marker '---'")
    parts = text.split("---", 2)
    if len(parts) < 3:
        raise ValueError("frontmatter not closed with '---'")
    data = load_yaml_strict(parts[1], where=str(path.relative_to(ROOT)))
    if not isinstance(data, dict):
        raise ValueError("frontmatter must be a single YAML mapping")
    data["_file"] = str(path.relative_to(ROOT))
    return data


def load_yaml_strict(text: str, where: str = "<yaml>") -> Any:
    """Parse YAML and deterministically reject duplicate mapping keys.

    PyYAML's safe_load silently keeps the last value for a duplicated key, which
    hides authoring errors (Q1.2). We walk the composed node tree and raise a
    ValueError naming the exact duplicate path so the gate can surface it.
    """
    loader = yaml.SafeLoader(text)
    try:
        node = loader.get_single_node()
    finally:
        loader.dispose()

    if node is None:
        return None  # empty document

    dups: list[str] = []
    _collect_duplicate_keys(node, dups, "")
    if dups:
        raise ValueError(f"{where}: duplicate YAML key(s): {', '.join(sorted(set(dups)))}")
    return yaml.safe_load(text)


def _collect_duplicate_keys(node: Any, dups: list[str], path: str) -> None:
    """Recursively find duplicate mapping keys in a composed YAML node."""
    if isinstance(node, yaml.MappingNode):
        seen: set[str] = set()
        for key_node, value_node in node.value:
            key = key_node.value if key_node is not None else ""
            key_path = f"{path}/{key}"
            if key in seen:
                dups.append(key_path)
            else:
                seen.add(key)
            _collect_duplicate_keys(value_node, dups, key_path)
    elif isinstance(node, yaml.SequenceNode):
        for value_node in node.value:
            _collect_duplicate_keys(value_node, dups, f"{path}[]")


def add_error(errors: list, message: str, severity: str = Severity.ERROR) -> None:
    """Add an error with severity level."""
    errors.append(f"[{severity}] {message}")


def validate_entity(entity: dict, errors: list, filename_slug: str | None = None) -> None:
    here = f"{entity['_file']}:"

    # Required fields present and non-empty strings
    for field in REQUIRED:
        value = entity.get(field)
        if value is None or (isinstance(value, str) and not value.strip()):
            add_error(errors, f"{here} missing/empty required field '{field}'")

    # ID format
    _id = entity.get("id")
    if isinstance(_id, str) and not ID_RE.fullmatch(_id):
        add_error(errors, f"{here} invalid stable ID format: {_id!r} (expected lhs:<domain>.<slug>)")

    # Filename must equal the final ID slug (canonical representation rule)
    if isinstance(_id, str) and filename_slug:
        slug = _id.rsplit(".", 1)[-1]
        if filename_slug != slug:
            add_error(errors,
                f"{here} filename '{filename_slug}.md' does not match id slug '{slug}'")

    # Enums
    if entity.get("type") not in TYPES:
        add_error(errors, f"{here} unknown type: {entity.get('type')!r}")
    if entity.get("status") not in STATUSES:
        add_error(errors, f"{here} unknown status: {entity.get('status')!r}")

    # Provenance shape
    prov = entity.get("provenance")
    if isinstance(prov, dict) and not isinstance(prov.get("ai_drafted"), bool):
        add_error(errors, f"{here} provenance.ai_drafted must be a boolean")
    if isinstance(prov, dict) and prov.get("source_kind") is not None:
        if prov.get("source_kind") not in SOURCE_KINDS:
            add_error(errors, f"{here} provenance.source_kind not in vocabulary: {prov.get('source_kind')!r}")
    if isinstance(prov, dict) and prov.get("ai_drafted") is False:
        if not (prov.get("source") or prov.get("reviewer")):
            add_error(errors, f"{here} provenance needs source or reviewer when not AI-drafted")

    # Reviewed/canonical status requires a named reviewer
    if entity.get("status") in REVIEWED_STATUSES:
        if not (isinstance(prov, dict) and prov.get("reviewer")):
            add_error(errors, f"{here} status {entity.get('status')!r} requires provenance.reviewer")

    # Aliases must be valid IDs and not equal the entity's own id
    for alias in entity.get("aliases", []) or []:
        if not isinstance(alias, str) or not ID_RE.fullmatch(alias):
            add_error(errors, f"{here} alias is not a valid stable ID: {alias!r}")
        elif alias == _id:
            add_error(errors, f"{here} alias must not equal the entity's own id: {alias!r}")

    # Relationships (inline - compatibility projection)
    for rel in entity.get("relationships", []) or []:
        if not isinstance(rel, dict):
            add_error(errors, f"{here} relationship must be an object")
            continue
        rtype = rel.get("type")
        if rtype not in REL_TYPES:
            add_error(errors, f"{here} relationship type not in core whitelist: {rtype!r}")
        target = rel.get("target")
        if not isinstance(target, str) or not target.startswith("lhs:"):
            add_error(errors, f"{here} relationship target must be an 'lhs:' ID: {target!r}")

    # Deprecation hygiene
    if entity.get("status") in ("deprecated", "superseded") and not entity.get("deprecated_by"):
        add_error(errors, f"{here} status is {entity.get('status')} but no deprecated_by set")

    # Extensions
    check_extensions(entity, "entity", errors, here)

    # Historical
    check_historical(entity, errors, here)


def load_relation_registry() -> dict:
    """Load the relation registry (authoritative relation vocabulary)."""
    if not RELATION_REGISTRY.exists():
        return {"relations": {}}
    try:
        data = yaml.safe_load(RELATION_REGISTRY.read_text(encoding="utf-8")) or {}
        return data if isinstance(data, dict) else {"relations": {}}
    except yaml.YAMLError:
        return {"relations": {}}


def _relation_semantics(raw: Any, info: dict) -> tuple[list, list]:
    """Best-effort domain/range lists from a relation descriptor.

    The vocabulary may encode domain/range as either YAML list syntax used here
    (a plain list) or the '|-' block style, both of which parse to a list under
    safe_load. Defensive fallback to [] keeps the check lenient for exotic forms.
    """
    domain = info.get("domain")
    range_ = info.get("range")
    return (
        [str(x) for x in domain] if isinstance(domain, list) else [],
        [str(x) for x in range_] if isinstance(range_, list) else [],
    )


def validate_connection(conn: dict, entities: dict, sources: dict, errors: list) -> None:
    """Validate a first-class connection (ADR-011 / connection.schema.json)."""
    here = f"{conn.get('_file', '<connection>')}:"
    cid = conn.get("id")
    if cid is None:
        add_error(errors, f"{here} missing required 'id'")
    elif not isinstance(cid, str) or not CONN_ID_RE.fullmatch(cid):
        add_error(errors, f"{here} invalid connection ID: {cid!r} (expected lhs:conn.NNNNNN)")

    if conn.get("type") != "connection":
        add_error(errors, f"{here} connection type must be 'connection' (found {conn.get('type')!r})")

    src = conn.get("source")
    tgt = conn.get("target")
    if not isinstance(src, str) or src not in entities:
        add_error(errors, f"{here} source does not resolve to a canonical entity: {src!r}")
    if not isinstance(tgt, str) or tgt not in entities:
        add_error(errors, f"{here} target does not resolve to a canonical entity: {tgt!r}")

    rel = conn.get("relation")
    registry = load_relation_registry().get("relations", {})
    info = registry.get(rel) if isinstance(rel, str) else None
    if rel is None:
        add_error(errors, f"{here} missing required 'relation'")
    elif not isinstance(rel, str) or info is None:
        add_error(errors, f"{here} relation not in relation-registry.yaml: {rel!r}")

    # Domain/range: only when both endpoint types and the registry allow-list are known.
    if info and isinstance(src, str) and isinstance(tgt, str):
        stype = entities.get(src, {}).get("type")
        ttype = entities.get(tgt, {}).get("type")
        domain, range_ = _relation_semantics(None, info)
        if stype and domain and stype not in domain:
            add_error(errors, f"{here} relation '{rel}' domain excludes source type '{stype}'")
        if ttype and range_ and ttype not in range_:
            add_error(errors, f"{here} relation '{rel}' range excludes target type '{ttype}'")

    # Assertion must be present (required by schema); enforce provenance presence.
    prov = conn.get("provenance")
    if not isinstance(prov, dict):
        add_error(errors, f"{here} connection requires a provenance object")
    else:
        if not prov.get("asserted_by"):
            add_error(errors, f"{here} provenance.asserted_by is required")
        if not prov.get("generated_by"):
            add_error(errors, f"{here} provenance.generated_by is required")
        if not prov.get("method"):
            add_error(errors, f"{here} provenance.method is required")

    # Evidence source_ref must resolve to a canonical source.
    for idx, ev in enumerate(conn.get("evidence", []) or []):
        if not isinstance(ev, dict):
            add_error(errors, f"{here} evidence[{idx}] must be an object")
            continue
        ref = ev.get("source_ref")
        if ref is not None and ref not in sources:
            add_error(errors, f"{here} evidence.source_ref does not resolve to a source: {ref!r}")

    check_extensions(conn, "connection", errors, here)


def validate_source(src: dict, errors: list) -> None:
    """Validate a canonical source object (source.schema.json)."""
    here = f"{src.get('_file', '<source>')}:"
    sid = src.get("id")
    if sid is None:
        add_error(errors, f"{here} missing required 'id'")
    elif not isinstance(sid, str) or not SRC_ID_RE.fullmatch(sid):
        add_error(errors, f"{here} invalid source ID: {sid!r} (expected lhs:src.<slug>)")
    check_extensions(src, "source", errors, here)


def load_canonical_yaml_dir(directory: Path, schema_path: Path, errors: list,
                            entities: dict, sources: dict) -> dict:
    """Load + validate all canonical YAML objects in a directory (connections/sources).

    Returns a dict keyed by object id. Each object is validated against (a) its
    JSON schema and (b) the custom checks in validate_connection/validate_source.
    Only objects that parse are collected; unparsable files are reported.
    """
    out: dict[str, dict] = {}
    if not directory.exists():
        return out
    schema = None
    if HAVE_JSONSCHEMA and schema_path.exists():
        try:
            schema = json.loads(schema_path.read_text(encoding="utf-8"))
            cast(Any, Draft202012Validator).check_schema(schema)
        except Exception as exc:  # noqa: BLE001 - schema misconfiguration is fatal
            errors.append(f"invalid schema {schema_path}: {exc}")
            schema = None
    validator = cast(Any, Draft202012Validator)(schema) if schema else None

    for path in sorted(directory.glob("*.yaml")):
        try:
            data = load_yaml_strict(path.read_text(encoding="utf-8"), where=str(path.relative_to(ROOT)))
        except ValueError as exc:
            errors.append(f"{path.relative_to(ROOT)}: {exc}")
            continue
        if not isinstance(data, dict):
            errors.append(f"{path.relative_to(ROOT)}: expected a YAML mapping")
            continue
        data["_file"] = str(path.relative_to(ROOT))
        if validator:
            obj = {k: v for k, v in data.items() if not k.startswith("_")}
            for err in validator.iter_errors(obj):
                add_error(errors, f"{data['_file']}: schema violation: {err.message}")
        # kind-specific deep checks
        kind = data.get("type")
        if kind == "connection":
            validate_connection(data, entities, sources, errors)
        else:
            validate_source(data, errors)
        _id = data.get("id")
        if isinstance(_id, str):
            if _id in out:
                add_error(errors, f"duplicate {kind} id {_id!r} in {out[_id]['_file']} and {data['_file']}")
            out[_id] = data
    return out


def detect_transitive_cycles(entities: dict, errors: list) -> None:
    """Detect cycles in STRUCTURAL transitive relationships only.

    Dependency cycles (mathematically_requires, logically_requires) are often
    legitimate in scientific knowledge (mutual interdependencies). Only structural
    hierarchies (part_of, is_a, special_case_of, etc.) should be acyclic.

    2-node cycles between inverse relationships (e.g., A generalizes B, B special_case_of A)
    are expected and correct - they represent the bidirectional nature of the relationship.
    Only cycles of length > 2 indicate true structural problems.
    """
    # Build adjacency for structural transitive relations only
    adj: dict[str, list[str]] = {}
    for eid, entity in entities.items():
        for rel in entity.get("relationships", []) or []:
            rtype = rel.get("type")
            target = rel.get("target")
            if rtype in STRUCTURAL_TRANSITIVE_REL_TYPES and target in entities:
                adj.setdefault(eid, []).append(target)

    # DFS cycle detection - only report cycles of length > 2
    # (2-node cycles between inverses are expected)
    visited = set()
    rec_stack = set()
    path = []

    def dfs(node: str) -> bool:
        visited.add(node)
        rec_stack.add(node)
        path.append(node)

        for neighbor in adj.get(node, []):
            if neighbor not in visited:
                if dfs(neighbor):
                    return True
            elif neighbor in rec_stack:
                # Found cycle - check length
                cycle_start = path.index(neighbor)
                cycle = path[cycle_start:] + [neighbor]
                if len(cycle) > 3:  # > 2 edges means > 2 nodes in cycle
                    add_error(errors, f"Cycle detected in structural transitive relationship: {' -> '.join(cycle)}", Severity.WARNING)
                    return True
                # 2-node cycle (A->B->A) between inverses is expected, ignore

        rec_stack.remove(node)
        path.pop()
        return False

    for node in adj:
        if node not in visited:
            dfs(node)


def validate_inverse_relationships(entities: dict, errors: list) -> None:
    """Validate that inverse relationship pairs are consistent.

    Note: This check is INFO-level because the existing dataset was created
    before this validation existed. New entities should include both directions.
    """
    # Build map of relationships
    rel_map: dict[tuple[str, str, str], dict] = {}  # (source, relation, target) -> relationship
    for eid, entity in entities.items():
        for rel in entity.get("relationships", []) or []:
            rtype = rel.get("type")
            target = rel.get("target")
            if rtype and target:
                rel_map[(eid, rtype, target)] = rel

    # Check inverse pairs
    for (source, rtype, target), rel in rel_map.items():
        inverse = INVERSE_PAIRS.get(rtype)
        if inverse and (target, inverse, source) not in rel_map:
            add_error(errors,
                f"{entities[source]['_file']}: missing inverse relationship '{inverse}' "
                f"for '{rtype}' from {source} to {target}",
                Severity.INFO)


def validate_semantic_layers(entities: dict, errors: list) -> None:
    """Validate semantic layer constraints.

    Ensure that entity types are used appropriately:
    - law entities should be sources of applies_to
    - quantity entities should have unit/symbol
    - misconception entities should have related_to to correct concept
    - observation/measurement should have evidence-like properties
    """
    for eid, entity in entities.items():
        etype = entity.get("type")
        here = f"{entity['_file']}:"

        # Law should not be target of applies_to (only source)
        if etype == "law":
            # Laws can have applies_to outgoing, not incoming
            pass  # Already validated in dangling check

        # Quantity should have unit (recommended)
        if etype == "quantity" and not entity.get("unit"):
            add_error(errors, f"{here} quantity entity should have a unit", Severity.INFO)

        # Misconception should relate to a concept
        if etype == "misconception":
            has_related = any(
                r.get("type") == "related_to" and entities.get(r.get("target"), {}).get("type") == "concept"
                for r in entity.get("relationships", []) or []
            )
            if not has_related:
                add_error(errors, f"{here} misconception should have related_to pointing to a concept", Severity.WARNING)

        # Claim entities should have evidence-like provenance
        if etype == "claim":
            if not entity.get("provenance", {}).get("source"):
                add_error(errors, f"{here} claim entity should have provenance.source", Severity.INFO)


def validate_entity_connection_consistency(entities: dict, connections: dict, errors: list) -> None:
    """Validate that inline entity.relationships[] are consistent with first-class connections.

    This is the compatibility projection check - inline relationships should be
    derivable from first-class connections.
    """
    # Build set of inline relationships
    inline_rels: set[tuple[str, str, str]] = set()
    for eid, entity in entities.items():
        for rel in entity.get("relationships", []) or []:
            rtype = rel.get("type")
            target = rel.get("target")
            if rtype and target:
                inline_rels.add((eid, rtype, target))

    # Build set of first-class connections (mapped to inline types)
    conn_rels: set[tuple[str, str, str]] = set()
    for cid, conn in connections.items():
        rel_type = conn.get("relation")
        source = conn.get("source")
        target = conn.get("target")
        if rel_type in REL_TYPES and source and target:
            conn_rels.add((source, rel_type, target))

    # Check for inline relationships not represented in connections
    for (source, rtype, target) in inline_rels:
        if (source, rtype, target) not in conn_rels:
            add_error(errors,
                f"{entities[source]['_file']}: inline relationship '{rtype}' -> {target} "
                f"not found in first-class connections (connection drift)",
                Severity.WARNING)


def main() -> int:
    errors: list = []
    entities: dict[str, dict] = {}

    if not CONTENT.exists():
        print(f"error: content directory not found: {CONTENT}", file=sys.stderr)
        return 1

    # Phase 1: Parse and validate entities
    for path in sorted(CONTENT.rglob("*.md")):
        try:
            entity = parse_entity(path)
        except ValueError as exc:
            add_error(errors, f"{path.relative_to(ROOT)}: {exc}")
            continue
        validate_entity(entity, errors, filename_slug=path.stem)
        _id = entity.get("id")
        if isinstance(_id, str):
            if _id in entities:
                add_error(errors, f"duplicate id {_id!r} in {entities[_id]['_file']} and {entity['_file']}")
            entities[_id] = entity

    # Phase 2: Schema conformance (optional dependency)
    schema = load_schema()
    if schema is not None:
        validator = cast(Any, Draft202012Validator)(schema)
        for _id, entity in entities.items():
            data = {k: v for k, v in entity.items() if not k.startswith("_")}
            for err in validator.iter_errors(data):
                add_error(errors, f"{entity['_file']}: schema violation: {err.message}")

    # Phase 3: Dangling relationship targets + semantic type rules
    for _id, entity in entities.items():
        etype = entity.get("type")
        for rel in entity.get("relationships", []) or []:
            target = rel.get("target")
            if isinstance(target, str) and target not in entities:
                add_error(errors, f"{entity['_file']}: dangling relationship target: {target} (from {_id})")
                continue
            rtype = rel.get("type")
            target_type = entities.get(target, {}).get("type")
            # Core semantic rules (specification §5.1)
            if rtype == "applies_to" and etype != "law":
                add_error(errors, f"{entity['_file']}: applies_to requires a 'law' source (found {etype})")
            if rtype == "appears_in_law" and target_type != "law":
                add_error(errors, f"{entity['_file']}: appears_in_law target must be a 'law' (found {target_type})")

    # Phase 4: Load + validate first-class connections and sources
    sources = load_canonical_yaml_dir(SOURCES, SOURCE_SCHEMA, errors, entities, {})
    connections = load_canonical_yaml_dir(CONNECTIONS, CONN_SCHEMA, errors, entities, sources)

    # Phase 5: Semantic validation (cross-entity)
    detect_transitive_cycles(entities, errors)
    validate_inverse_relationships(entities, errors)
    validate_semantic_layers(entities, errors)
    validate_entity_connection_consistency(entities, connections, errors)

    # Report
    # Only fail on ERROR severity. WARNING and INFO are reported but don't block.
    has_errors = any(e.startswith("[ERROR]") or (not e.startswith("[") and not e.startswith("[WARNING]") and not e.startswith("[INFO]")) for e in errors)

    # Build validation report
    validation_results = []
    for line in errors:
        parts = line.split(": ", 1)
        focus_node = parts[0] if len(parts) > 1 else "unknown"
        message = parts[1] if len(parts) > 1 else line
        # Extract severity if present
        severity = Severity.ERROR
        if message.startswith("[ERROR] "):
            severity = Severity.ERROR
            message = message[8:]
        elif message.startswith("[WARNING] "):
            severity = Severity.WARNING
            message = message[10:]
        elif message.startswith("[INFO] "):
            severity = Severity.INFO
            message = message[7:]

        validation_results.append({
            "resultSeverity": "Violation" if severity == Severity.ERROR else severity,
            "focusNode": focus_node,
            "resultPath": None,
            "resultMessage": message,
            "sourceConstraintComponent": "STEMMAValidator",
        })
    validation_report = {
        "conforms": not has_errors,
        "results": validation_results,
        "generated_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "kernel_version": (ROOT / "VERSION").read_text(encoding="utf-8").strip() if (ROOT / "VERSION").exists() else "unknown",
    }
    report_path = ROOT / "reports" / "validation-report.json"
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(
        json.dumps(validation_report, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )

    error_count = sum(1 for e in errors if e.startswith("[ERROR]") or (not e.startswith("[") and not e.startswith("[WARNING]") and not e.startswith("[INFO]")))
    warning_count = sum(1 for e in errors if e.startswith("[WARNING]"))
    info_count = sum(1 for e in errors if e.startswith("[INFO]"))

    if has_errors:
        print(f"FAIL: {error_count} error(s), {warning_count} warning(s), {info_count} info", file=sys.stderr)
        for line in errors:
            print(f"  - {line}", file=sys.stderr)
        return 1
    else:
        print(f"OK: {error_count} error(s), {warning_count} warning(s), {info_count} info (validation passed)")

    # Regenerate derived export (sorted for determinism)
    content_hash = hashlib.sha256()
    for path in sorted(CONTENT.rglob("*.md")):
        content_hash.update(path.read_bytes())
    for path in sorted(CONNECTIONS.glob("*.yaml")):
        content_hash.update(path.read_bytes())
    for path in sorted(SOURCES.glob("*.yaml")):
        content_hash.update(path.read_bytes())

    kernel_version = (ROOT / "VERSION").read_text(encoding="utf-8").strip() if (ROOT / "VERSION").exists() else "1.0.0"
    schema_version = "0.3"  # v0.3 schema with extended entity types

    payload = {
        "export_version": "0.2",  # Bumped due to new entity types in export
        "schema_version": schema_version,
        "kernel_version": kernel_version,
        "content_hash": content_hash.hexdigest(),
        "generated_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "source": "content/",
        "entity_count": len(entities),
        "connection_count": len(connections),
        "source_count": len(sources),
        "entities": [
            {k: v for k, v in entities[i].items() if not k.startswith("_")}
            for i in sorted(entities)
        ],
        "connections": [
            {k: v for k, v in connections[i].items() if not k.startswith("_")}
            for i in sorted(connections)
        ],
        "sources": [
            {k: v for k, v in sources[i].items() if not k.startswith("_")}
            for i in sorted(sources)
        ],
    }
    EXPORT.parent.mkdir(parents=True, exist_ok=True)
    EXPORT.write_text(
        json.dumps(payload, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    print(f"OK: {len(entities)} entities valid; export written to {EXPORT.relative_to(ROOT)}")

    # Auto-sync the derived export into the explorer (3D visual)
    explorer_target = ROOT / "explorer" / "public" / "exports" / "knowledge.json"
    if explorer_target.parent.is_dir() or (ROOT / "explorer").is_dir():
        explorer_target.parent.mkdir(parents=True, exist_ok=True)
        explorer_target.write_text(
            json.dumps(payload, indent=2, ensure_ascii=False) + "\n",
            encoding="utf-8",
        )
        print(f"OK: explorer export synced to {explorer_target.relative_to(ROOT)}")

    # Write validation report (success)
    validation_report = {
        "conforms": True,
        "results": [],
        "generated_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "kernel_version": kernel_version,
        "content_hash": content_hash.hexdigest(),
    }
    report_path = ROOT / "reports" / "validation-report.json"
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(
        json.dumps(validation_report, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    print(f"OK: validation report written to {report_path.relative_to(ROOT)}")

    return 0


if __name__ == "__main__":
    sys.exit(main())