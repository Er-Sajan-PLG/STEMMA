# Source Update / Drift Skill

**Purpose:** Teaches an agent how to detect source changes, analyze impact on canonical objects, and handle supersession/retraction.

**When to Use:** Periodic monitoring, after source updates, or when notified of corrections/retractions.

**Mental Model:** Sources change over time. STEMMA must track these changes and propagate impact to canonical objects.

---

## Required Inputs
- Source registry (`sources/`)
- Canonical export (`exports/knowledge.json`)
- Previous source state (`indexes/source_state.yaml`)

---

## Workflow

### 1. Drift Detection
```bash
# Run drift detection
python3 scripts/detect_drift.py
```

### 2. Change Analysis
The script reports:
- **New sources** — newly registered
- **Modified sources** — content hash changed
- **Removed sources** — no longer in registry
- **Lifecycle changes** — active→retracted, etc.
- **Affected canonical objects** — connections/entities using this source

### 3. Impact Assessment
For each affected canonical object:
1. **Check alternative evidence** — does other evidence support the claim?
2. **Determine action needed**:
   - `qualify` — other evidence exists, add `limited_by`/`qualifies`
   - `deprecate` — no other evidence, deprecate connection
   - `review` — entity provenance affected, human review needed

### 4. Handling Specific Events

#### Source Retraction
```bash
python3 scripts/handle_retraction.py --action retract --source lhs:src.xxx --reason "Retracted by publisher" --apply
```
Effect: Marks source `retracted`, proposes deprecation/qualification of dependents.

#### Source Correction
```bash
python3 scripts/handle_retraction.py --action correct --source lhs:src.xxx --reason "Corrigendum: Eq. 4.2 corrected" --apply
```
Effect: Flags dependents for review, adds correction notice.

#### Source Supersession
```bash
python3 scripts/handle_retraction.py --action supersede --source lhs:src.old --new-source lhs:src.new --reason "New edition published" --apply
```
Effect: Marks old `superseded`, links to new, proposes evidence migration.

### 5. Evidence Migration
When superseding:
1. Compare evidence content between old and new source
2. Where content unchanged → update `source_ref` to new source
3. Where content changed → flag for review
4. Where content removed → handle as retraction

### 6. Update Canonical Objects
After decisions:
1. Update connections (add `limited_by`, change status)
2. Update entities (change provenance, add historical note)
3. Regenerate exports: `python3 scripts/validate.py`

---

## Automation vs Manual

| Task | Automation | Human Required |
|------|------------|----------------|
| Drift detection | ✅ `detect_drift.py` | — |
| Impact identification | ✅ | — |
| Alternative evidence check | ✅ (basic) | ✅ (judgment) |
| Action decision | — | ✅ |
| Evidence migration | Partial | ✅ (verify) |
| Canonical updates | — | ✅ (review) |

---

## Monitoring Schedule

| Frequency | Action |
|-----------|--------|
| Per acquisition | `detect_drift.py` after new sources |
| Weekly | Automated drift check |
| On notification | Immediate `handle_retraction.py` |
| Quarterly | Full audit of lifecycle states |

---

## Anti-Patterns
| Don't | Do |
|-------|----|
| Ignore source lifecycle changes | Monitor `lifecycle` field |
| Assume superseded = identical | Verify content equivalence |
| Auto-deprecate on retraction | Check for alternative evidence |
| Modify canonical silently | Always via review workflow |

---

## Escalation Conditions
- Major source retracted with many dependents → Senior review
- Supersession with significant content changes → Domain expert
- Correction affects cross-domain claims → Multi-domain review
- Legal takedown request → Legal review