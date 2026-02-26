# Product Brief Agent

Create a decision-grade product brief from mixed inputs (docs, notes, links, transcripts, recording summaries) for internal business decision makers.

## Quick Start

1. Copy this pack's `.github` directory to your target repository root.
2. Start GitHub Copilot CLI.
3. Invoke the orchestrator agent with your context.

```bash
gh copilot
@brief-orchestrator Build a decision-grade product brief from the provided materials.
```

## Agent Invocation

Use `@brief-orchestrator` as the user-facing entry point.

Specialist agents are invoked by the orchestrator:

- `@evidence-analyst` — evidence extraction, contradiction detection, decision-relevance filtering
- `@strategy-modeler` — options/tradeoffs, metrics, milestones, financial framing (leads with recommendation)
- `@brief-composer` — executive-ready narrative drafting with strict quality rules

## What You Get

The orchestrator coordinates specialists to produce:

- A concise single narrative brief (target 3–4 pages, hard ceiling 5 pages)
- Natural, content-descriptive headings (never template headings)
- Canonical section order with enforced section distinctness
- Executive-grade tone with "so what?" test enforcement
- Standalone document (zero links — fully self-contained)
- Clean markdown formatting (lint-compliant)
- Explicit assumptions/open questions for missing evidence
- Evidence traceability for major claims

## Quality Enforcement

This pack implements multiple quality gates:

| Gate | What It Checks | Enforced By |
|------|---------------|------------|
| Heading Naturalness | No framework template headings in output | Orchestrator editing pass |
| Section Distinctness | Title, summary, problem serve distinct purposes | Orchestrator editing pass |
| Brevity Hard Ceiling | Target 1,500–2,000 words; ceiling 2,500 words | Composer target + orchestrator rejection |
| "So What?" Test | Every paragraph contributes to the decision | Orchestrator editing pass |
| Anti-Repetition | No duplicated content across sections | Orchestrator editing pass |
| Standalone Document | Zero links, all info inlined | Composer rules + orchestrator check |
| Markdown Lint | Proper formatting, heading hierarchy, consistent markers | Composer rules + orchestrator check |
| Executive Tone | No filler phrases, no buzzword inflation | Composer skill + orchestrator review |

## Included Agents

| Agent | Role |
|-------|------|
| `brief-orchestrator` | Coordination, delegation, mandatory 8-point editing pass, quality gates, final artifact assembly |
| `evidence-analyst` | Decision-relevant evidence extraction, contradiction surfacing, compact table output |
| `strategy-modeler` | Options/tradeoffs (recommendation-first), metrics, milestones, financial framing |
| `brief-composer` | Executive-ready narrative drafting with agency-over-formatting and anti-bloat rules |

## Included Skills

| Skill | Purpose |
|-------|---------|
| `product-brief-framework` | Section order, section distinctness contract, brevity protocol, standalone policy, lint rules |
| `evidence-integrity` | Decision-relevance filter, compact evidence tables, no-links policy, confidence labeling |
| `decision-metrics-financials` | Lead-with-recommendation, compact tables, KPI/OKR design, financial framing |
| `executive-writing-style` | Decision-maker framing, persuasive structure, "so what?" test, tone rules, good/bad examples |

## Typical Prompt

```text
@brief-orchestrator
Use the files in this repo plus the linked notes to draft a decision-grade product brief.
Audience: internal leadership.
Decision needed: whether to fund and prioritize in the next planning cycle.
```

## Notes

- If required data is missing, the system preserves all sections and marks `Insufficient data`, with explicit `Assumptions` and `Open Questions`.
- The orchestrator performs a mandatory 8-point editing pass on every draft before producing the final artifact.
- Drafts exceeding the hard ceiling are rejected and returned to the composer for condensation.
- The orchestrator is responsible for deterministic output paths and final quality validation.
