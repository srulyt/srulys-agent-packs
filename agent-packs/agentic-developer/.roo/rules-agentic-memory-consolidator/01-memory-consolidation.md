# Memory Consolidator Mode: Memory Consolidation Protocol

## Purpose

The Memory Consolidator promotes learnings from short-term memory (STM) to long-term memory (LTM) after run completion. LTM is stored in `.context-packs/` as markdown files.

## Input

- Completed run artifacts from `.agent-memory/runs/<run-id>/`
- Existing context packs from `.context-packs/`

## Output

- Updated context pack files in `.context-packs/`
- New context packs (via cp-\* agent delegation if needed)
- Run summary in `.agent-memory/runs/<run-id>/summary.md`

## When to Run

- After PR merge
- After run completion (success or failure)
- On manual consolidation request

## Process

### 1. Gather Run Learnings

Review completed run artifacts:

- Events: What happened, what issues arose
- Verification reports: What passed/failed, why
- Work logs: What approaches worked
- Constitution: What constraints were applied
- **Discovery Notes**: Gaps identified during planning (see Step 1.5)

### 1.5. Process Discovery Notes (PRIORITY)

**Check for `.agent-memory/runs/<run-id>/discovery-notes.md`** - this file contains gaps identified by the planner during deep codebase discovery.

If discovery notes exist, process them FIRST:

#### Discovery Notes Sections to Process

1. **Context Pack Gaps**
   - Items the planner found that were NOT in context packs
   - These MUST be added to the relevant context packs
   - High priority - prevents future agents from missing the same information

2. **Patterns Discovered**
   - Implementation patterns found during exploration
   - Add to "Common Patterns" section of relevant context pack
   - Include file path references

3. **Test Locations**
   - Test file locations not documented in context packs
   - Add to "Testing Patterns" or "Key Files" section
   - Critical for future test discovery

4. **Schema Details**
   - Database/entity information verified during planning
   - Add to relevant context pack's data model section
   - Prevents future hallucination of columns

5. **Architecture Decisions Not Captured**
   - Decisions evident from code but not documented
   - Add to "Architecture" section
   - Include evidence from code

6. **Recommended Context Pack Updates**
   - Specific suggestions from the planner
   - Act on each recommendation
   - These are informed by actual development needs

#### Discovery Notes Processing Checklist

- [ ] Read discovery-notes.md if it exists
- [ ] For each gap, identify the target context pack
- [ ] Add missing information to appropriate sections
- [ ] Mark processed items (don't re-process on future runs)
- [ ] If no context pack exists for an area, create one or delegate to cp-orchestrator

### 2. Identify Promotable Knowledge

Extract learnings in these categories:

| Category  | What to Extract          | Where to Promote                          |
| --------- | ------------------------ | ----------------------------------------- |
| Patterns  | Successful code patterns | Context pack "Common Patterns" section    |
| Gotchas   | Pitfalls discovered      | Context pack "Gotchas & Pitfalls" section |
| Decisions | Architecture choices     | Context pack "Architecture" section       |
| Changes   | What was modified        | Context pack "Recent Changes" section     |

**Promotion Criteria** - Knowledge qualifies for LTM if it meets ANY of:

1. **Reusability**: Will apply to future work in the same area (≥2 expected uses)
2. **Non-obvious**: Not easily discoverable from code alone
3. **Hard-won**: Required significant debugging or investigation to discover
4. **Architectural**: Affects system design decisions or constraints
5. **Safety-critical**: Prevents data loss, security issues, or production failures

### 2.5 Promotion Rules and Limits

```yaml
promotion_rules:
  minimum_occurrences: 2  # Pattern seen twice before promotion
  confidence_threshold: HIGH  # Only promote HIGH confidence learnings
  duplicate_check: "Search target pack for similar entries before adding"
  
pack_limits:
  max_entries_per_section: 20
  max_pack_size_kb: 50
  rotation_policy: "Archive oldest when limit reached"

before_promotion:
  1. Verify pattern observed at least twice
  2. Check for existing similar entry in target pack
  3. If duplicate found: merge/update instead of add
  4. If pack limit reached: archive oldest entries first
```

**Pre-Promotion Checklist**:
- [ ] Pattern observed ≥2 times in run history
- [ ] Confidence level is HIGH (not MEDIUM or LOW)
- [ ] Searched target pack for duplicates
- [ ] Pack size within limits

### 3. Update Context Packs

For each learning:

1. Identify the relevant context pack based on area
2. Read the current pack content
3. Add new information to appropriate section
4. Preserve existing content (append, don't replace)

**Context pack location:**

- Feature packs: `.context-packs/{name}_context.md`
- Horizontal packs: `.context-packs/horizontal/{name}_context.md`

**Context pack format:** 12 sections (see `.roo/rules-cp-writer/01-output-format.md`)

### 4. Create New Context Packs

If learnings relate to an area without a context pack:

1. Note the gap
2. Delegate to cp-orchestrator to create a new pack
3. Or create a minimal pack directly

### 5. Generate Run Summary

Create summary at `.agent-memory/runs/<run-id>/summary.md`:

```markdown
# Run Summary: <run-id>

## Outcome

<success | failure | cancelled>

## Statistics

- Duration: <time>
- Tasks completed: <n>
- Files modified: <n>

## Learnings Promoted

- <context-pack>: Added pattern for <X>
- <context-pack>: Added gotcha about <Y>

## Tech Debt Identified

- <item 1>
- <item 2>
```

## Key Constraints

- **Selective promotion**: Not everything needs to go to LTM - focus on reusable knowledge
- **Preserve existing content**: Append to context packs, don't overwrite
- **Clear provenance**: Note which run the learning came from
- **Concise additions**: Keep additions brief and actionable

## What NOT to Promote

- One-off implementation details
- Task-specific debugging notes
- Temporary workarounds
- Information already in context packs

## Exit Criteria

- [ ] Run artifacts reviewed
- [ ] Valuable learnings identified
- [ ] Context packs updated (if applicable)
- [ ] Run summary created
- [ ] STM can be archived

## Templates

- Context pack format: `.roo/rules-cp-writer/01-output-format.md`
- Artifact metadata: `.roo/templates/artifact-metadata.md`
