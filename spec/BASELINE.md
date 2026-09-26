# SPECIFICATION BASELINE — STEMMA pilot (CORE-GATE-EXPORT)

- **Baseline ID:** BASELINE-STEMMA-2026-09-22-PILOT-CORE-GATE-EXPORT
- **Repository commit at freeze:** `fb66dd9` (working tree = `fb66dd9` + uncommitted `spec/` additions only; zero modifications to code, schema, docs, content, or CI)
- **Date:** 2026-09-22
- **Scope:** pilot slice CORE–GATE–EXPORT only (charter `spec/PILOT_CHARTER.md`). Non-slice maturity MUST NOT be generalized from this document.
- **Approval status:** ⏳ **PENDING — awaiting SOLE_OWNER (Sajan).** The recovery executor is PROVISIONAL and may not approve baselines. Non-response is not approval.

## §25 minimum viable baseline checklist

| # | Artifact | Path | State |
|---|----------|------|-------|
| 1 | Pilot charter (slice, budget, abort conditions) | spec/PILOT_CHARTER.md | ✅ written; slice recorded as ADR-STEMMA-SPEC-001 |
| 2 | Roles & authority model (§4) | spec/ROLES_AND_AUTHORITY.md | ✅ SOLE_OWNER model recorded; executor non-actions explicit |
| 3 | Domain registry | spec/DOMAIN_REGISTRY.md | ✅ 10 domains: CORE GATE EXP SCH HITL SEC OPS INTEG RAG SPEC |
| 4 | Evidence register (classified) | spec/EVIDENCE_REGISTER.md | ✅ 37 records, FACT/CLAIM/INFERENCE + confidence + locators |
| 5 | As-built description | spec/AS_BUILT.md | ✅ present-state only, evidence-backed |
| 6 | External constraints | spec/EXTERNAL_CONSTRAINTS.md | ✅ XC-1..XC-7 |
| 7 | Open questions | spec/OPEN_QUESTIONS.md | ✅ 6 UNRES, none closed by executor |
| 8 | Conflict records | spec/CONFLICTS.md | ✅ 1 OPEN (CONFLICT-STEMMA-EXP-001) / 1 RESOLVED with authority level; no free interpretation field |
| 9 | Requirements (full §8.6 schema) | spec/REQUIREMENTS.md | ✅ 22 records, **ALL PROPOSED** — nothing self-approved |
| 10 | Recovered specification | spec/SPECIFICATION.md | ✅ v0.1.0-pilot.CORE-GATE-EXPORT, ⟦recovered-unapproved⟧ marks |
| 11 | Interface contracts | spec/INTERFACES/ | ✅ IFACE-STEMMA-EXP-001 (knowledge.json 2.2.0), IFACE-STEMMA-GATE-001 (verify_all CLI) |
| 12 | Decision records | spec/DECISIONS/ + docs/decisions/ | ✅ ADR-STEMMA-SPEC-001 (recovery layer); historical ADR-0040..0052 cross-linked, 0001–0039 located in archive/old-design/ |
| 13 | Assumptions | spec/ASSUMPTIONS.md | ✅ 5 ASM records |
| 14 | Verification mapping | spec/VERIFICATION.md | ✅ all 22 requirements UNVERIFIED per §9.1 (PROPOSED cannot be VERIFIED) |
| 15 | Gap analysis (two tiers) | spec/SPECIFICATION_GAP_ANALYSIS.md | ✅ Tier-1 deep slice findings + Tier-2 ASSESSED/NOT_YET_ASSESSED/OUT_OF_SCOPE inventory |
| 16 | Machine-readable canonical set | spec/machine-readable/*.yaml | ✅ 8 canonical registries + 2 derived mirrors, single representation per datum |
| 17 | Minimum validator (§22.2) | spec/machine-readable/validate_recovery.py | ✅ 9/9 checks PASS; negative-path tested (fails closed) |
| 18 | Baseline + maturity | **this file** | ✅ (approval pending owner) |
| 19 | Process review | /SPECIFICATION_PROCESS_REVIEW.md (repo root) | ✅ written |

Checklist verdict: **minimum viable baseline COMPLETE (artifacts); NOT APPROVED (authority).**

## Maturity declaration (L0–L6)

**Declared level: L2 — evidence-backed recovered specification, scoped to the pilot slice.**

| Attribute | Value |
|---|---|
| Scope | CORE–GATE–EXPORT pilot slice only (22 requirements, 2 interfaces). Repo-wide maturity is **not claimed**; Tier-2 explicitly marks webapp/adapters-internals/explorer/ingestion/RAG internals NOT_YET_ASSESSED |
| Assessor | Recovery executor (self-assessment). **Limitation: assessor is not independent** — sole-owner context, see spec/ROLES_AND_AUTHORITY.md |
| Evidence | EVIDENCE_REGISTER.md (37 locatable records, classified); validate_recovery.py PASS 9/9; `verify_all.py` gate green at fb66dd9; validator negative-path test fails closed |
| Blocking levels | **L3 (approved baseline) blocked**: requires SOLE_OWNER approval of 22 PROPOSED requirements + this baseline. **L4 (verified) blocked**: §9.1 forbids VERIFIED before APPROVED. L5/L6 (enforced / converged) out of pilot scope |

**What L2 does NOT mean:** it does not mean the statements are approved, verified, normative, or complete for the repo. It means: every substantive statement carries evidence or an explicit non-fact classification; unknowns are recorded as UNRES, not smoothed over; no claim was elevated from INFERENCE to FACT.

## Freeze conditions for the next step

1. Owner reviews `spec/` (entry points: REQUIREMENTS.md, OPEN_QUESTIONS.md, CONFLICTS.md).
2. Owner approves/rejects/defers each requirement (approval workflow DRAFT→PROPOSED→APPROVED/REJECTED/DEFERRED); only APPROVED counts for future conformance.
3. On approval: executor may re-run validator (approval-metadata checks 6–7 will then exercise the APPROVED path) and begin VERIFICATION executions from spec/VERIFICATION.md.
4. Post-pilot queue unchanged: **R5** (org/domain/IRI-base decision, human — UNRES-STEMMA-CORE-001) → **R4** content acceptance test per ADR-0052. Recovery does not reorder these.
