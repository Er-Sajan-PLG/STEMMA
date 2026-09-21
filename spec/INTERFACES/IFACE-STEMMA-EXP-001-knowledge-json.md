# IFACE-STEMMA-EXP-001 — `exports/knowledge.json` export contract

| Field | Value |
|---|---|
| ID | IFACE-STEMMA-EXP-001 |
| Provider | STEMMA producer (`scripts/validate.py`, regenerated deterministically) |
| Consumers | adapters/python SDK+API, explorer, external consumers (learninghub, professor-j, general — declared, unverified) |
| Owner | Sajan (STEMMA side); cross-repo counterparty UNASSIGNED (UNRES-STEMMA-INTEG-001) |
| Purpose | Single machine-readable, deterministic snapshot of the canonical corpus + introspection sidecars |
| Version | export_version 2.2.0 (source of truth `schema/VERSION.yaml`; ADR-0050) |
| Schema/Contract | `schema/export.schema.json` (JSON Schema; export validated in tests) |
| Inputs (to produce) | canonical `content/ connections/ sources/`, `schema/VERSION.yaml`, registries, vocabularies |
| Outputs | JSON: `entities[]`, `connections[]`, `sources[]`, `export_version`, `schema_version`, `relation_registry(_version)`, `vocabularies`, `content_hash`, entity_count fields |
| Errors | Gate failure ⇒ export not written (atomicity by gate-all-or-nothing; verify_all fail-closed) |
| AuthN/AuthZ | None (public file) |
| Compatibility policy | Additive within major version: old 2.x readers ignore new members; breaking changes → major bump (default policy §15.1; project history consistent: 2.0.0→2.1.0→2.2.0 all additive) |
| Deprecation policy | No field removed within 2.x without new major + MIGRATIONS.md entry (observed convention; not yet owner-ratified as policy) |
| Migration path | MIGRATIONS.md documents 2.0.0→2.2.0 lineage |
| Related requirements | REQ-STEMMA-EXP-001, -002, -003; REQ-STEMMA-SCH-002 |
| Related verification | test_deterministic_export (unit), CI freshness/determinism jobs (integration) |
