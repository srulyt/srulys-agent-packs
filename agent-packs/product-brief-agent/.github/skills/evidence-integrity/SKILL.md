---
name: evidence-integrity
description: Methods for evidence quality, decision-relevance filtering, compact table formatting, source traceability without links, contradiction handling, and explicit assumption/open-question labeling. Trigger keywords: evidence quality, source traceability, contradiction resolution, confidence, assumptions, decision-relevance.
---

# Evidence Integrity

Use this skill to keep briefs grounded in verifiable, decision-relevant inputs presented in compact format.

## Decision-Relevance Filter

Only extract and include evidence that directly informs one of:

- The decision ask (what stakeholders must decide)
- Available options and their tradeoffs
- Risks, blockers, or open concerns
- Success metrics or financial impact

Exclude:

- General background context that does not affect the decision
- Industry trends or market context unless directly tied to the ask
- Historical information that is not relevant to the current decision

When in doubt, include the evidence but annotate its relevance.

## Compact Evidence Format

Evidence outputs are reference tables, not narrative documents. Each entry is 1–2 sentences maximum.

### Evidence Log Table Template

| # | Claim | Source | Confidence | Notes |
|---|-------|--------|------------|-------|
| 1 | [Claim text, 1–2 sentences] | [File name, date] | High/Medium/Low | [Assumption/Open Question if applicable] |
| 2 | ... | ... | ... | ... |

### Format Rules

- One row per evidence point
- Claim column: 1–2 sentences maximum
- Source column: file name and date only
- No explanatory paragraphs between entries
- No sub-sections or narrative structure within the evidence log

## No-Links Policy

- Source pointers use descriptive file names and dates (e.g., "admin-roles transcript, February 2026")
- Never use file paths (e.g., not `.context/admin-roles.md`)
- Never use URLs or markdown links
- Never use `[text](url)` syntax or bare URLs in any output

## Valid Evidence Sources

Evidence must originate from user-provided input material only:

- Documents, transcripts, or files the user provided as context
- Links or URLs the user shared
- Data, quotes, or facts contained within those user-provided sources

Agent-generated artifacts are NOT valid evidence sources:

- Files created under the STM directory (`.product-brief-agent-stm/`) during any run
- Intermediate outputs from other agents (evidence logs, decision models, draft briefs)
- Synthesized or inferred content not traceable to user-provided material

A claim not traceable to user-provided source material is an `Assumption` or `Open Question`, never a sourced fact.

## Evidence Standards

- Prefer direct source excerpts, telemetry snippets, customer feedback, and meeting notes.
- Record source pointers for major claims.
- Include at least 3 evidence points when available.
- Distinguish facts from interpretations.

## Labeling Rules

- Supported statement → Fact with source pointer.
- Unsupported but plausible statement → `Assumption`.
- Missing information that blocks confidence → `Open Question`.

Never blur these categories.

## Contradiction Handling

When inputs conflict:

1. Record both claims and source pointers.
2. State impact on the decision.
3. Propose a resolution path (owner/data needed/timeline if known).
4. Reflect unresolved conflict in risks/open questions.

## Confidence Guidance

Use simple confidence labels for key claims:

- **High**: multiple consistent sources
- **Medium**: one strong source or minor conflicts
- **Low**: incomplete or conflicting evidence
