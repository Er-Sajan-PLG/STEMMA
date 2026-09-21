# PILOT CHARTER — Specification Recovery Pilot (Protocol v3.1)

| Field | Value |
|---|---|
| Protocol | Specification Recovery Protocol v3.1 (Pilot Edition) |
| Repository | Er-Sajan-PLG/STEMMA (`/home/user/STEMMA`) |
| Baseline commit | `fb66dd9` (branch `arena/01a0c5b1-stemma`, 2026-09-22) |
| Selected slice | **Canonical corpus → deterministic gate → derived export** ("CORE-GATE-EXPORT slice") |
| Slice boundaries | IN: `content/`, `connections/`, `sources/`, `schema/`, `scripts/validate.py` + gate chain (`verify_all.py` and its steps), `exports/`, related CI jobs and invariant tests. OUT: `webapp/`, `explorer/`, `adapters/` (except version/contract surface), `ingestion/semantic-pipeline` scripts, RAG internals, `examples/`, `archive/` (history only) |
| Why this slice | It is the system's heart: externally observable contract (`exports/knowledge.json` 2.2.0), the trust boundary (canonical vs derived), the fail-closed gate, security-sensitive invariants (no secrets, HITL, ID immutability), and it has direct test/CI verification evidence. Repo-wide drift discovered 2026-09-22 makes intent/evidence separation here especially valuable |
| Alternatives considered | (a) Webapp HITL ingestion slice — larger UI surface, more provider externalities; deferred as second pilot. (b) RAG/embeddings slice — derived/INFO-level; lower authority stakes. (c) Whole-repo — rejected by protocol §1 (pilot-first) |
| Deliberate exclusions | RAG answer quality/evaluation, embedding model performance, UI behavior, performance/scale benchmarking (R8), cross-repo consumer behavior |
| Dependencies | Python ≥3.10, pyyaml/jsonschema (requirements.txt), git history, GitHub Actions CI definition |
| Authority mode | **SOLE_OWNER** — Repository owner (Sajan, "Principal Architect") is Specification Owner, Approval Authority, and Baseline Approver. The Arena agent is executor/Provisional coordinator only (Constraint D) |
| Time/effort budget | One working session, ≤5 incremental agent passes; recovery expands only to the minimum viable baseline for the slice |
| Success criteria | All §25 minimum-baseline artifacts exist; validator passes; slice maturity assessed honestly (target L2 — L3 blocked pending owner approval); process review written from measured data |
| Abort/switch conditions | (1) evidence for the gate/export chain proves unreproducible; (2) authority model turns out not to be SOLE_OWNER; (3) budget exhausted before validator green → stop and record in process review |

First ADR: `spec/DECISIONS/ADR-STEMMA-SPEC-001-slice-selection.md`.

**Timebox statement:** overrun is evidence about the methodology, not permission to continue (§1.3).
