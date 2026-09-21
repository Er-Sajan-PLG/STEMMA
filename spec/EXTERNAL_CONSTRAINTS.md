# EXTERNAL CONSTRAINTS SWEEP — CORE-GATE-EXPORT slice

Protocol §4.3. Each: authority/source, scope, applicability, evidence,
requirement impact. Uncertain applicability → UNRES record, not assumption.

| # | Authority / Source | Scope | Applicability | Evidence | Requirement impact |
|---|---|---|---|---|---|
| XC-1 | CC-BY-4.0 (`LICENSE`) + MIT (`LICENSE-CODE`) | Knowledge content / code | Applicable to all published artifacts | repo license files | Export/consumption must preserve attribution semantics; spec metadata must keep code/content license split |
| XC-2 | BIPM SI Brochure 9th ed. (public standard text) | Source for SI definitions | Applicable: used as source_ref for metre | `sources/src.nist-si-brochure-9th.yaml`; `metre.md` provenance | Content accuracy obligation → verification method INSPECTION against source |
| XC-3 | Commercial textbook copyrights (HRW, Campbell, CLRS, Atkins, Carroll) | Ingestion source PDFs | Potentially applicable: named intended sources in docs | ROADMAP/SEMANTIC-ACQUISITION-PIPELINE (CLAIM); `workflow/` git-ignored | Ingested source PDFs MUST NOT be committed; extraction/licensing review needed before distribution of derived text spans → REQ-STEMMA-OPS-005, UNRES-STEMMA-OPS-001 |
| XC-4 | GitHub platform (Actions, gitleaks-action, commitlint action) | CI execution | Applicable | `.github/workflows/` | CI availability is assumed; wasm/pin risk recorded in ASSUMPTIONS |
| XC-5 | Frontier model provider terms (OpenRouter, NVIDIA NIM, Google, OpenAI) | Model selector operation | Potentially applicable: webapp/RAG reference paths | `webapp/providers.py`, `schema/llm-registry.yaml` | Out of deep scope (webapp NOT_YET_ASSESSED); key handling rules → REQ-STEMMA-SEC-002 |
| XC-6 | Consumer contracts toward LearningHub / PROFESSOR-J | Cross-repo semantics | Potentially applicable: consumers declared, no executing counterpart | `schema/consumer-registry.yaml`; docs/CONSUMERS.md (CLAIM) | Export contract 2.2.0 additive-semver policy → REQ-STEMMA-EXP-002; ownership UNRES-STEMMA-INTEG-001 |
| XC-7 | JSON Schema 2020-12 semantics (jsonschema lib) | Validation contract | Applicable | `tests/versioning/test_deterministic_export.py` jsonschema validation | Schema semantics inherited; validator behavior pinned via requirements.txt |

No regulatory/privacy obligations identified for the slice (no personal data
processed by the gate/export); recorded as reviewed-and-not-applicable rather
than ignored.
