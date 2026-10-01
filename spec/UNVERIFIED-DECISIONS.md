# The three UNVERIFIED requirements — owner decision sheet

Prepared: 2026-10-01 · For: Sajan (`human:curator.001`, SOLE_OWNER)
Status of the drive: **22 VERIFIED · 0 FAILED · 3 UNVERIFIED** (of 25)

This sheet exists because the three remaining requirements are **not** blocked on
verification work. Each is blocked on something only the owner can supply, or on
code that does not exist. They are listed here so the owner can rule on them in
one pass.

Executed by the executor under Constraint D (`spec/ROLES_AND_AUTHORITY.md` §79):
the executor may *execute* verification and *record* results, but may not
approve, reject, or defer requirements, close an `UNRES-` record, or convert an
`INFERENCE` to a `FACT` without owner review. Nothing below changes a status.

---

## Summary — three requirements, three different blockers

| Requirement | Why it is UNVERIFIED | Who can clear it |
|---|---|---|
| `REQ-STEMMA-EXP-004` | AC1 PASS; **AC2 needs an owner confirmation** that the canonical-only consumer contract is intended (closes `UNRES-STEMMA-EXP-001`) | **Owner** — a recorded ruling |
| `REQ-STEMMA-OPS-002` | Criterion is a **trend across releases**; only one release point existed when recorded | **Owner** — accept the criterion as met, or redefine it |
| `REQ-STEMMA-INTEG-001` | AC3 unmet — **no grounded AI chat is implemented** | **Nobody** — this is an implementation gap, not verification |

---

## 1 · `REQ-STEMMA-EXP-004` — consumer exports honor `review_policy`

**Statement.** Consumer exports SHOULD honor each consumer's declared
`review_policy` (e.g. learninghub = canonical-only).

**Method.** `INTEGRATION_TEST`. **Status.** `UNVERIFIED`.

### AC1 — PASS (re-executed 2026-10-01)

Executed against the live corpus by rebuilding the `learninghub` export under
each policy:

| `--review-policy` | entities | statuses |
|---|---|---|
| `all` | 9 | 8 draft + 1 canonical |
| `reviewed` | 1 | canonical |
| `trusted` | 1 | canonical |
| `canonical` | 1 | canonical |

The filter is **non-vacuous**: widening the policy re-admits the drafts, so the
exclusion is caused by `review_policy`, not by the drafts being absent.

> **Correction made this round.** The verification record and
> `EVID-STEMMA-EXP-017` previously stated *"7 canonical / 2 draft"* and
> *"reviewed/trusted/canonical each yield 7"*. Those numbers predate the HITL
> ruling that demoted six LLM-written entities. Re-executing showed the corpus is
> **1 canonical / 8 draft** and the filtered policies yield **1**. The records have
> been corrected to the executed values. A guard test now asserts the *relationship*
> (drafts excluded, monotonic widening, non-vacuity) so the numbers cannot drift
> silently again.

### AC2 — OPEN, needs the owner

AC2 requires that the behaviour be documented **and owner-confirmed** via
`UNRES-STEMMA-EXP-001`. The owner's *direction* is already recorded in
`spec/APPROVAL-WORKSHEET.md` A1:

> emptiness is exceptional; once any entity is canonical, a consumer whose policy
> admits that entity SHALL NOT receive an empty export — emptiness at that point
> indicates a canonicalization failure.

What has **not** happened is the formal closure of `UNRES-STEMMA-EXP-001`
(`authority_required: SOLE_OWNER`) with a resolution that matches that ruling.

**Decision requested.** One of:
- **(a)** Confirm the canonical-only consumer contract as intended → close
  `UNRES-STEMMA-EXP-001` with the amended acceptance criterion quoted above, and
  `EXP-004` becomes `VERIFIED`.
- **(b)** Amend the requirement (e.g. specify a minimum-canonical-count threshold
  before a canonical-only export is meaningful) → requirement is revised, not verified.
- **(c)** Defer → record why.

**Note.** `UNRES-STEMMA-EXP-001`'s original premise ("0 entities, all-draft
corpus") is now stale; the corpus has 1 canonical. Whatever is decided, the
resolution text should record the premise change rather than appearing to answer
the 0-entity question.

---

## 2 · `REQ-STEMMA-OPS-002` — machine-owned counts and versions

**Statement.** Living documents SHOULD NOT hardcode machine-owned counts or
versions; single sources (`status_truth`, `VERSION.yaml`) own them.

**Method.** `INSPECTION`. **Status.** `UNVERIFIED`.

### What is established

`EVID-STEMMA-OPS-008` (FACT, HIGH) records that **all single-source mechanisms
exist and are gate-enforced**. What was missing was the measurement: the criterion
is a **trend across releases**, and at the time of recording `git tag` was empty —
a single point in time cannot show a trend.

