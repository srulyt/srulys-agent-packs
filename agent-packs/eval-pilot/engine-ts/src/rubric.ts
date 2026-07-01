/**
 * Binary (pass/fail) rubric results.
 *
 * A *rubric* is a set of named pass/fail checks evaluated against a SUT's
 * output. It is the binary counterpart to {@link module:metrics}. Checks can
 * come from structural assertions, judge verdicts, or any boolean condition.
 */

import type { Verdict } from "./judge.js";

/** A single named pass/fail criterion. */
export interface Check {
  name: string;
  passed: boolean;
  detail: string;
}

export function makeCheck(
  name: string,
  passed: boolean,
  detail = "",
): Check {
  return { name, passed, detail };
}

/** A check may be a Check or a [name, passed] / [name, passed, detail] tuple. */
export type CheckLike =
  | Check
  | [string, boolean]
  | [string, boolean, string];

function coerce(check: CheckLike): Check {
  if (Array.isArray(check)) {
    if (check.length === 2) {
      return makeCheck(String(check[0]), Boolean(check[1]));
    }
    if (check.length === 3) {
      return makeCheck(String(check[0]), Boolean(check[1]), String(check[2]));
    }
    throw new TypeError(
      `Each check must be a Check or a [name, passed[, detail]] tuple; got ` +
        JSON.stringify(check),
    );
  }
  if (check && typeof check === "object" && "name" in check) {
    return { detail: check.detail ?? "", name: check.name, passed: check.passed };
  }
  throw new TypeError(
    `Each check must be a Check or a [name, passed[, detail]] tuple; got ` +
      JSON.stringify(check),
  );
}

/** Outcome of evaluating a rubric. */
export class RubricResult {
  checks: Check[];

  constructor(checks: Check[]) {
    this.checks = checks;
  }

  get passed(): boolean {
    return this.checks.every((c) => c.passed);
  }

  get failed(): Check[] {
    return this.checks.filter((c) => !c.passed);
  }

  get passRate(): number {
    if (!this.checks.length) return 1.0;
    return this.checks.filter((c) => c.passed).length / this.checks.length;
  }

  summary(): string {
    const lines = this.checks.map(
      (c) =>
        `[${c.passed ? "PASS" : "FAIL"}] ${c.name}` +
        (c.detail ? ` — ${c.detail}` : ""),
    );
    const passedCount = this.checks.filter((c) => c.passed).length;
    const header = `Rubric: ${passedCount}/${this.checks.length} checks passed`;
    return [header, ...lines].join("\n");
  }

  /** Throw an Error if any check failed. */
  assertPassed(opts: { logPath?: string } = {}): void {
    if (this.passed) return;
    const failed = this.failed
      .map((c) => `  - ${c.name}` + (c.detail ? `: ${c.detail}` : ""))
      .join("\n");
    const logHint = opts.logPath ? `\n  log: ${opts.logPath}` : "";
    throw new Error(
      `Rubric failed (${this.failed.length}/${this.checks.length} checks ` +
        `did not pass):\n${failed}${logHint}`,
    );
  }
}

/** Build a {@link RubricResult} from checks. */
export function rubric(...checks: CheckLike[]): RubricResult {
  return new RubricResult(checks.map(coerce));
}

/** Turn an LLM judge {@link Verdict} into a {@link Check}. */
export function checkJudge(
  name: string,
  verdict: Verdict | boolean,
  opts: { detail?: string } = {},
): Check {
  if (typeof verdict === "boolean") {
    return makeCheck(name, verdict, opts.detail ?? "");
  }
  const reasoning = verdict.reasoning ?? "";
  const score = verdict.score;
  const autoDetail =
    score !== undefined && score !== null
      ? `score=${score.toFixed(2)}: ${reasoning}`
      : reasoning;
  return makeCheck(
    name,
    Boolean(verdict.passed),
    opts.detail !== undefined ? opts.detail : autoDetail,
  );
}
