# INGESTION PRIMARY — PDF as Primary Feeder, HITL Before Canonical

**Status:** Authoritative, beginning, 0 entities. PDF ingestion is PRIMARY, direct agent addition SECONDARY, both require HITL.
**Related:** AGENT.md, PHYSICS-GOVERNING-LAWS.md, PHYSICS-MINIMAL-DESIGN-V2.md, PIPELINES.md, CURATION-PROTOCOL.md

> **Principle:** No entity becomes canonical without Human In The Loop explicitly editing markdown. AI extracts, AI shows markdown preview, human edits markdown, verification becomes easy.

---

## 1. Why PDF Primary, Direct Secondary

Old process: agent (LLM) directly writes `content/physics/...` — fast but bypasses human verification, risks hallucination, inconsistent placement.

New process (primary):
- **PDF (SI Brochure 9th ed., Halliday Resnick Walker textbook, custom PDFs)** → deterministic extraction → AI draft to markdown → human markdown edit → validation → canonical
- Human is you — you will be the human in HITL
- Direct agent addition still allowed but SECONDARY and must go through same HITL gate

Both flows have HITL before canonical — no entity can be `human_reviewed` or `canonical` without human markdown edit.

---

## 2. Primary Flow — PDF Ingestion

```
PDF File (BIPM SI Brochure, HRW, or custom upload)
  ↓
scripts/ingest.py (deterministic, poppler pdftotext + tesseract OCR, no LLM)
  → workflow/documents/<doc_id>/extracted.txt + meta.json (audit trail)
  ↓
AI Extraction (via webapp/providers.py — antigravity official local agent, or gemini_api, vertex_ai, openai_compatible)
  Prompt enforces AGENT.md standard procedure:
  - Must output markdown per template physics_entity_template.md
  - Must have scientifically agreed definition (exact SI with fixed constants, not general)
    Example metre: "The metre (symbol: m) is base unit of length in SI. Defined as length of path travelled by light in vacuum during 1/299,792,458 s. Exact c=299,792,458 m/s."
  - Must have governed_by from physics-governing-registry.yaml, subdomain matches law
  - Must have provenance.writer, link, original_author, retrieved_at, source_kind, source_refs>=1, external_ids
  - Must have historical timeline for laws
  - Must have evidence for connections with source_ref+locator+description
  → workflow/candidates/<doc_id>/<slug>.md (AI draft markdown preview)
  ↓
HITL STEP 1 — AI Shows Markdown Preview
  Webapp shows markdown in textarea, rendered preview side-by-side
  Human sees definition, units, governed_by, references
  ↓
HITL STEP 2 — Human Explicitly Edits Markdown File
  Human MUST edit markdown file explicitly — change definition, fix unit, add reference, etc.
  Audit: workflow/audit/audit.jsonl logs "candidate_edited" by human:curator.001 with timestamp
  File: workflow/candidates/<doc_id>/<slug>.md now has human edits
  Verification becomes easy because human edited file is plain markdown, diffable
  ↓
HITL STEP 3 — Human Stages Proposal
  Human clicks "Stage for human review" → moves to workflow/proposals/<slug>.md
  Audit logs "candidate_staged" by human
  ↓
Validation (deterministic, no LLM):
  python3 scripts/validate.py
  python3 scripts/physics_core_profile_check.py (mandatory source_kind, source, writer, link, retrieved_at, source_refs>=1, evidence>=1, historical for law canonical)
  python3 scripts/physics_governing_check.py (governed_by in registry, subdomain matches law, no self-governance)
  python3 scripts/hitl_check.py (NEW: verifies human edited markdown before canonical — checks audit trail, writer is human, file modified after AI draft)
  All must pass — if fails, human must fix markdown
  ↓
HITL STEP 4 — Human Reviews Entity
  python3 scripts/review_entity.py show <slug> — shows markdown + validation
  Human runs: python3 scripts/review_entity.py accept <slug> --reviewer human:curator.001
  → status becomes human_reviewed
  ↓
HITL STEP 5 — Human Canonicalizes
  python3 scripts/review_entity.py canonicalize <slug> --reviewer human:curator.001
  → copies to content/physics/<subdomain>/<slug>.md
  → creates connections with evidence
  → exports/knowledge.json regenerated
  Audit logs "entity_canonicalized" by human

No entity can skip HITL — hitl_check.py fails if audit shows no human edit.
```

