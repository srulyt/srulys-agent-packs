/**
 * Fluent TypeScript builder for evals — the power-user / escape-hatch surface.
 *
 * Mirrors the Markdown DSL one-to-one but stays in TypeScript, so authors who
 * need loops, computed prompts, shared fixtures, or arbitrary predicate
 * assertions never hit a DSL wall.
 *
 *     import { Eval } from "@evalpilot/cli";
 *
 *     export const spec = new Eval("migration-plan", {
 *         target: "my-agent", kind: "agent", tags: ["smoke", "judge"], timeout: 600,
 *       })
 *       .describe("Produces an ordered migration plan that names tests.")
 *       .prompt("Create a migration plan for argparse -> Typer.")
 *       .expectFile("plan.md")
 *       .expectContains("test", { path: "plan.md" })
 *       .judge("Score 1.0 only if it lists ordered steps and names tests.",
 *              { artifact: "plan.md", threshold: 0.7 })
 *       .metric("judge_score", "$judge.score", { direction: "higher_is_better",
 *               baseline: "rolling_mean", tolerance: 0.1 })
 *       .check("plan is short", (ctx) => (ctx.read("plan.md") ?? "").length < 8000)
 *       .build();
 *
 * Every method returns `this` for chaining; {@link Eval.build} returns the
 * validated {@link EvalSpec} the executor consumes.
 */

import {
  makeActSpec,
  makeAssertionSpec,
  makeEvalSpec,
  makeFileCopy,
  makeJudgeSpec,
  makeMetricSpec,
  makeSetupSpec,
  makeStageSpec,
  type ActSpec,
  type AssertionSpec,
  type EvalKind,
  type EvalSpec,
  type FileCopy,
  type JudgeSpec,
  type MetricSpec,
  type StageSpec,
} from "../spec.js";

export interface EvalOptions {
  target?: string | null;
  kind?: EvalKind;
  tags?: string[];
  timeout?: number;
  summary?: string;
  description?: string;
}

type TextArg = string | string[];

/** Chainable builder that compiles to an {@link EvalSpec}. */
export class Eval {
  private _name: string;
  private _target: string | null;
  private _kind: EvalKind;
  private _tags: string[];
  private _timeout: number;
  private _summary: string;
  private _description: string;
  private _stage: StageSpec;
  private _files: FileCopy[] = [];
  private _act: ActSpec | null = null;
  private _assertions: AssertionSpec[] = [];
  private _judges: JudgeSpec[] = [];
  private _metrics: MetricSpec[] = [];

  constructor(name: string, opts: EvalOptions = {}) {
    this._name = name;
    this._target = opts.target ?? null;
    this._kind = opts.kind ?? "none";
    this._tags = [...(opts.tags ?? [])];
    this._timeout = Number(opts.timeout ?? 600.0);
    this._summary = opts.summary ?? "";
    this._description = opts.description ?? "";
    this._stage = makeStageSpec();
  }

  // ---- metadata / arrange -----------------------------------------------

  summarize(text: string): this {
    this._summary = text;
    return this;
  }

  describe(text: string): this {
    this._description = text;
    return this;
  }

  tag(...tags: string[]): this {
    this._tags.push(...tags);
    return this;
  }

  stageAgent(name: string, opts: { includeSkills?: boolean } = {}): this {
    this._stage.agent = name;
    this._stage.include_skills = opts.includeSkills ?? true;
    return this;
  }

  stageSkill(name: string): this {
    this._stage.skill = name;
    return this;
  }

  stageAll(): this {
    this._stage.all = true;
    return this;
  }

  copy(src: string, dest = "."): this {
    this._files.push(makeFileCopy(src, dest));
    return this;
  }

  // ---- act --------------------------------------------------------------

  prompt(
    text: string,
    opts: { agent?: string | null; skill?: string | null; timeout?: number | null } = {},
  ): this {
    this._act = makeActSpec({
      prompt: text,
      agent: opts.agent ?? null,
      skill: opts.skill ?? null,
      timeout: opts.timeout ?? null,
    });
    return this;
  }

  // ---- assert -----------------------------------------------------------

  expectFile(...paths: string[]): this {
    this._assertions.push(
      makeAssertionSpec({ kind: "file_exists", args: { paths } }),
    );
    return this;
  }

