# Codex adapter

Documentation checked **2026-10-07**. Codex runtime is **unverified here**; no local executable is available. Local CLI/desktop/IDE and hosted/API behaviors are separate.

## Portable knowledge

Repository skills are discovered from `.agents\skills` along the working-directory-to-repository-root chain; user skills use `~\.agents\skills`. Copy the canonical `skills\agent-factory` directory to the project's `.agents\skills\agent-factory`, then explicitly invoke `$agent-factory` or select it through the host. Same-name skills are not merged.

Skills load metadata first, body on activation, and supporting resources when needed. Optional `agents\openai.yaml` is host metadata, not a custom agent definition. Do not add it, invocation overrides, tool grants, or a model pin without an actual requirement.

## Native behavior and profiles

Local Codex has native subagents and manages spawning, waiting, messaging and collection. Custom specialists use `.codex\agents\*.toml` (or personal agent directories), with `name`, `description`, and `developer_instructions`. The bundled TOML example is an optional shape, not proof of installed-client support.

Omit model/effort overrides to inherit defaults. Sandbox policy and permissions are native configuration; prose boundaries do not create a sandbox. Read-only audit isolation requires verified native sandbox/tool policy, not just a "read-only" name.

Responses API multi-agent is a distinct beta with separately documented model/tool support. Do not equate it with local TOML profiles or assume all GPT-6 models support every API feature. Hosted clients need separate capability/auth/connectivity checks.

## Instructions, prompts, tools and packaging

`AGENTS.override.md` then `AGENTS.md` are selected per directory; project instructions accumulate root-to-working-directory, with nearer guidance overriding earlier content. The documented default project-document budget is 32 KiB. Do not overwrite global/project instructions or install an override merely to load factory knowledge.

Custom prompts are deprecated in current Codex documentation; use a skill when reuse is actually needed, or a plain task request for convenience/no-customization. Do not generate `.prompt.md` pretending it is a Codex feature.

Local MCP is configured natively and supports STDIO/Streamable HTTP; cloud connectivity/authentication differs. Hooks require host trust, have specific supported handlers, and are not universal plugin components. Policy enforcement needs failure-path validation.

Current Copilot/Codex share portable root `plugin.json`, `skills\`, optional `mcp.json`. OpenAI-specific extensions belong in the documented namespace; legacy `.codex-plugin` overlays have different semantics. Plugin installation/distribution varies by client; do not claim runtime installation based on schema checks.

## Official sources

- [Skills](https://developers.openai.com/codex/skills), [instructions](https://developers.openai.com/codex/guides/agents-md).
- [Native multi-agent/custom profiles](https://developers.openai.com/codex/multi-agent), [configuration](https://developers.openai.com/codex/config-basic).
- [Prompting](https://developers.openai.com/codex/prompting), [models](https://developers.openai.com/codex/models), [API multi-agent](https://developers.openai.com/api/docs/guides/responses-multi-agent).
- [Plugins](https://developers.openai.com/plugins/build/plugins), [MCP](https://developers.openai.com/codex/mcp), [hooks](https://developers.openai.com/codex/hooks), [deprecated prompts](https://developers.openai.com/codex/custom-prompts).
