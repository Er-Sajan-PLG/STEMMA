# AGENT.md — Physics Entity Addition Protocol (Deterministic, Time-Invariant, HITL, PDF Primary)

**Status:** Authoritative for all agents (human, llm, process) adding physics entities. Companion to `AGENTS.md`, `GOVERNANCE.md`, `PHYSICS-GOVERNING-LAWS.md`, `PHYSICS-MINIMAL-DESIGN-V2.md`, `INGESTION-PRIMARY.md`.
**Purpose:** Ensure every entity is added the same way regardless of when, who, or which model — no LLM reasoning drift. No entity becomes canonical without HITL.
**Enforcement:** `scripts/physics_core_profile_check.py` + `scripts/physics_governing_check.py` + `scripts/hitl_check.py` + `scripts/validate.py` — all must pass.

> **Core Principles:**
> 1. Time of addition does not matter. Governing laws do. If two agents add `mass` in 2026 and 2030, they must produce identical `id`, `subdomain`, `governed_by`, and placement, because governing laws are deterministic.
> 2. PDF ingestion is PRIMARY feeder. Direct LLM addition is SECONDARY. Both require HITL before canonical — human must explicitly edit markdown file.
> 3. AI extracts, AI shows data in markdown preview, human explicitly edits markdown file so verification becomes easy.

---

## 0. Ingestion Modes — Primary vs Secondary

**PRIMARY — PDF Ingestion (preferred):**
```
PDF (SI Brochure 9th ed., HRW 12th ed., custom) → ingest.py (deterministic) → AI draft to markdown → HITL human edits markdown → stage → validate (including hitl_check) → review_entity accept → canonicalize
```
- Source: BIPM SI Brochure, Halliday Resnick Walker textbook, or custom PDFs you upload
- Tool: `python3 scripts/pdf_ingest_primary.py --pdf path/to/file.pdf`
- UI: `python3 webapp/server.py --port 8081` → Upload → Extract → Draft → Edit markdown → Stage
- Output: `workflow/candidates/<doc_id>/<slug>.md` (AI draft markdown preview) → human edits → `workflow/proposals/<slug>.md`
- HITL: Audit logs `candidate_edited` by human:curator.001, writer must be human:*, markdown file must be explicitly edited before canonical

**SECONDARY — Direct Agent Addition (LLM):**
```
Agent (you, LLM) proposes entity per this protocol → writes to workflow/candidates/agent/<slug>.md (AI draft markdown) → same HITL → human edits → stage → validate → review → canonical
```
- Direct writing to `content/physics/...` is FORBIDDEN — must go via workflow/candidates/ + HITL
- Tool: Agent writes markdown file to workflow/, then human edits
- Same HITL enforcement: hitl_check.py fails if no human edit

**Both modes require HITL before canonical — enforced by hitl_check.py and review_entity.py.**

---

## 1. Before Adding Any Entity — Read Governing Laws

**Mandatory reading order (no skipping):**

1. `docs/INGESTION-PRIMARY.md` — primary PDF ingestion with HITL flow
2. `docs/PHYSICS-GOVERNING-LAWS.md` — what laws exist, what they govern, what goes where
3. `schema/physics-governing-registry.yaml` — machine-readable governing laws, allowed quantities per subdomain
4. `docs/PHYSICS-MINIMAL-DESIGN-V2.md` — minimal schema with dual verification + history rules
5. `docs/DOMAIN-MODEL.md` §8 — physics profile
6. `schema/concept.schema.json` v1.3.0 — required fields

**Do NOT rely on LLM reasoning to decide subdomain or governing law.** Use deterministic mapping in `PHYSICS-GOVERNING-LAWS.md` §3.

---

## 2. Decision Procedure — What Goes Where (No LLM)

For new entity `<slug>`:

```
Step 1: What law defines or requires <slug>?
  → Search PHYSICS-GOVERNING-LAWS.md tables
  → Example: mass → Newton's Second Law requires mass
  → If not found → propose new law via ADR, do NOT invent subdomain

Step 2: Law's subdomain = entity's subdomain
  → newtons-second-law → mechanics
  → So mass → mechanics
  → File path: content/physics/<subdomain>/<slug>.md (only after HITL + canonicalize)

Step 3: Law's dimensions → entity's dimensions must be compatible
  → mechanics → only M, L, T (no I, no Θ)
  → mass → M → valid

Step 4: Entity's governed_by = law id(s)
  → mass governed_by: [newtons-second-law, conservation-energy, si-definitions]

Step 5: If entity is law itself, governed_by = more fundamental law
  → newtons-second-law governed_by: [conservation-momentum, conservation-energy, dimensional-analysis]
  → Never self-governance

If Step 1 fails (no law governs entity), entity does NOT belong in physics-core v0.1 — defer.
```

