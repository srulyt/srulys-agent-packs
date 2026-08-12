/**
 * Pluggable system-under-test (SUT) runner interface.
 *
 * A *runner* knows how to drive one kind of agent runtime non-interactively
 * inside a workspace and return a normalised {@link RunResult}. Selection is by
 * name via {@link getRunner}, overridable with the `EVALPILOT_RUNNER`
 * environment variable.
 */

import type { RunTelemetry } from "../telemetry/model.js";

/** Normalised outcome of a single SUT invocation. */
export interface RunResult {
  returncode: number;
  stdout: string;
  stderr: string;
  duration_seconds: number;
  log_path: string;
  timed_out: boolean;
  skipped: boolean;
  extra: Record<string, unknown>;
  /**
   * Captured run telemetry (tool calls, token usage, …), when available. When
   * absent, assertions treat telemetry as unavailable and skip (neutral).
   */
  telemetry?: RunTelemetry;
}

export function makeRunResult(
  init: Partial<RunResult> &
    Pick<
      RunResult,
      "returncode" | "stdout" | "stderr" | "duration_seconds" | "log_path"
    >,
): RunResult {
  return {
    timed_out: false,
    skipped: false,
    extra: {},
    ...init,
  };
}

export function runOk(r: RunResult): boolean {
  return r.returncode === 0;
}

/** True when the run produced real SUT output (not skipped/timed-out). */
export function runUsable(r: RunResult): boolean {
  return !(r.skipped || r.timed_out);
}

/** One-line reason a behavioural check should skip, or "". */
export function unavailableReason(r: RunResult): string {
  if (r.skipped) {
    return (
      "SUT not launched (EVALPILOT_SKIP_SUT set); this environment cannot run " +
      `the live SUT within budget. See ${r.log_path}.`
    );
  }
  if (r.timed_out) {
    return (
      "SUT did not complete within its (capped) wall-clock timeout in this " +
      `environment. See ${r.log_path}.`
    );
  }
  return "";
}

/** Raised when a runner's backend is not installed/usable. */
export class SUTUnavailable extends Error {}

export interface RunAgentArgs {
  prompt: string;
  workspace: string;
  agent: string | null;
  log_path: string;
  timeout: number;
  extra_args?: string[];
  /**
   * Explicit per-run SUT timeout override (seconds) from `--sut-timeout`.
   * When set (> 0) it is authoritative and can RAISE or lower the effective
   * timeout above/below the spec's frontmatter `timeout:`.
   */
  sut_timeout_override?: number | null;
}

export interface RunSkillArgs {
  skill: string;
  prompt: string;
  workspace: string;
  log_path: string;
  timeout: number;
  extra_args?: string[];
  /** See {@link RunAgentArgs.sut_timeout_override}. */
  sut_timeout_override?: number | null;
}

/** Drives one agent runtime non-interactively inside a workspace. */
export interface SUTRunner {
  /** Short stable identifier used by {@link getRunner} / `EVALPILOT_RUNNER`. */
  readonly name: string;
  /** Return true when this runner can actually execute (binary present). */
  available(): boolean;
  /** Run a named agent (or the host default) against `prompt`. */
  runAgent(args: RunAgentArgs): Promise<RunResult>;
  /** Exercise a single skill in isolation against `prompt`. */
  runSkill(args: RunSkillArgs): Promise<RunResult>;
}

type RunnerFactory = () => SUTRunner;

const REGISTRY: Map<string, RunnerFactory> = new Map();

/** Register a runner factory under its `name`. */
export function registerRunner(name: string, factory: RunnerFactory): void {
  REGISTRY.set(name, factory);
}

/**
 * Return a runner instance.
 * Resolution: explicit `name` > `EVALPILOT_RUNNER` env > `"copilot"`.
 */
export function getRunner(name?: string): SUTRunner {
  const chosen = name || process.env.EVALPILOT_RUNNER || "copilot";
  const factory = REGISTRY.get(chosen);
  if (!factory) {
    const available = [...REGISTRY.keys()].sort().join(", ") || "(none)";
    throw new Error(`Unknown SUT runner '${chosen}'. Registered: ${available}`);
  }
  return factory();
}
