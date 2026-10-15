# brief-writer

The brief-writer skill creates and edits decision-grade product briefs, one-pagers, and decision memos. A brief it produces:

- is written for its actual audience
- leads with business outcomes the reader is measured on
- gives the reader statements they can repeat to their own leadership
- grounds every claim in your sources
- reads like a sharp human wrote it, with no filler, buzzwords, or AI-isms

The pack is one skill with no agents, personas, or session state. It replaces the multi-agent `product-brief` pack, which remains in the repo unchanged. See [MIGRATION.md](MIGRATION.md) for what was kept and what was removed.

## Install

### GitHub Copilot CLI (also surfaces in VS Code)

```bash
copilot plugin marketplace add srulyt/srulys-agent-packs
copilot plugin install brief-writer@srulys-agent-packs
```

### VS Code

Use **Chat: Install Plugin From Source** with the repository URL, or point the `chat.pluginLocations` setting at a local clone:

```jsonc
"chat.pluginLocations": {
  "/absolute/path/to/srulys-agent-packs/agent-packs/brief-writer": true
}
```

### `gh skill` (preview)

```bash
gh skill install srulyt/srulys-agent-packs brief-writer
# or from a local clone:
gh skill install --from-local ./agent-packs/brief-writer/skills/brief-writer
```

## Use

Run `/brief-writer:brief-writer`, or ask in natural language. For example:

- "Write a product brief from these notes for the VP of Sales."
- "Turn this transcript into a one-pager."
- "Tighten this brief and remove the AI-isms."
- "Apply these review comments to the brief."

Say who the audience is if you can. The skill asks if it can't tell. It never adds web or tool research without your approval. When it finishes, it reports the brief type, maturity, audience, closing type, and open questions it used.

## Layout

```text
agent-packs/brief-writer/
├── plugin.json
├── MIGRATION.md
└── skills/brief-writer/
    ├── SKILL.md                            # outcome, invariants, completion
    ├── assets/brief-template.md            # section skeleton and table shapes
    └── references/
        ├── structure.md                    # brief type, maturity, sections, closing types, headings, lint
        ├── audience-and-championing.md     # audience calibration, cascade, incentives, posture
        ├── writing-style.md                # executive voice, readability, filler, AI-isms, length
        ├── evidence.md                     # sources, labels, decision status, numbers, external knowledge
        ├── decision-framing.md             # options, metrics, plan, financials, closing readiness
        └── review-and-editing.md           # quality checklist, editing existing briefs, review feedback
```

## Evals

Evals live in `evals/packs/brief-writer/`:

- one static pack-shape eval
- behavioural evals covering a late-stage decision ask, a scope-brief with no phantom ask, an early-stage brief with no padding, editing an existing brief, and unsourced numbers

Run them with `node scripts/run-evals.mjs brief-writer`.
