# Product Storytelling Agent

Transform graph-like product knowledge into compelling, audience-specific
PowerPoint decks — with a built-in visual-QA loop that catches AI-deck
antipatterns before delivery.

Product managers accumulate knowledge in many forms — specs, briefs,
customer feedback, research notes, competitive analyses. This knowledge is
inherently **graph-like**: interconnected, non-linear, multi-dimensional.
But stakeholders need **linear stories** — narratives told in a deliberate
order that captivate, make sense, and drive decisions.

The Product Storytelling Agent bridges that gap, then runs the result
through a render-and-critique pipeline so the deck *looks* as good as it
*reads*.

---

## Table of Contents

- [Quick Start](#quick-start)
- [Example Invocations](#example-invocations)
- [Agents](#agents)
- [Skills](#skills)
- [Architecture](#architecture)
- [7-Phase Workflow](#7-phase-workflow)
- [Approval Gate (Stop-B)](#approval-gate-stop-b)
- [Visual-QA Loop](#visual-qa-loop)
- [Content Placement](#content-placement)
- [File Structure](#file-structure)
- [Requirements](#requirements)
- [Examples Corpus](#examples-corpus)

---

## Quick Start

1. Copy this pack's `.github/` directory and (optionally) `examples/` into
   your target repository root.
2. Add `.story-telling-stm/` to your `.gitignore` — that directory holds
   per-run state and intermediate artifacts; you generally don't want it
   in version control.
3. Start GitHub Copilot CLI in that repository.
4. Invoke the orchestrator:

```text
@story-orchestrator Create a stakeholder buy-in deck from the feature
briefs in docs/briefs/. Goal: get Q3 funding approved.
Audience: VP Engineering + VP Product.
Current belief: platform investment is premature.
Desired belief: deferring is more expensive than investing now.
Desired action: approve the $200K Q3 budget line.
```

> **Optional belief-psychology fields** (recommended; new in v2.1.0).
> Stating `current_belief` / `desired_belief` / `desired_action` up
> front turns the deck into a *persuasion target* the strategist
> and critic can both measure against. Other optional fields:
> `stakes`, `objections`, `proof_required`, `presentation_mode`
> (`live` | `read-ahead` | `board` | `sales` | `investor` |
> `workshop`). See
> [`.story-telling-stm/schemas/intake.schema.json`](./.story-telling-stm/schemas/intake.schema.json).

> **Output mode** (new in v2.2.0). `output_mode` selects the
> deliverable: `pptx` (**default** — native python-pptx deck),
> `marp` (Marp/Marpit markdown rendered + verified via the
> `marp-engine` skill), or `both` (Marp markdown *source-of-record* plus
> a full-fidelity python-pptx deck). Marp output is intentionally
> simpler than native pptx — that trade-off is accepted. Marp / both
> require the **marp-cli toolchain** (Node + `@marp-team/marp-cli`, plus
> LibreOffice for editable pptx); when it is missing the agent
> **blocks gracefully** and asks you to install / ship-unverified /
> abort — it never silently ships unverified slides. Example:
> `@story-orchestrator ... output_mode: both`.

---

## Example Invocations

Pre-built example contexts live under [`examples/`](./examples/) — copy one
into your prompt as a starting point.

```text
@story-orchestrator Turn the spec in docs/platform-spec.md into a technical
review deck. Audience: engineering leads. Goal: get architecture sign-off.
```

```text
@story-orchestrator Create a customer success story from docs/case-study.md
and docs/metrics.md. Audience: sales team.
Goal: new pitch deck for enterprise prospects.
```

```text
@story-orchestrator Build a vision deck from docs/roadmap.md and
docs/strategy.md. Audience: board of directors. Goal: Q4 strategic
alignment. Template: assets/company-template.pptx
```

---

## Agents

| Agent | Role | User-Facing? |
|-------|------|--------------|
| `@story-orchestrator` | Coordinates the 7-phase workflow: intake → research → proposal → feedback → build → qa → complete. Owns the Stop-B approval gate, iteration counters, and STM. | ✅ Yes — invoke this one |
| `@story-strategist` | Reads context, analyzes audience, designs narrative strategy, produces story proposal. Constrained `web` to research-only. | ❌ Subagent |
| `@deck-builder` | Authors slide content, customizes `generate_deck.py`, produces the .pptx, hands off to `@deck-critic` for QA. | ❌ Subagent |
| `@deck-critic` | renders the .pptx to PNGs, runs structural assertions (15 checks), runs multimodal antipattern critique, returns `pass` / `revise` with prioritized top fixes. | ❌ Subagent |

---

## Skills

| Skill | Purpose | Used By |
|-------|---------|---------|
| `narrative-craft` | Storytelling frameworks (SCQA, Hero's Journey, Pyramid), graph-to-linear transformation, audience psychology, headline craft, approval-gate rationale | Orchestrator, Strategist |
| `presentation-design` | Slide types, one-message-per-slide rule, visual hierarchy, sequencing patterns. Canonical home for *positive* design rules. | Orchestrator, Strategist, Builder |
| `slide-design-systems` | Ten concrete design systems (palette + tint ladders + type scale + grid + slide-type defaults): executive-navy, technical-slate, customer-coral, investor-gold, editorial-mono, boardroom-conservative + premium ink-editorial, quiet-luxury, signal-dark, warm-editorial (render-present fonts) | Strategist, Builder |
| `pptx-engine` | python-pptx API reference, template/default mode, slide generation patterns, **native editable charts** (`add_chart`/`XL_CHART_TYPE`) for standard bar/line/pie, reference `generate_deck.py` with 13 builder functions covering 13 slide types | Builder |
| `render-visual` | Code-rendered chart / composite / diagram PNGs (matplotlib + Pillow) embedded via `add_picture`; reserved for non-native chart types (slopegraph, waterfall, sparkline). Bundles a render-safe font fallback via `assets/font_locator.py`. | Builder |
| `marp-engine` | Author Marp/Marpit markdown, render to PNG for QA, convert Marp → PPTX, with a self-probing **verify-or-block** toolchain policy. Theme CSS generated from the design-system tokens (token parity). Loaded only when `output_mode` is `marp` or `both`. | Builder, Critic |
| `slide-critique` | Canonical home for the 10-item AI-antipattern catalog. Defines the verdict logic and JSON-only output format consumed by `@deck-critic`. | Critic |
| `pptx-visual-qa` | Cross-platform render pipeline: `.pptx` → PNG per slide via soffice → pdf → **pypdfium2** → png (poppler `pdftoppm` / `pdf2image` fallback). Emits `manifest.json`. Graceful no-engine fallback. | Critic |
| `pptx-structural-asserts` | 15 structural checks: aspect ratio, overflow, WCAG contrast, alignment-grid 0.05" snap, repeated layout hash, title underline presence, dark/light run, speaker notes coverage, duplicate titles, body word count, **font render-presence (portability)**, **safe-area breathing-room**, + 3 archetype-spec checks | Critic |

---

## Architecture

```text
                       ┌──────────────────────┐
                       │ @story-orchestrator  │  ◀── user-invocable
                       │   (coordinator)      │      (Stop-B gate owner)
                       └──────────┬───────────┘
                                  │ task()
            ┌─────────────────────┼─────────────────────┐
            │                     │                     │
            ▼                     ▼                     ▼
   ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐
   │@story-strategist│  │  @deck-builder  │  │  @deck-critic   │
   │   (subagent)    │  │   (subagent)    │  │   (subagent)    │
   └─────────────────┘  └─────────────────┘  └─────────────────┘
   research + narrative   slide content +     render + structural
   proposal               .pptx generation    + visual antipattern
                                              critique → pass/revise
```

All sub-agents declare `user-invocable: false` and carry a proxy-aware
**Invocation Guard**: they refuse direct user invocation AND refuse calls
from any agent other than `@story-orchestrator`.

---

## 7-Phase Workflow

| Phase | What happens | Owner |
|-------|--------------|-------|
| 1. **intake** | Parse the brief; identify audience, decision, constraints; write `intake.json` | orchestrator |
| 2. **research** | `@story-strategist` ingests context, identifies and fills knowledge gaps (bounded `web` use) | strategist |
| 3. **proposal** | Design narrative + slide-by-slide outline → `proposal.md` | strategist |
| 4. **feedback** | Present proposal to user. **Stop-B**. Loop with `proposal_iteration` (cap 3) | orchestrator |
| 5. **build** | `@deck-builder` writes `deck-spec.json` + customizes `generate_deck.py` + produces `output.pptx` | builder |
| 6. **qa** | `@deck-critic` renders, runs structural + visual checks, returns `pass` / `revise`. Loop with `qa_iteration` (cap 2) | critic |
| 7. **complete** | Orchestrator returns `output.pptx` path + QA summary | orchestrator |

State at every step is persisted to
`.story-telling-stm/runs/<run-id>/state.json` (schema v2.0.0).

---

## Approval Gate (Stop-B)

Between phases 3 (proposal) and 5 (build), the orchestrator stops and
shows the proposal to the user. **No deck is built until the user replies
`APPROVED`** (case-insensitive). Anything else — feedback, "looks good",
silence, 👍 — is treated as not-yet-approved.

Rationale and full mechanics: see
[`narrative-craft/references/approval-gate-rationale.md`](./.github/skills/narrative-craft/references/approval-gate-rationale.md).

---

## Visual-QA Loop

After the deck is built, `@deck-critic` runs a three-stage check:

1. **Render** — `pptx-visual-qa/scripts/render_pptx.py` produces a PNG
   per slide (LibreOffice → pdf, then pypdfium2 → png). If no rendering
   engine is available on the host, it exits 0 with `render_engine: null`
   in the manifest, **but the critic does not silently continue**: per
   [Verify-or-block](#verify-or-block-no-silent-unverified-output) below,
   styled decks block with `render_unverified` and simple-only decks
   surface an explicit user decision.
2. **Structural** — `pptx-structural-asserts/scripts/check_pptx.py`
   runs 15 structural checks against the .pptx file (aspect
   ratio, overflow, contrast + contrast-resolution, dark/light run,
   duplicate titles, repeated layout, title-underline, speaker notes,
   alignment, body-word density, font presence, safe-area, and
   archetype-shape checks — no rendering needed).
3. **Visual** — multimodal critique against the rendered PNGs using
   the AI-antipattern catalog in `slide-critique/SKILL.md`.

Verdict logic: `pass` if all structural checks pass and ≤1 visual
warning; `revise` if any structural fail OR ≥2 visual fails. When no
render engine is available the critic does **not** silently pass —
styled decks return `render_unverified` (BLOCKING, `revise`), while
simple-only decks return `unverified-needs-user`, deferring an
explicit install / ship-with-consent / abort decision to the user
(see [Verify-or-block](#verify-or-block-no-silent-unverified-output)
below). On `revise`, `@deck-builder` retries with the top 5 fixes
(capped at `qa_iteration ≤ 2`).

### Verify-or-block (no silent unverified output)

The pack will **not silently ship a deck whose visual quality it could
not verify**. When no render engine is available:

- A deck with any **styled** slide → `render_unverified` (BLOCKING,
  `revise`).
- A **simple-only** deck → `unverified-needs-user`: the orchestrator
  surfaces an explicit decision — **install** a render engine & retry /
  **ship unverified with explicit consent** / **abort**. (This replaced
  the former silent `pass_unverified`.)

The **same** discipline applies to the Marp toolchain (`marp` / `both`
modes): a missing marp-cli toolchain blocks with `marp_toolchain_unverified`
and surfaces the same install / ship / abort decision.

---

## Content Placement

To avoid drift across artifacts, each topic has exactly one canonical
home:

| Topic | Canonical home |
|-------|----------------|
| Storytelling frameworks (SCQA, Hero's Journey, Pyramid) | `narrative-craft/SKILL.md` |
| Throughline + slide-sorter test | `narrative-craft/SKILL.md` (deterministic check in `slide-critique/SKILL.md`) |
| Per-slide AEI (Assertion–Evidence–Implication) triad | `narrative-craft/SKILL.md` |
| Audience-framework matrix | `narrative-craft/references/audience-framework-matrix.md` |
| Punch test | `narrative-craft/references/punch-test.md` |
| Headline craft | `narrative-craft/references/headline-craft.md` |
| Approval-gate rationale | `narrative-craft/references/approval-gate-rationale.md` |
| Slide-type catalog + positive design rules | `presentation-design/SKILL.md` |
| Per-element copy budgets (title / subtitle / bullets / callout / footnote) | `presentation-design/SKILL.md` |
| Layout archetype library (11 business-consulting forms) | `presentation-design/references/layout-archetypes.md` |
| Image-prompt template + reject-list | `presentation-design/references/image-direction.md` |
| Ten design systems (palette / tint ladders / type / grid tokens) | `slide-design-systems/SKILL.md` |
| `presentation_mode` → design-system selection | `slide-design-systems/SKILL.md` ("Selection by Use Case") |
| Chart-type-by-relationship matrix + native-vs-rendered split | `pptx-engine/references/chart-selection.md` |
| Marp authoring + theme token-parity + verify-or-block | `marp-engine/SKILL.md` + `references/marp-theming.md` |
| Code-rendered chart/diagram PNG recipes | `render-visual/SKILL.md` |
| AI-antipattern catalog (the "what NOT to do" list) | `slide-critique/SKILL.md` |
| Numeric quality score (0–100, prioritization-only) | `slide-critique/SKILL.md` |
| Render pipeline + manifest schema | `pptx-visual-qa/SKILL.md` |
| Structural check inventory | `pptx-structural-asserts/SKILL.md` |
| Builder functions + slide-type code patterns | `pptx-engine/SKILL.md` |
| Workflow + delegation + Stop-B gate | `story-orchestrator.agent.md` |
| Audience-belief intake fields | `.story-telling-stm/schemas/intake.schema.json` (v2.1.0) |
| `output_mode` (pptx / marp / both) intake field | `.story-telling-stm/schemas/intake.schema.json` (v2.2.0) |
| STM schemas (state, intake, deck-spec, qa-report, proposal) | `.story-telling-stm/schemas/` |

If a fact appears in multiple files, the canonical home above wins;
the others should reference it.

---

## File Structure

```text
story-telling-agent/
├── README.md                                   # this file
├── .github/
│   ├── agents/
│   │   ├── story-orchestrator.agent.md
│   │   ├── story-strategist.agent.md
│   │   ├── deck-builder.agent.md
│   │   └── deck-critic.agent.md                # NEW
│   └── skills/
│       ├── narrative-craft/
│       │   ├── SKILL.md
│       │   └── references/
│       │       ├── audience-framework-matrix.md
│       │       ├── punch-test.md
│       │       ├── headline-craft.md           # NEW
│       │       └── approval-gate-rationale.md  # NEW
│       ├── presentation-design/SKILL.md
│       ├── slide-design-systems/               # NEW skill
│       │   ├── SKILL.md
│       │   └── references/
│       │       ├── design-canon.md
│       │       └── systems/{10 system files}.md
│       ├── pptx-engine/
│       │   ├── SKILL.md
│       │   ├── references/{pptx-api-patterns,styled-recipes,chart-selection}.md
│       │   └── scripts/generate_deck.py
│       ├── render-visual/                       # code-rendered charts/diagrams
│       │   ├── SKILL.md
│       │   ├── assets/{font_locator.py, DejaVuSans.LICENSE.md, README.md}
│       │   ├── references/{chart,composite,diagram,recipe-mapping}-recipes.md
│       │   └── scripts/{render_chart,render_composite,render_diagram}.py
│       ├── marp-engine/                         # NEW skill (output_mode marp/both)
│       │   ├── SKILL.md
│       │   ├── references/marp-theming.md
│       │   └── scripts/render_marp.py
│       ├── slide-critique/SKILL.md
│       ├── pptx-visual-qa/
│       │   ├── SKILL.md
│       │   ├── references/{render-pipeline,visual-rubric}.md
│       │   └── scripts/render_pptx.py
│       └── pptx-structural-asserts/
│           ├── SKILL.md
│           └── scripts/{check_pptx,check_archetypes}.py
├── .story-telling-stm/
│   ├── README.md
│   ├── current-session.json
│   ├── schemas/                                # NEW
│   │   ├── state.schema.json
│   │   ├── deck-spec.schema.json
│   │   ├── qa-report.schema.json
│   │   └── proposal.schema.md
│   └── runs/<run-id>/{state.json, agents/...}
└── examples/                                   # NEW
    ├── buy-in/
    ├── customer-story/
    └── technical-review/
```

---

## Requirements

- **Python 3.x** — Required for PowerPoint generation and structural
  asserts. `python-pptx` is auto-installed by the scripts on first run.
- **GitHub Copilot CLI** — uses `.github/agents/` + `.github/skills/`
  conventions.
- **Optional, recommended for visual QA**:
  - **`pip install pypdfium2`** (recommended, PREFERRED pdf→png engine):
    bundles the PDFium binary as a wheel, so **no system Poppler is
    needed**. Pair with LibreOffice (`soffice`) on PATH for the
    pptx→pdf stage.
  - *Fallback only* (if you cannot use pypdfium2): Poppler
    (`pdftoppm`) on PATH, **or** `pip install pdf2image` + Poppler.
  - **Curated design fonts** (required for the design-font == render-font
    guarantee): install **Inter, Source Serif 4, IBM Plex Sans,
    IBM Plex Mono, Fraunces, Space Grotesk, Archivo** from
    [fonts.google.com](https://fonts.google.com) into your OS /
    LibreOffice font directory (`~/.local/share/fonts` on Linux/WSL,
    `~/Library/Fonts` on macOS, `%WINDIR%\Fonts` on Windows), then
    refresh the cache (`fc-cache -f` on Linux). Without them the pack
    does **not** ship silent bad output — LibreOffice substitutes,
    `check_pptx.py` raises `font_not_render_present`, and the critic
    surfaces a **substitution CONCERN** with this install
    recommendation. See
    [`render-pipeline.md` install notes](./.github/skills/pptx-visual-qa/references/render-pipeline.md#cross-platform-install-notes).
  - If no render engine is available the visual-QA stage does **not**
    silently pass: styled decks block (`render_unverified`) and
    simple-only decks surface a `unverified-needs-user` decision
    (install / ship-with-consent / abort).
- **Required only for `output_mode` `marp` / `both`**:
  - **Node.js 18+** and **`@marp-team/marp-cli`**
    (`npm install -g @marp-team/marp-cli`, or available via `npx`).
  - LibreOffice (`soffice`) additionally for *editable* Marp → pptx
    (`--pptx-editable`, experimental); without it, Marp → pptx is
    image-based.
  - When the toolchain is missing the agent **blocks gracefully** with a
    user decision — it never ships unverified Marp output.

---

## Examples Corpus

Three end-to-end fixtures live under [`examples/`](./examples/):

| Example | Audience | Purpose |
|---------|----------|---------|
| [`buy-in/`](./examples/buy-in/) | VP Eng + Director Product | Internal funding ask, SCQA, executive-navy |
| [`customer-story/`](./examples/customer-story/) | Mid-market financial-services prospects | Customer-voice-forward case study, Hero's Journey, customer-coral |
| [`technical-review/`](./examples/technical-review/) | Senior + staff engineers | Architecture review with explicit alternatives + rollback, Pyramid, technical-slate |

Each contains `context.md` (the prompt to paste), `expected-deck-shape.json`
(golden shape used by the eval pack), and a `README.md`.

Two matching eval packs live at
[`evals/packs/story-telling-agent/`](../../evals/packs/story-telling-agent/)
(narrative + build smoke cases) and
[`evals/packs/story-telling-agent-rendering/`](../../evals/packs/story-telling-agent-rendering/)
(render / verify-or-block cases, including `output_mode=marp`,
`output_mode=both`, and the no-render-engine user-decision gate).
