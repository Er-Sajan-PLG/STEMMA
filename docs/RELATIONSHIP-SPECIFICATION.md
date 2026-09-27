# RELATIONSHIP-SPECIFICATION (BEGINNING, NO LEGACY, HITL, EVOLVABLE, FRONTIER)

**Status:** Beginning clean, 1 entity (metre) via PDF primary ingestion with HITL, deterministic scales, evolvable templates, model selector like DeepSeek harness (local + frontier models). Old 74 entities archived.

## Allowed Relations

- **Physics core (ADR-0042):** the minimal 8 — mathematically_requires,
  derived_from, appears_in_law, applies_to, generalizes, special_case_of,
  part_of, approximates. `related_to` is forbidden in physics core
  (machine-checked by `physics_core_profile_check.py`).
- **Registry-wide:** `schema/relation-registry.yaml` v1.0.0 is the
  authoritative vocabulary — 15 adopted relations, including ADR-0048
  `equivalent_to` and `misconception_of`, plus general-purpose relations
  available outside the physics-core profile (`logically_requires`,
  `analogous_to`, `bridges`, `related_to`, …).

Each connection must have evidence ≥ 1 with source_ref+locator+description, mandatory.

## Evidence + HITL

Every connection needs evidence with type, stance, source_ref (must resolve to sources/ with url/doi/isbn), locator (page), description (why source supports claim).

HITL: Even LLM-generated connections require human edit before canonical — audit trail candidate_edited by human:*, writer human:*, markdown explicit — hitl_check.py enforces.

## Scaling + Evolvable + Frontier

- Deterministic scales: template-registry.yaml regex + exact SI constants, no LLM, scales
- Evolvable: add new domains without code change
- LLM fallback only when PDF missing exact SI: frontier models DeepSeek R1, Claude 3.5 Sonnet, GPT-4o, Gemini 2.5 Pro, Llama 3.3, custom via OpenRouter/NVIDIA NIM, selector like DeepSeek harness
- Even LLM requires HITL: human explicitly edits markdown before canonical

## No legacy

Old 74 entities archived to archive/beginning-74-entities/. This is beginning clean with HITL, deterministic scales, evolvable, frontier.
