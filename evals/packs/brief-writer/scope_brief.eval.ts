/**
 * Scope-brief: describe an already-committed MVP's boundary without inventing a decision ask.
 */

import { Eval } from "evalpilot";
import { NO_INPUT, hygiene, type Ctx, type Result } from "./brief-checks";

const BRIEF = "briefs/data-products-mvp-scope.md";
const SRC = "fixtures/scope_brief";

export default new Eval("brief-writer-scope-brief", {
  target: "brief-writer",
  kind: "skill",
  tags: ["behaviour", "slow", "judge"],
  timeout: 900,
})
  .summarize("A scope description stays a scope-brief: explicit in/out boundaries, no phantom decision ask.")
  .describe(
    "Fixture: scope overview + per-surface boundaries for a committed MVP. Expect in/out-of-scope " +
      "content per surface, deferred items listed, and no approval/funding/go-no-go request.",
  )
  .stageSkill("brief-writer")
  .copy(`${SRC}/scope-overview.md`, "inputs")
  .copy(`${SRC}/surfaces.md`, "inputs")
  .prompt(
    `Write a brief describing the scope of our Data Products MVP so partner engineering teams know what is in and out. ` +
      `Sources are in \`inputs/\`. The team has already committed to building it; nothing is being requested. ` +
      `Save it to \`${BRIEF}\`.\n\n${NO_INPUT}`,
  )
  .expectFile(BRIEF)
  .check("no approval or funding ask", (ctx: Ctx): Result => {
    const t = ctx.read(BRIEF) ?? "";
    const hit = t.match(/\b(we (request|ask|seek)|request(ing)? (approval|funding|sign-off)|approve (the|this)|go\/no-go)\b/i);
    return [!hit, hit ? `phantom ask: "${hit[0]}"` : ""];
  })
  .check("deferred items carried", (ctx: Ctx): Result => {
    const t = (ctx.read(BRIEF) ?? "").toLowerCase();
    const missing = ["version", "approval", "cross-org", "analytics"].filter((k) => !t.includes(k));
    return [missing.length === 0, `missing out-of-scope items: ${missing.join(", ")}`];
  })
  .check("writing hygiene", (ctx: Ctx): Result => hygiene(ctx.read(BRIEF)))
  .judge(
    "This brief describes a committed MVP's scope for partner engineering teams. Score 1.0 only if: (a) it states " +
      "in-scope and out-of-scope clearly, surface by surface (create, publish, discover/read) and for users " +
      "(producers and consumers in; admins and external orgs out); (b) it contains no decision, approval, funding, or " +
      "go/no-go request and does not invent a call to action; (c) the executive summary states the scope boundary " +
      "rather than an ask; (d) it uses plain language with no filler or writer-scaffolding. Score 0.5 if scope is " +
      "clear but an unsolicited ask or padding was added. Score 0.0 if it reads as a decision brief.",
    { artifact: BRIEF, threshold: 0.7 },
  )
  .metric("judge_score", "$judge.score", { direction: "higher_is_better", baseline: "rolling_mean", tolerance: 0.1 })
  .build();
