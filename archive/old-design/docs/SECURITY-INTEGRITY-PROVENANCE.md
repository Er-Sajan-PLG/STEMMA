# STEMMA — Security, Integrity & Provenance

**Status:** Authoritative (baseline 3.0.0).

---

## 1. Trust model

STEMMA has no users, sessions, or privileges to protect; its security problem
is **content integrity and honest attribution**:

| Threat | Control |
|---|---|
| Silent mutation of identity/claims | Git-history immutability guards (IDs + assertion triples) |
| Duplicate or contradictory claims smuggling in | Claim signatures + duplicate-claim gate + review state machine |
| Fabricated authority (fake review) | Review transitions require a registered human agent + reason; state machine is the only writer; `unknown:` reviewers impossible |
| Fabricated data (invented timestamps/origins) | `null`-when-unknown contract; "no fabrication" tests |
| Malformed/hostile data breaking consumers | Payload validated against the export contract *before* write |
| Secrets leaking into a public corpus | gitleaks + pattern scans in CI; no-secrets rule in governance |
| Supply-chain (CI/actions) | Least-privilege workflows (`permissions: contents: read`), pinned action versions, Dependabot |

## 2. Integrity mechanisms

- **`content_hash`** — deterministic SHA-256 over canonical inputs; stamped on
  every derived artifact; regeneration must be byte-identical (CI-enforced).
- **`claim_signature`** — derived identity of each asserted proposition;
  duplicate active claims fail the gate; consumers can deduplicate without
  trusting transport.
- **Immutability guards** — reconstruct identity history from git and reject
  ID reassignment, triple edits-in-place, and unretired deletion. The one
  documented namespace alias rule (ADR-0027) is non-extendable and
  covered by dedicated tests.
- **Strict parsing** — duplicate YAML keys rejected; no silent last-wins.

## 3. Provenance as the trust boundary

- Every canonical object records **who/what produced it** (agent registry:
  `human:` / `process:` / `llm:` / `unknown:`), **by which method**, and for
  connections the full **review history**.
- AI assistance is always visible and never conflated with authority.
- Evidence blocks separate *what supports a claim* (sources, locators, stance)
  from *where the record came from* (provenance) — mixing them is a schema
  violation.
- `unknown:*` agents are permitted only as honest legacy attribution; new
  canonical assertions may not use them.

## 4. Operational security

- CI runs with read-only repository permissions; security job separate from
  the data gate.
- No network calls in the gate; the chain is deterministic and hermetic
  (poppler/tesseract only for the optional ingestion stage, which detects and
  reports missing tools).
- Explorer consumes a static JSON export in a sandboxed front-end; it makes no
  privileged calls.

## 5. Reporting & disclosure

- Integrity anomalies have a standing reporter (`scripts/integrity_anomalies.py`,
  part of the verify chain — currently 0 anomalies).
- Suspected scientific errors are handled by the review protocol (assert a
  correcting claim; supersede) — never by quiet edits.
- Vulnerabilities in tooling: open a private advisory via GitHub security
  advisories; do not patch around the gate.
