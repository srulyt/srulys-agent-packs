# Repository Instructions

This repository is the source for the **Copilot Factory** agent pack
(`agent-packs/copilot-factory/`) and other packs.

## Audience check (do this first)

These repo-level instructions are written for the **default Copilot
CLI agent only**. Before applying anything below, check whether you
are actually the default agent:

- If your turn includes an `<agent_instructions>` block identifying
  you as the **Copilot Factory Orchestrator** (or any other custom
  agent), **stop reading this file**. Your `<agent_instructions>`
  govern your behavior — the routing rule below does not apply to
  you and you should not redirect the user back to yourself.
- Otherwise, you are the default agent: follow the routing rule
  below.

## Routing rule (default agent only)

The default Copilot CLI agent has **no programmatic way to invoke
`@copilot-factory`**. It is activated only when the user explicitly
types `@copilot-factory` in their prompt. It is not a `task`-tool
`agent_type`, and proxying it through a `general-purpose` sub-agent
or by calling the factory sub-agents (`Factory Architect`,
`Factory Critic`, `Factory Engineer`) directly silently breaks the
orchestrator's contract (skills, session state, file boundaries).

When the user's request matches factory triggers — creating,
improving, analyzing, or reviewing an agent pack; designing a
multi-agent system — and the user did NOT prefix with
`@copilot-factory`:

1. Briefly tell the user this work is owned by `@copilot-factory`.
2. Ask them to re-issue the request prefixed with
   `@copilot-factory` (e.g.
   `@copilot-factory improve the spec-author pack ...`).
3. Do **not** run the workflow yourself, invoke the factory
   sub-agents directly, or have another sub-agent role-play as the
   orchestrator.

For requests unrelated to agent-pack work (general coding, git
operations, file exploration, repository maintenance), proceed
normally.
