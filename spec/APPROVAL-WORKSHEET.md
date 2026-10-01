# SPEC APPROVAL WORKSHEET — CORE-GATE-EXPORT slice (24 requirements)

Prepared: 2026-10-01 · For: Sajan (SOLE_OWNER) · Status: **EXECUTED — verdicts given and applied 2026-10-01** (all 24 APPROVED; see spec/BASELINE.md L3)
Source of truth: `spec/machine-readable/requirements.yaml` (24 records, all `status: APPROVED`,
all `approver: null`). Readable mirror: `spec/REQUIREMENTS.md`.

## How to use this worksheet

1. Read the three **judgment calls** in Part A — they are the only ones needing real thought.
2. Skim Part B — 19 requirements. Recommended verdicts given; correct me if any is wrong.
3. Tell me the verdicts. Verdicts are `APPROVED` / `REJECTED` / `DEFERRED` per requirement.
4. I apply them to `requirements.yaml` (status + `approver: human:curator.001`), update the
   mirror + baseline, and the validator's approval-metadata checks then exercise the
   APPROVED path.

**Recommended overall stance: APPROVE what is true today; change what is not.** Approving a
requirement is asserting "this accurately describes the system as it exists and should
continue to." It is not a claim of perfection, and it is not irreversible — a REJECTED or
DEFERRED requirement can be revised and re-proposed later.

---

# PART A — THE THREE JUDGMENT CALLS

## A1 · REQ-STEMMA-EXP-004 — should an empty consumer export exist?

**Requirement as written:** *Consumer exports SHOULD honor each consumer's declared
`review_policy` (e.g. learninghub = canonical only).*
`validation_status: PARTIALLY_SUPPORTED` · `origin: RECOVERED` · P1 · SHOULD

**The question the recovery agent flagged:** `learninghub` declares `review_policy:
canonical`. At the time of writing (2026-10-01) the corpus had 7 canonical entities, so the
export was *not* empty then. **Superseded 2026-10-01:** the HITL ruling demoted six
LLM-written entities, so the corpus is now 1 canonical (metre) / 8 draft and the
canonical-only export yields 1 entity. This paragraph is a dated snapshot, not a
live count — the live count is owned by `scripts/status_truth.py`. But the agent noted a scenario where it would be — hence `UNRES-STEMMA-EXP-001`
"empty `learninghub` consumer export" — and could not confirm whether emptiness was
intended or a bug.

**Owner direction (2026-10-01), recorded:**
- STEMMA must be **clean of database and RAG concerns** — those are the *consumer's*
  problem. STEMMA's only job is to produce a **linkable schema** plus canonical content.
- The content **should not be empty** — verified entities already exist. *(As of the
  2026-10-01 ruling: 7 canonical; superseded later the same day to 1 canonical after
the HITL demotion. The criterion, not the count, is what was ruled.)*
- **If** an export is empty, emptiness is *exceptional and acceptable only at the current
  starting stage*. It must not be a standing condition: if a consumer export is empty
  *after* canonicalization is operating, that is a **signal that entities are not being
  canonicalized** — i.e. a canonicalization failure, not an export policy question.
- **Engine verification performed (2026-10-01, as of that date):** canonicalization is
  working. 7 entities were `status: canonical`; 2 (`second`, `kilogram`) sat at `draft`
  awaiting owner review — correct HITL behavior, not a failure. The export was
  non-empty. *(Superseded later the same day: the HITL ruling demoted the 6
  LLM-written canonical entities; corpus is now 1 canonical / 8 draft. The engine
  finding stands; the count does not.)* See also the engine defect found in Part C.

**Recommended verdict: APPROVE, with an acceptance-criteria amendment.**
The requirement's *intent* (exports honor `review_policy`) is sound and is what STEMMA
should do. What needs writing down is the owner's ruling that emptiness is exceptional:
add an acceptance criterion along the lines of *"an empty consumer export is permitted only
while the corpus is pre-canonical; once any entity is canonical, a consumer whose policy
admits that entity SHALL NOT receive an empty export — emptiness at that point indicates a
canonicalization failure and SHALL be treated as a defect."*

