---
name: mcp-cli-discovery
description: "Detection algorithm for MCP servers and CLIs available in the user's environment. Defines sources (user prompt, copilot-instructions, harness tool listing), use rules, and graceful degradation. Provides the canonical discovery.json schema. Triggers on: detect MCPs, MCP discovery, CLI discovery, available tools, graceful degradation."
---

# MCP / CLI Discovery

This skill is loaded by `@spec-author` (to interpret discovery
output) and `@context-detective` (to perform discovery). It
defines the detection algorithm, the canonical `discovery.json`
schema, and the graceful-degradation contract.

## When to Use This Skill

Load this skill when:

- Building `discovery.json` (context-detective).
- Interpreting `discovery.json` to decide whether to mention a
  tool to the user (orchestrator).

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

- **Map tool → relevant section.** Example: GitHub MCP → "engineering
  dependencies", "prior issues / discussion"; web-search → "market
  context"; CLI inspection of repo (`gh`, `git log`) → "current
  behaviour / prior art".
- **If the tool maps to a section the drafter will fill, invoke it
  now**, capture findings into `context-pack.md`, mark
  `used: true` in `discovery.json`.
- **If invocation fails** (auth, rate limit, missing permission,
  timeout), capture the reason and mark `used: false` with notes.
  Continue.

## Graceful degradation

This is the most important rule:

> **If zero MCPs and zero CLIs are detected, the detective writes
> `discovery.json` with empty arrays, sets
> `graceful_degradation: true`, and proceeds using only the
> harness's built-in tools (read, search, web-search/browse if
> available). It never hard-fails.**

When the user prompt mentions a tool that turns out NOT to be
available, that is also graceful degradation: record an
`expected: <name>; available: false` entry in `skipped` and
continue with built-ins.

## Bounded probing

The detective has **no `execute` tool**. It does NOT shell out to
probe `which`/`where` for arbitrary CLIs. It only verifies tools
referenced in the three sources above. This avoids unbounded
side-channel work and respects the no-`execute` boundary.

## `discovery.json` schema (canonical)

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
- `research_tools` — built-in harness tools the detective relied
  on (web_search, browse, fs, etc.).
- `graceful_degradation` — `true` if the detective could not
  invoke any of the tools the user/instructions/harness expected
  it would invoke, AND it proceeded anyway.
- `skipped` — human-readable reasons for any expected tool that
  was not used.

## Quality checklist

- [ ] All three sources consulted (prompt, copilot-instructions,
      harness listing).
- [ ] Every detected tool has a `used: true|false` flag and a
      reason if `false`.
- [ ] `graceful_degradation: true` when any expected tool was
      unavailable.
- [ ] No shell `execute` calls were made.
- [ ] `discovery.json` written **even when zero tools are
      detected** (with empty arrays).
