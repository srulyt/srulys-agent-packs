---
name: evidence-integrity
description: "Methods for evidence quality, decision-relevance filtering, compact table formatting, source traceability without links, contradiction handling, and explicit assumption/open-question labeling. Trigger keywords: evidence quality, source traceability, contradiction resolution, confidence, assumptions, decision-relevance."
---

# Evidence Integrity

Use this skill to keep briefs grounded in verifiable, decision-relevant inputs presented in compact format.

## Decision-Relevance Filter

Only extract and include evidence that directly informs one of:

- The closing section purpose (what the brief asks of readers — a decision, recommendation, action, input request, or informational synthesis)
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

| # | Claim | Source | Confidence | Status | Notes |
|---|-------|--------|------------|--------|-------|
| 1 | [Claim text, 1–2 sentences] | [File name, date] | High/Medium/Low | Settled/Proposed/Open/n.a. | [Assumption/Open Question if applicable] |
| 2 | ... | ... | ... | ... | ... |

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

Agent-generated artifacts are NOT valid evidence sources and must NEVER appear in any evidence log or source reference:

- Files created under the STM directory (`.product-brief-agent-stm/`) during any run — these are internal working artifacts, not evidence
- Intermediate outputs from other agents (evidence logs, decision models, draft briefs, contradictions, assumptions)
- Synthesized or inferred content not traceable to user-provided material
- Any file path containing `.product-brief-agent-stm/` is an absolute disqualifier as a source reference

A claim not traceable to user-provided source material is an `Assumption` or `Open Question`, never a sourced fact.

**Critical**: If an evidence log entry cites any `.product-brief-agent-stm/` path or agent-generated artifact, it is invalid and must be rewritten to either trace the claim to the original user-provided source or be relabeled as an Assumption.

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

## Authorship and Decision Status

A brief reads wrong when it defends a settled decision as if it were an open hypothesis, or misattributes who owns the proposal. Capture two extra signals during extraction so downstream framing is correct.

### Authorship / ownership

- Identify **who authored the source material and who owns the proposed initiative** (the producing team, the decision-maker, the requesting stakeholder), when the source reveals it.
- Distinguish the producing team from partner/consumer teams. Do not assume the author is an external party — the source is frequently written by the owning team itself.
- Record ownership in the evidence output so the composer frames the brief from the correct vantage point.

### Decision status per claim

Tag each material design/strategy claim with its decision status:

- **Settled** — the source presents this as a decided, owned choice (architecture chosen, disposition decided, team committed). The brief states it declaratively; it is not "defended" or hedged.
- **Proposed** — an advocated direction not yet ratified. The brief argues for it.
- **Open** — genuinely undecided; surfaces as an Open Question.

Never downgrade a Settled claim to Proposed framing (creates phantom uncertainty), and never upgrade a Proposed/Open claim to Settled (overclaims). When the source explicitly states a choice is final or owned, that is Settled regardless of how much supporting evidence is present.

## Contradiction Handling

When inputs conflict:

1. Record both claims and source pointers.
2. State impact on the decision.
3. Propose a resolution path (owner/data needed/timeline if known).
4. Reflect unresolved conflict in risks/open questions.

### Source vs. external-knowledge contradictions (mandatory check)

When the orchestrator supplies external/research findings (web, MCP-server, or internal-tool results) alongside user source material, explicitly compare them. This is the highest-value contradiction class — especially claims about **external product status, competitive positioning, or platform direction** (e.g., whether a named product is being retired, expanding, or superseded).

- If a research finding contradicts a transcript/source claim, you MUST record it as an explicit contradiction entry — never silently adopt either side.
- Propose a reframe that the composer can apply (e.g., reframe the premise as "convergence" or "supersession" rather than asserting the unverified version).
- Flag the contradiction's confidence and which side is better evidenced.

Silently inheriting a factually shaky source claim about the outside world is a defect; the reviewer will catch it and force a rewrite.

## Unverified Quantities

Specific numbers, counts, and magnitudes that are not traceable to a labeled source get walked back during review. Default to qualitative phrasing unless the quantity is evidence-backed.

- A precise count ("more than one hundred surfaces," "10 enterprise customers") is only stated as fact when a user-provided source or a labeled research finding supports it.
- Otherwise, use qualitative phrasing ("many," "a small number of early customers") OR present the number explicitly as an assumption/estimate with its basis.
- Never manufacture precision for rhetorical weight. The orchestrator's editing pass flags unsourced specifics.

## Confidence Guidance

Use simple confidence labels for key claims:

- **High**: multiple consistent sources
- **Medium**: one strong source or minor conflicts
- **Low**: incomplete or conflicting evidence