**Flag:** approving this closes `UNRES-STEMMA-EXP-001`. Also note the agent's wording was
"empty export"; the owner's ruling reframes it as "empty *state* is exceptional" — worth a
one-line note in the resolution so the record matches the ruling.

---

## A2 · REQ-STEMMA-SEC-002 — webapp API-key handling

**Requirement as written:** *Provider API keys SHALL NOT be committed; key material lives
only in runtime configuration/credentials stores.*
`validation_status: NEEDS_AUTHORITY` · `origin: EXTERNAL (XC-5)` · P2 · SHALL NOT

**Why the agent flagged it:** the origin is an *external constraint* (XC-5), not recovered
from the codebase, and the recovery slice marked `webapp/` as `NOT_YET_ASSESSED` —
so nothing verified that the webapp actually satisfies it. The agent could describe the
rule but could not assert the implementation conforms.

**Owner direction (2026-10-01), recorded:**
- The webapp's **main purpose** is to let the owner feed files in for canonicalization —
  it is, at least for now, **the only channel** by which content becomes canonical.
- An alternative (AI uses websearch and proposes entities) is **explicitly not wanted
  for now** — recorded as "it will be messy."
- Implication for scope: the webapp is a **private, owner-operated admin tool**, not a
  public service. Its security posture is therefore evaluated against that reality.

**Recommended verdict: APPROVE the requirement; DEFER its verification.**
The rule itself is uncontroversial and true of the canonical layer today (`SEC-001`
already machine-checks secrets in canonical, and CI passes). What is *unverified* is the
webapp's key handling — but that is a **verification** gap, not a requirement defect. Note
that ADR-0054 and the README already document the webapp as `127.0.0.1`-bound, admin-only,
fail-closed on identity, with an endpoint-bound key. So the practical risk surface is
narrow. Approving the requirement and deferring the verification keeps the requirement
honest without asserting an untested conformance claim.

**Small correction worth making:** the webapp being the *only* canonicalization channel is
a **load-bearing architectural fact** currently recorded nowhere in the spec. It arguably
deserves its own requirement (a new `REQ-STEMMA-*-NNN`) rather than living only in this
worksheet. Flagged as a follow-up, not part of this approval.

---

## A3 · REQ-STEMMA-OPS-002 — the "inference" requirement (elaboration requested)

**Requirement as written:** *Living documents SHOULD NOT hardcode machine-owned counts or
versions; single sources (status_truth, VERSION.yaml) own them.*
`validation_status: NEEDS_AUTHORITY` · `origin: PROPOSED` · P2 · SHOULD

**What "INFERENCE" means here.** The evidence register classifies every record as `FACT`
(directly observed), `CLAIM` (asserted, unconfirmed), or `INFERENCE` (reasoned conclusion
drawn *from* observations, not itself observed). `EVID-STEMMA-OPS-004` is classed
**INFERENCE / confidence MEDIUM** and reads, verbatim:

> *Locator:* `git diff main --stat` (12→11 model fix, contract-version edits in >10 files,
> 2026-09-22)
> *Observation:* 10+ files edited for count/version drift fixes
> *Interpretation:* Hardcoding machine-owned values in prose causes drift; single-source
> gates are the countermeasure

**So what is actually *observed* versus *inferred*:**
- **Observed (fact):** on 2026-09-22 a hygiene sweep touched 10+ files purely to fix
  count/version drift; e.g. a model count correction 12→11 propagated across many prose
  locations.
- **Inferred (not observed):** that the *mechanism* is "hardcoding machine-owned values in
  prose," and that "single sources are the working countermeasure." Nobody ran a controlled
  test; the agent reasoned from a single cleanup diff.

