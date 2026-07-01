/**
 * Unit tests for the evalpilot DSL layer (no copilot binary required).
 *
 * Covers the modeled result round-trip, the Markdown loader, the fluent
 * builder, the assertion registry, the executor end-to-end (via the offline
 * mock runner), and the three renderers. TS port of Python `tests/test_dsl.py`.
 */

import { mkdtempSync, writeFileSync } from "node:fs";
import { tmpdir } from "node:os";
import * as path from "node:path";
import { afterEach, beforeEach, describe, expect, it } from "vitest";
import { Eval } from "../src/loaders/builder.js";
import {
  loadMarkdownEval,
  parseMarkdownEval,
  EvalParseError,
} from "../src/loaders/markdown.js";
import { runEval, runSpecs } from "../src/executor.js";
import {
  FAILED,
  PASSED,
  makeAssertionResult,
  makeEvalResult,
  makeEvalRunReport,
  makeJudgeResult,
  makeMetricRecord,
  reportOk,
  runReportFromDict,
} from "../src/model.js";
import { AssertContext, assertion, runAssertion } from "../src/assertions.js";
import { makeAssertionSpec, specIsStub, specIsImplemented, validateSpec, type EvalSpec } from "../src/spec.js";
import { renderHtml, renderTerminal, toJsonStr } from "../src/render/index.js";
import { readJson, writeJson } from "../src/render/json.js";
import { configureMock, resetMock } from "../src/runners/mock.js";
import { getRunner } from "../src/runners/index.js";

function tmp(): string {
  return mkdtempSync(path.join(tmpdir(), "ep-dsl-"));
}

// ---- model round-trip ---------------------------------------------------

describe("model", () => {
  it("JSON round-trip", () => {
    const result = makeEvalResult({
      name: "demo",
      status: PASSED,
      duration_seconds: 1.5,
      assertions: [makeAssertionResult({ kind: "contains", name: "a", passed: true })],
      judges: [makeJudgeResult({ name: "judge", score: 0.9, threshold: 0.7, passed: true })],
      metrics: [makeMetricRecord({ name: "judge_score", value: 0.9 })],
    });
    const report = makeEvalRunReport({ run_id: "r1", results: [result] });
    expect(reportOk(report)).toBe(true);

    const text = toJsonStr(report);
    const back = runReportFromDict(JSON.parse(text));
    expect(back.run_id).toBe("r1");
    expect(back.results[0]!.name).toBe("demo");
    expect(back.results[0]!.assertions[0]!.kind).toBe("contains");
    expect(back.results[0]!.judges[0]!.score).toBe(0.9);
  });
});

// ---- markdown loader ----------------------------------------------------

const MD = `---
name: demo-eval
target: demo-agent
kind: agent
tags: [smoke, judge]
timeout: 42
---

# Title
> the description line

## Act
\`\`\`prompt
do the thing
\`\`\`

## Assert
\`\`\`yaml
stdout_contains:
  - { text: "hello" }
judge:
  threshold: 0.6
  criteria: |
    Be strict.
metrics:
  - { name: score, value: $judge.score, direction: higher_is_better,
      baseline: rolling_mean, tolerance: 0.1 }
\`\`\`
`;

const MD_DESC = `---
name: desc-eval
target: demo-agent
kind: agent
tags: [smoke]
---

# Human Title
> short summary line

## Description
First paragraph explaining the scenario in plain English.

Second paragraph with more detail about the expected outcome.

## Act
\`\`\`prompt
do the thing
\`\`\`

## Assert
\`\`\`yaml
stdout_contains:
  - { text: "hello" }
\`\`\`
`;

