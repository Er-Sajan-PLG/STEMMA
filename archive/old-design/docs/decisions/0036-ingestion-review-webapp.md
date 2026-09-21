# DECISION 0036 — Ingestion/review webapp (human-in-the-loop)

- **Date:** 2026-09-06
- **Status:** decided & implemented
- **Related:** ADR-0035 (ingest/proposal correctness), ADR-0029 (baseline),
  `docs/WEBAPP.md`, `docs/INGESTION.md`.

## Context

Uploading documents and reviewing what the ingestion path proposes was a
CLI-only, hard-to-inspect flow. A curator needed a visual way to see an upload,
what was extracted, what the Draft seam proposed, and exactly where a decision
goes before it can touch canonical knowledge. It must remain curriculum- and
product-neutral, and it must never write to canonical.

## Decision

- **Build a simple stdlib webapp** under `webapp/` (Python `http.server` +
  plain HTML/JS, no new runtime dependency) for upload → extraction → Draft →
  human review → staged proposal.
- **Everything lives in `workflow/`** (git-ignored): raw uploads, extracted
  text, generated candidates, staged proposal dossiers, LLM provider config
  (API key never committed), and an append-only audit log. The app *reads*
  `content/`/`schema/` where needed but **never writes canonical**.
- **All document types are accepted and retained.** Common types are directly
  extracted: PDF (poppler), images (Pillow + tesseract), text (md/txt/csv/json/
  yaml/xml/html). Unsupported types are retained and shown as `unsupported`
  with a reason (best-effort + honest).
- **The Draft seam is externally provided** (OpenAI-compatible `chat/completions`
  via `workflow/config/llm.json`). The webapp refuses to generate candidates
  until a provider is configured (ADR-0035 fail-closed policy). Generation only
  produces proposals for review.
- **Staging a proposal is explicit and human-only.** A candidate that fails the
  deterministic curation/schema checks cannot be staged. The staged dossier
  records: document source, extraction sidecar, candidate, human reviewer +
  note, and a destination note that the app does **not** write canonical — a
  human must verify and run `scripts/review.py` + `scripts/verify_all.py`.

## Alternatives considered

- **Multi-page / SPA-heavy product.** Rejected: keep it a simple single-page
  tool to review.
- **Write generated proposals directly into `proposals/` tracked dir.**
  Rejected: the human-review decision is the gate; we stage only after review,
  under the git-ignored workflow area. (A curator can copy a reviewed dossier
  to the tracked proposal flow if desired.)
- **Internal AI in canonical.** Rejected per standing constraint: the webapp is
  a consumer/drafter; authority stays human.

## Consequences

- `webapp/` (core/server/static), `workflow/` ignored, `docs/WEBAPP.md`,
  ADR-0036, `tests/webapp/test_webapp_core.py` in the verify chain,
  `docs/README.md`, `docs/IMPLEMENTATION-STATUS.md`, `docs/MIGRATIONS.md`,
  `docs/TESTING.md`.
- No canonical schema/export/version change. No LLM calls, uploads, or proposal
  writes are made by the verification chain or by running the webapp with no
  document.
