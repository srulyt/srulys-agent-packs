# Copilot Factory

Create multi-agent systems for GitHub Copilot CLI.

## Quick Start

### Using with GitHub Copilot CLI

```bash
# Copy the .github folder to your project
cp -r .github /path/to/your/project/

# Start Copilot CLI (after installing/authenticating it)
copilot

# Invoke the factory
@copilot-factory Create an agent pack for [describe your use case]
```

## What It Does

The Copilot Factory guides you through creating complete agent packs:

1. **Intake**: Captures your requirements
2. **Improve-Analysis** (improvement mode): Delegates existing-pack analysis to `@factory-critic`, offers incremental or rebuild path
3. **Design**: Delegates architecture creation to `@factory-architect`
4. **Review-Arch**: Delegates architecture validation to `@factory-critic`
5. **Approval**: Presents the architecture for your approval
6. **Build**: Delegates artifact generation to `@factory-engineer` (full build or incremental edits)
7. **Review-Prompts**: Delegates implementation validation to `@factory-critic`
8. **Eval-Execute**: Runs changed/full-build evals through `@factory-eval-runner`
9. **Eval-Fix-Loop** (failure + separate user approval): applies allowlisted fixes and reruns, cap 3
10. **Complete**: Reports review, validation, and eval status

## Agents

- `@copilot-factory`: Main orchestrator - manages phases, state, approvals, and delegation
- `@factory-architect`: Design specialist - creates architecture artifacts
- `@factory-engineer`: Implementation specialist - creates files from approved architecture
- `@factory-critic`: Quality gate - reviews architecture and implementation with PASS/BLOCKING verdicts
- `@factory-eval-runner`: Eval-execution specialist - runs the generated pack's evals via the Eval Pilot plugin and returns a pass/fail verdict

## Evals (Eval Pilot dependency)

The Factory does **not** ship its own eval framework. Eval creation,
execution, and metrics are delegated to the separate **Eval Pilot** plugin
(`agent-packs/eval-pilot/`) and its `evalpilot` engine. Generated packs get
an `evals/packs/<pack>/` suite authored via Eval Pilot's `eval-author` skill
and executed by `@factory-eval-runner` via Eval Pilot's `eval-runner` skill.

Install Eval Pilot and its engine as Factory dependencies:

```bash
copilot plugin install eval-pilot@srulys-agent-packs
npm install --save-dev evalpilot
```

For the **Factory production flow**, invoke `@copilot-factory`; do not run
`evalpilot`, `npx evalpilot`, or an `.mjs` file directly. The Factory delegates
execution to `@factory-eval-runner`, which must follow the canonical
guarded-wrapper instructions in
`.github/skills/agent-builder/references/workflow-contracts.md` (installed
pack) or
`agent-packs/copilot-factory/.github/skills/agent-builder/references/workflow-contracts.md`
(source checkout). That flow resolves the repository root, Node executable,
validator, and wrapper to absolute paths, then hosts the wrapper through the
resolved Node executable.

> **Unresolved write-confinement warning:** the guarded wrapper detects
> repository mutations but does not restore them. The canonical command flow
> does not fix or waive this blocker and must not be described as fully
> confining writes.

## Orchestration Pattern

```text
User Request
    ↓
@copilot-factory
    ├── → @factory-critic (improvement analysis, improvement mode)
    ├── → @factory-architect (design)
    ├── → @factory-critic (review architecture)
    ├── → User approval gate (required)
    ├── → @factory-engineer (build)
    ├── → @factory-critic (review implementation)
    ├── → @factory-eval-runner (versioned eval result)
    └── → approval-gated @factory-engineer fix ↔ eval rerun
         ↓
    Delivery to User
```

The orchestrator does not bypass these delegation steps.

The orchestrator never investigates target packs directly. Requests
like "summarise this pack" or "review this agent file" are routed to
`@factory-critic` (improvement-analysis or implementation review). If
the orchestrator appears to be reading agent files itself, that is a
bug — file an issue.

## Skills

- `system-design`: Multi-agent architecture patterns
- `agent-builder`: Templates for Copilot CLI artifacts

## Prompts

- `create-pack`: Guided new pack creation workflow
- `analyze-and-improve`: Analyze and improve an existing pack
- `resume-session`: Resume an interrupted factory session
- `improve-factory`: Run a self-improvement cycle on the Copilot Factory's own prompts

## State Management

Session state is stored in `.copilot-factory/sessions/{session-id}/`:

```text
sessions/{session-id}/
├── state.json          # Workflow state
├── context/
│   └── user-request.md # Your requirements
└── artifacts/
    ├── architecture.md               # Creation/rebuild design
    ├── improvement-analysis.md       # Incremental/rebuild recommendation
    ├── architecture-review.md        # Critic gate, when persisted
    ├── implementation-review.md      # Critic gate, when persisted
    ├── build-manifest.json
    └── eval-run-{n}.json             # factory.eval-result/v1
```

### Cross-Session Learning

Factory workflow decisions are deterministic files under the active session
and are explicitly read during recovery. A local `.github/memory/*.md` folder
is not automatically loaded by documented custom-instruction behavior; use it
only as a convention when an authorized agent explicitly reads it. Prefer
supported repository/path custom instructions for deterministic context.
GitHub Copilot Memory is a separate, availability-dependent product feature.

## Example Usage

```text
@copilot-factory Create an agent pack for code review automation.
The system should have a coordinator that assigns reviews to specialists
for different areas: security, performance, and style.
```

## Generated Pack Location

All generated packs are created in:

```text
agent-packs/{pack-name}/
```

## Troubleshooting

**Agent not found**: Ensure `.github/agents/` is in your project root.

**Skill not loading**: Check that `.github/skills/` exists and contains valid `SKILL.md` files.

**Compatibility**: The Factory baseline is `factory-cli-2026-08-12`; see
`agent-builder/references/copilot-artifacts.md`. Copilot CLI runtime validation
is **unverified** because no executable or run evidence was available. Targeted
static checks and Eval Pilot structural checks do not imply smoke-load success.

**Session issues**: Delete `.copilot-factory/` to start fresh.

**Git noise**: Add `.copilot-factory/` to your project's `.gitignore` to avoid committing session state.

## License

MIT