**Why that makes the requirement `NEEDS_AUTHORITY`:** a requirement built on an inference
needs a human to confirm the *causal* claim, because the evidence shows a *correlation*
(drift happened, and hardcoded values existed) but not the mechanism. The agent correctly
refused to promote an inference to a fact.

**Is the inference sound?** Reading the repository: yes, and it is unusually well
supported in practice. `status_truth.py` *is* the single source for counts and CI fails on
drift; `schema/VERSION.yaml` *is* the single source for versions and `SCH-002` forbids
hardcoded version literals; and `scripts/docs.py` now has a declared-generator mechanism
with drift checks. So the countermeasure is not merely asserted — it is implemented and
gated.

**Recommended verdict: APPROVE, with the evidence class left honestly recorded.**
The requirement describes an operating convention that the repository already follows and
enforces. Approving it does not assert the mechanism is proven — it asserts the convention
is correct and should hold. Keeping `EVID-STEMMA-OPS-004` labelled `INFERENCE` in the
register is the honest record. Optionally, promoting it to `FACT` on the strength of the
implemented single-source gates is defensible — but that is a *separate* edit to the
evidence register, and I would not bundle it into the approval.

**Note on strength:** this is a `SHOULD`, not a `SHALL`. `SHOULD` is the right level: the
convention is a strong default, not an absolute — prose may legitimately need to state a
number in a historical or narrative context.

---

# PART B — RECOMMENDED VERDICTS (the other 19)

All `SUPPORTED` unless noted. "Gate-backed" = the behavior is already enforced and tested
by the verification chain, so approving is confirming an accurate description.

| # | ID | Statement (condensed) | Rec. | Basis |
|---|----|----------------------|------|-------|
| 1 | CORE-001 | Canonical lives only in `content/`, `connections/`, `sources/`; all else regenerable | APPROVE | Gate-backed (EVID-GATE-003, CORE-001) |
| 2 | CORE-002 | IDs match `stemma:` patterns; never reused/reassigned; corrections supersede | APPROVE | Gate-backed (`check_id_immutability`, `test_id_immutability`) |
| 3 | CORE-003 | Canonical SHALL NOT contain embeddings/vectors/RAG artifacts | APPROVE | Gate-backed (CI grep). **Matches your "clean of RAG" direction** |
| 4 | CORE-004 | Canonical SHALL NOT contain curriculum/grade/course/country/product semantics | APPROVE | Gate-backed (`test_generality`) |
| 5 | SCH-001 | Every canonical object validates against its JSON Schema in the gate | APPROVE | Gate-backed (`validate.py`) |
| 6 | SCH-002 | Version literals produced from `schema/VERSION.yaml`; hardcoded forbidden | APPROVE | Gate-backed (`no_version_literals`, docs-consistency) |
| 7 | SCH-003 | Relation registry stays coherent (inverses mirrored, domain/range valid) | APPROVE | Gate-backed (registry coherence) |
| 8 | GATE-001 | Verification chain fails closed; any failed step = non-zero exit | APPROVE | Gate-backed (negative-run observed) |
| 9 | GATE-002 | README status block regenerated from live counts; drift fails CI | APPROVE | Gate-backed (`status_truth.py`) |
| 10 | GATE-003 | CI runs full pytest; all-green requires its success | APPROVE | Gate-backed (`ci.yml`) |
| 11 | GATE-004 | docs-consistency invariant is an executable gate, not prose | APPROVE | Gate-backed (ADR-0029) |
| 12 | GATE-005 | independence invariant is an executable gate, not prose | APPROVE | Gate-backed (ADR-0027/0051) |
| 13 | EXP-001 | Exports deterministic: byte-identical, content-hash stamped, no wall clock | APPROVE | Gate-backed (measured) |
| 14 | EXP-002 | Export contract versioned; additive within major; carries registry/vocab sidecars | APPROVE | Gate-backed (VERSION match) |
| 15 | EXP-003 | Committed derived artifacts fresh; CI regenerates and diffs | APPROVE | Gate-backed (CI freshness diff) |
| 16 | EXP-004 | Exports honor consumer `review_policy` | **APPROVE\*** | See A1 — with amended acceptance criteria |
| 17 | HITL-001 | AI-drafted content stays `draft` until a named human reviews; `writer: human:*` | **APPROVE\*** | See Part D — interacts with your AI-verification plan |
| 18 | HITL-002 | No object canonical without an explicit human markdown edit in the audit trail | **APPROVE\*** | See Part D — audit locality caveat stands |
| 19 | SEC-001 | Canonical layer free of secrets; machine-checked on every change | APPROVE | Gate-backed (gitleaks + grep) |
| 20 | SEC-002 | Provider API keys not committed; runtime config only | **APPROVE\*** | See A2 — verification deferred |
| 21 | OPS-001 | Clean clone runs the full gate after installing declared deps | APPROVE | Gate-backed (MEASUREMENT) |
| 22 | OPS-002 | Living docs don't hardcode machine-owned counts/versions | **APPROVE\*** | See A3 |

