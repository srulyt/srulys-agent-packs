# Product Knowledge Brain

**Product Knowledge Brain** is a **skills-only agent plugin** that turns
already-extracted text into durable, evolving Product-Management
**institutional memory** — a *living wiki*, not a document dump. It ships
**no custom agent**: its four skills run on the host's default agent
(GitHub Copilot CLI or VS Code GitHub Copilot). The **same single package**
works across three hosts: **GitHub Copilot CLI**, **VS Code GitHub
Copilot**, and the `gh skill` (agentskills.io) tooling.

It is invoked **frequently by other processes** whenever something needs to
write to or evolve the knowledge base. Each invocation runs a
deterministic, **idempotent, crash-safe** 10-step knowledge-evolution
cycle and checkpoints its in-flight state to disk so a mid-operation
context compaction loses **nothing**.

> **Scope boundary.** This plugin's job begins at *"I have extracted text;
> evolve the brain."* It does **not** do document ingestion, file /
> PowerPoint / email parsing, transcript retrieval, or MCP / external
> integration. All source content is assumed **already extracted into
> text** by upstream tools. The plugin writes only curated knowledge pages
> and **evidence descriptors** — never raw source material.

> **Preview status.** The VS Code agent-plugin feature and `gh skill` are
> both **preview**. Commands and settings below are accurate to the
> verified specs at the time of writing but may change.

## What it produces

Two on-disk artifacts:

1. **The knowledge base** (the primary deliverable) — a product-centric
   living wiki under a caller-named root (default `knowledge-base/`):
   curated concept pages, typed relationships + backlinks, evidence
   descriptors, ADR-style decision history, discovery indexes, and
   generated specialized **index skills**.
2. **A durable STM working state** under `.product-knowledge-brain-stm/`
   that checkpoints the in-flight evolution cycle between every step.

## The 10-step evolution cycle

The entry skill `knowledge-brain` owns this cycle and routes each step to a
specialist skill:

1. Receive extracted information → `knowledge-brain`
2. Classify information → `knowledge-consolidation`
3. Determine affected areas → `knowledge-consolidation`
4. Update existing knowledge → `knowledge-consolidation` + `knowledge-organization`
5. Create new knowledge (only if needed) → `knowledge-organization`
6. Create relationships → `knowledge-organization`
7. Update indexes → `knowledge-indexing`
8. Refactor structure if required → `knowledge-indexing`
9. Remove duplication → `knowledge-consolidation`
10. Preserve provenance → `knowledge-organization`

Steps 2→9 enforce **update-over-create** (consolidation) before any new
page is written, so the repo gets *simpler* and *more valuable* as it
grows. Contradictions are queued and resolved via change-log / ADR entries
— historical decisions are **never silently overwritten**.

---

## Installation

The plugin is a conformant agent plugin: a `plugin.json` manifest at the
root plus a `skills/` directory. **One package serves all three hosts.**
The repository path to the plugin is `agent-packs/product-knowledge-brain`.

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
copilot plugin install product-knowledge-brain@srulys-agent-packs

# …or, from a local clone of this repo, point the marketplace at the path:
copilot plugin marketplace add /absolute/path/to/srulys-agent-packs
copilot plugin install product-knowledge-brain@srulys-agent-packs
```

Manage / verify:

```bash
copilot plugin marketplace browse srulys-agent-packs   # discover plugins
copilot plugin list
copilot plugin enable product-knowledge-brain     # if disabled
```

Interactive equivalent inside a session:
`/plugin marketplace add srulyt/srulys-agent-packs` then
`/plugin install product-knowledge-brain@srulys-agent-packs`.

**Invoke:** run `/product-knowledge-brain:knowledge-brain` (optionally with
the extracted text or a path argument), or just ask the agent to
"consolidate this into the knowledge base" / "update the product wiki" —
the entry skill's `description` keywords trigger auto-load.

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
       "/absolute/path/to/srulys-agent-packs/agent-packs/product-knowledge-brain": true
     }
     ```

> **Note:** the **Chat: Install Plugin From Source** command takes a Git
> URL for the repository; it does not take a subdirectory path. Use the
> Copilot CLI `OWNER/REPO:agent-packs/product-knowledge-brain` form
> (option 1) or the `chat.pluginLocations` local-folder setting when you
> need to target this plugin's subdirectory specifically.

**Invoke:** run `/product-knowledge-brain:knowledge-brain` in Chat, pick
the skill from **Configure Skills**, or ask in natural language.

