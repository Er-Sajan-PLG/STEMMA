# Curation Pilot — v0.2 (15 canonical)

## Batch
15 high-value assertions prioritized by centrality, prerequisite, domain coverage, bridges/analogies/models.

## Reviewer effort
- 3 reviewers: biology-001, physics-001, chemistry-001; ~2 min per assertion with `review.py show` + evidence check

## Evidence availability
- Structural/hierarchical: axiomatic evidence added where missing (acceptable per protocol)
- Dependency: textbook citations present or added (halliday-resnick, atkins)
- Bridges/analogies/models: curated evidence with source_ref

## Relation ambiguity
- 0 ambiguous forced; remain related_to (177) preserved

## Schema friction
- review_history required schema patch (added to connection.schema.json)

## False-positive proposal rate
- 36 proposals, 12 curated accepted, 0 auto-canonicalized

## Canonicalization consistency
- All 15 passed gate: reviewer, semantics, source/target, context, evidence, provenance, origin preserved, history recorded

## Systematic problems
- None requiring architecture redesign; relation registry domain for bridges/analogous_to needed broadening (done)
