# Product Storytelling Agent

Transform graph-like product knowledge into compelling, audience-specific PowerPoint decks.

Product managers accumulate knowledge in many forms — specifications, feature briefs, customer feedback, research notes, competitive analyses. This knowledge is inherently **graph-like**: interconnected, non-linear, and multi-dimensional. But stakeholders need **linear stories** — clear narratives told in a deliberate order that captivate, make sense, and drive decisions.

The Product Storytelling Agent bridges that gap.

## What It Does

1. **Ingests** your product context (markdown files — specs, briefs, feedback, research)
2. **Analyzes** the content and identifies the strongest narrative thread for your target audience
3. **Proposes** a story strategy with a slide-by-slide deck outline for your approval
4. **Builds** a professionally designed PowerPoint deck (.pptx) with speaker notes

## Quick Start

1. Copy this pack's `.github/` directory into your target repository root.
2. Start GitHub Copilot CLI.
3. Invoke the orchestrator:

```
@story-orchestrator Create a stakeholder buy-in deck from the feature briefs
in docs/briefs/. Goal: get Q3 funding approved. Audience: VP Engineering + VP Product.
```

## Example Invocations

```
@story-orchestrator Turn the spec in docs/platform-spec.md into a technical review deck.
Audience: engineering leads. Goal: get architecture sign-off.
```

```
@story-orchestrator Create a customer success story from docs/case-study.md
and docs/metrics.md. Audience: sales team. Goal: new pitch deck for enterprise prospects.
```

```
@story-orchestrator Build a vision deck from docs/roadmap.md and docs/strategy.md.
Audience: board of directors. Goal: Q4 strategic alignment.
Template: assets/company-template.pptx
```

## Agents

| Agent | Role | User-Facing? |
|-------|------|-------------|
| `@story-orchestrator` | Coordinates the full 5-phase workflow: intake, delegation, approval gate, delivery | ✅ Yes — invoke this one |
| `@story-strategist` | Reads context, analyzes audience, designs narrative strategy, produces story proposal | ❌ Subagent |
| `@deck-builder` | Authors slide content, generates python-pptx script, produces the .pptx file | ❌ Subagent |

## Skills

| Skill | Purpose | Used By |
|-------|---------|---------|
| `narrative-craft` | Storytelling frameworks (SCR, Hero's Journey, etc.), graph-to-linear transformation, audience psychology, narrative arc design | Orchestrator, Strategist |
| `presentation-design` | Slide types, one-message-per-slide rule, visual hierarchy, sequencing patterns, design quality checklist | Orchestrator, Strategist, Builder |
| `pptx-engine` | python-pptx API reference, template/default mode, slide generation patterns, reference script | Builder |

## Architecture

```
                    ┌─────────────────────┐
                    │  story-orchestrator  │  ◀── User-facing
                    │  (orchestrator)      │
                    └──────────┬──────────┘
                               │
               ┌───────────────┼───────────────┐
               │                               │
               ▼                               ▼
    ┌─────────────────────┐         ┌─────────────────────┐
    │   story-strategist  │         │    deck-builder      │
    │   (subagent)        │         │    (subagent)        │
    └─────────────────────┘         └─────────────────────┘
    Research + Narrative Design      PowerPoint Generation
```

### 5-Phase Workflow

1. **Intake** — Parse context files, goal, audience. Validate inputs.
2. **Research** — Ingest context, identify and fill knowledge gaps.
3. **Proposal** — Design narrative strategy, produce slide-by-slide deck outline.
4. **Feedback** — Present proposal for user approval. ⛔ Must not build without approval.
5. **Build** — Generate the PowerPoint deck using python-pptx.

### Approval Gate

The orchestrator enforces a mandatory approval gate between proposal and build. You must explicitly approve, request revisions (up to 3 cycles), or choose from alternative narrative options before any deck is generated.

## Requirements

- **Python 3.x** — Required for PowerPoint generation. The deck-builder will attempt to auto-install `python-pptx` if not present.
- **GitHub Copilot CLI** — This pack uses `.github/agents/` and `.github/skills/` conventions.

## File Structure

```
story-telling-agent/
├── .github/
│   ├── agents/
│   │   ├── story-orchestrator.agent.md
│   │   ├── story-strategist.agent.md
│   │   └── deck-builder.agent.md
│   └── skills/
│       ├── narrative-craft/
│       │   ├── SKILL.md
│       │   └── references/
│       │       ├── storytelling-frameworks.md
│       │       └── audience-psychology.md
│       ├── presentation-design/
│       │   ├── SKILL.md
│       │   └── references/
│       │       └── slide-patterns.md
│       └── pptx-engine/
│           ├── SKILL.md
│           ├── references/
│           │   └── pptx-api-patterns.md
│           └── scripts/
│               └── generate_deck.py
├── .story-telling-stm/        # Session state (gitignored)
│   └── README.md
├── README.md
└── .gitignore
```

## Template Support

You can provide a .pptx file as a design template. The deck-builder will inherit the template's fonts, colors, backgrounds, and logos. Pass the template path in your invocation:

```
@story-orchestrator ... Template: path/to/template.pptx
```

If no template is provided, a professional default design is applied (Calibri fonts, steel blue accent, 16:9 widescreen).
