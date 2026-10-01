# ADR-0057: Multi-Stage Promotion and Revalidation Debt

Status: Decided — 2026-10-01
Date: 2026-10-01
Decided by: Sajan (sole owner), ruling on `UNRES-STEMMA-CORE-003` (canonical is
time-relative) and extending the HITL model of `UNRES-STEMMA-HITL-002`.
Relates to: ADR-0043 (mandatory source and history), ADR-0049 (delegated authority
v2), ADR-0050 (contract 2.2.0), ADR-0056 (additive evolution), REQ-STEMMA-HITL-001,
REQ-STEMMA-HITL-002, **REQ-STEMMA-HITL-003**, UNRES-STEMMA-CORE-003,
spec/ROLES_AND_AUTHORITY.md, spec/machine-readable/enforcement_rules.yaml
Amended by: nothing yet.
Enforced by: `scripts/validate.py`, `scripts/review_entity.py`,
`spec/machine-readable/enforcement_rules.yaml` (ENF-STEMMA-HITL-001..004).
Verified: EVID-STEMMA-HITL-009 / -010 (2026-10-01); 14 tests +
7-case mutation suite.

## Context

Two owner rulings on 2026-10-01 force the same conclusion from opposite ends.

**From the corpus side (`UNRES-STEMMA-CORE-003`).** An entity can be legitimately
canonicalized *before* the corpus contains enough entities to give it meaningful
connections. As the corpus grows — the target is millions to billions of entities —
every previously-canonicalized entity may come to owe connections it could not have
had, and must be re-validated. Today, `canonical` is treated as a **terminal state
reached once and gated once**. At scale that is unsound: an early canonical entity
can silently become connection-incomplete as the graph grows around it, and no gate
notices. The owner ruled that the obligation is to be modelled as **revalidation
debt**: canonical records the corpus state at approval; new relevant entities accrue
explicit "revalidation owed" debt; the entity stays canonical but flagged; the debt
must be cleared — or explicitly deferred by the owner — before the next baseline.

**From the authority side.** The owner ruled that the validator is **not** the final
canonicalizer:

> "the validator is not the final canonicalizer, it will be verified by another
> validator and it will finally reach board where multiple validators will finally
> validate it."

The current model has exactly one reviewer concept (`provenance.reviewer`, a single
human) and one promotion act (`review_entity.py canonicalize`, which jumps straight
from `human_reviewed` to `canonical`). That is a **single point of authority**. It is
also the model the `SOLE_OWNER` limitation record already flags as the project's
central structural weakness: *"Independence is absent."* A staged chain — validator,
then an *independent* validator, then a board — is the mechanism by which independence
enters the promotion path.

The owner also ruled that debt is cleared **by validation**, at every stage:

> "the validator cannot complete validation until debt is fixed as well … validator
> can do validation and mass debt clearance … independent validator and board also
> corrects debts if it needs it."

## Decision

### 1. Replace the single-act promotion with a three-stage chain

New entity status ladder (additive: existing values remain legal):

```
draft
  → machine_validated
  → validator_validated          (stage 1 — a validator validates)
  → independently_validated      (stage 2 — a DIFFERENT validator re-validates)
  → board_approved               (stage 3 — a board of validators approves)
  → canonical                    (only the board's approval promotes to canonical)
```

Rules:

- Each stage is recorded in `provenance.promotion_history[]` with the acting agent,
  the timestamp, the stage, and evidence. The record is append-only.
- **Stage 2 must be a different human than stage 1.** Stage 3 (board) must contain
  **at least two** humans, and the board's approvers must be disjoint from the
  stage-1 validator. This is the independence constraint, machine-enforced.
- `canonical` is only reachable from `board_approved`. No transition may jump a stage.
- `human_reviewed` is retained as a **legacy alias** for "at least stage 1
  validated" and is deprecated in favour of `validator_validated`; it remains legal so
  existing records do not break (see migration, §4).

#### 1a. Interim single-actor waiver (owner-sanctioned, recorded, must be retired)

