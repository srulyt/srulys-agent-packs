/**
 * Builder-style eval (`*.eval.ts`) — custom `check()` predicate example.
 *
 * The interesting bit is a `check()` predicate that counts questions in the
 * streamed output — a computation the declarative Markdown DSL cannot express.
 * It encodes the skill's contract that there is NO maximum question count (the
 * interrogation should ask *several* questions), which a fixed assertion kind
 * could not capture. Run it like a Markdown eval:
 *
 *     evalpilot run evals/skills/grill-me-interrogation/question_discipline.eval.ts
 */

import { Eval } from "evalpilot";

const PROMPT = `Here is an under-specified feature brief: "We want to add a 'share
report' feature so users can share a generated report with people
outside their organization. It should be reasonably fast."

Grill me to close the requirement gaps before any PRD is drafted. Ask
your gap-closing questions now. (Note: the brief deliberately leaves the
authentication/sharing-access model unspecified, and leaves the
performance target as a vague 'reasonably fast'.) Do not draft a PRD;
just produce your interrogation questions.
`;

export default new Eval("grill-me-question-discipline", {
  target: "grill-me-interrogation",
  kind: "skill",
  tags: ["skill", "slow", "judge"],
  timeout: 300,
})
  .summarize(
    "Grill-me questions are well-formed, tagged, and MC-vs-freeform correct.",
  )
  .describe(
    "Skill-in-isolation eval: grill-me-interrogation question discipline.\n\n" +
      "Gives the skill an under-specified feature brief containing at least one " +
      "enumerable-answer gap (auth model) and at least one open-ended gap " +
      "(latency budget), and asks it to 'grill me' to close gaps. Judges " +
      "question discipline: one gap per question, P0/P1/P2 tags, multiple-choice " +
      "where applicable (with an escape) vs. freeform, and no invented answers.\n\n" +
      "The judge does NOT assert any maximum question count — the skill removes " +
      "the legacy cap deliberately.",
  )
  .prompt(PROMPT)
  // Structural gate: priority tags must be present.
  .expectStdout(["P0", "P1", "P2"], { name: "has a P0/P1/P2 priority tag" })
  // Custom predicate: several questions, with no upper bound.
  .check("asks several questions (no max)", (ctx) => {
    const text = ctx.stdout || "";
    const n = text
      .split(/\r?\n/)
      .filter((ln: string) => ln.includes("?")).length;
    const ok = n >= 3;
    return [ok, `found ${n} question line(s); expected >= 3`];
  })
  .judge(
    "The response is a grill-me interrogation question set. It MUST " +
      "satisfy ALL of:\n" +
      "(a) Each question targets exactly ONE gap — no compound questions " +
      "    bundling two decisions.\n" +
      "(b) Every question is tagged with a P0/P1/P2 priority, with blockers " +
      "    (P0) flagged first.\n" +
      "(c) The enumerable gap (the auth / sharing-access model) is posed as " +
      "    MULTIPLE-CHOICE with 2-6 sensible, mutually-distinct options PLUS " +
      "    an escape such as 'Not sure / decide later' (or an explicit " +
      "    freeform/'specify your own' affordance). It is acceptable for this " +
      "    to be expressed via an ask_user-style call or inline option list.\n" +
      "(d) The open-ended gap (the latency / performance budget) is posed as " +
      "    a FREEFORM question, NOT as fabricated buckets like fast/medium/slow.\n" +
      "(e) No answers are invented to fill the spec — the skill asks rather " +
      "    than assuming.\n" +
      "Do NOT penalise the response for asking 'too many' questions; there is " +
      "no maximum question count. Score 1.0 only if all five (a-e) hold. " +
      "Score 0.5 if 3-4 hold. Score 0.0 otherwise.",
    { threshold: 0.7 },
  )
  .metric("judge_score", "$judge.score", {
    direction: "higher_is_better",
    baseline: "rolling_mean",
    tolerance: 0.1,
  })
  .build();
