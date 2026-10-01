# MACP — Multi-Agent Coordination Protocol

**Version 1.1** — original text (v1.0) plus **Amendment 1**, appended at the end of this file.

> **Canonical protocol text for this repository.** v1.0 was supplied by the owner
> (`human:curator.001`) on **2026-10-01**, replacing an earlier partial transcription.
> **Amendment 1** (sections A1–A7) was incorporated the same day from an owner-supplied
> review of proposals P1–P7, which accepted six of the seven *with refinements* — those
> refinements are part of the adopted text, not commentary on it.
>
> An earlier revision of this file was written from a **truncated** copy of the protocol
> and reconstructed the missing Section 7. That reconstruction is **superseded**: it got
> the agent-ID format, the session filename convention, the purpose of `INDEX.md`, and the
> plan lifecycle wrong. This file is now the authoritative text.
>
> **Amendments are additive.** v1.0's sections are left exactly as supplied. Where an
> amendment and an original section disagree, the amendment wins — recorded as `DEC-008`.

---

## The Problem

- Context compaction destroys agent memory
- Agents work in silos, unaware of each other
- Decisions get lost in chat history
- Conflicts emerge when agents make contradictory assumptions
- No shared understanding of project state

## The Solution

A **protocol** where the repository itself is the shared memory. All agents read from and
write to the same structured state directory. The repo is the source of truth — not any
agent's context window.

## The Core Principle

**The repository IS the shared memory.**

---

# THE PROTOCOL

## SECTION 0: AGENT REGISTRATION

Every agent must register before working:

```
agent_id: <your-id>              # e.g., "claude-code", "codex", "gemini", "human-curator"
session_id: <unique-session-id>  # e.g., "2026-01-15-refactor-auth"
started_at: <ISO timestamp>
task: <what you intend to do>
files_owned: [<files you will write>]
status: active
```

Register in `state/REGISTRY.md`.

---

## SECTION 1: KNOWLEDGE MANAGEMENT (THE REPO-AS-MEMORY)

### Rule 1: The repo is the single source of truth

If it's not in the repo, it doesn't exist. Chat history, agent context, and human memory
are all unreliable.

### Rule 2: Session files are append-only logs

`sessions/*.md` are append-only. Never edit a previous session's log. Add new entries at
the end.

### Rule 3: DASHBOARD is current state, not history

`DASHBOARD.md` shows what IS, not what happened. History lives in sessions.

### Rule 4: Decisions are immutable

Once a decision is in `DECISIONS.md`, it's permanent. To change it, add a NEW decision that
supersedes it. Never edit old decisions.

### Rule 5: Conflicts block progress

If two agents disagree, work stops until resolved. Record in `conflicts/`.

### Rule 6: Always end clean

Before ending a session:

- Update `DASHBOARD.md`
- Log to `sessions/`
- Release `files_owned` in `REGISTRY.md`
- Commit all state changes

**NEVER leave uncommitted changes.**

---

## SECTION 2: FILE STRUCTURE

### Directory Structure

```
state/
├── DASHBOARD.md          # Current project state (single source of truth)
├── REGISTRY.md           # Active agents + files owned
├── INDEX.md              # Searchable log of all past sessions
├── ARCHITECTURE.md       # Stable system understanding
├── DECISIONS.md          # Immutable decision log
├── DEBT.md               # Known problems, accumulated debt
├── BLOCKERS.md           # Things preventing progress
├── sessions/             # Per-session append-only logs
│   ├── YYYYMMDD-HHMM-<AGENT-ID>-<short-slug>.md
│   └── ...
├── plans/                # Active plans (deleted when done)
│   ├── agent-<AGENT-ID>-<slug>.md
│   └── ...
├── conflicts/            # Unresolved disagreements
│   ├── CONFLICT-<NNN>-<slug>.md
│   └── ...
└── archive/              # Old sessions compressed by month
```

### File Purposes

