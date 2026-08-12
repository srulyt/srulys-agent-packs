# `copilot-factory` evals

Eval Pilot behavioral and structural specs covering the `copilot-factory` pack —
including versioned handoff contracts, invocation/write safety, capability
compatibility, documentation consistency, and end-to-end workflows. The
behavioral suite covers the
orchestrator + sub-agents that design, build, review, and improve other
Copilot CLI agent packs.

| Test | Scenario |
|------|----------|
| `test_smoke_issue_triage.eval.md` | `smoke`: approval-gated happy path designs, reviews, builds, reviews, and evals a 2-agent issue-triage pack. |
| `test_critic_veto_weak_architecture.eval.md` | Regression (not smoke): critic vetoes a weak architecture and persists `architecture-review.md`. |
| `test_incremental_improvement_honoured.eval.md` | Regression (not smoke): complete improvement-v1 fixture drives a surgical incremental edit. |
| `negative_scope_architect_no_pack_writes.eval.ts` | Architect must not write to `agent-packs/`; only architecture artefacts under the session STM are allowed. |
| `test_smoke_orchestrator_no_self_redirect.eval.md` | `smoke`: orchestrator accepts intake without redirecting itself. |
| `test_workflow_contracts.eval.ts` | Eval and improvement contracts are versioned and wired across producer/orchestrator/consumer/template surfaces. |
| `test_runner_guard_and_write_scope.eval.ts` | Runner has `edit`, exact single-artifact write scope, and a two-sided guard. |
| `test_capability_and_docs_consistency.eval.ts` | Surface baseline, memory caveats, MCP/model guidance, and workflow docs remain consistent. |
| `run-evals-guarded.test.mjs` | Node unit tests prove repository-write detection and target-pack `.github` fix-path validation. |

Run from the repo root:

```powershell
evalpilot run evals/packs/copilot-factory/
evalpilot run evals/packs/copilot-factory/test_smoke_issue_triage.eval.md
node scripts/run-evals.mjs copilot-factory
```

See [`evals/README.md`](../../README.md) for framework-wide conventions
and [`evals/MIGRATION_NOTES.md`](../../MIGRATION_NOTES.md) for what
changed when the YAML harness was retired.

Behavioral specs whose filename starts `test_smoke_` carry the `smoke` tag.
Targeted regressions retain `pack` plus `slow`/`judge` where applicable and
are intentionally not mislabeled as smoke.

Copilot CLI runtime validation is **unverified** for this build: no executable
or run evidence was available, so no agent smoke-load is claimed. Targeted
validation uses Eval Pilot 0.2.0 structural specs, Node's built-in test runner,
and `scripts/lint-pack.mjs`, scoped to this pack and its evals.
