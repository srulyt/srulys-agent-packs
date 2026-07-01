/**
 * Modeled eval results — the single source of truth every renderer reads.
 *
 * The executor turns each eval into an {@link EvalResult} and a whole run into
 * an {@link EvalRunReport}. These are plain, JSON-round-trippable objects (paths
 * are stored as strings), so the terminal, HTML, and JSON renderers all consume
 * the *same* structured object.
 *
 * Status vocabulary (one string per eval):
 *  - "passed"  — ran and every assertion/metric gate passed.
 *  - "failed"  — ran but at least one assertion/metric gate failed.
 *  - "skipped" — deliberately not run (SUT unavailable, skip tag, …).
 *  - "error"   — the harness itself blew up (bad spec, exception).
 */

export const PASSED = "passed";
export const FAILED = "failed";
export const SKIPPED = "skipped";
export const ERROR = "error";

export type EvalStatus =
  | typeof PASSED
  | typeof FAILED
  | typeof SKIPPED
  | typeof ERROR;

const TERMINAL_OK = new Set<string>([PASSED, SKIPPED]);

/** Outcome of one assertion in an eval's `## Assert` block. */
export interface AssertionResult {
  kind: string;
  name: string;
  passed: boolean;
  detail: string;
  data: Record<string, unknown>;
}

export function makeAssertionResult(
  init: Partial<AssertionResult> &
    Pick<AssertionResult, "kind" | "name" | "passed">,
): AssertionResult {
  return {
    detail: "",
    data: {},
    ...init,
  };
}

export function assertionResultFromDict(d: Record<string, any>): AssertionResult {
  return {
    kind: d.kind,
    name: d.name,
    passed: Boolean(d.passed),
    detail: d.detail ?? "",
    data: { ...(d.data ?? {}) },
  };
}

/** Outcome of one LLM-as-judge assertion. */
export interface JudgeResult {
  name: string;
  passed: boolean;
  score: number;
  threshold: number;
  reasoning: string;
  evidence: unknown[];
  log_path: string | null;
}

export function makeJudgeResult(
  init: Partial<JudgeResult> &
    Pick<JudgeResult, "name" | "passed" | "score" | "threshold">,
): JudgeResult {
  return {
    reasoning: "",
    evidence: [],
    log_path: null,
    ...init,
  };
}

export function judgeResultFromDict(d: Record<string, any>): JudgeResult {
  return {
    name: d.name,
    passed: Boolean(d.passed),
    score: Number(d.score),
    threshold: Number(d.threshold),
    reasoning: d.reasoning ?? "",
    evidence: [...(d.evidence ?? [])],
    log_path: d.log_path ?? null,
  };
}

/** A metric recorded during this run, plus its regression verdict. */
export interface MetricRecord {
  name: string;
  value: number;
  unit: string;
  direction: string;
  baseline: number | null;
  baseline_strategy: string;
  delta: number | null;
  pct_delta: number | null;
  regressed: boolean;
  gated: boolean;
  history_path: string | null;
}

export function makeMetricRecord(
  init: Partial<MetricRecord> & Pick<MetricRecord, "name" | "value">,
): MetricRecord {
  return {
    unit: "",
    direction: "higher_is_better",
    baseline: null,
    baseline_strategy: "last",
    delta: null,
    pct_delta: null,
    regressed: false,
    gated: false,
    history_path: null,
    ...init,
  };
}

/** Shape of a metrics.MetricResult, kept structural to avoid an import cycle. */
export interface MetricResultLike {
  name: string;
  value: number;
  unit: string;
  direction: string;
  baseline: number | null;
  baseline_strategy: string;
  delta: number | null;
  pct_delta: number | null;
  regressed: boolean;
  history_path: string;
}

/** Build a {@link MetricRecord} from a metrics `MetricResult`. */
export function metricRecordFromResult(
  mr: MetricResultLike,
  gated = false,
): MetricRecord {
  return {
    name: mr.name,
    value: mr.value,
    unit: mr.unit,
    direction: mr.direction,
    baseline: mr.baseline,
    baseline_strategy: mr.baseline_strategy,
    delta: mr.delta,
    pct_delta: mr.pct_delta,
    regressed: mr.regressed,
    gated,
    history_path: String(mr.history_path),
  };
}

export function metricRecordFromDict(d: Record<string, any>): MetricRecord {
  return {
    name: d.name,
    value: Number(d.value),
    unit: d.unit ?? "",
    direction: d.direction ?? "higher_is_better",
    baseline: d.baseline ?? null,
    baseline_strategy: d.baseline_strategy ?? "last",
    delta: d.delta ?? null,
    pct_delta: d.pct_delta ?? null,
    regressed: Boolean(d.regressed ?? false),
    gated: Boolean(d.gated ?? false),
    history_path: d.history_path ?? null,
  };
}

/** The modeled outcome of running one eval spec. */
export interface EvalResult {
  name: string;
  status: EvalStatus;
  target: string | null;
  kind: string;
  summary: string;
  description: string;
  tags: string[];
  duration_seconds: number;
  prompt: string | null;
  assertions: AssertionResult[];
  judges: JudgeResult[];
  metrics: MetricRecord[];
  log_path: string | null;
  spec_path: string | null;
  skip_reason: string;
  error: string | null;
  started_at: string;
}