| File | Purpose | Owner | Update Frequency |
|------|---------|-------|------------------|
| `DASHBOARD.md` | Current state of everything | Any agent | Every session |
| `REGISTRY.md` | Who's working on what | Each agent (own row) | Start/end of session |
| `ARCHITECTURE.md` | How the system works | Any agent | When understanding changes |
| `DECISIONS.md` | Why we chose X over Y | Any agent (append-only) | When decisions are made |
| `DEBT.md` | What's broken or suboptimal | Any agent | When debt is found |
| `BLOCKERS.md` | What's stopping progress | Any agent | When blockers appear |
| `sessions/*` | What happened in each session | Owning agent | End of session |
| `plans/*` | Multi-step coordination | Plan owner | When plans change |
| `conflicts/*` | Unresolved disagreements | Conflict raiser | Until resolved |

### Critical: Write Isolation During Work

**During work, write ONLY to your own session file.** Do not touch `DASHBOARD.md`,
`REGISTRY.md`, or `INDEX.md` while working — they are updated at shutdown. This prevents
write conflicts between concurrent agents.

Your session file is your scratchpad AND your log. Use it heavily. Structure entries with
**event tags** so they are greppable:

```
[START]     session beginning, intended work
[PROGRESS]  meaningful advance (not every command)
[DISCOVERY] something learned that changes understanding
[PIVOT]     direction change + why
[DECISION]  a choice made + rationale
[BLOCKER]   something preventing progress
[COORDINATION] interaction with another agent
[DEBT]      technical debt noticed
[BUG FOUND] defect discovered
[SECURITY]  security-relevant finding
[SCOPE EXPANSION] work grew beyond the original task
[DISCREPANCY] plan vs reality mismatch
```

---

## SECTION 3: MEMORY PROTOCOL

### Startup Sequence

When starting work, an agent MUST:

1. **Read** `state/DASHBOARD.md` — current project state
2. **Read** `state/REGISTRY.md` — who else is working
3. **Read** `state/INDEX.md` — navigate to relevant files
4. **Check** `state/BLOCKERS.md` — anything stopping me?
5. **Check** `state/conflicts/` — unresolved disagreements?
6. **Read** relevant `state/plans/` — what's the current plan?
7. **Read** relevant `state/sessions/` — what happened recently?
8. **Verify** understanding against actual code
9. **Register** in `state/REGISTRY.md`

### Maintenance

- Update `DASHBOARD.md` after significant changes
- Append to session log continuously
- Record decisions immediately
- Record debt immediately
- Record blockers immediately

### Session End

- Update `DASHBOARD.md`
- Append to session log
- Release `files_owned` in `REGISTRY.md`
- Commit

---

## SECTION 4: CONFLICT PROTOCOL

### When agents disagree

**Phase A — Detection:** Any agent can raise a conflict. Record it in
`state/conflicts/<id>.md`.

**Phase B — Documentation:** Document BOTH positions with evidence. No resolution yet.

**Phase C — Resolution:**

- If evidence is clear, the agent with better evidence wins
- If not, escalate to human
- Record resolution in `conflicts/<id>.md` AND `DECISIONS.md`

**Phase D — Archive:** Move resolved conflict to `state/archive/`.

### Conflict File Format

```markdown
# CONFLICT: <id>

**Raised by:** <agent-id>
**Date:** <ISO date>
**Status:** OPEN | RESOLVED | ESCALATED

## Position A
<agent-id>: <claim + evidence>

## Position B
<agent-id>: <claim + evidence>

## Resolution
<how it was resolved, or "ESCALATED TO HUMAN">
```

---

## SECTION 5: PLANNING PROTOCOL

### When to create a plan

Create a plan in `state/plans/` when:

- Work spans multiple sessions
- Multiple agents are involved
- The approach is non-obvious
- The work is complex enough to lose track

### Plan File Format

