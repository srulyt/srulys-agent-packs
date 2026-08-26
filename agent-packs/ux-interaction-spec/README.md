# ux-interaction-spec

A GitHub Copilot **plugin** (multi-agent workflow + skills) that turns a PRD,
a brief, a pile of notes, or a rough feature concept into a **design-ready
behaviour specification** — not a design.

It produces **three documents**, always all three, in a location you confirm:

| Document | File | Shape |
|---|---|---|
| **Experience Interaction Specification** | `eis.md` | 22 sections, fixed order |
| **UX Pattern Research** | `ux-pattern-research.md` | 10 sections, fixed order |
| **UX Decision Log** | `decision-log.md` | 6 sections, fixed order |

The EIS specifies **behaviour before interface**: actors, conceptual model,
terminology, permissions and capability matrices, state models, entry points,
user journeys, system workflows, service blueprint, interaction contracts,
system feedback, error and recovery behaviour, edge cases, accessibility and
localization, design-handoff constraints, decisions, assumptions, open
questions and requirements traceability. It deliberately does **not** decide
colors, typography, spacing, layout or components — that is the designer's
job, and doing it early is how a spec stops being useful.

## What it does

1. **Analyzes** every supplied input into a frozen `REQ-###` inventory, with
   contradictions recorded rather than resolved, and supplied UX concepts
   recorded as *proposals* rather than requirements.
2. **Asks you the questions that actually matter** at three gates — and only
   those. A question is asked when a wrong default would change a flow's
   shape, a state's existence, an entry point, or a permission boundary.
3. **Researches** the host product, direct competitors and adjacent analogues,
   labelling every claim as Observed fact, Inference or Recommendation with a
   source, and converting patterns into adopt / adapt / reject / context-only
verdicts.
4. **Models** the interaction across four resumable passes, filling a
   pre-materialised 22-heading skeleton in place.
5. **Reviews** the result adversarially against a 16-point Definition of Done,
   an anti-requirement lint, and six named audits that read the ledgers on
   disk rather than trusting anyone's summary.

## Agents (1 orchestrator + 4 specialists)

| Agent | Role |
|---|---|
| `@ux-interaction-spec` | Owns the conversation, the phase machine, the question gates, the output location and session state. **The only user-facing agent.** |
| `@eis-context-analyst` | Indexes inputs, extracts the frozen requirement inventory, triages input shape, drafts the research brief, infers the output location. |
| `@ux-pattern-researcher` | Owns `ux-pattern-research.md` and the evidence ledger. |
| `@eis-author` | Owns `eis.md` and `decision-log.md`. Writes in four passes. |
| `@eis-critic` | The quality bar as a role. Reports; never edits. |

The four specialists are invoked **only** by the orchestrator via the `task`
tool. They refuse direct user invocation and refuse to be proxied by another
agent.

## Skills

| Skill | Purpose |
|---|---|
| `eis-document-contracts` | The three verbatim document skeletons, the ledger record schemas, the question format, the matrix shapes, the interaction-contract field list, the diagram conventions, the output-location heuristics. |
| `interaction-modeling` | The three-layer separation rule, the modeling method per section, input triage, the governance placement map, the core-objective coverage map. |
| `ux-research-method` | Research categories, source hierarchy, evidence labelling, synthesis and precedent judgment. |
| `eis-quality-bar` | The quality bar by category, the 16-point Definition of Done, the anti-requirement lints, the 14 discovery probes, the 14 conceptual distinctions. |

## Installation

This pack is a conformant **Copilot agent plugin**: a `plugin.json` manifest at
the pack root plus `agents/` and `skills/` directories. It is registered in
this repo's plugin marketplace (`.github/plugin/marketplace.json`).

```bash
# Register this repo as a marketplace (one-time):
copilot plugin marketplace add srulyt/srulys-agent-packs

# Install the plugin:
copilot plugin install ux-interaction-spec@srulys-agent-packs
```

Manage / verify:

```bash
copilot plugin marketplace browse srulys-agent-packs
copilot plugin list
copilot plugin enable ux-interaction-spec
```

Interactive equivalent inside a session:
`/plugin marketplace add srulyt/srulys-agent-packs` then
`/plugin install ux-interaction-spec@srulys-agent-packs`.

### VS Code

Turn on the `chat.plugins.enabled` setting, then either let VS Code
auto-discover the CLI install under `~/.copilot/installed-plugins/`, or point
`chat.pluginLocations` at
`/absolute/path/to/srulys-agent-packs/agent-packs/ux-interaction-spec`.

## Invoke

```
@ux-interaction-spec I need an interaction spec for governed data product access.
```

That is enough — it will ask for the rest. To skip the intake questions
entirely, supply the keys directly as `Key: value` lines:

