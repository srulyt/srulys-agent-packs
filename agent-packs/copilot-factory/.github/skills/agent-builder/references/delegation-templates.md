# Delegation Templates

Reusable delegation patterns for orchestrator agents that coordinate sub-agents through structured workflows.

## `task` Call Shape

Each template below shows the **prompt body** the orchestrator
constructs. The orchestrator must wrap that prompt in a literal
`task` tool call:

```
task(
  agent_type: "<frontmatter-name>",  // "Factory Architect" | "Factory Engineer" | "Factory Critic"
  name: "<short-kebab>",
  description: "<3-5 word summary>",
  mode: "sync",                      // background only when justified
  prompt: "<the prompt body from the matching template below>"
)
```

See [`task-tool-mechanics.md`](task-tool-mechanics.md) for the
canonical template, rules, and full `task` semantics. Never invoke
a sub-agent by writing prose — the only invocation channel is the
`task` tool.

## Architect Delegation

```markdown
Invoke @factory-architect to design the system architecture.

Session: {session-id}
Context: .copilot-factory/sessions/{session-id}/context/user-request.md
Output: .copilot-factory/sessions/{session-id}/artifacts/architecture.md

Requirements:
1. Design for requirement fit, not template compliance
2. Define clear agent boundaries and tool restrictions
3. Include communication and state strategy (if needed)
4. Return implementation-ready architecture
```

## Critic Delegation (Architecture)

```markdown
Invoke @factory-critic to review architecture.

Session: {session-id}
Requirements: .copilot-factory/sessions/{session-id}/context/user-request.md
Architecture: .copilot-factory/sessions/{session-id}/artifacts/architecture.md
Review Type: architecture

Return:
- PASS or BLOCKING
- Blocking issues with remediation
- Optional non-blocking concerns
```

## Critic Delegation (Improvement Analysis)

```markdown
Invoke @factory-critic to analyze and improve an existing agent pack.

Session: {session-id}
Target Pack: {pack-path-or-name}
Requirements: .copilot-factory/sessions/{session-id}/context/user-request.md
Review Type: improvement-analysis

Return:
- Prioritized improvements by category
- Actionable rewrites or diffs where possible
- Recommendation: proceed to implementation workflow or stop
```

## Engineer Delegation (Full Build)

```markdown
Invoke @factory-engineer to implement the system.

Session: {session-id}
Architecture: .copilot-factory/sessions/{session-id}/artifacts/architecture.md
Context: .copilot-factory/sessions/{session-id}/context/user-request.md

Output location: agent-packs/{pack-name}/

Artifacts to generate:
- .github/agents/*.agent.md
- .github/skills/*/SKILL.md
- README.md

Build manifest: .copilot-factory/sessions/{session-id}/artifacts/build-manifest.json

Requirements:
1. Read architecture document completely
2. Generate Copilot CLI artifacts
3. Update build manifest with created files
4. Return summary of what was created
```

## Engineer Delegation (Incremental Improvement)

When `improvement_strategy` is `incremental`:

```markdown
Invoke @factory-engineer to apply incremental improvements.

Session: {session-id}
Improvement Analysis: .copilot-factory/sessions/{session-id}/artifacts/improvement-analysis.md
Context: .copilot-factory/sessions/{session-id}/context/user-request.md
Mode: incremental

Target pack: agent-packs/{pack-name}/

Requirements:
1. Read the improvement analysis document completely
2. Apply ONLY the changes identified in the analysis
3. Preserve all existing content that is not flagged for change
4. Do NOT restructure or rewrite files beyond what the analysis specifies
5. Update build manifest with modified files
6. Return summary of changes applied vs. skipped
```

## Critic Delegation (Implementation)

```markdown
Invoke @factory-critic to review implementation.

Session: {session-id}
Architecture: .copilot-factory/sessions/{session-id}/artifacts/architecture.md
Build Manifest: .copilot-factory/sessions/{session-id}/artifacts/build-manifest.json
Review Type: implementation

Return:
- PASS or BLOCKING
- Architecture alignment findings
- Blocking issues if any
```
