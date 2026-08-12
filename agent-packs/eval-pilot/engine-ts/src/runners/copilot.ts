/**
 * Copilot CLI {@link SUTRunner} implementation.
 *
 * Drives the `copilot` binary non-interactively inside a workspace and returns
 * a normalised {@link RunResult}.
 *
 * Hardening retained from the Python original:
 *  - Known fatal Windows exit codes are surfaced via `result.extra.crash` so a
 *    CLI runtime crash isn't confused with an agent-prompt defect.
 *  - The subprocess is launched in its own process group; on timeout the whole
 *    tree is killed via `tree-kill`.
 *  - The prompt is fed via **stdin**, never `-p`: the Windows `copilot.CMD` shim
 *    truncates `-p` values at the first newline.
 *  - `--allow-all --no-ask-user` is the only flag combo that reliably grants
 *    write/shell perms in non-interactive mode.
 */

import { spawn, type SpawnOptions } from "node:child_process";
import { existsSync, mkdirSync, writeFileSync } from "node:fs";
import * as path from "node:path";
import treeKill from "tree-kill";
import {
  captureFromFile,
  telemetryEnabled,
  telemetryEnv,
} from "../telemetry/capture.js";
import { emptyTelemetry } from "../telemetry/model.js";
import {
  makeRunResult,
  registerRunner,
  SUTUnavailable,
  type RunAgentArgs,
  type RunResult,
  type RunSkillArgs,
  type SUTRunner,
} from "./base.js";

/** Known fatal Windows NTSTATUS exit codes (runtime crashes, not defects). */
const WIN_FATAL_EXIT_CODES: Record<number, string> = {
  3221225477: "STATUS_ACCESS_VIOLATION (0xC0000005)",
  3221225725: "STATUS_STACK_OVERFLOW (0xC00000FD)",
  3221226505: "STATUS_STACK_BUFFER_OVERRUN (0xC0000409)",
};

export class CopilotNotInstalled extends SUTUnavailable {}

function truthyEnv(name: string): boolean {
  const v = (process.env[name] ?? "").trim().toLowerCase();
  return v === "1" || v === "true" || v === "yes" || v === "on";
}

function skipSut(): boolean {
  return truthyEnv("EVALPILOT_SKIP_SUT") || truthyEnv("EVALS_SKIP_SUT");
}

/**
 * Resolve the effective SUT wall-clock timeout (seconds).
 *
 * Precedence:
 *   1. Explicit `--sut-timeout` override (`override`, when > 0) — authoritative;
 *      RAISES or lowers the timeout regardless of the frontmatter value.
 *   2. `EVALPILOT_SUT_TIMEOUT` / `EVALS_SUT_TIMEOUT` env — a MAX **cap**; it can
 *      only LOWER `requested`, never raise it (back-compat behaviour retained).
 *   3. `requested` — the spec's frontmatter `timeout:` (or the caller default).
 *
 * When neither override nor env is set, behaviour is unchanged (returns
 * `requested`).
 */
function resolveSutTimeout(requested: number, override?: number | null): number {
  // 1. Explicit CLI override wins and may raise above the frontmatter value.
  if (override != null && !Number.isNaN(override) && override > 0) {
    return override;
  }
  // 2. Env var is a cap only (Math.min): it can lower but never raise.
  const raw = (
    process.env.EVALPILOT_SUT_TIMEOUT ??
    process.env.EVALS_SUT_TIMEOUT ??
    ""
  ).trim();
  if (!raw) return requested;
  const cap = Number(raw);
  if (Number.isNaN(cap)) return requested;
  return cap > 0 ? Math.min(requested, cap) : requested;
}

/** Locate an executable on PATH (honours PATHEXT on Windows). */
function which(cmd: string): string | null {
  const isWin = process.platform === "win32";
  const exts = isWin
    ? (process.env.PATHEXT ?? ".COM;.EXE;.BAT;.CMD").split(";")
    : [""];
  const dirs = (process.env.PATH ?? "").split(path.delimiter);
  for (const dir of dirs) {
    if (!dir) continue;
    for (const ext of exts) {
      const candidate = path.join(dir, cmd + ext);
      if (existsSync(candidate)) return candidate;
    }
  }
  return null;
}

