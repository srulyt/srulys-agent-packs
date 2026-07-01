/**
 * Static pack-contract gate (structural, no SUT).
 *
 * Ports the legacy pytest `evals/static/test_pack_contract.py`: runs the
 * dependency-free `scripts/lint-pack.mjs` linter once per Copilot pack and
 * fails the pack's check on any error-severity issue. Warnings (soft caps) do
 * not fail. Emits one `.check()` per pack so violations surface individually,
 * mirroring the old pytest parametrization.
 */

import * as path from "node:path";
import { Eval } from "@evalpilot/cli";
import { discoverPacks, lintPack } from "../../scripts/lint-pack.mjs";

const builder = new Eval("pack-contract", {
  kind: "none",
  tags: ["static", "structural"],
})
  .summarize("Every Copilot agent pack satisfies the static pack contract.")
  .describe(
    "Runs scripts/lint-pack.mjs per pack: each .agent.md must have well-formed " +
      "front-matter declaring the required fields (description, tools). Any " +
      "error-severity issue fails that pack's check; soft-cap warnings do not.",
  );

for (const packDir of discoverPacks()) {
  const name = path.basename(packDir);
  builder.check(`pack contract: ${name}`, () => {
    const errors = lintPack(packDir).filter((i) => i.severity === "error");
    if (errors.length) {
      return [false, `Pack contract violations:\n${errors.map((e) => e.format()).join("\n")}`];
    }
    return true;
  });
}

export default builder.build();
