# Golden — smoke-update-revert-default (C3, F3 regression guard)

The prior spec contains two deliberately ugly Problem-Statement
sentences (typos + awkward gerund-heavy phrasing). The user asks for
ONE new AC (`AC-04` under FR-03). The post-F3 drafter must REVERT
the ugly sentences byte-for-byte rather than silently polishing
them — polish does not clear the per-statement value gate.

## What is asserted (positive)

- Bait sentences survive verbatim, typos and all:
  - `Workspace memebers miss important changes accross squads`
  - `the scrolling of individual channels in order to be finding
    what matters is taking too much of the time`
- `edit-audit-json.counts.add >= 1`,  `counts.modify == 0`.
- Exactly one edit-audit entry whose locator references `AC-04`
  (or `AC-4`).
- No edit-audit entry whose locator references Problem Statement.

## What is asserted (negative-control)

- The "polished" forms must NOT appear:
  - `Workspace members miss important changes across squads`
  - `Scrolling individual channels to find what matters takes too long`

## Critic-side contract

If the critic *does* surface per-statement / stylistic findings
(borderline cases are allowed), every such finding's `fix` field
MUST contain the substring `revert to prior wording at`. That is
the F3 contract on the critic side.

## Failure interpretation

- Typo "fixed" in output → drafter regression on F3.
- Per-statement / stylistic finding lacking the REVERT fix string →
  critic regression on F3 D10 sub-rubric.
- An edit-audit entry whose locator resolves to Problem Statement →
  drafter strayed beyond the requested change.
