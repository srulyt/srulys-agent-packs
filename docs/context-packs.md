# Context Packs Agent Pack

## Overview

A multi-agent system for creating comprehensive context packs from legacy codebases. Context packs are structured documentation that captures architecture, contracts, patterns, and change guidance, enabling confident agentic development on unfamiliar systems.

**Primary Use Case**: Creating structured documentation for legacy codebases (C#/SQL, Java, TypeScript, etc.) where developers need to understand complex systems quickly without losing context.

## Location

`agent-packs/context-packs/`

## Agents

| Agent | Slug | Responsibility |
|-------|------|----------------|
| Orchestrator | `cp-orchestrator` | Coordinates context pack creation workflow, manages phases and delegates to specialists |
| Discovery | `cp-discovery` | Finds relevant file paths using search strategies without reading full file contents |
| Analyzer | `cp-analyzer` | Reads and analyzes source files in batches, extracting key information for specific sections |
| Synthesizer | `cp-synthesizer` | Combines multiple analysis notes into coherent, well-structured draft sections |
| Writer | `cp-writer` | Produces the final polished context pack document with quality checks |

## Orchestration Flow

```text
User Request
    ↓
┌─────────────────────────────────────────────────────────────┐
│  Phase 0: INITIALIZE                                        │
│  Orchestrator creates task ID, temp directory, manifest     │
└─────────────────────────────────────────────────────────────┘
    ↓
┌─────────────────────────────────────────────────────────────┐
│  Phase 1: DISCOVERY                                         │
│  cp-discovery → Finds code, test, config, dependency paths  │
└─────────────────────────────────────────────────────────────┘
    ↓
┌─────────────────────────────────────────────────────────────┐
│  Phase 2: ANALYSIS (Batched)                                │
│  cp-analyzer → Processes files in batches by section target │
│  Multiple analysis rounds for different focus areas         │
└─────────────────────────────────────────────────────────────┘
    ↓
┌─────────────────────────────────────────────────────────────┐
│  Phase 3: SYNTHESIS                                         │
│  cp-synthesizer → Combines notes, resolves conflicts        │
└─────────────────────────────────────────────────────────────┘
    ↓
┌─────────────────────────────────────────────────────────────┐
│  Phase 4: WRITING                                           │
│  cp-writer → Produces final formatted context pack          │
└─────────────────────────────────────────────────────────────┘
    ↓
┌─────────────────────────────────────────────────────────────┐
│  Phase 5: CLEANUP                                           │
│  Orchestrator updates manifest, optionally clears temp      │
└─────────────────────────────────────────────────────────────┘
```

## Context Pack Structure

The output context pack contains 12 standard sections:

| Section | Purpose |
|---------|---------|
| 1. Overview & Purpose | Business purpose, responsibilities, stakeholders |
| 2. Architectural Overview | Component structure, layers, control flow |
| 3. Entry Points & Triggers | APIs, events, jobs, schedules |
| 4. Code Inventory | Categorized file listing by responsibility |
| 5. Public Contracts | API schemas, event payloads, configuration |
| 6. Dependencies | Internal modules, external services, infrastructure |
| 7. Domain Concepts | Glossary of business terms and their code representation |
| 8. Patterns & Practices | Established patterns and anti-patterns to avoid |
| 9. Constraints & Risks | Invariants, high-risk areas, compatibility requirements |
| 10. Test Strategy | Test inventory, patterns, coverage gaps |
| 11. Change Guidance | Safe modification areas, validation requirements |
| 12. Open Questions | Unverified assumptions, known gaps, follow-ups |

Each section includes a **confidence score** (1-5) indicating reliability of the information.

## Working Directory Structure

```
.context-packs/
├── _temp/                          # Working directory (per task)
│   └── {task_id}/
│       ├── manifest.json           # Task state and progress
│       ├── discovery/
│       │   ├── code_paths.md
│       │   ├── test_paths.md
│       │   ├── config_paths.md
│       │   └── dependencies.md
│       ├── analysis/
│       │   ├── 01_overview.md
│       │   ├── 02_architecture.md
│       │   └── ...
│       └── synthesis/
│           └── draft.md
├── {feature}_context.md            # Final feature context packs
└── horizontal/                     # Horizontal capability packs
    └── {capability}_context.md
```

## Installation

### Option 1: Direct Use

```bash
code agent-packs/context-packs
```

### Option 2: Copy to Project

```bash
cp agent-packs/context-packs/.roomodes /path/to/your/project/
cp -r agent-packs/context-packs/.roo /path/to/your/project/
```

### Option 3: Symlink

```bash
ln -s /path/to/agent-packs/context-packs/.roomodes .roomodes
ln -s /path/to/agent-packs/context-packs/.roo .roo
```

## Usage

### Basic Invocation

1. Activate `cp-orchestrator` mode
2. Request a context pack:

```
Create a context pack for [feature/capability name]

Business Context: [description of what it does]
Known Code Paths: [optional hints about where code lives]
Naming Conventions: [optional patterns to search for]
```

### Example Request

```
Create a context pack for WorkspaceInfo

Business Context: Handles workspace metadata retrieval and caching for the 
admin console. Provides API endpoints for workspace details, scanner status, 
and admin operations.

Known Code Paths:
- src/AdminConsoleApi/Controllers/WorkspaceInfoController.cs
- src/AdminConsoleApi/Managers/

Naming Conventions:
- Controllers end with "Controller"
- Managers end with "Manager"
- Data access uses "DataAccess" suffix
```

### Pack Types

| Type | When to Use | Output Location |
|------|-------------|-----------------|
| Feature (Vertical) | Specific feature spanning multiple layers | `.context-packs/{name}_context.md` |
| Horizontal | Cross-cutting capability (logging, auth) | `.context-packs/horizontal/{name}_context.md` |

## Configuration

### Context Pack Directory

Ensure the `.context-packs/` directory exists in your project root. The orchestrator will create it if needed.

### Batching Strategy

The analyzer processes files in batches to manage context limits:

| Batch Target | Focus Areas |
|--------------|-------------|
| Overview & Architecture | Entry points, managers, core services |
| Contracts & APIs | Controllers, DTOs, event handlers |
| Patterns & Practices | Domain logic, utilities, extensions |
| Tests & Dependencies | Test files, integration points |

Large codebases may require multiple analysis rounds.

## Confidence Scores

Each section includes a confidence score based on:

| Score | Meaning |
|-------|---------|
| 5/5 | High confidence - multiple corroborating sources |
| 4/5 | Good confidence - clear evidence with minor gaps |
| 3/5 | Moderate confidence - some uncertainty or conflicts |
| 2/5 | Low confidence - limited sources or significant gaps |
| 1/5 | Minimal confidence - sparse data, many assumptions |

**Aggregation**: Section confidence is calculated from contributing findings, reduced for conflicts or gaps.

## Pack Structure

```
context-packs/
├── .roomodes                           # Mode definitions (5 agents)
├── .roo/
│   ├── rules-cp-orchestrator/          # Orchestrator rules
│   │   ├── 01-orchestration-process.md
│   │   └── 02-task-management.md
│   ├── rules-cp-discovery/             # Discovery agent rules
│   │   └── 01-discovery-process.md
│   ├── rules-cp-analyzer/              # Analyzer agent rules
│   │   └── 01-analysis-process.md
│   ├── rules-cp-synthesizer/           # Synthesizer agent rules
│   │   └── 01-synthesis-process.md
│   └── rules-cp-writer/                # Writer agent rules
│       └── 01-output-format.md
└── README.md
```

## Best Practices

### For Discovery

- Provide known code paths when possible
- Specify naming conventions to improve search accuracy
- For large codebases, start with a focused area

### For Analysis

- Files are analyzed in batches to avoid context overflow
- Confidence scores reflect evidence quality
- Uncertainties are tracked for follow-up

### For Output

- Review the Open Questions section for gaps
- Low-confidence sections may need manual verification
- Context packs are living documents—update as knowledge grows

## Limitations

- **Context Window**: Large codebases require batched analysis
- **Binary Files**: Cannot analyze compiled or binary artifacts
- **Dynamic Behavior**: Runtime behavior must be inferred from code
- **External Documentation**: Doesn't automatically incorporate wikis or external docs

## Related Packs

- [Agentic Developer](./agentic-developer.md) - Uses context packs for development tasks
- [Factory](./factory.md) - Created this pack
