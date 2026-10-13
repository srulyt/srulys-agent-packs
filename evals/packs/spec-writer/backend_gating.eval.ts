/**
 * Gating, non-UI case: a backend-only technical spec omits the UX section,
 * keeps a single persona table, includes NFRs, and still derives failure FRs.
 */

import { Eval } from "evalpilot";
import {
  NO_INPUT, frShape, hasHeading, mandatoryInOrder, personaTableCount, unwantedFrCount,
  type Ctx, type Result,
} from "./spec-checks";

const SPEC = "specs/ingestion-rate-limit.md";

export default new Eval("spec-writer-backend-gating", {
  target: "spec-writer",
  kind: "skill",
  tags: ["behaviour", "slow", "judge", "gating"],
  timeout: 900,
})
  .summarize("A backend-only spec omits the UX section and carries NFRs and failure FRs.")
  .describe(
    "Per-tenant rate limiting on an internal gRPC API with no UI. The experience-surface " +
      "gate must not fire; infra-platform-change must (NFRs). Failure modes of the limiter " +
      "itself must be derived as FRs.",
  )
  .stageSkill("spec-writer")
  .prompt(
    `Write a technical spec and save it to \`${SPEC}\`.

Context: Our internal ingestion API is a gRPC service called only by other backend services; it has no UI. One noisy tenant recently saturated it and degraded ingestion for everyone. We want per-tenant rate limiting with a default of 1,000 requests/second per tenant, configurable per tenant by the platform team, enforced across all 12 API replicas. Rejected requests should get a clear signal so callers can back off.

${NO_INPUT}`,
  )
  .expectFile(SPEC)
  .check("mandatory sections in order", (ctx: Ctx): Result => mandatoryInOrder(ctx.read(SPEC)))
  .check("no UX / journeys section for a non-UI spec", (ctx: Ctx): Result => {
    const t = ctx.read(SPEC) ?? "";
    return [!hasHeading(t, /user experience|journey/i), "UX/journey section present on a backend-only spec"];
  })
  .check("at most one persona table", (ctx: Ctx): Result => {
    const n = personaTableCount(ctx.read(SPEC) ?? "");
    return [n <= 1, `${n} persona tables`];
  })
  .check("NFRs or capacity targets present", (ctx: Ctx): Result => {
    const t = ctx.read(SPEC) ?? "";
    return [hasHeading(t, /non-functional|capacity/i) && /\bNFR-\d+/.test(t), "no NFR section/IDs"];
  })
  .check("every FR is one shall + Given/When/Then AC", (ctx: Ctx): Result => frShape(ctx.read(SPEC)))
  .check("≥ 2 derived unwanted-behaviour FRs", (ctx: Ctx): Result => {
    const n = unwantedFrCount(ctx.read(SPEC) ?? "");
    return [n >= 2, `found ${n} If/then FRs`];
  })
  .judge(
    "This is a technical spec for per-tenant rate limiting on an internal backend gRPC API with no UI. Score 1.0 only " +
          "if ALL hold: (a) there is no user-experience/journey section and there is at most one persona/actor table " +
          "(mentioning actors in prose elsewhere is fine); (b) FRs name the " +
          "system as subject, use EARS, and state what not how; (c) the FRs derive limiter failure modes the brief did not " +
          "spell out — at least three of: shared counter/store unavailable (fail-open vs fail-closed, which should be TBD + " +
          "OQ unless justified), burst handling, missing or invalid tenant config, config changes taking effect, replica " +
          "skew/consistency, retry storms from rejected callers, unknown tenant id; (d) the rejection signal is specified " +
          "testably (e.g. RESOURCE_EXHAUSTED with retry hint); (e) every NFR has a verification method and either a " +
          "measurable target or, where the brief gave no number, a TBD linked to an Open Question (inventing numbers fails). " +
      "Score 0.5 if one or two of (a)-(e) fail. Score 0.0 if it reads like a UI product spec or covers only the happy path.",
    { artifact: SPEC, threshold: 0.7 },
  )
  .metric("judge_score", "$judge.score", { direction: "higher_is_better", baseline: "rolling_mean", tolerance: 0.1 })
  .build();