```markdown
# PLAN: <name>

**Owner:** <agent-id>
**Status:** ACTIVE | COMPLETE | ABANDONED
**Created:** <ISO date>

## Goal
<what we're trying to achieve>

## Steps
1. [ ] <step>
2. [ ] <step>

## Agents Involved
- <agent-id>: <role>

## Current State
<where we are now>
```

---

## SECTION 6: SESSION START PROTOCOL

Every session begins with:

1. **Read** `state/DASHBOARD.md`
2. **Read** `state/REGISTRY.md`
3. **Check** for conflicts
4. **Check** blockers
5. **Read** current plan
6. **Register** self
7. **Create** session file
8. **Verify** against code
9. **Begin** work

> **Only after all 9 steps are complete** may you begin actual work.

---

# MANDATORY SESSION STARTUP SEQUENCE

## Step 1: Git Reconnaissance

```bash
git status
git log --oneline -20
git branch -a
git diff HEAD~5 --stat
```

**Checklist:**

- [ ] Current branch identified
- [ ] Recent commits understood
- [ ] Uncommitted changes noted
- [ ] Other branches/agents detected

**If uncommitted changes exist:** Determine if they are yours or another agent's. If
another agent's, **DO NOT TOUCH THEM**. Record in your session file and work around them.

## Step 2: Check state/ exists

If `state/` does not exist → run the **Bootstrap Protocol (Section 7)** first.

## Step 3: Read DASHBOARD.md

```bash
cat state/DASHBOARD.md
```

**Critical:** Check the **"Last Reconciled"** timestamp at the top.

- If `< 24 hours` → state is trustworthy, proceed
- If `24–48 hours` → state may be stale, verify key claims
- If `> 48 hours` → **state is STALE**. You MUST reconcile before working.

## Step 4: Read REGISTRY.md

```bash
cat state/REGISTRY.md
```

**Checklist:**

- [ ] Are other agents active?
- [ ] Do their `files_owned` overlap with mine?
- [ ] If overlap → coordinate or pick different work

**Ownership rules:**

- Only ONE agent may write to a file at a time
- If you need a file another agent owns → coordinate or wait
- `state/` files are shared: append-only or clearly sectioned

## Step 5: Check BLOCKERS.md

```bash
cat state/BLOCKERS.md
```

If anything blocks your task, STOP and address it first.

## Step 6: Targeted History

Do **NOT** read all sessions. Use `INDEX.md` to find relevant ones:

```bash
cat state/INDEX.md
# Read only the 2-3 sessions relevant to your task
```

## Step 7: Read ARCHITECTURE.md (if needed)

Read when:

- Working on unfamiliar code
- Architecture may have changed
- You need to understand system boundaries

Also check `state/DECISIONS.md` for decisions affecting your work.

## Step 8: Register Yourself

Append to `state/REGISTRY.md`:

```markdown
| <AGENT-ID> | <session-id> | <ISO-timestamp> | <task description> | <files_owned> | active |
```

Then create your session file:

```bash
touch state/sessions/YYYYMMDD-HHMM-<AGENT-ID>-<slug>.md
```

**Choose an agent ID:** 4 alphanumeric characters. Be memorable. Example: `C7A2`

## Step 9: Create Plan Entry (if multi-step)

If your work requires multiple steps, create:

```bash
touch state/plans/agent-<AGENT-ID>-<slug>.md
```

Use the plan template from Section 5.

> **Only after all 9 steps are complete** may you begin actual work.

---

# VALIDATION

Before marking work complete, verify:

- [ ] All changes are on disk (not just planned)
- [ ] Tests pass (if applicable)
- [ ] No debug code or temporary files left behind
- [ ] Documentation updated if behavior changed
- [ ] Session file is complete and accurate
- [ ] `DASHBOARD.md` reflects current reality

---

# SHUTDOWN SEQUENCE

When finishing work:

## 1. Update Session File

Ensure all work is logged with event tags.

## 2. Update DASHBOARD.md

- Update **"Last Reconciled"** timestamp
- Update current state to reflect reality
- Do NOT include history

