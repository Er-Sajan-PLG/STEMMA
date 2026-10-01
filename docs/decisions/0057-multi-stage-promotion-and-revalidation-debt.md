# ADR-0057: Multi-Stage Promotion and Revalidation Debt

Status: Decided — 2026-10-01
Date: 2026-10-01
Decided by: Sajan (sole owner), ruling on `UNRES-STEMMA-CORE-003` (canonical is
time-relative) and extending the HITL model of `UNRES-STEMMA-HITL-002`.
Relates to: ADR-0043 (mandatory source and history), ADR-0049 (delegated authority
v2), ADR-0050 (contract 2.2.0), ADR-0056 (additive evolution), REQ-STEMMA-HITL-001,
REQ-STEMMA-HITL-002, **REQ-STEMMA-HITL-003**, UNRES-STEMMA-CORE-003,
spec/ROLES_AND_AUTHORITY.md, spec/machine-readable/enforcement_rules.yaml
Amended by: §1c (board waiver) and §3 (pilot-scale full debt block), both ruled
2026-10-01.
Enforced by: `scripts/validate.py`, `scripts/review_entity.py`,
`spec/machine-readable/enforcement_rules.yaml` (ENF-STEMMA-HITL-001..004, including
`pilot_scale_block` and `board_waiver`).
Verified: EVID-STEMMA-HITL-009 / -010 (2026-10-01); 18 tests +
8-case mutation suite.

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

### 1. Replace the single-act promotion with a staged chain

New entity status ladder (additive: existing values remain legal):

```
draft
  → machine_validated
  → validator_validated          (stage 1 — a validator validates)
  → independently_validated      (stage 2 — a DIFFERENT validator re-validates)
  → board_approved               (stage 3 — a board of validators approves)
  → canonical                    (only the board's approval promotes to canonical)
```

**While the board waiver is active (§1c) the chain is shortened**: stage 3 is
skipped, and `canonical` is reached from `independently_validated`:

```
draft → machine_validated → validator_validated → independently_validated → canonical
```

Rules:

- Each stage is recorded in `provenance.promotion_history[]` with the acting agent,
  the timestamp, the stage, and evidence. The record is append-only.
- **Stage 2 must be a different human than stage 1.** Stage 3 (board) must contain
  **at least two** humans, and the board's approvers must be disjoint from the
  stage-1 validator. This is the independence constraint, machine-enforced.
- `canonical` is only reachable from the last stage of the active chain — from
  `board_approved` normally, or from `independently_validated` while the board is
  waived. No transition may jump a stage.
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

#### 1c. Board waiver while the owner is the only validator

Owner ruling 2026-10-01: *"waive the board for now as I am the only validator."*

The board stage presumes a panel of **at least two** humans whose approval is
disjoint from the earlier validators. That panel does not exist yet — the owner is the
sole registered validator. Forcing the stage would produce either an unreachable
`canonical` or a fiction; the honest move is to **omit** it and say so.

The waiver is recorded as machine-readable data, not prose, in
`spec/machine-readable/enforcement_rules.yaml` as `ENF-STEMMA-HITL-003.board_waiver`:

```yaml
board_waiver:
  active: true
  required_stages_while_waived: [validator, independent_validator]
  terminal_status_while_waived: canonical
  retire_when: a second active human agent with a validation role is registered
```

Consequences, all machine-enforced:

- The **required chain becomes two stages** (validator → independent_validator).
  `validate.py` resolves `required_stages` at gate time from the registry, so a
  record carrying the shorter chain validates and a record carrying a board stage
  **fails** (`board stage is currently waived`).
- `canonical` is reachable from `independently_validated`; the CLI's `stage`
  subcommand resolves the chain from the same registry and therefore will not write a
  board stage while the waiver holds (`stage 'board' is not part of the current chain`).
- The two records promoted before the ruling (`metre`, `conn.000156`) were migrated to
  the waived chain; their terminal entry carries `board_waived: true` with a
  `board_waived_reason`, so the audit trail explains the missing stage rather than
  hiding it.
- **Retiring the waiver restores the three-stage chain mechanically.** Flip
  `active: false` and the gate once again requires a board stage with ≥2 humans; the
  records promoted under the waiver then need a board stage before they can be
  re-validated. This is the owner's `retire_when` condition, expressed as data.

The waiver is **narrower** than §1a's independence waiver and it does not replace it:
§1a still governs whether a *single* actor may fill consecutive stages that do exist.
While the board is waived there is no stage 3, so §1a's board-disjointness clause has
nothing to bind — but stage 1 and stage 2 must still be distinct humans, or carry the
§1a waiver.

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

### 3. Debt blocks review status — **fully**, at pilot scale

The central rule, and the one the validator enforces:

