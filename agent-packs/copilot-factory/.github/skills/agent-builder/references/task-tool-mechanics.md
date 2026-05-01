# Task Tool Mechanics (cross-cutting reference)

This reference describes how an orchestrator agent invokes a sub-agent
in GitHub Copilot CLI. It is **descriptive**: a template, the rules
that govern its use, and the shape of worked examples. Operational
runtime logic (which sub-agent to invoke at which phase, what to do
on a BLOCKING verdict, etc.) is **not** here — that lives in each
orchestrator's own prompt.


## Required orchestrator section

Every generated orchestrator (`.agent.md` whose architectural role is
coordinator / orchestrator) must include a section literally titled
`## How to Delegate (Task Tool Mechanics)` containing:

1. A statement that `task` is the only way to invoke a sub-agent. The
   `@<name>` labels in prose are user-facing shorthand only; the value
   passed as `agent_type` MUST be the sub-agent's **frontmatter `name`**
   value (verbatim, including spaces and capitalization), not the
   kebab-case filename slug. Passing the slug fails with `Unknown
   agent_type`.
2. Required parameters — `agent_type`, `name`, `description`,
   `prompt` — and optional parameters — `mode`, `model`.
3. A cross-reference to this reference file
   (`agent-builder/references/task-tool-mechanics.md`) for canonical
   `task` semantics. Do not re-derive them in the orchestrator prompt.
4. One worked `task(...)` example **per sub-agent** the orchestrator
   delegates to. Each example shows: the literal `agent_type` value
   (matching the sub-agent's frontmatter `name`); the prompt structure
   including session/artifact paths the sub-agent will need; and the
   named-fenced output contract blocks the orchestrator will parse
   from the sub-agent's final message.

> **Note on example syntax**: The `task(...)` blocks below use
> pseudo-code; `+` denotes host-language string concatenation. The
> real tool accepts JSON-object arguments and `prompt` is a single
> (possibly multi-line) string.

## Worked example shape (template)

```
task(
  agent_type: "<sub-agent-frontmatter-name>",
  name: "<short-kebab-case>",
  description: "<3-5 word summary>",
  mode: "sync" | "background",
  prompt: "You are being invoked as @<sub-agent-slug>.\n\n" +
          "<inputs: session id, file paths, parameters>\n\n" +
          "<output contract reminder: list each fenced block " +
          "the sub-agent must emit so the orchestrator can parse it>"
)
```

Rules:

- Pass file *paths*, not inlined file contents. Sub-agents read on
  demand.
- Always inject the sub-agent's named-fenced output contract into the
  prompt so the model emits it. Parse those fences from the final
  assistant message; do not paraphrase.
- Use `mode: "sync"` by default. Use `mode: "background"` only when
  you can do meaningful work in parallel and a completion notification
  will drive your next action. After launching a background task, end
  your turn — do not poll.
- Do not pass `model` overrides unless the pack's eval spec or a
  documented user override permits it.

## Hard Delegation Rule template

Every generated orchestrator must also include a section literally
titled `## Hard Delegation Rule (STOP-and-delegate)` containing:

1. A self-check the model runs before any non-`task`,
   non-STM-write tool call: *"Am I about to do work owned by a
   specialist? If yes, STOP and delegate via `task`."*
2. A list of forbidden actions concrete to the pack — at minimum:
   - No `read`/`grep`/`glob`/`view` over the target output directory
     (the directory the engineer-equivalent sub-agent writes to).
   - No reading or paraphrasing a sub-agent's artifact body beyond
     extracting its named fenced contract blocks.
   - No authoring specialist content (architecture text, review
     verdicts, build output) in the orchestrator's own words.
   - No writes outside the orchestrator's STM directory.
3. A statement that violating any item invalidates the orchestrator's
   role and the action must be retried as a `task` delegation.

## Tools-list discipline

A generated orchestrator's `tools:` frontmatter must be scoped to the
minimum needed. The defensible default for a coordinator is
`["read", "edit", "search", "agent"]`. `execute` requires an
architecture-document justification. `["*"]` is never acceptable.

## Worked-example shapes (illustrative, not operational)

These shapes are illustrative only — substitute pack-specific
sub-agent names, slugs, and contract block names.

**Design-style delegation**:

```
task(
  agent_type: "<designer-frontmatter-name>",
  name: "design-system",
  description: "Produce architecture",
  mode: "sync",
  prompt: "Session: {sid}\nInputs: {paths}\n\n" +
          "Emit fenced blocks: `summary`, `agents-json`, " +
          "`ready-for-review`."
)
```

**Review-style delegation**:

```
task(
  agent_type: "<critic-frontmatter-name>",
  name: "review-artifact",
  description: "Quality gate",
  mode: "sync",
  prompt: "Session: {sid}\nReview Type: {type}\n" +
          "iteration_count: {n}\nArtifact: {path}\n\n" +
          "Emit `verdict`, `blocking-issues-json`, `concerns-json`."
)
```

**Build-style delegation**:

```
task(
  agent_type: "<engineer-frontmatter-name>",
  name: "build-artifacts",
  description: "Materialise pack",
  mode: "sync",
  prompt: "Session: {sid}\nArchitecture: {path}\n" +
          "Output location: {dir}\n\n" +
          "Emit `implementation-summary`, `files-created-json`, " +
          "`ready-for-review`."
)
```

For full `task` parameter semantics — sync vs. background invocation,
`read_agent` / `write_agent` / `list_agents`, and information-flow
rules — see the §"Task tool semantics (canonical)" appendix below.

## Task tool semantics (canonical)

**Required parameters per call**:
- `agent_type` — sub-agent's frontmatter `name` value, verbatim
  (spaces and capitalization preserved). Not the kebab filename slug.
- `name` — short kebab-case identifier for this delegation.
- `description` — 3-5 word human summary.
- `prompt` — full instructions for the sub-agent. Pass file paths,
  not inlined contents.

**Optional parameters**:
- `mode` — `"sync"` (default) or `"background"`. Sync blocks until
  the sub-agent completes and returns its final assistant message
  as the tool result. Background returns immediately; the orchestrator
  ends its turn and resumes when the completion notification fires.
- `model` — model override. Do not pass unless the pack's eval spec
  or a documented user override permits it.

**Information flow**:
- Sub-agents are stateless launches; they receive only the prompt
  and any files they read on demand. They do NOT see prior orchestrator
  turns.
- The orchestrator parses the sub-agent's named-fenced output blocks
  from the final assistant message. It does NOT paraphrase the body.
- For multi-turn sub-agents, the orchestrator can `write_agent` to
  send a follow-up turn to an idle agent, and `read_agent` to retrieve
  cumulative or since-turn responses.

**When to use background**:
- Only when the orchestrator can do meaningful parallel work and
  a notification will drive its next action.
- After launching a background task, the orchestrator must end its
  turn with no further tool calls.
- Never poll; wait for the completion notification.