  expectAbsent(...paths: string[]): this {
    this._assertions.push(
      makeAssertionSpec({ kind: "file_absent", args: { paths } }),
    );
    return this;
  }

  expectContains(
    text: TextArg,
    opts: { path?: string; ignoreCase?: boolean; name?: string } = {},
  ): this {
    return this.textAssert("contains", text, opts.path, opts.name, opts.ignoreCase ?? false);
  }

  expectNotContains(
    text: TextArg,
    opts: { path?: string; name?: string } = {},
  ): this {
    return this.textAssert("not_contains", text, opts.path, opts.name, false);
  }

  expectProse(
    text: TextArg,
    opts: { path?: string; name?: string } = {},
  ): this {
    return this.textAssert("prose_contains", text, opts.path, opts.name, false);
  }

  expectStdout(
    text: TextArg,
    opts: { ignoreCase?: boolean; name?: string } = {},
  ): this {
    return this.textAssert(
      "stdout_contains",
      text,
      undefined,
      opts.name,
      opts.ignoreCase ?? false,
    );
  }

  expectMatches(
    pattern: string,
    opts: { path?: string; flags?: string; name?: string } = {},
  ): this {
    const args: Record<string, any> = { pattern, flags: opts.flags ?? "" };
    if (opts.path) args.path = opts.path;
    this._assertions.push(
      makeAssertionSpec({ kind: "matches", args, name: opts.name ?? null }),
    );
    return this;
  }

  expectGlobCount(
    pattern: string,
    opts: { min?: number; max?: number; equals?: number; name?: string } = {},
  ): this {
    const args: Record<string, any> = { pattern };
    if (opts.min !== undefined) args.min = opts.min;
    if (opts.max !== undefined) args.max = opts.max;
    if (opts.equals !== undefined) args.equals = opts.equals;
    this._assertions.push(
      makeAssertionSpec({ kind: "glob_count", args, name: opts.name ?? null }),
    );
    return this;
  }

  expectJson(
    path: string,
    query: string,
    opts: { equals?: unknown; exists?: boolean; name?: string } = {},
  ): this {
    const args: Record<string, any> = { path, query };
    if ("equals" in opts) args.equals = opts.equals;
    if ("exists" in opts) args.exists = opts.exists;
    this._assertions.push(
      makeAssertionSpec({ kind: "json_path", args, name: opts.name ?? null }),
    );
    return this;
  }

  /** Generic escape hatch for any registered assertion kind. */
  expect(kind: string, args: Record<string, any> = {}, name?: string): this {
    this._assertions.push(makeAssertionSpec({ kind, args, name: name ?? null }));
    return this;
  }

  // ---- telemetry assertions (tool calls, file access, tokens) -----------

  /** Assert a tool was invoked (default: at least once). */
  expectToolCalled(
    name: string,
    opts: {
      min?: number;
      max?: number;
      equals?: number;
      argsContain?: string;
      ignoreCase?: boolean;
      name?: string;
    } = {},
  ): this {
    const args: Record<string, any> = { name };
    if (opts.min !== undefined) args.min = opts.min;
    if (opts.max !== undefined) args.max = opts.max;
    if (opts.equals !== undefined) args.equals = opts.equals;
    if (opts.argsContain !== undefined) args.args_contain = opts.argsContain;
    if (opts.ignoreCase) args.ignore_case = true;
    this._assertions.push(
      makeAssertionSpec({ kind: "tool_called", args, name: opts.name ?? null }),
    );
    return this;
  }

  /** Assert a tool was never invoked (optionally only with matching args). */
  expectToolNotCalled(
    name: string,
    opts: { argsContain?: string; ignoreCase?: boolean; name?: string } = {},
  ): this {
    const args: Record<string, any> = { name };
    if (opts.argsContain !== undefined) args.args_contain = opts.argsContain;
    if (opts.ignoreCase) args.ignore_case = true;
    this._assertions.push(
      makeAssertionSpec({
        kind: "tool_not_called",
        args,
        name: opts.name ?? null,
      }),
    );
    return this;
  }

  /** Assert at least one file matching each pattern was read. */
  expectFileRead(paths: TextArg, opts: { name?: string } = {}): this {
    return this.fileAccess("file_read", paths, opts.name);
  }

  /** Assert no read touched any matching file. */
  expectFileNotRead(paths: TextArg, opts: { name?: string } = {}): this {
    return this.fileAccess("file_not_read", paths, opts.name);
  }

