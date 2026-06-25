# context-pack-builder

A GitHub Copilot **plugin** (custom multi-agent workflow + skills) that
**generates and updates codebase context packs**. Each generated context pack
is itself a **Copilot Skill** — a `SKILL.md` index plus progressively-disclosed
`references/*.md` — written into a context source-of-truth repo and
round-tripped (copied back) into the documented code repo for immediate testing.

## What it does

Seed the builder with a feature name, a description, and/or a few code paths.
A six-agent pipeline then:

1. **Discovers** all related paths across the **whole** repo and **all** layers
   (code, data, tests, docs, config, dependencies).
2. **Analyzes** the discovered files in batches into confidence-scored notes.
3. **Synthesizes** the notes into a unified draft mapped to **five content
   areas** (entry points; file & folder locations per layer; glossary; patterns
   & practices; architecture & design).
4. **Writes** a uniform, publishable context-pack skill into the context repo,
   with idempotent **update-over-rewrite** (no duplicate packs, human edits
   preserved, change-logged).
5. **Splits** the `SKILL.md` into a progressively-loading index +
   `references/01..05` when it exceeds the token threshold, and generates
   **write+copy-back install scripts** for round-trip testing.

## Agents (1 orchestrator + 5 specialists)

| Agent | Role |
|-------|------|
| `@cpb-orchestrator` | Owns the pipeline, STM/checkpoints, NEW-vs-UPDATE routing, retry bounds, user interaction. **User-facing entry point.** |
| `@cpb-discovery` | Finds all related paths across all layers (delegation-only). |
| `@cpb-analyzer` | Extracts confidence-scored notes per content area (delegation-only). |
| `@cpb-synthesizer` | Merges notes into a unified draft (delegation-only). |
| `@cpb-writer` | Materialises the pack; NEW-vs-UPDATE merge (delegation-only). |
| `@cpb-indexer` | Token-split + install-script generation (delegation-only). |

Only `@cpb-orchestrator` is user-invocable. The five specialists are invoked
**only** by the orchestrator via the `task` tool.

## Skills (the builder's own)

| Skill | Purpose |
|-------|---------|
| `context-pack-schema` | The 5 content areas + legacy map, confidence rubric, generated `SKILL.md` / `context-pack.json` schema. |
| `context-discovery` | Multi-layer search heuristics (code, data, tests, docs, config, dependencies). |
| `progressive-disclosure` | The token-split threshold (single source), the uniform index schema, and the write+copy-back install spec. |

## Install

This pack is a plugin registered in `.github/plugin/marketplace.json`. From a
Copilot CLI host that has this repo's marketplace configured:

```
copilot plugin install context-pack-builder
```

Or use it in-repo: with the repo open, the agents under `agents/` and skills
under `skills/` are auto-discovered. Invoke the orchestrator:

```
@cpb-orchestrator build a context pack for the "checkout" feature, seed paths: src/checkout/
```

## Round-trip (copy-back) testing

After a run, the indexer generates `_install/install-context-pack.{sh,ps1}` in
the **generated pack dir** (not this plugin). The **user** runs it to copy the
generated skill into a code repo's harness skills dir:

```
sh context-packs/<slug>-context/_install/install-context-pack.sh
# or on Windows:
pwsh context-packs/<slug>-context/_install/install-context-pack.ps1
```

Harness-dir resolution: explicit arg / `CPB_HARNESS_SKILLS_DIR` env → walk up
for `.git`/`.github` → `<repo>/.github/skills/` → `~/.copilot/skills/` → else
exit non-zero. **No agent ever runs the script.**

## Generated pack shape (uniform, publishable)

```
context-packs/<slug>-context/
├── plugin.json                  # independently installable
├── context-pack.json            # provenance + idempotency key
├── skills/<slug>-context/SKILL.md   # FULL or INDEX (if split)
│   └── references/01..05.md      # present only after a split
└── _install/install-context-pack.{sh,ps1}
```

## Preview status

The exact published token threshold (currently **5,000 tokens**, centralised in
`skills/progressive-disclosure/references/split-threshold.md`) and the
`plugin.json` field set are drawn from current knowledge + the verified in-repo
plugin precedents (`agent-packs/eval-pilot/`,
`agent-packs/product-knowledge-brain/`) — they could **not** be re-verified
against the live GitHub Copilot / Anthropic Agent Skills docs in the build
environment (no web access). Both are **centralised** (one skill reference, one
manifest) so a correction is a one-line change. **Re-confirm against the live
docs before publishing.** The structural conformance eval
(`evals/packs/context-pack-builder/test_smoke_plugin_conformance.py`) gates the
parts that matter mechanically.

## Evals

See `evals/packs/context-pack-builder/`:

- `test_smoke_plugin_conformance.py` — structural, no CLI: manifest, dirs,
  marketplace registration, frontmatter quoting/keys, no index over threshold.
- `test_smoke_new_context_pack.py` — happy-path NEW pack (judge).
- `test_progressive_disclosure_split.py` — split fires on a large feature.
- `test_update_over_rewrite.py` — idempotent UPDATE (no duplicate, change log,
  human-edit preservation, no-op re-run).

Run: `pytest evals/packs/context-pack-builder/`.

## State (STM)

Pipeline state lives under `.context-pack-builder-stm/` (git-ignored), keyed by
session id, checkpoint-resumable. State is shared between agents only through
these on-disk files.
