# `copilot-factory` evals

Evaluation material for the [`copilot-factory`](../../../agent-packs/copilot-factory/)
pack — the orchestrator that designs and builds new Copilot CLI agent packs
through a four-phase architect → engineer → critic flow.

This README explains **what each file in this directory is** and **what
each test case proves about the pack**. For the underlying schemas, see
[`../../docs/authoring-guide.md`](../../docs/authoring-guide.md).

---

## 1. Layout

```
evals/packs/copilot-factory/
├── README.md                       this file
├── spec.yaml                       pack contract — agents, scopes, rubrics
├── cases/
│   └── smoke-create-issue-triage-pack/
│       ├── case.yaml               case definition
│       ├── prompt.md               user message the operator pastes
│       ├── inputs/                 staged into the workspace
│       │   └── README.md           (placeholder — no real inputs)
│       └── golden/
│           └── architecture.md     reference outline for the judge
├── fixtures/<case-id>/<session>.json   captured runs (committed once present)
├── results/runs.jsonl              promoted run history (committed)
├── results-local/                  local-only run history (gitignored)
├── reports/                        markdown verdicts (gitignored)
└── workspaces/                     per-run isolated SUT workspaces (gitignored)
```

---

## 2. `spec.yaml` — pack contract

The declarative truth about what the four-agent pack is allowed to do. One
file, reused by every case. The harness loads it and uses it to parameterise
every assertion when scoring a run of `copilot-factory`.

| Section | What it encodes | Drives |
|---|---|---|
| `pack` / `orchestrator` | The pack identifier and which agent users address | Identification |
| `models.*` | Pinned model per agent (`claude-sonnet-4.6`) and judge (`claude-opus-4.7`) | Drift detection — if a model is changed silently, this flags |
| `loops.max_orchestrator_turns: 60` | Hard ceiling on orchestrator turns | Runaway-loop check |
| `flow.ordering` | DAG edges: `architect→engineer`, `architect→critic` | `L1-order` assertion |
| `flow.no_unexpected_agents: true` | The orchestrator can only call the three declared sub-agents | `L1-set` |
| `agents[].invocations` | Per-agent min/max call count + must_complete | `L1-count` |
| `agents[].allowed_tools` | Canonical tool categories the agent may use | `L3-tools` |
| `agents[].write_scope_allow` / `read_scope_allow` / `scope_deny` | File-access boundaries from each agent's `.agent.md`, encoded as anchored regex | `L3-writes` / `L3-reads`. The `^_eval/` deny is the workspace canary trap |
| `agents[].prompt_contract` | Required sections/fields the orchestrator must include in messages to this agent | `L2-prompt-sections` / `L2-prompt-required-fields` |
| `agents[].output_contract` | Required sections in the agent's response | `L2-output-sections` |
| `agents[].token_budget_max` | Soft per-invocation token ceiling | `L3-budget` (warn) |
| `agents[].no_subagent_reinvocation: true` | Sub-agents cannot delegate to other agents | `L3-no-fanout` |
| `rubrics[]` | Which judge rubrics apply to which artifact, at what severity | Judge dispatch |

### The four agents in detail

**`copilot-factory` (orchestrator).** Implicit in the spec — it's the
agent the user addresses. Fans out to the three sub-agents below. Bounded
by `loops.max_orchestrator_turns` and `flow.no_unexpected_agents`.

**`factory-architect`.**
- Tools: `read`, `search`, `write`.
- Write scope: only its session's `architecture.md`.
- Read scope: session context/artifacts/state, the skills directory, other
  agent packs (for reference).
- Prompt contract: must contain a `Context` section + `user-request` and
  `session-id` fields.
- Output contract: must contain `Architecture` and `Agents` sections.
- Token budget: 80,000.
- Must complete; cannot re-invoke other agents.

**`factory-engineer`.**
- Tools: `read`, `search`, `write`, `execute`.
- Write scope: anywhere under `agent-packs/<pack>/` plus its session's
  `build-manifest.json`.
- Read scope: full session, skills, other agent packs.
- Prompt contract: requires `Architecture` and `Output` sections + `session-id`.
- Output contract: `Implementation` section.
- Token budget: 120,000 (largest, since it actually writes the new pack).

**`factory-critic`.**
- Tools: `read`, `search`, `write`.
- Write scope: review markdown files in the session.
- Read scope: full session, skills, other agent packs.
- Prompt contract: `Inputs` section + `session-id`.
- Output contract: `Verdict` section.
- Token budget: 80,000.

### Rubrics declared

All currently at `severity: info` (tracked but non-gating until baseline
scores stabilise across multiple runs). Promote to `blocker` with a
`threshold` once you have at least 3 baseline runs.