The owner rulings of 2026-10-01 also establish the current operational reality:

> "Until further notice, I am the validator, independent validator and the board."

The independence constraint above cannot be *satisfied* by one human — but pretending
otherwise, or silently weakening the rule, would be the failure mode this whole line of
work exists to prevent. The resolution is to keep the rule **strict** and make the
waiver **explicit and visible**:

- A `human:` agent entry in `schema/agent-registry.yaml` carries
  `roles: [validator, independent_validator, board]` to declare which chain roles that
  agent may fill.
- A canonical entity's `provenance.promotion_history[]` may carry an
  **`independence_waiver`** object on the promotion: `{ authored_by, sanctioned_by,
  reason, sanctioned_at, retire_when }`. It is only legal when `sanctioned_by` is the
  `SOLE_OWNER`.
- When the promotion chain's actors are **not** all distinct (i.e., the independence
  rule is violated in fact), the promotion **must** carry a valid
  `independence_waiver`; otherwise `validate.py` exits 1. So either independence holds
  by identity, or the waiver is present and attributable to the owner. There is no
  third option where the check simply passes.
- **The waiver does not hide the gap — it labels it.** It is machine-visible, it
  names the owner who sanctioned it, and it carries a `retire_when` condition. A
  promotion that used the waiver is exported as such, so any consumer can see that a
  given canonical record rests on a single human's word.

This keeps the artifact honest under `SOLE_OWNER` while making the eventual arrival of
genuinely independent validators a *mechanical* change: the waiver disappears from new
promotions and the identity constraint enforces itself.

#### 1b. Stages must land on separate days — an owner-set, unbreakable rule

Owner directive 2026-10-01: *"real time gate the validation, do not let me validate,
independent validate and board validate at the same time, keep 1 day time different
and I cannot break it … Keep it in record, not in ADR, a strong enough place to
enforce it."*

Consecutive promotion stages of one record SHALL be applied on **separate calendar
days** (minimum gap: 1 day, inclusive of the day boundary). Three acts by one person
on one afternoon are a formality, not a review; a canonicalization reached that way
is measurably biased.

Unlike the rest of this ADR, the rule does **not** live only in prose. It is recorded
as machine-readable data in `spec/machine-readable/enforcement_rules.yaml`
(`ENF-STEMMA-HITL-001`), and enforced in two places:

- **Real time (the CLI):** `scripts/review_entity.py stage` refuses to record a stage
  that would fall on the same day as the previous one, with a `TIME GATE` error.
- **The gate:** `scripts/validate.py` re-checks every `promotion_history` at build
  time and exits 1 on a same-day pair, so a hand-edited frontmatter cannot slip past
  the CLI.

The whole registry **fails closed**: if `enforcement_rules.yaml` is missing or
unreadable, the gate exits non-zero rather than falling back to a default. Deleting
the file therefore does not waive the rule — it breaks the build. This is the
"strong enough place" the owner asked for: the rule is data, and the data is
load-bearing.

The **independence** requirement (distinct humans per stage) remains waivable via
§1a. The **time** requirement is not waivable by the waiver — the two are orthogonal,
and only the former has a legitimate single-actor justification.

### 2. Add a `revalidation_debt` object to every canonical record

Declared in **both** `schema/concept.schema.json` and `schema/connection.schema.json`
(closed object; `additionalProperties: false`). Owner directive 2026-10-01:
*"revalidation must be on all datasets, not just on entities, all datasets including
connection."* Entities and connections are both first-class canonical datasets, so a
connection that was promoted before its endpoints were canonical owes debt exactly as
an entity does.

