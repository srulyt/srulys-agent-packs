# Writing quality

## Voice

- **Register:** professional-technical, written for implementers. Be substantive, confident, and specific. Never procedural ("This section will describe…").
- **Lead with the point:** each section opens with its key claim and evidence follows. Apply the "so what?" test: if deleting a paragraph leaves an implementer's understanding unchanged, delete it.
- **Decisions, not options:** "The service publishes via the queue", not "could potentially". When genuinely uncertain, state the range **and** the reason; otherwise drop the hedge ("might", "we believe", "should be able to").
- **Sentences:** 15–20 words, hard ceiling 25. One idea per sentence and one point per paragraph (≤ 3–4 sentences). Use subject-verb-object order and active voice.
- **Plain words:** use, start, help, enough, build, not utilize, initiate, facilitate, sufficient, construct.
- **Specifics over abstractions:** "reduces p95 from 800 ms to 200 ms", not "improves performance".
- **Clarity:** name entities instead of using "it"/"they" at the start of a paragraph. Define jargon on first use or add it to the Glossary.
- **Strike filler:** "It is important to note that", "In order to" (→ "To"), "Moving forward", "Needless to say".
- **Strike buzzwords:** leverage, robust, scalable, seamless, best-in-class, holistic, end-to-end. Replace each with the actual target, mechanism, or boundary.
- **No fabricated vividness:** never invent quotes, data, personas, jobs, journey steps, or roles. Leave the cell blank, or mark it `[TBD]` with an OQ.
- **Formatting:**
  - Use real headers (`#`–`####`), not bold lines as pseudo-headers.
  - Don't hard-wrap body prose.
  - Each FR is ≤ 2 sentences: the shall-statement plus at most one clarifier.

### Good vs bad

- **Problem Statement:**
  - Bad: "The Problem Statement section will describe the challenges faced by users…"
  - Good: "Notifications land in one inbox with no priority signal. 47% of users miss high-severity alerts within 4 hours (Q4 telemetry, n=18,400)."
- **Solution Summary:**
  - Bad: "A robust, scalable solution leveraging modern patterns for a seamless experience."
  - Good: "Add a per-notification severity field (P0–P3) and a severity-aware inbox; P0/P1 surface in a top row. No publish-API changes."

## Upper-section signal density

The upper sections are Problem Statement, Goals, Users & Personas, Stakeholders, and Solution Summary. They orient the reader; they do not carry the contract. After reading them, a reader should know what is being solved, for whom, the chosen approach at the highest level, and what gates the rest of the spec. Nothing more.

- **Problem Statement:** the current pain, who feels it, evidence, and why now. No solution vocabulary. **Goals:** outcomes, not shipped features ("Reduce time-to-first-action from N to M min for >70% of users", not "Ship a notifications panel"). **Users:** identity, context, job, and expected outcome. **Solution Summary:** the chosen approach and the decisions that gate lower sections.
- **Move content to its canonical lower home:**
  - per-feature reasoning → FR *Rationale*
  - edge cases → FRs/ACs
  - uncertainty → Open Questions
  - trade-offs → Risks & Mitigations
  - implementation detail → Technical Considerations or the technical sections
- **Keep only gating context:** context earns its place in the upper sections only if it gates a downstream decision, such as `spec_kind`, a gating axis, a scope boundary, or persona-driven behaviour.
- **Backstop caps:**
  - Problem Statement ≤ 400 words
  - Solution Summary ≤ 350 words and ≤ 3 paragraphs
  - Goals narrative ≤ 200 words
  - Users narrative ≤ 150 words

  Good specs land well below these caps; hitting one is a smell.
- **Framing:** write the Problem Statement so an outsider could explain the customer's pain in one paragraph (working-backwards framing).

## Open Questions and Out of Scope

- **Open Questions:** every undecided matter becomes an `OQ-NN` with an owner and a due date. Never silently pick an option the inputs don't constrain. Promote every "we'll figure that out later" to an OQ.
- **Out of Scope:** include an item only when one of these holds:
  1. Surrounding spec language would lead a reader to assume the item is in scope.
  2. A stakeholder or prior document conflated it with this work.
  3. The user named it as a non-goal.

  Otherwise leave it out. An empty list beats fabricated negations like "implementation details are out of scope". Apply the same test to "not supported" or "no additional work required" phrasing anywhere in the spec.

## Evidence and citations

- **When to cite:** rarely. Cite only when all of these hold:
  - The evidence is critical context the body cannot carry.
  - The source is authoritative and durable: public docs, a standard or RFC, a versioned spec, a work item, a stable SharePoint/wiki URL, or a vendor/regulator reference.
  - The source is primary, not something that merely mentions it.
  - The reader is likely to need to open it.
- **Format:** Markdown footnotes (`[^name]`) with the real URL. Never use a numbered "Citations" appendix or `S1, S2` schemes. Internal cross-references use anchored links.
- **Never cite:** local, scratch, session, or `.gitignore`-matched paths. Instead, inline the fact and attribute it to its real upstream source, or mark it `[TBD — needs primary source URL]` with an OQ, or drop it.
- **Default:** most specs have no footnotes and no References section.

## User context patterns

- **JTBD:** "When <situation>, I want to <motivation>, so I can <outcome>". Keep it solution-agnostic; a JTBD is not a user story.
- **Job opportunity:** Importance + max(Importance − Satisfaction, 0), on a 1–10 scale. Scores above ~10 indicate underserved jobs. Include only with real importance/satisfaction evidence.
- **Journeys:** each journey keeps to about one printed page; micro-tasks cover 2–3 phases. Each step maps to an event-driven FR. Each "what can go wrong" maps to an unwanted-behaviour FR.
- **Roles:**
  - Default to deny-by-default, least privilege, and server-side enforcement; hiding something in the UI is cosmetic only.
  - Use RBAC by default; add ABAC/ReBAC only for attribute or relationship rules.
  - Express role-conditioned behaviour as `Where <role>…` FRs and pin deny paths in ACs.
- **Persona grounding:** mark any persona that lacks evidence as a proto-assumption rather than presenting it as validated.
