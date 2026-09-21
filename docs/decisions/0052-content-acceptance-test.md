# ADR-0052: Content as Acceptance Test Before IRI Gate

Status: Decided
Date: 2026-09-21
Baseline: ADR-0044
Related: docs/ARCHITECTURE-V2.md Part 10 Phase 4, docs/IMPLEMENTATION-PLAN-V2.md Phase 4

## Context

PR #41 said engine for canonicalization not yet built. Previous corpus deleted because engine not built. Need proof engine works — thing PR #41 said doesn't exist yet.

Previous integrated proposal ordered content as acceptance test after projection publication Phase 5, which delays proving engine. Content does not depend on IRI gate, so content acceptance can be before IRI gate.

Need minimal but real content that proves full L8 chain both authority tiers.

## Decision

**Phase 4 Content as Acceptance Test Before IRI Gate** Hours to Days proof engine works thing PR #41 said doesn't exist yet now does but extend to prove full L8 chain both authority tiers:

(a) Register one trusted external institution in agent-registry.yaml exercises delegated authority v2 path with audit.

(b) Seed one source record conforming to source.schema.json SI Brochure 9th ed.

(c) Seed two entities: metre with scientific definition exactly as meter example with reference fundamental quantities visible and phys.force with definition and reference conforming to updated concept.schema.json. Restores file AGENTS.md Quick Start references.

(d) Seed one relational connection with non-empty evidence[] pointing to source record.

(e) Seed one value-claim connection measurement or misconception prevalence exercising value-slot.

(f) One human review pass to canonical via scripts/review.py internal authority.

(g) One delegated-authority import exercising institution path with sample audit.

(h) python3 scripts/verify_all.py + git diff --exit-code -- exports reports.

Exit: Full L8 chain proven end-to-end both authority tiers. Corpus has 3-5 entities 2-3 connections real content. Engine is built.

This phase integrates early work from start as implementation of architecture v2:

- Reset to beginning 0 new primary PDF ingestion HITL markdown explicit edit — content/physics/measurement-units/metre.md 1 entity metre via HITL old 74 archived
- Fundamentals visible length mass time + derived area volume speed weight agreed definitions with refs clean 3D centering — docs/PHYSICS-MINIMAL-DESIGN-V2.md etc explorer clean small nodes thin lines
- Standard scientific definitions exactly as meter example with reference — docs/ARCHITECTURE.md comprehensive all-STEM mediocre coverage now 1 entity metre via HITL
- Clean minimal 3D small nodes thin lines manual legend centered zoom — explorer/
- Evolvable templates frontier model selector DeepSeek harness deterministic scales LLM fallback — scripts/evolvable_template.py webapp/
- Comprehensive all-STEM mediocre 8 domains 97 subdomains 12 entity types — schema/template-registry.yaml
- Explicit separation canonical vs derived vs consumer embeddings RAG consumer's job reference implementation guideline 81KB sample in derived — schema/embedding-registry.yaml consumer-registry.yaml llm-registry.yaml docs/GUIDELINE-EMBEDDER-RAG.md
- Strong CI + explorer + ingestion pipeline nothing bad gets pushed/merged 10 jobs all-green final gate — .github/workflows/ci.yml scripts/verify_all.py verify_strong.py
- Semantic acquisition pipeline 16 stages evidence first-class AI output must be proposal independent verification conflict explicit — scripts/semantic_extract.py verify_claim.py conflict_analysis.py proposal_generate.py entity_resolution.py schema/semantic-claim.schema.json

## Consequences

Easier: proving engine works with minimal real content, restoring AGENTS.md Quick Start references.

Harder: requires seeding real content with evidence[] and human review.

Hard to undo: once content exists removing requires careful scripting.

## Verification

- Full L8 chain proven end-to-end both authority tiers
- Corpus has 3-5 entities 2-3 connections real content
- python3 scripts/verify_all.py green + git diff --exit-code -- exports reports
- Explorer renders, webapp HITL enforced, PDF primary, model selector DeepSeek harness

## Related

- ADR-0044 Phase 4
- ADR-0049 delegated authority v2
- docs/ARCHITECTURE-V2.md Part 10 Phase 4
- docs/IMPLEMENTATION-PLAN-V2.md Phase 4
- PR #41 engine not yet built
