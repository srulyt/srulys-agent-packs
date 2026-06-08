---
name: marp-engine
description: "Author Marp/Marpit markdown decks, render them to PNG/PDF for visual QA, and convert Marp → PPTX — with a self-probing, verify-or-block toolchain policy. Use when output_mode is marp or both. Keywords: marp, marpit, markdown slides, marp-cli, marp to pptx, marp theme, output_mode."
license: MIT
---

# Marp Engine

Author Marp/Marpit markdown decks, render them to PNG for visual QA, and
(optionally) convert them to PPTX — sharing the **same six design-system
tokens** the python-pptx path uses, and the **same verify-or-block
discipline** the pptx render path uses.

> **Marp is intentionally simpler than native python-pptx.** Marp's CSS
> layout is coarser than python-pptx EMU control. That trade-off is
> acceptable and expected (the user accepted "simpler Marp slides"). For
> `output_mode: both`, treat the Marp markdown as the *source-of-record*
> and build the **pptx independently via python-pptx** for full design
> fidelity — `marp --pptx` (image-based) is only the fallback when
> python-pptx is unavailable.

## When to Use This Skill

Load this skill when:
- `intake.json.output_mode` is `marp` or `both` (see
  `.story-telling-stm/schemas/intake.schema.json`).
- You need to render Marp markdown to PNG so `@deck-critic` can run the
  multimodal rubric on it.
- You need to convert Marp markdown to a `.pptx`.

Do **not** load it for `output_mode: pptx` (the default) — that path is
fully owned by `pptx-engine`.

## Toolchain (self-probe; never assume present)

| Stage | Tool | Probe | On miss |
|-------|------|-------|---------|
| Render PNG/PDF (QA) | Node + `@marp-team/marp-cli` | `marp` on PATH, else `npx --no-install @marp-team/marp-cli --version` | **BLOCK** (user decision) |
| Marp → image-based pptx | same marp-cli | as above | **BLOCK** |
| Marp → **editable** pptx | `soffice` (LibreOffice) + marp-cli `--pptx-editable` (experimental) | `soffice`/`libreoffice` on PATH | downgrade to image-based pptx, record in manifest |

`scripts/render_marp.py` performs every probe. **It never silently emits
unverified output**: on a missing toolchain it writes a manifest with
`status: "blocked"`, `user_decision_required: true`, and concrete
`install_instructions`, and prints a `BLOCKED:` line. The caller surfaces
that as a user decision (install / ship-unverified-with-consent / abort)
via the orchestrator Phase 6 gate — exactly the same policy as the pptx
`render_unverified` / `unverified-needs-user` path (decisions.md OQ5).

**Non-interactive & self-bounding (hang-safe).** Every external invocation
the script makes (`marp`, `npx`, and — via `--pptx-editable` —
LibreOffice/`soffice`) runs with **stdin closed** (so a first-run
`npx @marp-team/marp-cli` "Ok to proceed?" prompt or a LibreOffice prompt
can never block on input), a **per-stage timeout** (probe 60s, PNG render
240s, pptx convert 240s), and a **process-tree kill** on timeout so a
detached grandchild (marp-cli's headless Chromium, or a `soffice.bin`
daemon) can never wedge an unbounded drain. A slow / interactive / broken
toolchain therefore degrades to a *fast graceful BLOCK*, never an
indefinite hang. Never call `npx @marp-team/marp-cli` or `soffice`
directly from the agent — always go through `render_marp.py`, which
enforces these guarantees.

Source: <https://github.com/marp-team/marp-cli> (convert to pdf/pptx/png;
`--pptx-editable` requires LibreOffice).

## Quick Start

```bash
# Render Marp markdown -> PNG for QA, themed with the design-system CSS,
# and also produce a pptx. Writes manifest.json mirroring pptx-visual-qa.
python .github/skills/marp-engine/scripts/render_marp.py \
  --md    .story-telling-stm/runs/<sid>/agents/deck-builder/deck.md \
  --theme .story-telling-stm/runs/<sid>/agents/deck-builder/theme.css \
  --out   .story-telling-stm/runs/<sid>/agents/deck-builder/marp-renders/ \
  --pptx  .story-telling-stm/runs/<sid>/agents/deck-builder/output.pptx
```

