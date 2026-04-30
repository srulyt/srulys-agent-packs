# Pack-Spec Schema

> **Read `05-design-revisions-v2.md` first.** That document supersedes specific
> fields here based on a rubber-duck critique. In particular: `prompt_contract`
> replaces `forbidden_in_prompt`; `write_scope_allow` + `read_scope_allow` +
> `scope_deny` replace `file_scope_allow`/`file_scope_deny`; `allowed_tools`
> uses canonical categories from `00-tool-taxonomy.md`; rubric `apply_to`
> values are now `artifact:<id>` or `per_agent:<name>`. Where docs disagree,
> v2 wins.

A **pack spec** is the declarative contract that drives evaluation of a single
agent pack. One YAML file per pack lives at `evals/packs/<pack>/spec.yaml`. The
harness loads it, validates it against the JSON-Schema below, and uses it to
parameterise every assertion.

The spec is the single source of truth for "what is this pack supposed to do
and not do?". Adding a new pack to the eval framework is approximately equal
to writing one of these files plus one or more cases under
`evals/packs/<pack>/cases/<pack>/`.

## File location

`evals/packs/<pack>/spec.yaml` — the `pack` field inside the file MUST equal the
filename stem. The filename stem MUST equal the pack's directory name under
`agent-packs/`.

## Top-level structure

```yaml
schema_version: 1                         # bump only on breaking changes
pack: copilot-factory                     # filename stem; matches agent-packs/<pack>/
description: |
  Multi-agent system for designing and building Copilot CLI agent packs.

orchestrator: copilot-factory             # the agent_type that talks to the user

agents:                                   # one entry per agent (orchestrator + sub-agents)
  - name: copilot-factory
    role: orchestrator
    model: claude-sonnet-4.6              # pinned per §2.5
    allowed_tools: [view, grep, glob, edit, create, task]
    file_scope_allow:
      - "^\\.copilot-factory/.*$"
    file_scope_deny:                      # OPTIONAL; takes precedence over allow
      - "^_eval/.*$"
    forbidden_in_prompt:                  # regex list; matched against EVERY sub-agent prompt this agent emits
      - "(?i)api[_-]?key"
      - "(?i)password"
    expected_invocations: { min: 1, max: 1 }
    token_budget_max: 80000
    may_invoke_subagents: true            # default false; orchestrators set true
    output_must_contain_sections: []      # blocker if non-empty; checked against final assistant message

  - name: factory-architect
    role: worker
    model: claude-sonnet-4.6
    allowed_tools: [view, grep, glob]
    file_scope_allow: []                  # read-only worker; cannot touch files
    forbidden_in_prompt:
      - "(?i)api[_-]?key"
    expected_invocations: { min: 1, max: 3 }
    token_budget_max: 60000
    may_invoke_subagents: false
    output_schema:                        # OPTIONAL JSON-Schema-like sketch
      kind: markdown_sections
      required_sections: ["## Architecture", "## Agents", "## Risks"]

flow_constraints:
  ordering:                               # list of "A must complete before B is launched"
    - { before: factory-architect, after: factory-critic }
    - { before: factory-architect, after: factory-engineer }
  no_unexpected_agents: true              # any agent_type seen in tool_requests not in agents[] -> blocker fail
  no_subagent_reinvocation_unless_permitted: true   # any agent without may_invoke_subagents that calls task -> blocker fail

# Rubrics this pack is graded on. Each entry references a file under eval_engine/rubrics/.
rubrics:
  - id: coherence                         # corresponds to eval_engine/rubrics/coherence.md
    severity: info                        # info | warn | blocker
    threshold: null                       # 0..1; null means "track only, do not gate"
    apply_to: pack_output                 # pack_output | per_agent:<name>

  - id: completeness
    severity: info
    threshold: null
    apply_to: pack_output

  - id: format-compliance
    severity: blocker
    threshold: 0.9                        # case fails if score < 0.9
    apply_to: pack_output
```

## Field reference

### Top-level

| Field | Type | Required | Notes |
|-------|------|----------|-------|
| `schema_version` | int | yes | Currently `1`. Harness rejects unknown versions. |
| `pack` | string | yes | Pack id; matches filename stem and `agent-packs/<pack>/`. |
| `description` | string | yes | Free text shown in reports. |
| `orchestrator` | string | yes | Must match one entry in `agents[].name` whose `role` is `orchestrator`. |
| `agents` | list | yes | One per agent (orchestrator + sub-agents). |
| `flow_constraints` | object | no | Pack-level invocation/ordering rules. |
| `rubrics` | list | no | Judge rubrics applied to this pack. |

### `agents[]`

