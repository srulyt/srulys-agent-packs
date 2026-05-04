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
```

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
| `@deck-critic` | Renders the .pptx to PNGs, runs structural assertions (10 checks), runs multimodal antipattern critique, returns `pass` / `revise` with prioritized top fixes. | ❌ Subagent |

---

## Skills

| Skill | Purpose | Used By |
|-------|---------|---------|
| `narrative-craft` | Storytelling frameworks (SCQA, Hero's Journey, Pyramid), graph-to-linear transformation, audience psychology, headline craft, approval-gate rationale | Orchestrator, Strategist |
| `presentation-design` | Slide types, one-message-per-slide rule, visual hierarchy, sequencing patterns. Canonical home for *positive* design rules. | Orchestrator, Strategist, Builder |
| `slide-design-systems` | Six concrete design systems (palette + type scale + grid + slide-type defaults): executive-navy, technical-slate, customer-coral, investor-gold, editorial-mono, boardroom-conservative | Strategist, Builder |
| `pptx-engine` | python-pptx API reference, template/default mode, slide generation patterns, reference `generate_deck.py` with 13 builder functions covering 13 slide types | Builder |
| `slide-critique` | Canonical home for the 10-item AI-antipattern catalog. Defines the verdict logic and JSON-only output format consumed by `@deck-critic`. | Critic |
| `pptx-visual-qa` | Cross-platform render pipeline: `.pptx` → PNG per slide via soffice + pdftoppm (with `pdf2image` fallback). Emits `manifest.json`. Graceful no-engine fallback. | Critic |
| `pptx-structural-asserts` | 10 structural checks: aspect ratio, overflow, WCAG contrast, alignment-grid 0.05" snap, repeated layout hash, title underline presence, dark/light run, speaker notes coverage, duplicate titles, body word count | Critic |

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
   per slide. If no rendering engine is available on the host, it
   exits 0 with `render_engine: null` in the manifest; the critic
   surfaces `render_skipped: true` as a non-blocking finding and
   continues with structural-only QA.
2. **Structural** — `pptx-structural-asserts/scripts/check_pptx.py`
   runs 10 checks against the .pptx file (no rendering needed).
3. **Visual** — multimodal critique against the rendered PNGs using
   the AI-antipattern catalog in `slide-critique/SKILL.md`.

Verdict logic: `pass` if all structural checks pass and ≤1 visual
warning; `revise` if any structural fail OR ≥2 visual fails; `error`
if the engine itself failed. On `revise`, `@deck-builder` retries
with the top 5 fixes (capped at `qa_iteration ≤ 2`).

---

## Content Placement

To avoid drift across artifacts, each topic has exactly one canonical
home:

| Topic | Canonical home |
|-------|----------------|
| Storytelling frameworks (SCQA, Hero's Journey, Pyramid) | `narrative-craft/SKILL.md` |
| Audience-framework matrix | `narrative-craft/references/audience-framework-matrix.md` |
| Punch test | `narrative-craft/references/punch-test.md` |
| Headline craft | `narrative-craft/references/headline-craft.md` |
| Approval-gate rationale | `narrative-craft/references/approval-gate-rationale.md` |
| Slide-type catalog + positive design rules | `presentation-design/SKILL.md` |
| Six design systems (palette / type / grid tokens) | `slide-design-systems/SKILL.md` |
| AI-antipattern catalog (the "what NOT to do" list) | `slide-critique/SKILL.md` |
| Render pipeline + manifest schema | `pptx-visual-qa/SKILL.md` |
| Structural check inventory | `pptx-structural-asserts/SKILL.md` |
| Builder functions + slide-type code patterns | `pptx-engine/SKILL.md` |
| Workflow + delegation + Stop-B gate | `story-orchestrator.agent.md` |
| STM schemas (state, deck-spec, qa-report, proposal) | `.story-telling-stm/schemas/` |

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
│       │       └── systems/{6 system files}.md
│       ├── pptx-engine/
│       │   ├── SKILL.md
│       │   ├── references/pptx-api-patterns.md
│       │   └── scripts/generate_deck.py
│       ├── slide-critique/SKILL.md
│       ├── pptx-visual-qa/                     # NEW skill
│       │   ├── SKILL.md
│       │   ├── references/{render-pipeline,visual-rubric}.md
│       │   └── scripts/render_pptx.py
│       └── pptx-structural-asserts/            # NEW skill
│           ├── SKILL.md
│           └── scripts/check_pptx.py
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
  - LibreOffice (`soffice`) + Poppler (`pdftoppm`) on PATH, **or**
  - `pip install pdf2image` + Poppler.
  - If neither is available the visual-QA stage gracefully degrades to
    structural-only with `render_skipped: true`.

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

A matching eval pack lives at
[`evals/packs/story-telling-agent/`](../../evals/packs/story-telling-agent/)
with five smoke cases.
