# ADR-0051: Governance Hygiene

Status: Decided
Date: 2026-09-21
Baseline: ADR-0044
Related: docs/ARCHITECTURE-V2.md Part 10 Phase 3

## Context

Stale references, ecosystem coupling, stubbed tests need cleaning before content acceptance test. ADR-0027 owner-ratification gate needs closing.

## Decision

**lhs sweep:** Across all tracked files EXCEPT ADR documents which are history per ADR-0027 §3.

**Fix AGENTS.md dead Quick Start references:** NORTHSTAR.md STEMMA-SPECIFICATION.md retired by ADR-0027 force.md deleted by PR #41.

**Un-stub tests/repo/test_independence.py and remove ecosystem references from AGENTS.md in same PR.**

**Close ADR-0027 owner-ratification gate.**

Exit: No stale references, independence test live, namespace clean.

## Consequences

Easier: clean namespace, no dead refs, independence test live.

Harder: lhs sweep may be large.

Hard to undo: once stale refs removed restoring violates clean.

## Verification

- No stale references NORTHSTAR.md STEMMA-SPECIFICATION.md force.md in tracked files EXCEPT ADR documents
- tests/repo/test_independence.py live not stubbed
- AGENTS.md no ecosystem references

## Related

- ADR-0027 ecosystem decoupling and namespace
- ADR-0044 Phase 3
- docs/ARCHITECTURE-V2.md Part 10 Phase 3
