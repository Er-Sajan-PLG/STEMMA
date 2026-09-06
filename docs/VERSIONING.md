# STEMMA Versioning

**Status:** Authoritative policy (ADR-0008, ADR-0022, ADR-0027/0028).
**Single version source:** `schema/VERSION.yaml`. Version literals in scripts
are forbidden.

---

## 1. Tracks (never collapsed)

| Track | Identifier | Meaning | Where |
|---|---|---|---|
| **Schema version** | `schema_version` (semver) | The four canonical JSON Schemas as a unit (fields, enums, constraints, ID grammar) | `schema/VERSION.yaml`, stamped in export |
| **Export contract version** | `export_version` (semver) | The `exports/knowledge.json` consumer contract (shape + semantics) | `schema/VERSION.yaml`, stamped in export |
| **Registry version** | `relation_registry_version` (semver) | `schema/relation-registry.yaml` semantics | `schema/VERSION.yaml` |
| **Repository release** | `VERSION` file (semver) | The repository's release line; currently **3.0.0** = refoundation baseline (ADR-0029) | `VERSION`, stamped as `kernel_version` in the export |

Current majors: schema **1.0.0**, export **2.1.0**, registry **1.0.0**
(export 2.1.0 is the additive relation-registry + vocabulary sidecar,
ADR-0032; broken out of the pre-refoundation 0.x line by the namespace +
projection changes; see `docs/MIGRATIONS.md`).

## 2. Bumping rules

- **Breaking** schema/contract/registry change (field removed/narrowed, ID
  grammar, contract shape): major bump + ADR + MIGRATIONS entry naming what
  old data does.
- **Additive** (optional field, enum value, new relation): minor bump;
  patch for corrections with no semantic surface change.
- **Content growth** (new entities/connections/reviews): never a contract
  bump; repository release MINOR (new knowledge) / PATCH (corrections).
- Consumers pin the **contract major**; they never pin content versions —
  `content_hash` identifies the snapshot.

## 3. Compatibility promise

- Within an export major version, required members and field semantics are
  stable; additions are backward-compatible for readers who ignore unknown
  members.
- Deprecated/superseded objects keep shipping (with successor pointers)
  within the major; their *removal from the contract* would be a major bump.
- Derived views (`knowledge.<policy>.json`, `knowledge.extended.json`)
  inherit the versions of their source and add a `policy` marker.

## 4. Determinism

Every derived artifact is content-hash stamped (`sha256:…`) — never a wall
clock — and must regenerate byte-identically (`tests/versioning/`; CI fails
on a stale or non-deterministic export).

## 5. Release procedure (roadmap R6 will formalize)

1. `python3 scripts/verify_all.py` green on the release commit.
2. Versions single-sourced in `schema/VERSION.yaml` (+ `VERSION` for the
   repository line).
3. MIGRATIONS.md current for any schema/contract change in the release.
4. Tag `v<VERSION>` with a conventional-changelog summary.
