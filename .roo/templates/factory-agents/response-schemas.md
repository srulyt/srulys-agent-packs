# Agent Response Schemas

Standard response formats for Factory agents to enable programmatic verification.

## Response Structure

All agent responses via `attempt_completion` SHOULD follow these JSON-compatible structures.

### Success Response

```json
{
  "status": "success",
  "confidence": "high|medium|low",
  "confidence_notes": "Optional explanation if not high",
  "deliverables": [
    {
      "path": ".factory/runs/{session-id}/artifacts/system_architecture.md",
      "type": "architecture|rules|config|skill",
      "description": "System architecture document"
    }
  ],
  "summary": "Brief description of completed work",
  "metrics": {
    "files_created": 1,
    "files_modified": 0,
    "lines_written": 250
  },
  "next_action": "ready_for_review"
}
```

### Questions Response

```json
{
  "status": "questions",
  "questions": [
    {
      "id": "q1",
      "question": "Should the system support multiple concurrent sessions?",
      "context": "Affects STM design significantly",
      "default": "single-session",
      "options": ["single-session", "multi-session"]
    }
  ],
  "partial_work": {
    "completed": ["agent topology", "communication patterns"],
    "blocked_on": ["STM schema"]
  },
  "recommendation": "Suggest single-session for simplicity"
}
```

### Failure Response

```json
{
  "status": "failure",
  "error": {
    "type": "missing_input|invalid_config|ambiguous_requirements|technical_error",
    "message": "Cannot find user-request.md in .factory/context/",
    "recoverable": true
  },
  "attempted": "Tried to read context files",
  "recommendation": "Ensure .factory/context/user-request.md exists"
}
```

## Validation Rules

### For Orchestrator

When receiving agent responses, verify:

1. **Status field exists** and is one of: `success`, `questions`, `failure`
2. **Success responses** have at least one deliverable with valid path
3. **Questions responses** have at least one question with id
4. **Failure responses** have error type and message

### For Sub-Agents

Before returning via `attempt_completion`:

1. Ensure all deliverable paths are absolute (from workspace root)
2. Verify files exist before claiming them as deliverables
3. Include meaningful summary (not just "Done")
4. Set appropriate next_action hint

## Response Examples by Agent

### Architect Success

```json
{
  "status": "success",
  "confidence": "high",
  "deliverables": [
    {
      "path": ".factory/runs/{session-id}/artifacts/system_architecture.md",
      "type": "architecture",
      "description": "Complete system architecture with 4 agents"
    }
  ],
  "summary": "Designed data-pipeline system with Orchestrator, Ingest, Transform, and Output agents",
  "metrics": {
    "agents_defined": 4,
    "skills_required": 1,
    "estimated_files": 6
  },
  "next_action": "ready_for_review"
}
```

### Engineer Success

```json
{
  "status": "success",
  "confidence": "high",
  "deliverables": [
    {"path": ".roomodes", "type": "config", "description": "Mode definitions"},
    {"path": ".roo/rules-pipeline-orchestrator/rules.md", "type": "rules", "description": "Orchestrator rules"},
    {"path": ".roo/rules-pipeline-ingest/rules.md", "type": "rules", "description": "Ingest agent rules"},
    {"path": ".roo/rules-pipeline-transform/rules.md", "type": "rules", "description": "Transform agent rules"},
    {"path": ".roo/rules-pipeline-output/rules.md", "type": "rules", "description": "Output agent rules"}
  ],
  "summary": "Built complete pipeline system with 4 agents and STM structure",
  "metrics": {
    "files_created": 5,
    "total_lines": 1200,
    "modes_created": 4
  },
  "next_action": "ready_for_review"
}
```

### Critic PASS

```json
{
  "status": "success",
  "summary": "Architecture review PASSED - all requirements verified",
  "verdict": "PASS",
  "requirements_checked": 9,
  "concerns": ["Minor: Consider adding LTM for long-running workflows"],
  "next_action": "proceed_to_build"
}
```

### Critic BLOCKING

```json
{
  "status": "success",
  "summary": "Architecture review found 2 BLOCKING issues",
  "verdict": "BLOCKING",
  "requirements_checked": 7,
  "blocking_issues": [
    {
      "id": "B1",
      "category": "stm_mechanism",
      "title": "No STM defined",
      "description": "Architecture lacks state.json schema",
      "resolution": "Add STM section with directory structure and schema"
    },
    {
      "id": "B2",
      "category": "consistent_paths",
      "title": "Path inconsistency",
      "description": "STM referenced as both .stm/ and .pipeline-stm/",
      "resolution": "Standardize to .pipeline-stm/ throughout"
    }
  ],
  "next_action": "return_to_architect"
}
```

## Implementation Notes

Agents MAY return plain markdown that follows the spirit of these schemas. The structured format is RECOMMENDED but not strictly required for backward compatibility.

When parsing responses, orchestrator should:
1. First try to extract JSON if present
2. Fall back to markdown parsing
3. Always verify file existence for claimed deliverables

## Confidence Signaling

Agents MAY include confidence indicators:

```json
{
  "status": "success",
  "confidence": "high",
  "confidence_notes": null,
  ...
}
```

| Level | Meaning |
|-------|---------|
| `high` | Standard case, no concerns |
| `medium` | Some ambiguity in requirements or approach |
| `low` | Significant uncertainty, recommend human review |

Orchestrator uses confidence to decide if additional review is needed.
