# AGENT.md — Physics Entity Addition Protocol (Deterministic, Time-Invariant)

**Status:** Authoritative for all agents (human, llm, process) adding physics entities. Companion to `AGENTS.md`, `GOVERNANCE.md`, `PHYSICS-GOVERNING-LAWS.md`, `PHYSICS-MINIMAL-DESIGN-V2.md`.
**Purpose:** Ensure every entity is added the same way regardless of when, who, or which model — no LLM reasoning drift.
**Enforcement:** `scripts/physics_core_profile_check.py` + `scripts/physics_governing_check.py` + `scripts/validate.py` — all must pass.

> **Core Principle:** Time of addition does not matter. Governing laws do. If two agents add `mass` in 2026 and 2030, they must produce identical `id`, `subdomain`, `governed_by`, and placement, because governing laws are deterministic.

---

## 1. Before Adding Any Entity — Read Governing Laws

**Mandatory reading order (no skipping):**

1. `docs/PHYSICS-GOVERNING-LAWS.md` — what laws exist, what they govern, what goes where
2. `schema/physics-governing-registry.yaml` — machine-readable governing laws, allowed quantities per subdomain
3. `docs/PHYSICS-MINIMAL-DESIGN-V2.md` — minimal schema with dual verification + history rules
4. `docs/DOMAIN-MODEL.md` §8 — physics profile
5. `schema/concept.schema.json` v1.2.0 — required fields

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
  → File path: content/physics/<subdomain>/<slug>.md

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

## 3. Entity Creation Protocol — Step-by-Step (Time-Invariant)

### 3.1 Choose ID (Deterministic)

- Grammar: `stemma:phys.<slug>` — slug lowercase [a-z0-9-], never reused
- Check `schema/id-domain-map.yaml`: prefix `phys` → domain `physics` → directory `physics`
- Check uniqueness: `grep -r "id: stemma:phys.<slug>" content/`
- Filename = slug: `content/physics/<subdomain>/<slug>.md` must match final ID segment

### 3.2 Fill Frontmatter (Mandatory Fields — Dual Verification)

Use template `scripts/templates/physics_entity_template.md`:

```yaml
id: stemma:phys.<slug>
type: quantity | unit | law | equation | concept | model | phenomenon  # from DOMAIN-MODEL
name: "<Human readable, Title Case>"
domain: physics
subdomain: mechanics | electricity-magnetism | thermal-physics | measurement-units  # from governing law
status: draft  # always draft initially, human_reviewed/canonical only after human review
definition: >-
  Curriculum-agnostic, 1-3 sentences, verifiable, no pedagogy.
  Must be definable via governing law.

symbol: "<symbol>"  # e.g., m, F, a — optional but needed for physics
unit: "<unit display>"  # e.g., kilogram (kg) — optional

governed_by:  # MANDATORY — deterministic placement, no LLM
  - stemma:phys.newtons-second-law
  - stemma:phys.conservation-energy

provenance:  # MANDATORY — dual verification
  ai_drafted: false  # true if LLM drafted, false if human authored
  source_kind: textbook  # textbook | academic-or-research | standards-or-specification | institutional | other
  source: >-
    Full citation with page: Halliday Resnick Walker 12th ed. Ch 5, p112: "Mass is..."
  writer: human:curator.001  # who wrote this file — must resolve in agent-registry.yaml
  original_author: "Halliday, Resnick, Walker"  # who originally stated science
  link: "https://www.wiley.com/..."  # URL or DOI — for triple-check
  retrieved_at: "2026-09-21"  # ISO date
  reviewer: null
  reviewed_at: null

source_refs:  # MANDATORY — canonical records, dual verification
  - stemma:src.halliday-resnick-walker-12th
  - stemma:src.nist-si-brochure-9th

historical:  # Optional for draft, MANDATORY for law/model/equation when human_reviewed/canonical
  stated_by: "Isaac Newton"
  year: 1687
  where: "Philosophiæ Naturalis Principia Mathematica"
  timeline:
    - year: 1687
      by: Isaac Newton
      event: First stated

external_ids:
  wd: Q11423
  qudt: quantitykind-Mass
```

**Rules:**
- `source_kind`, `source`, `writer`, `link`, `retrieved_at` — all mandatory for physics-core v2 (profile check fails otherwise)
- `source_refs` array >=1, each must have file in `sources/` with url/doi/isbn
- `governed_by` >=1, each must be in `physics-governing-registry.yaml`
- No `learning_objectives`, `real_world_applications`, `key_experiments`, `common_misconceptions` — forbidden per ADR-0041
- `subdomain` must match subdomain of governing law(s)

### 3.3 Create Canonical Source Record (Dual Verification)

If `source_refs` contains id not yet in `sources/`:

1. Create `sources/src.<slug>.yaml` using template `scripts/templates/physics_source_template.yaml`
2. Must have: id, type, citation, title, authors[], year, publisher, url/doi/isbn (at least one for verifiability), writer, retrieved_at
3. Validate: `python3 scripts/validate.py` checks id format, `physics_core_profile_check.py` checks url/doi/isbn present

