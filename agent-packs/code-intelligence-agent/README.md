# Code Intelligence Agent (CIA)

Reverse-engineer business and technical knowledge from source code into structured markdown knowledge bases.

## Quick Start

### Using with GitHub Copilot CLI

```bash
# Copy the .github folder to your project
cp -r .github /path/to/your/project/

# Start Copilot CLI and invoke the orchestrator
@cia-orchestrator Analyze this codebase and create a knowledge base
```

### Example Prompts

```text
# Greenfield — full codebase analysis
@cia-orchestrator Create a knowledge base for this repository

# Greenfield — scoped analysis
@cia-orchestrator Analyze the authentication and authorization system in this codebase

# Incremental — update existing KB
@cia-orchestrator Update the knowledge base at ./knowledge-base/ with the new payment module

# Targeted question
@cia-orchestrator What business events does this system emit? Document them in a knowledge base.
```

## What It Does

The CIA system performs multi-phase research to extract business and technical knowledge from code:

1. **Intake**: Parses your query, detects research mode (greenfield vs. incremental), creates a session
2. **Discovery**: `@codebase-scout` maps the repository structure, technology stack, and entry points
3. **Analysis**: `@domain-analyst` extracts business capabilities, domain entities, call paths, authorization models, and events
4. **Synthesis**: `@kb-composer` transforms raw findings into polished dual-layer markdown documents
5. **Output**: Orchestrator assembles and writes the final knowledge base

### Key Features

- **Dual-layer output**: Every section has a business summary (for PMs/architects) and technical details (for engineers/AI agents)
- **Full traceability**: Every business assertion links to specific file:function:line references
- **Confidence labeling**: Findings are labeled Explicit, High, or Inferred so readers know what's verified
- **Gap tracking**: Honest accounting of what the KB does NOT cover
- **Incremental updates**: Update an existing KB without regenerating everything

## Agents

| Agent | File | Role | Tools |
|-------|------|------|-------|
| **CIA Orchestrator** | `.github/agents/cia-orchestrator.agent.md` | User-facing coordinator — session management, delegation, quality gates | `read`, `edit`, `search`, `agent` |
| **Codebase Scout** | `.github/agents/codebase-scout.agent.md` | Structure discovery — maps repo topology, tech stack, entry points | `read`, `edit`, `search`, `execute` |
| **Domain Analyst** | `.github/agents/domain-analyst.agent.md` | Knowledge extraction — business logic, authorization, events, domain models | `read`, `edit`, `search`, `execute` |
| **KB Composer** | `.github/agents/kb-composer.agent.md` | Synthesis — transforms findings into polished KB documents | `read`, `edit`, `search` |

### Orchestration Pattern

```text
User Request
    ↓
@cia-orchestrator
    ├── → @codebase-scout   (Phase 2: Discovery)
    ├── → @domain-analyst    (Phase 3: Analysis — iterative)
    ├── → @kb-composer       (Phase 4: Synthesis)
    └── Final KB Assembly    (Phase 5: Output)
```

The orchestrator enforces quality gates between each phase and supports up to 3 iterations per focus area to refine incomplete findings.

## Skills

| Skill | File | Purpose | Used By |
|-------|------|---------|---------|
| **Code Analysis Patterns** | `.github/skills/code-analysis-patterns/SKILL.md` | Business logic detection across frameworks — authorization, events, domain models, API mappings | `@domain-analyst` |
| **Knowledge Extraction** | `.github/skills/knowledge-extraction/SKILL.md` | Finding schema, confidence labeling, traceability rules, incremental update protocol | `@domain-analyst`, `@kb-composer` |
| **Knowledge Base Structure** | `.github/skills/knowledge-base-structure/SKILL.md` | KB template, section rules, dual-layer format, quality lint rules | `@kb-composer`, `@cia-orchestrator` |

## KB Output Structure

The generated knowledge base follows this structure:

```
knowledge-base/
├── README.md                       # Overview, scope, reading guide
├── architecture/
│   ├── system-overview.md          # High-level system architecture
│   ├── tech-stack.md               # Technologies, frameworks, dependencies
│   └── module-map.md               # Module purposes and boundaries
├── business-capabilities/
│   └── {capability-name}.md        # One file per major capability
├── domain-model/
│   ├── entities.md                 # Core entities and relationships
│   └── glossary.md                 # Business term → technical term mapping
├── flows/
│   └── {flow-name}.md              # End-to-end business flows
├── api-surface/
│   └── endpoints.md                # API endpoints → business operations
├── authorization/
│   └── access-model.md             # Roles, permissions, enforcement
├── events/
│   └── event-catalog.md            # Business events and telemetry
└── _metadata/
    ├── generation-log.md           # Provenance and coverage summary
    └── gaps.md                     # Known gaps for human review
```

### Dual-Layer Format

Every content section has two layers:

```markdown
## Order Cancellation

Customers can cancel orders before shipment. The process reverses payments,
releases inventory, and notifies fulfillment. Only the order owner or admin
can cancel.

### Technical Implementation

| Aspect | Details |
|--------|---------|
| Primary Location | `src/orders/cancellation/` |
| Entry Points | `POST /api/orders/:id/cancel` |
| Key Functions | `OrderService.cancel()`, `PaymentService.reverse()` |

### Evidence

| Assertion | Confidence | Source |
|-----------|------------|--------|
| Only owner or admin can cancel | Explicit | `src/middleware/auth.ts:45` |
| Payment reversed on cancel | High | `src/services/order.ts:240` |
```

## Research Modes

### Greenfield Mode

Creates a complete knowledge base from scratch. Triggered when:
- No existing KB path is provided
- User says "create", "build", or "generate"

The scout performs full codebase discovery, the analyst covers all focus areas, and the composer generates the complete KB template.

### Incremental Mode

Updates an existing knowledge base. Triggered when:
- An existing KB path is provided
- User says "update", "add to", "extend", or "refresh"

The scout performs targeted discovery, the analyst identifies deltas, and the composer produces targeted section updates that preserve existing structure and tone.

## State Management

Session state is stored in `.code-intel-stm/` (add to `.gitignore`):

```
.code-intel-stm/
├── current-session.json
└── runs/{session-id}/
    ├── state.json
    ├── context/
    └── agents/
        ├── codebase-scout/
        ├── domain-analyst/
        └── kb-composer/
```

## Installation

1. Copy the `.github/` folder from this pack to your project root
2. Ensure your project has a `.gitignore` entry for `.code-intel-stm/`
3. Invoke `@cia-orchestrator` in GitHub Copilot CLI

## Troubleshooting

**Agent not found**: Ensure `.github/agents/` is in your project root.

**Skill not loading**: Check that `.github/skills/` exists with valid `SKILL.md` files.

**Session recovery**: If a session was interrupted, the orchestrator will attempt to resume from the last completed phase. Delete `.code-intel-stm/` to start fresh.

**Large codebase timeouts**: The system uses chunked discovery and scoped analysis. For very large monorepos, start with a scoped query targeting specific modules rather than full-codebase analysis.

**Orchestrator doing analysis itself**: If the orchestrator explores code directly instead of delegating to specialists, ensure you're invoking `@cia-orchestrator` (not a specialist directly) and that all `.github/agents/*.agent.md` files are present in your project.

## License

MIT
