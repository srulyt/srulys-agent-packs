# Context Pack Integration for Agentic Modes

Context packs provide domain knowledge to agentic modes. They are **simple markdown files**, not YAML manifests.

## Location

```
.context-packs/
├── {feature}_context.md           # Feature-specific packs
└── horizontal/
    └── {capability}_context.md    # Cross-cutting capability packs
```

## Format

Each context pack is a markdown file with 12 standard sections:

1. Overview
2. Architecture
3. Key Components
4. Data Flow
5. Dependencies
6. Configuration
7. Common Patterns
8. Testing Approach
9. Gotchas & Pitfalls
10. Recent Changes
11. Related Context Packs
12. Quick Reference

See `.roo/rules-cp-writer/01-output-format.md` for the full template.

## Usage by Agentic Modes

| Mode                | Usage                                                   |
| ------------------- | ------------------------------------------------------- |
| Orchestrator        | Load relevant packs at run start based on task keywords |
| Spec Writer         | Reference patterns and constraints in PRD               |
| Planner             | Understand area boundaries for planning                 |
| Executor            | Follow patterns, avoid documented gotchas               |
| Memory Consolidator | Update context packs with new learnings                 |

## Loading Context Packs

1. Identify relevant packs from task description keywords
2. Read the markdown file directly with `read_file`
3. Focus on sections relevant to current task
4. For large packs, read specific sections rather than entire file

## Creating/Updating Context Packs

Use the `cp-*` agent pack (cp-orchestrator, cp-discovery, cp-analyzer, cp-synthesizer, cp-writer) to create new context packs or update existing ones.
