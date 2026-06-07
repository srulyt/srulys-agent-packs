---
name: prd-context-gathering
description: "Step 1 of the EARS PRD workflow. Detects available tools (file-system search, web search, MCP servers), builds a short in-conversation context digest, and degrades gracefully when tools are missing. Triggers on: gather context, research the spec, what MCP web or file tools are available, graceful degradation, build PRD context."
---

# PRD Context Gathering (step 1)

This skill defines how the host agent builds the context it needs before
interrogating the user. It is distilled from `spec-author`'s
`mcp-cli-discovery` skill, but **without** the `discovery.json`
artifact — findings stay **in the conversation** (speed-first, no state).

## When to Use This Skill

Load this skill at **step 1** of the EARS PRD workflow: detect what
research tools are available, use the relevant ones, and record what was
skipped.

## Detection sources (precedence: all merged, no single source wins)

1. **Explicit mentions in the user prompt.** Phrases like "we have the
   GitHub MCP", "use `gh`", "you have access to <tool>".
2. **Declarations in `.github/copilot-instructions.md`** (or
   equivalent), if present in the workspace.
3. **Harness runtime tool listing.** Any tool whose name starts with
   `mcp_` counts as an MCP. Built-ins `read`/`search`/`web` are assumed
   available unless evidence says otherwise.

## Use rule — only use a tool that maps to a section

For each detected tool, decide whether to invoke it during research:

- **Map tool → relevant PRD section.** Examples: a GitHub MCP →
  "engineering dependencies / prior issues / prior art"; web-search →
  "market context / competitive landscape"; `read`/`search` over the
  repo → "current behaviour / existing implementation".
- **If the tool maps to a section the agent will fill, invoke it now**
  and fold the findings into the in-conversation context digest.
- **If invocation fails** (auth, rate limit, missing permission,
  timeout), record one line and continue — never block.

## Graceful-degradation contract (the most important rule)

> If a tool is **expected but unavailable**, record one line in the
> conversation — *"expected `<tool>`; not available — proceeding with
> built-ins"* — and continue.
>
> If **zero** MCP/web tools are detected, proceed using `read`/`search`
> only. The workflow **never hard-fails**.

Every skipped/expected-but-missing tool is also surfaced to the user at
the end of the run via the `degraded_tools` field of the `prd-summary`
block (owned by `ears-prd-workflow`). Degradation is visible so the user
understands which context sources were and weren't consulted.

## Bounded probing — no `execute`

This workflow has **no `execute`/shell tool** and must not acquire one.
It does NOT shell out to probe `which`/`where` for arbitrary CLIs. It
only verifies tools referenced in the three detection sources above.
This keeps context-gathering bounded and side-effect-free.

## Output of this step

A **short in-conversation context digest** (a few bullets) summarising:
what the feature is, what the workspace/tools revealed, and a one-line
note of any skipped tools. **No file is written** in this step.

## Must NOT

- MUST NOT use `execute`/shell or probe for arbitrary CLIs.
- MUST NOT hard-fail when a tool is missing — record and continue.
- MUST NOT fabricate context the tools did not actually return. If a
  tool was unavailable, say so; do not invent its findings.
- MUST NOT write a `discovery.json` or any other file — the digest lives
  in the conversation only.

## Quality Checklist

- [ ] All three detection sources consulted.
- [ ] Only tools that map to a PRD section were invoked.
- [ ] Every expected-but-unavailable tool recorded as a one-line skip.
- [ ] Zero tools detected → proceeded with `read`/`search`; no hard fail.
- [ ] No `execute`/shell calls; no files written.
- [ ] Skipped tools ready to surface in `prd-summary.degraded_tools`.
