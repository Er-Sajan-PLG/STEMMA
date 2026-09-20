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
python3 webapp/server.py --host 0.0.0.0 --port 8081
```

Open `http://localhost:8081` (or the platform's preview URL). It binds to
`0.0.0.0` so it can be used in the arena preview. The default port is `8081`
so it does not collide with common local harness ports such as DeepSeek/Antigravity
harnesses on `3080`.

To use a different workflow directory:

```bash
STEMMA_WORKFLOW_DIR=/tmp/stemma-workflow python3 webapp/server.py --port 8081
```

## LLM Draft provider abstraction

The app only *proposes*; it never generates canonical content. All model
access goes through a small provider registry (`webapp/providers.py`) that
treats every backend as a separate entitlement. The default selected provider
is the **official Antigravity local agent**, which uses your existing
Google AI Pro / Antigravity session rather than inventing a separate paid key.

### Providers

| Provider id | What it uses | Key required? | Notes |
|---|---|---|---|
| `antigravity` | Official Antigravity SDK (`google.antigravity`) if installed, otherwise official Antigravity CLI (`agy`) | No | Uses the **locally signed-in Google AI Pro / Antigravity** agent. No Gemini API key. Antigravity CLI/IDE do not support BYOK. |
| `gemini_api` | Official Gemini Developer API | Yes (`AIza…`) | Separate entitlement; not a substitute for Antigravity. |
| `vertex_ai` | Official Vertex AI on your own GCP project | ADC or Vertex key | Separate entitlement. |
| `openai_compatible` | Any OpenAI-compatible endpoint | Yes | Community bridge/tunnel only. NOT an Antigravity entitlement path. |
| `openrouter` | OpenRouter API (Free/Paid Models) | Yes | Auto-fetches free models. Managed via `.env` or config. |
| `nvidia` | NVIDIA NIM (Free Models) | Yes | Auto-fetches free models. Managed via `.env` or config. |
| `opencode` | OpenCode Free Coder | Yes | Auto-fetches free models. Managed via `.env` or config. |

`google` and `openai` remain accepted **aliases** in config files; they are
canonicalized to `gemini_api` and `openai_compatible` on save so persistence
never carries ambiguous ids.

### Using Antigravity (official, no key)

1. Run the webapp **on the same machine** as your Antigravity login
   (`python3 webapp/server.py --host 0.0.0.0 --port 8081`), or ensure
   `agy` / `google.antigravity` is installed on the host running the server.
2. In **LLM Draft settings** select **Antigravity (official local agent)**.
3. Press **Sign in to Google AI Pro / harness**. For the official provider this
   returns instructions to run `agy` locally once and complete Google Sign-In
   in your browser. STEMMA never asks for or stores your Google credentials.
4. Press **Load models**. It reads `agy models` (or shows common ids if the CLI
   isn't installed yet) and fills the model picker (e.g. `gemini-3-pro`,
   `gemini-3.1-pro-high`, `claude-opus-4-6-thinking`).
5. Leave API key blank. Optionally set `transport` (`auto`/`sdk`/`cli`),
   `effort`, or `agent`.
6. **Test provider**, then **Draft** on an extracted document.

Because Antigravity CLI's `--print` mode can stall on tool-permission prompts,
STEMMA does **not** pass `--dangerously-skip-permissions`; use `--sandbox` and
a bounded `--print-timeout` when the agent performs tool work.

### Using Gemini API / Vertex AI / a bridge

Select the corresponding provider, fill the required fields
(`gemini_api`: base URL + model + `AIza…` key; `vertex_ai`: model + GCP
project/location + ADC; `openai_compatible`: base URL + model + key). These are
recorded as separate providers, and the app never reuses a secret across
providers.

### Reachability rule

Every provider call is made by the **webapp server**, not by your browser. If
you are using the Arena preview and the Antigravity agent only lives on
`localhost`, either run the webapp on that machine or tunnel the agent to a
public URL and paste that URL into Base URL (this only applies to the
community-bridge/OpenAI-compatible provider; the official local Antigravity
agent must be on the machine hosting the server).

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
candidate validation/staging, connection endpoint resolution, the provider
registry contract (`antigravity`/`gemini_api`/`vertex_ai`/`openai_compatible`,
aliases canonicalized), the official `agy` headless command shape, JSON/fence
parsing, Antigravity availability failing closed without a local agent,
Antigravity chat dispatch without an API key, Gemini API and OpenAI-compatible
adapter mocks, model listing, and the login/guidance messages. It is part of
`scripts/verify_all.py`.
