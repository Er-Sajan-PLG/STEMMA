#!/usr/bin/env python3
"""STEMMA validator + export generator.

Validates canonical content under content/ (entities), connections/ (first-class
assertions) and sources/ (citations) against their schemas, the relation
registry, the controlled vocabularies, and the cross-object invariants added by
plan v2 (ADR-0020/0021):

    (connections/ is the single source of truth; regenerate with
    scripts/sync_relationships.py)
  - registry inverse coherence (mutual inverses, mirrored domain/range,
    symmetric relations carry no inverse, domain/range reference known types)
  - context vocabulary conformance (domains/subdomains/regimes/scales)
  - inference-rule mutual exclusivity (ADR-0014) and confidence/basis pairing
    (ADR-0013)
  - lifecycle pointer resolution (deprecated_by, lifecycle.replaced_by)
  - dependency/hierarchy cycle detection on transitive relations

then regenerates exports/knowledge.json (a derived artifact — never the source
of truth). Version constants come from schema/VERSION.yaml (ADR-0022); the
export stamps a deterministic content_hash instead of wall-clock time so the
tracked artifact is reproducible byte-for-byte.

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
VERSION_SOURCE = SCHEMA / "VERSION.yaml"
VOCAB_DOMAINS = SCHEMA / "vocabularies" / "domains.yaml"
VOCAB_SUBDOMAINS = SCHEMA / "vocabularies" / "subdomains.yaml"
VOCAB_REGIMES = SCHEMA / "vocabularies" / "regimes.yaml"
EXPORT = ROOT / "exports" / "knowledge.json"
EXPORT_SCHEMA = SCHEMA / "export.schema.json"

ID_RE = re.compile(r"^stemma:[a-z][a-z0-9-]*\.[a-z0-9][a-z0-9-]*$")
CONN_ID_RE = re.compile(r"^stemma:conn\.[0-9]{6}$")
SRC_ID_RE = re.compile(r"^stemma:src\.[a-z0-9][a-z0-9-]*$")
STATUSES = {"draft", "machine_validated", "human_reviewed", "canonical", "deprecated", "superseded"}
# Entity types — must match the enum in concept.schema.json (v0.3 adds
# phenomenon/model/experiment per ADR-0021; check_registry_coherence reads the
# schema enum as the authoritative list and falls back to this set).
TYPES = {"concept", "quantity", "unit", "law", "equation", "misconception", "phenomenon", "model", "experiment"}
REQUIRED = ["id", "type", "name", "domain", "status", "definition", "provenance"]

SOURCE_KINDS = {
    "human-authored", "textbook", "academic-or-research", "institutional",
    "standards-or-specification", "ai-assisted-draft", "other",
}
REVIEWED_STATUSES = {"human_reviewed", "canonical"}
EXTENSION_REGISTRY = ROOT / "schema" / "extension-registry.yaml"
AGENT_REGISTRY = SCHEMA / "agent-registry.yaml"
AGENT_ID_RE = re.compile(r"^(human|process|llm|unknown):[A-Za-z0-9][A-Za-z0-9._/@-]*$")

# external_ids (ADR-0016 / plan v2 E4.1): scheme -> value pattern. Unknown schemes
# are allowed (registry stays open) but the schema restricts scheme names; known
# schemes get format-checked so a typo'd QID cannot silently anchor an entity.
EXTERNAL_ID_FORMATS = {
    "wd": re.compile(r"^Q[1-9][0-9]*$"),
    "orcid": re.compile(r"^[0-9]{4}-[0-9]{4}-[0-9]{4}-[0-9]{3}[0-9X]$"),
    "doi": re.compile(r"^10\.[0-9]{4,9}/\S+$"),
    "isbn": re.compile(r"^(97[89])?[0-9]{9}[0-9X]$"),
    "qudt": re.compile(r"^[A-Za-z0-9_-]+$"),
    "ucum": re.compile(r"^\S+$"),
    "cas": re.compile(r"^[0-9]{2,7}-[0-9]{2}-[0-9]$"),
}


def load_versions() -> dict:
    """Load the single authoritative version source (ADR-0022)."""
    if not VERSION_SOURCE.exists():
        raise SystemExit(f"error: missing {VERSION_SOURCE.relative_to(ROOT)} (ADR-0022 single version source)")
    data = yaml.safe_load(VERSION_SOURCE.read_text(encoding="utf-8")) or {}
    for key in ("schema_version", "export_version"):
        if not data.get(key):
            raise SystemExit(f"error: {VERSION_SOURCE.relative_to(ROOT)} missing {key}")
    return data


def load_agent_registry() -> dict[str, dict]:
    """Load schema/agent-registry.yaml (plan v2 E4.2) -> {agent_id: entry}."""
    if not AGENT_REGISTRY.exists():
        return {}
    data = yaml.safe_load(AGENT_REGISTRY.read_text(encoding="utf-8")) or {}
    out: dict[str, dict] = {}
    for entry in data.get("agents") or []:
        if isinstance(entry, dict) and isinstance(entry.get("id"), str):
            out[entry["id"]] = entry
    return out


def check_agent_registry_shape(agents: dict[str, dict], errors: list) -> None:
    """Registry self-consistency: id prefix == class; well-formed ids."""
    for aid, entry in agents.items():
        if not AGENT_ID_RE.fullmatch(aid):
            errors.append(f"schema/agent-registry.yaml: malformed agent id {aid!r}")
            continue
        prefix = aid.split(":", 1)[0]
        if entry.get("class") != prefix:
            errors.append(f"schema/agent-registry.yaml: agent {aid} class {entry.get('class')!r} != id prefix {prefix!r}")
        if entry.get("status") not in ("active", "retired", "test"):
            errors.append(f"schema/agent-registry.yaml: agent {aid} status must be active|retired|test")


def _agent_refs(conn: dict) -> list[tuple[str, str]]:
    """All (field, agent_id) pairs referenced by a connection's provenance."""
    prov = conn.get("provenance") or {}
    refs: list[tuple[str, str]] = []
    for field in ("asserted_by", "generated_by"):
        obj = prov.get(field)
        if isinstance(obj, dict) and isinstance(obj.get("id"), str):
            refs.append((f"provenance.{field}.id", obj["id"]))
    for i, obj in enumerate(prov.get("reviewed_by") or []):
        if isinstance(obj, dict) and isinstance(obj.get("id"), str):
            refs.append((f"provenance.reviewed_by[{i}].id", obj["id"]))
    for i, h in enumerate(prov.get("review_history") or []):
        if isinstance(h, dict) and isinstance(h.get("reviewer"), str):
            refs.append((f"provenance.review_history[{i}].reviewer", h["reviewer"]))
    return refs


