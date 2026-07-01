/**
 * Numeric metric results with JSONL history and trend/regression compare.
 *
 * Each recorded value is appended as one JSON line to a **committed** history
 * file: `<eval_root>/_metrics/<metric-slug>/history.jsonl`.
 *
 * Recording a metric also **compares it to a baseline** and flags regressions.
 * Baseline strategies: "last", "rolling_mean", "best", "pinned".
 * Directions: "higher_is_better", "lower_is_better", "neutral".
 */

import { spawnSync } from "node:child_process";
import {
  appendFileSync,
  existsSync,
  mkdirSync,
  readdirSync,
  readFileSync,
  statSync,
} from "node:fs";
import * as path from "node:path";
import { randomUUID } from "node:crypto";
import { findMetricsRoot } from "./config.js";

const DIRECTIONS = new Set(["higher_is_better", "lower_is_better", "neutral"]);

// Process-wide run id so every metric recorded in one run shares it.
let RUN_ID: string | null = null;

function nowIso(): string {
  return new Date().toISOString().replace(/\.\d{3}Z$/, "+00:00");
}

/** Return a stable id for the current process/run (or `EVALPILOT_RUN_ID`). */
export function runId(): string {
  if (RUN_ID === null) {
    const env = process.env.EVALPILOT_RUN_ID;
    if (env) {
      RUN_ID = env;
    } else {
      const now = new Date();
      const stamp =
        now.toISOString().replace(/[-:]/g, "").replace(/\.\d{3}Z$/, "");
      RUN_ID = `${stamp}-${randomUUID().replace(/-/g, "").slice(0, 8)}`;
    }
  }
  return RUN_ID;
}

/** Return the short git SHA of `repo` (cwd by default), or null. */
export function gitSha(repo?: string): string | null {
  try {
    const out = spawnSync("git", ["rev-parse", "--short", "HEAD"], {
      cwd: repo,
      encoding: "utf-8",
    });
    const sha = (out.stdout ?? "").trim();
    return sha || null;
  } catch {
    return null;
  }
}

/** Stable filesystem slug identifying a metric series. */
export function metricSlug(evalId: string, name: string): string {
  const raw = evalId ? `${evalId}__${name}` : name;
  return raw.replace(/[^A-Za-z0-9._-]+/g, "_").replace(/^_+|_+$/g, "");
}

/** Return the JSONL history path for a metric series. */
export function historyPath(
  evalId: string,
  name: string,
  metricsRoot?: string,
): string {
  const root = metricsRoot ?? findMetricsRoot();
  return path.join(root, metricSlug(evalId, name), "history.jsonl");
}

/** Outcome of recording one metric value, with its regression verdict. */
export interface MetricResult {
  eval_id: string;
  name: string;
  value: number;
  unit: string;
  direction: string;
  baseline: number | null;
  baseline_strategy: string;
  delta: number | null;
  pct_delta: number | null;
  regressed: boolean;
  tolerance: number;
  tolerance_pct: number;
  run_id: string;
  git_sha: string | null;
  timestamp: string;
  history_path: string;
}

export function metricAsRecord(m: MetricResult): Record<string, unknown> {
  return {
    ts: m.timestamp,
    run_id: m.run_id,
    git_sha: m.git_sha,
    eval_id: m.eval_id,
    name: m.name,
    value: m.value,
    unit: m.unit,
    direction: m.direction,
    baseline: m.baseline,
    baseline_strategy: m.baseline_strategy,
    delta: m.delta,
    pct_delta: m.pct_delta,
    regressed: m.regressed,
    tolerance: m.tolerance,
    tolerance_pct: m.tolerance_pct,
  };
}

/** Throw an Error if this metric regressed (for gating checks). */
export function assertNoRegression(
  m: MetricResult,
  opts: { logPath?: string } = {},
): void {
  if (!m.regressed) return;
  const logHint = opts.logPath ? `\n  log: ${opts.logPath}` : "";
  throw new Error(
    `Metric '${m.name}' regressed: value=${m.value} baseline=${m.baseline} ` +
      `(${m.baseline_strategy}, ${m.direction}); delta=${m.delta} ` +
      `tolerance=${m.tolerance} tolerance_pct=${m.tolerance_pct}.${logHint}`,
  );
}

export function metricSummary(m: MetricResult): string {
  const base =
    m.baseline !== null
      ? `${m.baseline} (${m.baseline_strategy})`
      : "(no baseline yet)";
  const verdict = m.regressed ? "REGRESSED" : "ok";
  const unitPart = m.unit ? ` ${m.unit}` : "";
  return `metric ${m.name}=${m.value}${unitPart} vs baseline ${base} -> ${verdict}`;
}

/** Return all prior records for a metric series (oldest first). */
export function loadHistory(
  evalId: string,
  name: string,
  metricsRoot?: string,
): Array<Record<string, any>> {
  const p = historyPath(evalId, name, metricsRoot);
  if (!existsSync(p)) return [];
  const records: Array<Record<string, any>> = [];
  for (const rawLine of readFileSync(p, "utf-8").split(/\r?\n/)) {
    const line = rawLine.trim();
    if (!line) continue;
    try {
      records.push(JSON.parse(line));
    } catch {
      continue;
    }
  }
  return records;
}

