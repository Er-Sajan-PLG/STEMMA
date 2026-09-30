# SPECIFICATION BASELINE — STEMMA pilot (CORE-GATE-EXPORT)

- **Baseline ID:** BASELINE-STEMMA-2026-09-22-PILOT-CORE-GATE-EXPORT
- **Approval record:** **APPROVED 2026-10-01** by Sajan (`human:curator.001`), amending the 2026-09-22 freeze.
- **Repository commit at freeze:** `fb66dd9` (working tree = `fb66dd9` + uncommitted `spec/` additions only; zero modifications to code, schema, docs, content, or CI)
- **Date:** 2026-09-22
- **Scope:** pilot slice CORE–GATE–EXPORT only (charter `spec/PILOT_CHARTER.md`). Non-slice maturity MUST NOT be generalized from this document.
- **Approval status:** ✅ **APPROVED — 2026-10-01** by the SOLE_OWNER (Sajan, `human:curator.001`) for all 24 requirements. The recovery executor is PROVISIONAL and approved nothing; the approval was entered by the owner. Non-response was not treated as approval.

## §25 minimum viable baseline checklist

| # | Artifact | Path | State |
|---|----------|------|-------|
| 1 | Pilot charter (slice, budget, abort conditions) | spec/PILOT_CHARTER.md | ✅ written; slice recorded as ADR-STEMMA-SPEC-001 |
| 2 | Roles & authority model (§4) | spec/ROLES_AND_AUTHORITY.md | ✅ SOLE_OWNER model recorded; executor non-actions explicit |
| 3 | Domain registry | spec/DOMAIN_REGISTRY.md | ✅ 10 domains: CORE GATE EXP SCH HITL SEC OPS INTEG RAG SPEC |
| 4 | Evidence register (classified) | spec/EVIDENCE_REGISTER.md | ✅ 80 records, FACT/CLAIM/INFERENCE + confidence + locators |
| 5 | As-built description | spec/AS_BUILT.md | ✅ present-state only, evidence-backed |
| 6 | External constraints | spec/EXTERNAL_CONSTRAINTS.md | ✅ XC-1..XC-7 |
| 7 | Open questions | spec/OPEN_QUESTIONS.md | ✅ 10 UNRES (8 OPEN / 2 CLOSED — UNRES-CORE-002 and UNRES-GATE-001 closed by owner ruling; **UNRES-HITL-002 added 2026-10-01, blocking**); none closed by executor |
| 8 | Conflict records | spec/CONFLICTS.md | ✅ 1 OPEN (CONFLICT-STEMMA-EXP-001) / 1 RESOLVED with authority level; no free interpretation field |
| 9 | Requirements (full §8.6 schema) | spec/REQUIREMENTS.md | ✅ 24 records, **ALL APPROVED 2026-10-01** — owner-approved; nothing self-approved |
| 10 | Recovered specification | spec/SPECIFICATION.md | ✅ v0.1.0-pilot.CORE-GATE-EXPORT (see SPECIFICATION.md for approval marks) |
| 11 | Interface contracts | spec/INTERFACES/ | ✅ IFACE-STEMMA-EXP-001 (knowledge.json 2.2.0), IFACE-STEMMA-GATE-001 (verify_all CLI) |
| 12 | Decision records | spec/DECISIONS/ + docs/decisions/ | ✅ ADR-STEMMA-SPEC-001 (recovery layer); historical ADR-0040..0052 cross-linked, 0001–0039 located in archive/old-design/ |
| 13 | Assumptions | spec/ASSUMPTIONS.md | ✅ 5 ASM records |
| 14 | Verification mapping | spec/VERIFICATION.md | ⚠️ **19 VERIFIED · 2 FAILED · 3 UNVERIFIED** (2026-10-01) — CORE-004, EXP-002 criterion 4 and GATE-003 were repaired and re-verified; EXP-003 verified by executing the CI freshness gate (mutation + regeneration controls, EVID-EXP-014/015/016); SEC-002 verified by a full-history key scan with a non-vacuity control (6245 objects, zero keys, EVID-SEC-004/005). **New round-3 finding:** REQ-STEMMA-HITL-001/002 FAILED — the chain's `hitl_check --check-workflow` step audits an empty git-ignored `workflow/` and exits 0 ("nothing to check"), while 6 of 9 canonical entities declare `writer=llm:coding-agent.001`; routed as **UNRES-STEMMA-HITL-002** (owner ruling required). The 3 remaining UNVERIFIED are now recorded at **AC granularity**: EXP-004 AC1 PASS (only AC2 open, needs owner confirmation via UNRES-EXP-001); INTEG-001 AC1/AC2/AC4 PASS with AC3 unmet (no grounded AI chat implemented); OPS-002 alone is blocked purely on a precondition (no tagged releases) |
| 15 | Gap analysis (two tiers) | spec/SPECIFICATION_GAP_ANALYSIS.md | ✅ Tier-1 deep slice findings + Tier-2 ASSESSED/NOT_YET_ASSESSED/OUT_OF_SCOPE inventory |
| 16 | Machine-readable canonical set | spec/machine-readable/*.yaml | ✅ 8 canonical registries + 2 derived mirrors, single representation per datum |
| 17 | Minimum validator (§22.2) | spec/machine-readable/validate_recovery.py | ✅ 9/9 checks PASS; negative-path tested (fails closed) |
| 18 | Baseline + maturity | **this file** | ✅ APPROVED 2026-10-01 by owner |
| 19 | Process review | /SPECIFICATION_PROCESS_REVIEW.md (repo root) | ✅ written |

Checklist verdict: **minimum viable baseline COMPLETE and APPROVED (2026-10-01).**

## Maturity declaration (L0–L6)

**Declared level: L3 — approved specification baseline, scoped to the pilot slice.**

*History: declared **L2** (evidence-backed, unapproved) on 2026-09-22. Raised to **L3** on
2026-10-01 when the SOLE_OWNER approved all 24 requirements and this baseline.*

| Attribute | Value |
|---|---|
| Scope | CORE–GATE–EXPORT pilot slice only (24 requirements, 2 interfaces). Repo-wide maturity is **not claimed**; Tier-2 explicitly marks webapp/adapters-internals/explorer-product-layer/ingestion/RAG internals NOT_YET_ASSESSED |
| Assessor | Recovery executor (self-assessment). **Limitation: assessor is not independent** — sole-owner context, see spec/ROLES_AND_AUTHORITY.md |
| Evidence | EVIDENCE_REGISTER.md (41 locatable records, classified); validate_recovery.py PASS 9/9 with the APPROVED path exercised; `verify_all.py` gate green; validator negative-path test fails closed |
| Approval | **APPROVED 2026-10-01** by Sajan (`human:curator.001`) — approver + approval_date present on all 24 records (validator check 6); verification method named on all 24 (check 7) |
| Blocking levels | **L4 (verified) now UNBLOCKED**: §9.1 prohibits VERIFIED before APPROVED; approval has been given, so verification executions may begin. L5/L6 (enforced / converged) remain out of pilot scope |

**What L3 does mean:** every requirement in the slice is owner-approved and carries
evidence or an explicit non-fact classification; the approval is recorded with a named
human approver and date; the gate and validator are green; unknowns remain recorded as
UNRES rather than smoothed over.

**What L3 does NOT mean:** it does **not** mean the requirements are *verified* (§9.1 — L4
is the next step and is now permitted), does not extend maturity to the repo as a whole,
and does not assert that the approved statements are complete or defect-free. Approval is
"this accurately describes the system as it exists and should continue to"; it is not a
claim of perfection, and a REJECTED or DEFERRED requirement may still be revised and
re-proposed through the same workflow.

## Freeze conditions for the next step

1. ~~Owner reviews `spec/`~~ — done; entry points were REQUIREMENTS.md, OPEN_QUESTIONS.md, CONFLICTS.md, and the pre-approval SOTA comparison (`spec/SOTA-COMPARISON-2026-10-01.md`).
2. ~~Owner approves/rejects/defers each requirement~~ — **done 2026-10-01: all 24 APPROVED.** Only APPROVED counts for conformance.
3. **Next: begin VERIFICATION** from spec/VERIFICATION.md (L3 → L4). §9.1's blocking condition is satisfied; approved requirements may now be executed against their named methods. The validator's approval-path checks (6, 7) are live and passing.
4. Post-pilot queue unchanged: **R5** (org/domain/IRI-base decision, human — UNRES-STEMMA-CORE-001; settled for now as `stemma-urn-only` at R6) → **R4** content acceptance test per ADR-0052. Recovery does not reorder these.