def check_connection_agents(conn: dict, agents: dict[str, dict], errors: list) -> None:
    """Every agent id in provenance must resolve in the agent registry (E4.2).

    Additionally: the id's class prefix must match the declared `type`, a
    reviewer must be a human agent, and newly authored (non-migrated) assertions
    may not be attributed to an `unknown:` agent (plan v2 §4 metric)."""
    here = f"{conn.get('_file', '<connection>')}:"
    prov = conn.get("provenance") or {}
    for field, aid in _agent_refs(conn):
        if aid not in agents:
            errors.append(f"{here} {field} '{aid}' not in schema/agent-registry.yaml (E4.2)")
    for field in ("asserted_by", "generated_by"):
        obj = prov.get(field)
        if isinstance(obj, dict) and isinstance(obj.get("id"), str) and isinstance(obj.get("type"), str):
            if not obj["id"].startswith(obj["type"] + ":"):
                errors.append(f"{here} provenance.{field}: id '{obj['id']}' prefix != type '{obj['type']}'")
    for i, obj in enumerate(prov.get("reviewed_by") or []):
        if isinstance(obj, dict) and isinstance(obj.get("id"), str):
            if not obj["id"].startswith(str(obj.get("type")) + ":"):
                errors.append(f"{here} provenance.reviewed_by[{i}]: id '{obj['id']}' prefix != type '{obj.get('type')}'")
    for i, h in enumerate(prov.get("review_history") or []):
        if isinstance(h, dict) and isinstance(h.get("reviewer"), str) and not h["reviewer"].startswith("human:"):
            errors.append(f"{here} provenance.review_history[{i}].reviewer must be a human agent (found '{h['reviewer']}')")
    method = (prov.get("method") or {}).get("type") if isinstance(prov.get("method"), dict) else None
    asserted = prov.get("asserted_by") or {}
    if method != "migration" and isinstance(asserted, dict) and str(asserted.get("id", "")).startswith("unknown:"):
        errors.append(f"{here} non-migrated assertion attributed to an unknown: agent — forbidden (E4.2)")


def check_external_ids(obj: dict, errors: list, here: str) -> None:
    """Format-check external_ids values for known schemes (E4.1)."""
    ext = obj.get("external_ids")
    if ext is None:
        return
    if not isinstance(ext, dict):
        errors.append(f"{here} external_ids must be a mapping")
        return
    for scheme, value in ext.items():
        values = value if isinstance(value, list) else [value]
        pattern = EXTERNAL_ID_FORMATS.get(str(scheme))
        for v in values:
            if not isinstance(v, str) or not v.strip():
                errors.append(f"{here} external_ids.{scheme} contains a non-string/empty value")
            elif pattern and not pattern.fullmatch(v):
                errors.append(f"{here} external_ids.{scheme} value {v!r} does not match the {scheme} format")
        if isinstance(value, list) and len(set(value)) != len(value):
            errors.append(f"{here} external_ids.{scheme} has duplicate values")


