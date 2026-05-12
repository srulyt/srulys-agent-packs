# eval-framework agent pack

This pack ships **one custom agent**:

- `@eval-judge` — scores a SUT artifact against free-form criteria and
  returns a single JSON verdict.

It exists to support the pytest-based eval framework under
[`evals/`](../../evals/). End users do not invoke it directly. The
`judge` helper in `evals/_lib/judge.py` stages this agent into each
test's workspace, calls `copilot -p ... --agent eval-judge`, and parses
the JSON it emits.

## Why a dedicated agent

- **Model pinning.** The judge is pinned to a strictly stronger model
  than any system-under-test so its scores are credible. Pack/skill
  agents can use whichever model their own contract calls for; the
  judge uses its own.
- **Tight tool scope.** The judge only has `read` + `search`. It cannot
  modify files, invoke other agents, or fetch URLs.
- **Prompt-injection resistance.** SUT artifacts are untrusted input.
  Hard rules in the agent's prompt make the judge refuse to follow
  instructions embedded in those artifacts.
