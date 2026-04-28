---
applyTo: ".copilot-factory/**"
---

## Copilot Factory Context

This workspace contains the Copilot Factory system for creating multi-agent packs.

### Directory Structure

```
.copilot-factory/
├── current-session.json     # Pointer to active session
├── sessions/                # Active factory sessions
│   └── {session-id}/
│       ├── state.json       # Workflow state
│       ├── context/         # Input files
│       │   ├── user-request.md
│       │   └── decisions.md
│       └── artifacts/       # Output files
│           ├── architecture.md
│           └── build-manifest.json
└── history/                 # Archived sessions
```

### Working with Factory Sessions

- **Session ID format**: `{YYYY-MM-DD}-{8-char-hex}` (e.g., `2026-02-23-a1b2c3d4`)
- **State file**: `state.json` contains workflow phase and deliverables
- **Artifacts**: Generated architecture and build manifests go in `artifacts/`
- **User context**: Original requirements saved in `context/user-request.md`

### Workflow Phases

1. **intake**: Validate requirements
2. **improve-analysis** (improvement mode): Analyze existing pack and prioritize improvements
3. **design**: Create system architecture
4. **review-arch**: Validate architecture
5. **approval**: Get user approval
6. **build**: Generate artifacts
7. **review-prompts**: Validate implementation
8. **complete**: Present results

### Quality Standards

- All generated agents must have clear descriptions with trigger keywords
- Tools must be appropriately restricted per agent role
- Skills must be under 5,000 words with references for details
- Agents must be under 30,000 characters

### State Updates

When modifying `state.json`:
1. Read current state
2. Update relevant fields
3. Always update `updated_at` timestamp
4. Write complete file (no partial updates)

### Agent Delegation Model

Only `@copilot-factory` communicates with users. Sub-agents (`@factory-architect`, `@factory-engineer`, `@factory-critic`) are invoked by the orchestrator and return results to it. Do not invoke sub-agents directly.

### Common Pitfalls

- Do not manually edit `state.json` while a session is in progress
- Always use complete file writes (read → modify → write), never partial JSON updates
- The `improve-analysis` phase only applies to `mode: "improvement"` sessions