## 3. Update INDEX.md

Add an entry for your session:

```markdown
| YYYYMMDD-HHMM | <AGENT-ID> | <date> | <title> | <files-touched> | <status> | <branch> |
```

## 4. Release Your Files

Update your row in `REGISTRY.md`:

- Set `status: ended`
- Clear `files_owned`

## 5. Clean Up Plan

If your plan is complete, **delete your plan file**.

## 6. Commit

```bash
git add state/
git commit -m "state: <agent-id> session <session-id>"
```

## 7. Reconciliation (only if you were the last active agent)

If no other agents are active:

- Verify DASHBOARD matches reality
- Check for orphaned plans
- Archive old sessions (> 30 days) to `archive/`

---

# CONFLICT HANDLING

If you discover another agent's work contradicts yours:

## 1. STOP immediately

Do not overwrite or "fix" their work.

## 2. Document the conflict

```bash
cat > state/conflicts/CONFLICT-<NNN>-<slug>.md << 'EOF'
# CONFLICT: <NNN>-<slug>

**Raised by:** <your-agent-id>
**Date:** <ISO date>
**Status:** OPEN

## Position A
<agent-id>: <claim + evidence>

## Position B
<agent-id>: <claim + evidence>

## Resolution
PENDING
EOF
```

## 3. Notify via session file

Log the conflict in your session file.

## 4. Wait or escalate

- If the other agent is active → coordinate
- If unclear → escalate to human
- If you must proceed → pick non-conflicting work

---

# ANTI-PATTERNS (DO NOT DO)

❌ **Editing another agent's session file** — append-only, yours only
❌ **Deleting another agent's work** — even if it looks wrong
❌ **Working without registering** — invisible agents cause conflicts
❌ **Leaving uncommitted state** — state must always be committed
❌ **Writing history into DASHBOARD** — history goes in sessions
❌ **Reading all sessions** — use INDEX.md for targeted history
❌ **Editing old decisions** — add a new one that supersedes
❌ **Silent failures** — log everything with event tags

---

# SECTION 7: BOOTSTRAP PROTOCOL

If `state/` does not exist:

## 1. Perform a FULL REPOSITORY AUDIT

- Language(s) and frameworks used
- Entry points and build system
- Test framework and how to run tests
- Existing documentation (README, docs/)
- CI/CD configuration (`.github/workflows/`)
- Directory structure and purpose of each top-level dir
- Existing conventions (linting, formatting, commit style)
- Current state of the codebase (working? failing tests?)
- Dependencies and how they're managed

## 2. Create the structure

```
state/
├── DASHBOARD.md
├── REGISTRY.md
├── INDEX.md
├── ARCHITECTURE.md
├── DECISIONS.md
├── DEBT.md
├── BLOCKERS.md
├── sessions/
├── plans/
├── conflicts/
└── archive/
```

## 3. Populate from audit

- `ARCHITECTURE.md` ← full system understanding from the audit
- `DASHBOARD.md` ← current state + today's date as "Last Reconciled"
- `INDEX.md` ← note "Bootstrap: no prior sessions"
- `DEBT.md` ← issues found during audit
- `BLOCKERS.md` ← anything blocking

## 4. Commit

```bash
git add state/
git commit -m "chore(state): bootstrap MACP protocol with repository audit"
```

## 5. Register yourself and begin normal session flow

---

# QUICK REFERENCE

| Action | File |
|---|---|
| What's the current state? | `state/DASHBOARD.md` |
| Who's working on what? | `state/REGISTRY.md` |
| What happened before? | `state/INDEX.md` → `sessions/` |
| Why was this built this way? | `state/DECISIONS.md` |
| How does the system work? | `state/ARCHITECTURE.md` |
| What's broken? | `state/DEBT.md` |
| What's stuck? | `state/BLOCKERS.md` |

---

# HOW TO USE THIS PROTOCOL

**For a new agent:**

