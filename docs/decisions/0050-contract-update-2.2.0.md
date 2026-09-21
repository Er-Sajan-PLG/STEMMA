# ADR-0050: Contract Update 2.2.0 — Value-Slot + Delegated Authority

Status: Decided
Date: 2026-09-21
Baseline: ADR-0044, ADR-0045, ADR-0049
Related: docs/ARCHITECTURE-V2.md Part 10 Phase 2, schema/export.schema.json, schema/VERSION.yaml

## Context

Export contract v2.1.0 does not support value-slot claims or delegated authority. Need to bump to 2.2.0 with authority field and value-slot support, update adapters and explorer.

## Decision

**Export version bump:** 2.1.0 → 2.2.0 in schema/export.schema.json and schema/VERSION.yaml.

Add to export shape:
- authority field internal|delegated in provenance.reviewed_by[] and review_history[]
- value-slot support target XOR value amount lowerBound upperBound unit interim allowlist QUDT/UCUM/SI symbols

**Adapter update:** adapters/python/ to handle value-slot claims and delegated authority, round-trips.

**Explorer update:** explorer/ to render value-slot claims and authority filter, clean small nodes thin lines manual legend centered zoom 8 domains theme trust distribution search filter.

**Docs update:** docs/CONSUMERS.md with new contract surface trust thresholds consumer choices export carries all active objects at every review state with authority field exposed consumers filter status rank evidence presence authority.

Exit: Export contract bumped, adapter round-trips, explorer renders, gate green.

## Consequences

Easier: consumers can filter internal vs delegated, render measurements as first-class value-claims.

Harder: contract bump may be breaking for consumers expecting target always present, should be minor 2.2.0 additive but could be major 3.0.0 if breaking, need to decide via ADR.

Hard to undo: once 2.2.0 published changing back breaks consumers.

## Verification

- export_version matches schema/VERSION.yaml
- Adapter round-trips value-slot and authority
- Explorer renders value-slot claims and authority filter
- docs/CONSUMERS.md updated

## Related

- ADR-0044 Phase 2
- ADR-0045 value-slot
- ADR-0049 delegated authority v2
- docs/ARCHITECTURE-V2.md Part 10 Phase 2
