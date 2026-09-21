# DECISION 0015 — Evidence, provenance, source separation

- **Date:** 2026-08-30
- **Status:** decided (Phase A)
- **Related:** decisions 0011, 0013

## Context

Evidence and provenance answer different questions: **Evidence** = why believe this? **Provenance** = where did this assertion come from and who/what produced it? 2025 provenance surveys and nanopublication work separate source lineage from knowledge provenance. Proposed connection duplicated source metadata inside every connection.

Evidence targets proposed `experiment` entities that do not yet exist; requiring them would prematurely force ontology.

Migration proposed `asserted_by: human: migration` — false attribution; migration is a process, not a human assertion.

## Decision

**Separate evidence and provenance; canonical `sources/` objects; no false human attribution.**

Structure:

```yaml
# sources/lhs:src.halliday-resnick.yaml
id: lhs:src.halliday-resnick
type: textbook
citation: "Halliday, Resnick, Walker - Fundamentals of Physics, 12th ed."
locator_authority: publisher
```

```yaml
# connections/lhs:conn.000001.yaml
evidence:
  - type: derivation
    source_ref: lhs:src.halliday-resnick
    locator: "Chapter 5, Eq. 5.12"
    description: "..."
  - type: experiment
    source_ref: lhs:src.cavendish-1798
    locator: "Fig. 3"

provenance:
  asserted_by:
    type: human
    id: human:reviewer.physics-001
    # or: type: llm, id: llm:qwen3.7-plus
    # or: type: unknown, id: unknown:legacy-relationship (for migration)
  generated_by:
    type: process
    id: process:migration.relationships-v0.2
  reviewed_by:
    - type: human
      id: human:reviewer.physics-001
  review_status: unreviewed | reviewed | canonical
  method:
    type: manual | llm_inference | rule_inference | migration
    model: qwen3.7-plus  # when llm
    prompt_version: v3
```

Agent IDs are **namespaced**: `human:*`, `llm:*`, `process:*`, `unknown:*`. First segment = identity class. Agent = who/what produced it; Method = how (PROV-O agents vs activities).

**Evidence references are typed but not hard-validated against nonexistent entity types in v0.2.** Use `source_ref` (must resolve in `sources/`) + optional string evidence; later `experiment/observation/dataset` become first-class entities and `source_ref` migrates to `evidence.target`.

**Migration provenance:** `asserted_by: {type: unknown, id: unknown:legacy-relationship}` + `generated_by: {type: process, id: process:migration.relationships-v0.2}` + `method: migration`. Validator accepts `process` and `unknown` as agent classes; `asserted_by` is optional for `type: proposed`.

## Alternatives considered

- Merge evidence + provenance — rejected: conflates justification with lineage
- Require `experiment` entities now — rejected: premature ontology
- Copy source citation into each connection — rejected: duplication at 1000+ connections

## Reason

Source lineage vs knowledge provenance are distinct (PMC provenance survey). Agent/activity/qualified derivation separation follows PROV-O. `process` category prevents false human attribution.

## Consequences

- `sources/` is lightweight YAML; validator checks `source_ref` resolution
- v0.3 may promote `evidence.target` to entity references when those types exist