function numericValues(history: Array<Record<string, any>>): number[] {
  return history
    .map((r) => r.value)
    .filter((v): v is number => typeof v === "number");
}

function resolveBaseline(
  history: Array<Record<string, any>>,
  opts: {
    strategy: string;
    direction: string;
    window: number;
    pinned: number | null;
  },
): number | null {
  const values = numericValues(history);
  if (opts.strategy === "pinned") return opts.pinned;
  if (!values.length) return null;
  if (opts.strategy === "last") return Number(values[values.length - 1]);
  if (opts.strategy === "rolling_mean") {
    const windowVals = opts.window > 0 ? values.slice(-opts.window) : values;
    return windowVals.reduce((a, b) => a + b, 0) / windowVals.length;
  }
  if (opts.strategy === "best") {
    return opts.direction === "higher_is_better"
      ? Math.max(...values)
      : Math.min(...values);
  }
  throw new Error(`Unknown baseline strategy: ${JSON.stringify(opts.strategy)}`);
}

function isRegression(
  value: number,
  baseline: number | null,
  opts: { direction: string; tolerance: number; tolerancePct: number },
): boolean {
  if (baseline === null || opts.direction === "neutral") return false;
  const slack = Math.max(opts.tolerance, Math.abs(baseline) * opts.tolerancePct);
  if (opts.direction === "higher_is_better") {
    return value < baseline - slack;
  }
  if (opts.direction === "lower_is_better") {
    return value > baseline + slack;
  }
  return false;
}

export interface RecordMetricArgs {
  name: string;
  value: number;
  evalId?: string;
  direction?: string;
  unit?: string;
  baselineStrategy?: string;
  baseline?: number | null;
  window?: number;
  tolerance?: number;
  tolerancePct?: number;
  metricsRoot?: string;
  repo?: string;
}

/** Record `value` for a metric series and compute its regression verdict. */
export function recordMetric(args: RecordMetricArgs): MetricResult {
  const direction = args.direction ?? "higher_is_better";
  if (!DIRECTIONS.has(direction)) {
    throw new Error(
      `direction must be one of ${[...DIRECTIONS].join(", ")}, got ` +
        JSON.stringify(direction),
    );
  }
  const value = Number(args.value);
  const evalId = args.evalId ?? "";
  const name = args.name;
  const baselineStrategy = args.baselineStrategy ?? "last";
  const window = args.window ?? 5;
  const tolerance = args.tolerance ?? 0.0;
  const tolerancePct = args.tolerancePct ?? 0.0;

  const history = loadHistory(evalId, name, args.metricsRoot);
  const resolvedBaseline = resolveBaseline(history, {
    strategy: baselineStrategy,
    direction,
    window,
    pinned: args.baseline ?? null,
  });
  const delta = resolvedBaseline !== null ? value - resolvedBaseline : null;
  const pctDelta =
    delta !== null && resolvedBaseline !== null && resolvedBaseline !== 0
      ? delta / resolvedBaseline
      : null;
  const regressed = isRegression(value, resolvedBaseline, {
    direction,
    tolerance,
    tolerancePct,
  });

  const hp = historyPath(evalId, name, args.metricsRoot);
  const result: MetricResult = {
    eval_id: evalId,
    name,
    value,
    unit: args.unit ?? "",
    direction,
    baseline: resolvedBaseline,
    baseline_strategy: baselineStrategy,
    delta,
    pct_delta: pctDelta,
    regressed,
    tolerance,
    tolerance_pct: tolerancePct,
    run_id: runId(),
    git_sha: gitSha(args.repo),
    timestamp: nowIso(),
    history_path: hp,
  };

  mkdirSync(path.dirname(hp), { recursive: true });
  appendFileSync(hp, JSON.stringify(metricAsRecord(result)) + "\n", "utf-8");
  return result;
}

/** Return a compact trend summary for a metric series. */
export function summarize(
  evalId: string,
  name: string,
  metricsRoot?: string,
): Record<string, unknown> {
  const history = loadHistory(evalId, name, metricsRoot);
  const values = numericValues(history);
  return {
    eval_id: evalId,
    name,
    count: history.length,
    first: values.length ? values[0] : null,
    latest: values.length ? values[values.length - 1] : null,
    min: values.length ? Math.min(...values) : null,
    max: values.length ? Math.max(...values) : null,
    mean: values.length
      ? values.reduce((a, b) => a + b, 0) / values.length
      : null,
    regressions: history.filter((r) => r.regressed).length,
    history_path: historyPath(evalId, name, metricsRoot),
  };
}

/** Yield `[slug, historyPath]` for every metric series on disk. */
export function iterSeries(metricsRoot?: string): Array<[string, string]> {
  const root = metricsRoot ?? findMetricsRoot();
  if (!existsSync(root)) return [];
  const out: Array<[string, string]> = [];
  const dirs = readdirSync(root, { withFileTypes: true })
    .filter((e) => e.isDirectory())
    .map((e) => e.name)
    .sort();
  for (const name of dirs) {
    const hp = path.join(root, name, "history.jsonl");
    if (existsSync(hp) && statSync(hp).isFile()) out.push([name, hp]);
  }
  return out;
}