def load_vocabulary(path: Path) -> Any:
    if not path.exists():
        return None
    try:
        return yaml.safe_load(path.read_text(encoding="utf-8"))
    except yaml.YAMLError:
        return None



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


def validate_entity(entity: dict, errors: list, filename_slug: str | None = None) -> None:
    here = f"{entity['_file']}:"

    # Required fields present and non-empty strings
    for field in REQUIRED:
        value = entity.get(field)
        if value is None or (isinstance(value, str) and not value.strip()):
            errors.append(f"{here} missing/empty required field '{field}'")

    # ID format
    _id = entity.get("id")
    if isinstance(_id, str) and not ID_RE.fullmatch(_id):
        errors.append(f"{here} invalid stable ID format: {_id!r} (expected stemma:<domain>.<slug>)")

    # Filename must equal the final ID slug (canonical representation rule)
    if isinstance(_id, str) and filename_slug:
        slug = _id.rsplit(".", 1)[-1]
        if filename_slug != slug:
            errors.append(
                f"{here} filename '{filename_slug}.md' does not match id slug '{slug}'"
            )

    # Enums (schema would catch these too; keep checks independent of jsonschema)
    if entity.get("type") not in TYPES:
        errors.append(f"{here} unknown type: {entity.get('type')!r}")
    if entity.get("status") not in STATUSES:
        errors.append(f"{here} unknown status: {entity.get('status')!r}")

    # Provenance shape
    prov = entity.get("provenance")
    if isinstance(prov, dict) and not isinstance(prov.get("ai_drafted"), bool):
        errors.append(f"{here} provenance.ai_drafted must be a boolean")
    if isinstance(prov, dict) and prov.get("source_kind") is not None:
        if prov.get("source_kind") not in SOURCE_KINDS:
            errors.append(f"{here} provenance.source_kind not in vocabulary: {prov.get('source_kind')!r}")
    if isinstance(prov, dict) and prov.get("ai_drafted") is False:
        if not (prov.get("source") or prov.get("reviewer")):
            errors.append(f"{here} provenance needs source or reviewer when not AI-drafted")

    # Reviewed/canonical status requires a named reviewer
    if entity.get("status") in REVIEWED_STATUSES:
        if not (isinstance(prov, dict) and prov.get("reviewer")):
            errors.append(f"{here} status {entity.get('status')!r} requires provenance.reviewer")

    # Aliases must be valid IDs and not equal the entity's own id
    for alias in entity.get("aliases", []) or []:
        if not isinstance(alias, str) or not ID_RE.fullmatch(alias):
            errors.append(f"{here} alias is not a valid stable ID: {alias!r}")
        elif alias == _id:
            errors.append(f"{here} alias must not equal the entity's own id: {alias!r}")

    # Relationships live ONLY in connections/ (ADR-0020/0028); entities carry none.

    # Deprecation hygiene
    if entity.get("status") in ("deprecated", "superseded") and not entity.get("deprecated_by"):
        errors.append(f"{here} status is {entity.get('status')} but no deprecated_by set")


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
        errors.append(f"{here} missing required 'id'")
    elif not isinstance(cid, str) or not CONN_ID_RE.fullmatch(cid):
        errors.append(f"{here} invalid connection ID: {cid!r} (expected stemma:conn.NNNNNN)")

    if conn.get("type") != "connection":
        errors.append(f"{here} connection type must be 'connection' (found {conn.get('type')!r})")

    src = conn.get("source")
    tgt = conn.get("target")
    if not isinstance(src, str) or src not in entities:
        errors.append(f"{here} source does not resolve to a canonical entity: {src!r}")
    if not isinstance(tgt, str) or tgt not in entities:
        errors.append(f"{here} target does not resolve to a canonical entity: {tgt!r}")

    rel = conn.get("relation")
    registry = load_relation_registry().get("relations", {})
    info = registry.get(rel) if isinstance(rel, str) else None
    if rel is None:
        errors.append(f"{here} missing required 'relation'")
    elif not isinstance(rel, str) or info is None:
        errors.append(f"{here} relation not in relation-registry.yaml: {rel!r}")

    # Domain/range: only when both endpoint types and the registry allow-list are known.
    if info and isinstance(src, str) and isinstance(tgt, str):
        stype = entities.get(src, {}).get("type")
        ttype = entities.get(tgt, {}).get("type")
        domain, range_ = _relation_semantics(None, info)
        if stype and domain and stype not in domain:
            errors.append(f"{here} relation '{rel}' domain excludes source type '{stype}'")
        if ttype and range_ and ttype not in range_:
            errors.append(f"{here} relation '{rel}' range excludes target type '{ttype}'")

    # Assertion must be present (required by schema); enforce provenance presence.
    prov = conn.get("provenance")
    if not isinstance(prov, dict):
        errors.append(f"{here} connection requires a provenance object")
    else:
        if not prov.get("asserted_by"):
            errors.append(f"{here} provenance.asserted_by is required")
        if not prov.get("generated_by"):
            errors.append(f"{here} provenance.generated_by is required")
        if not prov.get("method"):
            errors.append(f"{here} provenance.method is required")

    # Evidence source_ref must resolve to a canonical source.
    for idx, ev in enumerate(conn.get("evidence", []) or []):
        if not isinstance(ev, dict):
            errors.append(f"{here} evidence[{idx}] must be an object")
            continue
        ref = ev.get("source_ref")
        if ref is not None and ref not in sources:
            errors.append(f"{here} evidence.source_ref does not resolve to a source: {ref!r}")

    check_extensions(conn, "connection", errors, here)