1. Read this protocol completely
2. Run the **Mandatory Session Startup Sequence** (9 steps)
3. Work, logging to your session file with event tags
4. Run the **Shutdown Sequence** (7 steps)

**For a human:**

- `DASHBOARD.md` is your status report
- `sessions/` is your audit trail
- `BLOCKERS.md` is what needs your attention
- `DECISIONS.md` is the architectural record

---

# SCOPE AND AUTHORITY

This protocol governs **coordination state** — the files under `state/`. It does not, and
must not, govern the project's specification.

| Tier | Files | Authority |
|---|---|---|
| **1 — coordination** | everything under `state/` | Agents may write freely. |
| **2 — specification** | `content/`, `connections/`, `sources/`, `spec/`, and every requirement status | **Owner only** (`human:curator.001`). |

In STEMMA, Tier 2 is governed by `spec/ROLES_AND_AUTHORITY.md` **Constraint D**: the
executor may run work and record results but may **not** approve, reject, or defer a
requirement, close a `UNRES-` record, or promote an `INFERENCE` to a `FACT`.

`state/DECISIONS.md` records *coordination* decisions and must never restate, replace, or
paraphrase a specification ruling — link to it instead. `state/` is never cited as evidence
in `spec/`. See `state/conflicts/CONFLICT-001-state-tier2-boundary.md`.

**Acknowledge you have read and understood this protocol before beginning any task.**

---

# AMENDMENT 1 (protocol v1.1) — verified shutdown, ownership, and record integrity

**Status:** incorporated 2026-10-01 from an owner-supplied review of proposals P1–P7, which
accepted six of seven **with refinements**. The refinements below are the adopted text.
**Applies to:** v1.0 §3 (validation), §Shutdown, §5 (plans), §1 (rules), §6 step 8.
**Supersedes:** nothing — this is additive. Where it disagrees with v1.0, it wins (DEC-008).

## Why this amendment exists — the unifying diagnosis

Every v1.0 section specified **actions** without **verifications**. That is why records rot:
nothing ever checked the record against reality. Six of the seven proposals close exactly one
feedback loop each:

| Amendment | Loop closed |
|---|---|
| A1 | "finalized" claim ↔ actually having stopped |
| A2 | shutdown summary ↔ repository reality |
| A3 | `COMPLETED` status ↔ work continuing |
| A4 | an event occurring ↔ the file that should record it |
| A5 | a written claim ↔ its reproducibility |
| A6 | the session file ↔ git truth |

> **Principle: every assertion needs a verifier, every state needs a transition, every file
> needs an owner.** v1.0 was an honour system; this amendment makes it a verified system.

---

## A1 — Shutdown Step 0: stop working first

**Before the shutdown sequence, explicitly STOP WORKING.**

Any new finding **aborts** the shutdown: return to work, then restart the shutdown from step 0.
Abort-and-restart is the only correct semantic — "update the summary too" would normalise the
drift.

**Scope — what aborts and what does not.** "Any new finding aborts" is too strict; a typo in
your own prose should not restart a shutdown:

| Aborts the shutdown | Does NOT abort |
|---|---|
| any code change | a typo or formatting fix in the session file currently being finalised |
| any config change | formatting of the shutdown summary itself |
| any state-file change **other than** the session file being finalised | |
| any new commit touching repo content | |

**Cap: 3 shutdown restarts per session.** On the fourth, halt, log `[NEEDS HUMAN]` in
`BLOCKERS.md`, and set the session outcome to `PARTIAL`.

**Root-cause rule (extends §2):** declare completion **only** when all plan items are checked
off **and** §3 validation passes. **User satisfaction is not a completion signal.** An agent
must not answer "done" because the user asked "are you done?".

**Interaction with A3:** a **mid-shutdown abort is not a re-open**. A re-open applies only
after a shutdown has *fully completed* and `REGISTRY.md` was set to `COMPLETED`.

---

## A2 — Terminal verification loop

After shutdown completes, verify the record against reality, in a loop:

