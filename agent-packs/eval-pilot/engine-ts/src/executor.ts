/**
 * Standalone executor — runs an {@link EvalSpec} and produces the result model.
 *
 * {@link runEval} performs arrange → act → assert for one spec and returns an
 * {@link EvalResult}; {@link runSpecs} fans a batch out (optionally with bounded
 * concurrency) into an {@link EvalRunReport}. Everything downstream reads that
 * model.
 */

import { existsSync } from "node:fs";
import * as path from "node:path";
import fg from "fast-glob";
import { AssertContext, runAssertion } from "./assertions.js";
import { findEvalRoot, findRepoRoot } from "./config.js";
import { JudgeError, judge as judgeCall } from "./judge.js";
import * as metricsMod from "./metrics.js";
import {
  ERROR,
  FAILED,
  makeAssertionResult,
  makeEvalResult,
  makeJudgeResult,
  makeMetricRecord,
  metricRecordFromResult,
  PASSED,
  SKIPPED,
  checkPassed,
  checkTotal,
  type EvalResult,
  type EvalRunReport,
  type JudgeResult,
  type MetricRecord,
} from "./model.js";
import { getRunner } from "./runners/index.js";
import { makeRunResult, runOk, runUsable, unavailableReason, type RunResult, type SUTRunner } from "./runners/base.js";
import { AGENT, SKILL, specIsStructural, validateSpec, type EvalSpec, type MetricSpec } from "./spec.js";
import { Workspace } from "./workspace.js";

function nowIso(): string {
  return new Date().toISOString().replace(/\.\d{3}Z$/, "+00:00");
}

function slug(text: string): string {
  return text.replace(/[^A-Za-z0-9._-]+/g, "-").replace(/^-+|-+$/g, "") || "eval";
}

function hrSeconds(t0: bigint): number {
  return Number(process.hrtime.bigint() - t0) / 1e9;
}

// ---- single eval --------------------------------------------------------

export interface RunEvalOptions {
  workRoot?: string;
  runner?: SUTRunner;
}

/** Execute one spec and return its {@link EvalResult}. */
export async function runEval(
  spec: EvalSpec,
  opts: RunEvalOptions = {},
): Promise<EvalResult> {
  const startedAt = nowIso();
  const t0 = process.hrtime.bigint();
  const runner = opts.runner ?? getRunner();
  const workRoot =
    opts.workRoot ?? path.join(findEvalRoot(), "_runs", "scratch");
  const s = slug(spec.name);
  const wsRoot = path.join(workRoot, s, "ws");
  const logsDir = path.join(workRoot, s, "_logs");

  const base = resultShell(spec, startedAt);

  const problems = validateSpec(spec);
  if (problems.length) {
    base.status = ERROR;
    base.error = "invalid spec: " + problems.join("; ");
    base.duration_seconds = hrSeconds(t0);
    return base;
  }

  if (spec.tags.includes("skip")) {
    base.status = SKIPPED;
    base.skip_reason = "eval tagged 'skip'";
    base.duration_seconds = hrSeconds(t0);
    return base;
  }

  // Structural eval: no SUT. Evaluate assertions/judges/metrics against the
  // repo tree directly. Runs offline (no runner, no staging).
  if (specIsStructural(spec)) {
    try {
      const ctx = new AssertContext({ root: findRepoRoot() });
      const synthetic = makeRunResult({
        returncode: 0,
        stdout: "",
        stderr: "",
        duration_seconds: hrSeconds(t0),
        log_path: "",
      });
      base.assertions = spec.assertions.map((a) => runAssertion(a, ctx));
      base.judges = await runJudges(spec, ctx, logsDir);
      base.metrics = recordMetrics(spec, base, synthetic);
      base.status = finalStatusStructural(base);
    } catch (exc) {
      base.status = ERROR;
      const err = exc as Error;
      base.error = `${err.name}: ${err.message}\n${err.stack ?? ""}`;
    }
    base.duration_seconds = hrSeconds(t0);
    return base;
  }

  if (!runner.available()) {
    base.status = SKIPPED;
    base.skip_reason =
      `SUT runner '${runner.name}' unavailable (set COPILOT_BIN / PATH, ` +
      `or use EVALPILOT_RUNNER=mock)`;
    base.duration_seconds = hrSeconds(t0);
    return base;
  }

  try {
    const ws = new Workspace({ root: wsRoot, logsDir, runner });
    arrange(spec, ws);
    const result = await act(spec, ws);
    base.log_path = result.log_path;

    if (!runUsable(result)) {
      base.status = SKIPPED;
      base.skip_reason = unavailableReason(result);
      base.duration_seconds = hrSeconds(t0);
      return base;
    }

    if (!runOk(result)) {
      base.status = FAILED;
      base.error = `SUT exited ${result.returncode}; see ${result.log_path}`;
      // Still evaluate assertions to give a full picture.
    }
    const ctx = new AssertContext({
      root: ws.root,
      stdout: result.stdout,
      stderr: result.stderr,
    });
    base.assertions = spec.assertions.map((a) => runAssertion(a, ctx));
    base.judges = await runJudges(spec, ctx, logsDir);
    base.metrics = recordMetrics(spec, base, result);
    base.status = finalStatus(base, result);
  } catch (exc) {
    base.status = ERROR;
    const err = exc as Error;
    base.error = `${err.name}: ${err.message}\n${err.stack ?? ""}`;
  }

  base.duration_seconds = hrSeconds(t0);
  return base;
}