def validate_source(src: dict, errors: list) -> None:
    """Validate a canonical source object (source.schema.json)."""
    here = f"{src.get('_file', '<source>')}:"
    sid = src.get("id")
    if sid is None:
        errors.append(f"{here} missing required 'id'")
    elif not isinstance(sid, str) or not SRC_ID_RE.fullmatch(sid):
        errors.append(f"{here} invalid source ID: {sid!r} (expected stemma:src.<slug>)")
    check_extensions(src, "source", errors, here)


def check_registry_coherence(registry: dict, errors: list) -> None:
    """Enforce relation-registry integrity (ADR-0021, audit F3).

    Invariants:
      - every `inverse` names a defined relation, is mutual, and mirrors
        domain/range
      - symmetric relations carry no `inverse` field
      - domain/range reference known entity types only (schema enum)
    """
    here = "relation-registry.yaml: "
    relations = registry.get("relations") or {}

    known_types: set = set(TYPES)
    schema = SCHEMA_
    if schema.exists():
        try:
            raw = json.loads(schema.read_text(encoding="utf-8"))
            known_types = set(raw.get("properties", {}).get("type", {}).get("enum") or known_types)
        except (json.JSONDecodeError, OSError):
            pass

    for name, meta in relations.items():
        if not isinstance(meta, dict):
            errors.append(f"{here}{name}: malformed descriptor")
            continue
        inv = meta.get("inverse")
        if meta.get("symmetric") and inv is not None:
            errors.append(f"{here}{name}: symmetric relation must not declare an inverse")
        if inv is not None:
            if inv not in relations:
                errors.append(f"{here}{name}: inverse '{inv}' is not defined in the registry")
                continue
            inv_meta = relations[inv] or {}
            if inv_meta.get("inverse") != name:
                errors.append(f"{here}{name}: inverse '{inv}' does not point back "
                              f"(its inverse is {inv_meta.get('inverse')!r})")
            if sorted(str(x) for x in (meta.get("domain") or [])) != sorted(str(x) for x in (inv_meta.get("range") or [])):
                errors.append(f"{here}{name}: domain does not mirror {inv}.range")
            if sorted(str(x) for x in (meta.get("range") or [])) != sorted(str(x) for x in (inv_meta.get("domain") or [])):
                errors.append(f"{here}{name}: range does not mirror {inv}.domain")
        for side in ("domain", "range"):
            for t in (meta.get(side) or []):
                if t not in known_types:
                    errors.append(f"{here}{name}: {side} references unknown entity type '{t}' "
                                  f"(known: {sorted(known_types)})")


def check_connection_context(conn: dict, vocab: dict, errors: list) -> None:
    """Enforce controlled context vocabularies (ADR-0021, audit F3/F11)."""
    here = f"{conn.get('_file', '<connection>')}:"
    ctx = conn.get("context") or {}
    domains = vocab.get("domains") or []
    subdomains = vocab.get("subdomains") or {}
    regimes = vocab.get("regimes") or []
    scales = vocab.get("scales") or []

    dom = ctx.get("domain")
    if dom is not None and dom not in domains:
        errors.append(f"{here} context.domain '{dom}' not in vocabularies/domains.yaml")
    sub = ctx.get("subdomain")
    if dom is not None and sub is not None:
        allowed = subdomains.get(dom)
        if allowed is None:
            errors.append(f"{here} context.domain '{dom}' has no subdomain vocabulary")
        elif sub not in allowed:
            errors.append(f"{here} context.subdomain '{sub}' not allowed for domain '{dom}' "
                          f"(vocabularies/subdomains.yaml)")
    for r in ctx.get("regime") or []:
        if r not in regimes:
            errors.append(f"{here} context.regime '{r}' not in vocabularies/regimes.yaml")
    scale = ctx.get("scale")
    if scale is not None and scales and scale not in scales:
        errors.append(f"{here} context.scale '{scale}' not in vocabularies/regimes.yaml (scales)")


