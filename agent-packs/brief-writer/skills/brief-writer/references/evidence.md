# Evidence

Keep the brief grounded in verifiable, decision-relevant input.

## Valid Sources

Only material the user provided counts as evidence:

- documents, transcripts, and files
- links the user shared
- facts, data, and quotes inside those sources
- external research the user approved (see External Knowledge)

Your own drafts, notes, and intermediate outputs are never sources. Synthesized or inferred content is an `Assumption` or an `Open Question`, never a sourced fact.

## Decision Relevance

Include evidence that informs at least one of these:

- the closing purpose
- the options and their tradeoffs
- risks or blockers
- metrics or financial impact

Exclude general background, trends, or history that does not affect the decision. The exception is orienting context that a non-expert reader needs. When in doubt, include the evidence and make its relevance clear.

## Labels

- **Fact:** supported by a source.
- **Assumption:** plausible but unsupported.
- **Open Question:** missing information that blocks confidence.

Never blur these categories. Distinguish facts from interpretations.

## Decision Status

Tag material design and strategy claims by their status in the source:

- **Settled:** the source presents the choice as decided or owned. State it declaratively, without defending or hedging it.
- **Proposed:** a direction the source advocates but has not ratified. Argue for it.
- **Open:** genuinely undecided. Surface it as an open question.

Never downgrade a Settled claim; that creates phantom uncertainty. Never upgrade a Proposed or Open claim to Settled; that overclaims. When the source says a choice is final or owned, treat it as Settled no matter how much supporting evidence it gives.

## Unverified Quantities

State a specific number, count, or magnitude as fact only when a user-provided source or an approved, labeled research finding supports it. Otherwise:

- use qualitative phrasing, such as "many" or "a small number of early customers", or
- present the number explicitly as an estimate and give its basis.

Never manufacture precision for rhetorical weight.

## Contradictions

When inputs conflict:

1. State both claims and where each comes from.
2. State the impact on the decision.
3. Propose a way to resolve it: an owner, the data needed, and a timeline if known.
4. Reflect any unresolved conflict in the risks or open questions.

Compare approved external research against source claims, especially claims about an outside product's status, competitive position, or platform direction. If research contradicts the source, surface the contradiction. Never silently adopt either side. Offer a reframe, for example "convergence" rather than an unverified "retirement," and say which side is better evidenced.

## External Knowledge

All content must trace to the user's sources. When those sources fall short, fill gaps in this order:

1. The context the user already provided.
2. Asking the user for more.
3. Your own internal knowledge, but only with the user's confirmation.
4. Web search, MCP tools, or other research, but only with the user's confirmation.

Steps 3 and 4 have three rules:

- **Ask first.** List the gaps and the sections they affect, and propose the source type. Never add external knowledge without explicit approval.
- **Say up front when an expected tool is unavailable.** Do not quietly substitute a guess.
- **Label external additions** when you report back to the user.

## Confidence

- **High:** multiple consistent sources.
- **Medium:** one strong source, or minor conflicts.
- **Low:** incomplete or conflicting evidence.

## Evidence Log

Include an evidence log only when the user explicitly asks for one. It is a reference table with no narrative, one row per claim, and each claim limited to 1–2 sentences. Give sources as a file name and date or another descriptive reference, never a path, URL, or link.

| # | Claim | Source | Confidence | Status | Notes |
|---|---|---|---|---|---|
| 1 | Claim, 1–2 sentences | File name, date | High / Medium / Low | Settled / Proposed / Open / n.a. | Assumption or open question, if any |
