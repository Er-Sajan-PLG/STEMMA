# STEMMA Canonical Admission Policy

**Version:** 1.0  
**Status:** Implemented  
**Related:** `docs/KNOWLEDGE-ACQUISITION.md`, `docs/PROVENANCE.md`, `docs/EVIDENCE-MODEL.md`, `scripts/curation_pipeline.py`, `scripts/review.py`

---

## Overview

This document defines the rules and gates for admitting knowledge into the canonical STEMMA system. Canonical admission is **always a human action** — AI output alone never establishes canonical truth.

---

## Admission Pipeline

```
Candidate Knowledge (proposed)
    ↓
Deterministic Gates (ALL must pass)
    ↓
Semantic Review Gates
    ↓
Human Governance Gate (canonicalize/reject)
    ↓
Canonical STEMMA
```

---

## Deterministic Gates (All Must Pass)

These gates run natively in `scripts/curation_pipeline.py` and `scripts/validate.py`:

| Gate | Validates | Failure Action |
|------|-----------|----------------|
| `schema` | JSON Schema conformance | Reject — fix schema violations |
| `identity` | ID format (`lhs:<domain>.<slug>`), uniqueness, slug match | Reject — fix ID |
| `relations` | Whitelist types, no dangling targets | Reject — fix relationships |
| `provenance` | Required fields, reviewer for canonical | Reject — complete provenance |
| `resolution` | Source/target entities exist | Reject — fix references |
| `conditions` | Context present for relation types | Reject — add context |

### Entity-Specific Gates
| Gate | Validates |
|------|-----------|
| `identity` | ID format, uniqueness, filename=slug |
| `schema` | Required fields, enums, types |
| `provenance` | `ai_drafted` boolean, `source_kind` vocabulary |
| `relations` | Whitelist, dangling target check |

### Connection-Specific Gates
| Gate | Validates |
|------|-----------|
| `resolution` | Source/target resolve to entities |
| `relations` | Relation in `relation-registry.yaml` |
| `conditions` | `context` object present |
| `provenance` | `asserted_by`, `generated_by`, `method` required |

### Source-Specific Gates
| Gate | Validates |
|------|-----------|
| `identity` | ID format `lhs:src.<slug>` |

---

## Semantic Review Gates (Judgment)

These gates require semantic judgment — delegated to LLM/human seam:

| Gate | Question | Who Decides |
|------|----------|-------------|
| `intent` | Does the candidate claim match the extracted evidence? | LLM + Human |
| `fidelity` | Is the extraction accurate? No hallucination? | LLM + Human |
| `consistency` | Does this contradict existing canonical knowledge? | LLM + Human |
| `epistemic_status` | Is confidence/uncertainty appropriately represented? | Domain Expert |

---

## Human Governance Gate (Mandatory)

**Canonicalization is ALWAYS a human action.**

### Reviewer Requirements
- Must be a named human (`human:reviewer.<name>`)
- Must provide reason for canonicalization
- Review recorded in `review_history` with timestamp

### Review Actions (via `scripts/review.py`)
| Action | New Status | Use Case |
|--------|------------|----------|
| `accept` / `reviewed` | `reviewed` | Gates pass, needs final human check |
| `canonicalize` | `canonical` | Ready for canonical admission |
| `reject` | `rejected` | Fails gates, contradiction, or insufficient evidence |

### Canonicalize Requirements
1. All deterministic gates PASS
2. Semantic review gates PASS
3. Evidence exists (per family rules)
4. Named human reviewer
4. Reason provided
5. `review_history` entry created

---

## Stronger Gates for High-Impact Claims

The following require additional scrutiny:

| Claim Type | Additional Requirements |
|------------|------------------------|
| Controversial claims | Multiple independent sources, explicit uncertainty |
| High-impact claims | Domain expert review, cross-discipline verification |
| Cross-domain relationships | Experts from both domains |
| New terminology | Terminology review, alias registration |
| Retracted/superseded source | Explicit handling of source status |

---

## Admission Decision Matrix

| Deterministic Gates | Semantic Gates | Human Review | Decision |
|---------------------|----------------|--------------|----------|
| All PASS | All PASS | Canonicalize | **ADMIT** (canonical) |
| All PASS | All PASS | Reviewed | **ADMIT** (reviewed) |
| Some FAIL | — | — | **REJECT** |
| All PASS | Some FAIL | — | **HOLD** (needs human/LLM attention) |
| All PASS | All PASS | Reject | **REJECT** |

---

## AI Candidate Admission