### What has changed

`v3.0.0` is now tagged (plus `v3.0.0-rc1..rc4`). The "`git tag` is empty" premise
is therefore **no longer true**, and a second release would make the trend
measurable for the first time.

### Why the executor did not simply mark it VERIFIED

Two reasons, both deliberate:

1. Whether one tagged release plus its candidates constitutes the "trend across
   releases" the criterion intends is a **judgment call**, not a mechanical test.
2. The supporting evidence `EVID-STEMMA-OPS-004` is class **INFERENCE** — and
   Constraint D forbids converting an `INFERENCE` to a `FACT` without owner review.

Ironically, this requirement is itself about machine-owned values drifting in
prose — and the drift corrected in §1 is a live example of exactly that failure
mode. That is offered as evidence *for* the requirement's value, not as proof of
the trend.

**Decision requested.** One of:
- **(a)** Accept a documented **per-release audit** as the measurement instrument,
  and treat the trend as **starting** at `v3.0.0` (first data point) → `OPS-002`
  stays `UNVERIFIED` until a second release completes the pair, then is verified
  mechanically.
- **(b)** Redefine the criterion to something measurable now (e.g. a gate that
  fails on any newly-introduced hardcoded machine-owned value), making the
  requirement verifiable at a single point in time.
- **(c)** Defer.

---

## 3 · `REQ-STEMMA-INTEG-001` — explorer preserves the graph, adds grounded AI chat

**Statement.** The reference explorer SHALL remain a working consumer that renders
the derived graph export, and SHALL provide an AI chat grounded in the STEMMA
export (citations to entity ids + source refs), reading derived artifacts only —
never canonical markdown.

**Method.** `INTEGRATION_TEST`. **Status.** `UNVERIFIED`.

### Criteria status

| AC | Result | Evidence |
|---|---|---|
| AC1 graph rendering | ✅ PASS | `verify-graph-projection.mjs` exits 0, 10 PASS; verifier rejects an export lacking `connections[]` |
| AC2 wired into CI, required by all-green | ✅ PASS | `ci.yml:87-116`; `ci.yml:331,339` |
| AC3 grounded AI chat with citations + refusal | ❌ **NOT SATISFIED** | — |
| AC4 reads `exports/` only (graph viewer) | ✅ PASS | no `content/` or `*.md` reference in `explorer/src` or `explorer/scripts` |

### Why AC3 fails — independently confirmed this round

`explorer/src/components/` contains only: `accessible-list-view`,
`concept-inspector-view`, `graph-legend`, `graph-view`, `search-filter-bar`.
There is **no chat surface**, and no citation, grounding, or refusal logic.

The only textual match for "chat" in the explorer is a CSS class `chat-soon`
(`explorer.css:26`) applied to a **Feedback link** (`search-filter-bar.ts:33`) —
a placeholder badge pointing at a GitHub issue form. It is not a chat.

**Decision requested.** One of:
- **(a)** Implement the grounded chat (AC3) → then `INTEG-001` becomes verifiable.
- **(b)** Split the requirement: verify the graph-consumer half (`INTEG-001a`,
  ACs 1/2/4 — all passing today) and re-scope the chat into its own requirement
  (`INTEG-001b`) tracked as an open implementation item.
- **(c)** Defer with a recorded rationale.

**This one cannot be closed by verification.** No amount of inspection can make a
missing feature exist. Marking it VERIFIED would be a false record.

---

## What the executor did this round

- **Re-executed** AC1 of `EXP-004` and recorded the actual result.
- **Corrected** stale counts in `spec/machine-readable/verification.yaml`
  (`EXP-004.result`) and `spec/machine-readable/evidence.yaml`
  (`EVID-STEMMA-EXP-017`, locator + observation).
- **Added a guard test** —
  `tests/repo/test_export_consumers.py::test_review_policy_filter_excludes_drafts_and_widens_monotonically`
  — asserting the review-policy relationship rather than hardcoded counts.
  Mutation-proven: sabotaging `entity_passes` to ignore the policy makes it fail,
  naming all 8 leaked drafts.
- **Did not** change any requirement status, close any `UNRES-`, or edit
  `docs/decisions/r6-identifier-base.md` (decision records are historical and
  exempt from `test_independence.py`; its "7 canonical" is a snapshot of decision
  time, not a live claim).

## Left deliberately untouched

- `spec/APPROVAL-WORKSHEET.md` — already marked "EXECUTED"; its A1 section is the
  record of the owner's *direction*, which remains accurate as written.
- `docs/decisions/r6-identifier-base.md` — immutable historical record.
- `PROGRESS.md` — a log; historical phrasing is correct there.
