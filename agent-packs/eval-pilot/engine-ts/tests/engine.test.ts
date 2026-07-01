/**
 * Unit tests for evalpilot's pure logic (no copilot binary required).
 *
 * Cover the rubric model, the metric JSONL store + regression compare,
 * discovery across layouts, and the runner registry. TS port of the Python
 * `tests/test_engine.py`.
 */

import { existsSync, mkdirSync, mkdtempSync, readFileSync, writeFileSync } from "node:fs";
import { tmpdir } from "node:os";
import * as path from "node:path";
import { afterEach, describe, expect, it } from "vitest";
import { checkJudge, rubric } from "../src/rubric.js";
import * as M from "../src/metrics.js";
import {
  discoverAgents,
  discoverSkills,
  findAgent,
} from "../src/discovery.js";
import { Workspace } from "../src/workspace.js";
import { makeRunResult, runOk, runUsable, unavailableReason } from "../src/runners/base.js";
import { getRunner } from "../src/runners/index.js";
import { collectSpecs } from "../src/collect.js";

function mkTmp(): string {
  return mkdtempSync(path.join(tmpdir(), "ep-test-"));
}

function metricsRoot(base: string): string {
  return path.join(base, "_metrics");
}

function write(p: string, text = "x"): void {
  mkdirSync(path.dirname(p), { recursive: true });
  writeFileSync(p, text, "utf-8");
}

const tmps: string[] = [];
function tmp(): string {
  const d = mkTmp();
  tmps.push(d);
  return d;
}
afterEach(() => {
  // Leave temp dirs for OS cleanup; keeps tests fast and avoids Windows locks.
  tmps.length = 0;
});

// ---- rubric -------------------------------------------------------------

describe("rubric", () => {
  it("all pass", () => {
    const r = rubric(["a", true], ["b", true, "detail"]);
    expect(r.passed).toBe(true);
    expect(r.passRate).toBe(1.0);
    r.assertPassed();
  });

  it("failure lists failed", () => {
    const r = rubric(["a", true], ["b", false, "nope"]);
    expect(r.passed).toBe(false);
    expect(r.failed.map((c) => c.name)).toEqual(["b"]);
    let msg = "";
    try {
      r.assertPassed({ logPath: "x.log" });
    } catch (e) {
      msg = (e as Error).message;
    }
    expect(msg).toContain("nope");
    expect(msg).toContain("x.log");
  });

  it("check_judge maps verdict", () => {
    const v = { passed: false, score: 0.42, reasoning: "weak" } as any;
    const c = checkJudge("semantic", v);
    expect(c.passed).toBe(false);
    expect(c.detail).toContain("0.42");
    expect(c.detail).toContain("weak");
  });

  it("bad check type throws", () => {
    expect(() => rubric(123 as any)).toThrow();
  });
});

// ---- metrics: store + baseline + regression -----------------------------

