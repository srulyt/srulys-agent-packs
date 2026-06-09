# PRD Pilot

**PRD Pilot** is a **lightweight, skills-only agent plugin** that guides you
through producing a high-quality **EARS-style PRD** (Easy Approach to
Requirements Syntax) fast. It ships **no custom agent** — its four skills run
on the host's default agent. The **same single package** works across three
hosts: **GitHub Copilot CLI**, **VS Code GitHub Copilot**, and the
`gh skill` (agentskills.io) tooling.

It is a *lighter, faster* re-imagining of the multi-agent
[`spec-author`](../spec-author/) pack: same quality bar (EARS conventions,
testable acceptance criteria, P0/P1/P2 priority, open-questions
discipline), minus the heavyweight machinery (5 agents, Stop gates,
`state.json` sessions, version/changelog, critic loop). It optimises for
**speed and low friction over first-pass completeness** — iteration is
expected.

> **Preview status.** The VS Code agent-plugin feature and `gh skill` are
> both **preview**. Commands and settings below are accurate to the
> verified specs at the time of writing but may change.

## The 4-step flow

1. **Gather context** — detect fs-search / web-search / `mcp_*` tools,
   build a short in-conversation digest, degrade gracefully if tools are
   missing (never hard-fail).
2. **Grill me** — a "grill me"-style interrogation that closes **every**
   requirement gap before drafting. **No upper cap on questions** — this
   step deliberately favours completeness over speed. Questions are posed
   via the ask-question (`ask_user`) tool: multiple-choice for enumerable
   answers, freeform for open-ended ones.
3. **Propose a short outline** for your approval. If you reject, the
   workflow takes your feedback, re-runs the minimal slice of steps 1–2,
   and re-presents (max 2 revisions).
4. **Format the final PRD** using EARS best practices: valid
   shall-statements, nested testable acceptance criteria, the mandatory
   section catalogue, and a pre-present self-check.

---

## Installation

The plugin is a conformant agent plugin: a `plugin.json` manifest at the
root plus a `skills/` directory. **One package serves all three hosts.**
The repository path to the plugin is `agent-packs/prd-pilot`.

### 1. GitHub Copilot CLI (primary — also lights up VS Code)

Installing via the CLI is the recommended path: **VS Code automatically
discovers CLI-installed plugins** under `~/.copilot/installed-plugins/`,
so this one command surfaces the plugin in both hosts.

This repo is a **plugin marketplace** (it ships a
`.github/plugin/marketplace.json`). Register the marketplace once, then
install the plugin with the `plugin@marketplace` syntax:

```bash
# Register this repo as a marketplace (one-time):
copilot plugin marketplace add srulyt/srulys-agent-packs

# Install the plugin from the registered marketplace:
copilot plugin install prd-pilot@srulys-agent-packs

# …or, from a local clone of this repo, point the marketplace at the path:
copilot plugin marketplace add /absolute/path/to/srulys-agent-packs
copilot plugin install prd-pilot@srulys-agent-packs
```

Manage / verify:

```bash
copilot plugin marketplace browse srulys-agent-packs   # discover plugins
copilot plugin list
copilot plugin enable prd-pilot     # if disabled
```

Interactive equivalent inside a session:
`/plugin marketplace add srulyt/srulys-agent-packs` then
`/plugin install prd-pilot@srulys-agent-packs`.

**Invoke:** run `/prd-pilot:ears-prd-workflow` (optionally with a
topic argument), or just ask the agent to "write an EARS PRD" — the entry
skill's `description` triggers auto-load.

### 2. VS Code GitHub Copilot (agent plugin)

1. **Enable the preview feature gate:** turn on the `chat.plugins.enabled`
   setting (it may be org-managed).
2. **Discover the plugin** by any of:
   - **Auto-discovery from the CLI install (zero extra steps):** if you
     ran the Copilot CLI install above, the plugin already appears under
     **Agent Plugins – Installed** and its skills in **Configure Skills**.
   - **Install From Source (Git URL):** Command Palette → **Chat: Install
     Plugin From Source** → enter
     `https://github.com/srulyt/srulys-agent-packs.git`.
   - **Local folder for development** via the `chat.pluginLocations`
     setting, pointing directly at the plugin directory:
     ```jsonc
     // settings.json
     "chat.pluginLocations": {
       "/absolute/path/to/srulys-agent-packs/agent-packs/prd-pilot": true
     }
     ```

> **Note:** the **Chat: Install Plugin From Source** command takes a Git
> URL for the repository; it does not take a subdirectory path. Use the
> Copilot CLI `OWNER/REPO:agent-packs/prd-pilot` form (option 1) or
> the `chat.pluginLocations` local-folder setting when you need to target
> this plugin's subdirectory specifically.

