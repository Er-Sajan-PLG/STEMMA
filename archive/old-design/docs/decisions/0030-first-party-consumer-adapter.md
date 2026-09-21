# DECISION 0030 — First-party consumer adapter (Python SDK, CLI, local JSON API)

- **Date:** 2026-09-04
- **Status:** decided and implemented
- **Related:** ADR-0001, ADR-0007, ADR-0027, ADR-0028, ADR-0029, `docs/CONSUMERS.md`

## Context

STEMMA's architecture deliberately publishes a validated export rather than a
service boundary. That keeps the canonical layer simple, but every consumer
still needs a small amount of repeated glue code:

- load the export safely,
- reject unsupported contract majors,
- filter active/reviewed/canonical/trusted edges consistently,
- resolve deprecated entity IDs,
- expose a minimal query surface for downstream tools.

Today the repository ships one first-party consumer (`explorer/`), but it is a
browser-facing application rather than a lightweight reusable adapter.

## Decision

STEMMA ships a **first-party, read-only Python consumer adapter** in
`adapters/python/` with these properties:

1. **Zero runtime dependencies** beyond the Python standard library.
2. **Consumer-only scope**: it reads the export and never writes canonical or
   derived repository data.
3. **Three surfaces** over the same validated export:
   - a Python SDK (`stemma_adapter.Stemma`),
   - a CLI (`stemma-adapter`),
   - a local read-only JSON API (`ThreadingHTTPServer`).
4. **Package identity**: distribution name `stemma-adapter`.
5. **License**: MIT, under the existing code license scope (`LICENSE-CODE`).
6. **Release posture**: in-repo adapter release `0.1.0` may ship with the
   repository; promotion to adapter `1.0` and any PyPI publication are
   explicit **human-gated** decisions.

## Deliberate constraint

The adapter validates the export contract it consumes, but it does **not**
reconstruct the full producer-side governance layer. In particular, the export
currently does not include `schema/relation-registry.yaml`, so relation-family
metadata is **not introspectable from the export alone**. The adapter therefore
supports literal relation-name queries and mirrors policy behavior, while the
relation-registry-in-export question remains an honest gap.

## Alternatives considered

### 1. Keep adapters fully consumer-owned only

Rejected for first-party bootstrapping. The architecture still says consumers
own their downstream integrations, but a maintained reference adapter reduces
repeated contract-loading bugs and documents the intended consumption pattern.

### 2. Ship a network service instead of a local adapter

Rejected. A hosted API would violate the current architectural boundary: STEMMA
publishes a validated file, not an online platform.

### 3. Use a third-party web framework or validation stack

Rejected. The adapter is deliberately standard-library-only so it remains easy
to audit, embed, and run in constrained environments.

## Consequences

- STEMMA now has a first-party example of safe export consumption outside the
  explorer.
- Consumers gain a small stable surface for loading, resolving, searching, and
  traversing the graph without cloning the whole producer toolchain.
- The adapter becomes part of the checked code surface and must stay green in
  `scripts/verify_all.py`.
- PyPI is **not** implied by implementation; publication remains a separate
  human product/release decision.
