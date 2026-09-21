# SPECIFICATION PROCESS REVIEW — STEMMA recovery pilot

Mandatory protocol deliverable (repo root). Reviews the *process*, not the content.
Content entry point: `spec/REQUIREMENTS.md`.

- **Pilot:** SPECIFICATION RECOVERY PROTOCOL v3.1 (Pilot Edition), single pass over the CORE–GATE–EXPORT vertical slice
- **Commit baseline:** `fb66dd9` + uncommitted `spec/` tree (zero repo-behavior modifications)
- **Date:** 2026-09-22 · **Executor:** Arena recovery agent (PROVISIONAL authority) · **Authority:** Sajan (SOLE_OWNER)

## 1. What was exercised (phases 0–8)

| Phase | Deliverable | Gate verdict |
|---|---|---|
| 0 Charter | spec/PILOT_CHARTER.md (budget, abort conditions, slice → ADR-STEMMA-SPEC-001) | PASS |
| 1 Evidence → As-Built | EVIDENCE_REGISTER.md (37), AS_BUILT.md | PASS |
| 2 Needs/Intent recovery | requirements origin classification (RECOVERED/PROPOSED/DERIVED/EXTERNAL), validation_basis per record | PASS |
| 3 Requirements | REQUIREMENTS.md — 22 × full §8.6 schema, ALL PROPOSED | PASS (nothing self-approved) |
| 4 Specification | SPECIFICATION.md v0.1.0-pilot with ⟦recovered-unapproved⟧ marks | PASS |
| 5 Architecture/Decision | spec/DECISIONS/ two-layer model; historical ADR-0001..0039 located in archive/old-design, 0040..0052 cross-linked | PASS |
| 6 Verification design | VERIFICATION.md — all UNVERIFIED by §9.1 rule; methods bound, procedures drafted | PASS |
| 7 Gap analysis | SPECIFICATION_GAP_ANALYSIS.md Tier-1 (deep) + Tier-2 (coverage inventory) | PASS |
| 8 Baseline + validator | machine-readable/*.yaml ×10, validate_recovery.py 9/9 PASS + negative-path test, BASELINE.md + maturity L2 | PASS (approval pending) |

## 2. Measured metrics

| Metric | Value |
|---|---|
| Evidence records | 37 (FACT 30 / CLAIM 5 / INFERENCE 2) |
| Requirements | 22 (P0 7, P1 12, P2 3) — 100% PROPOSED, 0% approved (correct: executor has no approval power) |
| Interfaces | 2 (EXP knowledge.json 2.2.0; GATE verify_all CLI) |
| Decisions | 1 recovery-layer ADR + 15 living historical ADRs cross-linked + ~39 archived located |
| Open questions | 6 UNRES (2 blocking) |
| Conflicts | 2 (1 OPEN: meta.json "faiss" label vs JSON fallback; 1 RESOLVED with owner-ratification pending) |
| Assumptions | 5 |
| Verification executions | 0 (correct: §9.1 forbids VERIFIED before APPROVED) |
| Validator checks | 9/9 PASS; negative-path confirmed fail-closed |
| Requirements with locatable evidence | 22/22 (via source: + traceability.yaml, validator-enforced) |
| Registry↔markdown parity | enforced as mirror discipline; validator is executable arbiter |

## 3. Methodology sections NOT exercised (honest list)

| Section/capability | Why unexercised |
|---|---|
| DRAFT→APPROVED transition mechanics on real records | Executor lacks authority; transition path exercised only in validator negative test |
| SUPERSEDED lifecycle (superseded_by chains) | v1 revision series; no supersessions yet |
| VERIFIED/FAILED verification executions | §9.1 blocked pre-approval |
| Multi-reviewer / delegated approval (§4 non-sole-owner modes) | Repo authority mode is SOLE_OWNER; delegation records (ADR-0049) not re-exercised by recovery |
| Repo-wide Tier-1 depth recovery | Charter forbids expansion before this review is evaluated |
| Cross-repo conformance (LearningHub, professor-j) | Consumer ownership UNASSIGNED (UNRES-STEMMA-INTEG-001) |
| Tooling beyond minimum validator | Charter forbids |
| R4 content acceptance test | Explicitly deferred; recovery must not start it |

## 4. Deviations from protocol (recorded, with disposition)

1. **Charter placement.** Initial draft placed PILOT_CHARTER.md at repo root; §27 canonical layout requires `spec/`. Corrected mid-pilot via `git mv` before baseline freeze; no content change. Disposition: closed, spec/PILOT_CHARTER.md is canonical.
2. **Evidence count bookkeeping.** An early header comment said 28 records; actual canonical count is 37 (a grep pattern had over-counted related-ID lines, then arithmetic was mis-totalled). Corrected in evidence.yaml header. Disposition: closed; validator counts records (not grep) and is authoritative.
3. **Historical ADR locators.** Pre-0040 ADRs are not files in docs/decisions/ (retired per ADR-0044); references were aimed at archive/old-design/docs/decisions/. Validator resolves both locations. Disposition: closed; validator check 4 encodes the two-location rule.
4. **One provisional conflict resolution.** CONFLICT-STEMMA-SCH-001 was RESOLVED by the executor applying the domain-profile scope rule. This edges toward the "executor must not resolve conflicts" boundary; it is recorded with authority_required = SOLE_OWNER ratification and is reopenable. Disposition: flagged for owner review.

## 5. Findings about the process itself

- **Pilot-first worked.** The slice was completable end-to-end in one pass; every §31 gate was checkable because the slice is small (22 requirements).
- **The approval firewall held.** Zero self-approvals occurred; the machine-readable set makes self-approval mechanically detectable (validator check 6).
- **Evidence-first discipline caught two documentation-class defects** the repo's own gates had not (CONFLICT-STEMMA-EXP-001 metadata kind-mismatch; UNRES-STEMMA-HITL-001 non-portable audit trail).
- **Cost driver:** full §8.6 schema per requirement is heavy for 22 records but pays off in validator strictness — recommend keeping for pilot, evaluating schema slimming only in owner review.

## 6. Recommendations to the SOLE_OWNER (next actions, in order)

1. Review spec/REQUIREMENTS.md → approve/reject/defer (blocks L3, L4, all verification).
2. Ratify or reopen CONFLICT-STEMMA-SCH-001 resolution (deviation 4).
3. Rule on the 2 blocking UNRES: UNRES-STEMMA-CORE-001 (IRI base — this is R5), UNRES-STEMMA-HITL-001 (audit-trail portability).
4. Only then: evaluate expanding recovery beyond the pilot slice (Tier-2 NOT_YET_ASSESSED areas) — expansion is **not authorized** until steps 1–3.
5. R4 (ADR-0052) proceeds on its own merits after R5, unchanged by this recovery.
