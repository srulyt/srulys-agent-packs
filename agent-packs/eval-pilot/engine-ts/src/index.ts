/**
 * evalpilot — portable eval engine for GitHub Copilot agents and skills.
 *
 * Public API (stable surface for eval authors):
 *
 * ```ts
 * import {
 *   Eval,                          // fluent builder for *.eval.ts
 *   Workspace,                     // isolated per-test workspace
 *   judge, type Verdict,           // LLM-as-judge
 *   rubric, checkJudge,            // binary pass/fail rubric
 *   recordMetric,                  // numeric metrics + JSONL history
 *   assertProseContains, assertProseNotContains,
 *   getRunner, type RunResult,     // pluggable SUT runner
 *   runEval, runSpecs,             // standalone executor
 * } from "@evalpilot/cli";
 * ```
 */

export const VERSION = "0.2.0";

// authoring surfaces
export { Eval } from "./loaders/builder.js";
export { loadMarkdownEval, parseMarkdownEval } from "./loaders/markdown.js";
export {
  makeEvalSpec,
  specIsStub,
  specIsStructural,
  specIsImplemented,
  validateSpec,
  AGENT,
  SKILL,
  NONE,
  type EvalSpec,
  type ActSpec,
  type AssertionSpec,
  type JudgeSpec,
  type MetricSpec,
  type SetupSpec,
  type StageSpec,
} from "./spec.js";

// execution
export { runEval, runSpecs, type RunEvalOptions, type RunSpecsOptions } from "./executor.js";
export { collectSpecs } from "./collect.js";

// result model
export {
  PASSED,
  FAILED,
  SKIPPED,
  ERROR,
  reportOk,
  reportToDict,
  type AssertionResult,
  type EvalResult,
  type EvalRunReport,
  type JudgeResult,
  type MetricRecord,
} from "./model.js";

// primitives (still public)
export { Workspace, FixtureMissingError } from "./workspace.js";
export { judge, JudgeError, type Verdict } from "./judge.js";
export { rubric, checkJudge, RubricResult, type Check } from "./rubric.js";
export {
  recordMetric,
  loadHistory,
  summarize,
  iterSeries,
  type MetricResult,
} from "./metrics.js";
export { assertProseContains, assertProseNotContains } from "./asserts.js";
export {
  AssertContext,
  assertion,
  registerAssertion,
  availableKinds,
  runAssertion,
} from "./assertions.js";
export {
  emptyTelemetry,
  filesRead,
  filesWritten,
  modelsUsed,
  toolCallsNamed,
  parseOtelFile,
  parseOtelTelemetry,
  captureFromFile,
  telemetryEnabled,
  telemetryEnv,
  type RunTelemetry,
  type TelemetryTotals,
  type TokenUsage,
  type ToolCall,
} from "./telemetry/index.js";
export {
  registerRunner,
  runOk,
  runUsable,
  type RunResult,
  type SUTRunner,
} from "./runners/base.js";
export { getRunner } from "./runners/index.js";
export { MockRunner, configureMock, resetMock } from "./runners/mock.js";
export { CopilotRunner } from "./runners/copilot.js";

// config
export {
  findRepoRoot,
  findEvalRoot,
  findMetricsRoot,
  bundledDataDir,
} from "./config.js";

// renderers
export { renderTerminal, renderHtml, writeJson, readJson, toJsonStr } from "./render/index.js";