\* = requires the corresponding Part A / Part D discussion before approval.

**Count: 22 original — 17 straight APPROVE, 5 needing your explicit ruling** (EXP-004,
HITL-001, HITL-002, SEC-002, OPS-002).

### Added after the SOTA comparison (2026-10-01) — requirements 23 and 24

The SOTA comparison (`spec/SOTA-COMPARISON-2026-10-01.md`) surfaced two requirements the
pilot did not yet record. The owner ruled on both the same day.

| # | ID | Statement (condensed) | Owner ruling | Basis |
|---|----|----------------------|--------------|-------|
| 23 | OPS-003 | Sole-owner approval authority is a recoverable capability, not an undocumented single point of failure | **ADD (F2)** — recorded | SOTA F2; `EVID-OPS-005`; bus-factor research 2026 |
| 24 | INTEG-001 | Reference explorer stays working and gains an AI chat grounded in the export (citations; derived-only) | **ADD (owner-raised)** | `EVID-INTEG-004`; `schema/consumer-registry.yaml` |

**EXP-002 amended (F3, owner ruling "extend it"):** acceptance criteria now also require an
adopted-from provenance record on merged/re-identified entities (revision 2, `EVID-EXP-008`,
OBO Principle 8 precedent).

**Resulting set: 24 requirements.** Owner rulings applied to F1–F5 are recorded in
`SPECIFICATION_PROCESS_REVIEW`-adjacent custody in `spec/SOTA-COMPARISON-2026-10-01.md` §5b.

---

# PART C — ENGINE DEFECT FOUND WHILE PREPARING THIS WORKSHEET

**`scripts/review.py list` crashes on the current corpus.** Verified 2026-10-01:

```
File "scripts/review.py", line 52, in cmd_list
    "target": d["target"],
KeyError: 'target'
```

**Cause:** `conn.000156` is a **value-slot** connection (ADR-0045): it carries `value:` and
has **no `target:` field**. `cmd_list()` reads `d["target"]` unconditionally.

**Why this matters beyond the crash.** This is the *same dormant bug class* that R4
identified and fixed across its consumers — `validate.py`, `graph_analysis.py`,
`check_id_immutability.py`, `relation_triage.py`, `integrity_anomalies.py`,
`export_subsets.py`, and later `curation_status.py`. **`review.py` was missed.**
Cross-checking confirms the pattern: `curation_status.py` uses the defensive
`c.get("target") or (f"value:{c.get('value')}" ...)` form, `validate.py` guards with
`if conn.get("target"):`, and `review.py` does neither.

**Severity: HIGH, and directly on your critical path.** `review.py` is the command-line
review interface — the documented way to move a draft entity to canonical. Your stated
plan is high-volume AI-assisted review; a `list` command that crashes on the corpus it is
meant to summarize is precisely the kind of friction that makes review slow. It also
matters for the spec: `REQ-STEMMA-HITL-001`/`-002` are enforced by `hitl_check.py`, but the
*operator path* to satisfy them is broken in its listing mode.

