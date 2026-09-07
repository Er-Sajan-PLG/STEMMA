# STEMMA

> An **open, structured, reusable knowledge foundation for STEM** — concepts,
> quantities, laws, models, and the relationships between them, expressed as
> version-controlled, machine-readable, human-reviewable data.
> Curriculum is external. Products are external. AI systems are consumers.

## What this is

STEMMA solves a data problem: established science and mathematics knowledge
is abundant in prose but scarce as *data*. STEMMA represents it as a governed
knowledge graph —

- **224 entities** (`content/`) — concepts, quantities, laws, equations… as
  Markdown + validated YAML,
- **654 first-class relationship assertions** (`connections/`) — each claim is
  its own object with evidence, context, confidence, and review status,
- **source records** (`sources/`) — citations those assertions point to,

— validated by a strict gate and published as a deterministic, versioned JSON
export that any curriculum, application, or AI system can build on.

## Status: live foundation in early curation

<!-- status-truth:start -->
## Status: live foundation in early curation

Machine-checkable live counts — `scripts/status_truth.py` (CI) fails if this
block drifts from canonical content (audit F2: status honesty is a gate):

- Entities: **0** — human-reviewed/canonical: **0**, draft: **0**
- Connections (first-class assertions): **0** — review-canonical: **0** (0.0%), unreviewed: **0**
- Canonical source records: **0**
<!-- status-truth:end -->


Canonicality is a *reviewed* property, not a folder: consumers should filter
by review status (`docs/CONSUMERS.md`). Architecture baseline **3.0.0**
(ADR-0029).

## Repository layout

```text
STEMMA/
├── content/          canonical entities (Markdown + YAML frontmatter)
├── connections/      canonical relationship assertions (one YAML object per claim)
├── sources/          canonical citation records
├── schema/           JSON Schema contracts, relation/agent/extension registries, vocabularies
├── adapters/python/  first-party read-only Python consumer adapter (SDK, CLI, local JSON API)
├── scripts/          the validation gate, review workflow (incl. entity review), ingestion, derived-artifact builders
├── webapp/           stdlib ingestion/review UI (upload → extract → draft → human review → staged proposal)
├── exports/          DERIVED artifacts (regenerable; never the source of truth)
├── tests/            invariant test suite (layered)
├── explorer/         stemma — reference 3-D graph explorer (a consumer; reads only the export)
└── docs/             the authoritative documentation set
```

## Quick start

```bash
pip install pyyaml jsonschema        # gate dependencies
python3 scripts/verify_all.py        # full verification chain (what CI runs)
python3 scripts/validate.py          # validate canonical data + regenerate the export
```

Exit code `0` = valid. To explore visually: `npm --prefix explorer run dev`.
For document ingestion/review: `python3 webapp/server.py --port 8081`
(see [`docs/WEBAPP.md`](docs/WEBAPP.md)). The webapp's Draft seam is a
provider abstraction (`webapp/providers.py`): the default **Antigravity**
provider uses the official Antigravity SDK or `agy` CLI on the webapp host with
your local Google AI Pro session (no Gemini API key); `gemini_api`, `vertex_ai`,
and `openai_compatible` are separate entitlements (ADR-0038). Without
poppler-utils, install the pure-Python PDF fallback for text PDFs:
`pip install pypdf`.

## Get the content out

```bash
PYTHONPATH=adapters/python python3 -m stemma_adapter serve exports/knowledge.json --port 8080
curl http://127.0.0.1:8080/v2/stats
curl "http://127.0.0.1:8080/v2/search?q=force&domain=physics"
```

## Documentation

Start with [`docs/README.md`](docs/README.md). Key entry points:
[VISION](docs/VISION.md) · [ARCHITECTURE](docs/ARCHITECTURE.md) ·
[DOMAIN-MODEL](docs/DOMAIN-MODEL.md) · [GOVERNANCE](docs/GOVERNANCE.md) ·
[CONSUMERS](docs/CONSUMERS.md) · [CONTRIBUTING](docs/CONTRIBUTING.md) ·
[ROADMAP](docs/ROADMAP.md).

## Ground rules

1. Canonical knowledge lives only in `content/`, `connections/`, `sources/`;
   everything derived is regenerable.
2. No curriculum, grade, course, country, or product appears in canonical
   data (machine-checked).
3. AI-drafted content stays `draft` until a named human reviews it.
4. Stable IDs (`stemma:…`) are never reused or reassigned; corrected claims
   are superseded, never edited in place.
5. The gate decides: if `verify_all.py` fails, nothing ships.

## License

- **Knowledge content** (`content/`, `connections/`, `sources/`, `docs/`):
  **Creative Commons Attribution 4.0** — see [`LICENSE`](LICENSE).
- **Code** (`scripts/`, `schema/`, `tests/`, `explorer/`, `adapters/`): **MIT** — see
  [`LICENSE-CODE`](LICENSE-CODE).

Rationale: ADR-0001.
