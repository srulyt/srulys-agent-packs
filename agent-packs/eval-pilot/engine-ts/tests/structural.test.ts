/**
 * Structural (no-SUT) eval mode: `kind: none` with no `## Act` runs offline
 * against the repo tree and evaluates assertions/judges/metrics.
 */

import { mkdirSync, mkdtempSync, writeFileSync } from "node:fs";
import { tmpdir } from "node:os";
import * as path from "node:path";
import { afterEach, describe, expect, it } from "vitest";
import { Eval } from "../src/loaders/builder.js";
import { runEval } from "../src/executor.js";
import { parseMarkdownEval } from "../src/loaders/markdown.js";
import { specIsStructural, validateSpec } from "../src/spec.js";
import { PASSED, FAILED } from "../src/model.js";

function mkTmp(): string {
  return mkdtempSync(path.join(tmpdir(), "ep-struct-"));
}

const saved = process.env.EVALPILOT_REPO_ROOT;
afterEach(() => {
  if (saved === undefined) delete process.env.EVALPILOT_REPO_ROOT;
  else process.env.EVALPILOT_REPO_ROOT = saved;
});

/** Point the engine's repo-root resolution at a scratch dir with fixtures. */
function fakeRepo(files: Record<string, string>): string {
  const root = mkTmp();
  for (const [rel, text] of Object.entries(files)) {
    const p = path.join(root, rel);
    mkdirSync(path.dirname(p), { recursive: true });
    writeFileSync(p, text, "utf-8");
  }
  process.env.EVALPILOT_REPO_ROOT = root;
  return root;
}

describe("structural spec classification", () => {
  it("kind=none with no act is structural and validates without a prompt", () => {
    const spec = new Eval("struct", { kind: "none" })
      .expectFile("plugin.json")
      .build();
    expect(specIsStructural(spec)).toBe(true);
    expect(validateSpec(spec)).toEqual([]);
  });

  it("agent evals still require an act prompt", () => {
    const spec = new Eval("needs-act", { target: "a", kind: "agent" }).build();
    expect(specIsStructural(spec)).toBe(false);
    expect(validateSpec(spec).join(";")).toContain("Act");
  });

  it("markdown with no Act and kind none parses as structural", () => {
    const md = [
      "---",
      "name: struct-md",
      "kind: none",
      "---",
      "# Structural",
      "## Assert",
      "```yaml",
      "file_exists:",
      "  - plugin.json",
      "```",
      "",
    ].join("\n");
    const spec = parseMarkdownEval(md, "x.eval.md");
    expect(specIsStructural(spec)).toBe(true);
  });
});

describe("structural execution against the repo tree", () => {
  it("passes when repo-root assertions hold", async () => {
    const work = mkTmp();
    fakeRepo({ "plugin.json": '{"name":"demo"}', "README.md": "hello" });
    const spec = new Eval("struct-pass", { kind: "none" })
      .expectFile("plugin.json", "README.md")
      .expectContains("demo", { path: "plugin.json" })
      .expect("json_path", { path: "plugin.json", query: "name", equals: "demo" })
      .check("has readme", (ctx) => (ctx.read("README.md") ?? "").includes("hello"))
      .build();
    const res = await runEval(spec, { workRoot: work });
    expect(res.status).toBe(PASSED);
    expect(res.assertions.every((a) => a.passed)).toBe(true);
  });

  it("fails when a repo-root assertion is violated", async () => {
    const work = mkTmp();
    fakeRepo({ "plugin.json": "{}" });
    const spec = new Eval("struct-fail", { kind: "none" })
      .expectFile("does-not-exist.json")
      .build();
    const res = await runEval(spec, { workRoot: work });
    expect(res.status).toBe(FAILED);
  });
});
