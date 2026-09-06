# Canonical Evidence Reviewer Skill

**Purpose:** Teaches an agent how to review evidence and candidates for canonical admission.

**When to Use:** When performing semantic review in the curation pipeline or human governance gate.

**Mental Model:** Review is the quality gate between candidate and canonical. Every canonical object must have an explainable evidence path.

---

## Required Inputs
- Candidate canonical object
- Supporting evidence (with locators)
- Source metadata
- Existing canonical context

---

## Review Checklist

### 1. Evidence Sufficiency
- [ ] At least one evidence item per canonical claim
- [ ] Evidence type appropriate for claim (textbook for definitions, experiment for causal)
- [ ] Locators precise enough to verify (page, equation, figure)
- [ ] Extraction confidence documented

### 2. Evidence Quality
- [ ] Source is authoritative for domain
- [ ] Source license permits extraction level used
- [ ] No evidence from retracted sources
- [ ] Contradictory evidence documented and qualified

### 3. Candidate Fidelity
- [ ] Definition matches evidence (no hallucination)
- [ ] Symbol/unit/equation consistent with evidence
- [ ] Relationships map to specific relation vocabulary
- [ ] Context (regime, scale, assumptions) documented

### 4. Provenance Completeness
- [ ] `ai_drafted` correctly set
- [ ] `source_kind` from controlled vocabulary
- [ ] Human reviewer identified for `reviewed`/`canonical`
- [ ] Connection provenance: `asserted_by`, `generated_by`, `method`

### 5. Consistency with Canonical
- [ ] No contradiction with existing canonical entities
- [ ] No contradiction with existing canonical connections
- [ ] New terminology checked against existing aliases
- [ ] Cross-domain relationships verified with domain experts

### 6. Epistemic Status
- [ ] Confidence appropriate for evidence strength
- [ ] Uncertainty documented where evidence is limited
- [ ] Controversial claims explicitly qualified
- [ ] Historical theories marked with `historical` field

---

## Review Actions

| Action | When | Result |
|--------|------|--------|
| `canonicalize` | All gates pass, evidence sufficient | Status → `canonical` |
| `accept` / `reviewed` | Gates pass, needs final check | Status → `reviewed` |
| `hold` | Minor issues fixable | Status → `proposed` (with findings) |
| `reject` | Fundamental issues, contradiction | Status → `rejected` |

### Canonicalization Requirements
1. All deterministic gates PASS
2. Semantic review gates PASS
3. Evidence exists (per family rules)
4. Named human reviewer (`human:reviewer.<name>`)
5. Reason provided
6. `review_history` entry created

---

## Contradiction Handling
When contradictory evidence exists:
1. **Document both sides** — add evidence with `stance: contradicts`
2. **Qualify canonical relationship** — add `limited_by` or `qualifies`
3. **Set appropriate confidence** — lower for contested claims
4. **Record decision rationale** in review history

---

## High-Impact Claims (Stronger Gates)
| Claim Type | Additional Requirements |
|------------|------------------------|
| Controversial | Multiple independent sources |
| High-impact | Domain expert review |
| Cross-domain | Experts from both domains |
| New terminology | Terminology review, alias registration |
| Retracted source | Explicit handling |

---

## Review Output
```yaml
review:
  reviewer: "human:reviewer.physics-001"
  action: "canonicalize"
  reason: "All gates pass; textbook evidence from Halliday & Resnick 12th ed. p.123 Eq.4.2"
  timestamp: "2026-09-06T12:00:00Z"
  findings:
    - "Evidence locator precise (p.123, Eq.4.2)"
    - "No contradictory evidence found"
    - "Symbol/unit/equation match source"
```

---

## Anti-Patterns
| Don't | Do |
|-------|----|
| Approve without checking locators | Verify every locator resolves |
| Ignore contradictory evidence | Document and qualify |
| Approve AI drafts without human check | Human review mandatory |
| Skip provenance check | Verify all provenance fields |
| Approve without domain expertise | Flag for expert review |

---

## Escalation Conditions
- Contradiction unresolved → Flag for senior review
- No authoritative source found → Document gap
- License unclear for evidence → Legal review
- Cross-domain without expert → Require both domain reviewers