---
name: narrative-craft
description: "Storytelling expertise for transforming graph-like product knowledge into compelling linear narratives. Covers storytelling frameworks (SCR, Hero's Journey, Problem-Solution), audience-framework selection, narrative arc design, and the So What test. Keywords: storytelling, narrative, story arc, framework, audience, SCR, hero journey, graph-to-linear."
---

# Narrative Craft

Expert knowledge for transforming interconnected product knowledge into compelling, audience-specific linear narratives. This is the core intellectual skill of the Product Storytelling Agent.

## When to Use This Skill

Load this skill when:
- Designing a narrative strategy for a presentation
- Choosing a storytelling framework for a specific goal + audience combination
- Transforming graph-like knowledge (specs, briefs, research) into a linear story
- Analyzing what an audience cares about and how they make decisions
- Structuring the emotional and rational arc of a presentation

## The Central Challenge: Graph → Linear Transformation

Product knowledge is inherently **graph-like**: entities connect to each other in multiple ways, information is non-linear, and any single fact relates to many others. But humans absorb stories **linearly** — one idea after another, in a deliberate order that builds understanding and conviction.

The storyteller's job is to find the **strongest path** through the knowledge graph for a given audience and goal. This is not summarization — it's curation and sequencing.

### Three Linearization Strategies

**1. Dependency Ordering**
Start with what the audience must understand first, then layer dependent concepts. Use when the content has prerequisite knowledge.
- Best for: Technical reviews, architecture decisions, complex product explanations
- Pattern: Foundation → Building blocks → Emergent capability → Implication

**2. Audience-Priority Ordering**
Start with what the audience cares about most, then provide supporting context. Use when the audience's attention is limited.
- Best for: Executive briefings, funding asks, status updates
- Pattern: Bottom line → Evidence → Context → Next steps

**3. Tension-Resolution Ordering**
Start by creating a problem or question, build tension, then resolve it. Use when you need emotional engagement.
- Best for: Customer stories, vision pitches, change management
- Pattern: Hook → Context → Tension → Evidence → Resolution → Action

## Storytelling Frameworks Quick Reference

### SCR: Situation–Complication–Resolution
**Best for**: Decision asks, funding requests, prioritization discussions

| Beat | Purpose | Example |
|------|---------|---------|
| Situation | Establish shared reality | "We've grown 3x in 12 months" |
| Complication | Introduce the tension | "But our infrastructure can't scale past 10K concurrent users" |
| Resolution | Present the path forward | "A $200K platform investment enables 100K users by Q4" |

**Slide mapping**: 2–3 situation slides → 2–3 complication slides → 3–4 resolution slides → 1 CTA

### SCQA: Situation–Complication–Question–Answer
**Best for**: Analytical presentations, risk assessments, strategic options

Extends SCR by explicitly framing the question the audience should be asking. The Question beat focuses attention before the Answer provides resolution.

### Hero's Journey (Customer as Protagonist)
**Best for**: Customer empathy stories, product vision, market positioning

| Beat | Purpose |
|------|---------|
| Ordinary World | Customer's current reality and frustrations |
| Call to Adventure | The trigger that demands change |
| Trials | Challenges faced during transformation |
| Transformation | How the product/solution changes their world |
| New Reality | The measurably better outcome |

**Slide mapping**: 1–2 ordinary world → 1 call → 2–3 trials → 2–3 transformation → 1–2 new reality → 1 CTA

### Problem–Solution
**Best for**: Technical reviews, architecture decisions, feature justifications

Direct and efficient. Present the problem with evidence, then the solution with evidence. Works when the audience values logic over narrative flair.

**Slide mapping**: 1 hook → 2–3 problem definition → 1–2 impact → 3–4 solution → 1–2 evidence → 1 CTA

### What Is / What Could Be
**Best for**: Vision decks, aspiration pitches, roadmap presentations

Alternates between current state and future possibility to create a pull toward the vision. Each contrast pair increases the gap between "now" and "possible."

**Slide mapping**: 1 hook → (what is → what could be) × 3–4 pairs → 1 bridge → 1 CTA

