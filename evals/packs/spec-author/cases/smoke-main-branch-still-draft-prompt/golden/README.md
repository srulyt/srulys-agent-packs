# Golden expectations — smoke-main-branch-still-draft-prompt

Rubric-judged. Key assertions:

- The orchestrator's transcript shows it parked at
  `phase: awaiting-mode-decision` (V5 branch probe → trunk + draft)
  AT LEAST ONCE.
- The orchestrator emitted the V6 verbatim prompt — the message
  must contain the literal strings `PUBLISH`, `KEEP-DRAFT`, and
  `ABORT` and reference the trunk-branch concern.
- The detective emitted a `branch-probe-json` fence with
  `branch_kind: trunk` (probe-only invocation; did NOT also write
  `discovery.json` for that probe).
- After the user replied `KEEP-DRAFT`, the orchestrator did NOT
  flip `status` to `published` and did NOT mutate the `Version:`
  field.
- The final `docs/specs/quick-toggle.md` still reads
  `Status: draft`, `Version: 0.0.1-draft`.
- A `pre-merge-reminder` block appears in the orchestrator's
  end-of-turn output (mutated_this_turn==true since the Out-of-
  Scope edit was applied).
- No `CHANGELOG.md` exists at run end.
