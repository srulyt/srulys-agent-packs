# Writing Style

Write concise, credible, decision-grade prose for leaders who have little time.

## Decision-Maker Framing

Your reader has **5 minutes** and **12 other documents** to read today. Every sentence must earn its place.

- If a paragraph does not change the reader's understanding or decision, delete it.
- The reader wants to know what this is, why now, what it costs, what it returns, and what you need from them.
- Write as if the reader will stop the moment you waste their time.

## Persuasive Structure

- **Lead with impact.** Open each section with its single most important point. Evidence follows the lead. Never open with background.
- **State the purpose early and reinforce it late.** Within 30 seconds the reader should know what the brief asks of them, or what it informs them about. The closing reinforces that purpose with specifics.
- **Structure each section as lead → evidence → implication.** Give the key point, then 1–3 supporting sentences, then what it means for the decision if that is not obvious. Never bury the lead.

## The "So What?" Test

After writing each paragraph, ask: **"If I deleted this, would *this reader's* decision or understanding change?"**

- **Yes:** keep it.
- **No:** delete it, or merge its one useful sentence into a neighboring paragraph.
- **Maybe:** tighten it to the one decision-relevant sentence.

Apply the test to every paragraph, scoped to the assessed audience. For a non-expert reader, term definitions and orienting background pass the test.

## The Championing Test

Next, ask: **"Could my reader use this to convince their boss in 30 seconds?"**

- **No:** reframe the lead sentence around a business outcome (cost, revenue, risk, customer impact) and push the technical detail into supporting sentences.
- **Partly:** pull the core business outcome out as one memorable statement and keep the technical depth as backup.

These examples describe the same work. Only the second gives the reader a sentence they can say aloud:

> Fails: "The modular RBAC architecture decouples permission assignment from hard-coded role checks, enabling composable admin roles across tenant, capacity, and domain scopes."
>
> Passes: "This lets customers define exactly what each admin type can do — eliminating 200 escalation tickets per month and unblocking enterprise deals that require granular permissions."

## Readability

The reader should never have to re-read a sentence.

- **Sentences:** aim for 15–20 words, with a hard ceiling of 25. Give each sentence one idea; when "and" joins two separate thoughts, split them. Use subject-verb-object order. Default to active voice, and use passive only when the actor is unknown or irrelevant.
- **Paragraphs:** one point per paragraph, 3–4 sentences at most. The lead sentence carries the point.
- **Words:** use the simplest accurate word ("use," not "utilize"; "start," not "initiate"; "help," not "facilitate"; "enough," not "sufficient"; "buy," not "procure"). Replace abstractions with specifics. Cut nominalizations ("we decided," not "a decision was made").
- **Scannability:** a reader who reads only the headings and each paragraph's first sentence should get the whole argument. Use bullets for three or more parallel items, and tables for comparisons.

## Tone

- **Confident and direct.** Write "This will reduce admin errors by 40%," not "This could potentially help reduce admin errors." Make claims like this only when the number is sourced.
- **Honest about uncertainty.** Give the range and the reason, for example: "We estimate 30–50% reduction based on the admin-roles review; the range reflects limited pilot data."
- **No hedging without a stated reason.** Cut "might," "could potentially," "it is possible that," "may help," "should be able to," and "we believe" unless the uncertainty is real and explained. If it is real, say so plainly: "We lack data on X; our estimate assumes Y."
- **State each limitation once.** Put an evidence gap or caveat where it matters, or in Open Questions, and do not restate it in other sections. Thin evidence calls for a short brief, not repeated disclaimers. Do not describe the brief's own status or purpose ("this is an exploratory concept with no decision requested"). The closing type already says that.
- **Write about the business, not the source files.** State the fact ("Option B's license is $420K in year one"), not the document ("The options source includes…"). Name a source only when provenance changes the reader's trust, and then by its business name ("the Q1 ops ticket export").
- **Lower the reader's risk.** Lead with outcomes the reader is measured on. Make "yes" feel safer than "no." Do not require the reader to become a domain expert to defend the proposal.

The combination of confidence and honest bounds is the hallmark of credible executive writing.

## Filler Phrases

Delete these on sight:

- "It is important to note that..."
- "It should be mentioned that..."
- "In today's rapidly evolving landscape..."
- "As we all know..."
- "It goes without saying..."
- "At the end of the day..."
- "Moving forward..."
- "In order to..."
- "The fact of the matter is..."
- "Needless to say..."
- "For all intents and purposes..."

If the sentence still makes sense without the phrase, the phrase was filler.

## Buzzword Inflation

| Inflated | Plain |
|---|---|
| "accelerated digital transformation enablement" | "faster" |
| "synergistic cross-functional alignment" | "teams working together" |
| "leverage our core competencies" | "use what we are good at" |
| "paradigm shift in operational excellence" | "a better process" |
| "holistic end-to-end solution" | "a complete solution" |

## AI-ism Cleanup

The goal is not to hide that AI helped draft the text. It is to make the text read the way a sharp human author would write it. AI-isms are the edit reviewers make by hand most often, so catch them before the draft ships.

