# DECISION 0038 — Provider abstraction: official Antigravity agent + separate Gemini/Vertex entitlements

- **Date:** 2026-09-07
- **Status:** decided & implemented
- **Related:** ADR-0036 (webapp), ADR-0035 (ingest/proposal correctness),
  `docs/WEBAPP.md` (LLM Draft provider), `docs/SOTA-REVIEW.md`,
  `docs/DEEP-DIVE-RECOMMENDATIONS.md`.

## Context

STEMMA's webapp needs a Draft backend that can use the models/agentic
capabilities of the user's **Google AI Pro / Antigravity** account. Google's
Antigravity CLI/IDE explicitly do **not** support bring-your-own-key or
bring-your-own-endpoint (Antigravity docs: "There is currently no support for:
Bring-your-own-key or bring-your-own-endpoint …"; community threads confirm the
same). Therefore using a separate Gemini API key would *bypass* the user's
Antigravity entitlements rather than delegate to them.

Official, supported programmatic surfaces for Antigravity (per Google I/O 2026
and `antigravity.google` docs):

- **Antigravity CLI (`agy`)** — Go binary, terminal surface of the same agent
  harness, headless mode via `agy -p`/`--print` with `--output-format json`,
  `--json-schema`, `--model`, `--effort`, `--print-timeout`. Auth is the **local
  system keyring / Google Sign-In** of the machine where `agy` runs; no API key.
- **Antigravity SDK (`google.antigravity`)** — official Python SDK giving
  programmatic access to the same agent harness (`Agent`, `LocalAgentConfig`,
  async `chat`, streaming, MCP, tools). Local mode uses the machine's existing
  Antigravity session. Vertex/enterprise mode is separate (project/location/ADC
  or `api_key` only when explicitly `vertex=True`).

## Decisions

1. **Antigravity is a first-class provider** (`antigravity`).
   - Transport `auto` (default): use the official Antigravity **SDK** when
     importable, else the official **CLI** (`agy`).
   - `sdk` and `cli` may be forced.
   - **No Gemini API key is required or used.** Antigravity CLI/IDE do not
     support BYOK, so the adapter does not invent one.
   - The provider reports its local availability; if neither SDK nor CLI is
     present/authenticated it fails closed with install/sign-in guidance instead
     of silently switching to a paid API key.

2. **Other providers are separate entitlements**, never aliases of Antigravity:
   - `gemini_api` — Gemini Developer API (`generateContent`, `AIza…`).
   - `vertex_ai` — Vertex AI on your own GCP project (ADC or Vertex key).
   - `openai_compatible` — any OpenAI-compatible endpoint; explicitly labelled
     as a **community bridge/tunnel**, not an Antigravity entitlement path.

3. **The webapp never collects or stores Google account credentials.** Its login
   flow for Antigravity tells the user to complete local `agy`/SDK sign-in on
   the host machine; it never attempts OAuth as a third-party Antigravity
   client. Only an `openai_compatible` harness may expose its own login URL.

4. **Canonical provider ids**, with backward-compatible aliases canonicalized
   on save (`google`→`gemini_api`, `openai`→`openai_compatible`). Persisted
   `workflow/config/llm.json` never contains an ambiguous alias.

5. **Deterministic tests** cover the registry contract, `agy` headless command
   shape, JSON/fence parsing, fail-closed availability, antigravity dispatch
   without an API key, model listing, and login guidance.

## Consequences

- `webapp/providers.py` is the single provider seam. `Workflow` delegates
  `chat`, `probe`, `list_models`, and login to it. Existing request-shape
  helpers remain for backward-compatible tests.
- The default selected provider is `antigravity`, configured only when the
  official SDK/CLI is available on the webapp host; otherwise the app fails
  closed (no placeholder candidates).
- Running the Arena preview against a local-only Antigravity agent is
  impossible by design (the server is not on the user's machine). The UI and
  docs state that the official local agent must be on the host running the
  webapp server; a tunneled community bridge is `openai_compatible`, not
  `antigravity`.
