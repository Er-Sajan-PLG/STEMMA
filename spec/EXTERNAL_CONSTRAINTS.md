# EXTERNAL CONSTRAINTS SWEEP — CORE-GATE-EXPORT slice

Protocol §4.3. Each: authority/source, scope, applicability, evidence,
requirement impact. Uncertain applicability → UNRES record, not assumption.

| # | Authority / Source | Scope | Applicability | Evidence | Requirement impact |
|---|---|---|---|---|---|
| XC-1 | CC-BY-4.0 (`LICENSE`) + MIT (`LICENSE-CODE`) | Knowledge content / code | Applicable to all published artifacts | repo license files | Export/consumption must preserve attribution semantics; spec metadata must keep code/content license split |
| XC-2 | BIPM SI Brochure 9th ed. (public standard text) | Source for SI definitions | Applicable: used as source_ref for metre | `sources/src.nist-si-brochure-9th.yaml`; `metre.md` provenance | Content accuracy obligation → verification method INSPECTION against source |
| XC-3 | Commercial textbook copyrights (HRW, Campbell, CLRS, Atkins, Carroll) | Ingestion source PDFs | **Applicable — policy ruled 2026-10-01 (see below)** | ROADMAP/SEMANTIC-ACQUISITION-PIPELINE; `workflow/` git-ignored; `sources/*.yaml` citation records | Ingested source PDFs MUST NOT be committed; **no verbatim passages are retained in any committed artifact** (citation metadata + re-expressed definitions only) → REQ-STEMMA-OPS-005; UNRES-STEMMA-OPS-001 **CLOSED 2026-10-01** |
| XC-4 | GitHub platform (Actions, gitleaks-action, commitlint action) | CI execution | Applicable | `.github/workflows/` | CI availability is assumed; wasm/pin risk recorded in ASSUMPTIONS |
| XC-5 | Frontier model provider terms (OpenRouter, NVIDIA NIM, Google, OpenAI) | Model selector operation | Potentially applicable: webapp/RAG reference paths | `webapp/providers.py`, `schema/llm-registry.yaml` | Out of deep scope (webapp NOT_YET_ASSESSED); key handling rules → REQ-STEMMA-SEC-002 |
| XC-6 | Consumer contracts toward LearningHub / PROFESSOR-J | Cross-repo semantics | Potentially applicable: consumers declared, no executing counterpart | `schema/consumer-registry.yaml`; docs/CONSUMERS.md (CLAIM) | Export contract 2.2.0 additive-semver policy → REQ-STEMMA-EXP-002; ownership UNRES-STEMMA-INTEG-001 |
| XC-7 | JSON Schema 2020-12 semantics (jsonschema lib) | Validation contract | Applicable | `tests/versioning/test_deterministic_export.py` jsonschema validation | Schema semantics inherited; validator behavior pinned via requirements.txt |

No regulatory/privacy obligations identified for the slice (no personal data
processed by the gate/export); recorded as reviewed-and-not-applicable rather
than ignored.

---

## XC-3 amendment — textbook rights policy (owner ruling 2026-10-01)

`UNRES-STEMMA-OPS-001` asked what the licensing position is for definition text
extracted from commercial textbooks, and what evidence may be committed. The
owner ruled **option (b): excerpt-free metadata only.** Recorded here because it
is an external constraint, not merely an internal convention.

**The rule.** Only two things derived from a copyrighted textbook may be
committed:

1. **Citation metadata** — title, authors, year, publisher, edition, ISBN, URL,
   language, `source_role`, locator (chapter/section). This is what
   `sources/*.yaml` already holds, and it is unambiguously safe: a
   bibliographic reference is not a reproduction.
2. **Re-expressed definitions** — STEMMA's own statement of the concept, written
   in the project's voice. Facts and ideas are not copyrightable; the *expression*
   is. `content/**/*.md` definitions fall here.

**What must never be committed.**

- Source PDFs. (Already true: `workflow/` is git-ignored, XC-3.)
- Verbatim passages, however short, from a copyrighted body.
- Anything under `workflow/audit/`, `workflow/extraction/`, or
  `workflow/uploads/` — these may contain extracted spans.

**How this is enforced, not merely asserted.**

- `sources/*.yaml` are citation records with no body-text field (verified: the
  three live source records carry metadata only).
- The HITL review manifest (`scripts/review_manifest.py`,
  `UNRES-STEMMA-HITL-001` option (c)) is **hash-only by construction**: it emits
  ids, declared provenance, promotion history, and sha256 digests, and no
  definition or source text. It is therefore committable under this policy — which
  is precisely why that option was chosen over committing the raw trail.
  `tests/repo/test_review_manifest.py` asserts no definition fragment from any
  record appears in the manifest, and that no text-bearing key exists in it.
- `hitl_check.py --all` and `validate.py`'s content-layer rule bind review claims
  to `content/` records, none of which hold source text.

**Residual, recorded honestly.** This is an owner policy position, not external
legal advice. It is the conservative reading (no verbatim reproduction at all,
therefore no reliance on fair-use/fair-dealing defences, which vary by
jurisdiction). Should the project later wish to retain short quotations for
audit fidelity, that would be a *new* decision requiring explicit attribution
terms and an excerpt cap; the safer default chosen here needs neither.

**Consequence for REQ-STEMMA-OPS-005:** the source-registry obligation is
satisfied by citation-complete `sources/*.yaml` records; no derived-text
distribution occurs, so no licensing review of derived spans is outstanding.