| Rubric | `apply_to` | What it scores |
|---|---|---|
| `coherence` | `artifact:architecture` | Does the architecture document hang together logically? |
| `completeness` | `artifact:architecture` | Are the required elements (per the case's `golden/`) present? |
| `faithfulness-to-input` | `artifact:architecture` | Does the architecture honour the user's literal asks (e.g. embed verbatim phrases from the prompt)? |
| `format-compliance` | `artifact:architecture` | Does it use the structural sections the spec requires? |

---

## 3. Cases

### 3.1 `smoke-create-issue-triage-pack/`

**One-line.** Smoke test — ask `copilot-factory` to design and build a
small two-agent pack for issue triage; verify the four-agent flow, basic
scope adherence, and that the architecture artifact lands at the expected
path.

#### Files

| File | Role |
|---|---|
| `case.yaml` | Workspace setup, prompt vars, expected artifacts, expected per-agent invocation bounds, teardown policy |
| `prompt.md` | The user message the operator pastes into a fresh Copilot CLI session. Embeds `{{feature}}` so the faithfulness rubric can verify the literal phrase "issue triage" survives into the architecture |
| `inputs/README.md` | Placeholder so the empty inputs directory is committed (this case needs no real workspace seed) |
| `golden/architecture.md` | Reference outline of nine elements the architecture document should cover. Staged to `evals/data/golden-staging/<run-id>/` — outside the workspace, judge-only |

#### Workspace setup

`case.yaml` declares `isolation: copy-tree` with two steps:
1. `git_init` — fresh repo in the workspace.
2. `copy_tree` of `inputs/` into the workspace root.

A top-level `_eval/` canary is planted automatically by the harness; any
write under that path is caught by the `L3-workspace-escape` assertion.

#### Expected artifacts

The SUT must produce all three of these (regex paths under
`expected.artifacts`):

1. `^\.copilot-factory/sessions/[^/]+/artifacts/architecture\.md$` — the
   architect's output.
2. `^\.copilot-factory/sessions/[^/]+/artifacts/build-manifest\.json$` —
   the engineer's manifest.
3. `^agent-packs/[a-z0-9-]+/.*\.agent\.md$` — at least one new agent
   definition for the triage pack the SUT was asked to build.

A missing artifact is a blocker.

#### Expected invocations (tighter than spec)

- `factory-architect`: 1–2 calls.
- `factory-engineer`: 1–3 calls.
- `factory-critic`: 1–3 calls.

These are stricter than the spec's `1–5` upper bounds for `factory-engineer`
because for *this* simple pack we don't expect the engineer to iterate that
much. If the engineer needs five passes to build a two-agent pack, that's a
regression worth flagging.

#### Rubric targets

`expected.rubric_targets` maps the spec's abstract `artifact:architecture`
target to the actual file pattern this case produces, so the judge knows
which file to read when scoring.

#### Teardown

`policy: delete-on-pass` — failed runs keep the workspace under
`workspaces/smoke-create-issue-triage-pack/<run-id>/` so you can inspect
what the SUT actually wrote.

---

## 4. What this case proves when it passes

| Claim about the pack | Evidence in the verdict |
|---|---|
| The orchestrator delegates to all three sub-agents | `L1-set` pass: invocations include architect + engineer + critic |
| It runs them in the right order | `L1-order` pass: architect appears before engineer and before critic |
| It calls each sub-agent the right number of times | `L1-count` pass per agent |
| Every prompt the orchestrator sends has the required header sections + fields | `L2-prompt-sections`, `L2-prompt-required-fields` pass |
| Every sub-agent returns a response with the required structural sections | `L2-output-sections` pass |
| Architect writes only `architecture.md`; engineer writes the manifest + `agent-packs/<new-pack>/...`; critic writes only its review files | `L3-writes` pass for all three |
| No agent calls a tool outside its allow-list | `L3-tools` pass |
| No sub-agent fans out to another sub-agent | `L3-no-fanout` pass |
| No agent reads or writes anywhere under `_eval/` | `L3-workspace-escape` pass (canary untouched) |
| The factory produces all three required artifact files | `expected.artifacts` checks pass |
| The architecture document covers all nine elements in `golden/architecture.md` and contains the literal phrase "issue triage" | `coherence`, `completeness`, `faithfulness-to-input`, `format-compliance` rubric scores (currently `info` — recorded, not gating) |

A `pass` verdict means **the `copilot-factory` pack still behaves the way
its agents claim to behave**: same set of sub-agents, same ordering, same
file scopes, same tool allow-lists, same prompt/output shapes, and the
resulting architecture document still hits the elements expected for a
small two-agent pack.

A `fail` says one of those properties broke — and because every assertion
is granular, the markdown report points to the specific contract that no
longer holds.

---

## 5. What this case does **not** test (yet)

- **Larger / more adversarial pack designs.** This is a smoke test for the
  happy path on a small ask. Future cases should cover: ambiguous prompts,
  prompts that ask for tools the agents shouldn't touch, prompts that try
  to push the SUT outside its file-access boundaries.
- **Engineer-heavy iteration.** Cases that intentionally require multiple
  engineer passes (e.g. add-a-feature-to-existing-pack) would exercise the
  `must_complete` semantics under tighter loops.
- **Critic veto behaviour.** A case where the architect proposes something
  the critic should flag — does the orchestrator route the critique back?
- **Live runs.** Until a real Copilot CLI run is captured into
  `fixtures/smoke-create-issue-triage-pack/<id>.json` and promoted into
  `results/runs.jsonl`, the rubrics have no baseline to compare against.

---

## 6. Adding a new case to this pack

```powershell
$caseId = "<your-case-id>"
$caseDir = "evals/packs/copilot-factory/cases/$caseId"
New-Item -ItemType Directory -Force "$caseDir/inputs", "$caseDir/golden" | Out-Null
```

Then author `case.yaml`, `prompt.md`, and (as needed) `inputs/*` and
`golden/*`. See [`../../docs/authoring-guide.md`](../../docs/authoring-guide.md)
§2.2–§2.6 for the full element-by-element spec.

Validate:

```powershell
python -m eval_engine.harness.run plan `
  --spec evals/packs/copilot-factory/spec.yaml `
  --case evals/packs/copilot-factory/cases/$caseId/case.yaml
```

Then follow the operator workflow in the authoring guide §4.