This ensures same placement in 2026 or 2030.

---

## 3. Entity Creation Protocol — Step-by-Step (Time-Invariant, HITL)

### 3.0 Choose Ingestion Mode

- **Primary (preferred):** Upload PDF via webapp or `pdf_ingest_primary.py` → AI extracts → markdown preview → human edits
- **Secondary:** Agent writes markdown draft to `workflow/candidates/agent/<slug>.md` → human edits

Both must produce markdown file per template `scripts/templates/physics_entity_template.md` and go through HITL.

### 3.1 Choose ID (Deterministic)

- Grammar: `stemma:phys.<slug>` — slug lowercase [a-z0-9-], never reused
- Check `schema/id-domain-map.yaml`: prefix `phys` → domain `physics` → directory `physics`
- Check uniqueness: `grep -r "id: stemma:phys.<slug>" content/`
- Filename = slug: `content/physics/<subdomain>/<slug>.md` must match final ID segment (only after canonicalize, not before)

### 3.2 Scientific Definition — Agreed, Referenced, Exact SI (Canonical)

**Every entity must have a STANDARD scientific definition that everyone has agreed to, with exact SI constants and reference.**

- **What is standard definition?** The definition agreed internationally in SI Brochure 9th ed. (BIPM 2019) with fixed constants, or in Halliday Resnick Walker 12th ed., not general description. Must show agreed status and source reference.

