# eval-framework agent pack

> ## ⚠️ DEPRECATED — superseded by `eval-pilot`
>
> This pack is **deprecated**. Its sole artifact, the `@eval-judge` agent, has
> been generalized and folded into the portable **`eval-pilot`** plugin
> (`agent-packs/eval-pilot/`), which ships a byte-identical judge as package
> data inside the pip-installable `evalpilot` engine
> (`evalpilot/_data/agents/eval-judge.agent.md`).
>
> - The in-repo `evals/` harness no longer uses this pack: `evals/_lib/judge.py`
>   re-exports `evalpilot.judge`, which stages the **bundled** judge into a
>   throwaway workspace for each call.
> - New repos should install `eval-pilot` instead — see
>   [`agent-packs/eval-pilot/README.md`](../eval-pilot/README.md).
>
> This directory is retained only for backward reference and will be removed in
> a future cleanup. **Do not build new work on it.**

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
