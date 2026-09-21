# CONFLICTS registered for the CORE-GATE-EXPORT slice

Protocol §12. Conflicts are relationships between sources — recorded, never
silently resolved. Machine copy: `spec/machine-readable/conflicts.yaml`.

---

## CONFLICT-STEMMA-EXP-001 — Vector store labelled `faiss` while implemented as JSON fallback

- **Sources:**
  1. Implementation: `scripts/embed.py:227` writes `"type": "faiss"` unconditionally; fallback at `:241-244` writes `vectors.json` when numpy/faiss absent. Result observed: `exports/vector_store/meta.json` says `"type": "faiss"` beside a JSON store. [EVID-STEMMA-EXP-004 — FACT/HIGH]
  2. Living docs (55 mentions across CONSUMERS/GOVERNANCE/RAG/EMBEDDINGS, sampled) describing the store as "vector_store/ FAISS". [EVID-STEMMA-EXP-004 related — CLAIM]
- **Conflicting statements:** "The store is FAISS" vs "the store is a deterministic JSON file set (today)".
- **Nature:** label/behavior divergence; documentation lag; minor contract ambiguity for consumers parsing meta.json.
- **Observed behavior (INFERENCE — not an authoritative resolution):** the JSON fallback is intentional demo behavior; the `faiss` label is aspirational/default-written regardless of actual backend.
- **Authority level required:** REPOSITORY_LOCAL (owner decides: honest `type` field vs FAISS-only store).
- **Impact:** LOW — consumer guidance may mislead; meta.json consumers may branch on a wrong type.
- **Resolution status:** OPEN · **Resolution authority:** Sajan · **Decision reference:** pending.

## CONFLICT-STEMMA-SCH-001 — "related_to forbidden" vs registry adopting `related_to` (RESOLVED — scope rule)

- **Sources:** physics-core check forbids `related_to` in physics (EVID-STEMMA-SCH-002) vs relation registry adopting 15 relations incl. `related_to` (same EVID).
- **Nature:** apparent contradiction; resolved by explicit scoping: the prohibition applies to the physics-core profile, not the registry vocabulary. RELATIONSHIP-SPECIFICATION.md updated 2026-09-22 to state both tiers.
- **Authority level required:** REPOSITORY_LOCAL.
- **Resolution status:** RESOLVED (docs scoping fix, commit fb66dd9; docs-consistency + registry coherence gates green).
- **Decision reference:** `git show fb66dd9 -- docs/RELATIONSHIP-SPECIFICATION.md`; ADR-0042 (physics minimal set) + ADR-0048 (registry extension) — historical decision records.
