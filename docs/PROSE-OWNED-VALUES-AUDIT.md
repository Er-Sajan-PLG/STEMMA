# Per-release audit — prose-owned machine values (REQ-STEMMA-OPS-002)

Owner ruling 2026-10-01 (option (a) of `spec/UNVERIFIED-DECISIONS.md` §2): a
documented per-release audit is the measurement instrument for `OPS-002`, and the
trend starts at **`v3.0.0`** as its first data point. This file is that
instrument's record. `REQ-STEMMA-OPS-002` therefore **remains `UNVERIFIED`** —
correctly — until a second release completes the pair.

## Instrument

`scripts/audit_prose_owned_values.py` (offline, read-only; reads the local git
object store only).

It measures one thing per revision: how many prose locations restate a
machine-owned **count** as a live value.

```
python3 scripts/audit_prose_owned_values.py --all-tags --summary
```

Machine-owned counts are read from the generated README status block, which
`status_truth.py` writes and the `status_truth` gate enforces — so the block is
the single source's own echo, not a second source to drift from.

## First data point — `v3.0.0`

| Revision | machine-owned counts | prose count-mentions | naive "stale" matches |
|---|---|---|---|
| `v3.0.0-rc1` | 9 entities / 2 connections / 3 sources | 202 | 187 |
| `v3.0.0-rc2` | 9 / 2 / 3 | 204 | 189 |
| `v3.0.0-rc3` | 9 / 2 / 3 | 204 | 189 |
| `v3.0.0-rc4` | 9 / 2 / 3 | 204 | 189 |
| **`v3.0.0`** | **9 / 2 / 3** | **204** | **189** |

`v3.0.0` is the first data point of the trend.

## What the instrument cannot do — recorded deliberately

The raw "stale" figure is **not** a defect count, and treating it as one would be
dishonest. Inspecting all 189 matches at `v3.0.0` shows they are overwhelmingly
numbers that are **not** restatements of the live count:

- **Plans and targets** — "400-800 entities across 8 domains", "grow from 1 entity
  to 400-800", "3-5 entities". A target is not a claim about the present.
- **Different quantities sharing a word** — "12 entity **types**",
  "`reports/entity-review-campaign/batch-01.md`: 5 entities" (a batch size),
  "6 entities have no connections" (an anomaly subcount).
- **Ordinal / scale references** — "10^4 entities", "10^5–10^6 entities".
- **History** — "old 74 entities archived", "0 entities after reset". Precisely
  the dated-snapshot form that *should* be preserved.
- **Gate prose** — `docs/TESTING.md:18` quotes live tool output verbatim inside a
  code block, which is a transcript, not a claim.

So the honest finding is: **a count mention in prose does not by itself indicate
drift, and no purely mechanical instrument can separate a stale live claim from a
legitimate target, type-name, subcount, or historical datum.** The one genuine
instance of the drift this requirement targets was found by *reading*, not by this
script — `spec/APPROVAL-WORKSHEET.md` carried "7 canonical entities" as a live
claim in three places after the corpus moved to 1 canonical. It has been converted
to a dated snapshot.

The instrument's real value is therefore narrower and still useful: it is a
**bounded review surface**. 204 locations at `v3.0.0` is a number a reviewer can
work through at the next release; the delta between that number and the next
release's is the trend `OPS-002` asks about. What changes across releases is what
matters, not the absolute figure.

## Consequence for the requirement

`OPS-002` stays `UNVERIFIED`. Nothing here is evidence of a *trend*, because there
is exactly one release point. When a second release is tagged:

1. run the instrument at the new tag,
2. compare the two rows,
3. if the prose-count surface shrank (or held while the corpus grew), the trend is
   established and `OPS-002` can be verified mechanically against this file.

`EVID-STEMMA-OPS-004` is class **INFERENCE** and is **not** promoted to FACT;
Constraint D reserves that to owner review.
