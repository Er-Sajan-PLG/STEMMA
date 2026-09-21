# DECISION 0017 — Adaptive metadata extension registry (open-but-governed schema seam)

- **Date:** 2026-09-01
- **Status:** decided (implemented with this PR)
- **Related:** decisions 0010, 0011, 0016; `docs/metadata/METADATA-DESIGN-v0.2.md`;
  `schema/extension-registry.yaml`; `schema/concept.schema.json`

## Context

LearningHubSTEM is a canonical foundation that must **outlive any single consumer,
curriculum, or information model**. The foundation will encounter knowledge dimensions
the schema does not yet name. Today every canonical object schema closes with
`additionalProperties: false`. The consequence: a genuinely new, legitimate metadata
dimension **cannot be tagged at all** — it either hard-fails validation or must wait for a
schema release. That contradicts the foundation's purpose (reusable, adaptable, growing).

The connection model already opened one controlled seam — `context.qualifiers[]`
(`additionalProperties: true` on `context`, ADR-0011/0016) — proving the pattern works.
But there is no equivalent governed seam on the **entity / connection / source objects
themselves**, so new top-level dimensions still require a breaking schema edit.

Two failure modes to avoid:
1. **Fully open schema** (`additionalProperties: true` everywhere) — destroys determinism,
   lets typos and junk pass as "metadata", breaks consumers.
2. **Closed schema** (`additionalProperties: false`) — kills adaptability, forces schema
   churn for every new dimension.

## Decision

Introduce a **governed extension registry**: an explicit, versioned, additive open seam.

1. **`schema/extension-registry.yaml`** — the authoritative catalog of extensible
   knowledge-layer dimensions. Each entry declares: `name`, `applies_to`
   (`entity` | `connection` | `source`), `value_type`, optional controlled `enum`
   (single scalar option only — richer structured values live in `context.qualifiers[]`),
   optional `description`, `status` (`proposed` | `adopted`), `registered_by`,
   `registered_at`. A dimension is registered here before it can be used on an object.

2. **`extensions:` object on entity / connection / source** — an **open** map
   (`additionalProperties: true`) so a new dimension never hard-fails the schema. The
   **validator** (not the schema) enforces governance: every `extensions` key must be a
   registered dimension for that object kind, or validation exits 1 with a precise
   "register it" message pointing at `scripts/register_extension.py`.

   This split — *schema open, validator governed* — is the whole point: the schema stops
   being the blocker, and governance is enforced at the mechanical gate instead.

3. **`scripts/register_extension.py`** — one-command registration of a new dimension:
   validates the declaration, appends to the registry, idempotent, refuses to downgrade
   an `adopted` dimension to `proposed`.

4. **`scripts/validate.py`** — gains `check_extensions()`: presence-check for unregistered
   keys, `applies_to` applicability, and controlled-`enum` conformance.

## Alternatives considered

- **Fully open** (`additionalProperties: true` everywhere): rejected — destroys consumer
  determinism and validation value; the existing model deliberately froze objects.
- **Closed + schema release for each field**: rejected — that is the status quo, and it is
  the exact blocker this decision removes.
- **Extend only `context.qualifiers` for everything**: rejected — top-level dimensional
  tags (e.g. a canonical representation of a quantity's symbol set) do not belong nested
  under context conditions.

## Reason

This preserves the foundation's two core invariants simultaneously:
- **Determinism** — registry membership is mechanically enforced; unknown keys fail
  loudly with a fix path, never silently.
- **Adaptability** — registering a new dimension is additive (registry row + use), does
  not change `schema_version`/`export_version`, does not break any consumer, and can be
  done "on the spot" as the knowledge demands.

Seeded extensions are chosen to be **knowledge-layer and curriculum-agnostic** (per the
Northstar: no grade/curriculum in `content/`). Adding "global grade-12 depth" content is
achieved by widening coverage and relationships, **not** by stamping entities with grade
tags — which this decision explicitly leaves prohibited. A curriculum→grade mapping is a
consumer-owned artifact (`docs/`), never canonical content.

## Consequences

- `concept.schema.json`, `connection.schema.json`, `source.schema.json` each gain an
  optional `extensions` open object. `schema_version 0.2` / `export_version 0.1` are
  **unchanged** (additive, backward-compatible; `extensions` defaults to absent/empty).
- `validate.py` enforces registry membership; unregistered use → exit 1 with guidance.
- `scripts/register_extension.py` is the operating contract for "create metadata/schema on
  the spot as necessary".
- A demonstration dimension is registered and used on at least one canonical entity so the
  mechanism is real, tested, and visible.
- No grade / curriculum tags are introduced into `content/` by this decision.

## Status

**decided (implemented with this PR).**