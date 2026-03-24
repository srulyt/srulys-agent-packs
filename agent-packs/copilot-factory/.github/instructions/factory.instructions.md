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
│       ├── state.json       # Workflow state (includes target_platform)
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
- **State file**: `state.json` contains workflow phase, target platform, and deliverables
- **Artifacts**: Generated architecture and build manifests go in `artifacts/`
- **User context**: Original requirements saved in `context/user-request.md`

### Target Platform

The Factory defaults to **Copilot CLI** (`copilot`) output. Only generates Roo Code (`roo`) artifacts if the user explicitly requests it.

| Target | Value | Generated Artifacts |
|--------|-------|---------------------|
| Copilot CLI (default) | `copilot` | `.github/agents/*.agent.md`, `.github/skills/*/SKILL.md` |
| Roo Code | `roo` | `.roomodes`, `.roo/rules-*/rules.md` |

Check `state.json.target_platform` for the current session's target.

### Workflow Phases

1. **intake**: Validate requirements, set target platform (defaults to `copilot`)
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