```
@ux-interaction-spec
Feature: Governed data product access
Host product: Acme Data Cloud
Inputs: docs/prd/data-access.md, docs/notes/operations-notes.md
Output dir: docs/specs/governed-data-product-access
Research mode: full
Interaction mode: interactive
On existing files: new-version
Max review rounds: 2
```

Recognised keys: `Feature:`, `Host product:`, `Inputs:`, `Output dir:`,
`Research mode:` (`full` | `degraded` | `skipped`), `Interaction mode:`
(`interactive` | `non-interactive`), `On existing files:` (`overwrite` |
`new-version` | `stop`), `Max review rounds:` (1–4), `Max specialist retries:`
(0–4). Anything you supply is recorded, not asked. The two `Max` keys can only
**lower** a ceiling.

## Where the documents go

The pack never guesses silently. The analyst surveys your project's directory
structure — layout only, not file contents — and proposes a concrete path with
a one-line rationale naming the evidence it saw (*"`docs/specs/<feature>/` —
the repo already has `docs/specs/billing/` and `docs/specs/search/`"*), plus up
to two alternatives. The orchestrator then **always** asks you to confirm, even
when the proposal is high-confidence and even when you supplied the path
yourself. The confirmed location is **write-once** for the session: relocating
means starting a new session. In non-interactive runs nothing is asked — the
supplied path, or failing that the proposal, is used, and the delivery report
leads with the location and the fact that it was assumed rather than confirmed.

## Ceilings, not targets

Four numbers bound the run. Each is a **ceiling** — the point at which the
pack stops — and never a quota to spend:

| Loop | Ceiling |
|---|---|
| Review rounds | 4 |
| Re-requests of one specialist within a round | 4 |
| Research top-ups | 2 |
| Questions per gate | 14 |

A run that reaches PASS after one review round with three questions asked is
the **good** outcome, not an under-used allowance.

## Research modes

`full` browses; `degraded` browses partially and labels every gap; `skipped`
browses not at all. **All three still produce `ux-pattern-research.md` with all
ten headings** — the mode sets the depth, never the existence. In `skipped`
mode each heading carries `Not performed — research_mode: skipped (<reason>)`
plus the `EV-GAP-###` ids naming what would have been verified, the
implications matrix still renders with `Unverified` cells, and every
recommendation is demoted to an assumption. The critic scores this honestly
rather than failing the run for a mode you chose.

## Session state

Short-term memory lives under `.ux-interaction-spec-stm/` in your working
directory: one `runs/{session-id}/` directory per run holding `state.json`, the
captured context, six append-only ledgers, and the review artifacts. It is
`.gitignore`d by default. It exists so a four-pass authoring run survives a
context reset — `state.passes_completed` makes the sequence resumable.

## Notes for maintainers

- **Frontmatter `name` equals the kebab-case filename stem for every agent**
  (`eis-critic.agent.md` → `name: eis-critic`). This is deliberate. The Copilot
  CLI resolves agents by filename stem, but this repo also documents a
  friendly-display-name convention; making the two literals identical means
  both readings resolve to the same agent id, so `task(agent_type: "eis-critic")`
  is correct under either. **Please do not "fix" these to friendly display
  names** — the delegation calls in the orchestrator prompt reference these
  exact strings, and `pack-shape.eval.ts` asserts the equality.
- `agents/eis-author.passes.md` is an **agent-local reference**, not an agent.
  It has no frontmatter on purpose; the plugin loader registers only
  `*.agent.md`. If a future loader version rejects non-agent files inside a
  directory-string `agents/` entry, move it to
  `skills/interaction-modeling/references/eis-author-passes.md`.
  **This is a manual migration instruction, not a live second path.** That
  target file does **not** exist in the pack today, and nothing creates it. If
  `agents/eis-author.passes.md` fails to load, `@eis-author` detects the
  missing file and halts with a `blocked-on` report rather than guessing at the
  pass protocol — which is the correct behaviour, but it is a stop, not a
  failover. Verify the file loads on first install; if it does not, copy it to
  the fallback path yourself before running the pack.
- The three document skeletons in
  `skills/eis-document-contracts/references/` are **verbatim contracts**: 22,
  10 and 6 headings in a fixed order. Do not rename, reorder, merge or
  "improve" them; three agents and six eval assertions depend on the literals.

## Evals

Seven specs under `evals/packs/ux-interaction-spec/`: six behavioural
(`kind: agent`) and one structural (`pack-shape.eval.ts`, `kind: none`,
deterministic, no judge).

```bash
evalpilot run evals/packs/ux-interaction-spec/
node scripts/run-evals.mjs ux-interaction-spec
```

See `evals/packs/ux-interaction-spec/README.md` for what each spec covers.
