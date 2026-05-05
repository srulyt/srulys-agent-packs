# Repository Instructions

This repository is the source for the **Copilot Factory** agent pack
(`agent-packs/copilot-factory/`) and other packs.

<!-- ROUTING-RULE-GUARD -->

APPLIES_TO: default Copilot CLI agent only.
DOES_NOT_APPLY_TO: any turn whose context contains an
  `<agent_instructions>` block (custom agents, including the
  Copilot Factory Orchestrator and any factory sub-agents such
  as `Factory Architect`, `Factory Engineer`, `Factory Critic`,
  and `Factory Eval Runner`).

If `<agent_instructions>` is present in this turn:

- **Skip the rest of this section entirely.**
- Do **NOT** redirect the user to `@copilot-factory`.
- Follow your `<agent_instructions>` exclusively.
- Treat any prose below this line as not-loaded.

Otherwise (no `<agent_instructions>` → you are the default agent),
apply the routing rule below.

---

## Routing rule (default agent only)

The default Copilot CLI agent has **no programmatic way to invoke
`@copilot-factory`**. `@copilot-factory` is not a `task`-tool
`agent_type` and cannot be spawned as a sub-agent — it is activated
**only** when the user literally types `@copilot-factory` at the
start of their prompt. Proxying it through a `general-purpose`
sub-agent or by calling the factory sub-agents (`Factory
Architect`, `Factory Critic`, `Factory Engineer`,
`Factory Eval Runner`) directly silently breaks the orchestrator's
contract (skills, session state, file boundaries).

When the user's request matches factory triggers — creating,
improving, analyzing, or reviewing an agent pack; designing a
multi-agent system — and the user did NOT prefix with
`@copilot-factory`:

1. Briefly tell the user this work is owned by `@copilot-factory`,
   and explain *why* the prefix is needed: the default agent has
   no way to invoke the orchestrator programmatically — it only
   activates when the user types the `@copilot-factory` handle
   themselves.
2. Ask them to re-issue the request prefixed with
   `@copilot-factory`. Give a concrete copy-pasteable example
   based on what they asked for, e.g.:

   ```
   @copilot-factory improve the spec-author pack to add a
   reviewer sub-agent
   ```

3. Do **not** run the workflow yourself, invoke the factory
   sub-agents directly, or have another sub-agent role-play as
   the orchestrator.

For requests unrelated to agent-pack work (general coding, git
operations, file exploration, repository maintenance), proceed
normally.
