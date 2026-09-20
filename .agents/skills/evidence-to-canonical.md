# Evidence-to-Canonical Skill

**Purpose:** Teaches an agent how to convert extracted evidence into canonical knowledge candidates.

**When to Use:** When processing ingestion output or human proposals into the curation pipeline.

**Mental Model:** Evidence → Claims → Entities/Relationships → Candidates → Validation → Review → Canonical

---

## Required Inputs
- Extracted evidence (with locators, source_ref)
- Domain context
- Existing canonical entities (for resolution)

---

## Workflow

### 1. Claim Extraction
From each evidence item, identify:
- **Core claim**: What factual statement is made?
- **Entities involved**: What concepts/quantities/laws are mentioned?
- **Relationships**: How do entities relate?
- **Conditions**: Under what assumptions/regimes?

### 2. Entity Identification
For each concept mentioned:
1. **Search existing canonical entities** by name, symbol, aliases
2. **If found**: Use existing `lhs:` ID
3. **If not found**: Create candidate with placeholder ID `lhs:<domain>.<proposed-slug>`
4. **Check for duplicates**: Use `scripts/entity_resolution.py`

### 3. Relationship Identification
For each relationship between entities:
1. **Map to relation vocabulary** from `schema/relation-registry.yaml`
2. **Select most specific relation** (avoid `related_to` when specific exists)
3. **Determine direction**: source → relation → target
4. **Add context**: domain, subdomain, regime, scale, assumptions

### 4. Candidate Construction

#### Entity Candidate
```yaml
kind: entity
intent: "Define Force as vector quantity causing acceleration"
data:
  id: lhs:phys.force
  type: concept
  name: Force
  domain: physics
  status: draft
  definition: "An influence that can change the motion of a body..."
  symbol: F
  unit: newton (N)
  equation: F = dp/dt ; F = m·a (constant mass)
  provenance:
    ai_drafted: true
    source_kind: textbook
    source: lhs:src.halliday-resnick
  relationships:
    - type: mathematically_requires
      target: lhs:phys.mass
    - type: mathematically_requires
      target: lhs:phys.acceleration
    - type: appears_in_law
      target: lhs:phys.newtons-second-law
```

#### Connection Candidate
```yaml
kind: connection
intent: "Newton's second law applies to force"
data:
  id: lhs:conn.000655
  type: connection
  source: lhs:phys.newtons-second-law
  relation: applies_to
  target: lhs:phys.force
  assertion:
    status: active
    type: proposed
    review: {status: unreviewed}
    polarity: positive
  context:
    domain: physics
    subdomain: mechanics
    regime: [classical]
    scale: macroscopic
  evidence:
    - type: textbook
      stance: supports
      source_ref: lhs:src.halliday-resnick
      locator: {page: "123", equation: "Eq. 4.2"}
      description: "Textbook statement of F=ma"
  provenance:
    asserted_by: {type: human, id: human:curator.001}
    generated_by: {type: human, id: human:curator.001}
    method: {type: manual}
```

### 5. Evidence Attachment
Every candidate MUST have traceable evidence:
```yaml
evidence:
  - type: textbook
    stance: supports
    source_ref: lhs:src.halliday-resnick
    locator:
      page: "123"
      section: "4.2"
      equation: "Eq. 4.2"
    description: "Textbook statement of Newton's second law as F=ma"
    extraction_method: pdftotext
    extraction_confidence: 0.98
```

### 6. Normalization
- **Terminology**: Use canonical names (check existing entities)
- **Symbols**: Standardize (SI symbols where applicable)
- **Units**: Use SI units in `unit` field
- **Equations**: Canonical form using defined symbols
- **Identifiers**: Resolve all `lhs:` references

### 7. Cross-Source Reconciliation
When multiple sources mention same claim:
1. **Aggregate evidence** from all sources
2. **Note contradictions** with `stance: contradicts`
3. **Qualify** canonical relationship if needed
4. **Set appropriate confidence** reflecting evidence balance

---

## Validation Before Submission
Run through deterministic gates:
```bash
python3 scripts/validate.py  # Must pass all gates
```

### Common Gate Failures
| Gate | Common Fix |
|------|------------|
| `identity` | Fix ID format `lhs:<domain>.<slug>` |
| `schema` | Add missing required fields |
| `relations` | Use whitelisted relation type |
| `provenance` | Add required provenance fields |
| `resolution` | Ensure all targets exist |

---

## Anti-Patterns
| Don't | Do |
|-------|----|
| Create entities without evidence | Every claim needs evidence |
| Use `related_to` as default | Use specific relation from registry |
| Skip provenance | Always include source_ref |
| Invent entities | Search existing first |
| Guess relationships | Map to relation registry |

---

## Escalation Conditions
- Unclear which relation type → Check relation-registry.yaml, flag for review
- Contradictory evidence from multiple sources → Document all, qualify canonical
- No existing entity for core concept → Create candidate, flag for domain expert
- Ambiguous terminology → Add to terminology review queue