# ASSUMPTIONS — CORE-GATE-EXPORT slice

Assumptions are not requirements (§17). Transition to approved
constraint/requirement is recorded explicitly when it happens.

## ASM-STEMMA-INTEG-001 — Sole-owner authority is correct

- **Statement:** Sajan is the legitimate SOLE_OWNER of this repository's specification authority.
- **Basis:** repo ownership; proposal authorship line "on behalf of Principal Architect Sajan" (docs.decisions 0044-proposal); owner directive to run this recovery in-session.
- **Risk if false:** entire authority model (approval path) invalid; baseline approval meaningless.
- **Validation method:** owner confirmation at first baseline review.
- **Owner:** Sajan · **Review condition:** first baseline approval session.

## ASM-STEMMA-CORE-001 — `archive/` is immutable history

- **Statement:** Nothing under `archive/` will be re-activated; it may be cited as history only.
- **Basis:** 2026-09-21/22 refoundation + hygiene commits; docs/decisions/README.
- **Risk if false:** exempting archive from live gates (independence/docs invariants) hides drift.
- **Validation method:** INSPECTION per change touching archive/.
- **Owner:** Sajan · **Review condition:** any PR touching archive/.

## ASM-STEMMA-RAG-001 — Deterministic-fake embeddings are demo-grade acceptable

- **Statement:** The hash-based embedding fallback (and JSON vector store) is acceptable as the reference implementation *for demonstration/testing* until real models are configured.
- **Basis:** INFO-not-FAIL design (EVID-STEMMA-GATE-010); docs label it "fake deterministic for demo".
- **Risk if false:** consumers prototype against non-semantic vectors; meta.json mislabeling (CONFLICT-STEMMA-EXP-001) misleads.
- **Validation method:** owner decision via UNRES-STEMMA-RAG-001.
- **Owner:** Sajan · **Review condition:** UNRES-STEMMA-RAG-001 closure.

## ASM-STEMMA-OPS-001 — GitHub Actions remains the CI platform

- **Statement:** CI definitions in `.github/workflows/` accurately describe the executed gate.
- **Basis:** platform binding in repo; no alternative CI evidence.
- **Risk if false:** green-CI claims unverifiable locally.
- **Validation method:** observe CI run on the next PR.
- **Owner:** Sajan · **Review condition:** next PR merge.

## ASM-STEMMA-SCH-001 — 8-domain vocabulary is stable during the pilot window

- **Statement:** `schema/vocabularies/domains.yaml` (8 domains) + subdomains do not change mid-pilot.
- **Basis:** registry v1.0.0 adopted; no open expansion ADR.
- **Risk if false:** slice evidence referencing domains/subdomains needs refresh.
- **Validation method:** gate (domain identity test) on every run.
- **Owner:** Sajan · **Review condition:** any ADR touching domain vocabulary.
