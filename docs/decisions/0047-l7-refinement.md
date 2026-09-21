# ADR-0047: L7 Refinement Not Blanket Purge

Status: Decided
Date: 2026-09-21
Baseline: ADR-0044
Related: docs/ARCHITECTURE-V2.md Part 1 L7, Part 3.6

## Context

L7 no curriculum, grade, course, country, product semantics in canonical data. STEMMA is knowledge foundation pedagogical metadata belongs to consumers enforced by tests/curation/test_generality.py.

Previous integrated proposal wanted blanket purge of learning_objectives, real_world_applications, common_misconceptions from concept.schema.json. Debate found purge too rigid: real_world_applications and common_misconceptions are knowledge when evidenced, not automatically pedagogical.

Need refined boundary: pedagogical about teaching vs knowledge about world including human beliefs.

## Decision

Refine L7 to distinguish pedagogical vs knowledge:

- Remove learning_objectives, instructional_sequencing from concept.schema.json properties entirely. Extend test_generality.py to reject these keys in frontmatter.
- Allow real_world_applications, common_misconceptions ONLY when evidenced as ValueClaim with evidence[] and source not free-form strings. If present as free-form without evidence → gate error. If present as ValueClaim with evidence → allowed and exported as claim not as property.
- Misconception itself as Entity referent domain misconception with relation misconception_of linking to subject. Misconception prevalence as ValueClaim about misconception entity with evidence.

Examples:
- "Photosynthesis is basis for agriculture" with evidence source — is knowledge, allowed as Claim
- "42% of students think photosynthesis occurs only in sunlight (Source: misconception study 2023)" — is ValueClaim about misconception entity with evidence, allowed
- "Learning objective: students will understand photosynthesis" — is pedagogical, belongs to consumer, rejected from canonical

Distinction: pedagogical about teaching, knowledge about world including human beliefs. Misconception prevalence is knowledge about human beliefs with evidence, allowed as ValueClaim.

Record SOTA-REVIEW §6.5 softer alternative governed extensions as partially adopted via extension-registry.yaml. No properties wrapper: ADR-0017 extensions seam with extension-registry.yaml governance already provides mechanism for structural non-truth fields use existing extension registry.

## Consequences

Easier: preserving knowledge about misconceptions and real-world applications when evidenced, not losing useful data.

Harder: test_generality.py must distinguish pedagogical keys vs evidenced knowledge claims, boundary definition more precise.

Hard to undo: once L7 refined restoring pedagogical fields violates constitution.

## Verification

- learning_objectives key → error
- instructional_sequencing key → error
- real_world_applications free-form without evidence → error
- real_world_applications as ValueClaim with evidence[] → pass
- common_misconceptions free-form without evidence → error
- common_misconceptions as ValueClaim with evidence[] → pass
- Negative tests per key

## Related

- ADR-0044 L7
- docs/ARCHITECTURE-V2.md Part 1 L7, Part 3.6
- tests/curation/test_generality.py