> A record (entity **or** connection) whose `revalidation_debt.status` is
> `outstanding` SHALL NOT hold any reviewed status — `validator_validated`,
> `independently_validated`, `board_approved`, `human_reviewed`, or `canonical`.
> At pilot scale the record is **invalid outright** until the debt is cleared and
> the record re-validated.

Owner ruling 2026-10-01: *"for debt at this small scale, actually block it fully until
it is updated and validated. At starting phases, I can handle it; let's see how much
entity it takes for debt to cause problem."*

**Why full, and why now.** The earlier design (see the superseded note below) blocked
only *forward* promotion: a record that accrued debt after being legitimately promoted
was not made illegal, it simply could not advance. That reading is sound *at scale* —
otherwise the arrival of one new entity would cascade into thousands of invalid
records, contradicting provisional canonical. At **pilot scale** the trade-off inverts:
the corpus is small enough that a full block is cheap, and the owner wants to *feel*
the burden — to measure the corpus size at which full blocking starts to hurt. That
measurement is a direct input to the still-OPEN method/tier decisions
(`UNRES-STEMMA-CORE-003`). This is the deliberate "block fully and observe" phase.

The block is therefore data, not a permanent design commitment. `ENF-STEMMA-HITL-002`
carries a `pilot_scale_block` block and a `block_mode: full` value; the gate reads the
mode from the registry. Relaxing to the previous `forward_only` behaviour — when the
owner judges the burden visible — is a one-value owner act in the registry, not a code
change.

The validator must surface the debt **as it validates that record** — the debt must
be visible in frontmatter, and the gate reports it **by name** for the exact record
being validated, so validation of record R cannot pass silently while R owes
obligations. Under `block_mode: full` any reviewed status with outstanding debt is a
**hard error**.

Debt is cleared *by the act of satisfying it*, recorded at whichever stage does the
work:

- **Stage 1 (validator)** clears debt by supplying the missing connections/evidence,
  or by confirming the debt was spurious.
- **Stage 2 (independent validator)** may correct or clear debt the first validator
  missed — a second pair of eyes is exactly where a missed obligation surfaces.
- **Stage 3 (board)** — present only when the board waiver is retired — may correct or
  clear remaining debt before approving.
- Only the **owner** may set debt to `deferred`, with a recorded reason and a
  `deferred_until` condition.

A `cleared` debt records who cleared it, at which stage, and on what evidence. A
`cleared` debt with no `cleared_by`/`cleared_stage`/`clearance_evidence` is rejected —
clearance must be attributable, or it is not clearance.

> **Superseded reading (2026-10-01, same day).** An earlier draft of this section
> described the block as *forward-only*: debt blocked advancement past the last
> recorded stage, and debt on a non-advancing record was a warning. That reading was
> replaced by the owner's full-block ruling above. It is recorded here because the
> forward-only behaviour is the intended behaviour **at scale**, and `block_mode:
> forward_only` remains a legal registry value — the pilot-scale full block is a
> deliberate, time-boxed deviation, not a reversal of the underlying reasoning.

### 4. Migration of the current corpus

The live corpus is `1 canonical (metre) / 8 drafts`. `metre` was promoted under the
single-reviewer model by `human:curator.001`, who was both writer and reviewer. Under
this ADR that is **stage 1 only** — there is no independent validator and no board
record.

`metre` is **not** demoted. Instead it was migrated to the model with an honest
promotion history: the existing `human:curator.001` review is recorded as **stage 1**,
and stage 2 is recorded by the owner acting under the interim single-actor waiver
(§1a) — `human:curator.001` filling `independent_validator` — carrying an
`independence_waiver` sanctioned by the owner. This makes the single-actor fact
**visible in the artifact** rather than hidden in the fact that only one name appears.

When the board waiver (§1c) was ruled later the same day, `metre`'s earlier board entry
was **retired** (`scripts/migrate_board_waiver.py`), leaving the two-stage waived chain;
the terminal entry carries `board_waived: true` so the audit trail explains the gap.
`conn.000156` was migrated the same way.

`metre` also carried an `outstanding` revalidation debt of kind
**`connection_obligations_pending`**: it was canonicalized with only one connection
(`conn.000156`, its own value-slot assertion) and no cross-entity relations, because
the corpus was too small at approval. Under the pilot-scale full block (§3) an
outstanding debt on a reviewed record is a hard error, so the debt was **cleared**
attributably once `conn.000156` was canonical under the waived chain — recorded with
`cleared_by`, `cleared_stage`, `cleared_at`, and `clearance_evidence`.

The 8 drafts carry no debt (debt is a property of promoted entities).

### 5. Consequences in the gate

- `validate.py` gains: `check_revalidation_debt` (debt blocks review status; cleared
  debt must be attributable) and `check_promotion_chain` (canonical requires a
  complete, independent history of the **currently required** chain — two stages while
  the board waiver holds, three otherwise).
