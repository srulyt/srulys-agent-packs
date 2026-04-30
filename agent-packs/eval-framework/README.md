# eval-framework agent pack

Two custom agents used by the harness under `eval/`:

- `@eval-runner` — captures session evidence into a fixture JSON.
- `@eval-judge` — scores SUT artifacts against a single rubric.

These are **not** end-user-facing agents — they exist to support the
evaluation framework, not to ship to users. See the top-level
[`eval/README.md`](../../eval/README.md) for the operator workflow.

## Why split runner and judge

- Separation of concerns: the runner is a thin SQL → JSON transformer; the
  judge is a high-capability evaluator. Pinning each to the right model
  keeps cost and latency proportional to value.
- Independence: the judge never sees the orchestrator's session log or
  other rubrics' scores. This prevents anchoring and lets us double-judge
  blocker rubrics for self-consistency.
- Negative scope: each agent's tool list is tight enough that the L3
  assertions over the agent's own runs would catch any drift.

## Model choice

Both agents pin a specific model in front-matter:

- Runner: standard model — its job is mechanical.
- Judge: a strictly stronger model than any system-under-test. The
  framework records the judge model on every run record so trends can
  be sliced by it.
