# STEMMA — Pipelines

**Status:** Authoritative (baseline 3.0.0). What enters the system, what
transforms occur, what is canonical vs derived, where validation and human
review occur, and what is reproducible.

---

## 1. The pipeline chain

```
authoring ──▶ ingestion ──▶ normalization ──▶ validation ──▶ semantic review
   │              │              │               │               │ (human)
   ▼              ▼              ▼               ▼               ▼
 propose      extract to      canonical      gate: exit 0    review state
 (draft)      proposals       file format    or block        machine
                                                                │
                                                ┌───────────────┘
                                                ▼
                       build ──▶ publication ──▶ consumption
                       (export)   (release/tag)  (explorer, consumers)
```

## 2. Stage by stage

### 2.1 Authoring
- **Input:** a human or AI-assisted draft of an entity/connection/source.
- **Mechanism:** directly, or via the ingestion pipeline. AI output is
  `status: draft` / `assertion.type: proposed` — never authoritative.
- **Canonical writes:** only through review (below).

### 2.2 Ingestion (`scripts/ingest.py`, `ingest_to_proposals.py`,
`curation_pipeline.py`)
- **Input:** any document (PDF/image/scan).
- **Transform:** deterministic extraction (poppler/tesseract) → a canonical
  Source candidate → LLM-agnostic *draft seam* proposes entities/connections.
- **Output:** staged proposals in gitignored `proposals/`.
- **Invariants:** never writes canonical; decision set is
  {propose, request_review, hold, reject} — `canonical` is unreachable by
  construction; no hardcoded curriculum, subject, or language.

### 2.3 Normalization
- Authoring output lands in the canonical file grammar (ID rules, filename
  rules, strict YAML, registry vocabularies). Performed at write time by
  tooling; re-normalization is never a silent bulk rewrite (bulk changes are
  migrations: ADR + MIGRATIONS entry).

### 2.4 Validation — the gate (`scripts/validate.py`)
- Schema conformance (4 JSON Schemas) · identity/grammar/uniqueness ·
  filename↔ID · strict-YAML duplicate-key rejection · reference resolution ·
  registry coherence + domain/range · vocabulary conformance · epistemic rules
  (review transitions, confidence pairing, agent resolution) · cycle
  detection · duplicate-claim signatures · legacy-namespace guard ·
  **export validated against its own contract before write**.
- **Failure behavior:** exit 1, no export write. The gate is the only writer
  of `exports/knowledge.json`.
- History guards run alongside (`check_id_immutability.py`): ID and
  assertion-triple immutability reconstructed from git.

### 2.5 Semantic review (human) — `scripts/review.py`,
`curation_state.py`, `apply_review_decisions.py`, `dependency_review_campaign.py`
- The authority stage: `unreviewed → reviewed → canonical` with named human
  reviewer + reason; worksheet campaigns batch pending dependency edges for
  human decisions. AI never fills decisions.
- Evidence standards per relation family apply here
  (`docs/CURATION-PROTOCOL.md`).

### 2.6 Build (derived artifacts)
- `exports/knowledge.json` — the contract (deterministic, content-hash
  stamped).
- Review-policy views, extended graph view (inverses/transitive closure,
  marked derived), operational reports (`reports/`).
- **Reproducibility:** byte-identical regeneration (tested; CI freshness via
  `git diff --exit-code`).

### 2.7 Publication
- Today: the export file in-repo + git history.
- Planned (roadmap R6): signed tags, GitHub releases, published IRIs
  (**requires the public-IRI human decision**, ADR-0029).

### 2.8 Consumption
- First-party: the explorer and the read-only Python adapter
  (`adapters/python/`), both reading only the export and pinning the contract
  major.
- External: any consumer via the versioned export contract
  (`docs/CONSUMERS.md`). Consumers own their adapters, curriculum mappings,
  and presentation.

## 3. Canonical / derived ledger

| Artifact | Status |
|---|---|
| `content/`, `connections/`, `sources/` | **Canonical** — the only truth |
| `exports/*.json` | Derived — regenerable, contract-bound |
| `reports/*.json|md` | Derived — operational state; campaign worksheets are the one human-writable exception (decisions) |
| `explorer/public/exports/` | Derived — synced by the explorer itself, gitignored |
| `proposals/` | Staging — gitignored, never canonical |

## 4. Failure and review map

| Failure | Where it surfaces | Who acts |
|---|---|---|
| Malformed object | gate (exit 1) | author/tooling |
| Broken reference / duplicate claim / cycle | gate | author/tooling |
| Identity/triple mutation attempt | history guard | author → supersession flow |
| Scientific doubt | review queue / campaign | **human reviewer** |
| Contract change | ADR + export_version bump | governance |
| Stale derived artifact | CI freshness diff | committer (regenerate) |

## 5. Reproducibility guarantees

- The gate is deterministic and dependency-light (PyYAML + jsonschema);
  full-history guards run in CI (`fetch-depth: 0`).
- Regenerating any derived artifact from a given commit yields identical
  bytes (no wall clocks anywhere in the chain).
- Human decisions are recorded in-band (review_history), so canonical state
  is reconstructible from the repo alone — no external system holds state.
