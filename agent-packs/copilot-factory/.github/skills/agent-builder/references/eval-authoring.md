# Eval Integration (delegate to the Eval Pilot plugin)

The Copilot Factory does **not** own an eval framework. Eval creation,
execution, and metrics are owned by the **Eval Pilot** plugin
(`agent-packs/eval-pilot/`) and its TypeScript `evalpilot` engine. This
reference is a thin *integration contract*: it says what the Factory
produces, where it lives, and which Eval Pilot skill to invoke. It does
**not** re-teach eval mechanics — that would duplicate Eval Pilot.

> **Dependency:** a repository that runs Factory-generated evals must have
> the Eval Pilot plugin installed (`copilot plugin install eval-pilot`) and
> the engine available (`npm install --save-dev evalpilot` or `npx
> evalpilot`). The Factory assumes Eval Pilot is present.

## Single source of truth

For every eval mechanic — spec templates, the Markdown DSL, the TypeScript
builder, `kind` values, tags, judge criteria, metrics, structural checks,
CLI commands, flags, environment knobs, and result locations — read the
Eval Pilot docs directly. Do not copy them here:

| Topic | Authoritative source (in `agent-packs/eval-pilot/`) |
|-------|------------------------------------------------------|
| Authoring specs (`*.eval.md`, `*.eval.ts`, `kind`, tags, judge, metrics) | `skills/eval-author/SKILL.md` + `skills/eval-author/references/` |
| Running specs, triage, tag filters, result JSON | `skills/eval-runner/SKILL.md` |
| Numeric metric trends and regression gates | `skills/eval-metrics/SKILL.md` |
| CLI surface (`new`/`run`/`show`/`lint`/`metrics`/`discover`/`init`) | `README.md` + `engine-ts/README.md` |
| Spec templates to copy | `evals/_templates/` (`pack.eval.md`, `skill.eval.md`, `structural.eval.ts`) |

## What the Factory produces (integration contract)

### Creation — `@factory-engineer`

The engineer creates evals by **invoking Eval Pilot's `eval-author`
skill** (or `evalpilot new <name> --target <target> --kind agent|skill`)
to scaffold, then filling in the scenario-specific prompt and assertions
per that skill's guidance. The engineer must produce, for each generated
pack, the following directory shape:

```
evals/packs/<pack>/
├── README.md                   # one paragraph describing coverage
├── <scenario>.eval.md          # at least one behavioral pack eval
└── <scenario>.eval.ts          # optional structural eval (kind: "none")
```

Skill evals mirror this under `evals/skills/<skill>/`.

Minimum bar for a full build:

- At least one `evals/packs/<pack>/<scenario>.eval.md` **or** `.eval.ts`.
- A one-paragraph `evals/packs/<pack>/README.md`.
- Specs parse cleanly under `evalpilot lint evals/packs/<pack>/`.
- The engineer does **not** run live behavioral evals during build; the
  `@factory-eval-runner` executes them (Phase 7.5/7.6).

### Build-manifest contract

The build manifest MUST record eval artifacts so the critic and
orchestrator can verify them without reading `evals/`:

```json
"evals_created": {
  "tests": ["evals/packs/<pack>/<scenario>.eval.md"],
  "readme": "evals/packs/<pack>/README.md"
}
```

`evals_created` must always be present (use `{"tests": [], "readme": null}`
only when `improvement_strategy: "incremental"` flags no eval changes).

### Execution — `@factory-eval-runner`

The Factory Eval Runner owns eval *execution*. It invokes Eval Pilot's
`eval-runner` skill / the `evalpilot run` engine, parses the modeled
`evals/_runs/<run-id>/report.json` (exit code `0` = pass, `1` = fail,
other = harness-error), and returns a structured verdict. The Factory
never reimplements run logic — see `factory-eval-runner.agent.md`.

## Factory Engineer checklist

- [ ] Scaffolded via Eval Pilot's `eval-author` skill / `evalpilot new`.
- [ ] `evals/packs/<pack>/<scenario>.eval.md` or `.eval.ts` exists.
- [ ] Behavioral specs set `target`, `kind`, tags, an action prompt, and
      at least one structural (non-judge) assertion.
- [ ] Structural specs use `kind: "none"`, no `.prompt(...)`, and `.check(...)`.
- [ ] `evals/packs/<pack>/README.md` describes coverage in one paragraph.
- [ ] Eval files appear under `files_created` and `evals_created.tests` in
      the build manifest.
- [ ] `evalpilot lint evals/packs/<pack>/` succeeds.

For anything beyond this contract, defer to the Eval Pilot skills listed
above — they are authoritative.
