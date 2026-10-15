/**
 * Late-stage Decision Ask: funding brief for VP Product + CFO from four source docs.
 */

import { Eval } from "evalpilot";
import { NO_INPUT, hygiene, noTypeLabelHeadings, type Ctx, type Result } from "./brief-checks";

const BRIEF = "briefs/onboarding-funding.md";
const SRC = "fixtures/decision_ask";

export default new Eval("brief-writer-decision-ask", {
  target: "brief-writer",
  kind: "skill",
  tags: ["behaviour", "slow", "judge"],
  timeout: 900,
})
  .summarize("A funding request becomes a decision-grade brief with sourced options and an explicit ask.")
  .describe(
    "Fixture: funding ask, customer research, options (build $1.4M vs buy $900K + $650K/yr), metrics. " +
      "Expect a recommendation-first brief with sourced option trade-offs, a P1 closing naming the " +
      "decision and approvers, CFO-readable language, and no AI-isms or bold pseudo-headings.",
  )
  .stageSkill("brief-writer")
  .copy(`${SRC}/funding-ask.md`, "inputs")
  .copy(`${SRC}/customer-research.md`, "inputs")
  .copy(`${SRC}/options.md`, "inputs")
  .copy(`${SRC}/metrics.md`, "inputs")
  .prompt(
    `I need a brief asking leadership to approve funding for the FY26 onboarding redesign. Source material is in \`inputs/\`. ` +
      `Audience: VP Product and CFO. The decision is approve or reject the FY26 funding. Save it to \`${BRIEF}\`.\n\n${NO_INPUT}`,
  )
  .expectFile(BRIEF)
  .check("both costed options carried from source", (ctx: Ctx): Result => {
    const t = ctx.read(BRIEF) ?? "";
    const ok = /1\.4\s?M/i.test(t) && /(900\s?K|0\.9\s?M)/i.test(t) && /650\s?K/i.test(t);
    return [ok, "missing $1.4M / $900K / $650K option costs"];
  })
  .check("writing hygiene", (ctx: Ctx): Result => hygiene(ctx.read(BRIEF)))
  .check("closing heading is not a type label", (ctx: Ctx): Result => noTypeLabelHeadings(ctx.read(BRIEF)))
  .judge(
    "This brief asks the VP Product and CFO to approve FY26 onboarding funding. Score 1.0 only if ALL hold: " +
      "(a) the recommendation and the decision appear in the opening executive summary; (b) at least two options " +
      "are compared with cost and trade-offs taken from the sources, including Option B's recurring fee and the " +
            "month-22 cost crossover (questioning the crossover's support is acceptable); (c) the closing states the exact decision, who decides, the commitment, and what " +
      "the approvers gain by saying yes and risk by saying no; (d) the business case is in terms a CFO uses " +
      "(cost, revenue/conversion, timing, risk), not product or engineering jargon; (e) no writer-scaffolding or " +
      "meta-commentary (announcing captions, 'this matters because', design self-commentary, emphasis-only " +
            "'X, not Y', narrating the source documents such as 'the source includes…', or the same caveat repeated across sections); judge the class, not exact phrases; (f) no numbers absent from the sources are presented as fact. " +
      "Score 0.5 if options and evidence are covered but the ask is vague or scaffolding is noticeable. " +
      "Score 0.0 if it reads as an exploratory summary without a decision.",
    { artifact: BRIEF, threshold: 0.7 },
  )
  .metric("judge_score", "$judge.score", { direction: "higher_is_better", baseline: "rolling_mean", tolerance: 0.1 })
  .build();