### 3. `gh skill` (agentskills.io — preview)

`gh skill` consumes the **`skills/<name>/SKILL.md`** files directly. It
**ignores `plugin.json`** entirely, and the plugin-root `skills/` layout
is found **without** `--allow-hidden-dirs`. Non-spec frontmatter
(`user-invocable`) is ignored by `gh skill` — harmless, since that field
only affects the Copilot hosts.

```bash
# Install the entry skill from the GitHub repo:
gh skill install srulyt/srulys-agent-packs knowledge-brain

# …or from a local clone:
gh skill install --from-local ./agent-packs/product-knowledge-brain/skills/knowledge-brain
```

Install the specialist skills (`knowledge-consolidation`,
`knowledge-organization`, `knowledge-indexing`) the same way for the full
cycle.

> **Publishing note:** `gh skill publish` requires the repository to carry
> the `agent-skills` topic. Publishing is a separate, optional step and is
> not required to install from the repo as shown above.

---

## What ships in the package

```
agent-packs/product-knowledge-brain/
├── plugin.json                                  # manifest (root, Copilot default)
├── .gitignore                                   # ignores the STM working-state root
└── skills/
    ├── knowledge-brain/                         # entry — user-invocable: true
    │   ├── SKILL.md
    │   └── references/
    │       ├── evolution-cycle.md               # 10-step runbook (idempotent)
    │       └── stm-schema.md                    # STM layout + checkpoint protocol
    ├── knowledge-consolidation/                 # user-invocable: false
    │   ├── SKILL.md
    │   └── references/
    │       ├── knowledge-types.md
    │       └── contradiction-changelog.md
    ├── knowledge-organization/                  # user-invocable: false
    │   ├── SKILL.md
    │   └── references/
    │       ├── repo-layout.md
    │       ├── page-templates.md
    │       └── relationships-provenance.md
    └── knowledge-indexing/                       # user-invocable: false
        ├── SKILL.md
        └── references/
            ├── index-schema.md
            ├── refactoring-heuristics.md
            └── dynamic-index-skills.md
```

There is **no `agents/`**, **no `prompts/`**, **no `chatmodes/`**, **no
`instructions/`**, and **no `.github/`** directory — by design. This is a
skills-only plugin.

> **License:** this repository does not ship a `LICENSE` file, so the
> manifest intentionally **omits** a `license` field. Add one to
> `plugin.json` only after a `LICENSE` is added to the repo root.

## On-disk knowledge base (the deliverable)

The KB root defaults to `knowledge-base/` and is **caller-overridable** via
a documented parameter (pass `kb_root: <path>` or say "use `<path>` as the
knowledge base"). It is product-centric: knowledge lives under product
**areas**, with cross-cutting concept pages (personas, segments, strategic
goals, competitors, decisions) at the root, discovery indexes under
`indexes/`, evidence descriptors under `evidence/`, and generated
specialized index skills under `_skills/`. See
`skills/knowledge-organization/references/repo-layout.md` for the full
layout.

## Durable STM (no-data-loss guarantee)

The in-flight evolution cycle checkpoints to
`.product-knowledge-brain-stm/runs/{session-id}/` between **every** step
(write state before the step; persist the step artifact + update the
checkpoint after). On resume after a context compaction, the skill reads
`checkpoint.json`, skips completed steps (content-hash keyed, so re-running
one is a no-op), and continues from `next_step`. See
`skills/knowledge-brain/references/stm-schema.md`.

## Output contract

The completing response emits a machine-parseable `knowledge-brain-summary`
fenced block (`kb_root`, `session_id`, `cycle_status`, `pages_created`,
`pages_updated`, `relationships_added`, `indexes_updated`,
`contradictions`, `evidence_added`, `dynamic_index_skills`,
`open_questions`). See `skills/knowledge-brain/SKILL.md`.

## Evals

- **Pack-level (structural, no CLI):**
  `evals/packs/product-knowledge-brain/test_smoke_plugin_conformance.py` —
  plugin conformance smoke.
- **Behavioural pack evals** (require the `copilot` CLI):
  `test_smoke_consolidation_happy_path.py`,
  `test_stm_checkpoint_survives_compaction.py`,
  `test_update_over_create.py`,
  `test_provenance_relationship_links.py`,
  `test_index_update.py`,
  `test_dynamic_index_skill_generation.py`.

Run with `pytest evals/packs/product-knowledge-brain/`.
