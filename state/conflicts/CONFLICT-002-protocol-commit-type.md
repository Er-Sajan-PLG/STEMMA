# CONFLICT: CONFLICT-002-protocol-commit-type

**Raised by:** `A7F3`
**Date:** 2026-10-01
**Status:** **RESOLVED**

---

## The question

MACP §Shutdown step 6 **mandates** the commit format:

```
git commit -m "state: <agent-id> session <session-id>"
```

This repository enforces Conventional Commits via `commitlint.config.cjs`, and
`Conventional Commits (commitlint)` is one of the **seven required status checks** on `main`.
Its `type-enum` did not include `state`:

```
[feat, fix, docs, style, refactor, perf, test, build, ci, chore, revert, merge]
```

So following the protocol produced a commit that fails a required check and blocks the PR.
The protocol also says it wins over conflicting instructions — but "winning" by breaking a
required gate would block the merge, which is not a resolution.

Observed: CI run `36859282799` — `Conventional Commits (commitlint)` **fail**,
`✖ type must be one of [...]`, on commit `8d4d74a`
(`state: A7F3 session 20261001-1153-A7F3-debt-cleanup`).

## Position A — `A7F3`: add `state` to the type enum

The protocol is now the governing convention for coordination-state commits in this
repository, and the owner directed it be followed. A gate that rejects the protocol's
mandated commit format makes the protocol unusable as written: every future shutdown commit
would either fail the required check or force a history rewrite, and agents would drift to
whatever message happens to pass.

Adding a type is additive, and this repository has precedent — `merge` is already a
repository-specific addition to the conventional list.

## Position B — the counter-argument, stated fairly

Bending a lint policy to fit a commit message is the kind of move that quietly weakens a
gate. The alternative is to keep the gate as-is and have MACP commits use a conventional
type, e.g. `chore(state): A7F3 session <id>`. That preserves the lint list untouched and
still conveys the same information.

## Resolution

**Add `state` to the type enum.** Reasons, in order of weight:

1. The protocol's format is **owner-specified**, and the owner directed that it be followed.
   Deviating on every session would be a silent, permanent divergence from an explicit
   instruction — worse than a one-word config change.
2. The change is **additive and narrow**: it admits one new type; it does not relax any
   existing rule (subject case, line lengths, and the rest are untouched). Verified with a
   negative control — a bogus type still fails, and every pre-existing subject still passes.
3. The repo already extends the list (`merge`), so this is the established pattern rather
   than a new precedent.
4. It resolves the already-pushed commit `8d4d74a` **without rewriting history**, which
   matters because the protocol also says tags and history are not to be moved lightly.

**Also recorded as** `DEC-006`.

## Why this is a standing invariant, not a spent disagreement

§4 **Phase D** says a resolved conflict moves to `archive/`. That step was **not** applied,
for the same reason as `CONFLICT-001` — and this case makes the reasoning sharper.

This is not a disagreement that is over once settled. It is a **live coupling**: if someone
later removes `state` from `type-enum`, every future MACP shutdown commit breaks a required
check, silently and at a distance from the change that caused it. The resolution therefore
has to stay discoverable, and `commitlint.config.cjs` points here from an inline comment.

To keep it from being documentation-only, `tests/repo/test_state_tree.py` now **asserts**
that the commitlint `type-enum` accepts the protocol's commit type. Removing `state` from the
enum turns that guard red, so the invariant is enforced rather than merely written down.

**Proposed refinement to MACP (owner review, restated from CONFLICT-001):** Phase D should
distinguish a *spent disagreement* (archive it) from a *standing invariant* (keep it live,
mark `RESOLVED`). Two independent cases have now hit this distinction, which is weak evidence
the protocol text is ambiguous here rather than that the agent is reading it loosely.
