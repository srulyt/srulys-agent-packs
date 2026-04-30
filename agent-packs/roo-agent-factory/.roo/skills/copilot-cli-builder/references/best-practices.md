# Best Practices for Building Copilot CLI Agents & Skills

Design guidance for creating effective custom agents, skills, and instructions.

---

## Choosing the Right Customization Type

| Requirement | Best Option |
|-------------|-------------|
| Always follow repository conventions | **Custom Instructions** |
| Repeatable workflow invoked on demand | **Skill** |
| Specialist with constrained toolset for specific tasks | **Custom Agent** |
| Guardrails, policy, or automation around tool use and session events | **Hooks** |
| Connect to external services/APIs | **MCP Servers** |
| Bundle of functionality (skills + agents + hooks + MCP) for distribution | **Plugin** |

### Custom Instructions vs Skill vs Custom Agent

**Custom Instructions** — persistent guidance loaded at session start:
- Apply to **everything** the agent does
- Best for: coding standards, build commands, commit conventions, architecture overview
- Keep concise — lengthy instructions dilute effectiveness
- Repository instructions override global instructions

**Skills** — just-in-time instructions loaded when relevant:
- Activated based on task context or explicit invocation (`/skill-name`)
- Best for: repeatable workflows, consistent output formats, domain-specific task guidance
- Avoid overloading context with permanently loaded instructions
- Use when guidance is sometimes needed, but not always

