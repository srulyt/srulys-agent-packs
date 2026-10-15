/**
 * Early-stage: thin concept note, author as audience, no decision. Brief stays short and closes as a summary.
 */

import { Eval } from "evalpilot";
import { NO_INPUT, hygiene, noTypeLabelHeadings, words, type Ctx, type Result } from "./brief-checks";

const BRIEF = "briefs/pinned-insights.md";

export default new Eval("brief-writer-early-stage", {
  target: "brief-writer",
  kind: "skill",
  tags: ["behaviour", "slow", "judge"],
  timeout: 900,
})
  .summarize("Thin material yields a short exploratory brief with no padded sections or invented ask.")
  .describe(
    "Fixture: a few-paragraph concept note. Expect a short brief that keeps the unknowns as open " +
      "questions, closes as a summary-style section, and doesn't pad optional sections.",
  )
  .stageSkill("brief-writer")
  .copy("fixtures/early_stage/concept-note.md", "inputs")
  .prompt(
    `Turn my concept note in \`inputs/concept-note.md\` into a short brief for my own thinking. No decision is being ` +
      `asked; audience is just me for now. Save it to \`${BRIEF}\`.\n\n${NO_INPUT}`,
  )
  .expectFile(BRIEF)
  .check("short (≤ 700 words)", (ctx: Ctx): Result => {
    const n = words(ctx.read(BRIEF) ?? "");
    return [n <= 700, `${n} words`];
  })
  .check("no padded optional sections", (ctx: Ctx): Result => {
    const t = ctx.read(BRIEF) ?? "";
    const hit = t.match(/^#+\s*.*\b(investment|cost|budget|implementation plan|faq|options considered)\b/im);
    return [!hit, hit ? `unsupported section: ${hit[0]}` : ""];
  })
  .check("writing hygiene", (ctx: Ctx): Result => hygiene(ctx.read(BRIEF)))
  .check("closing heading is not a type label", (ctx: Ctx): Result => noTypeLabelHeadings(ctx.read(BRIEF)))
  .judge(
    "This brief comes from a thin concept note about 'Pinned Insights' (starring charts onto one page). " +
      "The source itself states: analysts rebuild views every Monday, three customer calls last month, and a " +
      "possible proposal next quarter; these are not inventions. Score 1.0 " +
      "only if: (a) its length matches the thin source, with no padding; (b) it captures the hypothesis and the " +
      "customer signal (analysts keeping personal docs of key charts) without inflating it into statistics; (c) the " +
      "three unknowns (personal vs shared, live vs snapshot, adoption) are kept as open questions, not resolved by " +
      "invention; (d) it closes with a summary-style section (key takeaways, where things stand, or what would need " +
            "to be true before acting), not a decision or approval ask; (e) there's no writer-scaffolding or meta-commentary, " +
            "including restating the same evidence caveat in several sections or describing the brief's own status. " +
            "Score 0.5 if 3-4 of these hold. Score 0.0 otherwise.",
    { artifact: BRIEF, threshold: 0.7 },
  )
  .metric("judge_score", "$judge.score", { direction: "higher_is_better", baseline: "rolling_mean", tolerance: 0.1 })
  .build();
