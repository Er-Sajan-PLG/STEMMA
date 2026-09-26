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
# From the repo root — binds to 127.0.0.1 (local only) by default
export STEMMA_REVIEWER_ID=human:curator.001   # your id in schema/agent-registry.yaml
python3 webapp/server.py --port 8081
```

Without a valid `STEMMA_REVIEWER_ID` the UI still loads, but *Save human edit*
and *Stage* are refused (see **Who you are** below).

Open `http://127.0.0.1:8081`. The default port is `8081` so it does not collide
with common local harness ports such as DeepSeek/Antigravity harnesses on `3080`.

### Security model (single-owner admin tool)

The webapp is the **private curation tool**: it holds LLM provider keys and
writes workflow files, so it is never shared with readers (family/testers use
the read-only explorer site instead — see ADR-0054).

- Binds to `127.0.0.1` by default; sends **no CORS headers**.
- Rejects requests whose `Host` is not this server (DNS rebinding) or whose
  `Origin` is another site (cross-site requests), and requires JSON for writes.
- A saved API key is bound to the provider **and** `base_url` it was saved
  with; it is never sent to another endpoint (changing `base_url` requires
  re-entering the key). `workflow/config/llm.json` is written `0600`.

**Remote access from your own devices:** use a private network, not the
internet. With [Tailscale](https://tailscale.com/kb/1312/serve):

```bash
export STEMMA_REVIEWER_ID=human:curator.001            # your id in schema/agent-registry.yaml
python3 webapp/server.py --port 8081                   # still loopback-only
tailscale serve --bg 8081                              # HTTPS on your tailnet
export STEMMA_ALLOWED_HOSTS=<machine>.<tailnet>.ts.net # the name you browse with
```

If a request is refused with `host ... not allowed`, add exactly that hostname
to `STEMMA_ALLOWED_HOSTS` (comma-separated). Uploads are capped at
`STEMMA_MAX_BODY_MB` (default 50). Do not run with `--host 0.0.0.0`
on a shared or public network.

**Who you are (provenance):** human edits and staging are attributed to the
operator configured on the server, never to a name typed in the browser:

```bash
export STEMMA_REVIEWER_ID=human:curator.001   # your id in schema/agent-registry.yaml
```

It must be an active, individual `class: human` agent in
`schema/agent-registry.yaml`; if it is unset or invalid, *Save human edit* and
*Stage* are refused. Machine drafts are recorded as
`process:deterministic-draft.v1` (templates) or `llm:antigravity-001` (LLM).
When you edit one, you become `writer`/`edited_by` and the machine id is kept
as `drafted_by` — the origin is never rewritten.

To use a different workflow directory:

```bash
export STEMMA_REVIEWER_ID=human:curator.001
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
   (`python3 webapp/server.py --port 8081`), or ensure
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

## Environment variables (§6 — contract-enforced)

Root `.env` (git-ignored; see [../.env.example](../.env.example)) is parsed
line-wise by `webapp/providers.py`; the `STEMMA_*` variables are read from the
process environment by `webapp/core.py` / `webapp/server.py`:

| Variable | Read by | Purpose |
|---|---|---|
| `OPENROUTER_API_KEY` | webapp/providers.py | OpenRouter provider calls (model selector free/frontier models) |
| `NVIDIA_NIM_API_KEY` | webapp/providers.py | NVIDIA NIM provider calls |
| `OPENCODE_API_KEY` | webapp/providers.py | OpenCode provider calls |
| `OPENAI_API_KEY` | scripts/embed.py (CLI) | Frontier OpenAI embedding model runs (or `--api-key`) |
| `STEMMA_WORKFLOW_DIR` | webapp/core.py | Override the HITL workflow directory (default `./workflow`) |
| `STEMMA_REVIEWER_ID` | webapp/core.py | Your `human:*` id (agent registry); required for human edits and staging |
| `STEMMA_ALLOWED_HOSTS` | webapp/server.py | Extra allowed `Host` names, e.g. your Tailscale name |
| `STEMMA_MAX_BODY_MB` | webapp/server.py | Max request body (uploads), default 50 |

All are optional to browse and to run the deterministic ingestion path;
`STEMMA_REVIEWER_ID` is needed to record a human edit or stage a proposal.
(`scripts/embed.py --placeholder` needs no key but is labelled non-semantic.) Never commit `.env` or real values.

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
