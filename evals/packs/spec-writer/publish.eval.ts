/**
 * Lifecycle: an explicit publish strips -draft, sets the requested SemVer and
 * Status: published, keeps IDs, and writes a Keep-a-Changelog CHANGELOG.md.
 */

import { Eval } from "evalpilot";
import { NO_INPUT, fixture, frBlocks, status, version, type Ctx, type Result } from "./spec-checks";

const SPEC = "specs/search-filters.md";
const LOG = "specs/CHANGELOG.md";

export default new Eval("spec-writer-publish", {
  target: "spec-writer",
  kind: "skill",
  tags: ["behaviour", "slow", "lifecycle"],
  timeout: 600,
})
  .summarize("Explicit publish sets 0.1.0 / published, keeps IDs, and writes CHANGELOG.md.")
  .describe("Fixture is a 0.0.1-draft spec. The user asks to publish as 0.1.0.")
  .stageSkill("spec-writer")
  .copy("fixtures/draft/search-filters.md", "specs")
  .prompt(`Publish \`${SPEC}\` as version 0.1.0.\n\n${NO_INPUT}`)
  .expectFile(LOG)
  .check("status published, version 0.1.0", (ctx: Ctx): Result => {
    const t = ctx.read(SPEC) ?? "";
    const ok = status(t) === "published" && version(t) === "0.1.0";
    return [ok, `status=${status(t)} version=${version(t)}`];
  })
  .check("no -draft suffix remains", (ctx: Ctx): Result => [!/-draft\b/.test(ctx.read(SPEC) ?? ""), "-draft still present"])
  .check("FR IDs unchanged", (ctx: Ctx): Result => {
    const now = [...frBlocks(ctx.read(SPEC) ?? "").keys()].join(",");
    const was = [...frBlocks(fixture("draft/search-filters.md")).keys()].join(",");
    return [now === was, `was ${was}, now ${now}`];
  })
  .check("CHANGELOG has a 0.1.0 entry with Added", (ctx: Ctx): Result => {
    const c = ctx.read(LOG) ?? "";
    const ok = /^##\s+\[?0\.1\.0\]?/m.test(c) && /^###\s+Added/m.test(c);
    return [ok, "missing '## [0.1.0]' or '### Added'"];
  })
  .build();
