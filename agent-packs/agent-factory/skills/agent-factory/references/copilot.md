# Copilot adapter

Documentation checked **2026-10-07**. Distinguish CLI, app, IDE harness, cloud agent, and code review. Installed CLI during implementation: **1.0.86-1**; live verification is recorded in the eval report, not assumed here.

## Knowledge and invocation

Project skills can live in `.github\skills`, `.agents\skills`, or `.claude\skills`; this repository's `init.cmd` copies the canonical skill to `.github\skills\agent-factory`. Portable plugin skills live at root `skills\<name>\SKILL.md`. Use explicit skill invocation or ask the default agent to use the `agent-factory` skill. Do not invoke `@copilot-factory` expecting this new skill; that selects the intact legacy system.

CLI already has automatic subagents, built-in specialists and optional `/fleet`/`--fleet`. No custom profiles or Fleet invocation are needed to install this factory. Runtime concurrency/depth and AI-credit cost are not permanent domain facts.

Repository/path instructions combine in CLI; do not assume cloud's nearest-`AGENTS.md` semantics apply unchanged. Keep factory expertise out of always-loaded instructions. Local memory directories do not have a universal automatic-loading contract.

## Target-specific artifacts

- Custom agents: `.github\agents\<slug>.agent.md`, with YAML `description` and explicit minimum supported `tools` when restricting capabilities. Omitted tools default broadly; unknown tools can be ignored, so verify actual exposure.
- `user-invocable: false` and `disable-model-invocation: true` have different purposes. Do not add either as universal delegation boilerplate.
- Custom-agent subagents do not receive repository instructions by default; CLI's `include-custom-instructions` is target-specific. Do not assume skills or conversation context are inherited.
- `.github\prompts\*.prompt.md` is an IDE convenience, not documented CLI prompt-file support. A plain task-request template is usable without inventing CLI compatibility.
- Project MCP `.mcp.json`/`.github\mcp.json`, user `~\.copilot\mcp-config.json`, IDE `.vscode\mcp.json`, and cloud admin settings differ. Check built-in GitHub tools before adding a server; no credentials in generated packs.
- CLI hooks use documented lifecycle JSON/handlers; cloud OS/event/permission behavior differs. Test event and failure handling rather than assert all hooks fail closed.

## Distribution

Use portable root `plugin.json` with recognized Agent Plugins `$schema` and fixed `skills\` locations. Portable 1.0.0 components are skills and optional MCP; Copilot-specific components belong in its documented extension namespace/layout. No such extension is needed for this factory.

Adding `$schema` to an existing legacy manifest changes interpretation; never upgrade another pack incidentally. CLI/app/cloud installation differs, and installed plugin copies can be cached. Test the installed copy. This repository's marketplace entry is a CLI distribution route, not universal cloud setup.

## Official sources

- [Skills](https://docs.github.com/en/copilot/concepts/agents/about-agent-skills), [CLI skill authoring](https://docs.github.com/en/copilot/how-tos/copilot-cli/customize-copilot/add-skills).
- [Native/custom agents](https://docs.github.com/en/copilot/concepts/agents/copilot-cli/about-custom-agents), [profile configuration](https://docs.github.com/en/copilot/reference/custom-agents-configuration), [CLI reference](https://docs.github.com/en/copilot/reference/copilot-cli-reference/cli-command-reference).
- [Fleet](https://docs.github.com/en/copilot/concepts/agents/copilot-cli/fleet), [context management](https://docs.github.com/en/copilot/concepts/agents/copilot-cli/context-management).
- [Instructions](https://docs.github.com/en/copilot/how-tos/copilot-cli/customize-copilot/add-custom-instructions), [surface support](https://docs.github.com/en/copilot/reference/customization-cheat-sheet).
- [Plugins](https://docs.github.com/en/copilot/reference/copilot-cli-reference/cli-plugin-reference), [MCP](https://docs.github.com/en/copilot/how-tos/copilot-cli/customize-copilot/add-mcp-servers), [hooks](https://docs.github.com/en/copilot/reference/hooks-reference).
