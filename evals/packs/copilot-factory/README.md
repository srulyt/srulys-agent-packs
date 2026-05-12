# `copilot-factory` evals

Pytest tests covering the `copilot-factory` agent pack — the
orchestrator + sub-agents that design, build, review, and improve other
Copilot CLI agent packs.

| Test | Scenario |
|------|----------|
| `test_smoke_issue_triage.py` | Happy path: factory designs and builds a 2-agent issue-triage pack from a one-line user request. |
| `test_critic_veto_weak_architecture.py` | Critic must veto an architecture that omits required risks/decisions and route back to the architect. |
| `test_incremental_improvement_honoured.py` | Improvement loop honours an explicit "do not rewrite from scratch" instruction. |
| `test_negative_scope_architect_no_pack_writes.py` | Architect must not write to `agent-packs/`; only architecture artefacts under the session STM are allowed. |
| `test_smoke_orchestrator_no_self_redirect.py` | Orchestrator must dispatch via `task(...)`; it must not impersonate sub-agents in its own response. |

Run from the repo root:

```powershell
pytest evals/packs/copilot-factory/ -v
pytest evals/packs/copilot-factory/test_smoke_issue_triage.py -v
```

See [`evals/README.md`](../../README.md) for framework-wide conventions
and [`evals/MIGRATION_NOTES.md`](../../MIGRATION_NOTES.md) for what
changed when the YAML harness was retired.
