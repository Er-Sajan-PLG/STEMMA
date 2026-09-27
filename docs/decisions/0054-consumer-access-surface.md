# ADR-0054: Consumer Access Surface — File/SDK Contract First, Read-only `/v2`, Private Admin Webapp, Static Family Site

Status: Decided — 2026-09-26
Date: 2026-09-26
Decided by: Sajan (sole owner). This ADR records the owner's decisions Q1–Q3 and the adapter "Option A" from the 2026-09 audit follow-up; it does not create them.
Amends: docs/ARCHITECTURE-V2.md Part 5 §5.3 (Export Mechanism to Consumers)
Related: ADR-0045 (value-slot), ADR-0053 (publisher / IRI base), docs/API.md, schema/api.yaml, docs/WEBAPP.md

## Context

ARCHITECTURE-V2 §5.3 described one blended "API" surface: `schema/api.yaml`
endpoints listed as `/api/*`, the webapp claimed to implement
"existing `/api/entities /api/connections /api/ingest /api/rag/search`", and
consumers (LearningHub, PROFESSOR-J) were implied to use it. The audit found
that this description did not match the code:

- `schema/api.yaml` defines `/v2/*` paths, which the **adapter** server
  (`adapters/python/stemma_adapter/server.py`) implements. The webapp has no
  `/api/entities`, `/api/connections` or `/api/ingest` routes.
- The webapp (`webapp/server.py`) is a **curation tool**. It holds LLM provider
  keys, writes workflow files, and was bound to `0.0.0.0` with `CORS: *`. In
  that setup a saved key could be sent to an attacker-chosen `base_url`
  (finding C2).
- The adapter refused to load the real export, because it did not know the
  ADR-0045 valued claims (`target: null`). So no consumer could actually read
  STEMMA data.
- Several `/v2` routes (`/v2/resolve/{id}`, `/v2/relations/{name}`,
  `/v2/vocabularies`, `/v2/external/{scheme}/{value}`, `/openapi.yaml`) were
  served but not in the spec. The RAG/embeddings routes run on deterministic
  placeholder vectors, not a real model, unless `sentence-transformers` is
  installed.

The owner also wants family members to use STEMMA and give feedback, with
exactly one admin.

## Decision

1. **The file contract is the consumer contract.** `exports/knowledge.json`
   (plus the review-aware `knowledge.*.json` views and the derived
   `knowledge.jsonld`), identified by `content_hash`, is what consumers depend
   on. The Python SDK (`stemma_adapter`) is the reference reader. It validates
   fail-closed, including ADR-0045 valued claims (`Stemma.values()`).
   Published read-only at `https://er-sajan-plg.github.io/STEMMA/exports/`.

2. **`/v2/*` HTTP is an optional convenience, not a hosted service.** It is a
   read-only view over one export, run by a consumer on its own machine
   (default `127.0.0.1`). It has no auth, no rate limiting and no production
   host in this phase: `api.stemma.example.com`, api_key tiers and per-consumer
   rate limits are future work. `schema/api.yaml` must describe what the server
   actually serves. The embeddings/RAG/export paths are marked
   `x-stability: experimental` (reference/demo; ARCHITECTURE-V2 §5.1–5.2 keep
   production embedding/RAG as the consumer's job).

3. **The webapp is the private admin tool, not a consumer API.** Its `/api/*`
   routes are not part of the consumer surface and may change without notice.
   It binds `127.0.0.1` by default, sends no CORS headers, rejects foreign
   `Host` or `Origin`, and is reached remotely only over the owner's private
   network (Tailscale; `STEMMA_ALLOWED_HOSTS`). It is never internet-facing.

4. **LLM keys: one server key owned by the admin.** A stored key is bound to
   the provider and `base_url` it was saved with, and is never sent elsewhere.
   `workflow/config/llm.json` is `0600`. The provider-side spend cap is set by
   the owner outside STEMMA. The "free" model list holds only `:free` models.

5. **Family and testers get read-only access plus feedback.** The public site
   is the static 3D explorer and exports on GitHub Pages
   (`.github/workflows/pages.yml`). Feedback goes through the GitHub issue form
   `.github/ISSUE_TEMPLATE/feedback.yml`, pre-filled with the selected concept.
   There are no contributor accounts in this phase. Multi-user curation
   (accounts, roles, review queues) needs a new ADR before any work starts.

## Consequences

- ARCHITECTURE-V2 §5.3 is corrected in place to match this ADR (see the
  amendment note there). ROADMAP scope is unchanged.
- `docs/API.md` states what is implemented versus planned. The docs drift gate
  (`scripts/docs.py`, `api_surface`) keeps `schema/api.yaml` and the docs in
  sync, and `tests/repo/test_api_spec_matches_server.py` keeps the spec in sync
  with the adapter's routes.
- Consumers must treat a new `export_version` major as breaking. The adapter
  fails closed rather than guessing.
- Family feedback needs a (free) GitHub account. If that becomes a barrier, a
  no-account channel (e.g. a form service) is a small follow-up decision.
- Accepted residual risk: anyone on the owner's tailnet who is allowed in
  `STEMMA_ALLOWED_HOSTS` can use the admin tool. The tailnet is the
  authentication boundary in this phase.


## Amendment 1 — 2026-09-26: versioning and release policy

Status: **Partly decided.** Items marked *Decided* restate owner decisions
already made. Items marked *Proposed* await the owner's yes/no and are not
binding until this line says so. Full rules: `docs/VERSIONING.md` →
"Consumer versioning and release policy". Test:
`tests/repo/test_versioning_policy.py`.

- *Decided* — The release version (`./VERSION`, tag, `kernel_version`),
  `export_version`, `schema_version` and `content_hash` are independent.
  `export_version` stays on 2.x, and a new export major is breaking.
- *Decided* — Tags are immutable. `-rcN` = CI pre-release with the Sigstore
  attestation only. Final = `publication_gate`, then a draft, then the owner
  GPG-signs `SHA256SUMS.txt` locally, then publishes. The key never goes into
  Actions.
- *Proposed D1* — Release SemVer from the consumer's view: MAJOR = export
  major or removed/renamed export asset; MINOR = export minor, new content or
  new assets; PATCH = corrections with IDs unchanged.
- *Proposed D2* — Additive (export minor) vs breaking (export major) as listed
  in `VERSIONING.md` §3. Any new value-slot member is breaking, and consumers
  treat unknown enum values as "unknown — not canonical".
- *Proposed D3* — IDs are never deleted or reused: retire them with
  `deprecated_by` / `replaced_by`. Contract members and assets are announced,
  kept for at least one final MINOR release and 90 days, and removed only in
  the next MAJOR.
- *Proposed D4* — Change records live in `docs/MIGRATIONS.md`,
  `schema/VERSION.yaml` comments, `adapters/python/CHANGELOG.md` and the
  release notes. No root CHANGELOG, so release-please is retired.
- *Proposed D5* — A final tag points at exactly the commit of the last rc of
  that version that passed `release.yml`, so its export files are
  byte-identical to that rc. Enforcing this in `release.yml` is a follow-up.
