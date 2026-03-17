# Audience Psychology

Deep-dive reference on stakeholder archetypes, decision-making psychology, persuasion patterns, and handling mixed audiences.

## Stakeholder Archetypes

### The Executive

**What they care about**: Business outcomes, competitive position, risk, ROI, team capacity, strategic alignment
**Decision-making style**: Top-down, fast, pattern-matching. They've seen hundreds of proposals — they're looking for signals of quality, not details.
**Time horizon**: Quarterly and annual. Connect everything to business cycles.
**Attention span**: Short. You have 2–3 minutes before they form an initial opinion.

**How to persuade an executive:**
- Lead with the outcome, not the process
- Frame everything in terms of what they're measured on: revenue, growth, market share, risk reduction
- Provide a clear, binary (or trinary) decision with your recommendation
- Make the "do nothing" option explicit and unappealing
- Use specific numbers — executives distrust vague claims
- Anticipate their objections and address them preemptively

**Language patterns that work:**
- "This unlocks $X in annual value" (quantified outcome)
- "The cost of inaction is..." (loss aversion)
- "We can start with a $X pilot in N weeks" (low-risk entry)
- "Three other companies in our space have already..." (competitive pressure)

**Language patterns to avoid:**
- "We think this could be interesting" (no conviction)
- "The technology enables..." (features, not outcomes)
- "It's complicated, but..." (complexity = anxiety)

### The Technical Decision-Maker

**What they care about**: Correctness, scalability, maintainability, technical debt, team capability, operational risk
**Decision-making style**: Bottom-up, evidence-driven, detail-oriented. They want to understand HOW things work.
**Time horizon**: Implementation timeline to long-term maintenance
**Attention span**: Long for relevant detail, zero for hand-waving

**How to persuade a technical leader:**
- Show that you understand the problem space deeply
- Provide architectural context — how this fits into the existing system
- Address failure modes and edge cases proactively
- Offer tradeoffs, not just a single option — they want to see your reasoning
- Include performance data, benchmarks, or prototypes
- Respect their expertise — don't oversimplify

**Language patterns that work:**
- "Here's how this handles the N+1 case" (edge-case awareness)
- "We evaluated three approaches; here's why this one wins" (systematic reasoning)
- "The migration path is..." (practical reality)
- "This reduces complexity from O(n²) to O(n log n)" (quantified technical improvement)

### The Customer-Facing Stakeholder

**What they care about**: User experience, adoption rates, customer feedback, support burden, competitive differentiation
**Decision-making style**: Empathy-driven, user-focused. They represent the customer's voice.
**Time horizon**: Feature releases to annual planning
**Attention span**: Moderate — engaged when content connects to real users

**How to persuade customer-facing stakeholders:**
- Lead with user stories and real customer quotes
- Show user impact data — adoption rates, satisfaction scores, support tickets
- Demonstrate that you've listened to customer feedback
- Frame technical decisions in terms of user experience
- Include customer journey implications

### The Investor / Board Member

**What they care about**: Market size, growth trajectory, competitive moat, unit economics, team strength, risk
**Decision-making style**: Portfolio thinking — comparing this opportunity to all others
**Time horizon**: 1–5 years
**Attention span**: Short for details, long for narrative

**How to persuade an investor:**
- Market size before product details
- Traction and momentum metrics front and center
- Clear articulation of competitive advantage
- Team credibility signals
- Transparent about risks with mitigation plans

## Decision-Making Psychology

### Loss Aversion

People feel losses roughly twice as strongly as equivalent gains. Use this:
- Frame the cost of inaction: "Every month we delay costs us $X in lost revenue"
- Show competitive loss: "While we evaluate, competitors are capturing the market"
- Don't overdo it — too much fear creates paralysis, not action

### Anchoring Effect

The first number people hear becomes their reference point. Use this:
- Present the full cost/impact first, then show your more efficient approach
- When showing ROI, lead with the return, not the investment
- In comparisons, put the larger/worse number first

### Social Proof

People follow what others are doing, especially peers. Use this:
- "Three Fortune 500 companies adopted this approach in Q2"
- "Teams that implemented this saw 40% improvement on average"
- Internal examples: "The payments team did this and reduced incidents by 60%"

### The IKEA Effect

People value things more when they contributed to creating them. Use this:
- Frame the proposal as building on the audience's earlier decisions
- Acknowledge their team's work as the foundation
- Position the new proposal as the natural next step of their strategy

### Choice Architecture

How you present options shapes the decision:
- **Three options**: Present three alternatives — one modest, one recommended, one ambitious. The recommended option should be the middle path.
- **Default option**: Make the recommended path the "default" — what happens if they simply say yes
- **Explicit "do nothing"**: Always include the status quo as an option and show its consequences

## Persuasion Patterns

### Championing Language

