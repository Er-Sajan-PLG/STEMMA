# Curation Protocol

**Status:** Authoritative review protocol (human review workflow).

## 1. Status definitions

| State | Meaning |
|-------|---------|
| `proposed` | Candidate assertion, unreviewed; may be LLM or migration-generated |
| `asserted` | Directly authored assertion awaiting review (migration legacy uses proposed, not asserted) |
| `reviewed` | Human has reviewed and accepted as scientifically sound; not yet canonical |
| `canonical` | Human-reviewed and endorsed as established knowledge; trusted export includes it |
| `rejected` | Human has reviewed and rejected; remains auditable, never deleted |
| `deprecated` | Superseded by newer assertion; retained with `deprecated_by` |
| `inferred` | `assertion.type == inferred` with `inference.rule`/`path`; review independent of type |

> A schema-valid connection is not necessarily a scientifically accepted assertion. Schema correctness ≠ semantic acceptance.

## 2. Transitions (authoritative — see `scripts/curation_state.py`)

```
proposed ──accept──→ reviewed ──canonicalize──→ canonical
   │                    │
   ├──reject──→ rejected ├──reject──→ rejected
   └──defer──→ proposed └──defer──→ reviewed

asserted ──review──→ reviewed / canonical / rejected (see state machine)
inferred ──review──→ reviewed / canonical (requires inference metadata)
rejected ──reopen──→ proposed (explicit reopen, never direct to canonical)
```

Forbidden: `rejected → canonical` without reopen; `proposed → canonical` without `reviewed` intermediate; `inferred` without `inference` block.

## 3. Evidence standards by family

| Family | Minimum evidence for canonical |
|--------|-------------------------------|
| **structural/hierarchical** (`is_a`, `part_of`, `generalizes`) | Authoritative conceptual source (textbook/standard) or definition |
| **dependency** (`mathematically_requires`, `logically_requires`, `requires`) | Explicit derivation, definition, or prerequisite documentation; equation where applicable |
| **causal** (`causes`, `contributes_to`, `influences`) | Experimental literature or strong theoretical derivation; textbook alone insufficient for strong `causes` |
| **explanatory** (`explains`, `accounts_for`) | Source showing explanatory relation |
| **model** (`approximates`, `idealizes`, `extends`, `supersedes`) | Scope/regime/applicability conditions required (`context.regime`, `assumptions`) when regime-dependent |
| **analogy** (`analogous_to`) | Explicit mapping or structural correspondence; `analogous_to` ≠ `equivalent_to` ≠ `isomorphic_to` |
| **measurement** (`measures`, `expressed_in`, `has_unit`) | Standard definition or unit specification |
| **cross_domain** (`bridges`, `shared_mechanism_with`) | Mechanism or pathway citation; scope-aware (domain OR subdomain differs) |
| **associative/derivation** (`related_to`, `derived_from`, `appears_in_law`, `applies_to`) | Source citation for `related_to` may be general; `derived_from` requires derivation source |

Where evidence is absent but relation is axiomatic/definition-like (e.g., `part_of` for nucleus→cell), document why absence is acceptable in `evidence: [{type: other, description: "axiomatic structural definition"}]`.

## 4. Review gate (D17)

Before marking canonical, all must hold:
- Reviewer identified (`provenance.reviewed_by` human)
- Relation semantics valid (registry domain/range)
- Source/target valid
- Context valid where required (model regime)
- Evidence adequate per family (above)
- Provenance adequate (asserted_by preserved, origin preserved)
- No unresolved contradiction (integrity anomalies)
- Origin preserved (`migrated` remains migrated)
- Review history recorded (previous state preserved)

## 5. Confidence policy (D9)

- `confidence` optional for reviewed/canonical
- If set, `confidence_basis` required (`expert_review`, `experimental`, `theoretical`, `derived`)
- Confidence does not increase automatically on canonicalization
- Do not use confidence as proxy for review status

## 6. Provenance & origin (D7, D11, D12)

- `origin` derived from `provenance.method` + `asserted_by.type`: `migrated` | `human-authored` | `llm-authored` | `derived`
- Migrated: `origin=migrated` persists even after `review.status=canonical`; `asserted_by` remains `unknown:legacy-relationship` (not rewritten to human)
- LLM-assisted: `asserted_by: {type: llm}` must remain traceable; canonical requires human `reviewed_by`
- Every canonicalization records `review_history` (previous state → new state, reviewer, date, reason) — see `provenance.review_history`

## 7. Contradiction/dispute (D10)

Conflicting reviewed assertions (`A causes B` vs `A contradicts B`) are not silently deleted. Keep both with `review.status`, add dispute note, or mark one `rejected` with reason; preserve audit trail.

## 8. Exports (D13)

- `all`: all active
- `reviewed`: `reviewed` + `canonical`
- `canonical`: `canonical` only
- `trusted` (default educational): `reviewed`/`canonical` excluding `llm-authored` unreviewed (see `scripts/graph_policy.py`)
- `exports/knowledge.json` remains backward compatible (all active); filtered exports via policy module

## 9. Pilot

First batch 10–20 high-value assertions prioritized by centrality, prerequisite importance, domain coverage; quality over quota.

## 10. Principles

- Preserve uncertainty: `related_to` preferable to false precision
- Never fabricate confidence/evidence/reviewer
- Derived never becomes canonical without independent review
- Rejected remains auditable