- **How to write — must be exact, not general:**
  - `definition: >-` — 1-3 sentences, curriculum-agnostic, verifiable, must include exact SI with fixed constants
  - **Example metre (user specified exactly):** "The metre (symbol: m) is the base unit of length in the International System of Units (SI). It is scientifically defined as the length of the path travelled by light in a vacuum during a time interval of 1/299,792,458 of a second. Exact: c=299,792,458 m/s."
  - **Example kilogram:** "The kilogram (symbol: kg) is the base unit of mass in SI. Defined by fixing Planck constant h=6.62607015e-34 J·s, with metre and second defined via c and ΔνCs. Exact: h=6.62607015×10⁻³⁴ kg·m²·s⁻¹."
  - **Example second:** "The second (symbol: s) is the base unit of time in SI. Defined by fixing caesium frequency ΔνCs=9,192,631,770 Hz. Exact: ΔνCs=9,192,631,770 s⁻¹."
  - **Example newton:** "The newton (symbol: N) is the SI derived unit of force, defined as kg·m·s⁻². Exact: 1 N = 1 kg·m/s² per SI Brochure, derived from Newton's Second Law F=ma."
  - **Must include:** Symbol, what it is, how defined via fixed constant or law, exact value with "Exact:" keyword, agreed per SI Brochure 9th ed.
  - **For quantities (length, mass, time):** Must state dimension (L, M, T), unit (metre, kilogram, second), governing law, agreed as base per SI
  - **For laws (Newton's laws):** Must state formula F=ma exact, historical year, agreed since Principia

- **Reference mandatory — triple verification:**
  - `provenance.source: >-` — full citation with page/equation: `BIPM SI Brochure 9th ed. (2019) §2.3.1, p130: The metre is defined as... Exact c=299,792,458 m/s` or `Halliday Resnick Walker 12th ed. Ch 1, p4: Length is...`
  - `provenance.source_kind: textbook | standards-or-specification` — textbook = HRW, standards = SI Brochure, both community-accepted, mandatory for profile check
  - `provenance.link: https://www.bipm.org/en/publications/si-brochure` — URL to BIPM SI Brochure or Wiley HRW for triple-check, mandatory
  - `provenance.writer: human:curator.001` — who wrote this file — must be human:* for HITL, not llm:*
  - `provenance.original_author: "BIPM & Halliday, Resnick, Walker"` — who originally agreed
  - `provenance.retrieved_at: "2026-09-21"` — ISO date, mandatory
  - `source_refs: [stemma:src.nist-si-brochure-9th, stemma:src.halliday-resnick-walker-12th]` — each must have canonical file in sources/ with url/doi/isbn for verification, >=1 mandatory
  - `external_ids: wd: Q...` — Wikidata QID for cross-check, mandatory wd

**Fundamental vs Derived (must be visible in 3D, prominent):**
- **Fundamental (SI base, 7):** length (L), mass (M), time (T), electric-current (I), thermodynamic-temperature (Θ), amount-substance (N), luminous-intensity (J) — defined by fixing constants per SI 2019, agreed internationally, must be visible in explorer
- **Derived (from fundamentals):** area (L²), volume (L³), speed/velocity (L T⁻¹), acceleration (L T⁻²), density (M L⁻³), force (M L T⁻²), pressure (M L⁻¹ T⁻²), energy/work (M L² T⁻²), power (M L² T⁻³), etc. — defined via governing laws, dimensions must be compatible, must show derivation exact

All definitions must be verifiable via link + source_refs + external_ids triple-check, and must have agreed status with reference.

### 3.2 Fill Frontmatter (Mandatory Fields — Dual Verification + HITL)

Use template `scripts/templates/physics_entity_template.md`:

```yaml
id: stemma:phys.<slug>
type: quantity | unit | law | equation | concept | model | phenomenon  # from DOMAIN-MODEL
name: "<Human readable, Title Case>"
domain: physics
subdomain: mechanics | electricity-magnetism | thermal-physics | measurement-units  # from governing law
status: draft  # always draft initially, human_reviewed/canonical only after HITL + human review
definition: >-
  STANDARD scientific definition with exact SI, agreed per SI Brochure 9th ed. 2019.
  Example: "The metre (symbol: m) is base unit of length in SI. Defined as length of path travelled by light in vacuum during 1/299,792,458 s. Exact c=299,792,458 m/s."

symbol: "<symbol>"  # e.g., m, kg, s, N — mandatory for unit
unit: "<unit display>"  # e.g., kilogram (kg) — mandatory for quantity

governed_by:  # MANDATORY — deterministic placement, no LLM
  - stemma:phys.newtons-second-law
  - stemma:phys.si-definitions

provenance:  # MANDATORY — dual verification + HITL
  ai_drafted: false  # true if LLM drafted, false if human authored — but writer must be human:* for HITL
  source_kind: standards-or-specification  # textbook | academic-or-research | standards-or-specification | institutional | other — mandatory
  source: >-
    Full citation with page and exact: BIPM SI Brochure 9th ed. (2019) §2.3.1, p130: The metre is defined as path of light in vacuum during 1/299,792,458 s. Exact c=299,792,458 m/s.
  writer: human:curator.001  # who wrote this file — must be human:* for HITL, must resolve in agent-registry.yaml, not llm:*
  drafted_by: llm:antigravity-001  # optional (schema 1.3.0): machine that produced the draft — origin kept, never rewritten
  original_author: "BIPM"  # who originally stated science — BIPM or Halliday, Resnick, Walker
  link: "https://www.bipm.org/en/publications/si-brochure"  # URL — mandatory, for triple-check
  retrieved_at: "2026-09-21"  # ISO date — mandatory
  reviewer: null
  reviewed_at: null

source_refs:  # MANDATORY — canonical records, dual verification, >=1
  - stemma:src.nist-si-brochure-9th

historical:  # Optional for draft, MANDATORY for law/model/equation when human_reviewed/canonical
  stated_by: "BIPM"
  year: 2019
  where: "SI Brochure 9th ed."
  timeline:
    - year: 1983
      by: BIPM
      event: Metre defined via c
    - year: 2019
      by: BIPM
      event: SI redefinition with fixed constants

external_ids:
  wd: Q11573
  qudt: unit-M
```

**Rules:**
- `source_kind`, `source`, `writer`, `link`, `retrieved_at` — all mandatory for physics-core v2 (profile check fails otherwise)
- `writer` must be `human:*` for HITL — `llm:*` or `unknown:*` fails hitl_check.py
- `source_refs` array >=1, each must have file in `sources/` with url/doi/isbn
- `governed_by` >=1, each must be in `physics-governing-registry.yaml`, subdomain must match law's subdomain
- No `learning_objectives`, `real_world_applications`, `key_experiments`, `common_misconceptions` — forbidden per ADR-0041
- `subdomain` must match subdomain of governing law(s)
- `definition` must contain exact SI with "Exact:" and agreed reference — not general

### 3.3 AI Extract to Markdown Preview — Human Explicit Edit (HITL)

**Primary flow:**
1. PDF uploaded → `workflow/documents/<doc_id>/`
2. AI extraction (via providers.py) creates markdown draft: `workflow/candidates/<doc_id>/<slug>.md`
3. Webapp shows markdown preview:
   - Left: textarea with raw markdown (human can edit explicitly)
   - Right: rendered preview (definition, symbol, unit, governed_by, references)
   - Checklist: standard definition? units? governed_by? source_refs? writer? link? historical?
4. Human explicitly edits markdown file — changes definition, fixes unit, adds reference
5. Human clicks Save → audit logs `candidate_edited` by `human:curator.001` with timestamp → `workflow/candidates/<doc_id>/<slug>.md` now has human edits
6. Verification becomes easy because markdown file is plain text, diffable, human-readable

**Secondary flow (direct agent):**
1. Agent writes to `workflow/candidates/agent/<slug>.md` (AI draft)
2. Same as primary: human edits markdown explicitly → Save → audit log

**HITL enforcement:**
- `workflow/audit/audit.jsonl` must contain `candidate_edited` event by `human:*` for entity id after AI draft
- `provenance.writer` must start with `human:` not `llm:`
- `workflow/candidates/` and `workflow/proposals/` must have markdown file with human edits
- `hitl_check.py` verifies all before canonicalization — fails if no human edit

### 3.4 Create Canonical Source Record (Dual Verification)

If `source_refs` contains id not yet in `sources/`:

1. Create `sources/src.<slug>.yaml` using template `scripts/templates/physics_source_template.yaml`
2. Must have: id, type, citation, title, authors[], year, publisher, url/doi/isbn (at least one for verifiability), writer, retrieved_at
3. Validate: `python3 scripts/validate.py` checks id format, `physics_core_profile_check.py` checks url/doi/isbn present

### 3.5 Add Historical Timeline (For Laws)

If `type` is `law`, `model`, `equation`, `experiment`:
- Draft: historical optional but encouraged
- human_reviewed/canonical: historical MANDATORY with `stated_by`, `year`, `where`, `timeline[]` with year, event, by
- Timeline shows progression for verification and future change (e.g., Newton 1687 → Euler 1749 → Einstein 1916)

### 3.6 Validate Deterministically (No LLM, Includes HITL)

After human edited markdown and staged:

```bash
python3 scripts/validate.py
# Must be OK: X entities valid

python3 scripts/physics_core_profile_check.py
# Must be OK: 0 violations
# Checks: mandatory source fields, source_refs resolve, evidence for connections, historical for law canonical, no forbidden fields, no related_to

python3 scripts/physics_governing_check.py
# Must be OK: 0 violations
# Checks: every entity has governed_by, subdomain matches law, no self-governance, law entities exist

python3 scripts/hitl_check.py --entity <slug>
# Must be OK: HITL satisfied — human edited markdown before canonical
# Checks: audit trail candidate_edited by human:*, writer human:*, markdown explicit edit

python3 scripts/status_truth.py --write
# Updates README status block — must commit

python3 scripts/verify_all.py
# Full chain — must be green, includes hitl_check
```

All 5 must pass. If any fails, human must fix markdown — do not rely on model reasoning to guess.

### 3.7 Connections (Every Claim Has Source)

For every new quantity/law, add at least 1 connection using template `physics_connection_template.yaml`:

```yaml
id: stemma:conn.00000X  # sequential, never reused
source: stemma:phys.newtons-second-law
relation: mathematically_requires  # only from minimal set ADR-0042
target: stemma:phys.mass
context:
  domain: physics
  subdomain: mechanics
  regime: [classical]
evidence:  # MANDATORY >=1
  - type: textbook
    stance: supports
    source_ref: stemma:src.halliday-resnick-walker-12th
    locator: "Ch 5, Eq 5-1, p112"
    description: "Why source supports claim"
provenance:
  asserted_by: {type: human, id: human:curator.001}
  generated_by: {type: human, id: human:curator.001}
  method: {type: manual}
```

**Allowed relations only (ADR-0042):** `mathematically_requires`, `derived_from`, `appears_in_law`, `applies_to`, `generalizes`, `special_case_of`, `part_of`, `approximates`. No `related_to`.

---

## 4. Governance — What Governs What

**Governing hierarchy:**

```
INGESTION-PRIMARY.md (PDF primary + HITL, human is you)
    ↓
PHYSICS-GOVERNING-LAWS.md (human-readable guiding point)
    ↓
schema/physics-governing-registry.yaml (machine-readable, deterministic)
    ↓
workflow/candidates/<doc_id>/<slug>.md (AI draft markdown preview)
    ↓
Human explicitly edits markdown → workflow/proposals/<slug>.md (human-approved)
    ↓
content/physics/<subdomain>/<slug>.md (canonical, only after HITL + human review)
    ↓
connections/*.yaml (law --mathematically_requires--> quantity, with evidence)
    ↓
scripts/hitl_check.py + physics_governing_check.py + physics_core_profile_check.py (verification, deterministic, no LLM)
```

**No LLM reasoning in placement:** Subdomain, governed_by, dimensions are decided by registry lookup, not model inference. Same input → same output any time.

**HITL enforcement:** No entity becomes canonical without human markdown edit — audit trail + writer human:* + markdown explicit.

**Laws embedded in 3 places (triple redundancy):**
1. `PHYSICS-GOVERNING-LAWS.md` table
2. `physics-governing-registry.yaml` machine-readable
3. As entities themselves in `content/physics/` with historical timeline

---

## 5. Time-Invariant + HITL Guarantee

- **ID stability:** `stemma:phys.<slug>` never reused, never reassigned — guard `check_id_immutability.py`
- **Deterministic placement:** `governed_by` → `subdomain` mapping is in registry, not model
- **Source audit trail:** `provenance.writer`, `link`, `retrieved_at`, `source_refs` + canonical `sources/` record + external URL = triple-checkable now or in 10 years
- **HITL audit trail:** `workflow/audit/audit.jsonl` logs `candidate_edited` by human:*, markdown file diffable, verification easy
- **History progression:** `historical.timeline` shows previous and progression, so future change can compare old vs new
- **Validation is same:** `validate.py` + `physics_core_profile_check.py` + `physics_governing_check.py` + `hitl_check.py` are deterministic, no wall clock, content-hash stamped

If you add entity in 2026 or 2030 following this protocol (PDF primary → AI draft → human edit → canonical), you will produce identical file (except `retrieved_at` date, which is allowed to differ).

---

## 6. Checklist Before Commit (Definition of Done for Physics Entity v2 + HITL)

- [ ] Ingestion mode chosen: PDF primary preferred, direct secondary allowed but both need HITL
- [ ] ID follows `stemma:phys.<slug>` grammar, unique, filename matches slug
- [ ] `type` is one of 9, `domain: physics`, `subdomain` from governing law
- [ ] `definition` STANDARD scientific definition with exact SI and fixed constants, not general, includes "Exact:" + agreed per SI Brochure 9th ed. + reference
- [ ] `governed_by` >=1, each in `physics-governing-registry.yaml`, subdomain matches
- [ ] `provenance.source_kind`, `source`, `writer` (human:*), `original_author`, `link`, `retrieved_at` all present
- [ ] `source_refs` >=1, each resolves to file in `sources/` with url/doi/isbn
- [ ] If `type` law/model/equation and status human_reviewed/canonical: `historical` with `stated_by`, `year`, `timeline`
- [ ] No forbidden fields: `learning_objectives`, `real_world_applications`, `key_experiments`, `common_misconceptions`
- [ ] At least 1 connection with mandatory evidence (source_ref, locator, description)
- [ ] AI draft markdown preview exists in `workflow/candidates/<doc_id>/<slug>.md`
- [ ] **HITL:** Human explicitly edited markdown file, audit logs `candidate_edited` by human:*, writer is human:*, file modified after AI draft — `hitl_check.py` passes
- [ ] `validate.py` OK
- [ ] `physics_core_profile_check.py` OK
- [ ] `physics_governing_check.py` OK
- [ ] `hitl_check.py` OK
- [ ] `status_truth.py --write` + README updated
- [ ] No curriculum/grade/country/product semantics

---

## 7. Example — Adding `metre` via Primary PDF Ingestion (Deterministic, HITL)

1. **Upload PDF:** SI Brochure 9th ed. PDF via webapp or `python3 scripts/pdf_ingest_primary.py --pdf ~/SI-Brochure-9.pdf`
2. **Extract:** Click Extract → deterministic text extraction via poppler
3. **AI Draft:** Click Draft to markdown → AI extracts per AGENT.md: `workflow/candidates/<doc_id>/metre.md` with standard definition exact: "The metre (symbol: m) is base unit of length in SI. Defined as length of path travelled by light in vacuum during 1/299,792,458 s. Exact c=299,792,458 m/s."
4. **HITL:** Webapp shows markdown preview side-by-side, checklist shows standard definition? units? governed_by? You explicitly edit markdown — fix definition to exact user wording, add reference `BIPM SI Brochure 9th ed. §2.3.1, p130`, set writer `human:curator.001`, link `https://www.bipm.org/en/publications/si-brochure` → Save → audit logs candidate_edited by human
5. **Stage:** Click Stage for human review → moves to `workflow/proposals/metre.md`, validation runs (including hitl_check)
6. **Review:** `python3 scripts/review_entity.py accept metre --reviewer human:curator.001` → human_reviewed
7. **Canonicalize:** `python3 scripts/review_entity.py canonicalize metre --reviewer human:curator.001` → `content/physics/measurement-units/metre.md`
8. **Verify:** `python3 scripts/verify_all.py` → must pass hitl_check

Same steps in 2026 or 2030 → same result, with HITL audit trail.

---

**End of Agent Protocol — PDF Primary, HITL Before Canonical**
