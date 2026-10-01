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
- **Resolution status:** **RESOLVED — truthfulness half fixed 2026-10-01; policy half open.**

  The conflict had two halves that were being treated as one:

  1. **The metadata was untrue** — `meta.json` asserted `type: faiss` while no FAISS
     index existed. This needed no policy ruling: writing the *actual* store type is
     correct under every possible policy. **Fixed** (`scripts/embed.py` now records
     `numpy-flat` / `json-flat` per the store it writes, with a `type_note`; the
     living docs that repeated the claim were synced). A guard,
     `tests/repo/test_vector_store_type_truthfulness.py`, runs the real writer and
     asserts the label matches the file on disk; reverting the writer to the
     hardcoded label turns it red (2 failed), restoring gives 3 passed.
  2. **Whether the hash fallback is *acceptable*** — a genuine product/spec
     decision. **Still open**, tracked as **`UNRES-STEMMA-RAG-001`**.

  The mislabel is therefore no longer a conflict; what remains is a policy
  question, which lives in the `UNRES-` record rather than here.
- **Decision reference:** EVID-STEMMA-EXP-019 (label fix + guard); policy half →
  `spec/OPEN_QUESTIONS.md` § `UNRES-STEMMA-RAG-001`.

## CONFLICT-STEMMA-SCH-001 — "related_to forbidden" vs registry adopting `related_to` (RESOLVED — scope rule)

- **Sources:** physics-core check forbids `related_to` in physics (EVID-STEMMA-SCH-002) vs relation registry adopting 15 relations incl. `related_to` (same EVID).
- **Nature:** apparent contradiction; resolved by explicit scoping: the prohibition applies to the physics-core profile, not the registry vocabulary. RELATIONSHIP-SPECIFICATION.md updated 2026-09-22 to state both tiers.
- **Authority level required:** REPOSITORY_LOCAL.
- **Resolution status:** RESOLVED (docs scoping fix, commit fb66dd9; docs-consistency + registry coherence gates green).
- **Decision reference:** `git show fb66dd9 -- docs/RELATIONSHIP-SPECIFICATION.md`; ADR-0042 (physics minimal set) + ADR-0048 (registry extension) — historical decision records.