export function makeEvalResult(
  init: Partial<EvalResult> & Pick<EvalResult, "name" | "status">,
): EvalResult {
  return {
    target: null,
    kind: "none",
    summary: "",
    description: "",
    tags: [],
    duration_seconds: 0.0,
    prompt: null,
    assertions: [],
    judges: [],
    metrics: [],
    log_path: null,
    spec_path: null,
    skip_reason: "",
    error: null,
    started_at: "",
    ...init,
  };
}

export function evalResultFromDict(d: Record<string, any>): EvalResult {
  return {
    name: d.name,
    status: d.status,
    target: d.target ?? null,
    kind: d.kind ?? "none",
    summary: d.summary ?? "",
    description: d.description ?? "",
    tags: [...(d.tags ?? [])],
    duration_seconds: Number(d.duration_seconds ?? 0.0),
    prompt: d.prompt ?? null,
    assertions: (d.assertions ?? []).map(assertionResultFromDict),
    judges: (d.judges ?? []).map(judgeResultFromDict),
    metrics: (d.metrics ?? []).map(metricRecordFromDict),
    log_path: d.log_path ?? null,
    spec_path: d.spec_path ?? null,
    skip_reason: d.skip_reason ?? "",
    error: d.error ?? null,
    started_at: d.started_at ?? "",
  };
}

// ---- derived views (functions, since EvalResult is a plain object) --------

export function resultPassed(r: EvalResult): boolean {
  return r.status === PASSED;
}

/** True when the eval did not fail/error (passed or skipped). */
export function resultOk(r: EvalResult): boolean {
  return TERMINAL_OK.has(r.status);
}

export function checkTotal(r: EvalResult): number {
  return r.assertions.length + r.judges.length;
}

export function checkPassed(r: EvalResult): number {
  return (
    r.assertions.filter((a) => a.passed).length +
    r.judges.filter((j) => j.passed).length
  );
}

export function failedLabels(r: EvalResult): string[] {
  const out: string[] = [];
  for (const a of r.assertions) if (!a.passed) out.push(a.name);
  for (const j of r.judges) if (!j.passed) out.push(j.name);
  for (const m of r.metrics)
    if (m.gated && m.regressed) out.push(`metric:${m.name}`);
  return out;
}

/** The modeled outcome of a whole `evalpilot run` invocation. */
export interface EvalRunReport {
  run_id: string;
  started_at: string;
  finished_at: string;
  duration_seconds: number;
  results: EvalResult[];
  git_sha: string | null;
}

export function makeEvalRunReport(
  init: Partial<EvalRunReport> & Pick<EvalRunReport, "run_id">,
): EvalRunReport {
  return {
    started_at: "",
    finished_at: "",
    duration_seconds: 0.0,
    results: [],
    git_sha: null,
    ...init,
  };
}

export function runReportFromDict(d: Record<string, any>): EvalRunReport {
  return {
    run_id: d.run_id,
    started_at: d.started_at ?? "",
    finished_at: d.finished_at ?? "",
    duration_seconds: Number(d.duration_seconds ?? 0.0),
    results: (d.results ?? []).map(evalResultFromDict),
    git_sha: d.git_sha ?? null,
  };
}

// ---- aggregate counts -----------------------------------------------------

export function reportTotal(rep: EvalRunReport): number {
  return rep.results.length;
}

function countStatus(rep: EvalRunReport, status: string): number {
  return rep.results.filter((r) => r.status === status).length;
}

export function reportPassed(rep: EvalRunReport): number {
  return countStatus(rep, PASSED);
}

export function reportFailed(rep: EvalRunReport): number {
  return countStatus(rep, FAILED);
}

export function reportSkipped(rep: EvalRunReport): number {
  return countStatus(rep, SKIPPED);
}

export function reportErrored(rep: EvalRunReport): number {
  return countStatus(rep, ERROR);
}

/** True when nothing failed or errored (CI-gate friendly). */
export function reportOk(rep: EvalRunReport): boolean {
  return reportFailed(rep) === 0 && reportErrored(rep) === 0;
}

export function reportRegressions(rep: EvalRunReport): number {
  let n = 0;
  for (const r of rep.results)
    for (const m of r.metrics) if (m.gated && m.regressed) n++;
  return n;
}

/**
 * Canonical JSON projection of a report: the plain result objects plus an
 * aggregate `summary` block (mirrors Python's `EvalRunReport.to_dict`).
 */
export function reportToDict(rep: EvalRunReport): Record<string, unknown> {
  return {
    run_id: rep.run_id,
    started_at: rep.started_at,
    finished_at: rep.finished_at,
    duration_seconds: rep.duration_seconds,
    git_sha: rep.git_sha,
    summary: {
      total: reportTotal(rep),
      passed: reportPassed(rep),
      failed: reportFailed(rep),
      skipped: reportSkipped(rep),
      errored: reportErrored(rep),
      regressions: reportRegressions(rep),
    },
    results: rep.results,
  };
}