Your audience needs to sell your story in THEIR meetings. Give them ammunition:
- Include memorable one-liners they can repeat: "This is the difference between serving 10K and 100K users"
- Provide specific talking points they can use: "If someone asks about risk, here's the answer..."
- Make the executive summary work as a verbal pitch — 30 seconds max

### Risk Reduction

Every proposal creates anxiety. Proactively reduce it:
- **Pilot framing**: "We can validate this with a 4-week pilot before committing"
- **Reversibility**: "If results aren't there by week 6, we can roll back with no lasting impact"
- **Precedent**: "This approach is proven — [Company X] ran this playbook last quarter"
- **Staging**: "Phase 1 is low-risk and delivers value independently"

### Aspiration Framing

For vision and roadmap presentations, paint the future vividly:
- Use present tense for the future state: "In this world, customers onboard in 3 minutes, not 3 days"
- Create contrast with current pain: "Today we spend 40% of engineering time on X. Tomorrow, zero."
- Connect to identity: "This is how we become the platform our customers can't live without"

## Handling Mixed Audiences

When your audience contains multiple archetypes (e.g., exec + technical lead + customer PM):

1. **Layer your content**: Start with executive-level takeaways, then provide deeper detail. Each layer should work standalone.
2. **Use the appendix pattern**: Core deck for the broadest audience; detailed slides in an appendix for deep-divers
3. **Label sections**: "For the business case..." "For technical due diligence..."
4. **Speaker notes carry the detail**: The slides stay clean; the presenter adapts depth verbally
5. **Default to the highest-authority audience**: If the CEO and an engineer are both present, design for the CEO — the engineer will ask clarifying questions

### The Mixed-Audience Slide Pattern

For a slide that must serve multiple audiences:
- **Title**: Executive-friendly action statement
- **Body**: 3 bullets at business level
- **Speaker notes**: Technical depth and nuance for verbal delivery
- **Appendix reference**: "See slide 18 for architecture detail"

This way, the executive sees what they need, and the technical person knows where to find depth.

## Decision Triggers

Beyond general psychology, these specific triggers push audiences toward "yes":

### Urgency
Create time pressure — not artificial deadlines, but real consequences of delay.
- "Every week we delay, 3 more enterprise prospects evaluate the competitor"
- "The Q3 window closes in 6 weeks — after that, we're waiting until Q1"
- "This pricing expires when the contract renews in March"

### Social Proof
Show that smart, respected peers have made the same decision.
- "Stripe, Shopify, and Figma all adopted this pattern in the last 12 months"
- "Our payments team piloted this — incidents dropped 60% in 4 weeks"
- Name-drop strategically: specific companies and specific results

### Loss Aversion
Frame the cost of inaction, not just the benefit of action. Losses feel 2x heavier than equivalent gains.
- ❌ "We could save $2M" → ✅ "We're losing $2M every year we wait"
- ❌ "This would improve retention" → ✅ "We lose 23% of users in week 1 — that's $800K walking out the door"

### Aspiration
Connect to identity and ambition — who the audience wants to become.
- "This is how we become the platform our customers can't live without"
- "The best engineering teams in the industry have already made this shift"
- "This isn't just a product bet — it's a statement about who we are"

## Making Abstract Concrete

Abstract numbers don't drive decisions. Translate every metric into something the audience can feel.

**The translation patterns:**
- **Money → People**: "$2M savings" → "That's 20 engineers for a year"
- **Percentages → Stories**: "40% reduction" → "4 out of every 10 support calls disappear"
- **Time → Experience**: "Reduced from 14 days to 3" → "A customer who signed Monday is productive by Wednesday"
- **Scale → Comparison**: "50 petabytes" → "That's every book ever written, times 500"
- **Rates → Frequency**: "99.9% uptime" → "Less than 9 hours of downtime per year"

**Rule**: Every big number in your deck should be followed by a "That means..." translation on the same slide or in speaker notes.

## The Villain and Hero Technique

Every compelling story has a villain (the problem) and a hero (the solution). This framing technique makes abstract business concepts emotionally engaging.

**How to apply it:**
1. **Name the villain**: Don't just describe a problem — personify it. "Manual reporting" becomes "the report that steals 20 hours from your best people every month."
2. **Show the villain's damage**: Quantify what the villain costs in terms the audience feels: time lost, money wasted, talent frustrated, customers leaving.
3. **Introduce the hero**: Your solution/approach. But the hero isn't the product — it's what the product enables the AUDIENCE to do.
4. **Show the hero winning**: Before/after data. The villain defeated. The audience triumphant.

**Example framing:**
- Villain: "Legacy infrastructure that breaks every time we scale"
- Damage: "$1.2M in lost revenue from outages, 3 enterprise deals killed"
- Hero: "A modern platform that scales automatically"
- Victory: "Zero outages in 6 months, 5 enterprise contracts signed"

**Key**: The audience is always the hero. Your proposal is the sword they wield. Never position yourself as the hero — position the audience as the one who makes the smart decision.