def check_assertion_epistemics(conn: dict, errors: list, warnings: list) -> None:
    """Enforce ADR-0014 inference exclusivity + ADR-0013 confidence pairing."""
    here = f"{conn.get('_file', '<connection>')}:"
    assertion = conn.get("assertion") or {}
    atype = assertion.get("type")
    inference = conn.get("inference")

    if atype == "inferred":
        if not isinstance(inference, dict) or not inference.get("rule") or not inference.get("path"):
            errors.append(f"{here} assertion.type 'inferred' requires inference.rule and inference.path (ADR-0014)")
    elif inference:
        errors.append(f"{here} inference block is only legal when assertion.type is 'inferred' "
                      f"(found type {atype!r}) (ADR-0014)")

    conf = assertion.get("confidence")
    basis = assertion.get("confidence_basis")
    if (conf is None) != (basis is None):
        warnings.append(f"{here} confidence and confidence_basis must be set together "
                        f"(confidence={conf!r}, basis={basis!r}) (ADR-0013)")
    if isinstance(conf, (int, float)) and not isinstance(conf, bool) and not (0.0 <= float(conf) <= 1.0):
        errors.append(f"{here} confidence {conf!r} outside [0.0, 1.0]")


def check_lifecycle_pointers(conn: dict, connections: dict, errors: list) -> None:
    """lifecycle.replaced_by must resolve to an existing connection (ADR-0016)."""
    here = f"{conn.get('_file', '<connection>')}:"
    lifecycle = conn.get("lifecycle") or {}
    replaced_by = lifecycle.get("replaced_by")
    if replaced_by is not None and replaced_by not in connections:
        errors.append(f"{here} lifecycle.replaced_by does not resolve to a connection: {replaced_by!r}")


def claim_signature(conn: dict) -> str:
    """Derived identity of the *claim* a connection asserts (plan v2 E4.3; ADR-0026).

    signature = sha256(source | relation | target | polarity | sorted(qualifiers))

    It is the identity of the PROPOSITION, not of the record: two connections with the
    same signature assert the same thing, which `check_duplicate_claims` rejects for
    active connections (E4.3). Derived — never stored in canonical YAML — but emitted
    into the export so consumers can deduplicate claims without recomputing.

    Deterministic: qualifiers are order-insensitive (sorted, canonically serialised);
    polarity defaults to `positive` per connection.schema.json.
    """
    assertion = conn.get("assertion") or {}
    context = conn.get("context") or {}
    qualifiers = context.get("qualifiers") or []
    if not isinstance(qualifiers, list):
        qualifiers = [qualifiers]
    normalised = sorted(
        json.dumps(q, sort_keys=True, ensure_ascii=False, default=str) if isinstance(q, (dict, list)) else str(q)
        for q in qualifiers
    )
    polarity = assertion.get("polarity") or "positive"
    parts = [
        str(conn.get("source")),
        str(conn.get("relation")),
        str(conn.get("target")),
        str(polarity),
        json.dumps(normalised, sort_keys=True, ensure_ascii=False),
    ]
    return "sha256:" + hashlib.sha256("\x1f".join(parts).encode("utf-8")).hexdigest()


def check_duplicate_claims(connections: dict, errors: list) -> dict[str, str]:
    """Reject two ACTIVE connections asserting the same proposition (E4.3 / ADR-0026).

    Returns {connection_id: signature} for every active connection so the export can
    carry the derived signature without recomputing it.
    """
    by_signature: dict[str, list[str]] = {}
    signatures: dict[str, str] = {}
    for cid, conn in connections.items():
        if (conn.get("assertion") or {}).get("status", "active") != "active":
            continue
        sig = claim_signature(conn)
        signatures[cid] = sig
        by_signature.setdefault(sig, []).append(cid)
    for sig, ids in sorted(by_signature.items()):
        if len(ids) > 1:
            errors.append(
                "duplicate claim: " + ", ".join(sorted(ids))
                + f" assert the same proposition (claim_signature {sig[:19]}… over "
                "source|relation|target|polarity|qualifiers). Keep one connection and "
                "supersede the rest via lifecycle.replaced_by (plan v2 E4.3)"
            )
    return signatures


