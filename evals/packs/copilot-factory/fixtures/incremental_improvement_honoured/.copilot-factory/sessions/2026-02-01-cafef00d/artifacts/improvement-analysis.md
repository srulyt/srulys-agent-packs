# Improvement analysis (incremental, seed-pack)

- Session: `2026-02-01-cafef00d`
- Target pack: `agent-packs/seed-pack/`
- Strategy: `incremental`

## Findings

### S1 — Add explicit "Must NOT" section to seed-orchestrator
- **Severity:** blocking
- **File:** `agent-packs/seed-pack/.github/agents/seed-orchestrator.agent.md`
- **Concrete change:** Insert immediately after `## File Access Boundaries`:

```markdown
## Must NOT

- Write outside `.seed-stm/`.
- Invoke any sub-agent (this pack has none).
```

## Strategy recommendation

```recommendation
strategy: incremental
rationale: One additive section; no structural change.
findings_total: 1
blocking: 1
major: 0
minor: 0
```