| Key | Required | Meaning |
|---|---|---|
| `status` | **yes** | `outstanding` \| `cleared` \| `deferred` |
| `reason` | **yes** | why the debt was incurred (e.g. "no candidate connections existed at approval; corpus now contains `stemma:phys.mass`") |
| `incurred_at` | **yes** | ISO date the debt was incurred |
| `items` | no | the specific obligations owed (connection ids to add, entities to reconcile) |
| `cleared_by` | no | registered human who cleared it (a validator, independent validator, or board member) |
| `cleared_at` | no | ISO timestamp of clearance |
| `cleared_stage` | no | `validator` \| `independent_validator` \| `board` — which stage cleared it |
| `clearance_evidence` | no | what was done to clear it (connection ids added, etc.) |
| `deferred_by` | no | owner who deferred it (SOLE_OWNER only) |
| `deferred_until` | no | condition or date the deferral ends |

### 3. Debt blocks review-status promotion

The central rule, and the one the validator enforces:

> A record (entity **or** connection) whose `revalidation_debt.status` is
> `outstanding` may not be promoted **past the stage it has already reached** —
> it may not advance to `validator_validated`, `independently_validated`,
> `board_approved`, or `canonical`.

Reading, and why it is a *forward* block rather than a retroactive one: a record
that accrued debt *after* being legitimately promoted is not made illegal by the
arrival of a new obligation — otherwise every canonical record would become invalid
the moment the corpus grew, which contradicts the whole point of provisional
canonical. What debt blocks is **advancement**. It is checked against the last
recorded promotion stage, so debt accrued at the validator stage blocks the
independent-validator stage, and so on.

The validator must surface the debt **as it validates that record** — the debt must
be visible in frontmatter, and the gate reports it **by name** for the exact record
being validated, so validation of record R cannot pass silently while R owes
obligations. A forward promotion attempted under `outstanding` debt is a **hard
error**; the same debt on a record that is not advancing is reported loudly as a
**warning** on every run, so it can never be forgotten.

Debt is cleared *by the act of satisfying it*, recorded at whichever stage does the
work:

- **Stage 1 (validator)** clears debt by supplying the missing connections/evidence,
  or by confirming the debt was spurious.
- **Stage 2 (independent validator)** may correct or clear debt the first validator
  missed — a second pair of eyes is exactly where a missed obligation surfaces.
- **Stage 3 (board)** may correct or clear remaining debt before approving.
- Only the **owner** may set debt to `deferred`, with a recorded reason and a
  `deferred_until` condition.

A `cleared` debt records who cleared it, at which stage, and on what evidence. A
`cleared` debt with no `cleared_by`/`cleared_stage`/`clearance_evidence` is rejected —
clearance must be attributable, or it is not clearance.

### 4. Migration of the current corpus

The live corpus is `1 canonical (metre) / 8 drafts`. `metre` was promoted under the
single-reviewer model by `human:curator.001`, who was both writer and reviewer. Under
this ADR that is **stage 1 only** — there is no independent validator and no board
record.

`metre` is **not** demoted. Instead it is migrated to the new model with an honest
promotion history: the existing `human:curator.001` review is recorded as **stage 1**,
and stages 2 and 3 are recorded by the owner acting under the interim single-actor
waiver (§1a) — `human:curator.001` filling `independent_validator` and `board` — each
carrying an `independence_waiver` sanctioned by the owner. This makes the
single-actor fact **visible in the artifact** rather than hidden in the fact that
only one name appears.

Independently, `metre` carries an `outstanding` revalidation debt of kind
**`connection_obligations_pending`**: it was canonicalized with only one connection
(`conn.000156`, its own value-slot assertion) and no cross-entity relations, because
the corpus was too small at approval. Its `items` name the obligation to acquire the
connections the now-larger corpus implies. This debt must be cleared by a validation
stage or owner-deferred before the next baseline.

The 8 drafts carry no debt (debt is a property of promoted entities).

### 5. Consequences in the gate

- `validate.py` gains: `check_revalidation_debt` (debt blocks review status; cleared
  debt must be attributable), and `check_promotion_chain` (canonical requires a
  complete, independent three-stage history).
- A new promotion CLI records staged promotions; `review_entity.py`'s single
  `canonicalize` is retained but now **refuses** to promote to `canonical` directly —
  it can only advance one stage.

## Consequences

