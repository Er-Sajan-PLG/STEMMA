# PIPELINES (BEGINNING, NO LEGACY, HITL, PDF PRIMARY)

**Status:** Beginning, 0 entities after clean reset. PDF ingestion PRIMARY, direct LLM addition SECONDARY, both require HITL before canonical.

```
PRIMARY FLOW — PDF Ingestion (preferred):
─────────────────────────────────────────
PDF File (SI Brochure 9th ed., HRW 12th ed., custom PDFs)
  ↓
scripts/ingest.py (deterministic, poppler pdftotext + tesseract OCR, no LLM)
  → workflow/documents/<doc_id>/extracted.txt + meta.json
  ↓
AI Extraction (via webapp/providers.py — antigravity official local agent first, then gemini_api, vertex_ai, openai_compatible)
  Prompt enforces AGENT.md standard procedure:
  - Must output markdown per physics_entity_template.md
  - Must have scientifically agreed definition (exact SI with fixed constants, not general)
    Example metre: "The metre (symbol: m) is base unit of length in SI. Defined as length of path travelled by light in vacuum during 1/299,792,458 s. Exact c=299,792,458 m/s."
  - Must have governed_by from physics-governing-registry.yaml, subdomain matches law
  - Must have provenance.writer human:curator.001, link, original_author, retrieved_at, source_kind, source_refs>=1, external_ids
  - Must have historical timeline for laws
  → workflow/candidates/<doc_id>/<slug>.md (AI draft markdown preview)
  ↓
HITL STEP 1 — AI Shows Markdown Preview
  Webapp shows markdown in textarea + rendered preview side-by-side
  Human sees definition, units, governed_by, references, checklist
  ↓
HITL STEP 2 — Human Explicitly Edits Markdown File (mandatory)
  Human MUST edit markdown file explicitly — change definition, fix unit, add reference
  Audit: workflow/audit/audit.jsonl logs candidate_edited by human:curator.001
  File: workflow/candidates/<doc_id>/<slug>.md now has human edits, plain text diffable
  Verification becomes easy because human edited file is markdown
  ↓
HITL STEP 3 — Human Stages Proposal
  Human clicks Stage for human review → moves to workflow/proposals/<slug>.md
  Audit logs candidate_staged by human
  ↓
Validation (deterministic, no LLM):
  python3 scripts/validate.py (schema, identity, refs)
  python3 scripts/physics_core_profile_check.py (mandatory source_kind, source, writer, link, retrieved_at, source_refs>=1, evidence>=1, historical for law)
  python3 scripts/physics_governing_check.py (governed_by in registry, subdomain matches law, no self-governance)
  python3 scripts/hitl_check.py (NEW: verifies human edited markdown before canonical — audit trail, writer human, file modified after AI draft)
  All must pass — if fails, human must fix markdown
  ↓
HITL STEP 4 — Human Reviews Entity
  python3 scripts/review_entity.py show <slug> — shows markdown + validation
  python3 scripts/review_entity.py accept <slug> --reviewer human:curator.001 → human_reviewed
  ↓
HITL STEP 5 — Human Canonicalizes
  python3 scripts/review_entity.py canonicalize <slug> --reviewer human:curator.001
  → copies to content/physics/<subdomain>/<slug>.md
  → creates connections with evidence source_ref+locator+description
  → exports/knowledge.json regenerated
  Audit logs entity_canonicalized by human

No entity can skip HITL — hitl_check.py fails if audit shows no human edit.


SECONDARY FLOW — Direct Agent Addition (LLM, allowed but secondary):
──────────────────────────────────────────────────────────────────────
Agent (LLM, you) proposes entity per AGENT.md standard procedure
  ↓
Writes to workflow/candidates/agent/<slug>.md (AI draft markdown)
  Must follow template: id, type, name, domain, subdomain, status draft, definition (standard agreed with exact SI), symbol, unit, governed_by, provenance.writer/link/source_refs, historical for laws, external_ids
  ↓
Same HITL as primary: AI shows markdown preview → human explicitly edits → stages → validation (including hitl_check) → review_entity accept → canonicalize

Direct addition is secondary — PDF primary is preferred because source PDF provides provenance.


VALIDATION CHAIN (authoritative):
─────────────────────────────────
content/physics/ (0 entities now, will grow via primary ingestion, governed_by law)
+ sources/ (3 records, nistsi, halliday, etc.)
+ connections/ (0 now, mandatory evidence source_ref+locator+description)
↓
validate.py (schema, identity, refs, export to exports/knowledge.json)
↓
status_truth.py (truth report)
↓
physics_core_profile_check.py (mandatory source, writer human:*, link, source_refs, evidence, history for law)
↓
physics_governing_check.py (governed_by in registry, subdomain matches law, deterministic, no LLM)
↓
hitl_check.py (HITL enforcement: audit trail candidate_edited by human:*, writer human:*, markdown explicit edit before canonical)
↓
graph_analysis.py (invariants)
↓
export_review_aware.py (review-aware export)
↓
exports/knowledge.json (v2.2.0, deterministic, content-hash)

No legacy, this is beginning. PDF primary ingestion with HITL.