1. Re-read the record and check it against the repository (see "what re-read means" below).
2. If there are discrepancies, **classify** them — this is the part v1.0's "fix it" would
   have got wrong:
   - **Record error** — the record is wrong, reality is fine → fix the record, re-verify.
   - **Reality error** — the work itself is wrong or incomplete → fix the work. That means
     re-entering work mode, which means **A1 aborts the shutdown**. Say so explicitly rather
     than quietly resuming.
3. Repeat. **Cap: 3 iterations.** Each iteration strictly reduces the discrepancy set for a
   finite set of discrepancies, so the loop terminates; new discrepancies appearing is itself
   a signal of deeper rot.

**If three iterations do not converge:** record it in `BLOCKERS.md` **and** set the session
outcome to `PARTIAL` or `FAILED` — **not** `COMPLETED`. A non-converging verification loop
means the session did not complete, regardless of what shipped.

**What "re-read" means (minimum):**

- `git log <base>..HEAD --oneline` — every commit appears in the session file's commit list.
- `git status` — clean.
- `DASHBOARD.md` active-agent note ↔ `REGISTRY.md` rows — they match.
- Every claim in the session summary is checkable (per A5).

**Forbidden inside the loop:** starting new work. Verification that turns into more work
falsifies the thing being verified.

**Non-negotiable pairing with A4.** Without ownership rules the loop finds rot and does not
know whose job it is. Ship them together.

---

## A3 — Re-open transition

`COMPLETED → ACTIVE` is a **legal transition**, but only explicitly:

- It requires a dated `Re-opened: <reason>` entry in the session file, so a reader can explain
  why the session has non-linear timestamps.
- **Full shutdown must be re-executed afterward.** No half-reopening.

**Decision rule — re-open the same session, or start a new one?** Without this, agents pick
arbitrarily, which defeats the purpose:

| Re-open the same session | Start a new session |
|---|---|
| continuing the same objective | a new objective |
| the same calendar day | the next day |
| no other agent worked in between | another agent's session is interleaved |

**The reason field must record:** (1) what triggered the reopen — user request, self-review,
cold-read finding, or new discovery; (2) why it could not wait for a fresh session; (3) the
delta from the "completed" state. "Forgot to add tests" is not an audit trail.

**Mandatory git check on reopen:** run `git fetch`, and compare against the previous session's
commit list. If the branch diverged — merged, or others committed — resolve that **before**
proceeding.

---

## A4 — State-file ownership table

Ownership is **event-driven**, not periodic. "Update `ARCHITECTURE.md` periodically" is vague
and skippable; "`ARCHITECTURE.md` MUST be updated when structure changes" is triggered and
checkable. Ownerless files rot — that is the predicted outcome, not an accident.

**Definition of an event:** anything that would make an existing claim in a state file become
**false or incomplete**. Self-referential, but testable.

| Event | Files that MUST be updated in the same session |
|---|---|
| Structural change (module/dir added, removed, moved) | `ARCHITECTURE.md`, session |
| Dependency added / removed / upgraded | `ARCHITECTURE.md` (if the stack changed), `DEBT.md` (if risk changed), session |
| Test suite restructured | `ARCHITECTURE.md`, session |
| CI/CD configuration changed | `ARCHITECTURE.md`, session |
| Environment variable added | `ARCHITECTURE.md`, session |
| Public API changed | `ARCHITECTURE.md`, `DECISIONS.md` (if breaking), session |
| Security-relevant change | `DECISIONS.md`, session |
| An ADR / decision is created | `DECISIONS.md`, session |
| A defect or limitation is found | `DEBT.md`, session |
| Something becomes blocked | `BLOCKERS.md`, session |
| A generated artifact is added or removed | `ARCHITECTURE.md`, session |

**Meta-rule: this table is incomplete by design.** When an event occurs that no row covers,
**add a row** as part of the shutdown.

**All triggered files must be updated in the session that produced the event. A partial update
is a failure**, not a partial success.