def check_relationship_cycles(connections: dict, registry: dict, errors: list) -> None:
    """Reject cycles on non-symmetric transitive relations (ADR-0012/0021).

    A cycle A requires B requires A (or part_of/hierarchy/derivation cycles) is a
    logical contradiction for a transitive relation.
    """
    transitive = {
        name for name, meta in (registry.get("relations") or {}).items()
        if isinstance(meta, dict) and meta.get("transitive") and not meta.get("symmetric")
    }
    by_relation: dict[str, dict[str, set]] = {}
    for cid, conn in connections.items():
        rel = conn.get("relation")
        if conn.get("assertion", {}).get("status") != "active":
            continue
        if rel in transitive:
            by_relation.setdefault(rel, {}).setdefault(conn["source"], set()).add(conn["target"])

    for rel in sorted(by_relation):
        graph = by_relation[rel]
        for start in sorted(graph):
            # iterative DFS looking for a path back to start
            stack = [(start, [start])]
            while stack:
                node, path = stack.pop()
                for nxt in sorted(graph.get(node, ())):
                    if nxt == start:
                        errors.append(
                            "cycle detected: " + " -> ".join(p.replace("stemma:", "") for p in path + [nxt])
                            + f" (relation '{rel}')"
                        )
                        break
                    if nxt not in path:
                        stack.append((nxt, path + [nxt]))


