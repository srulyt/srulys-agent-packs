/**
 * The {@link EvalSpec} — the compiled, engine-neutral description of one eval.
 *
 * Both authoring surfaces (the Markdown `*.eval.md` loader and the fluent
 * TypeScript builder) produce an {@link EvalSpec}. The executor consumes it.
 * Nothing here executes anything; this module is pure data plus a little
 * validation.
 *
 * Structure mirrors arrange → act → assert.
 */

export const AGENT = "agent";
export const SKILL = "skill";
export const NONE = "none";

export type EvalKind = typeof AGENT | typeof SKILL | typeof NONE;

/** What agents/skills to copy into the eval workspace. */
export interface StageSpec {
  agent: string | null;
  skill: string | null;
  all: boolean;
  include_skills: boolean;
}

export function makeStageSpec(init: Partial<StageSpec> = {}): StageSpec {
  return {
    agent: null,
    skill: null,
    all: false,
    include_skills: true,
    ...init,
  };
}

/** Copy fixture files into the workspace before the SUT runs. */
export interface FileCopy {
  copy: string; // source path/glob, relative to the spec's base_dir
  dest: string; // destination subdir inside the workspace
}

export function makeFileCopy(copy: string, dest = "."): FileCopy {
  return { copy, dest };
}

/** Arrange step: staging + fixture files. */
export interface SetupSpec {
  stage: StageSpec;
  files: FileCopy[];
}

export function makeSetupSpec(init: Partial<SetupSpec> = {}): SetupSpec {
  return {
    stage: init.stage ?? makeStageSpec(),
    files: init.files ?? [],
  };
}

/** Act step: drive the SUT with a prompt. */
export interface ActSpec {
  prompt: string;
  agent: string | null;
  skill: string | null;
  timeout: number | null;
}

export function makeActSpec(
  init: Partial<ActSpec> & Pick<ActSpec, "prompt">,
): ActSpec {
  return {
    agent: null,
    skill: null,
    timeout: null,
    ...init,
  };
}

/**
 * One assertion. `kind` selects a registered checker; `args` are its
 * parameters. `predicate` carries a callable for `kind='custom'`.
 */
export interface AssertionSpec {
  kind: string;
  args: Record<string, any>;
  name: string | null;
  predicate: ((ctx: any) => any) | null;
}

export function makeAssertionSpec(
  init: Partial<AssertionSpec> & Pick<AssertionSpec, "kind">,
): AssertionSpec {
  return {
    args: {},
    name: null,
    predicate: null,
    ...init,
  };
}

/** An LLM-as-judge assertion over an artifact (or stdout). */
export interface JudgeSpec {
  criteria: string;
  artifact: string | null; // file glob; null => use stdout
  threshold: number;
  name: string;
  golden: string[];
}

export function makeJudgeSpec(
  init: Partial<JudgeSpec> & Pick<JudgeSpec, "criteria">,
): JudgeSpec {
  return {
    artifact: null,
    threshold: 0.7,
    name: "judge",
    golden: [],
    ...init,
  };
}

/**
 * A numeric metric recorded to JSONL history and (optionally) gated.
 *
 * `value` may be a number, a callable (builder only), or a `$`-reference
 * string resolved by the executor: `$judge.score`, `$judge.<name>.score`,
 * `$duration`, `$stdout.words`, `$stdout.chars`, `$assertions.pass_rate`.
 */
export interface MetricSpec {
  name: string;
  value: number | string | ((ctx: any) => number);
  direction: string;
  unit: string;
  baseline_strategy: string;
  baseline: number | null;
  window: number;
  tolerance: number;
  tolerance_pct: number;
  gate: boolean;
}

export function makeMetricSpec(
  init: Partial<MetricSpec> & Pick<MetricSpec, "name" | "value">,
): MetricSpec {
  return {
    direction: "higher_is_better",
    unit: "",
    baseline_strategy: "last",
    baseline: null,
    window: 5,
    tolerance: 0.0,
    tolerance_pct: 0.0,
    gate: false,
    ...init,
  };
}