describe("metrics", () => {
  it("first record has no baseline", () => {
    const root = metricsRoot(tmp());
    const res = M.recordMetric({
      name: "lat",
      value: 100.0,
      evalId: "t",
      direction: "lower_is_better",
      metricsRoot: root,
    });
    expect(res.baseline).toBeNull();
    expect(res.delta).toBeNull();
    expect(res.regressed).toBe(false);
    const line = JSON.parse(
      readFileSync(res.history_path, "utf-8").split(/\r?\n/)[0]!,
    );
    expect(line.value).toBe(100.0);
    expect(line.name).toBe("lat");
  });

  it("last baseline + regression (lower_is_better)", () => {
    const root = metricsRoot(tmp());
    M.recordMetric({ name: "lat", value: 100, evalId: "t", direction: "lower_is_better", metricsRoot: root });
    const res = M.recordMetric({ name: "lat", value: 130, evalId: "t", direction: "lower_is_better", tolerance: 10, metricsRoot: root });
    expect(res.baseline).toBe(100.0);
    expect(res.delta).toBe(30.0);
    expect(res.regressed).toBe(true);
  });

  it("tolerance absorbs small drift", () => {
    const root = metricsRoot(tmp());
    M.recordMetric({ name: "lat", value: 100, evalId: "t", direction: "lower_is_better", metricsRoot: root });
    const res = M.recordMetric({ name: "lat", value: 105, evalId: "t", direction: "lower_is_better", tolerance: 10, metricsRoot: root });
    expect(res.regressed).toBe(false);
  });

  it("higher_is_better regression", () => {
    const root = metricsRoot(tmp());
    M.recordMetric({ name: "score", value: 0.9, evalId: "t", direction: "higher_is_better", metricsRoot: root });
    const res = M.recordMetric({ name: "score", value: 0.6, evalId: "t", direction: "higher_is_better", tolerancePct: 0.1, metricsRoot: root });
    expect(res.regressed).toBe(true);
    expect(res.delta).toBeCloseTo(-0.3, 6);
  });

  it("neutral never regresses", () => {
    const root = metricsRoot(tmp());
    M.recordMetric({ name: "n", value: 1, evalId: "t", direction: "neutral", metricsRoot: root });
    const res = M.recordMetric({ name: "n", value: 1000, evalId: "t", direction: "neutral", metricsRoot: root });
    expect(res.regressed).toBe(false);
  });

  it("rolling_mean baseline", () => {
    const root = metricsRoot(tmp());
    for (const v of [10, 20, 30])
      M.recordMetric({ name: "r", value: v, evalId: "t", direction: "higher_is_better", baselineStrategy: "rolling_mean", metricsRoot: root });
    const res = M.recordMetric({ name: "r", value: 25, evalId: "t", direction: "higher_is_better", baselineStrategy: "rolling_mean", metricsRoot: root });
    expect(res.baseline).toBeCloseTo(20.0, 6);
  });

  it("best baseline", () => {
    const root = metricsRoot(tmp());
    for (const v of [0.5, 0.8, 0.6])
      M.recordMetric({ name: "b", value: v, evalId: "t", direction: "higher_is_better", baselineStrategy: "best", metricsRoot: root });
    const res = M.recordMetric({ name: "b", value: 0.7, evalId: "t", direction: "higher_is_better", baselineStrategy: "best", metricsRoot: root });
    expect(res.baseline).toBe(0.8);
  });

  it("pinned baseline", () => {
    const res = M.recordMetric({ name: "p", value: 5, evalId: "t", baselineStrategy: "pinned", baseline: 10, direction: "higher_is_better", tolerance: 0, metricsRoot: metricsRoot(tmp()) });
    expect(res.baseline).toBe(10);
    expect(res.regressed).toBe(true);
  });

  it("assert_no_regression raises", () => {
    const root = metricsRoot(tmp());
    M.recordMetric({ name: "g", value: 100, evalId: "t", direction: "lower_is_better", metricsRoot: root });
    const res = M.recordMetric({ name: "g", value: 200, evalId: "t", direction: "lower_is_better", metricsRoot: root });
    expect(() => M.assertNoRegression(res)).toThrow();
  });

  it("summarize and iter_series", () => {
    const root = metricsRoot(tmp());
    for (const v of [1, 2, 3])
      M.recordMetric({ name: "s", value: v, evalId: "t", direction: "higher_is_better", metricsRoot: root });
    const s = M.summarize("t", "s", root);
    expect(s.count).toBe(3);
    expect(s.latest).toBe(3);
    expect(s.min).toBe(1);
    expect(s.max).toBe(3);
    const slugs = M.iterSeries(root).map(([slug]) => slug);
    expect(slugs).toEqual([M.metricSlug("t", "s")]);
  });

  it("bad direction throws", () => {
    expect(() =>
      M.recordMetric({ name: "x", value: 1, direction: "sideways", metricsRoot: metricsRoot(tmp()) }),
    ).toThrow();
  });
});

// ---- discovery ----------------------------------------------------------

