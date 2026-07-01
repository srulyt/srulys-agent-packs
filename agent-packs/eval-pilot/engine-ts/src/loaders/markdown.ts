/**
 * Parse a Markdown `*.eval.md` file into an {@link EvalSpec}.
 *
 * A spec reads top-to-bottom as arrange → act → assert. Prose (prompts, judge
 * criteria) is plain text; structured knobs live in small fenced `yaml` blocks.
 */

import { readFileSync } from "node:fs";
import * as path from "node:path";
import yaml from "js-yaml";
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
  type SetupSpec,
} from "../spec.js";

const FRONTMATTER = /^\ufeff?---\s*\n([\s\S]*?)\n---\s*\n/;
const FENCE = /```([^\n`]*)\n([\s\S]*?)```/g;
const HEADING = /^(#{1,6})\s+(.*)$/gm;

const LIST_KINDS = new Set([
  "contains",
  "not_contains",
  "prose_contains",
  "stdout_contains",
  "matches",
  "glob_count",
  "json_path",
  "json_empty",
  "section_contains",
  "section_not_contains",
  "file_exists",
  "file_absent",
]);

/** Raised when a `*.eval.md` file cannot be parsed into a spec. */
export class EvalParseError extends Error {}

/** Load and parse a `*.eval.md` file from disk. */
export function loadMarkdownEval(specPath: string): EvalSpec {
  const text = readFileSync(specPath, "utf-8");
  const spec = parseMarkdownEval(text, specPath);
  spec.base_dir = path.dirname(specPath);
  return spec;
}

/** Parse `*.eval.md` source text into an {@link EvalSpec}. */
export function parseMarkdownEval(text: string, specPath?: string): EvalSpec {
  const [front, body] = splitFrontmatter(text);
  const { title, summary: blockquote, sections } = splitSections(body);

  const name = front.name || slug(title) || "unnamed-eval";
  const kind = String(front.kind ?? "none").toLowerCase() as EvalKind;
  const summary = String(front.summary ?? blockquote ?? "").trim();

  const descSection = sections.get("description");
  let description = "";
  if (descSection !== undefined) description = descSection.prose().trim();
  if (!description) description = String(front.description ?? "").trim();

  const setup = parseSetup(sections.get("setup"));
  const act = parseAct(sections.get("act"), front);
  const { assertions, judges, metrics } = parseAssert(sections.get("assert"));

  return makeEvalSpec({
    name,
    target: front.target ?? null,
    kind,
    tags: asList(front.tags).map(String),
    timeout: Number(front.timeout ?? 600),
    summary,
    description: description || summary,
    setup,
    act,
    assertions,
    judges,
    metrics,
    spec_path: specPath ?? null,
    base_dir: specPath ? path.dirname(specPath) : null,
  });
}

// ---- structural parsing -------------------------------------------------

function splitFrontmatter(text: string): [Record<string, any>, string] {
  const m = FRONTMATTER.exec(text);
  if (!m) return [{}, text];
  let data: unknown;
  try {
    data = yaml.load(m[1]!) ?? {};
  } catch (exc) {
    throw new EvalParseError(`invalid frontmatter YAML: ${(exc as Error).message}`);
  }
  if (typeof data !== "object" || data === null || Array.isArray(data)) {
    throw new EvalParseError("frontmatter must be a YAML mapping");
  }
  return [data as Record<string, any>, text.slice(m.index + m[0].length)];
}

class Section {
  raw: string;
  blocks: Array<[string, string]>;

  constructor(raw: string) {
    this.raw = raw;
    this.blocks = [];
    for (const m of raw.matchAll(new RegExp(FENCE.source, "g"))) {
      this.blocks.push([m[1]!.trim().toLowerCase(), m[2]!]);
    }
  }

  block(lang: string): string | null {
    for (const [blang, content] of this.blocks) {
      if (blang === lang) return content;
    }
    return null;
  }

  /** Section text with fenced blocks and blockquotes stripped. */
  prose(): string {
    const stripped = this.raw.replace(new RegExp(FENCE.source, "g"), "");
    const lines = stripped
      .split("\n")
      .filter((ln) => !ln.trim().startsWith(">"));
    return lines.join("\n").trim();
  }
}

interface SplitResult {
  title: string;
  summary: string;
  sections: Map<string, Section>;
}

function splitSections(body: string): SplitResult {
  let title = "";
  let summary = "";
  const sections = new Map<string, Section>();

  const masked = maskFences(body);
  const matches = [...masked.matchAll(new RegExp(HEADING.source, "gm"))];
  const firstStart = matches.length ? matches[0]!.index! : body.length;
  const preamble = body.slice(0, firstStart);

  for (const h of matches) {
    const level = h[1]!.length;
    const headingText = h[2]!.trim();
    if (level === 1 && !title) title = headingText;
  }
  if (!title) {
    const m = /^#\s+(.*)$/m.exec(preamble);
    if (m) title = m[1]!.trim();
  }

  // Collect level-2 sections (## Setup / ## Act / ## Assert ...).
  const h2 = matches.filter((h) => h[1]!.length === 2);
  for (let i = 0; i < h2.length; i++) {
    const h = h2[i]!;
    const start = h.index! + h[0].length;
    const end = i + 1 < h2.length ? h2[i + 1]!.index! : body.length;
    const nm = h[2]!.trim().toLowerCase();
    sections.set(nm, new Section(body.slice(start, end)));
  }

  // The `> summary` blockquote lives above the first ## section.
  const headerEnd = h2.length ? h2[0]!.index! : body.length;
  const qm = /^>\s?(.*)$/m.exec(body.slice(0, headerEnd));
  if (qm) summary = qm[1]!.trim();

  return { title, summary, sections };
}

/** Blank fenced regions while preserving length + newline positions. */
function maskFences(text: string): string {
  return text.replace(new RegExp(FENCE.source, "g"), (block) =>
    [...block].map((ch) => (ch === "\n" ? "\n" : " ")).join(""),
  );
}

// ---- section builders ---------------------------------------------------

function parseSetup(section: Section | undefined): SetupSpec {
  if (section === undefined) return makeSetupSpec();
  const raw = section.block("yaml") ?? section.block("json");
  let data = raw ? parseYaml(raw) : {};
  if (data === null || data === undefined) data = {};
  if (typeof data !== "object" || Array.isArray(data)) {
    throw new EvalParseError("## Setup yaml block must be a mapping");
  }
  const d = data as Record<string, any>;
  const stageData = d.stage ?? {};
  const stage = makeStageSpec({
    agent: stageData.agent ?? null,
    skill: stageData.skill ?? null,
    all: Boolean(stageData.all ?? false),
    include_skills: Boolean(stageData.include_skills ?? true),
  });
  const files: FileCopy[] = [];
  for (const f of asList(d.files)) {
    if (typeof f === "string") {
      files.push(makeFileCopy(f));
    } else if (f && typeof f === "object") {
      files.push(makeFileCopy(String(f.copy), String(f.dest ?? ".")));
    }
  }
  return makeSetupSpec({ stage, files });
}

function parseAct(
  section: Section | undefined,
  front: Record<string, any>,
): ActSpec | null {
  let prompt: string | null = null;
  let agent = front.agent ?? null;
  let skill = front.skill ?? null;
  let timeout = front.timeout ?? null;

  if (section !== undefined) {
    prompt = section.block("prompt");
    if (prompt === null) {
      const raw = section.block("yaml");
      if (raw) {
        const data = (parseYaml(raw) ?? {}) as Record<string, any>;
        prompt = data.prompt ?? null;
        agent = data.agent ?? agent;
        skill = data.skill ?? skill;
        timeout = data.timeout ?? timeout;
      }
    }
    if (prompt === null) prompt = section.prose();
  }
  if (!prompt) return null;
  const normalizedPrompt = prompt.endsWith("\n")
    ? prompt
    : prompt.replace(/\n+$/, "") + "\n";
  return makeActSpec({
    prompt: normalizedPrompt,
    agent,
    skill,
    timeout: timeout !== null && timeout !== undefined ? Number(timeout) : null,
  });
}

function parseAssert(section: Section | undefined): {
  assertions: AssertionSpec[];
  judges: JudgeSpec[];
  metrics: MetricSpec[];
} {
  const assertions: AssertionSpec[] = [];
  const judges: JudgeSpec[] = [];
  const metrics: MetricSpec[] = [];
  if (section === undefined) return { assertions, judges, metrics };

  const raw = section.block("yaml") ?? section.block("json");
  let data = raw ? parseYaml(raw) : {};
  if (data && (typeof data !== "object" || Array.isArray(data))) {
    throw new EvalParseError("## Assert yaml block must be a mapping");
  }
  const d = (data ?? {}) as Record<string, any>;

  // files: {exists: [...], absent: [...]}
  const files = d.files ?? {};
  if (files.exists) {
    assertions.push(
      makeAssertionSpec({
        kind: "file_exists",
        args: { paths: asList(files.exists) },
      }),
    );
  }
  if (files.absent) {
    assertions.push(
      makeAssertionSpec({
        kind: "file_absent",
        args: { paths: asList(files.absent) },
      }),
    );
  }

  // direct list kinds
  for (const kind of LIST_KINDS) {
    for (const entry of asList(d[kind])) {
      assertions.push(assertionFromEntry(kind, entry));
    }
  }

  // generic escape hatch
  for (const entry of asList(d.asserts)) {
    if (!entry || typeof entry !== "object" || !("kind" in entry)) {
      throw new EvalParseError("each 'asserts' entry needs a 'kind'");
    }
    const e = { ...(entry as Record<string, any>) };
    const kind = e.kind;
    const nm = e.name ?? null;
    delete e.kind;
    delete e.name;
    assertions.push(makeAssertionSpec({ kind, args: e, name: nm }));
  }

  // judges (single mapping or list)
  const judgeBlock = d.judge;
  if (judgeBlock !== undefined && judgeBlock !== null) {
    const entries = Array.isArray(judgeBlock) ? judgeBlock : [judgeBlock];
    for (const e of entries) judges.push(judgeFromEntry(e));
  }
  // standalone ```judge fenced block => criteria only
  const jc = section.block("judge");
  if (jc) judges.push(makeJudgeSpec({ criteria: jc.trim() }));

  for (const e of asList(d.metrics)) {
    metrics.push(metricFromEntry(e));
  }

  return { assertions, judges, metrics };
}

