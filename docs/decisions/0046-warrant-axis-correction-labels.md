# ADR-0046: Warrant Axis + Correction Labels

Status: Decided
Date: 2026-09-21
Baseline: ADR-0044
Related: docs/ARCHITECTURE-V2.md Part 3.5, 3.7

## Context

Assertion type and warrant conflated in previous model. Need surgical separation: how held vs how justified vs why corrected.

Previous assertion.type had 3 values asserted inferred proposed. Some proposals wanted to expand to 6 values including derived disputed hypothesized — conflates warrant with stance, breaks check_assertion_epistemics which requires inference block only for inferred.

Need warrant taxonomy and correction tracking for calibration reports.

## Decision

**Warrant axis:** Keep assertion.type surgical ["asserted","inferred","proposed"] do NOT expand to derived disputed hypothesized. Extend confidence_basis enum currently ["expert_review","experimental","theoretical","derived",null] to serve as warrant taxonomy: add definitional, axiomatic, model_based. Field already exists pairs with confidence avoids breaking check_assertion_epistemics. Update check_assertion_epistemics to handle extended basis without requiring inference blocks for non-inferred types.

- expert_review — reviewed by human expert
- experimental — measured via experiment
- theoretical — derived from theory
- derived — derived via rule
- definitional — defined by standard (e.g., metre per SI Brochure)
- axiomatic — axiomatic definition
- model_based — from model/simulation

**Stance axis:** Via contradicts relation reserved adopt when needed, polarity field, evidence stance.

**Correction axis:** Add optional correction_class field to provenance.review_history[] items:

Enum factual_error | category_error | relationship_error | provenance_error | incompleteness | hallucination | format_error | dangling_ref
Start actively used set at 3 factual_error relationship_error other expand based on Phase 5 review data.
Attaches to individual review decisions not whole claims.
Per L3 never touches model_confidence never sets review_status never infers epistemic_status.

## Consequences

Easier: measuring AI curation quality through correction labels and calibration reports, expressing definitional truth with warrant definitional + evidence.

Harder: authoring canonical content requires understanding Property/Claim/ValueClaim distinction warrant axis.

Hard to undo: once warrant values exist removing requires migrating all claims with those warrants.

## Verification

- Unknown confidence_basis value → error
- assertion.type remains 3-value enum
- Unknown correction_class enum → error
- correction_class attaches to review_history[] items not whole claims per L3

## Related

- ADR-0044 L3 five states never collapsed plus warrant and correction axes
- docs/ARCHITECTURE-V2.md Part 3.5, 3.7
