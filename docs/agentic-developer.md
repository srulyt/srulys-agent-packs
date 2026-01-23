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

```text
User Request
    ↓
┌─────────────────────────────────────────────────────────────┐
│  Phase 0: INTAKE                                            │
│  Orchestrator assesses task, routes to Spec Writer if needed│
└─────────────────────────────────────────────────────────────┘
    ↓
┌─────────────────────────────────────────────────────────────┐
│  Phase 1: PLANNING (GATE - User Approval Required)         │
│  Planner → Task Breaker → Constitution created             │
└─────────────────────────────────────────────────────────────┘
    ↓
┌─────────────────────────────────────────────────────────────┐
│  Phase 2: EXECUTION + VERIFICATION LOOP                    │
│  Executor (per task) → Verifier (every 3 tasks)            │
└─────────────────────────────────────────────────────────────┘
    ↓
┌─────────────────────────────────────────────────────────────┐
│  Phase 3: CLEANUP + PR PREP                                │
│  Cleanup → PR Prep → Final checklist                       │
└─────────────────────────────────────────────────────────────┘
    ↓
┌─────────────────────────────────────────────────────────────┐
│  Phase 4: MEMORY CONSOLIDATION (Post-Merge)                │
│  Memory Consolidator promotes learnings to context packs   │
└─────────────────────────────────────────────────────────────┘
```

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

### Bootstrap Capability (New Projects)

When working with an **empty or near-empty workspace**, the orchestrator automatically detects this and routes to the Bootstrap Planner instead of the standard Planner.

#### When Bootstrap is Triggered

- User explicitly mentions "new project", "bootstrap", "create from scratch", "greenfield"
- Workspace has no source files or project manifests (`package.json`, `pyproject.toml`, etc.)

#### Bootstrap Workflow

```text
User Request (new project)
    ↓
┌─────────────────────────────────────────────────────────────┐
│  Phase 0.5: BOOTSTRAP DETECTION                             │
│  Orchestrator detects empty workspace → Bootstrap Planner   │
└─────────────────────────────────────────────────────────────┘
    ↓
┌─────────────────────────────────────────────────────────────┐
│  Bootstrap Planner creates:                                 │
│  - Technology research document                             │
│  - Architecture Decision Records (ADRs)                     │
│  - Comprehensive bootstrap-plan.md                          │
└─────────────────────────────────────────────────────────────┘
    ↓
┌─────────────────────────────────────────────────────────────┐
│  Task Breaker decomposes bootstrap plan into B-tasks        │
│  (B001, B002, ... B999)                                     │
└─────────────────────────────────────────────────────────────┘
    ↓
    (Standard execution flow continues)
```

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
│   ├── rules-agentic-orchestrator/        # Orchestrator-specific
│   ├── rules-agentic-bootstrap-planner/   # Bootstrap planner rules
│   ├── rules-agentic-executor/            # Executor-specific
│   ├── rules-agentic-*/                   # Other agent rules
│   └── templates/                         # Artifact templates
│       ├── agentic-bootstrap-plan.md      # Bootstrap plan template
│       ├── agentic-bootstrap-research.md  # Research document template
│       └── agentic-bootstrap-adr.md       # ADR template
└── README.md
```
