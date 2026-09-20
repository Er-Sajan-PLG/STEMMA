# Canonical Knowledge Designer Skill

**Purpose**: Teach an agent how to model canonical STEM entities, distinguish canonical vs derived information, design relationships, reason about semantic constraints, avoid product contamination, and evolve the schema safely.

**When to Use**: When adding new canonical STEM entities, modifying entity types, designing new relationship types, or making schema changes to STEMMA.

**Mental Model**: STEMMA is a curriculum-agnostic, product-independent knowledge foundation. Every entity and relationship must pass the "North Star test": *Is this intrinsic to the STEM knowledge itself, or is it a way of organizing/teaching/consuming that knowledge?*

---

## Required Inputs
- Domain expertise in the STEM area being modeled
- Understanding of STEMMA's entity types and relationship vocabulary
- Access to authoritative sources for provenance

---

## Workflow

### 1. Determine Entity Type
Choose from the canonical entity types:
- **Core** (always available): `concept`, `quantity`, `unit`, `law`, `equation`, `misconception`
- **Extended** (for richer modeling): `phenomenon`, `model`, `experiment`, `regime`, `observation`, `measurement`, `classification`, `definition`, `claim`

**Rules**:
- One entity = one type (type changes require new entity with new ID)
- If uncertain between types, prefer `concept` for general ideas, `quantity` for measurable properties, `law` for principles

### 2. Assign Stable ID
Format: `lhs:<domain>.<slug>`
- `<domain>`: one lowercase ASCII word (`math`, `physics`, `chemistry`, `biology`, `earth`, `engineering`, `practice`)
- `<slug>`: lowercase `[a-z0-9-]`, matches filename
- **Never reuse IDs** - even for deprecated entities
- Renaming an entity does NOT change its ID

### 3. Write Canonical Definition
- Curriculum-agnostic (no grade, curriculum, country, product references)
- Clear, precise, scientifically accurate
- One paragraph preferred, can have multiple sentences
- Avoid pedagogical language ("students learn", "we teach", "lesson covers")

### 4. Add Knowledge-Layer Metadata (Optional but Recommended)
| Field | Purpose | Example |
|-------|---------|---------|
| `symbol` | Symbol for quantity/law | `F`, `m`, `a` |
| `unit` | SI unit for quantities | `newton (N)` |
| `equation` | Canonical mathematical form | `F = m·a` |
| `common_misconceptions` | False beliefs learners hold | `"Heavier objects fall faster"` |
| `learning_objectives` | What learner should understand | `["Define force...", "Apply F=ma..."]` |
| `real_world_applications` | Technologies/phenomena explained | `["Vehicle acceleration", "Spacecraft propulsion"]` |
| `key_experiments` | Classic demonstrations | `["Dynamics cart + force sensor"]` |

**These are knowledge-layer, NOT pedagogy.** They describe the concept itself, not how to teach it.

### 5. Design Relationships
Use **core relationship types** (inline `relationships[]`):
| Type | When to Use |
|------|-------------|
| `logically_requires` | Target is logically necessary for understanding source |
| `mathematically_requires` | Target is mathematically necessary (derivation, definition) |
| `part_of` | Source is a component of target |
| `derived_from` | Source follows from target |
| `special_case_of` | Source is narrower than target |
| `generalizes` | Source is broader than target |
| `equivalent_to` | Same thing, different presentation |
| `applies_to` | **Source must be `law`**; target is concept/quantity/equation |
| `appears_in_law` | **Target must be `law`**; source appears in that law |
| `related_to` | Meaningful connection, no necessity (use only when no specific type fits) |

**Rules**:
- Never use `related_to` when a specific relationship is known
- `applies_to` source MUST be `law` type
- `appears_in_law` target MUST be `law` type
- Transitive relationships (`part_of`, `derived_from`, `special_case_of`, `generalizes`, `equivalent_to`, `logically_requires`, `mathematically_requires`) should not create cycles of length > 2

### 6. Provide Provenance
```yaml
provenance:
  ai_drafted: true|false
  source_kind: human-authored|textbook|academic-or-research|institutional|standards-or-specification|ai-assisted-draft|other
  source: "Citation or reference"
  reviewer: "Name"  # required for human_reviewed/canonical
  reviewed_at: "ISO date"  # required for human_reviewed/canonical
```

### 7. Add Historical Attribution (for laws, major discoveries)
```yaml
historical:
  stated_by: "Isaac Newton"
  year: 1687
  where: "Philosophiæ Naturalis Principia Mathematica"
  context: "Classical mechanics"
  note: "F=ma is constant-mass special case; general form is F=dp/dt"
  timeline:
    - year: 1687
      by: "Isaac Newton"
      event: "Second law stated in Principia"
```

### 8. Set Lifecycle Status
- `draft` → `machine_validated` → `human_reviewed` → `canonical` → (deprecated/superseded)
- **Forward-only transitions** - never edit canonical in place, deprecate and replace
- AI-drafted content NEVER auto-becomes canonical

### 9. Run Validation
```bash
python3 scripts/validate.py
```
Must exit 0. Check warnings (INFO/WARNING) for data quality improvements.

---

## Anti-Patterns to Avoid

| Anti-Pattern | Why It's Wrong | Correct Approach |
|--------------|----------------|------------------|
| Adding `grade: 10` to entity | Curriculum in canonical | Curriculum mapping is consumer-owned |
| Creating `Force-Grade9` variant | Duplication | One `lhs:phys.force`, curricula map to it |
| Using `teaches` as relationship | Pedagogical | Use `logically_requires`, `mathematically_requires` |
| Putting lesson sequence in entity | Product coupling | Consumer adapter handles sequencing |
| Changing ID on rename | Breaks consumers | Keep ID, change `name` field |
| Adding product-specific fields | Couples foundation to product | Use extensions (registered) or consumer adapter |

---

## Validation Checklist
- [ ] ID format matches `lhs:<domain>.<slug>`
- [ ] Filename matches ID slug
- [ ] All required fields present
- [ ] Type is valid enum value
- [ ] Status is valid enum value
- [ ] Definition is curriculum-agnostic
- [ ] Relationship types are from core whitelist
- [ ] `applies_to` source is `law`
- [ ] `appears_in_law` target is `law`
- [ ] No dangling relationship targets
- [ ] Provenance has `ai_drafted` boolean
- [ ] `human_reviewed`/`canonical` have `reviewer`
- [ ] Historical has `stated_by` + `year` (if present)
- [ ] Extensions keys are registered
- [ ] Validation passes (exit 0)

---

## Escalation Conditions
- Unclear which entity type fits → Document reasoning, prefer `concept`
- New relationship type needed → Check relation-registry.yaml first; if truly new, propose ADR
- Circular dependency detected → Analyze if structural (error) or dependency (may be legitimate)
- Conflicts with existing entity → Check for duplicate, deprecate/replace per identity rules
- Need curriculum-specific info → STOP. This belongs in consumer, not STEMMA.