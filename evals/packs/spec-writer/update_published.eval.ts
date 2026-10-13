/**
 * Lifecycle: editing a published spec opens a `<next>-draft`, keeps surviving
 * published IDs and text untouched, gives new items the next free ID, leaves
 * upper sections alone, and writes no changelog while draft. Fully deterministic.
 */

import { Eval } from "evalpilot";
import {
  NO_INPUT, fixture, frBlocks, norm, section, shallLine, status, version,
  type Ctx, type Result,
} from "./spec-checks";

const SPEC = "specs/notifications.md";
const LOG = "specs/CHANGELOG.md";
const ORIG = fixture("published/notifications.md");

export default new Eval("spec-writer-update-published", {
  target: "spec-writer",
  kind: "skill",
  tags: ["behaviour", "slow", "lifecycle"],
  timeout: 900,
})
  .summarize("Updating a published spec opens a draft without renumbering, rewriting, or changelog writes.")
  .describe(
    "Fixture is a published v1.0.0 spec with FR-01..FR-04 and its CHANGELOG. The user " +
      "removes FR-02 and adds a mute requirement. Expect a <next>-draft version, FR-01/03/04 " +
      "untouched, the new requirement as FR-05+, Problem Statement and Users unchanged, and " +
      "CHANGELOG.md untouched (no change-tracking while draft).",
  )
  .stageSkill("spec-writer")
  .copy("fixtures/published/notifications.md", "specs")
  .copy("fixtures/published/CHANGELOG.md", "specs")
  .prompt(
    `Update \`${SPEC}\`: we're dropping the daily email digest requirement, and we need a new requirement that a user can mute a channel temporarily for between 1 and 24 hours.

${NO_INPUT}`,
  )
  .check("status draft and version is a next -draft", (ctx: Ctx): Result => {
    const t = ctx.read(SPEC) ?? "";
    const s = status(t), v = version(t) ?? "";
    const ok = s === "draft" && /^(1\.[1-9]\d*\.0|2\.0\.0)-draft$/.test(v);
    return [ok, `status=${s} version=${v}`];
  })
  .check("published FRs keep IDs; unrelated FRs keep wording", (ctx: Ctx): Result => {
    const now = frBlocks(ctx.read(SPEC) ?? "");
    const was = frBlocks(ORIG);
    // FR-03 (push delivery) may legitimately be amended to respect the mute; FR-01/FR-04 are unrelated.
    const missing = ["FR-01", "FR-03", "FR-04"].filter((id) => !now.has(id));
    const changed = ["FR-01", "FR-04"].filter(
      (id) => now.has(id) && norm(shallLine(now.get(id)!)) !== norm(shallLine(was.get(id)!)));
    return [missing.length + changed.length === 0, `missing: ${missing.join(", ")}; reworded: ${changed.join(", ")}`];
  })
  .check("new requirement takes a new ID (≥ FR-05), mentions mute", (ctx: Ctx): Result => {
    const now = frBlocks(ctx.read(SPEC) ?? "");
    const fresh = [...now.entries()].filter(([id]) => Number(id.slice(3)) >= 5);
    const ok = fresh.some(([, b]) => /mute/i.test(b));
    return [ok, `new FR ids: ${fresh.map(([id]) => id).join(", ") || "none"}`];
  })
  .check("FR-02 no longer an active digest requirement", (ctx: Ctx): Result => {
    const b = frBlocks(ctx.read(SPEC) ?? "").get("FR-02");
    const ok = !b || /deprecat|removed|superseded|withdrawn/i.test(b) || !/\bshall\b[^\n]*digest/i.test(b);
    return [ok, "FR-02 still states the digest shall-statement"];
  })
  .check("Problem Statement and Users & Personas untouched", (ctx: Ctx): Result => {
    const t = ctx.read(SPEC) ?? "";
    const bad = ["Problem Statement", "Users & Personas"].filter((s) => norm(section(t, s)) !== norm(section(ORIG, s)));
    return [bad.length === 0, `modified: ${bad.join(", ")}`];
  })
  .check("no change-tracking in the draft body", (ctx: Ctx): Result => {
    const t = ctx.read(SPEC) ?? "";
    const hit = t.match(/^##\s+(Changes since|Revision History|Changelog)|\[Changed in v/im);
    return [!hit, `found: ${hit?.[0]}`];
  })
  .check("CHANGELOG.md untouched while draft", (ctx: Ctx): Result => {
    const ok = norm(ctx.read(LOG) ?? "") === norm(fixture("published/CHANGELOG.md"));
    return [ok, "CHANGELOG.md was modified during a draft edit"];
  })
  .build();
