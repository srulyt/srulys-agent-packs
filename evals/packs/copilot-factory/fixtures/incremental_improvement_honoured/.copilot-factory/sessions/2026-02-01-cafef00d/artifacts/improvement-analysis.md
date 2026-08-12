# Improvement analysis (incremental, seed-pack)

The seed orchestrator lacks the required negative-scope section. The change is
additive and does not justify redesigning or rebuilding the pack.

```verdict
schema_version: factory.improvement-analysis/v1
review_type: improvement-analysis
status: BLOCKING
iteration_count: 0
```

```recommendation
strategy: incremental
rationale: One additive section in one existing agent; no structural change.
findings_total: 1
blocking: 1
major: 0
minor: 0
```

```findings-json
[
  {
    "id": "S1",
    "severity": "blocking",
    "category": "negative-scope",
    "file": "agent-packs/seed-pack/.github/agents/seed-orchestrator.agent.md",
    "section": "after File Access Boundaries",
    "action": "add",
    "fix": "Add a Must NOT section forbidding writes outside .seed-stm/ and sub-agent invocation.",
    "validation": "The existing agent is otherwise unchanged and contains both prohibitions under ## Must NOT."
  }
]
```

```improvement-plan
sequence:
  - S1
dependencies: none
preserve_unflagged_content: true
```

```ready-for-orchestrator
true
```
