# Claude adapter

Documentation checked **2026-10-07**. Claude Code runtime is **unverified here**; no local executable is available. Claude Code, chat, Cowork and API execution are not interchangeable.

## Portable skills and instructions

Claude Code project skills use `.claude\skills`; personal skills use `~\.claude\skills`. Plugins use root `skills\` and namespace skill names. Explicit invocation uses the native slash skill/command entry. The factory's `.claude-plugin\plugin.json` is a thin wrapper over the same canonical skill.

Portable skills require standard `name`/`description`. Claude Code extensions such as `context: fork`, invocation/model flags, arguments, hooks and shell interpolation do not belong in portable frontmatter. `allowed-tools` preapproves tools; it is not a universal exclusive allowlist.

`CLAUDE.md` files are additive context, not enforcement; imports also consume context. A plugin-root `CLAUDE.md` does not automatically load as plugin context. Current `AGENTS.md` fallback behavior is version- and existing-`CLAUDE.md`-dependent; do not assume identical cross-host precedence.

## Native delegation and justified specialists

Built-in subagents and ephemeral runtime definitions already support delegation. A recurring specialist can use `.claude\agents\*.md` or plugin `agents\`, with documented minimum tool restrictions. This factory supplies an optional native example, not a required agent.

Subagents start fresh and do not generally inherit conversation history or invoked skills. Built-in Explore/Plan skip `CLAUDE.md`; a custom agent's `skills` field preloads full bodies and can increase context overhead. Explicit handoffs must contain essential constraints when needed.

Nested delegation support is version-sensitive; do not encode the historical blanket ban. Agent teams remain experimental, disabled by default, and have resume/coordination/Windows limitations. Teammate plan approvals are not guaranteed human approval. The factory neither enables teams nor prescribes them.

Plugin agents ignore some permission/MCP/hook frontmatter, whereas plugin-level components can apply broadly. A private MCP tool boundary may therefore require a project-local profile/configuration instead of a distributable plugin-agent promise.

## Distribution and enforcement

The native Claude manifest lives in `.claude-plugin\plugin.json`; components remain outside that directory. Custom component paths must be contained. Knowledge is in skills, not duplicate `CLAUDE.md` bodies. Plugin resources are not mutable session-state locations.

Native deny/ask/allow rules, sandbox configuration and lifecycle hooks have different enforcement scopes. `PreToolUse` blocking depends on specific handler output/exit semantics; errors/timeouts are not universally fail-closed. Do not describe shell-command matching or prompt instructions as filesystem/network isolation.

MCP server output can contain untrusted instructions; connecting a capability does not make its content authoritative. Tools, hooks and agents supported in Claude Code may not execute in other Claude products.

## Official sources

- [Skills](https://code.claude.com/docs/en/skills), [portable authoring](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices).
- [Memory/instructions](https://code.claude.com/docs/en/memory), [subagents](https://code.claude.com/docs/en/sub-agents), [teams](https://code.claude.com/docs/en/agent-teams).
- [Plugin manifest](https://code.claude.com/docs/en/plugins/manifest-reference), [platform support](https://claude.com/docs/plugins/platform-support).
- [Permissions](https://code.claude.com/docs/en/permissions), [hooks](https://code.claude.com/docs/en/hooks), [MCP](https://code.claude.com/docs/en/mcp).
- [Models](https://code.claude.com/docs/en/model-config), [agentic prompting](https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/claude-prompting-best-practices).