### Before–During–After
**Best for**: Transformation stories, migration plans, improvement case studies

Shows the journey from old state through transition to new state. Effective when the audience needs to understand both the change and the path.

## Audience-Framework Matrix

| Audience | Goal: Decision Ask | Goal: Vision/Roadmap | Goal: Technical Review | Goal: Customer Story |
|----------|-------------------|---------------------|----------------------|---------------------|
| **Executive** | SCR | What Is/Could Be | SCR (problem-first) | Hero's Journey |
| **Technical** | Problem–Solution | What Is/Could Be | Problem–Solution | Before–During–After |
| **Customer-facing** | Hero's Journey | What Is/Could Be | Problem–Solution | Hero's Journey |
| **Investor** | SCR | What Is/Could Be | SCQA | Hero's Journey |
| **Mixed** | SCR (safest) | What Is/Could Be | SCQA | SCR |

When in doubt, SCR is the safest framework — it works for almost any professional audience.

## Narrative Arc Design

Every great presentation follows an emotional arc. Map your slides to this intensity curve:

```
Engagement
    ▲
    │         ╱╲
    │        ╱  ╲     ╱╲
    │   ╱╲  ╱    ╲   ╱  ╲
    │  ╱  ╲╱      ╲ ╱    ╲
    │ ╱             ╳      ╲___
    │╱                        
    └──────────────────────────▶ Slides
    Hook  Context  Tension  Evidence  Resolution  CTA
```

### Emotional vs. Rational Beats

**Emotional beats** create engagement and urgency:
- Customer pain quotes
- Striking statistics ("40% of users abandon within 3 minutes")
- Vision statements
- Before/after contrasts

**Rational beats** build conviction and credibility:
- Data analysis
- Competitive comparison
- Technical architecture
- ROI calculations

**Rule**: Alternate between emotional and rational beats. Never have more than 2 consecutive beats of the same type. If you have 3 data slides in a row, insert a human story or provocative question between them.

## The "So What?" Test

Every slide, every section, every bullet point must answer one question for the target audience: **"So what?"**

Apply the test:
1. Read the content from the audience's perspective
2. Ask: "Why should I care about this?"
3. If you can't answer in one sentence, the content fails the test
4. Fix it: either cut it, reframe it in terms of what the audience values, or add the missing "so what"

**Common "So What?" failures:**
- Feature descriptions without user impact → Add the benefit
- Metrics without context → Add the comparison or trend
- Process details the audience doesn't need → Cut or summarize
- History without relevance to the decision → Cut or compress

## The Punch Test

Every slide headline must make someone **look up from their phone**. If a headline is a flat statement or a topic label, it fails.

**Apply the Punch Test:**
1. Read the headline out loud
2. Ask: "Would a busy executive glance up and want to know more?"
3. If no — rewrite using one of these patterns:
   - **Provocative question**: "What if we could 3x conversion without adding headcount?"
   - **Bold claim**: "We left $2M on the table last quarter"
   - **Surprising stat**: "73% of users quit before seeing our best feature"
   - **Tension statement**: "Our biggest competitor just solved the problem we're ignoring"

**Punch Test examples:**
- ❌ "Q3 revenue was $4.2M, representing a 40% increase" → ✅ "Revenue exploded 40% — and we're just getting started"
- ❌ "Customer satisfaction improved across all segments" → ✅ "Customers went from frustrated to fanatical in 90 days"
- ❌ "Market Overview" → ✅ "The market just shifted — and we're positioned to win"
- ❌ "Product Roadmap Update" → ✅ "Three bets that will define our next 12 months"

## Emotional Beat Mapping

Plan which **emotion** each slide evokes. A deck without an emotional arc is a document, not a story.

**The emotional progression for a decision-ask deck:**
```
curiosity → concern → hope → excitement → confidence → action
```

**Map it to slides:**