/** Return absolute path to the `copilot` binary or throw. */
export function findCopilotBin(): string {
  const override = process.env.COPILOT_BIN;
  if (override) return override;
  const candidate = which("copilot");
  if (!candidate) {
    throw new CopilotNotInstalled(
      "No `copilot` binary found on PATH. Set COPILOT_BIN to override " +
        "(useful for tests with a stubbed binary).",
    );
  }
  return candidate;
}

function killTree(pid: number): Promise<void> {
  return new Promise((resolve) => {
    treeKill(pid, "SIGTERM", () => resolve());
  });
}

interface RunOpts {
  cwd: string;
  logPath: string;
  timeout: number;
  stdinText?: string | null;
  /** Extra environment variables merged into the child process. */
  env?: Record<string, string> | null;
  /** OTel file-exporter path to parse into telemetry after the run. */
  otelPath?: string | null;
}

function isWindowsBatchWrapper(bin: string): boolean {
  return process.platform === "win32" && /\.(?:cmd|bat)$/i.test(bin);
}

function isWindowsPowerShellScript(bin: string): boolean {
  return process.platform === "win32" && /\.ps1$/i.test(bin);
}

function quoteWindowsShellArg(arg: string): string {
  const escaped = arg
    .replace(/(\\*)"/g, '$1$1\\"')
    .replace(/(\\+)$/g, '$1$1');
  return `"${escaped}"`;
}

function prepareSpawn(
  bin: string,
  args: string[],
  baseOptions: SpawnOptions,
): { bin: string; args: string[]; options: SpawnOptions } {
  if (isWindowsBatchWrapper(bin)) {
    // Node cannot spawn .cmd/.bat directly on Windows; run through cmd.exe
    // and pre-quote each argument so spaces/metacharacters stay in argv.
    return {
      bin,
      args: args.map(quoteWindowsShellArg),
      options: { ...baseOptions, shell: true, detached: false },
    };
  }
  if (isWindowsPowerShellScript(bin)) {
    return {
      bin: "powershell.exe",
      args: ["-NoProfile", "-ExecutionPolicy", "Bypass", "-File", bin, ...args],
      options: { ...baseOptions, detached: false },
    };
  }
  return { bin, args, options: baseOptions };
}

async function runProcess(cmd: string[], opts: RunOpts): Promise<RunResult> {
  mkdirSync(path.dirname(opts.logPath), { recursive: true });
  const started = process.hrtime.bigint();
  const stdinText = opts.stdinText ?? null;

  const [bin, ...args] = cmd;
  const baseOptions: SpawnOptions = {
    cwd: opts.cwd,
    // Own process group so tree-kill can reap the whole tree.
    detached: process.platform !== "win32",
    windowsHide: true,
    env: opts.env ? { ...process.env, ...opts.env } : process.env,
    stdio: [stdinText !== null ? "pipe" : "ignore", "pipe", "pipe"],
  };
  const prepared = prepareSpawn(bin!, args, baseOptions);
  const proc = spawn(prepared.bin, prepared.args, prepared.options);

  let stdout = "";
  let stderr = "";
  let timedOut = false;

  proc.stdout?.setEncoding("utf-8");
  proc.stderr?.setEncoding("utf-8");
  proc.stdout?.on("data", (d) => (stdout += d));
  proc.stderr?.on("data", (d) => (stderr += d));

  if (stdinText !== null && proc.stdin) {
    proc.stdin.write(stdinText);
    proc.stdin.end();
  }

  const returncode: number = await new Promise((resolve) => {
    const timer = setTimeout(() => {
      timedOut = true;
      if (proc.pid) void killTree(proc.pid);
      // Give the tree a moment to die, then resolve with the timeout code.
      setTimeout(() => resolve(124), 5000);
    }, opts.timeout * 1000);

    proc.on("error", () => {
      clearTimeout(timer);
      resolve(-1);
    });
    proc.on("close", (code, signal) => {
      if (timedOut) return; // handled by the timeout path
      clearTimeout(timer);
      if (code === null) {
        // Killed by signal; surface a non-zero code.
        resolve(signal ? 128 : 1);
      } else {
        resolve(code);
      }
    });
  });

  if (timedOut) {
    stderr = (stderr || "") + `\n[evalpilot] TIMEOUT after ${opts.timeout}s\n`;
  }

  const duration = Number(process.hrtime.bigint() - started) / 1e9;

  const crash =
    !timedOut && returncode in WIN_FATAL_EXIT_CODES
      ? WIN_FATAL_EXIT_CODES[returncode]
      : null;

  const crashLine = crash ? `[crash] ${crash}\n` : "";
  writeFileSync(
    opts.logPath,
    `$ ${cmd.join(" ")}\n[cwd] ${opts.cwd}\n[exit] ${returncode}\n` +
      `[duration_s] ${duration.toFixed(2)}\n${crashLine}\n` +
      `--- PROMPT (stdin) ---\n${stdinText ?? ""}\n` +
      `--- STDOUT ---\n${stdout}\n--- STDERR ---\n${stderr}\n`,
    "utf-8",
  );

  return makeRunResult({
    returncode,
    stdout,
    stderr,
    duration_seconds: duration,
    log_path: opts.logPath,
    timed_out: timedOut,
    extra: crash ? { crash } : {},
    telemetry: opts.otelPath
      ? captureFromFile(opts.otelPath)
      : emptyTelemetry("telemetry capture disabled"),
  });
}

function skippedResult(opts: {
  cmd: string[];
  cwd: string;
  logPath: string;
  stdinText?: string | null;
}): RunResult {
  mkdirSync(path.dirname(opts.logPath), { recursive: true });
  writeFileSync(
    opts.logPath,
    `$ ${opts.cmd.join(" ")}\n[cwd] ${opts.cwd}\n[exit] 125\n` +
      `[skipped] EVALPILOT_SKIP_SUT is set; SUT not launched.\n\n` +
      `--- PROMPT (stdin) ---\n${opts.stdinText ?? ""}\n` +
      `--- STDOUT ---\n\n--- STDERR ---\n`,
    "utf-8",
  );
  return makeRunResult({
    returncode: 125,
    stdout: "",
    stderr: "[evalpilot] EVALPILOT_SKIP_SUT set; SUT not launched.\n",
    duration_seconds: 0.0,
    log_path: opts.logPath,
    skipped: true,
  });
}

class CopilotRunner implements SUTRunner {
  readonly name = "copilot";

  available(): boolean {
    try {
      findCopilotBin();
      return true;
    } catch (e) {
      if (e instanceof CopilotNotInstalled) return false;
      throw e;
    }
  }

  async runAgent(args: RunAgentArgs): Promise<RunResult> {
    const extraArgs = args.extra_args ?? [];
    if (skipSut()) {
      const agentPart = args.agent ? ["--agent", args.agent] : [];
      return skippedResult({
        cmd: ["<copilot>", ...agentPart, "--allow-all", "--no-ask-user"],
        cwd: args.workspace,
        logPath: args.log_path,
        stdinText: args.prompt,
      });
    }
    const binPath = findCopilotBin();
    const cmd: string[] = [binPath];
    if (args.agent) cmd.push("--agent", args.agent);
    cmd.push("--allow-all", "--no-ask-user", ...extraArgs);
    const otelPath = telemetryEnabled() ? `${args.log_path}.otel.jsonl` : null;
    return runProcess(cmd, {
      cwd: args.workspace,
      logPath: args.log_path,
      timeout: resolveSutTimeout(args.timeout, args.sut_timeout_override),
      stdinText: args.prompt,
      env: otelPath ? telemetryEnv(otelPath) : null,
      otelPath,
    });
  }

  async runSkill(args: RunSkillArgs): Promise<RunResult> {
    const augmented =
      `Use the \`${args.skill}\` skill to handle the following request. ` +
      `Do not invoke any other skill.\n\n${args.prompt}`;
    return this.runAgent({
      prompt: augmented,
      workspace: args.workspace,
      agent: null,
      log_path: args.log_path,
      timeout: args.timeout,
      extra_args: args.extra_args,
      sut_timeout_override: args.sut_timeout_override,
    });
  }
}

registerRunner("copilot", () => new CopilotRunner());

export { CopilotRunner };

// Exported for unit tests (budget-control regression guards).
export { truthyEnv, skipSut, resolveSutTimeout, runProcess, prepareSpawn };
