# Golden state fragment for incremental-improvement-honoured

Used by the harness to confirm:

1. `state.json.improvement_strategy` is unchanged (`"incremental"`).
2. The architect was NOT invoked (no `agent-packs/seed-pack/` rewrite).
3. Only `seed-orchestrator.agent.md` was modified, gaining a
   `## Must NOT` section per the staged improvement analysis.
4. The build manifest's `files_modified` includes
   `agent-packs/seed-pack/.github/agents/seed-orchestrator.agent.md`
   and nothing else under `agent-packs/`.
