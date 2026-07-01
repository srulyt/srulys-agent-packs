/**
 * A deterministic, offline `mock` SUT runner.
 *
 * Select it with `EVALPILOT_RUNNER=mock`. It never launches a real agent, so
 * the whole pipeline runs without the `copilot` binary.
 *
 * Behaviour is scripted in three ways (checked in order):
 *  1. Programmatically via {@link configureMock} (used by tests).
 *  2. Via env: `EVALPILOT_MOCK_STDOUT`, `EVALPILOT_MOCK_FILES` (JSON of
 *     `{relpath: content}`), `EVALPILOT_MOCK_JUDGE_SCORE`.
 *  3. A sensible default: echo the prompt, create nothing.
 *
 * When asked to run the `eval-judge` agent, the mock emits a canned JSON
 * verdict so the judge helper works offline too.
 */

import { mkdirSync, writeFileSync } from "node:fs";
import * as path from "node:path";
import {
  makeRunResult,
  registerRunner,
  type RunAgentArgs,
  type RunResult,
  type RunSkillArgs,
  type SUTRunner,
} from "./base.js";

interface MockScript {
  stdout?: string;
  files?: Record<string, unknown>;
  returncode?: number;
  judge_score?: number;
  judge_rationale?: string;
}

let SCRIPT: MockScript = {};

/** Script the next mock runs. Pass `undefined` fields to leave them unset. */
export function configureMock(opts: {
  stdout?: string;
  files?: Record<string, unknown>;
  returncode?: number;
  judgeScore?: number;
  judgeRationale?: string;
} = {}): void {
  SCRIPT = {};
  if (opts.stdout !== undefined) SCRIPT.stdout = opts.stdout;
  if (opts.files !== undefined) SCRIPT.files = { ...opts.files };
  SCRIPT.returncode = opts.returncode ?? 0;
  if (opts.judgeScore !== undefined) SCRIPT.judge_score = opts.judgeScore;
  SCRIPT.judge_rationale = opts.judgeRationale ?? "mock verdict";
}

/** Clear any programmatic script. */
export function resetMock(): void {
  SCRIPT = {};
}

function judgeScore(): number {
  if (SCRIPT.judge_score !== undefined) return Number(SCRIPT.judge_score);
  const raw = process.env.EVALPILOT_MOCK_JUDGE_SCORE;
  return raw ? Number(raw) : 1.0;
}

function scriptedFiles(): Record<string, unknown> {
  if (SCRIPT.files !== undefined) return SCRIPT.files;
  const raw = process.env.EVALPILOT_MOCK_FILES;
  if (raw) {
    try {
      return JSON.parse(raw);
    } catch {
      return {};
    }
  }
  return {};
}

function scriptedStdout(prompt: string): string {
  if (SCRIPT.stdout !== undefined) return SCRIPT.stdout;
  const env = process.env.EVALPILOT_MOCK_STDOUT;
  if (env !== undefined) return env;
  return `[mock] received prompt (${prompt.length} chars); no action taken.\n`;
}

class MockRunner implements SUTRunner {
  readonly name = "mock";

  available(): boolean {
    return true;
  }

  async runAgent(args: RunAgentArgs): Promise<RunResult> {
    const started = process.hrtime.bigint();
    let stdout: string;
    let returncode: number;

    if (args.agent === "eval-judge") {
      stdout = JSON.stringify({
        score: judgeScore(),
        rationale: SCRIPT.judge_rationale ?? "mock verdict",
        evidence: [{ path: "artifact", quote: "(mock)" }],
      });
      returncode = 0;
    } else {
      for (const [rel, content] of Object.entries(scriptedFiles())) {
        const target = path.join(args.workspace, rel);
        mkdirSync(path.dirname(target), { recursive: true });
        writeFileSync(target, String(content), "utf-8");
      }
      stdout = scriptedStdout(args.prompt);
      returncode = Number(SCRIPT.returncode ?? 0);
    }

    const duration = Number(process.hrtime.bigint() - started) / 1e9;
    mkdirSync(path.dirname(args.log_path), { recursive: true });
    writeFileSync(
      args.log_path,
      `$ <mock> agent=${args.agent}\n[cwd] ${args.workspace}\n` +
        `[exit] ${returncode}\n[duration_s] ${duration.toFixed(4)}\n\n` +
        `--- PROMPT (stdin) ---\n${args.prompt}\n` +
        `--- STDOUT ---\n${stdout}\n--- STDERR ---\n`,
      "utf-8",
    );
    return makeRunResult({
      returncode,
      stdout,
      stderr: "",
      duration_seconds: duration,
      log_path: args.log_path,
      extra: { mock: true },
    });
  }

  async runSkill(args: RunSkillArgs): Promise<RunResult> {
    return this.runAgent({
      prompt: args.prompt,
      workspace: args.workspace,
      agent: null,
      log_path: args.log_path,
      timeout: args.timeout,
      extra_args: args.extra_args,
    });
  }
}

registerRunner("mock", () => new MockRunner());

export { MockRunner };