function assertionFromEntry(kind: string, entry: unknown): AssertionSpec {
  if (typeof entry === "string") {
    return makeAssertionSpec({ kind, args: { text: entry } });
  }
  if (entry && typeof entry === "object") {
    const e = { ...(entry as Record<string, any>) };
    const nm = e.name ?? null;
    delete e.name;
    return makeAssertionSpec({ kind, args: e, name: nm });
  }
  throw new EvalParseError(`invalid ${kind} entry: ${JSON.stringify(entry)}`);
}

function judgeFromEntry(e: any): JudgeSpec {
  if (!e || typeof e !== "object" || !("criteria" in e)) {
    throw new EvalParseError("each judge needs 'criteria'");
  }
  return makeJudgeSpec({
    criteria: String(e.criteria),
    artifact: e.artifact ?? null,
    threshold: Number(e.threshold ?? 0.7),
    name: String(e.name ?? "judge"),
    golden: asList(e.golden).map(String),
  });
}

function metricFromEntry(e: any): MetricSpec {
  if (!e || typeof e !== "object" || !("name" in e)) {
    throw new EvalParseError("each metric needs 'name'");
  }
  const baseline = e.baseline ?? "last";
  let baselineValue = e.baseline_value ?? null;
  const strategy = typeof baseline === "string" ? baseline : "pinned";
  if (typeof baseline === "number") baselineValue = Number(baseline);
  return makeMetricSpec({
    name: String(e.name),
    value: e.value,
    direction: String(e.direction ?? "higher_is_better"),
    unit: String(e.unit ?? ""),
    baseline_strategy: strategy,
    baseline: baselineValue,
    window: Number(e.window ?? 5),
    tolerance: Number(e.tolerance ?? 0.0),
    tolerance_pct: Number(e.tolerance_pct ?? 0.0),
    gate: Boolean(e.gate ?? false),
  });
}

// ---- small utilities ----------------------------------------------------

function parseYaml(raw: string): unknown {
  try {
    return yaml.load(raw);
  } catch (exc) {
    throw new EvalParseError(`invalid YAML block: ${(exc as Error).message}`);
  }
}

function asList(value: unknown): any[] {
  if (value === null || value === undefined) return [];
  if (Array.isArray(value)) return [...value];
  return [value];
}

function slug(text: string): string {
  return text
    .toLowerCase()
    .replace(/[^a-z0-9]+/g, "-")
    .replace(/^-+|-+$/g, "");
}