describe("discovery", () => {
  it("agents and skills across layouts", () => {
    const repo = path.join(tmp(), "repo");
    mkdirSync(path.join(repo, ".git"), { recursive: true });
    write(path.join(repo, ".github", "agents", "alpha.agent.md"), "---\nname: alpha\n---\n");
    write(path.join(repo, "plugins", "p", "plugin.json"), "{}");
    write(path.join(repo, "plugins", "p", "agents", "beta.agent.md"), "---\nname: beta\n---\n");
    write(path.join(repo, "plugins", "p", "skills", "do-thing", "SKILL.md"), "---\nname: do-thing\n---\n");
    write(path.join(repo, ".github", "skills", "shared", "SKILL.md"), "---\nname: shared\n---\n");

    const agents = new Map(discoverAgents(repo).map((a) => [a.name, a]));
    expect(new Set(agents.keys())).toEqual(new Set(["alpha", "beta"]));
    expect(agents.get("beta")!.plugin_root).toBe(path.resolve(path.join(repo, "plugins", "p")));
    expect(agents.get("alpha")!.plugin_root).toBeNull();

    const skills = new Map(discoverSkills(repo).map((s) => [s.name, s]));
    expect(new Set(skills.keys())).toEqual(new Set(["do-thing", "shared"]));
    expect(skills.get("do-thing")!.plugin_root).toBe(path.resolve(path.join(repo, "plugins", "p")));
  });

  it("find_agent missing and ambiguous", () => {
    const repo = path.join(tmp(), "repo");
    mkdirSync(path.join(repo, ".git"), { recursive: true });
    expect(() => findAgent("nope", repo)).toThrow();
    write(path.join(repo, "a", "agents", "dup.agent.md"));
    write(path.join(repo, "b", "agents", "dup.agent.md"));
    expect(() => findAgent("dup", repo)).toThrow();
  });

  it("prunes noise dirs", () => {
    const repo = path.join(tmp(), "repo");
    mkdirSync(path.join(repo, ".git"), { recursive: true });
    write(path.join(repo, "node_modules", "x", "agents", "ghost.agent.md"));
    write(path.join(repo, ".github", "agents", "real.agent.md"));
    const names = new Set(discoverAgents(repo).map((a) => a.name));
    expect(names).toEqual(new Set(["real"]));
  });

  it("collectSpecs skips _templates and other noise dirs", async () => {
    const root = tmp();
    const md = "---\nname: from-real\n---\n\n# Real eval\n";
    write(path.join(root, "packs", "demo", "real.eval.md"), md);
    write(path.join(root, "_templates", "structural.eval.md"), md.replace("from-real", "from-template"));
    write(path.join(root, "_runs", "old", "stale.eval.md"), md.replace("from-real", "from-run"));
    const names = new Set((await collectSpecs(root)).map((s) => s.name));
    expect(names).toEqual(new Set(["from-real"]));
  });

  it("stage_agent copies legacy pack support dirs", () => {
    const base = tmp();
    const repo = path.join(base, "repo");
    mkdirSync(path.join(repo, ".git"), { recursive: true });
    const pack = path.join(repo, "agent-packs", "product-brief", ".github");
    write(path.join(pack, "agents", "brief-orchestrator.agent.md"), "---\nname: brief-orchestrator\n---\n");
    write(path.join(pack, "skills", "product-brief-skill", "SKILL.md"), "---\nname: product-brief-skill\n---\n");
    write(path.join(pack, "instructions", "product-brief.instructions.md"), "instructions");

    const ws = new Workspace({
      root: path.join(base, "ws"),
      logsDir: path.join(base, "_logs"),
      repoRoot: repo,
    });
    ws.stageAgent("brief-orchestrator");

    expect(existsSync(path.join(ws.root, ".github", "agents", "brief-orchestrator.agent.md"))).toBe(true);
    expect(existsSync(path.join(ws.root, ".github", "skills", "product-brief-skill", "SKILL.md"))).toBe(true);
    expect(existsSync(path.join(ws.root, ".github", "instructions", "product-brief.instructions.md"))).toBe(true);
  });
});

// ---- runner registry ----------------------------------------------------

describe("runner registry", () => {
  it("copilot runner registered", () => {
    expect(getRunner("copilot").name).toBe("copilot");
  });

  it("unknown runner raises", () => {
    expect(() => getRunner("does-not-exist")).toThrow();
  });

  it("RunResult helpers", () => {
    const r = makeRunResult({ returncode: 0, stdout: "", stderr: "", duration_seconds: 1.0, log_path: "x" });
    expect(runOk(r)).toBe(true);
    expect(runUsable(r)).toBe(true);
    expect(unavailableReason(r)).toBe("");
    const sk = makeRunResult({ returncode: 125, stdout: "", stderr: "", duration_seconds: 0.0, log_path: "x", skipped: true });
    expect(runUsable(sk)).toBe(false);
    expect(unavailableReason(sk)).toContain("not launched");
  });
});
