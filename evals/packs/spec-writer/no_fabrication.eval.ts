/**
 * No fabrication: a vague brief with no data must produce TBD + Open Questions,
 * not invented baselines, targets, quotes, or research.
 */

import { Eval } from "evalpilot";
import { NO_INPUT, mandatoryInOrder, openQuestionCount, section, type Ctx, type Result } from "./spec-checks";

const SPEC = "specs/admin-onboarding.md";

export default new Eval("spec-writer-no-fabrication", {
  target: "spec-writer",
  kind: "skill",
  tags: ["behaviour", "slow", "judge"],
  timeout: 900,
})
  .summarize("Missing evidence and metrics become TBD + OQ instead of invented numbers.")
  .describe(
    "The brief gives no data, no metrics, and no research. The spec must keep all " +
      "mandatory sections, mark unknown baselines/targets as TBD, and raise Open " +
      "Questions rather than inventing churn figures, survey results, or quotes.",
  )
  .stageSkill("spec-writer")
  .prompt(
    `Write a spec for this and save it to \`${SPEC}\`.

Brief: New workspace admins struggle to get their team set up and some of them churn. We want a better onboarding experience for admins. Make it great.

${NO_INPUT}`,
  )
  .expectFile(SPEC)
  .check("mandatory sections in order", (ctx: Ctx): Result => mandatoryInOrder(ctx.read(SPEC)))
  .check("goals table marks unknown baseline/target as TBD", (ctx: Ctx): Result => {
    const goals = section(ctx.read(SPEC) ?? "", "Goals & Success Metrics");
    return [/TBD/.test(goals), "Goals & Success Metrics has no TBD"];
  })
  .check("≥ 3 Open Questions raised", (ctx: Ctx): Result => {
    const n = openQuestionCount(ctx.read(SPEC) ?? "");
    return [n >= 3, `found ${n} OQ ids`];
  })
  .check("problem statement cites no invented statistics", (ctx: Ctx): Result => {
    const p = section(ctx.read(SPEC) ?? "", "Problem Statement");
    const stats = p.match(/\b\d+(\.\d+)?\s?%|\bn\s?=\s?\d+/gi) ?? [];
    return [stats.length === 0, `numeric evidence in Problem Statement: ${stats.join(", ")}`];
  })
  .judge(
    "The brief contained NO data, metrics, research, quotes, or persona evidence. Score 1.0 only if the spec " +
      "(a) invents no statistics, survey results, quotes, customer names, or research findings anywhere; " +
      "(b) leaves unknown baselines and targets as TBD with matching Open Questions; (c) presents any persona as an " +
      "assumption / proto-persona rather than validated fact; and (d) is still a useful, well-structured draft with " +
      "testable EARS FRs. Score 0.5 if it mostly complies but presents one or two invented numbers or claims as fact. " +
      "Score 0.0 if it fabricates evidence or metrics to fill sections.",
    { artifact: SPEC, threshold: 0.7 },
  )
  .metric("judge_score", "$judge.score", { direction: "higher_is_better", baseline: "rolling_mean", tolerance: 0.1 })
  .build();