describe("markdown loader", () => {
  it("parses all sections", () => {
    const spec = parseMarkdownEval(MD);
    expect(spec.name).toBe("demo-eval");
    expect(spec.kind).toBe("agent");
    expect(spec.timeout).toBe(42);
    expect(spec.tags).toContain("smoke");
    expect(spec.act!.prompt.trim()).toBe("do the thing");
    expect(spec.assertions.some((a) => a.kind === "stdout_contains")).toBe(true);
    expect(spec.judges[0]!.threshold).toBe(0.6);
    expect(spec.metrics[0]!.value).toBe("$judge.score");
    expect(validateSpec(spec)).toEqual([]);
  });

  it("empty setup is valid", () => {
    const md = MD.replace("## Act", "## Setup\n```yaml\n# only comments\n```\n\n## Act");
    const spec = parseMarkdownEval(md);
    expect(validateSpec(spec)).toEqual([]);
  });

  it("bad yaml raises", () => {
    const bad = MD.replace("stdout_contains:", "stdout_contains: : :");
    expect(() => parseMarkdownEval(bad)).toThrow(EvalParseError);
  });

  it("description and summary", () => {
    const spec = parseMarkdownEval(MD_DESC);
    expect(spec.summary).toBe("short summary line");
    expect(spec.description.startsWith("First paragraph")).toBe(true);
    expect(spec.description).toContain("Second paragraph");
    expect(spec.description).not.toContain("short summary line");
    expect(validateSpec(spec)).toEqual([]);
  });

  it("frontmatter summary overrides blockquote", () => {
    const md = MD_DESC.replace("kind: agent\n", "kind: agent\nsummary: from frontmatter\n");
    const spec = parseMarkdownEval(md);
    expect(spec.summary).toBe("from frontmatter");
  });

  it("stub detection and lint", () => {
    const stubMd = `---
name: stub-eval
target: demo-agent
kind: agent
---

# Stub
> a described-but-unimplemented eval

## Description
We want to check that the agent refuses unsafe requests. Not implemented yet.
`;
    const spec = parseMarkdownEval(stubMd);
    expect(specIsStub(spec)).toBe(true);
    expect(specIsImplemented(spec)).toBe(false);
    expect(specIsStub(parseMarkdownEval(MD_DESC))).toBe(false);
  });

  it("load from disk", () => {
    const dir = tmp();
    const file = path.join(dir, "x.eval.md");
    writeFileSync(file, MD, "utf-8");
    const spec = loadMarkdownEval(file);
    expect(spec.name).toBe("demo-eval");
    expect(spec.spec_path).toBe(file);
  });
});

// ---- builder ------------------------------------------------------------

describe("builder", () => {
  it("summary and describe", () => {
    const spec = new Eval("b", { target: "a", kind: "agent" })
      .summarize("one liner")
      .describe("the long form")
      .prompt("go")
      .expectStdout("x")
      .build();
    expect(spec.summary).toBe("one liner");
    expect(spec.description).toBe("the long form");
  });

  it("matches markdown shape", () => {
    const spec = new Eval("demo-eval", { target: "demo-agent", kind: "agent", tags: ["smoke", "judge"], timeout: 42 })
      .describe("the description line")
      .prompt("do the thing")
      .expectStdout("hello")
      .judge("Be strict.", { threshold: 0.6 })
      .metric("score", "$judge.score", { direction: "higher_is_better", baseline: "rolling_mean", tolerance: 0.1 })
      .build();
    expect(spec.act!.prompt.trim()).toBe("do the thing");
    expect(spec.judges[0]!.threshold).toBe(0.6);
    expect(spec.metrics[0]!.baseline_strategy).toBe("rolling_mean");
    expect(validateSpec(spec)).toEqual([]);
  });
});

// ---- assertion registry -------------------------------------------------