---

## 3. Secondary Flow — Direct Agent Addition (LLM)

```
Agent (you, LLM) proposes entity per AGENT.md standard procedure
  ↓
Writes to workflow/candidates/agent/<slug>.md (AI draft markdown)
  Must follow template: id, type, name, domain, subdomain, status draft, definition (standard agreed with exact SI), symbol, unit, governed_by, provenance.writer/link/source_refs, historical for laws, external_ids
  ↓
Same HITL as primary: AI shows markdown preview → human explicitly edits → stages → validation (including hitl_check) → review_entity accept → canonicalize
```

Direct addition is secondary — PDF primary is preferred because source PDF provides provenance.

---

## 4. HITL Enforcement — hitl_check.py

**Script:** `scripts/hitl_check.py`

Checks before canonicalization:
1. **Audit trail:** `workflow/audit/audit.jsonl` must contain `candidate_edited` event for entity id by human (human:*) after AI draft
2. **Writer is human:** `provenance.writer` must start with `human:` not `llm:` or `unknown:`
3. **File modified by human:** `workflow/candidates/<id>/*.md` mtime > AI draft time, or `workflow/proposals/<id>.md` exists and was edited by human
4. **Markdown explicit:** File must exist as markdown, human-readable, diffable — not binary

If any fails → ERROR: "HITL required — human must explicitly edit markdown before canonical"

This script is part of `verify_all.py` chain — CI fails if HITL bypassed.

---

## 5. File Ingestion System — AI Extract to Markdown Preview

**Components:**

- `scripts/ingest.py` — deterministic PDF text extraction (poppler, tesseract)
- `scripts/pdf_ingest_primary.py` — primary feeder, wraps ingest.py + AI extraction
  - Usage: `python3 scripts/pdf_ingest_primary.py --pdf path/to/SI-Brochure.pdf --provider antigravity --model gemini-3-pro`
  - Output: `workflow/documents/<doc_id>/` + `workflow/candidates/<doc_id>/*.md`
- `webapp/server.py` + `webapp/core.py` — UI for upload, extraction, AI draft, markdown preview, human edit
  - Endpoint: `POST /api/documents/<doc_id>/extract` — runs ingest.py
  - Endpoint: `POST /api/documents/<doc_id>/draft` — runs AI extraction to markdown candidates
  - Endpoint: `GET /api/candidates?doc_id=<id>` — lists markdown previews
  - Endpoint: `PATCH /api/candidates/<candidate_id>` — human edits markdown (explicit)
  - Endpoint: `POST /api/candidates/<candidate_id>/stage` — stages to proposals
- `webapp/static/app.js` — shows markdown preview side-by-side with rendered, textarea for explicit edit, verification checklist

**AI Prompt (enforces standard procedure):**

```
You are STEMMA physics entity extractor. You MUST follow AGENT.md standard procedure.

Input: extracted text from PDF (SI Brochure or HRW textbook)

Output: one or more markdown files per template physics_entity_template.md, each with:

- id: stemma:phys.<slug> (lowercase, unique)
- type: quantity|unit|law
- name: Title Case
- domain: physics
- subdomain: from governing law (mechanics, measurement-units, etc.)
- status: draft
- definition: STANDARD scientific definition, exact SI with fixed constants, not general. Example metre: "The metre (symbol: m) is base unit of length in SI. Defined as length of path travelled by light in vacuum during 1/299,792,458 s. Exact c=299,792,458 m/s." Must include exact values, agreed per SI Brochure 9th ed. 2019.
- symbol, unit
- governed_by: from physics-governing-registry.yaml, at least 1, subdomain matches
- provenance: source_kind (textbook or standards-or-specification), source (full citation with page), writer human:curator.001, original_author BIPM/HRW, link https://www.bipm.org/en/publications/si-brochure, retrieved_at 2026-09-21
- source_refs: [nistsi, halliday]
- historical: for laws, stated_by, year, where, timeline
- external_ids: wd, qudt

Every entity must be verifiable via link + source_refs + external_ids triple-check.

No forbidden fields. No related_to. Only allowed relations.
```

