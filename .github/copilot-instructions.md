# Repository Instructions

This repository is the source for the **Copilot Factory** agent pack
(`agent-packs/copilot-factory/`) and other packs. Agent-pack creation and
improvement work is owned by the `@copilot-factory` orchestrator.

## Routing rule (read carefully)

`@copilot-factory` can ONLY be activated by the user explicitly typing
`@copilot-factory` in their prompt. It is not a `task`-tool `agent_type`,
and the default Copilot CLI agent has **no programmatic way to invoke
it**. Do not attempt to "delegate to" the orchestrator — there is no
tool call that does so.

When the user's request matches factory triggers (creating, improving,
analyzing, or reviewing an agent pack; designing a multi-agent system)
and the user did NOT prefix with `@copilot-factory`:

1. Briefly tell the user this work is owned by `@copilot-factory`.
2. Ask them to re-issue the request with the `@copilot-factory` prefix
   (e.g. `@copilot-factory create a new pack for ...`).
3. **Do not** attempt to run the workflow yourself.
4. **Do not** invoke the factory sub-agents (`Factory Architect`,
   `Factory Critic`, `Factory Engineer`) directly via the `task` tool —
   they will refuse with an invocation guard, and proxying them
   bypasses session-state, skill loading, and the delegation contract.
5. **Do not** spawn a `general-purpose` (or any other) sub-agent and
   instruct it to role-play as `@copilot-factory`. The orchestrator's
   prompt, skills, file-access boundaries, and `state.json` discipline
   cannot be reproduced by a proxy; this is a known anti-pattern that
   silently breaks the contract.

For requests unrelated to agent-pack creation/improvement (general
coding, git operations, file exploration, repository maintenance),
proceed normally as the default Copilot CLI agent.

## When you ARE the orchestrator

If you are running as `@copilot-factory` (the user invoked you
explicitly), follow the orchestrator's own prompt at
`agent-packs/copilot-factory/.github/agents/copilot-factory.agent.md`
and the supporting instructions under
`agent-packs/copilot-factory/.github/instructions/`. The repo-level
instruction here does not override those.
