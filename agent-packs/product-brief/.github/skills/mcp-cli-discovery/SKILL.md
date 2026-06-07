---
name: mcp-cli-discovery
description: "Detection algorithm for MCP servers and CLIs available in the user's environment. Defines sources (user prompt, copilot-instructions, harness tool listing), use rules, and graceful degradation. Defines how tool availability is reported through the research-runner's mcp-results fence and handoff. Triggers on: detect MCPs, MCP discovery, CLI discovery, available tools, graceful degradation."
---

# MCP / CLI Discovery

This skill is loaded by `@research-runner` (to perform discovery and
invoke whatever MCP server / CLI matches a requested research intent)
and by `@brief-orchestrator` (to interpret discovery output and decide
whether to mention a tool to the user). It defines the detection
algorithm, how tool availability is reported through the
research-runner's `mcp-results` fence and `handoff`, and the
graceful-degradation contract.

> **No file writes.** `@research-runner` never persists files. It
> discovers tools, runs queries, and reports availability / used /
> skipped through the `mcp-results` fence plus the `handoff` it
> returns to the orchestrator. Only the orchestrator persists those
> payloads to disk (to the `mcp-results.md` path in the STM Layout).
> There is no `discovery.json` artifact in this pack.

## When to Use This Skill

Load this skill when:

- Performing tool discovery and running an `mcp-query` (research-runner).
- Deciding, before composition, whether a tool is available and
  whether to surface its absence to the user (orchestrator).

## Detection sources (precedence: all merged, no source wins)

1. **Explicit mentions in the user prompt.**
   Example phrases: "we have the GitHub MCP", "use `gh`", "the
   `azd` CLI is available", "you have access to <tool>".
2. **Declarations in `.github/copilot-instructions.md`.**
   Anything the consuming repo declares as available.
3. **Harness runtime tool listing.**
   Any tool the harness exposes whose name starts with `mcp_`
   counts as an MCP. Other tools that match a CLI naming
   convention (e.g. shell-bound `gh`, `az`, `kubectl`) only count
   if (1) or (2) referenced them.

## Use rules

For each detected tool, decide whether to invoke it during
research:

- **Map tool → relevant research intent.** Example: GitHub MCP →
  "engineering dependencies", "prior issues / discussion";
  web-search → "market context"; CLI inspection of repo (`gh`,
  `git log`) → "current behaviour / prior art".
- **If the tool maps to the requested research intent, invoke it
  now**, capture the raw findings into the `mcp-results` fence, and
  report it as `used: true` in the in-memory discovery payload carried
  by that fence.
- **If invocation fails** (auth, rate limit, missing permission,
  timeout), capture the reason and report `used: false` with notes.
  Continue.

## Graceful degradation

This is the most important rule:

> **If zero MCPs and zero CLIs are detected, report a discovery
> payload with empty arrays in the `mcp-results` fence, set
> `graceful_degradation: true`, and proceed using only the harness's
> built-in tools (read, search, web-search/browse if available).
> Never hard-fail.**

When the user prompt mentions a tool that turns out NOT to be
available, that is also graceful degradation: record an
`expected: <name>; available: false` entry in `skipped` and
continue with built-ins.

## Bounded probing

Verify only tools referenced in the three sources above. Do NOT
shell out to probe `which`/`where` for arbitrary CLIs. This avoids
unbounded side-channel work and respects each agent's tool
boundary.

## Discovery payload shape (carried in the `mcp-results` fence)

The discovery state is **not** a written file. It is an in-memory
structure the research-runner embeds in the `mcp-results` fence it
returns to the orchestrator (and summarises in `handoff`). The shape
below is illustrative of that payload:

```json
{
  "mcps_detected": [
    {
      "name": "github-mcp",
      "source": "prompt | copilot-instructions | harness",
      "used": true,
      "notes": "Pulled 12 prior issues for prior-art research."
    }
  ],
  "clis_detected": [
    {
      "name": "gh",
      "source": "prompt | copilot-instructions | harness",
      "used": false,
      "notes": "User mentioned but harness exposes no shell binding."
    }
  ],
  "research_tools": ["web_search", "browse"],
  "graceful_degradation": false,
  "skipped": [
    "expected: github-mcp; available: false (auth missing)"
  ]
}
```

Field meanings:

- `mcps_detected` / `clis_detected` — every tool seen across the
  three sources. `used: true` means it was successfully invoked
  for this session.
- `research_tools` — built-in harness tools relied on (web_search,
  browse, fs, etc.).
- `graceful_degradation` — `true` only if **none** of the expected
  tools could be invoked AND the run proceeded anyway. Partial
  unavailability is already captured per-tool by `used: false` and
  `skipped` entries, so it does NOT set this flag.
- `skipped` — human-readable reasons for any expected tool that
  was not used.

## Quality checklist

- [ ] All three sources consulted (prompt, copilot-instructions,
      harness listing).
- [ ] Every detected tool has a `used: true|false` flag and a
      reason if `false`.
- [ ] `graceful_degradation: true` only when **none** of the expected
      tools could be invoked (partial unavailability is captured
      per-tool via `used: false` / `skipped`).
- [ ] No unbounded shell probing was performed.
- [ ] The discovery payload is reported in the `mcp-results` fence
      **even when zero tools are detected** (with empty arrays);
      availability / used / skipped are summarised in `handoff`.