**Custom Agents** — specialized personas with their own context window:
- Run as **subagents** with separate context (don't clutter main agent)
- Best for: specialist reviewers, read-only auditors, domain experts
- Can restrict tool access for safety
- Can auto-delegate via inference when `disable-model-invocation` is not `true`

### Decision Flow

```
Is this guidance needed for EVERY task?
  YES → Custom Instructions
  NO  ↓

Is this a repeatable workflow or domain knowledge?
  YES → Skill
  NO  ↓

Does this need a specialist perspective, restricted tools, or separate context?
  YES → Custom Agent
  NO  ↓

Does this need external service integration?
  YES → MCP Server
  NO  ↓

Do you need programmatic control over tool execution or session lifecycle?
  YES → Hook
```

---

## How Subagents Work

Understanding subagents is critical to designing effective custom agents.

### Architecture

```
Main Agent (your CLI session)
  ├── Subagent: explore (built-in, fast codebase analysis)
  ├── Subagent: task (built-in, runs commands)
  ├── Subagent: general-purpose (built-in, complex tasks)
  ├── Subagent: code-review (built-in, reviews changes)
  └── Subagent: your-custom-agent (your agent profile)
```

- Each subagent has its **own context window** — separate from the main agent
- The main agent decides when to delegate to a subagent
- Subagents can use tools allowed by their configuration
- Results flow back to the main agent when the subagent completes

### When Copilot Uses Subagents

Copilot is likely to spin up a subagent for:
- **Codebase exploration** — listing endpoints, tracing dependencies
- **Command execution** — running test suites, builds
- **Code review** — reviewing staged changes
- **Complex multi-step work** — implementing features with many changes
- **Custom agent delegation** — when your custom agent matches the task via inference

### Design Implications

- **Keep agent prompts focused** — the subagent's context starts clean, so the prompt is the primary driver of behavior
- **Restrict tools appropriately** — a read-only agent should only get `["read", "search"]`
- **Write clear descriptions** — this is how the main agent decides whether to delegate to your agent
- **Consider context isolation** — subagents can do heavy work without bloating the main agent's context

---

## Writing Effective Agent Descriptions

The `description` field is the most important part of an agent profile. It determines:
1. When the agent appears in agent selection
2. When inference triggers automatic delegation
3. How the user understands the agent's purpose

### Good Description Patterns

**Specificity + Trigger Keywords:**
```yaml
description: Refactors TypeScript code for better performance. Use when optimizing slow functions, reducing bundle size, or improving runtime efficiency.
```

**Domain + Scope + When to Use:**
```yaml
description: Reviews Python code for security vulnerabilities including injection attacks, authentication flaws, and data exposure. Use for security audits and pre-merge checks.
```

**Explicit Trigger Words:**
```yaml
description: Creates and maintains API documentation. Use when asked to document endpoints, generate OpenAPI specs, or update API reference docs. Trigger words: api-docs, swagger, openapi.
```

### Bad Description Patterns

```yaml
# Too vague — won't trigger appropriately
description: Helps with code

# Too broad — will trigger too often
description: A helpful coding assistant for all programming tasks

# Missing trigger context — inference won't know when to use it
description: React component specialist
```

### Description Checklist

- [ ] States the agent's specific expertise
- [ ] Describes when the agent should be used
- [ ] Includes relevant trigger keywords
- [ ] Doesn't overlap significantly with other agent descriptions

---

## Writing Effective Agent Prompts

The markdown body of an agent profile is the prompt that drives the subagent's behavior.

### Structure Pattern: Role → Responsibilities → Constraints → Output

```markdown
You are a [role] specializing in [domain].

Your responsibilities:
- [Primary task 1]
- [Primary task 2]
- [Primary task 3]

Constraints:
- Never [prohibited action]
- Always [required behavior]
- Only modify files matching [pattern]

Output format:
- [Expected structure or format]
```

### Structure Pattern: Process → Steps → Verification

```markdown
Follow this process for every task:

1. **Analyze**: Examine the relevant code and understand the current state
2. **Plan**: Identify what needs to change and why
3. **Execute**: Make the changes following [standards]
4. **Verify**: Run [verification command] to confirm correctness

At each step, explain your reasoning before proceeding.
```

### Prompt Design Principles

1. **Be specific, not generic** — "Use Jest for unit tests with describe/it blocks" beats "Write good tests"
2. **Set explicit boundaries** — "Only modify test files" prevents scope creep
3. **Define output expectations** — "Create a markdown report with severity ratings" gives clear goals
4. **Include domain knowledge** — Things Copilot wouldn't know about your stack or conventions
5. **Don't repeat what Copilot already knows** — No need to explain how to write JavaScript
6. **Keep under 30,000 characters** — Hard limit, but shorter is better for focus

### Prompt Anti-Patterns

| Anti-Pattern | Problem | Fix |
|-------------|---------|-----|
| "Help with code" | Too vague, no direction | Define specific expertise and scope |
| Contradictory rules | "Never modify files" + "Fix all bugs" | Resolve conflicts, be consistent |
| Giant prompt (>10K chars) | Dilutes focus, wastes context | Extract details to skill references |
| Duplicating built-in knowledge | Wastes tokens on what Copilot knows | Focus on what's unique to your context |
| No boundaries | Agent does everything, does nothing well | Restrict scope with explicit constraints |

---

## Designing for Inference

Inference is how the main agent automatically decides to delegate to your custom agent. Understanding this helps you design agents that activate at the right time.

### How Inference Works

1. User sends a prompt to the main agent
2. Main agent evaluates available custom agents by their `description`
3. If a custom agent's description matches the task, the main agent delegates to it as a subagent
4. The subagent runs with its own context, tools, and prompt

### Controlling Inference

```yaml
# Agent auto-delegates when task matches (default behavior)
# (no disable-model-invocation needed — true by default)

# Agent must be manually selected
disable-model-invocation: true
```

**Set `disable-model-invocation: true` when:**
- The agent is a **user-facing orchestrator** that should not be auto-routed to by another model (users still invoke it with `@name`)
- The agent does something destructive or irreversible
- The agent should only run when explicitly requested
- Multiple agents have overlapping descriptions
- The agent is experimental or under development

**Do NOT set `disable-model-invocation: true` on subagents.** Subagents
are invoked by an orchestrator via the `task` tool; this flag hides
them from the calling agent's task-tool registry and makes them
unreachable. Use a prompt-level invocation guard to redirect
accidental direct invocations.

**Leave inference enabled when:**
- The agent has a clear, non-overlapping specialty
- Auto-delegation would save the user time
- The agent is safe to run without supervision

### Inference Triggers

Users can trigger agents in four ways:
1. **Slash command**: `/agent` → select from list
2. **Explicit instruction**: "Use the security-auditor agent on these files"
3. **By inference**: Prompt naturally matches the agent's description
4. **Programmatically**: `copilot --agent my-agent --prompt "do X"`

Design your agent description to work well with option 3 (inference) since that's the most seamless user experience.

---

## Skill Design Patterns

### Progressive Disclosure

Keep SKILL.md concise with core instructions. Put detailed reference material in subdirectories:

```
my-skill/
├── SKILL.md              # Core instructions (< 5000 words)
├── references/            # Loaded on demand
│   ├── patterns.md        # Detailed patterns
│   └── api-docs.md        # API reference
├── scripts/               # Executable code
│   └── validate.py        # Validation script
└── assets/                # Output templates
    └── report-template.md # Template file
```

### Script-Backed Skills

Skills can include scripts that Copilot executes as part of the workflow:

```markdown
---
name: image-converter
description: Converts images between formats. Use when asked to convert, resize, or transform images.
---

# Image Converter

To convert an image, run the conversion script:

\`\`\`bash
python scripts/convert.py --input INPUT --output OUTPUT --format FORMAT
\`\`\`

Supported formats: PNG, JPEG, WebP, SVG (to PNG only).
See [references/formats.md](references/formats.md) for format-specific options.
```

### Skill Trigger Design

The skill `description` determines when Copilot activates it. Include:
- **What it does**: "Patterns for testing REST APIs"
- **When to use it**: "Use when writing API tests, mocking HTTP responses"
- **Trigger keywords**: Include terms users might naturally use

### Skills vs Custom Instructions: The Overlap

| Characteristic | Custom Instructions | Skill |
|---------------|-------------------|-------|
| Always loaded | ✅ | ❌ (on demand) |
| Context cost | Constant | Only when relevant |
| Scope | Everything | Specific task type |
| Can include scripts | ❌ | ✅ |
| Can include references | ❌ | ✅ |
| User can enable/disable | Via `/instructions` | Via `/skills` |

**Rule of thumb**: If the guidance applies to >80% of tasks, use custom instructions. Otherwise, use a skill.

---

## Custom Instructions Best Practices

### Keep Instructions Actionable

```markdown
## Build Commands
- `npm run build` - Build the project
- `npm run test` - Run all tests
- `npm run lint:fix` - Fix linting issues

## Code Style
- Use TypeScript strict mode
- Prefer functional components over class components
- Always add JSDoc comments for public APIs

## Workflow
- Run `npm run lint:fix && npm test` after making changes
- Commit messages follow conventional commits format
```

### Instruction File Organization

Use modular path-specific instructions when different rules apply to different parts of the codebase:

```
.github/
├── copilot-instructions.md              # Global: build commands, coding standards
└── instructions/
    ├── frontend.instructions.md         # applyTo: "src/frontend/**"
    ├── api.instructions.md              # applyTo: "src/api/**"
    └── tests.instructions.md            # applyTo: "**/*.test.*"
```

Each path-specific file uses the `applyTo` frontmatter:
```markdown
---
applyTo: "src/frontend/**/*.{ts,tsx}"
---

Use React functional components with hooks.
Follow the component structure in src/frontend/components/Button.tsx as a reference.
```

---

## Hooks: Programmable Guardrails

Hooks let you run shell commands at specific lifecycle moments. They're defined in `.github/hooks/` or `~/.copilot/hooks/`.

### Available Hook Points

| Hook | When It Runs |
|------|-------------|
| `preToolUse` / `postToolUse` | Before/after a tool runs |
| `userPromptSubmitted` | When a user submits a prompt |
| `sessionStart` / `sessionEnd` | At the start/end of a session |
| `errorOccurred` | When an error occurs |
| `agentStop` | When the main agent stops |
| `subagentStop` | When a subagent completes |

### When to Use Hooks vs Other Options

- Need to **block** a tool from running? → Hook (`preToolUse`)
- Need to **log** activity? → Hook (`sessionEnd`)
- Need to **guide** behavior? → Custom Instructions or Skill
- Need **specialist knowledge**? → Custom Agent

---

## Plugins: Packaging Customizations

Plugins bundle skills, custom agents, hooks, and MCP server configs into installable packages.

### When to Create a Plugin

- Distributing a team-wide configuration bundle
- Sharing reusable customizations publicly
- Packaging related skills + agents + hooks together

### When NOT to Create a Plugin

- Experimenting locally (just use local files)
- Single-purpose one-off workflow (a skill is simpler)

Plugins are managed with `/plugin` commands (install, update, list, uninstall).

---

## Testing and Iteration

### Testing Custom Agents

1. **Start with narrow scope** — restrict tools and domain
2. **Test with representative prompts** — try the exact prompts users would send
3. **Check inference triggers** — does the agent activate when expected?
4. **Verify boundaries** — does the agent stay within its defined scope?
5. **Test edge cases** — ambiguous prompts, overlapping agent descriptions

### Testing Skills

1. **Invoke explicitly** — use `/skill-name` to verify it works as expected
2. **Test auto-activation** — use natural prompts that should trigger the skill
3. **Verify scripts** — run any included scripts manually first
4. **Check reference loading** — ensure references are found and useful

### Iterative Refinement

1. Deploy with `disable-model-invocation: true` initially
2. Test with explicit invocation until confident
3. Enable inference once the description is refined
4. Monitor for false positive triggers (agent activating when it shouldn't)
5. Refine description and prompt based on real usage
