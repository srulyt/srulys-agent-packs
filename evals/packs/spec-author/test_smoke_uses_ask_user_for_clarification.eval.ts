/**
 * Structural ask_user clarification conformance for spec-author.
 *
 * No SUT (kind: none) — reads the shipped orchestrator prompt directly and
 * asserts that user-facing clarification prompts use the built-in `ask_user`
 * tool. Runs offline via `evalpilot run` (no copilot binary, no LLM judge).
 *
 * Ported from the legacy pytest
 * `test_smoke_uses_ask_user_for_clarification.py`.
 */

import { Eval } from "evalpilot";

const ORCHESTRATOR =
  "agent-packs/spec-author/.github/agents/spec-author.agent.md";

type Ctx = {
  read(rel: string): string | null;
};
type Result = boolean | [boolean, string];

function normalise(text: string): string {
  return text.split(/\s+/).filter(Boolean).join(" ");
}

function pyRepr(text: string): string {
  return `'${text.replace(/\\/g, "\\\\").replace(/'/g, "\\'")}'`;
}

function assertProseNotContains(text: string, needle: string, extra = ""): Result {
  const normText = normalise(text);
  const normNeedle = normalise(needle);
  if (!normText.includes(normNeedle)) return true;
  const prefix = extra ? `${extra}\n` : "";
  return [
    false,
    `${prefix}prose substring unexpectedly present (after whitespace normalisation):` +
      `\n  needle: ${pyRepr(normNeedle)}`,
  ];
}

export default new Eval("spec-author-ask-user-clarification", {
  kind: "none",
  tags: ["pack", "structural"],
})
  .summarize(
    "spec-author orchestrator uses ask_user for user-facing clarification prompts.",
  )
  .describe(
    "Structural conformance (no SUT): orchestrator prompt contains ask_user, " +
      "documents ask conventions, covers Stop 0/V/A/B sections, and omits the " +
      "legacy verbatim KIND reply prompt.",
  )
  .check("orchestrator uses ask user for clarifications", (ctx: Ctx): Result => {
    const text = ctx.read(ORCHESTRATOR);
    if (text === null) {
      return [
        false,
        `orchestrator prompt not found at ${ORCHESTRATOR}; ` +
          "cannot run static ask_user adoption check",
      ];
    }

    if (!text.includes("ask_user(")) {
      return [
        false,
        "spec-author orchestrator must surface user-facing prompts " +
          "via the built-in `ask_user` tool (factory standard, req #3)",
      ];
    }
    if (!text.includes("## How to Ask the User")) {
      return [
        false,
        "orchestrator must include a `## How to Ask the User` " +
          "conventions section documenting choices vs. freeform usage",
      ];
    }

    const section = (heading: string): string => {
      const idx = text.indexOf(heading);
      if (idx < 0) return "";
      const rest = text.slice(idx + heading.length);
      const nextH2 = rest.indexOf("\n## ");
      return nextH2 < 0 ? rest : rest.slice(0, nextH2);
    };

    const stopSections: Record<string, string> = {
      "Stop 0": "## Output Location & Spec-Kind Intake (Stop 0 — runs before context-discovery)",
      "Stop V": "## Stop V — Mode Decision",
      "Stop A": "## Stop A Protocol",
      "Stop B": "## Stop B Protocol",
    };

    for (const [label, heading] of Object.entries(stopSections)) {
      let sec = section(heading);
      if (!sec && label === "Stop 0") {
        const idx = text.indexOf("### Resolving `output_path`");
        if (idx >= 0) sec = text.slice(idx, idx + 4000);
      }
      if (!sec.includes("ask_user(")) {
        return [
          false,
          `${label} section must surface its user prompt via ` +
            "`ask_user(...)` (factory standard, req #3); " +
            `heading searched: ${pyRepr(heading)}`,
        ];
      }
    }

    return assertProseNotContains(
      text,
      "Reply with `KIND: product`, `KIND: technical`, or `KIND: mixed`",
      "legacy verbatim 'Reply with KIND:' Stop 0 prompt must be " +
        "replaced by an ask_user(choices=[product, technical, mixed]) call",
    );
  })
  .build();