| Slide Position | Target Emotion | How to Evoke It |
|---------------|---------------|-----------------|
| Opening hook | Curiosity | Surprising stat, provocative question, bold claim |
| Context | Recognition | "You already know this" — nod-along content |
| Tension | Concern / Urgency | Cost of inaction, competitive threat, missed opportunity |
| Solution reveal | Hope | "What if we could..." — possibility framing |
| Evidence | Excitement | Proof it works — data, case studies, prototypes |
| Plan | Confidence | Clear path forward — timeline, resources, milestones |
| CTA | Action | Specific ask — make it easy to say yes |

**Rule**: Label each slide in your proposal with its intended emotion. If two adjacent slides target the same emotion, one of them is redundant.

## The Movie Trailer Method

Structure your deck like a movie trailer — tease the payoff, build tension, deliver the climax, end with action.

**The pattern:**
1. **Tease** (slides 1–2): Open with the payoff — "What if we could 3x our conversion?" Show the destination before the journey.
2. **Build tension** (slides 3–5): "But right now, we're losing $2M/year to..." Show what's broken, what's at stake, why inaction is dangerous.
3. **Climax** (slides 6–8): "Here's the solution" — reveal the approach with evidence. This is the turning point.
4. **Resolution** (slides 9–10): Show what the world looks like after. Paint the future.
5. **Action** (final slide): "Here's exactly what we need from you, by when."

The trailer method works because it creates a **desire gap** — the audience sees where they could be before they see how to get there. This makes them lean forward through the tension section.

## Language That Punches vs. Summarizes

Headlines and body text should create momentum, not report facts. The difference between a boring deck and a compelling one is often just the language.

**Punchy language patterns:**
- **Action verbs over state verbs**: "Revenue exploded" not "Revenue was high"
- **Specifics over generalities**: "23% in 6 months" not "significant improvement"
- **Forward-looking over backward-looking**: "and we're just getting started" not "which was a good result"
- **Contrast for drama**: "from 14 days to 3" not "reduced onboarding time"
- **Short, punchy sentences**: "That changes everything." not "This represents a significant shift in our approach."

**More examples:**
- ❌ "The team successfully completed the migration project" → ✅ "Migration complete. Zero downtime. 40% faster."
- ❌ "User engagement metrics showed improvement" → ✅ "Users went from 2 visits/month to daily — in 6 weeks"
- ❌ "We recommend investing in the platform" → ✅ "Invest $200K now or lose $2M next year"

## Anti-Patterns: Stories That Kill Decks

### "Information Vomit"
8 bullets per slide, each a full sentence. The presenter reads them aloud. The audience reads ahead and tunes out. **Fix**: One message per slide, max 4 bullets, max 15 words each.

### "The Encyclopedia"
Comprehensive but boring. Every fact included, no editorial judgment about what matters. **Fix**: Cut ruthlessly. If it doesn't drive the decision, it's an appendix item.

### "The Hedger"
"Results were somewhat positive" / "We believe this could potentially improve..." / "There may be an opportunity to..." **Fix**: Take a position. "Results crushed expectations" or "Results fell short — here's why and what we're doing."

### "The Agenda Slide Opener"
Starting with "Today we'll cover..." kills momentum before the story begins. **Fix**: Open with a hook — a surprising stat, a provocative question, or a bold claim. Never open with logistics.

### "The Data Dump"
Six charts on one slide. Each chart has 10 data points. No headline telling you what to see. **Fix**: One chart per slide. Headline states the conclusion. Simplify to 3–5 data points max.

## Handling Multiple Valid Narratives

When the knowledge graph supports several equally compelling paths:

1. Generate 2–3 alternatives (never more than 3 — choice overload)
2. For each, provide: framework name, 2-sentence rationale, and slide title sequence
3. Include your recommendation with reasoning
4. Let the user choose — they know their audience better than you do

## References

For detailed framework deep-dives:
- [Storytelling Frameworks](references/storytelling-frameworks.md) — Complete framework guides with examples and anti-patterns
- [Audience Psychology](references/audience-psychology.md) — Stakeholder archetypes, decision-making psychology, persuasion patterns
- [Headline Craft](references/headline-craft.md) — Punch Test patterns, emotional-arc annotation, language-that-punches
- [Approval-Gate Rationale](references/approval-gate-rationale.md) — Why the orchestrator's Stop-B gate is non-negotiable
