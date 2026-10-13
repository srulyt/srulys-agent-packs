/**
 * Review feedback: given meeting notes, the skill proposes changes (including
 * what-ifs raised by reviewers) but does not modify the spec without authorization.
 */

import { Eval } from "evalpilot";
import { NO_INPUT, fixture, norm, type Ctx, type Result } from "./spec-checks";

const SPEC = "specs/search-filters.md";

export default new Eval("spec-writer-review-proposes-only", {
  target: "spec-writer",
  kind: "skill",
  tags: ["behaviour", "slow", "judge"],
  timeout: 600,
})
  .summarize("Review notes produce proposed changes; the spec is not edited without authorization.")
  .describe(
    "Fixture is a draft spec plus review notes. The user asks the skill to go through the " +
      "notes. Expect the spec file byte-identical and the reply to propose concrete FR/AC " +
      "changes, including FRs for the reviewers' what-ifs.",
  )
  .stageSkill("spec-writer")
  .copy("fixtures/draft/search-filters.md", "specs")
  .copy("fixtures/review/review-notes.md", "inputs")
  .prompt(
    `Go through the review notes in \`inputs/review-notes.md\` for \`${SPEC}\` and tell me what you would change.\n\n${NO_INPUT}`,
  )
  .check("spec file not modified", (ctx: Ctx): Result => {
    const ok = norm(ctx.read(SPEC) ?? "") === norm(fixture("draft/search-filters.md"));
    return [ok, "spec was edited without authorization"];
  })
  .judge(
    "The reply responds to review notes on a search-filters spec without having edited it. Score 1.0 only if it " +
      "proposes concrete, spec-ready changes for each note: (a) constrained rating options; (b) a new requirement for " +
      "the facet service being unavailable (its fallback behaviour may be a TBD linked to an Open Question if the notes " +
      "don't decide it); (c) a clear-all control when results exist; (d) currency handling for price; (e) products with " +
      "no price as a new FR or TBD + OQ; and it treats the persistence question as the existing OQ-01 rather than " +
      "deciding it. It must ask for (or await) authorization before applying changes. Inventing an answer the notes " +
      "leave open counts against it. Score 0.5 if 3-4 notes are handled concretely. Score 0.0 if it only summarises the notes.",
    { threshold: 0.7 },
  )
  .metric("judge_score", "$judge.score", { direction: "higher_is_better", baseline: "rolling_mean", tolerance: 0.1 })
  .build();