describe("assertions", () => {
  it("custom assertion registers and runs", () => {
    assertion("two_lines_min")((ctx, _args) => {
      const n = ctx.stdout.split(/\r?\n/).length;
      return makeAssertionResult({ kind: "two_lines_min", name: "two_lines_min", passed: n >= 2, detail: `lines=${n}` });
    });
    const ctx = new AssertContext({ root: ".", stdout: "a\nb\nc", stderr: "" });
    const res = runAssertion(makeAssertionSpec({ kind: "two_lines_min" }), ctx);
    expect(res.passed).toBe(true);
  });

  it("json_empty assertion", () => {
    const dir = tmp();
    writeFileSync(path.join(dir, "state.json"), JSON.stringify({ mcps_detected: [], count: 3 }), "utf-8");
    const ctx = new AssertContext({ root: dir });
    const ok = runAssertion(makeAssertionSpec({ kind: "json_empty", args: { path: "state.json", query: "mcps_detected" } }), ctx);
    expect(ok.passed).toBe(true);
    const absent = runAssertion(makeAssertionSpec({ kind: "json_empty", args: { path: "state.json", query: "missing" } }), ctx);
    expect(absent.passed).toBe(true);
    const nonempty = runAssertion(makeAssertionSpec({ kind: "json_empty", args: { path: "state.json", query: "count" } }), ctx);
    expect(nonempty.passed).toBe(false);
  });

  it("section-scoped assertions", () => {
    const dir = tmp();
    const spec =
      "## Problem Statement\n" +
      "The rotation is drowning in pages.\n\n" +
      "## Solution Summary\n" +
      "A dashboard showing SLO state per service.\n";
    writeFileSync(path.join(dir, "spec.md"), spec, "utf-8");
    const ctx = new AssertContext({ root: dir });
    const isolated = runAssertion(makeAssertionSpec({ kind: "section_not_contains", args: { path: "spec.md", section: "Solution Summary", text: "drowning" } }), ctx);
    expect(isolated.passed).toBe(true);
    const present = runAssertion(makeAssertionSpec({ kind: "section_contains", args: { path: "spec.md", section: "Solution Summary", text: "dashboard" } }), ctx);
    expect(present.passed).toBe(true);
    const leak = runAssertion(makeAssertionSpec({ kind: "section_not_contains", args: { path: "spec.md", section: "Problem Statement", text: "drowning" } }), ctx);
    expect(leak.passed).toBe(false);
  });
});

// ---- executor end-to-end (mock runner) ----------------------------------

describe("executor (mock runner)", () => {
  beforeEach(() => {
    resetMock();
    process.env.EVALPILOT_METRICS_ROOT = path.join(tmp(), "_metrics");
  });
  afterEach(() => {
    resetMock();
    delete process.env.EVALPILOT_METRICS_ROOT;
  });

  function nostageSpec(): EvalSpec {
    return new Eval("nostage", { kind: "none", tags: ["smoke"] })
      .prompt("say hi")
      .expectStdout("STATUS=ok")
      .metric("out_chars", "$stdout.chars", { direction: "higher_is_better", baseline: "last" })
      .build();
  }

  it("pass path", async () => {
    configureMock({ stdout: "hello STATUS=ok" });
    const result = await runEval(nostageSpec(), { workRoot: path.join(tmp(), "_runs"), runner: getRunner("mock") });
    expect(result.status).toBe(PASSED);
    expect(result.assertions[0]!.passed).toBe(true);
    expect(result.metrics[0]!.value).toBe("hello STATUS=ok".length);
  });

  it("fail path", async () => {
    configureMock({ stdout: "nothing useful here" });
    const result = await runEval(nostageSpec(), { workRoot: path.join(tmp(), "_runs"), runner: getRunner("mock") });
    expect(result.status).toBe(FAILED);
  });

  it("run_specs and renderers", async () => {
    configureMock({ stdout: "hello STATUS=ok" });
    const report = await runSpecs([nostageSpec()], { workRoot: path.join(tmp(), "_runs"), runner: getRunner("mock") });
    expect(reportOk(report)).toBe(true);

    const dir = tmp();
    const jpath = writeJson(report, path.join(dir, "report.json"));
    expect(reportOk(readJson(jpath))).toBe(true);

    const term = renderTerminal(report);
    expect(term).toContain("nostage");
    const html = renderHtml(report);
    expect(html.toLowerCase()).toContain("<html");
    expect(html).toContain("nostage");
  });
});