- A new promotion CLI records staged promotions; `review_entity.py`'s single
  `canonicalize` is retained but now **refuses** to promote to `canonical` directly —
  it can only advance one stage of the active chain.
- Both `check_revalidation_debt` and `check_promotion_chain` resolve their active
  parameters (`block_mode`, `required_stages`, `board_waived`) from
  `enforcement_rules.yaml` at run time, so retiring the board waiver or relaxing the
  debt block is a registry edit the gate honours on its next run.

## Consequences

**Easier.** Independence becomes structural rather than aspirational. The
`SOLE_OWNER` limitation is no longer the only barrier: a `canonical` entity now
carries machine-checked evidence that the required humans validated it. Debt makes the
time-relative nature of `canonical` explicit instead of implicit, so the corpus-scale
problem is visible rather than latent.

**Harder.** Promotion becomes a pipeline, not a command — multiple recorded acts with
identity constraints. That is more work per entity, which is the point: the previous
model was cheap because it was unverified. The stage-2 independence rule means a
single maintainer **cannot** promote to `canonical` alone *without an owner-sanctioned
waiver*; the interim waiver (§1a) is what allows the current single-actor reality to
proceed, and it is deliberately loud: every promotion that used it exports an
`independence_waiver` naming the owner who sanctioned it. The day a second reviewer is
registered, the waiver drops out of new promotions and the rule enforces itself. The
board waiver (§1c) is the same shape one level up: while no ≥2-human panel exists the
board stage is omitted, not faked, and retiring the waiver restores the three-stage
chain mechanically.

**Hard to undo.** Consumers branching on the staged statuses, on `revalidation_debt`,
or on `independence_waiver` make removal a breaking change. Mitigated by the statuses
being additive and the objects closed.

**Explicitly NOT decided here.** The "should connect" predicate at scale (candidate
generation; naive all-pairs is *O(N²)*), the numeric corpus-size tier thresholds for
validation methods, whether "connection-complete" is a boolean/ratio/graph invariant,
and whether a debt-clearing edit is a new revision under supersede-don't-edit. Also
undecided: the point at which the pilot-scale *full* debt block should relax to
`forward_only`. These remain open in `UNRES-STEMMA-CORE-003` and the pilot-scale
observation is the intended way to inform the last one.

## Verification

Status: **executed and passing (EVID-STEMMA-HITL-009, EVID-STEMMA-HITL-010).**
Implementation: `scripts/validate.py` (`check_promotion_chain`,
`check_revalidation_debt`, `_debt_block_mode`, `_required_stages`, `_board_waiver`),
`scripts/review_entity.py` (`stage`, `clear-debt`, `defer-debt`),
`spec/machine-readable/enforcement_rules.yaml` (`ENF-STEMMA-HITL-001..004`, including
`pilot_scale_block` and `board_waiver`). Migration:
`scripts/migrate_board_waiver.py`. Tests: `tests/repo/test_promotion_chain.py`
(18 passing, wired into the chain) and the mutation suite
`scripts/_mutation_test_promotion.sh` (8 cases).

- `revalidation_debt` declared and closed in **both** `concept.schema.json` and
  `connection.schema.json`; a valid record survives `validate.py`; malformed variants
  rejected.
- A record holding **any** reviewed status while `outstanding` debt is owed →
  `validate.py` exit 1 (full block, `block_mode=full`). (Mutation M5.)
- Clearing the same debt, attributably, returns the record to green.
- A board stage recorded while the board waiver is active → `validate.py` exit 1.
  (Mutation M3.)
- A record carrying the two-stage waived chain → green; flipping
  `board_waiver.active: false` → red, proving the waiver is data the gate honours.
- `canonical` without the required chain → `validate.py` exit 1. (Mutation M2.)
- **Same-day consecutive stages → `validate.py` exit 1 AND `review_entity.py` refuses
  the act in real time.** (Mutation M1.)
- Deleting `enforcement_rules.yaml` → `validate.py` exits non-zero (fail closed),
  proving the day-gap rule cannot be waived by removing its source. (Mutation M8.)
- A promotion whose actors are **not** all distinct and which carries **no**
  `independence_waiver` → `validate.py` exit 1; **with** the waiver → accepted. (M3,
  the negative control.)
- Board with fewer than two members and no waiver → rejected; with the owner waiver →
  accepted and recorded as such. (M3, pre-waiver; superseded by §1c.)
- The same promotion/chain on a **connection** (`conn.000156`) behaves identically —
  all-datasets coverage. (M6, M7, and the migrated record itself.)
- `metre` and `conn.000156` migrated: still canonical, two-stage waived chain with
  `board_waived: true`, debt cleared attributably; export reflects all of it.

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
