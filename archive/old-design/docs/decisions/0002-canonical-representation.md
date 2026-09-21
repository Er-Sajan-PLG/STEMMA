# DECISION 0002 — Canonical representation

- **Date:** 2026-08-12
- **Status:** decided (documented); format approval pending in the human-decision list
- **Related:** specification §2

## Context

The canonical source of truth must be human-readable, machine-readable, version-controlled,
diffable, and independent of any product, database, or language.

## Alternatives considered

- Pure JSON or YAML files (machine-readable but poor for prose definitions)
- Markdown + YAML frontmatter (prose body + machine metadata) ← **chosen**
- A database as canonical source (rejected: not version-friendly, not portable)
- RDF/OWL/JSON-LD now (rejected: standards prestige, premature)

## Decision

Canonical entities = one Markdown file each, YAML frontmatter (the machine data) + prose `##`
body. Schema in `schema/concept.schema.json`; export in `exports/` is **derived**.

## Reason

Markdown+YAML gives readable prose plus validated metadata, is diffable in git, needs no database,
and is simple to validate with PyYAML + JSON Schema (already installed).

## Consequences

- Canonical files are the source of truth; derived artifacts are regenerable and never authoritative.
- No database, no semantic-web stack for v0.1.

## Status

**decided (documented).** Final format approval is human item 5.
