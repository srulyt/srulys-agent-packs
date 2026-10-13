/**
 * What-if coverage: a happy-path-only brief must still yield derived
 * negative-path FRs (EARS unwanted-behaviour) with negative ACs, and
 * business-policy what-ifs must become TBD + OQ rather than invented answers.
 */

import { Eval } from "evalpilot";
import {
  NO_INPUT, frShape, headings, mandatoryInOrder, openQuestionCount, unwantedFrCount,
  type Ctx, type Result,
} from "./spec-checks";

const SPEC = "specs/report-export.md";

export default new Eval("spec-writer-what-if-coverage", {
  target: "spec-writer",
  kind: "skill",
  tags: ["behaviour", "slow", "judge", "what-if"],
  timeout: 900,
})
  .summarize("A happy-path brief yields derived failure/edge-case FRs, not just the happy path.")
  .describe(
    "The brief describes only the success path of a CSV export. The skill must " +
      "derive what can go wrong (empty report, very large report, permission " +
      "loss, export failure, special characters / formula injection, data " +
      "changing mid-export) as ordinary FRs, and route policy choices to TBD + OQ.",
  )
  .stageSkill("spec-writer")
  .prompt(
    `Write a new product spec and save it to \`${SPEC}\`.

Brief: Analysts in our web reporting app want to export the report they are viewing to a CSV file so they can analyse it in Excel. Clicking "Export CSV" downloads the report's current rows and columns.

${NO_INPUT}`,
  )
  .expectFile(SPEC)
  .check("mandatory sections in order", (ctx: Ctx): Result => mandatoryInOrder(ctx.read(SPEC)))
  .check("every FR is one shall + Given/When/Then AC", (ctx: Ctx): Result => frShape(ctx.read(SPEC)))
  .check("≥ 3 derived unwanted-behaviour FRs (If … then … shall)", (ctx: Ctx): Result => {
    const n = unwantedFrCount(ctx.read(SPEC) ?? "");
    return [n >= 3, `found ${n} If/then FRs`];
  })
  .check("what-ifs live in FRs, not a separate section", (ctx: Ctx): Result => {
    const bad = headings(ctx.read(SPEC) ?? "").filter((h) =>
      /^(edge cases?|error (cases|handling)|failure (modes|cases)|what.?ifs?|negative scenarios)\b/i.test(h));
    return [bad.length === 0, bad.length ? `separate section(s): ${bad.join(", ")}` : ""];
  })
  .check("policy gaps become TBD + OQ", (ctx: Ctx): Result => {
    const t = ctx.read(SPEC) ?? "";
    const ok = /\[?TBD\b/.test(t) && openQuestionCount(t) >= 2;
    return [ok, `TBD present: ${/TBD/.test(t)}, OQs: ${openQuestionCount(t)}`];
  })
  .judge(
    "The artifact is a product spec for exporting a report to CSV. The brief mentioned ONLY the happy path. " +
      "Score how well the Functional Requirements proactively cover what can go wrong. Candidate cases: " +
      "(1) empty report / zero rows; (2) very large report (row/size limits, timeouts, async delivery); " +
      "(3) user lacks or loses permission to the report or to some columns/rows; (4) export generation or " +
      "download fails or is interrupted; (5) CSV/formula injection or special characters, delimiters, " +
      "encoding/locale (e.g. Excel UTF-8, commas, leading = + - @); (6) report data changes during export " +
      "or filters applied; (7) concurrent/repeated clicks.\n" +
      "Score 1.0 if at least 5 of these are written as FRs (not only risks or prose), AND at least 4 of those " +
      "have a concrete observable response with a negative acceptance criterion (established safe defaults such as " +
      "neutralising formula injection, a header-only file for zero rows, or ignoring duplicate clicks count as " +
      "concrete), AND choices that are genuinely business policy (e.g. the maximum row limit, whether hidden columns " +
      "are included) are left as [TBD] with an Open Question instead of invented numbers. Score 0.7 if 4 cases are " +
      "covered as FRs and at least 3 have concrete responses, with policy mostly TBD. Score 0.4 if only 2–3 cases are " +
      "covered, if most what-if FRs defer even obvious safe defaults to TBD, or if policy limits are invented as facts. " +
      "Score 0.0 if the FRs cover only the happy path.",
    { artifact: SPEC, threshold: 0.7 },
  )
  .metric("judge_score", "$judge.score", { direction: "higher_is_better", baseline: "rolling_mean", tolerance: 0.1 })
  .build();
