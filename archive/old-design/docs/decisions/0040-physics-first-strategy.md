# DECISION 0040 — Physics-First Minimal Canonicalization Strategy

- **Date:** 2026-09-21
- **Status:** PROPOSED — awaiting human activation (GOVERNANCE.md Level 1/2)
- **Related:** VISION.md (depth over breadth), ROADMAP.md R1/R2, ADR-0029 (refoundation baseline 3.0.0), ADR-0024 (math layer), DEEP-DIVE-RECOMMENDATIONS.md R1/R3/R4, IMPLEMENTATION-STATUS.md
- **Author:** arena/01a0c072-stemma branch

## Context

STEMMA's engine (validate.py + 4 JSON Schemas + relation registry + vocabularies + deterministic export) is domain-agnostic and already chain-green. The failure mode is not engine impossibility but **curation scalability**.

Evidence from pre-refoundation corpus (224 entities, 654 connections):
- 604 unreviewed assertions (92%)
- 599 connections with empty evidence
- 371 `related_to` (56.7%) as vague fallback, 0 canonical
- 0/224 entities human-reviewed
- Review is the bottleneck by design (human-only canonicalization).

Attempting all STEM (physics, chemistry, biology, earth-space, math, engineering, scientific-practice) at once multiplies review load combinatorially: 7 domains × 9 entity types × 55 relations. Human review does not scale linearly.

VISION.md already states non-goal: "Coverage of the whole of science. Depth and correctness over breadth." This ADR operationalizes that non-goal.

Physics is the optimal first domain:
- Highest consensus (Newton, Maxwell, thermo are stable)
- Most mathematized (equations, dimensions, units give machine-checkable invariants)
- Curriculum-neutral (same laws globally)
- Tests the hardest part of STEMMA: quantity/law/equation/unit modeling + dimensional analysis (ADR-0024)

Current repo state is 0 entities / 0 connections after refoundation (ADR-0029) — ideal time to start depth-first.

## Decision

**Depth-first, physics-only for v0.1.**

1. **Scope for v0.1 (NOW):** Physics core only — subdomains `mechanics`, `electricity-magnetism`, `thermal-physics` + `measurement-units` for units. ~70 entities, ~150 connections, 5 canonical source records. Other physics subdomains (`waves-optics`, `atomic-nuclear`) and other STEM domains are LATER.

2. **Success is a vertical slice, not breadth:** Content + connections + sources + gate + export v2.1.0 + explorer visualization + adapter search must all work for physics. If the vertical slice works, the engine is proven.

3. **Governance:** Update GOVERNANCE.md §3: NOW = physics-core v0.1 + ADR-0024 partial activation. LATER = other physics subdomains, then chemistry. OUT = curriculum mapping, grade tags (still forbidden).

4. **Roadmap:** Rewrite ROADMAP.md R1/R2 to physics-core (see PHYSICS-FIRST-IMPLEMENTATION-PLAN.md §10). Old generic R1 moves to R3.

5. **Exit criteria for v0.1:**
   - `verify_all.py` exit 0
   - 70 physics entities human_reviewed, 150 connections canonical, 5 sources
   - Zero `related_to` in physics/
   - Explorer shows connected DAG (not isolated dots)
   - Adapter: `/v2/search?q=force&domain=physics` returns force + its mathematically_requires closure
   - `status_truth.py` physics count >0, README status block updated via CI

## Alternatives Considered

- **Continue all-STEM breadth:** Rejected — repeats pre-refoundation failure; review bottleneck unsolved; 224 entities already proved unreviewable.
- **Chemistry-first or biology-first:** Rejected — less consensus, less mathematized, harder to machine-validate; physics gives dimensional checks as CI.
- **No domain reduction, just better tooling:** Rejected — tooling already exists (review.py, campaign worksheets); bottleneck is human attention, not tooling.
- **Zero relations (glossary):** Rejected — violates VISION tagline ("relationships between them") and ARCHITECTURE invariant (connections-only truth). Graph value disappears. See ADR-0042.

## Consequences

- Positive: Review load drops ~80% (70 vs 224+), focus enables 1 expert to finish in days, proves engine with hardest science, creates reference pattern for other domains.
- Negative: Other domains deferred; consumers wanting biology/chemistry must wait. Mitigated by explicit LATER classification and documentation.
- Neutral: No schema/registry breaking change — additive content only. Schema version stays 1.1.0, export 2.1.0.

## Implementation

See `docs/PHYSICS-FIRST-IMPLEMENTATION-PLAN.md` Phases P0-P4. Requires ADR-0041 (minimal profile) and ADR-0042 (minimal relation set) as companion.

## Open Questions

- Should physics-core include `waves-optics` in v0.1? Proposal says no, to keep 70 target. Could expand to 100 if expert available.
- Who is `human:reviewer.physics-001`? Needs ORCID-backed identity per GOVERNANCE.

## Status History

- 2026-09-21: PROPOSED on arena/01a0c072-stemma
