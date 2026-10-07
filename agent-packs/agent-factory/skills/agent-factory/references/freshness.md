# Platforms are changing dependencies

Last documentation review: **2026-10-07**. The platform references are snapshots of architecture-affecting facts, not eternal schemas or universal parity claims.

Refresh affected assumptions when a major model generation/client changes, native capabilities replace an artifact, plugin/skill schemas change, a substantial redesign begins, an adapter fails to load, or permission/inheritance behavior changes. Ordinary creation with still-applicable facts does not require exhaustive web research.

Prefer official documentation for the exact host/surface. Record the source URL/revision, checked date, relevant fact, local client version, and whether it was only documented or actually exercised. A working personal install does not establish cloud availability.

Current researched model pages identify GPT-6.1 Sol, GPT-6 Astra/Sol/Luna and Claude Opus/Sonnet 5.5. These facts belong here rather than in enduring domain knowledge. Inherit defaults; verify availability before emitting an explicitly requested override. Account, provider, authentication method, and host can change effective availability and aliases.

## Sources and evidence anchors

- [Agent Skills specification](https://agentskills.io/specification): portable metadata, naming, resources and progressive disclosure. Its recommendation is under 5,000 **tokens**, not a universal 5,000-word hard limit.
- [Agent Plugins specification](https://agent-plugins.org/specification) and [1.0.0 manifest schema](https://agent-plugins.org/schemas/1.0.0/plugin.schema.json): portable fixed discovery and filesystem-resolved containment. Packaging containment does not sandbox running code.
- [OpenAI model recommendations](https://developers.openai.com/codex/models), [frontier prompting](https://developers.openai.com/api/docs/guides/latest-model).
- [Claude model overview](https://platform.claude.com/docs/en/models/overview), [agentic prompting guidance](https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/claude-prompting-best-practices).

Research anchors: GitHub docs `73050b4dbc76c79079f6dcf6985419504a3161d8`; OpenAI Codex 0.160.1 source `d27764b82f7118f674371e6d6e76271d9d606edb`; Anthropic skill examples `683bc88e56f3e09ba94f7055977f3d3aa499f202`. These pin evidence, not required client versions.

Local implementation checks are reported separately in the pack's evaluation documentation. Codex/Claude runtime verification cannot be inferred from a Copilot skill smoke run.