| Field | Type | Required | Notes |
|-------|------|----------|-------|
| `name` | string | yes | The `agent_type` value the orchestrator passes to `task`. |
| `role` | enum | yes | `orchestrator` \| `worker` \| `critic`. Exactly one orchestrator. |
| `model` | string | yes | Pinned per §2.5. Used to slice trend reports. |
| `allowed_tools` | list[string] | yes | Tool allow-list. Used by L3-tools assertion. Empty list means "no tools at all". |
| `file_scope_allow` | list[regex] | yes | Paths the agent may read/write **inside the workspace**. Used by L3-files. Empty = read-only via tools that don't touch FS. |
| `file_scope_deny` | list[regex] | no | Takes precedence over `_allow`. The harness automatically prepends `^_eval/.*$` to every agent's deny list (golden-ref protection). |
| `forbidden_in_prompt` | list[regex] | no | Strings that must NOT appear in any prompt this agent constructs for downstream sub-agents. Used by L2-prompt-forbidden. |
| `expected_invocations` | `{min, max}` | yes | Used by L1-count. Use `{min:1,max:1}` for the orchestrator. |
| `token_budget_max` | int | yes | Used by L3-budget (warn). |
| `may_invoke_subagents` | bool | no | Default `false`. If `false` and the agent calls `task`, L3-no-fanout fires (blocker). |
| `output_must_contain_sections` | list[string] | no | Markdown headings required in the agent's final response. Used by L2-prompt-sections (despite the name, it can also be applied to outputs). |
| `output_schema` | object | no | Sketch of the expected output. Currently supports `{ kind: markdown_sections, required_sections: [...] }`; future kinds can be added. Used by L2-output-schema. |

### `flow_constraints`

| Field | Type | Notes |
|-------|------|-------|
| `ordering` | list of `{before, after}` | Each rule asserts `before` completes before `after` is launched (timestamp-based). Used by L1-order. |
| `no_unexpected_agents` | bool | Default `true`. Any `agent_type` in `tool_requests` not in `agents[]` is a blocker fail. Used by L1-set. |
| `no_subagent_reinvocation_unless_permitted` | bool | Default `true`. Cross-checked against each agent's `may_invoke_subagents`. Used by L3-no-fanout. |

### `rubrics[]`

| Field | Type | Required | Notes |
|-------|------|----------|-------|
| `id` | string | yes | Filename stem under `eval_engine/rubrics/`. |
| `severity` | enum | yes | `info` (track only) \| `warn` (report but don't gate) \| `blocker` (gate the case). |
| `threshold` | float \| null | conditional | Required when `severity` is `warn` or `blocker`. Score < threshold = fail at that severity. |
| `apply_to` | string | yes | `pack_output` (judge sees the pack's final artifacts) \| `per_agent:<name>` (judge sees a specific sub-agent's final response). |

## Validation rules (enforced at load time)

1. `pack` matches filename stem.
2. Exactly one `agents[]` entry has `role: orchestrator`.
3. `orchestrator` field equals that agent's `name`.
4. All `name`s are unique within `agents[]`.
5. All regexes compile.
6. Every `flow_constraints.ordering[].before/.after` is a known agent name.
7. Every rubric `id` resolves to a file at `eval_engine/rubrics/<id>.md`.
8. When `severity` ∈ {`warn`, `blocker`}, `threshold` is set.
9. Each rubric's `apply_to` resolves: `pack_output` always valid;
   `per_agent:<name>` requires `<name>` in `agents[]`.
10. `_eval/` is automatically denied for every agent (the harness prepends
    `^_eval/.*$` to each agent's `file_scope_deny`); operators MUST NOT add it
    to `file_scope_allow`. The validator rejects any spec that does.

## Defaults applied by the loader

- `flow_constraints.no_unexpected_agents` defaults to `true`.
- `flow_constraints.no_subagent_reinvocation_unless_permitted` defaults to `true`.
- Every agent's `file_scope_deny` gets `^_eval/.*$` prepended automatically.
- An agent missing `may_invoke_subagents` is treated as `false`.

## Why this shape

- **Single source of truth**: every assertion in the L1/L2/L3 catalogue is
  parameterised from one of these fields. No assertion has hidden constants.
- **Allow + deny lists**: most packs only need `allow`; `deny` is the escape
  hatch for "everything matching X except subdir Y". The reserved `_eval/`
  deny is enforced by the framework, not by hand-rolling.
- **Negative scope is declarative**: `may_invoke_subagents`, `forbidden_in_prompt`,
  `file_scope_deny` make negative-scope checks data-driven instead of code.
- **Rubric severity decoupled from assertion severity**: rubric severity is
  per-pack and tunable as the rubric matures; assertion severity is a global
  property of the assertion logic.
