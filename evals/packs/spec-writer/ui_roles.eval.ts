/**
 * Gating, UI-forward case: a multi-role workflow UI gets the UX section with a
 * journey, a role/permission matrix, deny-path ACs, and a single persona table.
 */

import { Eval } from "evalpilot";
import { NO_INPUT, frShape, hasHeading, mandatoryInOrder, personaTableCount, type Ctx, type Result } from "./spec-checks";

const SPEC = "specs/expense-approval.md";

export default new Eval("spec-writer-ui-roles", {
  target: "spec-writer",
  kind: "skill",
  tags: ["behaviour", "slow", "judge", "gating"],
  timeout: 900,
})
  .summarize("A UI-forward, multi-role spec includes journeys, a role matrix, and deny-path ACs.")
  .describe(
    "Expense approval with employees, managers, and finance admins. The experience-surface " +
      "gate must fire; personas appear only once; roles are deny-by-default and pinned by " +
      "negative ACs; role-related what-ifs (self-approval, absent manager, concurrent " +
      "approve/override) are derived.",
  )
  .stageSkill("spec-writer")
  .prompt(
    `Write a product spec and save it to \`${SPEC}\`.

Brief: We're building a new expense approval experience in our web app. Employees submit expenses with a receipt. Their manager reviews a queue and approves or rejects each one. Finance admins can override any decision. Employees see the status of their submissions.

${NO_INPUT}`,
  )
  .expectFile(SPEC)
  .check("mandatory sections in order", (ctx: Ctx): Result => mandatoryInOrder(ctx.read(SPEC)))
  .check("UX / journeys section present", (ctx: Ctx): Result => {
    const t = ctx.read(SPEC) ?? "";
    return [hasHeading(t, /user experience|journey/i), "no UX/journey section on a UI-forward spec"];
  })
  .check("exactly one persona table", (ctx: Ctx): Result => {
    const n = personaTableCount(ctx.read(SPEC) ?? "");
    return [n === 1, `${n} persona tables`];
  })
  .check("role/permission matrix present", (ctx: Ctx): Result => {
    const t = ctx.read(SPEC) ?? "";
    return [/^\|\s*Role\s*\|/im.test(t), "no '| Role |' table"];
  })
  .check("deny-path acceptance criteria present", (ctx: Ctx): Result => {
    const acs = (ctx.read(SPEC) ?? "").split(/\r?\n/).filter((l) => /AC-\d+\.\d+/.test(l));
    const deny = acs.filter((l) => /\b(denied|deny|rejected with|forbidden|403|not (permitted|authori[sz]ed|allowed)|cannot|is blocked)\b/i.test(l));
    return [deny.length >= 2, `${deny.length} deny-path ACs`];
  })
  .check("every FR is one shall + Given/When/Then AC", (ctx: Ctx): Result => frShape(ctx.read(SPEC)))
  .judge(
    "This is a UI-forward expense approval spec with employee, manager, and finance-admin roles. Score 1.0 only if ALL " +
      "hold: (a) personas are defined once in Users & Personas and referenced by name elsewhere; (b) there is a primary " +
      "journey whose steps map to FRs and whose 'what can go wrong' entries map to failure FRs; (c) a role/permission " +
      "matrix states a deny-by-default, server-side-enforced posture; (d) role-related what-ifs are derived as FRs — at " +
      "least three of: a manager trying to approve their own expense, an absent/departed manager, approve and override " +
      "racing on the same item, an employee editing an expense after submission, an invalid or missing receipt, a " +
      "non-manager calling the approve endpoint directly; (e) policy choices (e.g. who approves when the manager is " +
      "absent) are TBD + Open Question rather than invented. Score 0.5 if one or two of (a)-(e) fail. Score 0.0 if " +
      "roles are only described in prose or only the happy path is covered.",
    { artifact: SPEC, threshold: 0.7 },
  )
  .metric("judge_score", "$judge.score", { direction: "higher_is_better", baseline: "rolling_mean", tolerance: 0.1 })
  .build();