Note the crash does **not** mean canonicalization is broken — `accept`/`canonicalize` on a
specific ID may still work, and the 7 canonical entities prove the path has worked. But
`list` is how you *find* what to review, so it is the entry point.

**Recommended: fix before (or alongside) approval.** It is a small, well-understood change
(mirror the `curation_status.py` defensive form in `cmd_list` and `cmd_show`), and it
should be test-pinned so the value-slot case cannot regress — exactly as R4 pinned its
sibling fixes.

---

# PART D — HITL UNDER YOUR AI-ASSISTED VERIFICATION PLAN

**Your direction (2026-10-01), recorded:**
- Keep it **HITL**. The owner remains the approver.
- **Document that contributors will not be accepted for some time.**
- The owner will verify content as HITL **using AI, deliberately**: AI does verification
  and re-verification **alongside reading books/sources** so verification is *faster* —
  not "AI does everything and you check at the end," though you note that variant could
  also work.
- Framing: **human-directed, AI-assisted** — the human directs and remains accountable.

**Why this is coherent with HITL-001 as written.** `HITL-001` requires that content stay
`draft` until a **named human** reviews it, and that canonical objects declare
`writer: human:*`. Nothing in that forbids AI performing verification *work*; what it
forbids is a machine being *recorded as the human authority*. Your model keeps
`human:curator.001` as the accountable writer/reviewer while AI accelerates the
verification labour that informs the owner's decision. That is consistent.

**What would need writing down (a follow-up, not this approval):**

1. **`CURATION-PROTOCOL.md`** — a section defining the AI-assisted verification role: what
   AI may assert, what it must escalate, how its output is recorded, and the explicit
   statement that the *human* remains the authority of record.
2. **A contributors-not-accepted-yet statement** — where? `CONTRIBUTING.md` is the natural
   home (it is the file a would-be contributor opens first). This is a real governance
   position, not a temporary disclaimer, and should read as deliberate.
3. **`UNRES-STEMMA-HITL-001` (audit locality)** — still open, and now more pointed. The
   audit trail is git-ignored, so a fresh clone cannot verify HITL. Under a
   single-owner + AI model this is *less* urgent (no third party needs to verify it yet),
   but it becomes a blocking issue the moment contributors are accepted — which is exactly
   what (2) defers. Worth recording that link explicitly: *the contributors-not-accepted
   policy is what makes the unverifiable audit trail acceptable for now.*

**Recommended verdict: APPROVE HITL-001 and HITL-002 as written**, because they accurately
describe the mechanism that exists and runs today, and your AI-assisted model does not
contradict them. Then make the AI-verification design a **separate, deliberate change**
(new ADR + `CURATION-PROTOCOL.md` + `CONTRIBUTING.md`), so the specification keeps
describing reality at every step rather than describing an intention.

This follows the same principle as A1: **approve what is true today, change what is not.**

---

# PART E — WHAT HAPPENS AFTER VERDICTS

1. I set each record's `status` (`APPROVED` / `REJECTED` / `DEFERRED`) and
   `approver: human:curator.001` in `spec/machine-readable/requirements.yaml`.
2. Update `spec/REQUIREMENTS.md` (mirror + status column) and `spec/BASELINE.md`
   (`PENDING` → approved, maturity L2 → **L3**).
3. Run `spec/machine-readable/validate_recovery.py` — the approval-metadata checks
   (checks 6–7) then exercise the APPROVED path for the first time.
4. Record closures: `UNRES-STEMMA-EXP-001` (per A1); note the remaining `UNRES` records.
5. **L4 (verified) becomes unblocked** — verification executions can begin from
   `spec/VERIFICATION.md`. This is the real prize: it converts the spec from "we described
   it accurately" into "we can prove it."

Total requirement count: **22** (unchanged). Nothing in this worksheet adds, removes, or
renumbers a requirement.
