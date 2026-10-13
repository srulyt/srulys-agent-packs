# spec-writer

The spec-writer skill writes, updates, and publishes EARS-style specifications (PRDs and technical specs). It uses one fixed template, conditional sections, and a draft/publish lifecycle. It also derives what can go wrong (edge cases, errors, failures, permission and concurrency cases) and writes each case as a functional requirement, so reviewers don't have to ask "but what if…?".

The pack is one skill with no agents, personas, or session state. It replaces `spec-author`, `spec-creator`, and `prd-pilot`, which remain in the repo unchanged. See [MIGRATION.md](MIGRATION.md) for what was kept and what was removed.

## Install

### GitHub Copilot CLI (also surfaces in VS Code)

```bash
copilot plugin marketplace add srulyt/srulys-agent-packs
copilot plugin install spec-writer@srulys-agent-packs
```

### VS Code

Use **Chat: Install Plugin From Source** with the repository URL, or point the `chat.pluginLocations` setting at a local clone:

```jsonc
"chat.pluginLocations": {
  "/absolute/path/to/srulys-agent-packs/agent-packs/spec-writer": true
}
```

### `gh skill` (preview)

```bash
gh skill install srulyt/srulys-agent-packs spec-writer
# or from a local clone:
gh skill install --from-local ./agent-packs/spec-writer/skills/spec-writer
```

## Use

Run `/spec-writer:spec-writer`, or ask in natural language, for example: "write a spec for…", "update the spec to add…", "publish the spec as 1.0.0".

If your source material is a `.docx` or `.vtt`, export it to Markdown or text first.

## Layout

```text
agent-packs/spec-writer/
├── plugin.json
├── MIGRATION.md
└── skills/spec-writer/
    ├── SKILL.md                         # outcome, invariants, completion
    ├── assets/spec-template.md          # output contract
    └── references/
        ├── sections-and-gating.md       # mandatory/gated sections, spec_kind, IDs
        ├── requirements-writing.md      # EARS, priorities, ACs, metrics, NFRs
        ├── what-if-coverage.md          # deriving negative-path FRs
        ├── writing-quality.md           # voice, signal density, citations, user context
        ├── lifecycle.md                 # draft/publish, versioning, minimal edits
        ├── interviewing.md              # closing gaps before drafting
        └── quality-checklist.md         # blocker/major/minor review
```

## Evals

Evals live in `evals/packs/spec-writer/`: one static pack-shape eval and seven behavioural evals that prove the business logic (what-if FRs, no fabrication, UI/backend gating, published-spec updates, publish mechanics, review-proposes-only). Run them with `node scripts/run-evals.mjs spec-writer -- --parallel 7`. See that folder's README for details.