1. **Inflated transitions:** "moreover," "furthermore," "additionally," "notably," "importantly," "crucially," "fundamentally," "ultimately," "essentially," "indeed." Usually just delete them.
2. **"X isn't just Y, it's Z":** the most recognizable tell. Rewrite it as a direct claim.
3. **Rule-of-three padding:** keep only the words that are true and load-bearing ("robust, scalable, and future-proof").
4. **Hedged significance claims:** "plays a key role in," "serves as a critical component," "is a powerful tool for," "stands as a testament to," "underscores the importance of." Replace each with the concrete thing it does.
5. **Empty engagement scaffolding:** "It's worth noting that," "As we navigate," "In an era of," "When it comes to," "At its core." Keep the payload and drop the wrapper.
6. **Symmetrical wrap-up sentences:** for example, "By combining X with Y, the team can achieve Z while ensuring W." Cut them.
7. **Over-signposting:** "Let's explore," "In this section we will," "Having established X, we now turn to Y." Remove the tour-guide voice.
8. **Promotional intensifiers:** "seamless," "robust," "cutting-edge," "game-changing," "best-in-class," "unlock," "empower," "elevate," "harness," "leverage" (as a verb), "supercharge." Use a literal verb or claim instead.

### 9. Writer Scaffolding and Metadiscourse (Recognize the Class)

Most AI-isms share one tell: the sentence serves the **writer's narration** rather than the **reader's need**. It narrates the writing, captions what a passage is about, or editorializes on why something matters. Williams calls this *metadiscourse*. Recognize the category, not a phrase list. When a reviewer just says "remove the AI-isms," strip new variants of the class too.

Ask four questions of each sentence:

1. **Reader value or writer narration?** If it talks *about* the writing, cut it and keep the payload.
2. **A content label or announcement?** If it captions a point the next sentence already makes, delete the label.
3. **Significance or design meta-commentary?** If it asserts *that* something matters, matters a lot, or was deliberate, replace it with the concrete consequence.
4. **Is the contrast only for emphasis?** Keep "X, not Y" only when the reader needs the rejected alternative to understand the claim. Cut it when the positive statement stands alone.

These examples are illustrative, not a list to grep for: "What the customer gets:", "The publish step is deliberately simple.", "and that is the point", "This matters because…", "the value of this is…", "the benefit is…", "to be clear", reflexive "explicitly / notably / clearly", "a different posture from…", and a bare "X, not Y" used only for emphasis.

These rules rest on established plain-language authority: Strunk & White ("Omit needless words"; "Put statements in positive form"), Orwell ("If it is possible to cut a word out, always cut it out"), the U.S. Federal Plain Language Guidelines (write for the reader and do not announce what you are about to say), and Williams, *Style: Lessons in Clarity and Grace* (cut metadiscourse).

### Naturalness Test

Read each sentence aloud and ask: "Would a busy human expert actually write this, or does it sound like it's performing thoughtfulness?" A human author writing fast and well produces asymmetric, specific, occasionally blunt sentences, not balanced, hedged, adjective-padded ones.

> AI-ism-laden: "It's important to note that this isn't just an incremental improvement — it's a fundamental shift. By leveraging a robust, scalable, and seamless architecture, the team can unlock powerful new capabilities while ensuring long-term maintainability."
>
> Cleaned: "This replaces the architecture, not patches it. The new design removes the per-item permission checks that block enterprise rollout, and it reuses the existing OneLake identity model — so there is no new permission primitive to maintain."

## Good vs Bad

> Bad (template fill-in tone): "The Problem Statement section describes the challenges faced by administrators in the current environment. It is important to note that the existing role-based access control system presents several significant pain points that impact operational efficiency and user satisfaction."
>
> Good (executive memo tone): "Administrators today have two choices: grant full access or grant none. This forces 340 active admins to either over-provision permissions — creating audit failures — or under-provision them, generating 200+ escalation tickets per month."

> Bad (hedging without a reason): "This solution could potentially help address some of the challenges that administrators might face when managing permissions in the system."
>
> Good (confident, with honest bounds): "This solution eliminates the binary permission model. Based on the February 2026 admin-roles review, we project a 60–80% reduction in escalation tickets within 90 days of rollout."

The numbers in these examples are illustrative. In a real brief, use numbers only from the source.

## Anti-Repetition

- **Title, summary, and problem are three different things.** The title names the product. The summary arcs the whole story in 3–5 sentences. The problem section digs into the pain with evidence. Each goes one level deeper than the last.
- If you wrote something in one section, do not write it again in another. A one-sentence back-reference is fine. Restating the same content in different words is not.
- No "in conclusion" or "to summarize" paragraphs within the body.

## Right Length

A brief should be as short as possible, but no shorter. Clarity outranks brevity. The figures below are typical ranges that prompt a review, not caps.

- **Expert audience:** usually 1,500–2,500 words (about 3–5 pages). Past roughly 2,500 words, review for filler and repetition; do not auto-cut.
- **Non-expert audience:** up to about 4,500 words. Extra length is fine when it goes to definitions, orientation, rationale, or clarifying scenarios. It is never fine when it goes to filler.
- **Early-stage or thin-source briefs** may be much shorter. Never pad to hit a number.

When a brief runs long, first remove filler, repetition, and non-load-bearing content. If every remaining passage is load-bearing for this audience, keep it; earned length is not a defect. **Never merge two distinct concepts to save words.** If a passage is too dense, split it and add explanation.

Anti-bloat rules apply at every audience level:

- No paragraphs that introduce the next section, and no bridging paragraphs between sections.
- No restating earlier sections, and no internal "in conclusion" paragraphs.
- Collapse sentences only when they make the **same** point.
- Prefer tables and lists for structured data.
- No background that does not inform the decision for this audience.
