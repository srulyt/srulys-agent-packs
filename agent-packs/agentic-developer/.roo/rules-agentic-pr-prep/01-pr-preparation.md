# PR Prep Mode: PR Preparation Protocol

## Purpose

The PR Prep agent prepares the implementation for pull request submission: organizing commits, writing PR description, and creating review guidance.

## Input

- All run artifacts from `.agent-memory/runs/<run-id>/`
- Change manifest, cleanup report, verification reports
- Tech debt discovered during run

## Output

- PR description at `.agent-memory/runs/<run-id>/pr-description.md`
- Review checklist at `.agent-memory/runs/<run-id>/pr-checklist.md`
- Completion event in `.agent-memory/runs/<run-id>/events/pr-prep/`

## When to Run

After cleanup completes successfully.

## Process

### 1. Pre-PR Verification

Confirm:

- All tasks verified
- Cleanup complete
- Build and tests passing
- No uncommitted changes

### 2. Generate PR Description

Write a clear PR description with these sections:

```markdown
## Summary

[One paragraph: what this PR does]

## Motivation

[Why this change is needed - from PRD]

## Changes

| File | Change Type | Description |
| ---- | ----------- | ----------- |
| ...  | ...         | ...         |

## Testing

- Tests added: X
- Tests passing: Y/Y
- Coverage delta: +Z%

## Rollback Plan

[How to revert if issues found]

## Checklist

- [ ] Code follows project style
- [ ] Tests added for new functionality
- [ ] No breaking changes
```

### 3. Create Review Checklist

Identify focus areas for reviewers:

- Critical changes (core logic)
- Risk areas (refactored code)
- Architecture decisions

### 4. Document Follow-ups

- Tech debt items to create as tickets
- Future improvements noted during implementation
- Known limitations

## Key Constraints

- **Accurate summary**: PR description must match actual changes
- **Reviewer-focused**: Highlight what reviewers should focus on
- **Complete**: Include all necessary context for review
- **Concise**: Don't overwhelm with unnecessary detail

## PR Title Format

Use a conventional commit-style title:

```
<type>(<scope>): <short description>
```

**Types**: `feat`, `fix`, `refactor`, `docs`, `test`, `chore`, `perf`

**Examples**:

- `feat(auth): add SSO login support`
- `fix(api): handle null response in user endpoint`
- `refactor(core): extract validation logic to shared module`

**Rules**:

- Keep under 72 characters
- Use imperative mood ("add" not "added")
- Scope should match affected area/module
- No period at end

## PR Description Guidelines

1. **Executive summary first** - What and why in 2-3 sentences
2. **File-by-file breakdown** - What changed in each file
3. **Testing evidence** - Proof that changes work
4. **Review guidance** - Where to focus attention

## Exit Criteria

- [ ] PR description complete
- [ ] Review checklist created
- [ ] Follow-up items documented
- [ ] Event emitted
- [ ] Ready for human review

## Templates

- Artifact metadata: `.roo/templates/artifact-metadata.md`
- Event format: `.roo/templates/event-format.md`
