# STEMMA

> An **open, structured, reusable knowledge foundation for STEM** — concepts,
> quantities, laws, models, and the relationships between them, expressed as
> version-controlled, machine-readable, human-reviewable data.
> Curriculum is external. Products are external. AI systems are consumers.

**Browse it:** <https://er-sajan-plg.github.io/STEMMA/> — the read-only 3D explorer
and downloadable exports (`/STEMMA/exports/knowledge.json`). Found a problem?
Use the **💬 Feedback** button (opens a
[GitHub feedback form](https://github.com/Er-Sajan-PLG/STEMMA/issues/new?template=feedback.yml)).

## What this is

STEMMA solves a data problem: established science and mathematics knowledge
is abundant in prose but scarce as *data*. STEMMA represents it as a governed
knowledge graph:

- **Entities** (`content/<domain>/`) — concepts, quantities, laws, units,
  constants, principles, theorems, equations, processes, structures,
  algorithms, materials across 8 domains (physics, chemistry, biology,
  earth-space/astronomy, computer-science, engineering, mathematics,
  scientific-practice) as Markdown + validated YAML, added via PDF-primary
  ingestion with deterministic templates (LLM fallback only when a source PDF
  lacks an exact definition) and **human-in-the-loop review before canonical**.
- **Connections** (`connections/`) — first-class relationship assertions, one
  YAML object per claim, with mandatory evidence (`source_ref` + locator),
  context, confidence and review status. Physics core uses the minimal 8
  relations (ADR-0042); `schema/relation-registry.yaml` v1.0.0 is the
  authoritative vocabulary (15 adopted incl. ADR-0048 `equivalent_to` /
  `misconception_of`; `related_to` is forbidden in physics core).
- **Sources** (`sources/`) — canonical citation records those assertions point
  to (url/doi/isbn, dual verification, `writer: human:*`).

— validated by a strict gate (`scripts/verify_all.py`: validate + status truth
+ physics profile/governing checks + HITL + registry/domain coherence +
deterministic export + semantic-pipeline checks) and published as
deterministic, content-hash-stamped exports (`exports/knowledge.json`
**export_version 2.2.0**, ADR-0050) that any curriculum, application, or AI
system (LearningHub, PROFESSOR-J, general, explorer) can build on.

The pre-refoundation corpus (74 entities + 150 connections) and design live in
`archive/`. Current canonical corpus grows through the R4 content acceptance
test (ADR-0052).

## Canonical vs derived vs consumer — who owns embeddings/RAG

- **Canonical** (`content/`, `connections/`, `sources/`) — never contains
  embeddings, vectors, or RAG artifacts. `validate.py` never checks embeddings.
- **Derived** (`exports/`) — knowledge.json, `embeddings.jsonl`,
  `vector_store/` (deterministic JSON store; FAISS optional when installed),
  `consumers/<consumer>/`, openapi.yaml — all regenerable, deterministic,
  content-hash versioned. Checked as INFO (not FAIL) in `verify_all.py`.
- **RAG/embeddings are the consumer's job.** STEMMA ships a reference
  implementation for demo and testing (`scripts/embed.py`, `scripts/rag.py`,
  `scripts/export_consumers.py`, adapter `/v2/*` endpoints, webapp RAG
  playground, `examples/external-rag/` for the out-of-STEMMA variant), but
  production embedding models, vector stores, top-k and LLM choices are
  per-consumer decisions. Full rationale and build guide:
  [docs/GUIDELINE-EMBEDDER-RAG.md](docs/GUIDELINE-EMBEDDER-RAG.md) and
  [docs/ARCHITECTURE-V2.md](docs/ARCHITECTURE-V2.md) (producer/consumer
  separation, connection via file/API/SDK + `content_hash`).

## Specification (recovered, pilot)

`spec/` holds an **evidence-backed, reviewable specification** recovered under the
Specification Recovery Protocol v3.1 (pilot edition) over the CORE–GATE–EXPORT
vertical slice (2026-09-22, ahead of the R4 content acceptance test):

- **22 requirements** (full schema, evidence-traced) — **all PROPOSED**; none are
  normative until the owner approves them. The recovery agent had no approval power.
- **2 interface contracts** (`exports/knowledge.json` 2.2.0; `verify_all.py` CLI),
  37 classified evidence records, 6 open questions, 2 conflict records,
  two-tier gap analysis, machine-readable registries + a minimum validator
  (`python3 spec/machine-readable/validate_recovery.py`, 9/9 checks).
- Baseline `spec/BASELINE.md` — maturity **L2 (slice-scoped only)**; approval and
  verification are the owner's next steps. Entry points: `spec/REQUIREMENTS.md`,
  `spec/OPEN_QUESTIONS.md`; process review: `SPECIFICATION_PROCESS_REVIEW.md`.

## Status

<!-- status-truth:start -->
## Status: live foundation in early curation

Machine-checkable live counts — `scripts/status_truth.py` (CI) fails if this
block drifts from canonical content (audit F2: status honesty is a gate):

- Entities: **9** — human-reviewed/canonical: **7**, draft: **2**
- Connections (first-class assertions): **2** — review-canonical: **2** (100.0%), unreviewed: **0**
- Canonical source records: **3**
<!-- status-truth:end -->

Canonicality is a *reviewed* property, not a folder: consumers filter by
review status ([docs/CONSUMERS.md](docs/CONSUMERS.md), `export_version: 2.2.0`).
Architecture baseline **3.0.0**.

## Repository layout

```text
STEMMA/
├── content/<domain>/     canonical entities (Markdown + YAML frontmatter)
├── connections/          canonical relationship assertions (one YAML per claim)
├── sources/              canonical citation records
├── schema/               JSON Schemas, VERSION.yaml, relation/template/embedding/
│                         consumer/llm/agent registries, api.yaml (OpenAPI 3.0.3)
├── adapters/python/      first-party read-only Python adapter v0.2.0 (SDK, CLI, JSON API)
├── scripts/              validation gate, review workflow, ingestion, embedding/RAG
│                         reference implementation, derived-artifact builders
├── webapp/               stdlib ingestion/review UI + RAG playground (HITL; never
│                         writes canonical directly)
├── exports/              DERIVED artifacts (regenerable; never the source of truth)
├── tests/                invariant test suite (pytest + gate scripts)
├── explorer/             reference 3-D graph explorer (a consumer; reads the export only)
├── examples/external-rag/ minimal embed/RAG living OUTSIDE STEMMA, consuming the export
├── docs/                 authoritative documentation set (docs/README.md indexes it)
└── archive/              pre-refoundation corpus + old design (immutable history)
```

## Quick start

```bash
pip install -r requirements.txt            # gate dependencies (pyyaml, jsonschema)
python3 scripts/verify_all.py              # full verification chain (what CI runs)
python3 -m pytest tests/ -q                # full test suite (dev: pip install -r requirements-dev.txt)
python3 scripts/embed.py --model sentence-transformers/all-MiniLM-L6-v2
python3 scripts/rag.py --search "metre" --top-k 2
python3 scripts/export_consumers.py --consumer general --format json
```

Exit code `0` = valid. Explore visually: `npm --prefix explorer run dev`.
Ingestion/review UI + RAG playground (admin only, loopback):

```bash
export STEMMA_REVIEWER_ID=human:curator.001   # your id in schema/agent-registry.yaml
python3 webapp/server.py --port 8081
```

(see [docs/WEBAPP.md](docs/WEBAPP.md), [docs/RAG.md](docs/RAG.md),
[docs/EMBEDDINGS.md](docs/EMBEDDINGS.md), [docs/API.md](docs/API.md)).

> **Webapp identity:** the webapp has **no login**. Identity = whoever started the
> server: set `STEMMA_REVIEWER_ID=human:<you>` (your id in
> `schema/agent-registry.yaml`) before `python3 webapp/server.py`. Saving a human
> edit or staging a proposal **fails closed** if it is missing, unregistered,
> inactive, a group (`human:institution.*`) or not a human. Machine drafts are
> recorded as `process:deterministic-draft.v1` / `llm:antigravity-001`; when you
> edit one you become `writer` and the machine stays as `drafted_by`.

## Get the content out — file, API, SDK

```bash
# File
cat exports/knowledge.json | python3 -c "import json; print(json.load(open('exports/knowledge.json'))['content_hash'])"

# API — optional read-only adapter over the export (ADR-0054; local, no auth).
# Stable: /v2/stats, /v2/entities, /v2/search, /v2/neighbors, /v2/values, ...
# Experimental (placeholder vectors): /v2/embeddings, /v2/rag/*, /v2/export
PYTHONPATH=adapters/python python3 -m stemma_adapter serve exports/knowledge.json --port 8080
curl http://127.0.0.1:8080/v2/stats

# SDK
PYTHONPATH=adapters/python python3 -c "from stemma_adapter import Stemma; s=Stemma.from_file('exports/knowledge.json'); print(s.stats)"
```

## Documentation

Start with [docs/README.md](docs/README.md). Key entry points:
[ARCHITECTURE-V2](docs/ARCHITECTURE-V2.md) · [VISION](docs/VISION.md) ·
[DOMAIN-MODEL](docs/DOMAIN-MODEL.md) · [GOVERNANCE](docs/GOVERNANCE.md) ·
[CONSUMERS](docs/CONSUMERS.md) · [EMBEDDINGS](docs/EMBEDDINGS.md) ·
[RAG](docs/RAG.md) · [API](docs/API.md) ·
[GUIDELINE-EMBEDDER-RAG](docs/GUIDELINE-EMBEDDER-RAG.md) ·
[ROADMAP](docs/ROADMAP.md) · [CONTRIBUTING](docs/CONTRIBUTING.md).

## Ground rules

1. Canonical knowledge lives only in `content/`, `connections/`, `sources/`;
   everything derived is regenerable.
2. No curriculum, grade, course, country, or product appears in canonical
   data (machine-checked, L7).
3. AI-drafted content stays `draft` until a named human reviews it — HITL
   enforced (`hitl_check.py`), writer `human:*`, audit trail.
4. Stable IDs (`stemma:…`) are never reused or reassigned; corrected claims
   are superseded, never edited in place.
5. The gate decides: if `verify_all.py` fails, nothing ships.
6. Exports are deterministic, content-hash stamped, no wall clock
   (`export_version 2.2.0`, single version source `schema/VERSION.yaml`).

## License

- **Knowledge content** (`content/`, `connections/`, `sources/`, `docs/`):
  **Creative Commons Attribution 4.0** — see [LICENSE](LICENSE).
- **Code** (`scripts/`, `schema/`, `tests/`, `explorer/`, `adapters/`):
  **MIT** — see [LICENSE-CODE](LICENSE-CODE). Rationale: ADR-0001 (archived).
