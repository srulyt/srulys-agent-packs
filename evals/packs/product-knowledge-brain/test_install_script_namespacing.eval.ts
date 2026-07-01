/**
 * Structural install-script namespacing for Product Knowledge Brain.
 *
 * No SUT (kind: none) — reads the shipped reference docs directly and asserts
 * namespace-at-install, receipt, and uninstall-on-change requirements. Runs
 * offline via `evalpilot run` (no copilot binary, no LLM judge).
 *
 * Ported from the legacy pytest `test_install_script_namespacing.py`.
 */

import { Eval } from "@evalpilot/cli";

const INDEXING_REFS =
  "agent-packs/product-knowledge-brain/skills/knowledge-indexing/references";
const HARNESS_DOC = `${INDEXING_REFS}/harness-skills-dir.md`;
const MANIFEST_DOC = `${INDEXING_REFS}/removed-skills-manifest.md`;

type Ctx = {
  read(rel: string): string | null;
};
type Result = boolean | [boolean, string];

export default new Eval("product-knowledge-brain-install-namespacing", {
  kind: "none",
  tags: ["pack", "structural"],
})
  .summarize(
    "Product Knowledge Brain install-script references encode namespace-at-" +
      "install, receipts, and uninstall-on-change.",
  )
  .describe(
    "Structural conformance (no SUT): harness-skills-dir.md and " +
      "removed-skills-manifest.md must document and implement install " +
      "namespacing, receipt schema, scoped deletion, resolution order, and " +
      "non-zero fallback.",
  )
  .check("install script doc namespaces at install with receipt", (ctx: Ctx): Result => {
    const text = ctx.read(HARNESS_DOC);
    if (text === null) return [false, `missing install-script reference: ${HARNESS_DOC}`];

    if (!text.includes("$NS-$bare") && !text.includes("$NS-$($bare)")) {
      return [
        false,
        "the .sh skeleton must compute the installed name as <NS>-<bare> when " +
          "copying a bare source dir into the harness dir",
      ];
    }
    if (!text.includes('"$NS-$bare"') && !text.includes("$NS-$bare")) {
      return [false, "expected the sh script to namespace the destination dir on copy"];
    }
    if (!text.includes('"$NS-$bare"') && !text.includes('$instName = "$NS-$bare"')) {
      return [false, 'the .ps1 skeleton must compute $instName = "$NS-$bare" on copy'];
    }
    if (!/name:\s*\$installed/.test(text) && !text.includes("name: $instName")) {
      return [
        false,
        "the install script must rewrite the copied SKILL.md 'name:' line to " +
          "equal the namespaced destination dir",
      ];
    }

    if (!text.includes("installed-skills.json")) {
      return [false, "the install script must maintain an installed-skills.json receipt"];
    }
    for (const token of ["source_bare_name", "installed_name"]) {
      if (!text.includes(token)) {
        return [false, `the receipt must record '${token}' (source->installed mapping)`];
      }
    }

    const low = text.toLowerCase();
    if (!low.includes("uninstall") || !low.includes("receipt")) {
      return [false, "the doc must describe uninstall-on-change driven by the receipt diff"];
    }
    if (!text.includes('"$NS"-*')) {
      return [false, 'the .sh skeleton must scope deletions to names starting with "$NS"-'];
    }
    if (!text.includes('"$NS-*"') && !text.includes('-like "$NS-*"')) {
      return [false, 'the .ps1 skeleton must scope deletions to names matching "$NS-*"'];
    }

    for (const rule of ["explicit-arg", "env-override", "repo-github", "user-copilot", "none"]) {
      if (!text.includes(rule)) return [false, `harness-dir resolution rule '${rule}' missing`];
    }
    if (!text.includes("exit 3")) {
      return [false, "no-harness fallback must exit non-zero (exit 3)"];
    }
    return true;
  })
  .check("receipt schema documented in manifest ref", (ctx: Ctx): Result => {
    const text = ctx.read(MANIFEST_DOC);
    if (text === null) return [false, `missing manifest reference: ${MANIFEST_DOC}`];

    if (!text.includes("installed-skills.json")) {
      return [
        false,
        "removed-skills-manifest.md must document the installed-skills.json receipt",
      ];
    }
    for (const token of ["kb_namespace", "harness_dir", "source_bare_name", "installed_name"]) {
      if (!text.includes(token)) return [false, `receipt schema must document '${token}'`];
    }

    const low = text.toLowerCase();
    if (!low.includes("uninstall-on-change")) {
      return [false, "the doc must describe uninstall-on-change"];
    }
    if (!low.includes("never touch") && !low.includes("never touches")) {
      return [false, "the doc must state deletions never touch another KB's skills"];
    }
    if (!low.includes("bare")) {
      return [false, "removed-skills.json names must be documented as bare (pivot)"];
    }
    return true;
  })
  .build();
