# Delegation Templates

Reusable delegation patterns for orchestrator agents that coordinate sub-agents through structured workflows.

## Architect Delegation

```markdown
Invoke @factory-architect to design the system architecture.

Session: {session-id}
Context: .copilot-factory/sessions/{session-id}/context/user-request.md
Target Platform: {target_platform}
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
Target Platform: {target_platform}

Output location: agent-packs/{pack-name}/

Artifacts to generate:
- If roo: .roomodes, .roo/rules-{slug}/rules.md
- If copilot: .github/agents/*.agent.md, .github/skills/*/SKILL.md
- Always: README.md

Build manifest: .copilot-factory/sessions/{session-id}/artifacts/build-manifest.json

Requirements:
1. Read architecture document completely
2. Check target_platform in state.json
3. Generate artifacts for selected target ONLY
4. Update build manifest with created files
5. Return summary of what was created
```

## Engineer Delegation (Incremental Improvement)

When `improvement_strategy` is `incremental`:

```markdown
Invoke @factory-engineer to apply incremental improvements.

Session: {session-id}
Improvement Analysis: .copilot-factory/sessions/{session-id}/artifacts/improvement-analysis.md
Context: .copilot-factory/sessions/{session-id}/context/user-request.md
Target Platform: {target_platform}
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
