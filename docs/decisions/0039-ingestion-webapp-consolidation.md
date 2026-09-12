# 39. Ingestion Webapp Consolidation

Date: 2026-09-12

## Status

Accepted

## Context

We had two separate webapp iterations for Human-in-the-Loop (HITL) review: `ingestion_webapp/` (an early multi-provider LLM studio prototype) and `webapp/` (the new upstream refoundation architecture). Maintaining two separate web frontends and backends led to fragmented logic, disjointed provider integrations, and an unclear path for future development.

Specifically, the `ingestion_webapp/` contained valuable tooling (e.g., dynamic free model fetching from OpenRouter and NVIDIA, a 5-stage side-by-side verification UI) that the upstream `webapp/` lacked, while `webapp/` implemented a cleaner, strictly segregated architecture (e.g., `providers.py` decoupling).

## Decision

We have decided to consolidate all ingestion, drafting, and review tooling into the upstream `webapp/` directory and deprecate/abandon the old `ingestion_webapp/` structure.

To achieve this:
1. We ported the multi-provider LLM abstraction (OpenRouter, NVIDIA NIM, OpenCode) into `webapp/providers.py`, standardizing the way we invoke third-party models alongside the official Antigravity and Gemini APIs.
2. We integrated the `.env` API key loader natively into `webapp/providers.py` to seamlessly manage credentials.
3. We merged the UI features (progress spinners, actionable error handling, tabular audit logs) into `webapp/static/app.js`.

## Consequences

*   **Positive**: A single unified webapp for all HITL operations. Reduced technical debt and cognitive load for maintainers. Consistent error handling and LLM generation pipelines.
*   **Positive**: Improved UI/UX (spinners, robust error messaging, structured audit logs) are now standardized.
*   **Negative**: Slight increase in complexity in `webapp/providers.py` to handle the diverse API structures of external bridges (like OpenRouter).
