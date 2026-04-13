# Agent Topology Patterns

Detailed patterns for structuring multi-agent systems.

## Hierarchical Pattern

```
           ┌─────────────┐
           │ Orchestrator│
           └──────┬──────┘
        ┌─────────┼─────────┐
        ▼         ▼         ▼
   ┌────────┐ ┌────────┐ ┌────────┐
   │Agent A │ │Agent B │ │Agent C │
   └────────┘ └────────┘ └────────┘
```

**Characteristics**:
- Single point of coordination
- Clear delegation paths
- Orchestrator manages workflow

**Best For**:
- Complex multi-phase workflows
- When user interaction should be centralized
- Factory-style systems

**Implementation**:
- Orchestrator has `agent` tool for delegation
- Specialists have restricted tools
- State managed by orchestrator

## Flat Pattern

```
   ┌────────┐   ┌────────┐   ┌────────┐
   │Agent A │   │Agent B │   │Agent C │
   └────────┘   └────────┘   └────────┘
       │             │             │
       └─────────────┴─────────────┘
                     │
               (User selects)
```

**Characteristics**:
- No central coordinator
- User chooses agent directly
- Independent operation

**Best For**:
- Specialized tools that don't interact
- User knows which agent to use
- Simple, focused tasks

**Implementation**:
- Each agent is self-contained
- No inter-agent communication
- User manages workflow

## Pipeline Pattern

```
   ┌────────┐     ┌────────┐     ┌────────┐
   │ Input  │────▶│Process │────▶│ Output │
   │ Agent  │     │ Agent  │     │ Agent  │
   └────────┘     └────────┘     └────────┘
```

**Characteristics**:
- Sequential processing
- Each stage transforms data
- Clear input/output contracts

**Best For**:
- Data transformation workflows
- When each stage is distinct
- Linear processes

**Implementation**:
- Artifacts passed between stages
- Each agent reads from previous output
- Final agent produces deliverable

## Hub-and-Spoke Pattern

```
                ┌────────┐
                │Spoke A │
                └───┬────┘
                    │
   ┌────────┐   ┌───┴───┐   ┌────────┐
   │Spoke B │◀──│  Hub  │──▶│Spoke C │
   └────────┘   └───┬───┘   └────────┘
                    │
                ┌───┴────┐
                │Spoke D │
                └────────┘
```

**Characteristics**:
- Central coordinator (hub)
- Specialists (spokes) for specific tasks
- Hub manages all communication

**Best For**:
- When specialists need to collaborate
- Complex decision trees
- Review/approval workflows

**Implementation**:
- Hub has full tool access
- Spokes have restricted scope
- All communication through hub

## Choosing a Pattern

| Criteria | Recommended Pattern |
|----------|-------------------|
| Complex workflow | Hierarchical |
| Independent tasks | Flat |
| Sequential processing | Pipeline |
| Collaborative specialists | Hub-and-Spoke |
| User-driven selection | Flat |
| Automated coordination | Hierarchical |

## Hybrid Approaches

Real systems often combine patterns:

**Factory Pattern** (Hierarchical + Pipeline):
```
Orchestrator
    │
    ├── Critic (improvement analysis, if improvement mode)
    │
    ├── Architect (design phase)
    │
    ├── Critic (architecture review)
    │
    ├── Engineer (build phase)
    │
    └── Critic (implementation review)
```

**Review System** (Hub-and-Spoke + Flat):
```
     ┌─────────────┐
     │  Reviewer   │◀── User
     └──────┬──────┘
   ┌────────┼────────┐
   ▼        ▼        ▼
┌─────┐ ┌─────┐ ┌─────┐
│Code │ │Docs │ │Tests│
└─────┘ └─────┘ └─────┘
```