---

## A5 — Reproducible claims (a principle, not a ban)

> **Principle.** Any claim in a record must be either **(a)** a durable historical fact that
> cannot change, or **(b)** a current-state claim **paired with the command and timestamp that
> would reproduce it**. Unverifiable assertions rot.

**Why a principle and not a ban.** A ban on counts produces *protocol-compliant mush*: agents
stop writing anything concrete to avoid violation, and the record becomes technically valid
and informationally dead. Lead with the principle; the rules below are applications.

**Counts** are permitted as **deltas or historical markers** — "+30 tests this session", "at
session start: 1100 passing". They are forbidden as **current-state claims** without the
verification suffix — "we have 1130 passing tests".

**Timestamps — two kinds, two rules:**

| Kind | Example | Rule |
|---|---|---|
| **Action** timestamp | "Decision made at 15:30 UTC" | Always allowed — a durable historical fact. |
| **State** timestamp | "DASHBOARD current as of `abc123`, verified via `git log -1`" | Requires the verification context. A bare state timestamp is freshness evidence only if nothing has happened since. |

**Positive form:** when you reference a count or a state, cite the command that produced it, so
a later reader can re-verify instead of trusting.

---

## A6 — Record verification in §3, and the session-file header schema

Add to the §3 validation checklist:

- [ ] The session file's commit list is complete (`git log <base>..HEAD --oneline`).
- [ ] Statuses are current — no stale `IN-PROGRESS` markers.
- [ ] No checked-off plan item describes unfinished work.
- [ ] The session file header matches `REGISTRY.md`.

**Session-file header schema (required, and mechanically checkable).** Every session file MUST
begin with this metadata block:

```
**Agent:** <AGENT-ID>
**Session ID:** <YYYYMMDD-HHMM-<AGENT-ID>-<slug>>
**Started:** <ISO-8601 UTC>
**Status:** active | ended
**Branch:** <branch>
**Base commit:** <short sha this session started from>
**Task:** <one line>
**Files owned:** <paths, or — >
```

These fields MUST match the agent's row in `REGISTRY.md`. Without a schema, "matches REGISTRY"
is unenforceable.

*(Aspirational, not required: a **cold** re-read after a context break catches more than an
immediate one — the author of a file is its worst reader. The checklist is the enforceable
floor.)*

---

## A7 — Machine-checked drift: DEFERRED

**Not adopted yet.** The sequencing argument is accepted: **discipline fixes precede
mechanical ones.** Tooling that enforces undisciplined behaviour produces compliant-looking
rot — suppression becomes the goal and the suppressed problem persists.

Defer until A1–A6 have run for a non-trivial period, so any checker encodes **observed residual
failures** rather than guesses about them.

**Constraints if it is ever implemented:**

- A **completeness** checker (did you touch the required files?), **not** a correctness
  checker — correctness is not mechanically decidable.
- Pre-commit hooks must **warn, not block**. Blocking enforcement belongs in CI. A blocking
  pre-commit hook trains agents to `--no-verify` reflexively, or to write minimal records that
  satisfy the hook — both worse than no hook.

---

## Known gaps (next-batch backlog)

Not addressed by A1–A6. Recorded here so they are not lost:

1. **Context-window pressure.** Record quality degrades first when context runs short, and
   there is no "stop and hand off cleanly" rule.
2. **User-induced protocol violation.** When the user says "skip the protocol, just do X", the
   protocol is silent — so agents comply silently, which is the worst of the three options
   (refuse / comply / comply-and-document).
3. **Protocol version drift.** If this file or `AGENTS.md` changes mid-session, the agent is
   operating under a different protocol than it started with. No rule covers that.
4. **The "boring update" skip.** For a one-line fix, agents will skip state updates as
   disproportionate, and then fail to re-engage for substantial work. Needs a **minimum viable
   session record** for small changes.

**Acknowledge you have read and understood this protocol, including this amendment, before
beginning any task.**
