# STEMMA Architecture Reviewer Skill

**Purpose**: Teach an agent how to review future architectural changes against STEMMA's principles.

**When to Use**: When evaluating proposed changes to schema, validation, export, relationships, or any foundational aspect of STEMMA.

**Mental Model**: STEMMA is a canonical knowledge foundation. Every architectural decision must preserve: independence from consumers, semantic integrity, deterministic tooling, and governed extensibility.

---

## Core Principles (Invariants)

These are NEVER overridden:

1. **Knowledge ≠ Curriculum ≠ Pedagogy ≠ Product**
2. **Canonical source of truth = `content/`, `connections/`, `sources/`**
3. **Derived artifacts are regenerable, never authoritative**
4. **Stable IDs are forever (`lhs:` namespace)**
5. **AI output requires human review before canonical**
6. **Products are consumers, never dependencies**
7. **Dependency direction: Consumer → Foundation**
8. **Simple now, extensible later**

---

## Review Checklist for Any Architectural Change

### Schema Changes
| Question | Pass Criteria |
|----------|---------------|
| Does it add curriculum/grade/product fields? | NO - these belong in consumers |
| Does it change ID format or stability rules? | Only via ADR with human approval |
| Does it add entity type? | Must be justified by knowledge modeling need |
| Does it remove entity type? | Only if deprecated with migration path |
| Does it change required fields? | Only additive, with default for existing |
| Is it backward compatible? | Existing content must still validate |

### Relationship Changes
| Question | Pass Criteria |
|----------|---------------|
| New relationship type? | Must have clear semantics, inverse, domain/range, transitivity |
| Change relationship semantics? | Only via ADR, document migration |
| Remove relationship type? | Must deprecate first, provide alternative |
| Change domain/range? | Must not invalidate existing valid connections |

### Validation Changes
| Question | Pass Criteria |
|----------|---------------|
| New validation rule? | Must catch real errors, not style preferences |
| Change severity? | ERROR→WARNING OK; WARNING→ERROR needs justification |
| Remove validation? | Only if proven false positive with evidence |
| Performance impact? | Must not exceed 10s for full validation |

### Export Changes
| Question | Pass Criteria |
|----------|---------------|
| Change export shape? | Bump `export_version`, ADR required |
| Add required field? | Must be in all existing entities |
| Remove field from export? | Only if deprecated with notice period |
| New subset export? | Document information loss explicitly |

### Versioning Changes
| Question | Pass Criteria |
|----------|---------------|
| Change versioning scheme? | ADR required, document consumer impact |
| Bump major version? | Breaking change documented, migration guide |
| Collapse version tracks? | NEVER - three tracks are distinct by design |

---

## ADR Requirements

The following changes REQUIRE a documented ADR in `docs/decisions/`:
- Entity type changes
- Relationship semantics changes
- ID rules changes
- Canonical representation changes
- Lifecycle semantics changes
- Export contract changes
- Schema version major bumps
- License changes
- New consumer integration patterns

**ADR Template**:
```markdown
# DECISION NNNN — Title
- Date: YYYY-MM-DD
- Status: proposed|decided|rejected
- Context: Why this change?
- Decision: What exactly?
- Alternatives: What else considered?
- Consequences: Impact on consumers, validators, content
```

---

## Review Process

### 1. Classify the Change
```
NOW      — Required for current milestone
SEAM     — Small interface protecting known future change
LATER    — Architecture-described, not required now
OUT      — Not relevant, do not implement
```

### 2. Check Against Invariants
- Does this couple STEMMA to a specific product?
- Does this add curriculum/grade to canonical content?
- Does this make derived artifacts authoritative?
- Does this break stable IDs?
- Does this make AI output auto-canonical?

### 3. Verify Tooling Impact
- Validator still passes on all existing content
- Export still regenerates deterministically
- Subset exports still work
- Consumer adapter still works (or has migration path)
- Tests still pass

### 4. Document Decision
- If NOW or SEAM: Implement with tests
- If LATER: Document in ADR as future work
- If OUT: Record why not done

---

## Red Flags (Changes That Violate Principles)

| Red Flag | Principle Violated |
|----------|-------------------|
| Adding `grade` field to entity schema | Knowledge ≠ Curriculum |
| Making `exports/knowledge.json` the source of truth | Derived ≠ Authoritative |
| Hardcoding LearningHub paths in STEMMA scripts | Products are consumers |
| Auto-promoting AI drafts to canonical | AI requires review |
| Reusing deprecated ID for new concept | Stable IDs forever |
| Adding `lesson_order` to relationships | Knowledge order ≠ Curriculum order |
| Building REST API in STEMMA repo | Simple now, extensible later |
| Creating `STEMMA → LearningHub` dependency | Dependency: Consumer → Foundation |

---

## Green Flags (Changes That Align With Principles)

| Green Flag | Principle Supported |
|------------|-------------------|
| New entity type for `observation` | Richer knowledge modeling |
| Extension registry for new metadata | Governed extensibility |
| Subset export for `ai-rag` | Consumer needs without coupling |
| Cycle detection for structural relations | Semantic integrity |
| Inverse relationship validation | Relationship consistency |
| Historical attribution separate from provenance | Provenance model clarity |

---

## Escalation Conditions
- Change violates invariant → STOP, requires human decision
- Two valid architectural approaches → Document both, human chooses
- Consumer requests coupling → Redirect to adapter pattern
- Unclear if schema change is breaking → Err on side of ADR
- Performance vs correctness tradeoff → Correctness wins (document)