def write_validation_report(conforms: bool, results: list, content_hash: str | None) -> None:
    """Write the SHACL-style machine-readable validation report.

    Kept from the AXIOM-kernel work (PR #22), reconciled with ADR-0022: the report
    is DETERMINISTIC — stamped with the canonical content_hash, never wall-clock
    time — so the tracked reports/validation-report.json never churns between runs.
    """
    validation_results = []
    for line in results:
        parts = line.split(": ", 1)
        validation_results.append({
            "resultSeverity": "Violation",
            "focusNode": parts[0] if len(parts) > 1 else "unknown",
            "resultPath": None,
            "resultMessage": parts[1] if len(parts) > 1 else line,
            "sourceConstraintComponent": "STEMMAValidator",
        })
    kernel_version = None
    version_file = ROOT / "VERSION"
    if version_file.exists():
        kernel_version = version_file.read_text(encoding="utf-8").strip()
    report = {
        "conforms": conforms,
        "results": validation_results,
        "kernel_version": kernel_version,
        "content_hash": content_hash,
    }
    report_path = ROOT / "reports" / "validation-report.json"
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(
        json.dumps(report, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )


def check_legacy_namespace(raw_text: str, where: str, errors: list) -> None:
    """ADR-0027 migration completeness: the retired `lhs:` namespace must never
    reappear in canonical files (an `stemma:` ID would be unresolvable and would
    silently fork the identity space)."""
    if "lhs:" in raw_text:
        errors.append(
            f"{where}: retired `lhs:` namespace reference found — canonical IDs use "
            "`stemma:` (ADR-0027); see docs/MIGRATIONS.md"
        )


def check_inline_projection(entities: dict, connections: dict, errors: list) -> None:
    """ADR-0028: entities carry NO relationship data at all — connections/ is the
    single relationship source. Any relationship-shaped block on an entity is an
    authoring error (the generated projection was removed with export contract 2.0)."""
    for eid, entity in entities.items():
        if "relationships" in entity:
            errors.append(
                f"{entity['_file']}: `relationships` is not an entity field — assert "
                "relationships as first-class objects in connections/ (ADR-0020/0028)"
            )


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
            raw = path.read_text(encoding="utf-8")
            data = load_yaml_strict(raw, where=str(path.relative_to(ROOT)))
        except ValueError as exc:
            errors.append(f"{path.relative_to(ROOT)}: {exc}")
            continue
        if not isinstance(data, dict):
            errors.append(f"{path.relative_to(ROOT)}: expected a YAML mapping")
            continue
        check_legacy_namespace(raw, str(path.relative_to(ROOT)), errors)
        # Filename ↔ ID consistency (ADR-0027): colon-free filenames carry the ID
        # minus the namespace segment — stemma:conn.000001 → conn.000001.yaml.
        _id = data.get("id")
        if isinstance(_id, str) and _id.startswith("stemma:"):
            expected_stem = _id.split(":", 1)[1]
            if path.stem != expected_stem:
                errors.append(
                    f"{path.relative_to(ROOT)}: filename must be '{expected_stem}.yaml' "
                    f"for id {_id!r} (colon-free form of the ID)"
                )
        data["_file"] = str(path.relative_to(ROOT))
        if validator:
            obj = {k: v for k, v in data.items() if not k.startswith("_")}
            for err in validator.iter_errors(obj):
                errors.append(f"{data['_file']}: schema violation: {err.message}")
        # kind-specific deep checks
        kind = data.get("type")
        if kind == "connection":
            validate_connection(data, entities, sources, errors)
        else:
            validate_source(data, errors)
        _id = data.get("id")
        if isinstance(_id, str):
            if _id in out:
                errors.append(f"duplicate {kind} id {_id!r} in {out[_id]['_file']} and {data['_file']}")
            out[_id] = data
    return out


def main() -> int:
    errors: list = []
    entities: dict[str, dict] = {}

    if not CONTENT.exists():
        print(f"error: content directory not found: {CONTENT}", file=sys.stderr)
        return 1

    for path in sorted(CONTENT.rglob("*.md")):
        try:
            entity = parse_entity(path)
        except ValueError as exc:
            errors.append(f"{path.relative_to(ROOT)}: {exc}")
            continue
        check_legacy_namespace(path.read_text(encoding="utf-8"), str(path.relative_to(ROOT)), errors)
        validate_entity(entity, errors, filename_slug=path.stem)
        check_extensions(entity, "entity", errors, f"{entity['_file']}:")
        check_historical(entity, errors, f"{entity['_file']}:")
        check_external_ids(entity, errors, f"{entity['_file']}:")
        _id = entity.get("id")
        if isinstance(_id, str):
            if _id in entities:
                errors.append(f"duplicate id {_id!r} in {entities[_id]['_file']} and {entity['_file']}")
            entities[_id] = entity

    # Schema conformance (optional dependency)
    schema = load_schema()
    if schema is not None:
        validator = cast(Any, Draft202012Validator)(schema)
        for _id, entity in entities.items():
            data = {k: v for k, v in entity.items() if not k.startswith("_")}
            for err in validator.iter_errors(data):
                errors.append(f"{entity['_file']}: schema violation: {err.message}")

    # Dangling entity→entity pointers (aliases, deprecated_by) + semantic type rules
    # (relationship targets are checked on connections below — entities carry none).
    for _id, entity in entities.items():
        for alias in entity.get("aliases", []) or []:
            if isinstance(alias, str) and alias not in entities and not alias.startswith("stemma:"):
                errors.append(f"{entity['_file']}: alias is not a valid stemma: ID: {alias!r}")

    # Q2: load + validate first-class connections and sources (ADR-011). These are
    # first-class canonical inputs — the gate now covers content/ + connections/ + sources/.
    sources = load_canonical_yaml_dir(SOURCES, SOURCE_SCHEMA, errors, entities, {})
    connections = load_canonical_yaml_dir(CONNECTIONS, CONN_SCHEMA, errors, entities, sources)

    # Plan v2 cross-object invariants (ADR-0020/0021; audit F1, F3, F5–F7).
    registry = load_relation_registry()
    check_registry_coherence(registry, errors)
    vocab = {
        "domains": (load_vocabulary(VOCAB_DOMAINS) or {}).get("domains") or [],
        "subdomains": load_vocabulary(VOCAB_SUBDOMAINS) or {},
        "regimes": (load_vocabulary(VOCAB_REGIMES) or {}).get("regimes") or [],
        "scales": (load_vocabulary(VOCAB_REGIMES) or {}).get("scales") or [],
    }
    warnings: list = []
    agents = load_agent_registry()
    if not agents:
        errors.append("schema/agent-registry.yaml missing or empty (plan v2 E4.2: every provenance agent must resolve)")
    check_agent_registry_shape(agents, errors)
    for conn in connections.values():
        check_connection_agents(conn, agents, errors)
        check_connection_context(conn, vocab, errors)
        check_assertion_epistemics(conn, errors, warnings)
        check_lifecycle_pointers(conn, connections, errors)
    check_relationship_cycles(connections, registry, errors)
    check_inline_projection(entities, connections, errors)
    claim_signatures = check_duplicate_claims(connections, errors)

    # Entity-side reviewer ids resolve in the agent registry too (E4.2).
    for _id, entity in entities.items():
        reviewer = (entity.get("provenance") or {}).get("reviewer")
        if isinstance(reviewer, str) and reviewer not in agents:
            errors.append(f"{entity['_file']}: provenance.reviewer '{reviewer}' not in schema/agent-registry.yaml (E4.2)")
    # Extension registrants resolve as well.
    for ext_entry in (load_extension_registry().get("extensions") or []):
        reg = ext_entry.get("registered_by") if isinstance(ext_entry, dict) else None
        if isinstance(reg, str) and reg not in agents:
            errors.append(f"schema/extension-registry.yaml: registered_by '{reg}' not in schema/agent-registry.yaml (E4.2)")

    # deprecated_by must resolve to an existing entity (never a dangling pointer).
    for _id, entity in entities.items():
        successor = entity.get("deprecated_by")
        if successor is not None and successor not in entities:
            errors.append(f"{entity['_file']}: deprecated_by does not resolve to an entity: {successor!r}")

    # Report
    for line in warnings:
        print(f"WARNING: {line}", file=sys.stderr)
    if errors:
        print(f"FAIL: {len(errors)} problem(s) found", file=sys.stderr)
        for line in errors:
            print(f"  - {line}", file=sys.stderr)
        write_validation_report(conforms=False, results=errors, content_hash=None)
        return 1

    # Regenerate derived export (sorted for determinism; versions from the single
    # source ADR-0022; deterministic content_hash instead of wall-clock generated_at,
    # so the tracked artifact is reproducible byte-for-byte and CI can enforce
    # freshness via `git diff --exit-code exports/`).
    hasher = hashlib.sha256()
    for canonical_dir in (CONTENT, CONNECTIONS, SOURCES):
        if not canonical_dir.exists():
            continue
        for path in sorted(p for p in canonical_dir.rglob("*") if p.is_file()):
            hasher.update(str(path.relative_to(ROOT)).encode("utf-8"))
            hasher.update(b"\x00")
            hasher.update(path.read_bytes())
            hasher.update(b"\x00")
    versions = load_versions()
    content_hash_value = f"sha256:{hasher.hexdigest()}"
    kernel_version = (ROOT / "VERSION").read_text(encoding="utf-8").strip() if (ROOT / "VERSION").exists() else None
    payload = {
        "export_version": versions["export_version"],
        "schema_version": versions["schema_version"],
        "content_hash": content_hash_value,
        "kernel_version": kernel_version,
        "relation_registry_version": versions.get("relation_registry_version"),
        # ADR-0032 / contract v2.1: publish producer-side semantics so consumers
        # can introspect families/inverses/domain-range without cloning the repo.
        "relation_registry": registry.get("relations", {}),
        "vocabularies": {
            "domains": vocab["domains"],
            "subdomains": vocab["subdomains"],
            "regimes": vocab["regimes"],
            "scales": vocab["scales"],
        },
        "source": "content/ + connections/ + sources/ (canonical)",
        "entity_count": len(entities),
        "connection_count": len(connections),
        "source_count": len(sources),
        "entities": [
            {k: v for k, v in entities[i].items() if not k.startswith("_")}
            for i in sorted(entities)
        ],
        # `claim_signature` is DERIVED (E4.3 / ADR-0026): the identity of the asserted
        # proposition (source|relation|target|polarity|qualifiers). Never canonical;
        # it lets consumers deduplicate claims without recomputing the hash.
        "connections": [
            {
                **{k: v for k, v in connections[i].items() if not k.startswith("_")},
                "claim_signature": claim_signatures.get(i, claim_signature(connections[i])),
            }
            for i in sorted(connections)
        ],
        "sources": [
            {k: v for k, v in sources[i].items() if not k.startswith("_")}
            for i in sorted(sources)
        ],
    }
    # Contract v1.0 (ADR-0023 / gate G-A): the export must conform to
    # schema/export.schema.json BEFORE it is written — a producer can never ship
    # a payload that violates the contract it advertises.
    if HAVE_JSONSCHEMA and EXPORT_SCHEMA.exists():
        export_schema = json.loads(EXPORT_SCHEMA.read_text(encoding="utf-8"))
        contract_errors = [
            f"export contract violation ({EXPORT_SCHEMA.name}): {err.message}"
            for err in cast(Any, Draft202012Validator)(export_schema).iter_errors(payload)
        ]
        if contract_errors:
            print(f"FAIL: {len(contract_errors)} export contract problem(s)", file=sys.stderr)
            for line in contract_errors[:20]:
                print(f"  - {line}", file=sys.stderr)
            write_validation_report(conforms=False, results=contract_errors, content_hash=None)
            return 1
    EXPORT.parent.mkdir(parents=True, exist_ok=True)
    EXPORT.write_text(
        json.dumps(payload, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    print(f"OK: {len(entities)} entities valid; export written to {EXPORT.relative_to(ROOT)}")
    write_validation_report(conforms=True, results=[], content_hash=content_hash_value)
    print("OK: validation report written to reports/validation-report.json")

    # E7.4: the validator no longer writes into explorer/. The explorer is a consumer,
    # not part of the canonical gate: it copies exports/knowledge.json itself via
    # explorer/scripts/sync-export.mjs (wired to `predev`/`prebuild`), so the validator
    # never mutates another component's tree.
    return 0


if __name__ == "__main__":
    sys.exit(main())