**Easier.** Independence becomes structural rather than aspirational. The
`SOLE_OWNER` limitation is no longer the only barrier: a `canonical` entity now
carries machine-checked evidence that two or more *different* humans validated it.
Debt makes the time-relative nature of `canonical` explicit instead of implicit, so
the corpus-scale problem is visible rather than latent.

**Harder.** Promotion becomes a pipeline, not a command — three recorded acts with
identity constraints. That is more work per entity, which is the point: the previous
model was cheap because it was unverified. The stage-2 independence rule means a
single maintainer **cannot** promote to `canonical` alone *without an owner-sanctioned
waiver*; the interim waiver (§1a) is what allows the current single-actor reality to
proceed, and it is deliberately loud: every promotion that used it exports an
`independence_waiver` naming the owner who sanctioned it. The day a second reviewer is
registered, the waiver drops out of new promotions and the rule enforces itself.

**Hard to undo.** Consumers branching on the staged statuses, on `revalidation_debt`,
or on `independence_waiver` make removal a breaking change. Mitigated by the statuses
being additive and the objects closed.

**Explicitly NOT decided here.** The "should connect" predicate at scale (candidate
generation; naive all-pairs is *O(N²)*), the numeric corpus-size tier thresholds for
validation methods, whether "connection-complete" is a boolean/ratio/graph invariant,
and whether a debt-clearing edit is a new revision under supersede-don't-edit. These
remain open in `UNRES-STEMMA-CORE-003` and need their own ruling.

## Verification

Status: **executed and passing (EVID-STEMMA-HITL-009, EVID-STEMMA-HITL-010).**
Implementation: `scripts/validate.py` (`check_promotion_chain`,
`check_revalidation_debt`), `scripts/review_entity.py` (`stage`, `clear-debt`,
`defer-debt`), `spec/machine-readable/enforcement_rules.yaml`. Tests:
`tests/repo/test_promotion_chain.py` (14 passing, wired into the chain) and the
mutation suite `scripts/_mutation_test_promotion.sh` (7 cases).

- `revalidation_debt` declared and closed in **both** `concept.schema.json` and
  `connection.schema.json`; a valid record survives `validate.py`; malformed variants
  rejected.
- A record promoted forward while `outstanding` debt is owed → `validate.py` exit 1.
- An `outstanding` debt on a record that is **not** advancing → reported by name on
  every run (warning), never silently dropped.
- `canonical` without stage-2 and stage-3 records → `validate.py` exit 1.
- **Same-day consecutive stages → `validate.py` exit 1 AND `review_entity.py` refuses
  the act in real time.** (Mutation M1.)
- Deleting `enforcement_rules.yaml` → `validate.py` exits non-zero (fail closed),
  proving the day-gap rule cannot be waived by removing its source. (Mutation M7.)
- A promotion whose actors are **not** all distinct and which carries **no**
  `independence_waiver` → `validate.py` exit 1; **with** the waiver → accepted. (M3,
  the negative control.)
- Board with fewer than two members and no waiver → rejected; with the owner waiver →
  accepted and recorded as such. (M3.)
- The same promotion/chain on a **connection** (`conn.000156`) behaves identically —
  all-datasets coverage. (M6, and the migrated record itself.)
- `metre` migrated: still canonical, full three-stage history with waiver, carries
  `outstanding` debt `connection_obligations_pending`; export reflects all of it.

## Related

- ADR-0043 — mandatory source and history (the review-history precedent)
- ADR-0049 — delegated authority v2 (the `authority` key the board uses)
- ADR-0050 — contract 2.2.0 (additive-evolution precedent)
- ADR-0056 — additive evolution ("evolve additively within a major version")
- REQ-STEMMA-HITL-001 / -002 / **-003** — the review requirements this extends
- `spec/machine-readable/enforcement_rules.yaml` — `ENF-STEMMA-HITL-001`..`004`
- `UNRES-STEMMA-CORE-003` — the revalidation-debt ruling
- `spec/ROLES_AND_AUTHORITY.md` — the `SOLE_OWNER` limitation and interim three-role
  waiver record