### 3.4 Add Historical Timeline (For Laws)

If `type` is `law`, `model`, `equation`, `experiment`:
- Draft: historical optional but encouraged
- human_reviewed/canonical: historical MANDATORY with `stated_by`, `year`, `where`, `timeline[]` with year, event, by
- Timeline shows progression for verification and future change (e.g., Newton 1687 → Euler 1749 → Einstein 1916)

### 3.5 Validate Deterministically (No LLM)

After creating file:

```bash
python3 scripts/validate.py
# Must be OK: X entities valid

python3 scripts/physics_core_profile_check.py
# Must be OK: 0 violations
# Checks: mandatory source fields, source_refs resolve, evidence for connections, historical for law canonical, no forbidden fields, no related_to

python3 scripts/physics_governing_check.py
# Must be OK: 0 violations
# Checks: every entity has governed_by, subdomain matches law, no self-governance, law entities exist

python3 scripts/status_truth.py --write
# Updates README status block — must commit

python3 scripts/verify_all.py
# Full chain — must be green
```

All 4 must pass. If any fails, fix — do not rely on model reasoning to guess.

### 3.6 Connections (Every Claim Has Source)

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
PHYSICS-GOVERNING-LAWS.md (human-readable guiding point)
    ↓
schema/physics-governing-registry.yaml (machine-readable, deterministic)
    ↓
content/physics/<subdomain>/<slug>.md (entity with governed_by field)
    ↓
connections/*.yaml (law --mathematically_requires--> quantity)
    ↓
scripts/physics_governing_check.py (verification tool, no LLM)
```

**No LLM reasoning in placement:** Subdomain, governed_by, dimensions are decided by registry lookup, not model inference. Same input → same output any time.

**Laws embedded in 3 places (triple redundancy):**
1. `PHYSICS-GOVERNING-LAWS.md` table
2. `physics-governing-registry.yaml` machine-readable
3. As entities themselves in `content/physics/` with historical timeline

---

## 5. Time-Invariant Guarantee

- **ID stability:** `stemma:phys.<slug>` never reused, never reassigned — guard `check_id_immutability.py`
- **Deterministic placement:** `governed_by` → `subdomain` mapping is in registry, not model
- **Source audit trail:** `provenance.writer`, `link`, `retrieved_at`, `source_refs` + canonical `sources/` record + external URL = triple-checkable now or in 10 years
- **History progression:** `historical.timeline` shows previous and progression, so future change can compare old vs new
- **Validation is same:** `validate.py` + `physics_core_profile_check.py` + `physics_governing_check.py` are deterministic, no wall clock, content-hash stamped

If you add entity in 2026 or 2030 following this protocol, you will produce identical file (except `retrieved_at` date, which is allowed to differ).

---

## 6. Checklist Before Commit (Definition of Done for Physics Entity v2)

- [ ] ID follows `stemma:phys.<slug>` grammar, unique, filename matches slug
- [ ] `type` is one of 9, `domain: physics`, `subdomain` from governing law
- [ ] `definition` curriculum-agnostic, verifiable, no pedagogy
- [ ] `governed_by` >=1, each in `physics-governing-registry.yaml`, subdomain matches
- [ ] `provenance.source_kind`, `source`, `writer`, `original_author`, `link`, `retrieved_at` all present
- [ ] `source_refs` >=1, each resolves to file in `sources/` with url/doi/isbn
- [ ] If `type` law/model/equation and status human_reviewed/canonical: `historical` with `stated_by`, `year`, `timeline`
- [ ] No forbidden fields: `learning_objectives`, `real_world_applications`, `key_experiments`, `common_misconceptions`
- [ ] At least 1 connection with mandatory evidence (source_ref, locator, description)
- [ ] `validate.py` OK
- [ ] `physics_core_profile_check.py` OK
- [ ] `physics_governing_check.py` OK
- [ ] `status_truth.py --write` + README updated
- [ ] No curriculum/grade/country/product semantics

---

## 7. Example — Adding `velocity` (Deterministic)

1. **Governing law:** Newton's Second Law requires acceleration which requires velocity → `newtons-second-law` → subdomain `mechanics` → dimensions L T⁻¹
2. **Create file:** `content/physics/mechanics/velocity.md` with id `stemma:phys.velocity`
3. **Fill frontmatter** using template, with `governed_by: [newtons-second-law, si-definitions]`, `source_refs: [halliday-resnick]`, provenance with writer/link/retrieved_at
4. **Create connection:** `newtons-second-law mathematically_requires velocity` with evidence HRW Ch4
5. **Validate:** 4 scripts must pass
6. **Commit:** atomic commit with message `feat(physics): add velocity quantity governed by newtons-second-law`

Same steps in 2026 or 2030 → same result.

---

**End of Agent Protocol**