  /** Assert at least one file matching each pattern was written/created. */
  expectFileWritten(paths: TextArg, opts: { name?: string } = {}): this {
    return this.fileAccess("file_written", paths, opts.name);
  }

  /** Assert no write/create touched any matching file (catches write-then-delete). */
  expectFileNotWritten(paths: TextArg, opts: { name?: string } = {}): this {
    return this.fileAccess("file_not_written", paths, opts.name);
  }

  /** Assert the run stayed within a token budget / allowed model set. */
  expectTokenBudget(
    opts: {
      maxTotal?: number;
      maxInput?: number;
      maxOutput?: number;
      models?: string[];
      name?: string;
    } = {},
  ): this {
    const args: Record<string, any> = {};
    if (opts.maxTotal !== undefined) args.max_total = opts.maxTotal;
    if (opts.maxInput !== undefined) args.max_input = opts.maxInput;
    if (opts.maxOutput !== undefined) args.max_output = opts.maxOutput;
    if (opts.models !== undefined) args.models = [...opts.models];
    this._assertions.push(
      makeAssertionSpec({ kind: "token_budget", args, name: opts.name ?? null }),
    );
    return this;
  }

  /** Register a custom predicate `predicate(ctx) -> boolean | [boolean, string]`. */
  check(name: string, predicate: (ctx: any) => boolean | [boolean, string]): this {
    this._assertions.push(
      makeAssertionSpec({ kind: "custom", name, predicate }),
    );
    return this;
  }

  judge(
    criteria: string,
    opts: {
      artifact?: string | null;
      threshold?: number;
      name?: string;
      golden?: string[];
    } = {},
  ): this {
    this._judges.push(
      makeJudgeSpec({
        criteria,
        artifact: opts.artifact ?? null,
        threshold: opts.threshold ?? 0.7,
        name: opts.name ?? "judge",
        golden: [...(opts.golden ?? [])],
      }),
    );
    return this;
  }

  metric(
    name: string,
    value: number | string | ((ctx: any) => number),
    opts: {
      direction?: string;
      unit?: string;
      baseline?: string | number;
      baselineValue?: number | null;
      window?: number;
      tolerance?: number;
      tolerancePct?: number;
      gate?: boolean;
    } = {},
  ): this {
    const baseline = opts.baseline ?? "last";
    let strategy: string;
    let baselineValue = opts.baselineValue ?? null;
    if (typeof baseline === "number") {
      strategy = "pinned";
      baselineValue = Number(baseline);
    } else {
      strategy = baseline;
    }
    this._metrics.push(
      makeMetricSpec({
        name,
        value,
        direction: opts.direction ?? "higher_is_better",
        unit: opts.unit ?? "",
        baseline_strategy: strategy,
        baseline: baselineValue,
        window: opts.window ?? 5,
        tolerance: opts.tolerance ?? 0.0,
        tolerance_pct: opts.tolerancePct ?? 0.0,
        gate: opts.gate ?? false,
      }),
    );
    return this;
  }

  // ---- compile ----------------------------------------------------------

  private textAssert(
    kind: string,
    text: TextArg,
    path: string | undefined,
    name: string | undefined,
    ignoreCase: boolean,
  ): this {
    const args: Record<string, any> = {};
    if (Array.isArray(text)) {
      args.all = [...text];
    } else {
      args.text = text;
    }
    if (path) args.path = path;
    if (ignoreCase) args.ignore_case = true;
    this._assertions.push(makeAssertionSpec({ kind, args, name: name ?? null }));
    return this;
  }

  private fileAccess(kind: string, paths: TextArg, name?: string): this {
    const list = Array.isArray(paths) ? [...paths] : [paths];
    this._assertions.push(
      makeAssertionSpec({ kind, args: { paths: list }, name: name ?? null }),
    );
    return this;
  }

  build(): EvalSpec {
    return makeEvalSpec({
      name: this._name,
      target: this._target,
      kind: this._kind,
      tags: this._tags,
      timeout: this._timeout,
      summary: this._summary,
      description: this._description || this._summary,
      setup: makeSetupSpec({ stage: this._stage, files: this._files }),
      act: this._act,
      assertions: this._assertions,
      judges: this._judges,
      metrics: this._metrics,
    });
  }
}