export interface RunSpecsOptions {
  workRoot?: string;
  parallel?: number;
  runner?: SUTRunner;
}

/** Execute a batch of specs into an {@link EvalRunReport}. */
export async function runSpecs(
  specs: EvalSpec[],
  opts: RunSpecsOptions = {},
): Promise<EvalRunReport> {
  const runId = new Date()
    .toISOString()
    .replace(/\.\d{3}Z$/, "")
    .replace(/:/g, "-");
  const workRoot = opts.workRoot ?? path.join(findEvalRoot(), "_runs", runId);
  const startedAt = nowIso();
  const t0 = process.hrtime.bigint();
  const parallel = opts.parallel ?? 1;

  const one = (sp: EvalSpec): Promise<EvalResult> =>
    runEval(sp, { workRoot, runner: opts.runner });

  let results: EvalResult[];
  if (parallel > 1 && specs.length > 1) {
    results = await runPool(specs, parallel, one);
  } else {
    results = [];
    for (const sp of specs) results.push(await one(sp));
  }

  return {
    run_id: runId,
    started_at: startedAt,
    finished_at: nowIso(),
    duration_seconds: hrSeconds(t0),
    results,
    git_sha: metricsMod.gitSha(),
  };
}

/** Bounded-concurrency map preserving input order. */
async function runPool<T, R>(
  items: T[],
  limit: number,
  fn: (item: T) => Promise<R>,
): Promise<R[]> {
  const results = new Array<R>(items.length);
  let next = 0;
  async function worker(): Promise<void> {
    while (true) {
      const i = next++;
      if (i >= items.length) return;
      results[i] = await fn(items[i]!);
    }
  }
  const workers = Array.from({ length: Math.min(limit, items.length) }, () =>
    worker(),
  );
  await Promise.all(workers);
  return results;
}

// ---- phases -------------------------------------------------------------

function resultShell(spec: EvalSpec, startedAt: string): EvalResult {
  return makeEvalResult({
    name: spec.name,
    status: PASSED,
    target: spec.target,
    kind: spec.kind,
    summary: spec.summary,
    description: spec.description,
    tags: [...spec.tags],
    prompt: spec.act ? spec.act.prompt : null,
    spec_path: spec.spec_path,
    started_at: startedAt,
  });
}

function arrange(spec: EvalSpec, ws: Workspace): void {
  const stage = spec.setup.stage;
  if (stage.all) ws.stageAll();
  if (stage.agent) ws.stageAgent(stage.agent, { includeSkills: stage.include_skills });
  if (stage.skill) ws.stageSkill(stage.skill);
  const baseDir = spec.base_dir;
  for (const fc of spec.setup.files) {
    copyFixture(baseDir, fc.copy, fc.dest, ws);
  }
}

function copyFixture(
  baseDir: string | null,
  pattern: string,
  dest: string,
  ws: Workspace,
): void {
  if (baseDir === null) {
    if (existsSync(pattern)) ws.stageFiles(pattern, dest);
    return;
  }
  let matches = fg
    .sync(pattern, { cwd: baseDir, dot: true, absolute: true })
    .sort();
  if (!matches.length && existsSync(path.join(baseDir, pattern))) {
    matches = [path.join(baseDir, pattern)];
  }
  for (const m of matches) ws.stageFiles(m, dest);
}

async function act(spec: EvalSpec, ws: Workspace): Promise<RunResult> {
  const a = spec.act!;
  const timeout = a.timeout !== null ? a.timeout : spec.timeout;
  const skill = a.skill || (spec.kind === SKILL ? spec.target : null);
  if (skill) {
    return ws.runSkill(skill, a.prompt, { timeout });
  }
  const agent = a.agent || (spec.kind === AGENT ? spec.target : null);
  return ws.runAgent(a.prompt, { agent, timeout });
}

async function runJudges(
  spec: EvalSpec,
  ctx: AssertContext,
  logsDir: string,
): Promise<JudgeResult[]> {
  const out: JudgeResult[] = [];
  for (let i = 0; i < spec.judges.length; i++) {
    const js = spec.judges[i]!;
    const artifact = js.artifact ? ctx.read(js.artifact) : ctx.stdout;
    if (artifact === null) {
      out.push(
        makeJudgeResult({
          name: js.name,
          passed: false,
          score: 0.0,
          threshold: js.threshold,
          reasoning: `judge artifact not found: ${js.artifact}`,
        }),
      );
      continue;
    }
    try {
      const verdict = await judgeCall({
        artifact,
        criteria: js.criteria,
        threshold: js.threshold,
        golden: js.golden,
        logDir: path.join(logsDir, `judge-${i}-${slug(js.name)}`),
      });
      out.push(
        makeJudgeResult({
          name: js.name,
          passed: verdict.passed,
          score: verdict.score,
          threshold: js.threshold,
          reasoning: verdict.reasoning,
          evidence: [...verdict.evidence],
        }),
      );
    } catch (exc) {
      if (exc instanceof JudgeError) {
        out.push(
          makeJudgeResult({
            name: js.name,
            passed: false,
            score: 0.0,
            threshold: js.threshold,
            reasoning: `judge error: ${exc.message}`,
          }),
        );
      } else {
        throw exc;
      }
    }
  }
  return out;
}