---

## 6. Fundamental Books to Ingest (Primary Sources)

**Priority 1 — SI Brochure 9th ed. (BIPM 2019):**
- PDF: https://www.bipm.org/documents/20126/41483022/SI-Brochure-9.pdf
- Contains standard definitions for all 7 base units + derived units with exact constants
- Use to extract: metre, kilogram, second, ampere, kelvin, mole, candela, newton, joule, watt, pascal, coulomb, volt, ohm, tesla, hertz, etc.

**Priority 2 — Halliday Resnick Walker Fundamentals of Physics 12th ed.:**
- Chapters: Ch1 Measurement (length, mass, time, area, volume), Ch2-5 Mechanics (speed, velocity, acceleration, force, weight, momentum, energy, work, power, pressure, density, torque, angular-momentum, impulse, frequency)
- Contains standard definitions for quantities + laws (Newton's laws, work-energy, impulse-momentum, conservation laws)

**Priority 3 — Custom PDFs you upload:**
- Any PDF you upload via webapp becomes primary source, AI extracts to markdown, you edit, canonicalize

---

## 7. Verification of Entities — Standard Procedure Checklist

Before canonical, every entity must pass:

- [ ] **Standard definition:** Contains exact SI definition with fixed constants (e.g., metre = light path 1/299792458 s, c exact), not general description. Must include "Exact:" with value.
- [ ] **Units:** Symbol present, unit display present, dimensions compatible with governing law
- [ ] **Governed_by:** >=1, each in registry, subdomain matches entity subdomain
- [ ] **Source_refs:** >=1, each resolves to sources/*.yaml with url/doi/isbn
- [ ] **Provenance:** source_kind, source (full citation), writer human:*, original_author, link (bipm.org or wiley.com), retrieved_at all present
- [ ] **Historical:** For law/model/equation, timeline with year, by, event
- [ ] **External_ids:** wd: Q... at least
- [ ] **HITL:** Audit shows human edited markdown, writer is human, file modified after AI draft — hitl_check.py passes
- [ ] **Connections:** At least 1 connection with evidence source_ref+locator+description
- [ ] **Validation:** validate.py + physics_core_profile_check.py + physics_governing_check.py + hitl_check.py all OK

If any fails → human must fix markdown in webapp before staging.

---

## 8. Webapp UI — Markdown Before Canonical

**UI Flow:**

1. Upload PDF → shows in Documents list, status uploaded
2. Click Extract → runs ingest.py, shows extracted text preview
3. Click Draft with AI → runs AI extraction, creates candidates, shows markdown preview:
   - Left: textarea with raw markdown (human can edit explicitly)
   - Right: rendered preview (definition, symbol, unit, governed_by, references)
   - Checklist: standard definition? units? governed_by? source_refs? writer? link? historical?
4. Human edits markdown explicitly → Save → audit logs candidate_edited by human
5. Click Stage → moves to proposals, validation runs, shows hitl_check result
6. Review entity → accept → canonicalize — both require human reviewer

Human explicitly markdown file so verification becomes easy — plain text diff, no binary.

---

## 9. Reset Entities — Clean Up

Current: 0 entities after reset (archived 74 to archive/beginning-74-entities/)

Next: Add entities via new primary system with HITL — you will be human.

Commands to add first entity via primary:

```bash
# 1. Upload SI Brochure PDF via webapp or CLI
python3 scripts/pdf_ingest_primary.py --pdf ~/SI-Brochure-9.pdf --provider antigravity --model gemini-3-pro

# 2. Open webapp
python3 webapp/server.py --port 8081
# Open http://localhost:8081 → Documents → Extract → Draft → Edit markdown → Stage

# 3. Validate HITL
python3 scripts/hitl_check.py --entity metre

# 4. Review
python3 scripts/review_entity.py accept metre --reviewer human:curator.001
python3 scripts/review_entity.py canonicalize metre --reviewer human:curator.001

# 5. Verify
python3 scripts/verify_all.py
```

---

**End of Primary Ingestion**
