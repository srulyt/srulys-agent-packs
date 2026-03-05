---
name: decision-metrics-financials
description: Practical frameworks for leading with recommendation, option tradeoffs in compact table format, KPI/OKR design, milestone planning, dependencies, and financial/resource decision framing without links. Trigger keywords: tradeoff matrix, KPI baseline target guardrail, milestone plan, resourcing, ROI range, recommendation.
---

# Decision Metrics Financials

Use this skill to make the brief decision-ready with clear options, measurable outcomes, and realistic resource framing.

## Lead with Recommendation

State the recommended option first with a one-sentence rationale. Then present alternatives.

- Do not force the reader to parse all options before learning the recommendation
- The recommendation appears at the top of the options section
- The recommendation rationale must be in language a non-domain-expert can confidently repeat
- Alternatives follow with comparative tradeoffs framed in business terms
- A comparison table summarizes all options against decision criteria

Structure:

1. **Recommendation**: "[Option name] because [one-sentence business-outcome rationale]."
2. **Alternative(s)**: Each with a brief tradeoff statement in business terms.
3. **Comparison table**: All options side-by-side against criteria, including Stakeholder-Friendly Impact.

## Compact Output Format

Use tables for structured data. Narrative paragraphs only where tables cannot capture the nuance.

### Options Comparison Table

| Option | Impact | Cost | Time | Risk | Strategic Fit | Stakeholder-Friendly Impact | Recommendation |
|--------|--------|------|------|------|---------------|----------------------------|----------------|
| [Name] | ... | ... | ... | ... | ... | [Plain-language business outcome a non-expert can repeat] | Recommended / Alternative |

### Metrics Table

| Metric | Baseline | Target | Guardrail | Measurement Method | Cadence |
|--------|----------|--------|-----------|-------------------|---------|
| ... | ... | ... | ... | ... | ... |

### Milestones Table

| Phase | Milestone | Timeline | Dependencies | Owner/DRI |
|-------|-----------|----------|-------------|-----------|
| ... | ... | ... | ... | ... |

### Financial Framing Table

| Cost Driver | Range | Assumptions |
|-------------|-------|-------------|
| ... | ... | ... |

| Value Driver | Range | Assumptions |
|-------------|-------|-------------|
| ... | ... | ... |

## No-Links Policy

- All references use descriptive text (file names, dates, context)
- No file paths, URLs, or markdown links in any output
- Never use `[text](url)` syntax or bare URLs

## Options and Tradeoffs

- Define at least two viable options (including status quo when relevant).
- Use explicit decision criteria (impact, cost, time, risk, reversibility, strategic fit).
- State why the recommended option wins for this decision context.

## Metrics Design (3–7 KPIs/OKRs)

For each metric include:

- Baseline (if known)
- Target
- Guardrail(s)
- Measurement method and cadence

Prefer a small, high-signal metric set.

## Plan, Milestones, Dependencies

- Present phased execution (crawl/walk/run or equivalent).
- Identify key milestones and dependency risks.
- Name owners/DRIs where known; otherwise mark as unknown.

## Financial and Resourcing Framing

- Provide cost drivers (people, time, infrastructure, vendors).
- Provide value drivers (revenue, savings, risk reduction, strategic enablement).
- Use ranges under uncertainty; avoid false precision.
- Declare assumptions behind any estimate.

## Closing Section Readiness Check

A closing section is ready when its type-specific criteria are met:

- **Decision Ask readiness**: Scope and commitment requested are explicit; timing is clear; metrics and risk posture are understandable to leadership.
- **Recommendation readiness**: Recommended direction is clearly stated; rationale is evidence-backed; impact of adoption vs. non-adoption is concrete.
- **Next Steps readiness**: Actions are specific and ordered; owners/DRIs are identified (or flagged as unknown); timeline is stated.
- **Call to Action readiness**: The ask is specific (what, from whom, by when); the reason for the ask is clear; the next step after input is stated.
- **Summary readiness**: Key takeaways are synthesized (not restated); current state is clear; conditions for future action are identified.

## Maturity-Aware Output

Not every brief needs the full strategy model. The orchestrator will specify the brief maturity level. Scope your outputs accordingly:

- **Early-stage briefs**: You should not be invoked. If invoked, return only what minimal framing the evidence supports.
- **Mid-stage briefs**: Focus on options/tradeoffs and risks. Include metrics, milestones, or financials only if the evidence explicitly contains that data.
- **Late-stage briefs**: Full scope — options, metrics, milestones, financials as supported by evidence.

When evidence does not support a particular output section (e.g., no financial data in sources), do not generate it. Instead, include a brief note in a "Gaps" section listing what was not produced and why.
