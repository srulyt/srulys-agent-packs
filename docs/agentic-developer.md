# Agentic Developer Pack

## Overview

A workflow-first, spec-driven development system for large-scale coding tasks. This pack implements a multi-agent architecture with resumable state, quality gates, and memory consolidation.

**Primary Use Case**: Legacy codebase development (C#/SQL) requiring structured planning, task decomposition, and PR-conscious implementation.

## Location

`agent-packs/agentic-developer/`

## Agents

| Agent | Slug | Responsibility |
|-------|------|----------------|
| Orchestrator | `agentic-orchestrator` | Central coordinator; manages workflow phases and quality gates |
| Spec Writer | `agentic-spec-writer` | Creates PRDs from user requirements |
| Bootstrap Planner | `agentic-bootstrap-planner` | Creates comprehensive project setup plans for new/empty workspaces |
| Planner | `agentic-planner` | Designs implementation plans and architecture decisions |
| Task Breaker | `agentic-task-breaker` | Decomposes plans into executable task DAGs |
| Executor | `agentic-executor` | Implements individual tasks with strict context boundaries |
| Verifier | `agentic-verifier` | Validates work against acceptance criteria |
| Cleanup | `agentic-cleanup` | Removes AI artifacts and PR noise |
| PR Prep | `agentic-pr-prep` | Final verification and PR checklist generation |
| Memory Consolidator | `agentic-memory-consolidator` | Promotes learnings from STM to LTM |

## Orchestration Flow

The pack now supports a **Unified Workflow** with 12 sequential phases (0-11) that combines bootstrap and development into a single session.

```text
User Request
    ↓
┌─────────────────────────────────────────────────────────────┐
│  Phase 0: INTAKE                                            │
│  Orchestrator assesses task, routes to Spec Writer if needed│
└─────────────────────────────────────────────────────────────┘
    ↓
┌─────────────────────────────────────────────────────────────┐
│  Phase 1: PRD CREATION                                      │
│  Spec Writer creates Product Requirements Document          │
└─────────────────────────────────────────────────────────────┘
    ↓
┌─────────────────────────────────────────────────────────────┐
│  Phase 2: BOOTSTRAP DETECTION                               │
│  Orchestrator checks if workspace needs bootstrap           │
│  (Routes to Phase 7 if no bootstrap needed)                 │
└─────────────────────────────────────────────────────────────┘
    ↓ (if bootstrap needed)
┌─────────────────────────────────────────────────────────────┐
│  Phase 3: DEPENDENCY CHECK                                  │
│  Bootstrap Planner detects missing CLI tools                │
│  Generates install scripts if needed                        │
│  (User runs scripts before continuing)                      │
└─────────────────────────────────────────────────────────────┘
    ↓
┌─────────────────────────────────────────────────────────────┐
│  Phase 4: BOOTSTRAP PLANNING                                │
│  Bootstrap Planner creates comprehensive project plan       │
└─────────────────────────────────────────────────────────────┘
    ↓
┌─────────────────────────────────────────────────────────────┐
│  Phase 5: BOOTSTRAP TASK BREAKDOWN                          │
│  Task Breaker creates B-tasks (B001, B002, ...)             │
└─────────────────────────────────────────────────────────────┘
    ↓
┌─────────────────────────────────────────────────────────────┐
│  Phase 6: BOOTSTRAP APPROVAL GATE                           │
│  User chooses:                                              │
│  • "Approve Bootstrap" - pause after bootstrap              │
│  • "Approve and Continue" - proceed to development          │
└─────────────────────────────────────────────────────────────┘
    ↓
┌─────────────────────────────────────────────────────────────┐
│  Phase 7: DEVELOPMENT PLANNING                              │
│  Planner designs implementation approach                    │
└─────────────────────────────────────────────────────────────┘
    ↓
┌─────────────────────────────────────────────────────────────┐
│  Phase 8: DEVELOPMENT APPROVAL GATE                         │
│  User approves D-tasks before execution                     │
│  (Skipped if "Approve and Continue" was selected)           │
└─────────────────────────────────────────────────────────────┘
    ↓
┌─────────────────────────────────────────────────────────────┐
│  Phase 9: EXECUTION + VERIFICATION LOOP                     │
│  Execute B-tasks first (if any), then D-tasks               │
│  Verifier runs every 3 tasks                                │
└─────────────────────────────────────────────────────────────┘
    ↓
┌─────────────────────────────────────────────────────────────┐
│  Phase 10: CLEANUP + PR PREP                                │
│  Cleanup → PR Prep → Final checklist                        │
└─────────────────────────────────────────────────────────────┘
    ↓
┌─────────────────────────────────────────────────────────────┐
│  Phase 11: MEMORY CONSOLIDATION (Post-Merge)                │
│  Memory Consolidator promotes learnings to context packs    │
└─────────────────────────────────────────────────────────────┘
```

### Phase Overview Table

| Phase | Name | Agent | Gate? |
|-------|------|-------|-------|
| 0 | Intake | Orchestrator | No |
| 1 | PRD | Spec Writer | No |
| 2 | Bootstrap Detection | Orchestrator | No |
| 3 | Dependency Check | Bootstrap Planner | User action* |
| 4 | Bootstrap Planning | Bootstrap Planner | No |
| 5 | Bootstrap Tasks | Task Breaker | No |
| 6 | Bootstrap Approval | Orchestrator | **Yes** |
| 7 | Development Planning | Planner | No |
| 8 | Development Approval | Orchestrator | **Yes** |
| 9 | Execution | Executor + Verifier | No |
| 10 | Cleanup | Cleanup + PR Prep | No |
| 11 | Consolidation | Memory Consolidator | No |

*Phase 3 pauses for user to run install scripts if dependencies are missing.

## Memory Architecture

### Short-Term Memory (STM)
- Location: `.agent-memory/runs/<run-id>/`
- Contains: PRD, plan, task-graph, events, verifications
- Lifecycle: Per-run, archived after completion

### Long-Term Memory (LTM)
- Location: `.context-packs/`
- Contains: Durable codebase knowledge, patterns, gotchas
- Updated: Post-merge via Memory Consolidator

## Installation

### Option 1: Direct Use

```bash
code agent-packs/agentic-developer
```

### Option 2: Copy to Project

```bash
cp agent-packs/agentic-developer/.roomodes /path/to/your/project/
cp -r agent-packs/agentic-developer/.roo /path/to/your/project/
```

### Option 3: Symlink

```bash
ln -s /path/to/agent-packs/agentic-developer/.roomodes .roomodes
ln -s /path/to/agent-packs/agentic-developer/.roo .roo
```

## Usage

1. Activate `agentic-orchestrator` mode
2. Describe your development task
3. Orchestrator routes through phases automatically
4. Approve plan at Phase 1 gate
5. Review PR checklist at completion

### Task Sizing

| Size | Characteristics | Workflow |
|------|----------------|----------|
| SMALL | Single file, clear requirements | May skip detailed planning |
| MEDIUM | Multi-file, some complexity | Standard planning flow |
| LARGE | Cross-cutting, architectural | Full planning + task breakdown |

### Unified Workflow

The Agentic Developer now supports a **unified workflow** that combines bootstrap and development into a single session. This eliminates the need to run separate workflows for new projects.

#### Key Benefits

1. **Single Approval Flow**: User approves bootstrap and optionally development in one step
2. **Dependency Detection**: Missing CLI tools are detected before planning begins
3. **Seamless Transition**: Bootstrap tasks flow directly into development tasks
4. **Resume Support**: Can resume at any phase after interruption

#### Two-Option Approval Gate (Phase 6)

At the Bootstrap Approval Gate, users choose:

| Option | Behavior |
|--------|----------|
| **"Approve Bootstrap"** | Execute bootstrap tasks, then pause for separate development approval |
| **"Approve and Continue"** | Execute bootstrap tasks AND proceed directly to development (skips Phase 8 gate) |

### Dependency Handling (Phase 3)

Before full planning begins, the Bootstrap Planner runs in **Dependency Check Mode** to detect missing development tools.

#### Detected Tools

| Category | Tools Detected |
|----------|----------------|
| Runtime | Node.js, Python, Rust, Go, Java, .NET, Ruby, PHP |
| Package Managers | npm, pnpm, yarn, pip, cargo, maven, gradle, composer |
| Version Control | Git |
| Containers | Docker, kubectl |
| Build Tools | make, cmake |

#### Dependency Artifacts

When missing dependencies are detected:

1. **Dependency Report** (`dependency-report.md`) - Lists all required tools with status
2. **Install Script** - Platform-specific installation script:
   - Windows: `install-dependencies.ps1` (uses winget/chocolatey)
   - Unix/macOS: `install-dependencies.sh` (uses brew/apt/dnf/pacman)

#### User Action Required

If dependencies are missing, the workflow pauses:

```text
┌─────────────────────────────────────────────────────────────┐
│  Missing Dependencies Detected                              │
│                                                             │
│  The following tools are required but not installed:        │
│  • Node.js (v18+)                                           │
│  • Docker                                                   │
│                                                             │
│  To install, run:                                           │
│  .\install-dependencies.ps1     (Windows)                   │
│  ./install-dependencies.sh      (macOS/Linux)               │
│                                                             │
│  After installation, type "continue" to proceed.            │
└─────────────────────────────────────────────────────────────┘
```

### Bootstrap Capability (New Projects)

When working with an **empty or near-empty workspace**, the orchestrator automatically detects this (Phase 2) and routes through the bootstrap workflow (Phases 3-6).

#### When Bootstrap is Triggered

- User explicitly mentions "new project", "bootstrap", "create from scratch", "greenfield"
- Workspace has no source files or project manifests (`package.json`, `pyproject.toml`, etc.)

#### Bootstrap Phases

| Phase | Action |
|-------|--------|
| 2 | Detection - Orchestrator identifies need for bootstrap |
| 3 | Dependency Check - Verify CLI tools are installed |
| 4 | Bootstrap Planning - Create comprehensive project plan |
| 5 | Task Breakdown - Generate B-tasks (B001, B002, ...) |
| 6 | Approval Gate - User approves bootstrap plan |

#### Technology Decisions

The Bootstrap Planner evaluates and documents decisions across 12 categories:

| Category | Examples |
|----------|----------|
| Language/Runtime | TypeScript, Python, Rust, Go |
| Package Management | npm, pnpm, pip, cargo |
| Project Type | CLI, API, Web App, Library |
| Framework | Express, FastAPI, Actix |
| Architecture | Monolith, Microservices, Serverless |
| Database | PostgreSQL, SQLite, MongoDB |
| Caching | Redis, in-memory, none |
| Testing | Jest, pytest, testing frameworks |
| Deployment | Docker, serverless, traditional |
| Tooling | ESLint, Prettier, CI/CD |
| API Design | REST, GraphQL, gRPC |
| Observability | Logging, metrics, tracing |

#### Bootstrap Plan Artifacts

- `bootstrap-plan.md` - Comprehensive project setup plan
- `research/technology-evaluation.md` - Research and comparison notes
- `adrs/ADR-*.md` - Architecture Decision Records for major choices

## Configuration

### Context Packs

Place codebase knowledge in `.context-packs/`:
- `architecture_context.md` - System overview
- `patterns_context.md` - Common patterns
- `<area>_context.md` - Area-specific knowledge

### Constitution

After plan approval, `constitution.md` defines:
- Allowed/forbidden modifications
- Code standards
- Quality gates
- Forbidden patterns

## Pack Structure

```
agentic-developer/
├── .roomodes                              # Mode definitions (10 agents)
├── .roo/
│   ├── docs/                              # Pack-internal docs
│   ├── rules/                             # Global rules (all agents)
│   │   └── agentic-global.md
│   ├── rules-agentic-orchestrator/        # Orchestrator rules
│   │   ├── 01-orchestration-workflow.md   # Phase definitions
│   │   ├── 02-phase-management.md         # Phase transitions
│   │   └── 03-resume-protocol.md          # Resume handling
│   ├── rules-agentic-bootstrap-planner/   # Bootstrap planner rules
│   │   ├── 01-bootstrap-planning-process.md
│   │   └── 04-dependency-detection.md     # Dependency check logic
│   ├── rules-agentic-executor/            # Executor-specific
│   ├── rules-agentic-*/                   # Other agent rules
│   └── templates/                         # Artifact templates
│       ├── agentic-bootstrap-plan.md      # Bootstrap plan template
│       ├── agentic-bootstrap-research.md  # Research document template
│       ├── agentic-bootstrap-adr.md       # ADR template
│       ├── agentic-dependency-report.md   # Dependency report template
│       ├── agentic-install-deps-windows.ps1  # Windows install script
│       ├── agentic-install-deps-unix.sh   # Unix/macOS install script
│       └── agentic-workflow-state.json    # Workflow state schema
└── README.md
```

## Version History

| Version | Date | Changes |
|---------|------|---------|
| 2.0.0 | 2026-01-24 | Unified workflow with 12 phases, dependency detection, dual approval gates |
| 1.0.0 | Initial | Original 5-phase workflow |
