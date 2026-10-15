/**
 * Edit an existing brief from reviewer comments: rename propagates, links and bold labels go,
 * marketing filler is removed, and sourced facts survive.
 */

import { Eval } from "evalpilot";
import { NO_INPUT, hygiene, type Ctx, type Result } from "./brief-checks";

const BRIEF = "briefs/alert-routing.md";

export default new Eval("brief-writer-edit-existing", {
  target: "brief-writer",
  kind: "skill",
  tags: ["behaviour", "slow", "judge"],
  timeout: 900,
})
  .summarize("Reviewer comments are applied to an existing brief without losing the author's facts.")
  .describe(
    "Fixture: a draft brief with AI-isms, bold-as-headings, a link, and a product name, plus four review " +
      "comments (rename, lead with numbers, no links, fix bold labels). Expect every comment applied in place " +
      "and all sourced numbers and the ask preserved.",
  )
  .stageSkill("brief-writer")
  .copy("fixtures/edit_existing/alert-routing.md", "briefs")
  .copy("fixtures/edit_existing/review-comments.md", "inputs")
  .prompt(
    `Apply the review comments in \`inputs/review-comments.md\` to \`${BRIEF}\` and update the file.\n\n${NO_INPUT}`,
  )
  .expectFile(BRIEF)
  .check("rename propagated everywhere", (ctx: Ctx): Result => {
    const t = ctx.read(BRIEF) ?? "";
    if (/smart alert/i.test(t)) return [false, "old name 'Smart Alerts' remains"];
    return [/Owner Routing/.test(t), "new name 'Owner Routing' absent"];
  })
  .check("writing hygiene (no AI-isms, bold labels, links)", (ctx: Ctx): Result => hygiene(ctx.read(BRIEF)))
  .check("sourced facts preserved", (ctx: Ctx): Result => {
    const t = ctx.read(BRIEF) ?? "";
    const missing = ["4,100", "62%", "38 minutes", "two engineers", "Q3"].filter((k) => !t.toLowerCase().includes(k.toLowerCase()));
    return [missing.length === 0, `lost facts: ${missing.join(", ")}`];
  })
  .judge(
    "An existing brief was edited per four reviewer comments: rename Smart Alerts to Owner Routing; replace the " +
      "marketing opening and lead with the numbers; remove links; turn bold pseudo-headings into real structure. " +
      "Score 1.0 only if: (a) all four comments are applied; (b) the executive summary now opens with concrete " +
            "sourced numbers about the problem instead of marketing copy, and still carries the ask; (c) the author's facts, scope (unowned services " +
      "fall back to central rotation; thresholds unchanged) and ask (two engineers for Q3) are preserved and nothing " +
      "new is invented; (d) the edit is in place, not a rewrite into a different document. Score 0.5 if 2-3 comments " +
      "are applied cleanly. Score 0.0 otherwise.",
    { artifact: BRIEF, threshold: 0.7 },
  )
  .metric("judge_score", "$judge.score", { direction: "higher_is_better", baseline: "rolling_mean", tolerance: 0.1 })
  .build();