**Invoke:** run `/prd-pilot:ears-prd-workflow` in Chat, pick the
skill from **Configure Skills**, or ask in natural language.

### 3. `gh skill` (agentskills.io — preview)

`gh skill` consumes the **`skills/<name>/SKILL.md`** files directly. It
**ignores `plugin.json`** entirely, and the plugin-root `skills/` layout
is found **without** `--allow-hidden-dirs`. Non-spec frontmatter
(`user-invocable`, `argument-hint`) is ignored by `gh skill` — harmless,
since those fields only affect the Copilot hosts.

```bash
# Install a single skill from the GitHub repo:
gh skill install srulyt/srulys-agent-packs ears-prd-workflow

# …or from a local clone:
gh skill install --from-local ./agent-packs/prd-pilot/skills/ears-prd-workflow
```

Install the other skills (`prd-context-gathering`,
`grill-me-interrogation`, `ears-prd-format`) the same way for the full
4-step workflow.

> **Publishing note:** `gh skill publish` requires the repository to carry
> the `agent-skills` topic. Publishing is a separate, optional step and is
> not required to install from the repo as shown above.

---

## What ships in the package

```
agent-packs/prd-pilot/
├── plugin.json                                   # manifest (root, Copilot default)
└── skills/
    ├── ears-prd-workflow/SKILL.md                # S1 entry — user-invocable: true
    ├── prd-context-gathering/SKILL.md            # S2 — step 1
    ├── grill-me-interrogation/SKILL.md           # S3 — step 2
    └── ears-prd-format/
        ├── SKILL.md                              # S4 — step 4 + quality bar
        └── references/ears-patterns.md           # EARS worked examples (overflow)
```

There is **no `agents/`**, **no `prompts/`**, **no `chatmodes/`**, **no
`instructions/`**, and **no state directory** — by design. The only file
the workflow writes is the PRD at the path you name (the full PRD is also
always rendered inline in the response).

> **License:** this repository does not ship a `LICENSE` file, so the
> manifest intentionally **omits** a `license` field. Add one to
> `plugin.json` only after a `LICENSE` is added to the repo root.

## Quality bar carried from `spec-author` (audit trail)

| `spec-author` source | What this plugin keeps | What it drops (for speed) |
|---|---|---|
| `spec-driven-prd-best-practices` | EARS pattern catalogue, one-`shall`, what-not-how, testable ACs | PR/FAQ deep-dive, working-backwards essay |
| `prd-template` | mandatory section catalogue, `[TBD]`+OQ rule, EARS FR convention | complexity-gated sections, per-section isolation, `spec_kind` modes |
| `prd-quality-rubric` | D1 coverage + D4 EARS/AC/evidence as a **self-check** | full D1–D10 weighted critic, verdict thresholds, update-mode dims |
| `prd-interview` | P0/P1/P2, do-not-invent, partial-answer fallback, ask-question tool usage (MC vs. freeform) | **the question cap — removed entirely** |
| `mcp-cli-discovery` | detection sources, graceful degradation, no-`execute` | `discovery.json` artifact (kept in conversation) |
| `versioning-discipline`, `prd-evolution` | — | dropped entirely (no update mode / changelog) |

## Output contract

The completing response emits two machine-parseable blocks: `prd-outline`
(emitted at step 3 with `status: proposed`, re-emitted at completion) and
`prd-summary` (`output_path`, `fr_count`, `ears_valid`, `open_questions`,
`degraded_tools`). The full PRD body is rendered inline in the response
and optionally also written to your named output path.

## Evals

- **Pack-level (structural, no CLI):**
  `evals/packs/prd-pilot/test_smoke_plugin_conformance.py` — plugin
  conformance smoke.
- **Behavioural skill evals** (require the `copilot` CLI):
  - `evals/skills/ears-prd-workflow/test_smoke_happy_path.py` — full
    4-step smoke.
  - `evals/skills/ears-prd-workflow/test_outline_rejection_loop.py` —
    reject outline → loop back to steps 1–2 → re-present.
  - `evals/skills/ears-prd-format/test_ears_shape.py` — EARS validity.
  - `evals/skills/grill-me-interrogation/test_question_discipline.py` —
    well-formed questions, P0/P1/P2 tags, MC-vs-freeform, no invented
    answers.

The eval harness stages plugin skills from the plugin-root `skills/`
layout automatically. Run with `pytest evals/packs/prd-pilot/` or
`pytest evals/skills/<skill>/`.
