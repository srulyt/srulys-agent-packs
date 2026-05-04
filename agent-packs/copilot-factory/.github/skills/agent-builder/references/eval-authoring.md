# Eval Authoring (cross-cutting reference)

This file documents the eval authoring rules every generated pack
must satisfy. When the pack is deployed standalone, this reference
is authoritative. When this pack ships inside the
`srulyt/srulys-agent-packs` monorepo, the in-repo
`evals/docs/authoring-guide.md` provides additional examples but does
not override anything stated here.

## Required directory shape per generated pack

```
evals/packs/<pack>/
├── spec.yaml
└── cases/
    └── smoke-<happy-path>/
        ├── case.yaml
        ├── prompt.md
        ├── inputs/
        │   └── README.md
        └── golden/
            └── README.md
```

Every directory must be tracked by git — keep a `README.md` placeholder
in `inputs/` and `golden/` even when empty.

## `spec.yaml` skeleton

```yaml
schema_version: 1
pack: <pack-name>             # MUST equal directory name
orchestrator: <orchestrator>  # usually same as pack name

models:
  <pack-name>: claude-sonnet-4.6
  <sub-agent-1>: claude-sonnet-4.6
  judge: claude-opus-4.7      # judge >= strongest SUT agent

loops:
  max_orchestrator_turns: 60

flow:
  ordering:
    - [<sub-agent-1>, <sub-agent-2>]
  no_unexpected_agents: true

agents:
  - name: <sub-agent-1>
    invocations: { min: 1, max: 3, must_complete: true }
    allowed_tools: [read, search, write]   # canonical names only
    write_scope_allow:
      - "^path/regex/.*"
    read_scope_allow:
      - "^path/regex/.*"
    scope_deny:
      - "^_eval/"
      - "^\\.git/"
    prompt_contract:
      required_sections: ["Context"]
      required_fields: ["session-id"]
    output_contract:
      must_contain_sections: ["<fence-label-1>", "<fence-label-2>"]
    token_budget_max: 80000
    no_subagent_reinvocation: true

rubrics:
  - id: coherence
    apply_to: artifact:<artifact-id>
    severity: info              # always start at info
```

Source: see authoring-guide §2.1.

### Translating an `.agent.md` into the spec

1. `tools:` front-matter → `allowed_tools`. The eval spec uses
   internal canonical names (`read`, `search`, `write`, `execute`,
   `agent`, `mcp`, `mcp:<server>`); map agent-profile aliases via
   this table:

   | `.agent.md` `tools:` (Copilot CLI alias) | `spec.yaml` `allowed_tools` (eval canonical) |
   |---|---|
   | `read` | `read` |
   | `edit` (covers `Write`, `Edit`, `MultiEdit`, `NotebookEdit`) | `write` |
   | `search` | `search` |
   | `execute` (covers `shell`, `Bash`, `powershell`) | `execute` |
   | `agent` (covers `Task`, `custom-agent`) | `agent` |
   | `web` | `web` |
   | `vision` | `vision` |
   | `<server>/<tool>` (MCP) | `mcp:<server>` |

   Source: [Copilot docs — Custom agents configuration: Tool aliases](https://docs.github.com/en/copilot/reference/custom-agents-configuration#tool-aliases).
2. `## File Access Boundaries` table → `write_scope_allow` and
   `read_scope_allow` as anchored regexes (start with `^`,
   double-escape backslashes).
3. Always include `scope_deny: ["^_eval/", "^\\.git/"]` — the
   `^_eval/` deny stops the workspace canary trap; without it the
   harness cannot detect scope escapes.
4. Each agent's `## Output Contract` fenced block labels go into
   `output_contract.must_contain_sections`.

## `case.yaml` skeleton

```yaml
id: <case-id>                 # MUST equal directory name; kebab-case
pack: <pack-name>
description: |
  One paragraph: what the case asks the pack to do, and what it
  proves if it passes.

prompt_file: prompt.md

prompt_template_vars:
  feature: "<value>"

workspace:
  isolation: copy-tree
  inputs_dir: inputs/
  golden_dir: golden/
  steps:
    - kind: git_init
    - kind: copy_tree
      src: inputs/
      dest: .
    # Stage the SUT's own agents/skills so Copilot CLI discovers them:
    - kind: copy_tree
      src: ../../../../../agent-packs/<pack>/.github/agents
      dest: .github/agents
    - kind: copy_tree
      src: ../../../../../.github/skills
      dest: .github/skills
    # Stage the @eval-judge agent so the harness's run-judge
    # subcommand can subprocess-invoke it. Without this step the
    # judge agent is absent from the case workspace and judge calls
    # fail with "Unknown agent_type: eval-judge". This is required
    # for ALL packs, not just copilot-factory.
    - kind: copy_tree
      src: ../../../../../agent-packs/copilot-factory/.github/agents/eval-judge.agent.md
      dest: .github/agents/eval-judge.agent.md

teardown:
  policy: delete-on-pass

expected:
  artifacts:
    - id: <artifact-id>
      path_pattern: "^path/regex/.*\\.md$"
      required: true
  invocations:
    <agent-name>: { min: 1, max: 2 }
  rubric_targets:
    "artifact:<artifact-id>": "^path/regex/.*\\.md$"
```

Source: see authoring-guide §2.2.

## Hard rules (do not violate)

- `id` MUST equal the case directory name; `pack` MUST equal the
  parent pack directory name.
- All scope regexes are **anchored** with `^`. Un-anchored regexes
  silently let the SUT write outside its sandbox.
- All YAML `description` values are **double-quoted**. Bare strings
  containing `:` cause "Nested mappings are not allowed" parse errors.
- Every rubric starts at `severity: info`. Promote to `warn` or
  `blocker` (with `threshold: 0..1`) only after ≥3 baseline runs.
- Never put golden material under `inputs/` — that leaks the answer
  to the SUT.
- Always include `^_eval/` and `^\\.git/` in `scope_deny`.

## Quick checklist for the engineer

- [ ] `evals/packs/<pack>/spec.yaml` created with all sub-agents
      listed under `agents:`
- [ ] `pack:` equals the directory name
- [ ] Models pinned for orchestrator + every sub-agent + `judge`
- [ ] At least one `cases/smoke-<happy-path>/` directory with
      `case.yaml`, `prompt.md`, `inputs/README.md`, `golden/README.md`
- [ ] All scope regexes anchored
- [ ] All rubrics at `severity: info`
- [ ] All YAML `description` values quoted
- [ ] Eval files appear under `files_created` and `evals_created` in
      the build manifest
- [ ] **`@eval-judge` is staged into the case workspace** via a
      `copy_tree` step that brings in
      `agent-packs/copilot-factory/.github/agents/eval-judge.agent.md`.
      The harness's `run-judge` subcommand subprocess-invokes this
      agent non-interactively; if it is not in the case workspace,
      every judge call fails with `Unknown agent_type`. This is
      required for ALL packs, not just `copilot-factory`.

## Source of truth

When run inside the `srulys-agent-packs` monorepo, the in-repo
`evals/docs/authoring-guide.md` is the harness's authoritative spec
and supersedes this reference. When this pack is deployed standalone,
this reference is authoritative.