/** The full compiled description of one eval. */
export interface EvalSpec {
  name: string;
  target: string | null;
  kind: EvalKind;
  tags: string[];
  timeout: number;
  summary: string;
  description: string;
  setup: SetupSpec;
  act: ActSpec | null;
  assertions: AssertionSpec[];
  judges: JudgeSpec[];
  metrics: MetricSpec[];
  spec_path: string | null;
  base_dir: string | null;
}

/**
 * Build an {@link EvalSpec}, applying the same post-init normalization as the
 * Python dataclass `__post_init__` (kind validation + target-staging inference).
 */
export function makeEvalSpec(
  init: Partial<EvalSpec> & Pick<EvalSpec, "name">,
): EvalSpec {
  const spec: EvalSpec = {
    name: init.name,
    target: init.target ?? null,
    kind: init.kind ?? NONE,
    tags: init.tags ?? [],
    timeout: init.timeout ?? 600.0,
    summary: init.summary ?? "",
    description: init.description ?? "",
    setup: init.setup ?? makeSetupSpec(),
    act: init.act ?? null,
    assertions: init.assertions ?? [],
    judges: init.judges ?? [],
    metrics: init.metrics ?? [],
    spec_path: init.spec_path ?? null,
    base_dir: init.base_dir ?? null,
  };

  if (spec.kind !== AGENT && spec.kind !== SKILL && spec.kind !== NONE) {
    throw new Error(
      `eval ${JSON.stringify(spec.name)}: kind must be 'agent', 'skill', or ` +
        `'none', got ${JSON.stringify(spec.kind)}`,
    );
  }

  // Infer the staged target when the setup doesn't say otherwise.
  if (
    spec.target &&
    spec.kind === AGENT &&
    !spec.setup.stage.agent &&
    !spec.setup.stage.all
  ) {
    spec.setup.stage.agent = spec.target;
  }
  if (
    spec.target &&
    spec.kind === SKILL &&
    !spec.setup.stage.skill &&
    !spec.setup.stage.all
  ) {
    spec.setup.stage.skill = spec.target;
  }
  return spec;
}

/** True when the eval carries human-readable intent (summary/description). */
export function specHasProse(spec: EvalSpec): boolean {
  return Boolean(spec.summary.trim() || spec.description.trim());
}

/**
 * True for a structural eval: `kind: none` with no act prompt. These run
 * offline against the repo tree (no SUT) and only need assertions/judges/metrics.
 */
export function specIsStructural(spec: EvalSpec): boolean {
  return spec.kind === NONE && spec.act === null;
}

/** True when the eval has an act prompt and at least one check. */
export function specIsImplemented(spec: EvalSpec): boolean {
  const checksOk = Boolean(
    spec.assertions.length || spec.judges.length || spec.metrics.length,
  );
  if (specIsStructural(spec)) return checksOk;
  const actOk = spec.act !== null && Boolean(spec.act.prompt.trim());
  return actOk && checksOk;
}

/** A description-first draft: has prose but isn't implemented yet. */
export function specIsStub(spec: EvalSpec): boolean {
  return specHasProse(spec) && !specIsImplemented(spec);
}

/** Return a list of human-readable problems (empty when the spec is ok). */
export function validateSpec(spec: EvalSpec): string[] {
  const problems: string[] = [];
  if (!spec.name) problems.push("missing 'name'");
  const structural = specIsStructural(spec);
  if (!structural) {
    if (spec.act === null) {
      problems.push("missing an '## Act' prompt");
    } else if (!spec.act.prompt.trim()) {
      problems.push("act prompt is empty");
    }
  }
  if (spec.kind === AGENT && !(spec.setup.stage.agent || spec.setup.stage.all)) {
    problems.push("kind=agent but no agent is staged (set 'target')");
  }
  if (spec.kind === SKILL && !(spec.setup.stage.skill || spec.setup.stage.all)) {
    problems.push("kind=skill but no skill is staged (set 'target')");
  }
  if (!(spec.assertions.length || spec.judges.length || spec.metrics.length)) {
    problems.push("no assertions, judges, or metrics — nothing to check");
  }
  for (const m of spec.metrics) {
    if (!m.name) problems.push("a metric is missing 'name'");
  }
  return problems;
}