AI-generated candidates follow the same pipeline with additional safeguards:

### AI Candidate Requirements
1. `provenance.ai_drafted: true` on entity
2. `provenance.method.type: "llm_inference"` on connection
3. `provenance.asserted_by.type: "llm"` on connection
4. Evidence must be attached (AI cannot fabricate evidence)
5. **Human review mandatory** — AI candidates never auto-canonicalize

### AI Candidate Flow
```
AI Draft → Evidence Attachment → Schema Validation → Semantic Validation → Provenance Verification → Human Approval → Canonical
```

---

## Evidence Sufficiency Rules

### Minimum Evidence by Relationship Family
| Family | Minimum Evidence for Canonical |
|--------|-------------------------------|
| `derivation` | Mathematical derivation or textbook |
| `dependency` | Textbook or authoritative source |
| `causal` | Empirical measurement or experiment |
| `explanatory` | Textbook, standard, or review |
| `measurement` | Dataset or empirical measurement |
| `structural` | Definition or authoritative source |
| `model` | Standard, textbook, or paper |
| `conflict` | Contradicting sources explicitly documented |
| `analogy` | Expert assessment or textbook |
| `cross_domain` | Sources from both domains |
| `associative` | Textbook or review |

**Rule:** No canonical connection without at least one evidence item (unless family explicitly allows theoretical derivation).

---

## Contradiction Handling

### When Contradictory Evidence Exists
1. **Document both sides** — add evidence with `stance: contradicts`
2. **Qualify the canonical relationship** — add `limited_by` or `qualifies`
3. **Set appropriate confidence** — lower confidence for contested claims
4. **Record in review history** — why this stance was chosen

### Example
```yaml
connection:
  relation: causes
  evidence:
    - type: experiment
      stance: supports
      source_ref: lhs:src.paper-a
    - type: academic-paper
      stance: contradicts
      source_ref: lhs:src.paper-b
      description: "Found no causal link under controlled conditions"
    - type: review
      stance: qualifies
      source_ref: lhs:src.review-c
      description: "Causal only under specific conditions"
```

---

## Retraction / Supersession Admission

### Source Retracted
1. Source marked `retracted`
2. All dependent connections flagged
3. Human review required for each dependent canonical object
4. Possible actions:
   - Update with alternative evidence
   - Deprecate canonical object
   - Qualify with `limited_by`

### Source Superseded
1. New source registered with `supersedes` link
2. Evidence migrated where content unchanged
3. Dependent canonical objects flagged for review
4. Human confirms or updates

---

## Admission Audit Trail

Every admission creates a ledger entry:

```yaml
ledger_entry:
  id: lhs:ledger.<uuid>
  type: canonical_admitted
  timestamp: "2026-09-06T12:00:00Z"
  actor: "human:reviewer.physics-001"
  canonical_ref: "lhs:phys.newtons-second-law"
  source_ref: "lhs:src.halliday-resnick"
  evidence_refs: ["lhs:evidence.001"]
  prior_state: "reviewed"
  new_state: "canonical"
  details:
    gates_passed: ["schema", "identity", "relations", "provenance", "resolution", "conditions", "intent", "fidelity"]
    reason: "All gates pass; textbook evidence from Halliday & Resnick 12th ed."
```

---

## Rejection / Hold Policies

### Rejection Reasons
| Reason | Description |
|--------|-------------|
| `schema_failure` | JSON Schema validation failed |
| `identity_conflict` | Duplicate or invalid ID |
| `dangling_reference` | Target entity doesn't exist |
| `insufficient_evidence` | No evidence for canonical claim |
| `contradiction` | Contradicts established canonical knowledge |
| `provenance_incomplete` | Missing required provenance fields |
| `retracted_source` | Sole evidence from retracted source |
| `copyright_violation` | Evidence exceeds fair use |

### Hold Reasons
| Reason | Description |
|--------|-------------|
| `needs_expert_review` | Domain expert required |
| `needs_cross_domain_review` | Multiple domain experts needed |
| `awaiting_source_update` | Source being revised |
| `terminology_review` | New/conflicting terminology |
| `contradiction_unresolved` | Conflicting evidence not qualified |

---

## Admission in Exports

Canonical objects in exports carry admission metadata implicitly through:
- `status: canonical` (vs `reviewed`, `draft`, `proposed`)
- `provenance.reviewer` and `reviewed_at`
- `provenance.review_history` showing admission path
- Evidence array showing supporting evidence

---

## Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.0 | 2026-09-06 | Initial canonical admission policy |