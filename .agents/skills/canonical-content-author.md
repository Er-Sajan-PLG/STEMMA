# Canonical Content Author Skill

**Purpose**: Teach an agent how to add or modify STEMMA canonical knowledge correctly.

**When to Use**: When creating new entities, updating existing ones, adding relationships, or improving content quality.

**Mental Model**: You are contributing to a shared knowledge foundation. Every change must be accurate, well-sourced, curriculum-agnostic, and validated.

---

## Required Inputs
- Domain knowledge or access to authoritative sources
- STEMMA repository with write access
- Understanding of entity model and relationships

---

## Workflow: Adding a New Entity

### 1. Check for Existing Entity
```bash
# Search by name/concept
grep -r "Name of Concept" content/
# Or check exports
jq '.entities[] | select(.name == "Name")' exports/knowledge.json
```

### 2. Choose Domain & Create File
```bash
# Domain directories:
# content/math/, content/physics/, content/chemistry/, content/biology/
# content/earth-space/, content/engineering/, content/scientific-practice/

# Filename = ID slug
# Example: Force → content/physics/force.md
```

### 3. Write Entity Frontmatter (use template)
```markdown
---
id: lhs:phys.force
type: concept
name: Force
domain: physics
status: draft
definition: >-
  An influence that can change the motion of a body — that is, accelerate it.
  In classical mechanics the net force on a body equals the rate of change of
  its momentum. Force is a vector quantity.
symbol: F
unit: newton (N)
equation: F = dp/dt ; F = m·a (constant mass)
examples:
- Pushing a shopping trolley makes it accelerate.
- A magnet pulls a pin toward it — a contact-free force.
common_misconceptions:
- A constant net force produces constant speed (it produces constant acceleration).
- Force is a property of an object (force acts between objects).
learning_objectives:
- Define force as a vector quantity that causes acceleration.
- Distinguish between contact and non-contact forces.
real_world_applications:
- Vehicle acceleration and braking.
- Engineering structures.
provenance:
  ai_drafted: true
  source_kind: standards-or-specification
  source: "IUPAP / Physics Curriculum Framework"
relationships:
- type: mathematically_requires
  target: lhs:phys.mass
- type: mathematically_requires
  target: lhs:phys.acceleration
- type: appears_in_law
  target: lhs:phys.newtons-second-law
---

## Notes
Optional prose body for additional context.
```

### 4. Run Validation
```bash
python3 scripts/validate.py
# Must exit 0
```

### 5. Iterate Until Clean
- Fix all ERRORs
- Address WARNINGs where possible
- INFO items are optional improvements

### 6. Human Review (for canonical status)
- Change `status: draft` → `status: canonical`
- Add `provenance.reviewer` and `provenance.reviewed_at`
- Re-run validation

---

## Workflow: Updating Existing Entity

### 1. Locate Entity
```bash
find content/ -name "*.md" -exec grep -l "lhs:phys.force" {} \;
```

### 2. Apply Identity Rules
| Change | Action |
|--------|--------|
| Fix typo in definition | Edit in place (if draft/machine_validated) |
| Rename concept | Change `name`, keep `id` |
| Split concept | Create 2 new entities, deprecate old (`status: deprecated`, `deprecated_by`) |
| Merge concepts | Keep one ID, deprecate other (`deprecated_by` = survivor) |
| Correct misunderstanding | Deprecate old, create new with `aliases` |

### 3. Never Edit Canonical In-Place
- `canonical` status entities are frozen
- Create new entity with new ID
- Deprecate old entity

### 4. Run Validation
```bash
python3 scripts/validate.py
```

---

## Workflow: Adding Relationships

### 1. Inline (Entity Frontmatter)
Add to `relationships:` array in entity file.

### 2. First-Class (Connection File)
Create `connections/lhs:conn.NNNNNN.yaml`:
```yaml
id: lhs:conn.000655
type: connection
source: lhs:phys.force
relation: mathematically_requires
target: lhs:phys.mass
assertion:
  status: active
  type: proposed
  review:
    status: unreviewed
  confidence: null
  confidence_basis: null
  polarity: positive
context:
  domain: physics
  subdomain: mechanics
  regime:
  - classical
  scale: macroscopic
  assumptions: []
  qualifiers: []
evidence: []
provenance:
  asserted_by:
    type: human
    id: human:reviewer.physics-001
  generated_by:
    type: human
    id: human:curator.001
  method:
    type: manual
```

### 3. Validate
```bash
python3 scripts/validate.py
python3 scripts/export_subsets.py
```

---

## Content Quality Standards

### Definition Quality
- One clear paragraph preferred
- Avoid: "In grade X, students learn..." or "This lesson covers..."
- Use: "Force is..." or "The law states..."
- Be precise: "rate of change of momentum" not "push or pull"

### Relationship Quality
- Use specific types over `related_to`
- `logically_requires` = conceptual prerequisite
- `mathematically_requires` = formal derivation dependency
- `part_of` = structural component
- `derived_from` = logical consequence

### Provenance Quality
- `ai_drafted: true` for AI-assisted content
- `source_kind` from controlled vocabulary
- `source` = specific citation (textbook edition, paper DOI, standard)
- `reviewer` = human name/identifier for reviewed/canonical

### Metadata Quality
- `learning_objectives`: What the concept enables understanding of (not pedagogy)
- `real_world_applications`: Actual phenomena/technologies (not "textbook problem")
- `common_misconceptions`: Documented false beliefs (not teaching tips)
- `key_experiments`: Classic experiments establishing the concept

---

## Anti-Patterns

| Don't | Do |
|-------|----|
| Add `grade: 10` field | Curriculum maps are consumer-owned |
| Create `Force-GCSE` entity | One canonical entity, curricula map to it |
| Write "Students should be able to..." | Write "Understand that force causes acceleration" |
| Use `teaches` relationship | Use `logically_requires` |
| Put lesson order in entity | Consumer adapter handles sequence |
| Copy-paste without provenance | Always cite source |

---

## Validation Checklist Before Committing
- [ ] `python3 scripts/validate.py` exits 0
- [ ] No new ERRORs
- [ ] WARNINGs reviewed and justified
- [ ] ID format correct
- [ ] Filename matches ID
- [ ] Provenance complete
- [ ] Relationships resolve
- [ ] No curriculum/grade/product references
- [ ] Historical attribution for laws/discoveries

---

## Escalation Conditions
- Unsure about entity type → Check specification, prefer `concept`
- Conflicting sources → Document in `historical.note`, create separate entities if needed
- Need new relationship type → Check relation-registry.yaml, propose ADR if truly new
- Large restructuring → Create ADR, discuss with human