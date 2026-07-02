/**
 * Builder-style eval (`*.eval.ts`) — judge-only skill example.
 *
 * This is one of a handful of evals authored with the fluent TypeScript builder
 * instead of the Markdown DSL. Reach for the builder when you want computed
 * prompts, shared fixtures, or custom `check()` predicates. Run it exactly like
 * a Markdown eval:
 *
 *     evalpilot run evals/skills/ears-prd-format/ears_shape.eval.ts
 *
 * It exercises the `ears-prd-format` skill in isolation: cheap structural gates
 * on the streamed stdout, then an LLM judge on EARS shape. There is no artifact
 * file — the judge scores the run output directly.
 */

import { Eval } from "evalpilot";

const PROMPT = `Format the following raw requirements for an "Orders" service as EARS
Functional Requirements with nested Given/When/Then acceptance criteria.
Use FR-NN and AC-<FR>.<n> IDs. Output the formatted requirements as
markdown.

Raw requirements:
1. The service keeps an audit log of every order state change.
2. When a customer cancels an order, refund the payment.
3. If the payment provider times out, mark the order pending and retry.
4. While the store is in maintenance mode, reject new orders.
`;

export default new Eval("ears-prd-format-shape", {
  target: "ears-prd-format",
  kind: "skill",
  tags: ["skill", "slow", "judge"],
  timeout: 300,
})
  .summarize("Formatted FRs are valid EARS with one shall each and testable ACs.")
  .describe(
    "Skill-in-isolation eval: ears-prd-format EARS validity.\n\n" +
      "Gives the format skill a short list of raw requirements and asks it " +
      "to format them as EARS Functional Requirements with nested " +
      "acceptance criteria, then judges EARS shape.",
  )
  .prompt(PROMPT)
  // Cheap structural gates on the streamed output before spending a judge call.
  .expectStdout(["FR-", "AC-"])
  .expectStdout("shall", { ignoreCase: true })
  .judge(
    "The response formats raw requirements as EARS Functional " +
      "Requirements. Every FR MUST:\n" +
      "1. Match one of the 6 EARS patterns (ubiquitous, event-driven, " +
      "   state-driven, optional-feature, unwanted, complex).\n" +
      "2. Contain EXACTLY ONE `shall`.\n" +
      "3. Name a system/component as the subject (never 'we' or 'the user').\n" +
      "4. Express WHAT, not HOW (no implementation choices).\n" +
      "5. Have at least one nested, testable Given/When/Then acceptance " +
      "   criterion with concrete inputs and an observable result.\n" +
      "Score 1.0 only if ALL listed FRs satisfy all five rules. Score 0.5 " +
      "if most do with minor violations. Score 0.0 if multiple FRs are " +
      "malformed (e.g. multiple shalls, 'we shall', or how-not-what).",
    { threshold: 0.7 },
  )
  .metric("judge_score", "$judge.score", {
    direction: "higher_is_better",
    baseline: "rolling_mean",
    tolerance: 0.1,
  })
  .build();