function recordMetrics(
  spec: EvalSpec,
  base: EvalResult,
  result: RunResult,
): MetricRecord[] {
  const out: MetricRecord[] = [];
  for (const ms of spec.metrics) {
    let value: number;
    try {
      value = resolveValue(ms.value, base, result);
    } catch (exc) {
      base.assertions.push(
        makeAssertionResult({
          kind: "metric",
          name: `metric:${ms.name}`,
          passed: false,
          detail: `could not resolve value ${JSON.stringify(ms.value)}: ${
            (exc as Error).message
          }`,
        }),
      );
      continue;
    }
    const mr = metricsMod.recordMetric({
      name: ms.name,
      value,
      evalId: slug(spec.name),
      direction: ms.direction,
      unit: ms.unit,
      baselineStrategy: ms.baseline_strategy,
      baseline: ms.baseline,
      window: ms.window,
      tolerance: ms.tolerance,
      tolerancePct: ms.tolerance_pct,
    });
    out.push(metricRecordFromResult(mr, ms.gate));
  }
  return out;
}

interface MetricContext {
  judges: Record<string, number>;
  duration: number;
  stdout: string;
  result: RunResult;
  assertions: EvalResult["assertions"];
}

function resolveValue(
  value: MetricSpec["value"],
  base: EvalResult,
  result: RunResult,
): number {
  if (typeof value === "function") {
    const mctx: MetricContext = {
      judges: Object.fromEntries(base.judges.map((j) => [j.name, j.score])),
      duration: result.duration_seconds,
      stdout: result.stdout,
      result,
      assertions: base.assertions,
    };
    return Number(value(mctx));
  }
  if (typeof value === "number") return value;
  if (typeof value === "string" && value.startsWith("$")) {
    return resolveRef(value, base, result);
  }
  return Number(value);
}

function resolveRef(ref: string, base: EvalResult, result: RunResult): number {
  const parts = ref.slice(1).split(".");
  const head = parts[0];
  if (head === "judge") {
    if (parts.length === 2 && parts[1] === "score") return firstJudgeScore(base);
    if (parts.length === 3 && parts[2] === "score") {
      return namedJudgeScore(base, parts[1]!);
    }
    throw new Error(`bad judge ref ${JSON.stringify(ref)}`);
  }
  if (head === "duration") return result.duration_seconds;
  if (head === "stdout") {
    const metric = parts.length > 1 ? parts[1] : "chars";
    const text = result.stdout;
    const lookup: Record<string, number> = {
      words: text.split(/\s+/).filter(Boolean).length,
      chars: text.length,
      lines: text.split(/\r?\n/).length,
    };
    const v = lookup[metric!];
    if (v === undefined) throw new Error(`unknown metric ref ${JSON.stringify(ref)}`);
    return v;
  }
  if (head === "assertions" || head === "checks") {
    const total = head === "checks" ? checkTotal(base) : base.assertions.length;
    const passed =
      head === "checks"
        ? checkPassed(base)
        : base.assertions.filter((a) => a.passed).length;
    return total ? passed / total : 1.0;
  }
  throw new Error(`unknown metric ref ${JSON.stringify(ref)}`);
}

function firstJudgeScore(base: EvalResult): number {
  if (!base.judges.length) throw new Error("$judge.score used but no judge ran");
  return base.judges[0]!.score;
}

function namedJudgeScore(base: EvalResult, name: string): number {
  for (const j of base.judges) if (j.name === name) return j.score;
  throw new Error(`no judge named ${JSON.stringify(name)}`);
}

function finalStatus(base: EvalResult, result: RunResult): EvalResult["status"] {
  if (!runOk(result)) return FAILED;
  if (base.assertions.some((a) => !a.passed)) return FAILED;
  if (base.judges.some((j) => !j.passed)) return FAILED;
  if (base.metrics.some((m) => m.gated && m.regressed)) return FAILED;
  return PASSED;
}

/** Status for a structural (no-SUT) eval — no run to check. */
function finalStatusStructural(base: EvalResult): EvalResult["status"] {
  if (base.assertions.some((a) => !a.passed)) return FAILED;
  if (base.judges.some((j) => !j.passed)) return FAILED;
  if (base.metrics.some((m) => m.gated && m.regressed)) return FAILED;
  return PASSED;
}
