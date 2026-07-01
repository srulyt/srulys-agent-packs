/**
 * Budget-control regression guards for the copilot runner (ports the legacy
 * pytest `test_sut_budget_controls.py`).
 *
 * Behavioural pack evals drive the live Copilot CLI, which makes multi-minute,
 * non-deterministic LLM calls. Two opt-in controls keep a hung or too-slow SUT
 * from starving the whole suite:
 *   - EVALPILOT_SUT_TIMEOUT clamps every SUT subprocess timeout (fail fast, 124).
 *   - EVALPILOT_SKIP_SUT short-circuits runAgent (clean skip, 125) with 0 tokens.
 * These deterministic, no-live-SUT tests pin that behaviour so it can't regress.
 */

import { mkdtempSync, existsSync, readFileSync, writeFileSync } from "node:fs";
import { tmpdir } from "node:os";
import * as path from "node:path";
import { afterEach, describe, expect, it } from "vitest";

import {
  CopilotRunner,
  resolveSutTimeout,
  runProcess,
  skipSut,
  truthyEnv,
} from "../src/runners/copilot.js";
import { runOk, runUsable, unavailableReason } from "../src/runners/base.js";

const BUDGET_ENV = [
  "EVALPILOT_SUT_TIMEOUT",
  "EVALS_SUT_TIMEOUT",
  "EVALPILOT_SKIP_SUT",
  "EVALS_SKIP_SUT",
  "COPILOT_BIN",
];

function clearBudgetEnv(): void {
  for (const key of BUDGET_ENV) delete process.env[key];
}

afterEach(clearBudgetEnv);

function mkTmp(): string {
  return mkdtempSync(path.join(tmpdir(), "evalpilot-budget-"));
}

// ---- timeout clamping ---------------------------------------------------

describe("resolveSutTimeout", () => {
  it("passes through when unset", () => {
    delete process.env.EVALPILOT_SUT_TIMEOUT;
    expect(resolveSutTimeout(900)).toBe(900);
  });

  it("clamps when set, never raising above the requested value", () => {
    process.env.EVALPILOT_SUT_TIMEOUT = "30";
    expect(resolveSutTimeout(900)).toBe(30);
    expect(resolveSutTimeout(10)).toBe(10);
  });

  it("ignores garbage and non-positive values", () => {
    process.env.EVALPILOT_SUT_TIMEOUT = "not-a-number";
    expect(resolveSutTimeout(900)).toBe(900);
    process.env.EVALPILOT_SUT_TIMEOUT = "0";
    expect(resolveSutTimeout(900)).toBe(900);
  });
});

describe("truthyEnv", () => {
  const cases: Array<[string, boolean]> = [
    ["1", true],
    ["true", true],
    ["YES", true],
    ["on", true],
    ["0", false],
    ["", false],
    ["false", false],
    ["nope", false],
  ];
  for (const [value, expected] of cases) {
    it(`treats ${JSON.stringify(value)} as ${expected}`, () => {
      process.env.EVALPILOT_SKIP_SUT = value;
      expect(truthyEnv("EVALPILOT_SKIP_SUT")).toBe(expected);
    });
  }

  it("skipSut honours EVALPILOT_SKIP_SUT", () => {
    process.env.EVALPILOT_SKIP_SUT = "1";
    expect(skipSut()).toBe(true);
  });
});

// ---- EVALPILOT_SKIP_SUT short-circuit -----------------------------------

describe("EVALPILOT_SKIP_SUT short-circuit", () => {
  it("returns a clean skip sentinel without consulting the binary", async () => {
    const tmp = mkTmp();
    process.env.EVALPILOT_SKIP_SUT = "1";
    // Point COPILOT_BIN at a non-existent path: if the short-circuit regresses
    // and bin resolution runs, spawn would fail — proving skip runs first.
    process.env.COPILOT_BIN = path.join(tmp, "does-not-exist");

    const log = path.join(tmp, "agent.log");
    const res = await new CopilotRunner().runAgent({
      prompt: "hello",
      workspace: tmp,
      agent: null,
      log_path: log,
      timeout: 900,
    });

    expect(res.skipped).toBe(true);
    expect(res.timed_out).toBe(false);
    expect(res.returncode).toBe(125);
    expect(runUsable(res)).toBe(false);
    expect(unavailableReason(res)).not.toBe("");
    expect(existsSync(log)).toBe(true);
  });

  it("runUsable/runOk are true for a normal result", () => {
    const res = {
      returncode: 0,
      stdout: "",
      stderr: "",
      duration_seconds: 0.0,
      log_path: "x",
      timed_out: false,
      skipped: false,
      extra: {},
    };
    expect(runUsable(res)).toBe(true);
    expect(runOk(res)).toBe(true);
    expect(unavailableReason(res)).toBe("");
  });
});

// ---- fail-fast timeout (the actual stall the loop hit) ------------------

describe("hung SUT", () => {
  it(
    "is force-killed at the timeout and marked timed_out (not run to completion)",
    async () => {
      const tmp = mkTmp();
      // A child that holds stdin/stdout open and sleeps far past the timeout.
      const stub = path.join(tmp, "hang.mjs");
      writeFileSync(
        stub,
        [
          "process.stdin.resume();",
          "process.stdin.on('data', () => {});",
          "setTimeout(() => {}, 600000);",
        ].join("\n"),
        "utf-8",
      );
      const log = path.join(tmp, "out.log");
      const t0 = Date.now();
      const res = await runProcess([process.execPath, stub], {
        cwd: tmp,
        logPath: log,
        timeout: 5,
        stdinText: "x",
      });
      const elapsed = (Date.now() - t0) / 1000;

      expect(res.returncode).toBe(124);
      expect(res.timed_out).toBe(true);
      expect(runUsable(res)).toBe(false);
      expect(existsSync(log)).toBe(true);
      // Must terminate near the timeout, never the stub's 600s sleep.
      expect(elapsed).toBeLessThan(45);
    },
    60_000,
  );
});
