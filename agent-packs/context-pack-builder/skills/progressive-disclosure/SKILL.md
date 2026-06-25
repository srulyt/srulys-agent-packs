---
name: progressive-disclosure
description: "Progressive-disclosure + install logic for generated context packs: the SKILL.md token-split threshold and measurement, the uniform index schema, and the write+copy-back install scripts. Keywords: progressive disclosure, split threshold, SKILL.md index, references, install script, copy-back, round-trip."
---

# Progressive Disclosure

How a generated context pack stays a **lean entry point**: the token-split
threshold, the uniform index schema once split, and the write+copy-back install
scripts. Loaded by the indexer (and the writer for the index schema).

## When to Use This Skill

Load this skill when:
- Measuring a `SKILL.md` body and deciding whether to split (indexer).
- Restructuring a `SKILL.md` into an index + `references/01..05` (indexer).
- Generating the `_install/` copy-back scripts (indexer).

## Quick Start

1. Measure the `SKILL.md` body (frontmatter excluded). See
   [references/split-threshold.md](references/split-threshold.md) — the
   **single source of truth** for the threshold constant (**5,000 tokens**) and
   the deterministic heuristic.
2. If over threshold → split into the uniform index + `references/01..05`. See
   [references/skill-index-schema.md](references/skill-index-schema.md).
3. Generate `_install/install-context-pack.{sh,ps1}`. See
   [references/install-roundtrip.md](references/install-roundtrip.md) — the
   single source so the two scripts cannot drift.

## Core Concepts

### Progressive disclosure

A `SKILL.md` should be a **lean entry point** that loads detail on demand from
bundled `references/*.md`. Keeping the index small saves context tokens when the
harness auto-loads the pack. The split is **re-evaluated every run**: a pack can
cross the threshold as it grows, or uncross it as it shrinks (then `references/`
collapse back into `SKILL.md`).

### Split threshold (centralised)

The threshold is **5,000 tokens** of body. It lives in **one** place —
[references/split-threshold.md](references/split-threshold.md) — so a correction
(e.g. after re-verifying live docs) is a one-line change. The conformance eval
asserts no shipped index `SKILL.md` body exceeds it.

### Round-trip install

The pack is written to the **context repo**; the generated `_install/` scripts
**copy it back** into a code repo's harness skills dir when the **user** runs
them. No agent ever runs the scripts.

## Best Practices

1. **Centralise the number** — never hardcode the threshold in the agent prompt;
   read it from `split-threshold.md`.
2. **Index stays under threshold** — the whole point of splitting.
3. **Two native scripts, one logic source** — `.sh` + `.ps1` share identical
   behaviour described in `install-roundtrip.md`.
4. **Agent generates, user runs** — the indexer never executes the scripts.

## Quality Checklist

- [ ] Body measured with the deterministic heuristic (frontmatter excluded).
- [ ] Split fires iff either estimate exceeds the threshold.
- [ ] On split: index body under threshold; `references/01..05` present.
- [ ] On uncross: `references/` collapsed back; removed files recorded.
- [ ] Both install scripts generated; neither executed by an agent.

## References

- [split-threshold.md](references/split-threshold.md) — the threshold constant +
  measurement heuristic (single source of truth).
- [skill-index-schema.md](references/skill-index-schema.md) — the uniform index
  `SKILL.md` layout.
- [install-roundtrip.md](references/install-roundtrip.md) — the write+copy-back
  script spec (single source for both native scripts).
