# STEMMA — Ingestion & Review Webapp

**Status:** Authoritative for the local human-in-the-loop ingestor/reviewer
(`webapp/`), ADR-0036.
**Guarantee:** this tool never writes to `content/`, `connections/`, or
`sources/`. The only path to canonical is the existing human review flow
(`scripts/review.py` + `scripts/verify_all.py`).

## What it does

A simple single-page webapp that makes the proposal-engineering lane visible and
reviewable:

```
upload ──► extract ──► draft (LLM seam, optional) ──► human review ──► staged proposal
  │           │            │                              │                 │
  file kept   text/OCR      proposed candidates           edit/reject      workflow/proposals/
  (any type)  preview       (never canonical)              /approve         (never canonical)
```

- **Upload any file.** The raw file is retained. Common types are extracted
  automatically where tooling is available; unsupported types are kept and
  reported as `unsupported` with a reason.
- **See what was extracted.** Status, kind, character count, OCR flag, and a
  preview of the extracted text.
- **Review every generated candidate.** Each candidate shows its schema fields,
  deterministic findings, and lets you edit, delete, or stage it.
- **Decide with full context.** Every staged proposal records the source
  document, the extraction sidecar, the candidate, the human reviewer + note,
  and a destination line explaining it is *not* written to canonical by the app.
- **Audit trail.** An append-only `workflow/audit/audit.jsonl` logs upload,
  extraction, generation, edit, stage, and delete events.

## Running it

```bash
# From the repo root
python3 webapp/server.py --host 0.0.0.0 --port 8080
```

Open `http://localhost:8080` (or the platform's preview URL). It binds to
`0.0.0.0` so it can be used in the arena preview.

To use a different workflow directory:

```bash
STEMMA_WORKFLOW_DIR=/tmp/stemma-workflow python3 webapp/server.py --port 8080
```

## LLM Draft provider

The app only *proposes*; it never generates canonical content.

1. Open **LLM Draft settings** in the UI.
2. Pick a provider:
   - **Antigravity / local harness (OpenAI-compatible)** — for the models
     inside your Google-AI-Pro/Antigravity subscription via a local bridge
     (e.g. Antigravity CLI/Gateway, DeepSeek-harness-style proxies). It calls
     `POST {base_url}/chat/completions` with a Bearer key. Defaults:
     `http://127.0.0.1:6012/v1`. **Important:** the webapp server makes this
     call server-side. If you are using the Arena preview (the server runs in
     a container), put the harness's tunneled/public URL here, or run the
     webapp on the same machine as Antigravity.
   - **Google Gemini / AI Pro (Antigravity) via API key** — calls
     `POST {base_url}/models/{model}:generateContent` with an
     `x-goog-api-key` header. Defaults:
     `https://generativelanguage.googleapis.com/v1beta` /
     `gemini-3-pro-preview` (or any Gemini Pro/Flash model id you have
     access to).
   - **OpenAI-compatible (any API)** — calls `POST {base_url}/chat/completions`
     with a Bearer key. Defaults: `https://api.openai.com/v1`.
3. Enter the base URL, model, and API key. Google AI Studio/GenAI API keys
   usually start with `AIza…`.
4. **Sign in to Google AI Pro / harness** (`POST /api/config/login`): for the
   Antigravity/local-harness provider the app calls the harness login endpoint
   (`/api/login`, `/login`) and opens the returned Google/OAuth URL in a new
   browser tab. It never asks for or stores Google credentials itself. The
   Google Gemini provider explains that it uses an AI Studio API key instead
   of an account OAuth.
5. **Load models** (`POST /api/config/models`): fetches `GET {base_url}/models`
   from the signed-in harness/Google endpoint and fills the model picker, so
   you select e.g. `gemini-3-pro`, `gemini-3.1-pro-high`, or
   `claude-opus-4-6-thinking` just like inside a DeepSeek/agent harness.
6. Save. The config is stored in `workflow/config/llm.json` (git-ignored; the
   GET summary masks the key). Switching providers requires a fresh key; the
   app never reuses a masked key across providers.

**Reachability rule.** Every provider call is made by the **webapp server**
(container in the Arena preview), not by your browser. If you are using the
preview and your Antigravity harness-only lives on `localhost`, either run the
webapp on the same machine (`python3 webapp/server.py --host 0.0.0.0 --port
8080`) or tunnel the harness to a public URL and paste that URL into Base URL.

The Draft/LLM step is never auto-run: the app refuses to run until a provider
is configured (fail closed, ADR-0035), and no placeholder proposal is ever
staged.

## Where things live

| Path (relative to repo) | Meaning |
|---|---|
| `workflow/uploads/` | raw uploaded files |
| `workflow/meta/` | document metadata + extraction status |
| `workflow/extraction/` | extracted text per document |
| `workflow/candidates/` | generated candidates awaiting review |
| `workflow/proposals/` | human-staged proposal dossiers |
| `workflow/config/llm.json` | LLM provider config (API key, git-ignored) |
| `workflow/audit/audit.jsonl` | append-only audit trail |

`workflow/` is git-ignored. `content/`, `connections/`, `sources/` are never
written by this app.

## Boundaries

- This is a **consumer/drafter tool**, not a canonicality decision maker.
- The webapp validates candidate shape using the same deterministic rules as
  `scripts/validate.py`; it does **not** approve canonical status.
- Staged proposals carry `workflow_status: proposed` and a human-review record.
  Moving a proposal into canonical remains a separate human-reviewed action
  through the existing review + verification flow.

## Tests

`python3 tests/webapp/test_webapp_core.py` verifies: git-ignored workflow dir,
upload + text extraction, unsupported-type retention, fail-closed generation,
candidate validation/staging, connection endpoint resolution, Google/OpenAI
request + response parsing with local mocks, Antigravity local-harness model
listing, and the harness sign-in URL flow. It is part of
`scripts/verify_all.py`.
