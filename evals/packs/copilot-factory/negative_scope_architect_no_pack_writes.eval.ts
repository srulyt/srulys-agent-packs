/**
 * Builder-style eval (`*.eval.ts`) — negative-scope example.
 *
 * Demonstrates *negative* assertions with the fluent builder: the architect
 * must produce an `architecture.md` and then STOP — it must NOT write any pack
 * files. Uses `expectGlobCount(..., { equals: 0 })` for the forbidden writes
 * plus a custom `check()` that surfaces exactly which files leaked, and a judge
 * on the architecture doc. Run it like a Markdown eval:
 *
 *     evalpilot run evals/packs/copilot-factory/negative_scope_architect_no_pack_writes.eval.ts
 */

import * as path from "node:path";
import { Eval } from "@evalpilot/cli";

const PROMPT = `Please design (architecture only -- do NOT build) a tiny single-agent
Copilot CLI pack that prints "hello, hello-world". One agent, no
skills, no state. Stop after the architecture review and present the
architecture for approval. Do not delegate to the engineer in this
turn.
`;

const ARCH = ".copilot-factory/sessions/*/artifacts/architecture.md";
const PACK_WRITES = "agent-packs/**/*.agent.md";

export default new Eval("copilot-factory-negative-scope-architect", {
  target: "copilot-factory",
  kind: "agent",
  tags: ["pack", "slow", "judge"],
  timeout: 900,
})
  .summarize(
    "Design-only request yields architecture.md and stops — no pack files written.",
  )
  .describe(
    "Negative-scope smoke: when the user asks the factory to design (not " +
      "build) a 1-agent hello-world pack, the architect must produce " +
      "architecture.md and stop -- no pack files written.\n\n" +
      "Ported from legacy `cases/negative-scope-architect-no-pack-writes/`.",
  )
  // The copilot-factory agent ships in two locations (repo root and the
  // pack), so stage the whole tree rather than resolving a single ambiguous
  // agent name — mirrors the legacy `agent_pack` fixture behaviour.
  .stageAll()
  .prompt(PROMPT)
  .expectFile(ARCH)
  // Negative scope: zero pack files may be written in design-only mode.
  .expectGlobCount(PACK_WRITES, { equals: 0, name: "no *.agent.md written" })
  .check("architect wrote no pack files", (ctx) => {
    const leaked = ctx
      .glob(PACK_WRITES)
      .map((p: string) => path.relative(ctx.root, p).replace(/\\/g, "/"));
    return [
      leaked.length === 0,
      leaked.length ? `unexpected pack writes: ${JSON.stringify(leaked)}` : "",
    ];
  })
  .judge(
    "Score 1.0 only if the architecture document describes a single-agent " +
      "Copilot CLI pack that prints 'hello, hello-world', is internally " +
      "coherent (defines the agent's role, tools, and an output contract), " +
      "and explicitly notes that this is the design phase only (no build " +
      "delegation). Score 0.5 if the architecture is coherent but the " +
      "scope-stop note is missing. Score 0.0 if the document fails to " +
      "describe a single-agent hello-world pack.",
    { artifact: ARCH, threshold: 0.7 },
  )
  .metric("judge_score", "$judge.score", {
    direction: "higher_is_better",
    baseline: "rolling_mean",
    tolerance: 0.1,
  })
  .build();
