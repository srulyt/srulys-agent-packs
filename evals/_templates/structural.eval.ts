/**
 * Structural eval template (no SUT). Runs offline via `evalpilot run` — no
 * copilot binary, no LLM judge. Use for packaging/conformance checks that read
 * the shipped pack files directly.
 *
 * `kind: "none"` + no `.prompt(...)` makes this a structural eval. Each
 * `.check(name, predicate)` maps to one assertion; the predicate returns `true`
 * on pass or `[false, "message"]` on failure. `ctx.root` is the repo root;
 * `ctx.read(relPath)` returns file text or null; `ctx.glob(pattern)` returns
 * sorted absolute paths.
 */

import { Eval } from "evalpilot";

type Ctx = { root: string; read(rel: string): string | null; glob(p: string): string[] };
type Result = boolean | [boolean, string];

export default new Eval("my-structural-eval", {
  kind: "none",
  tags: ["pack", "structural"],
})
  .summarize("One line describing what conformance this guards.")
  .describe("What the checks below verify and why.")
  .check("manifest declares the expected shape", (ctx: Ctx): Result => {
    const text = ctx.read("agent-packs/my-pack/plugin.json");
    if (text === null) return [false, "missing plugin.json"];
    const m = JSON.parse(text);
    if (m.name !== "my-pack") return [false, `unexpected name ${JSON.stringify(m.name)}`];
    return true;
  })
  .build();