Always inspect the resulting `manifest.json`: if `status == "blocked"`,
**stop and surface the user decision** — do not report success.

## Authoring Marp Markdown

A Marp deck is a single `.md` file with a YAML front-matter directive
block, slides separated by `---`, and per-slide directives.

```markdown
---
marp: true
theme: story-telling
paginate: true
size: 16:9
---

<!-- _class: title -->
# Defer is more expensive than invest now
#### CFO + finance committee — Q3 review

---

<!-- _class: section -->
# The cost of waiting

---

## Three forces are compounding
- Tech debt interest is now 18% of velocity
- Two enterprise deals blocked on the gap
- Hiring can't outrun the backlog

<!--
Speaker notes go in an HTML comment on each slide.
Two to three sentences, specific data, a transition cue.
-->
```

Authoring rules (inherit the pptx canon — do not restate it):
- **One message per slide**, action titles, ≤4 bullets / ≤15 words each
  (see `presentation-design/SKILL.md`).
- **Speaker notes on every slide** via an HTML comment block. The Marp
  PNG cannot carry notes, so notes also go into `deck-spec.json` so the
  structural checks and the pptx path stay in sync.
- **Style gating still applies**: most slides `_class: simple`; promote
  to styled (`title`, `section`, `hero`) only at inflection points
  (see `presentation-design/references/style-gating.md`).

## Theming = design-token parity

The Marp theme CSS is **generated from the same six design systems** the
pptx path uses, so a `marp` or `both` deck inherits the *same* palette and
type scale as the `pptx` deck. Map design-system tokens →
Marp CSS custom properties per
[`references/marp-theming.md`](references/marp-theming.md). Never invent a
parallel Marp palette — token parity is mandatory (concern C3).

## Modes (output_mode)

| `output_mode` | Marp markdown | Marp PNG (QA) | pptx |
|---------------|---------------|---------------|------|
| `pptx` (default) | — | — | python-pptx (pptx-engine) |
| `marp` | ✅ deliverable | ✅ via render_marp.py | — |
| `both` | ✅ source-of-record | ✅ via render_marp.py | ✅ **python-pptx** (full fidelity); `marp --pptx` only as fallback |

## QA hand-off

`render_marp.py` writes `marp-renders/manifest.json` whose schema mirrors
`pptx-visual-qa/references/render-pipeline.md` (`render_engine`, `slides[]`
with `png_path`, `errors[]`, `duration_ms`) plus Marp-specific fields
(`status`, `block_reason`, `user_decision_required`, `pptx_path`,
`pptx_editable`, `install_instructions`). `@deck-critic` runs the **same**
multimodal rubric over the Marp PNGs and applies the **same** verify-or-block
verdict logic.

## Anti-Patterns

| Anti-Pattern | Problem | Solution |
|--------------|---------|----------|
| Ship Marp output when marp-cli is missing | Unverified output — violates the user's "don't ship unassured" rule | BLOCK; surface install/ship/abort decision |
| Invent a separate Marp palette | Modes drift visually | Generate theme from design-system tokens (token parity) |
| Use `marp --pptx` for `both` mode pptx | Image-based, non-editable, lower fidelity | Build pptx via python-pptx; `marp --pptx` is fallback only |
| Silent `npx` network fetch | Unexpected network/consent | `--allow-npx-fetch` is opt-in; otherwise block |

## Quality Checklist

- [ ] Toolchain probed; on miss, manifest `status: "blocked"` + user decision surfaced
- [ ] Theme CSS generated from design-system tokens (palette + type scale parity)
- [ ] Every slide has speaker notes (in the `.md` comment AND `deck-spec.json`)
- [ ] `marp` mode: PNGs rendered and QA'd; `both` mode: pptx built via python-pptx
- [ ] `manifest.json` written mirroring the pptx-visual-qa schema

## References

- [marp-theming.md](references/marp-theming.md) — design-system tokens →
  Marp CSS custom properties (token-parity mapping for all six systems).

## Assets / Scripts

- [scripts/render_marp.py](scripts/render_marp.py) — probe toolchain,
  render PNG, convert to pptx, emit verify-or-block manifest.
