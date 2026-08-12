/**
 * Per-test isolated workspaces for evals (repo-agnostic).
 *
 * A {@link Workspace} wraps a temporary directory the SUT is launched from and
 * provides staging helpers, SUT drivers, and inspection helpers. Agents and
 * skills are located by {@link module:discovery}, which understands both
 * `.github/agents` and plugin-root `agents/` / `skills/` layouts.
 */

import { spawnSync } from "node:child_process";
import {
  cpSync,
  copyFileSync,
  existsSync,
  mkdirSync,
  readFileSync,
  rmSync,
  statSync,
} from "node:fs";
import * as path from "node:path";
import fg from "fast-glob";
import { findJudgeAgentFile, findRepoRoot } from "./config.js";
import * as discovery from "./discovery.js";
import { getRunner } from "./runners/index.js";
import type { RunResult, SUTRunner } from "./runners/base.js";

export interface WorkspaceOptions {
  root: string;
  logsDir: string;
  runner?: SUTRunner;
  repoRoot?: string;
  /** Explicit per-run SUT timeout override (seconds) from `--sut-timeout`. */
  sutTimeout?: number | null;
}

/** Raised by {@link Workspace.findOne} when zero matches are found. */
export class FixtureMissingError extends Error {
  pattern: string;
  workspaceRoot: string;
  suggestions: string[];

  constructor(opts: {
    pattern: string;
    workspaceRoot: string;
    suggestions: string[];
  }) {
    const suggestionBlock = opts.suggestions.length
      ? "\n  closest paths in workspace:\n    - " +
        opts.suggestions.join("\n    - ")
      : "\n  (workspace appears empty)";
    super(
      `Expected exactly 1 match for '${opts.pattern}' in workspace at ` +
        `${opts.workspaceRoot}, got 0.\n` +
        `  This usually means the fixture file is missing, or the agent ` +
        `failed to create the artefact (check the agent log).` +
        suggestionBlock,
    );
    this.pattern = opts.pattern;
    this.workspaceRoot = opts.workspaceRoot;
    this.suggestions = opts.suggestions;
    this.name = "FixtureMissingError";
  }
}

/** Isolated working directory for a single eval test. */
export class Workspace {
  root: string;
  logsDir: string;
  runner: SUTRunner;
  repoRoot: string;
  sutTimeout: number | null;

  constructor(opts: WorkspaceOptions) {
    this.root = opts.root;
    this.logsDir = opts.logsDir;
    mkdirSync(this.root, { recursive: true });
    mkdirSync(this.logsDir, { recursive: true });
    this.runner = opts.runner ?? getRunner();
    this.repoRoot = opts.repoRoot ?? findRepoRoot();
    this.sutTimeout = opts.sutTimeout ?? null;
    if (!existsSync(path.join(this.root, ".git"))) {
      try {
        spawnSync("git", ["init", "-q"], { cwd: this.root });
      } catch {
        // git not installed — harmless.
      }
    }
  }

  // ---- staging ----------------------------------------------------------

  /** Stage a discovered agent (and, if it's a plugin, its skills). */
  stageAgent(name: string, opts: { includeSkills?: boolean } = {}): void {
    const includeSkills = opts.includeSkills ?? true;
    const info = discovery.findAgent(name, this.repoRoot);
    copyTree(info.agents_dir, path.join(this.root, ".github", "agents"), true);
    if (includeSkills) {
      for (const src of supportDirsForAgent(info)) {
        copyTree(
          src,
          path.join(this.root, ".github", path.basename(src)),
          true,
        );
      }
    }
  }

  /** Stage exactly one discovered skill (no agents). */
  stageSkill(name: string): void {
    const info = discovery.findSkill(name, this.repoRoot);
    copyTree(info.path, path.join(this.root, ".github", "skills", name), false);
  }

  /** Stage every agent and skill discovered in the repo. */
  stageAll(): void {
    for (const agent of discovery.discoverAgents(this.repoRoot)) {
      copyTree(
        agent.agents_dir,
        path.join(this.root, ".github", "agents"),
        true,
      );
    }
    for (const skill of discovery.discoverSkills(this.repoRoot)) {
      copyTree(
        skill.path,
        path.join(this.root, ".github", "skills", skill.name),
        false,
      );
    }
  }

  /** Stage evalpilot's bundled `eval-judge` agent into the workspace. */
  stageJudgeAgent(): void {
    const agentFile = findJudgeAgentFile();
    if (agentFile === null) {
      throw new Error(
        "Bundled eval-judge agent not found. Set EVALPILOT_JUDGE_AGENT to its " +
          "path or reinstall evalpilot.",
      );
    }
    const dest = path.join(this.root, ".github", "agents");
    mkdirSync(dest, { recursive: true });
    copyFileSync(agentFile, path.join(dest, path.basename(agentFile)));
  }

  /** Copy `src` (file or dir) into `workspace/<destSubdir>`. */
  stageFiles(src: string, destSubdir = "."): void {
    const target = path.resolve(this.root, destSubdir);
    mkdirSync(target, { recursive: true });
    if (statSync(src).isDirectory()) {
      copyTree(src, target, true);
    } else {
      copyFileSync(src, path.join(target, path.basename(src)));
    }
  }

  // ---- driving the SUT --------------------------------------------------

  async runAgent(
    prompt: string,
    opts: { agent?: string | null; timeout?: number; logName?: string } = {},
  ): Promise<RunResult> {
    return this.runner.runAgent({
      prompt,
      workspace: this.root,
      agent: opts.agent ?? null,
      log_path: path.join(this.logsDir, `${opts.logName ?? "agent"}.log`),
      timeout: opts.timeout ?? 600.0,
      sut_timeout_override: this.sutTimeout,
    });
  }

  async runSkill(
    skill: string,
    prompt: string,
    opts: { timeout?: number; logName?: string } = {},
  ): Promise<RunResult> {
    return this.runner.runSkill({
      skill,
      prompt,
      workspace: this.root,
      log_path: path.join(this.logsDir, `${opts.logName ?? "skill"}.log`),
      timeout: opts.timeout ?? 300.0,
      sut_timeout_override: this.sutTimeout,
    });
  }

  // ---- inspection -------------------------------------------------------

  glob(pattern: string): string[] {
    return fg
      .sync(pattern, { cwd: this.root, dot: true, absolute: true })
      .map((p) => path.normalize(p))
      .sort();
  }

  /** Return the single match for `pattern`; throw if 0 or >1 found. */
  findOne(pattern: string): string {
    const matches = this.glob(pattern);
    if (matches.length === 1) return matches[0]!;
    if (matches.length === 0) {
      throw new FixtureMissingError({
        pattern,
        workspaceRoot: this.root,
        suggestions: suggestClosePaths(this.root, pattern),
      });
    }
    throw new Error(
      `Expected exactly 1 match for '${pattern}' in workspace, got ` +
        `${matches.length}: ${JSON.stringify(matches)}`,
    );
  }

  read(relativePath: string): string {
    return readFileSync(path.join(this.root, relativePath), "utf-8");
  }
}

// ---- internal helpers ---------------------------------------------------

function suggestClosePaths(root: string, pattern: string, n = 5): string[] {
  const bare =
    pattern.replace(/[*?]/g, "").replace(/^[/\\]+|[/\\]+$/g, "") || pattern;
  let candidates: string[];
  try {
    candidates = fg
      .sync("**/*", { cwd: root, dot: true, onlyFiles: true })
      .map((p) => p.replace(/\\/g, "/"));
  } catch {
    return [];
  }
  return closeMatches(bare, candidates, n, 0.3);
}

/** Approximate difflib.get_close_matches using a similarity ratio. */
function closeMatches(
  word: string,
  possibilities: string[],
  n: number,
  cutoff: number,
): string[] {
  const scored = possibilities
    .map((p) => ({ p, score: similarity(word.toLowerCase(), p.toLowerCase()) }))
    .filter((x) => x.score >= cutoff)
    .sort((a, b) => b.score - a.score);
  return scored.slice(0, n).map((x) => x.p);
}

/** SequenceMatcher-style ratio: 2*M / (len(a)+len(b)). */
function similarity(a: string, b: string): number {
  if (!a.length && !b.length) return 1;
  const matches = lcsLength(a, b);
  return (2 * matches) / (a.length + b.length);
}

function lcsLength(a: string, b: string): number {
  const m = a.length;
  const k = b.length;
  let prev = new Array<number>(k + 1).fill(0);
  for (let i = 1; i <= m; i++) {
    const curr = new Array<number>(k + 1).fill(0);
    for (let j = 1; j <= k; j++) {
      curr[j] =
        a[i - 1] === b[j - 1]
          ? prev[j - 1]! + 1
          : Math.max(prev[j]!, curr[j - 1]!);
    }
    prev = curr;
  }
  return prev[k]!;
}

/** Copy `src` directory into `dest`. If `merge`, keep existing files. */
function copyTree(src: string, dest: string, merge: boolean): void {
  if (!merge && existsSync(dest)) {
    rmSync(dest, { recursive: true, force: true });
  }
  mkdirSync(dest, { recursive: true });
  cpSync(src, dest, { recursive: true, force: true });
}

/** Return skills/instructions dirs that should be staged with an agent. */
function supportDirsForAgent(info: discovery.AgentInfo): string[] {
  let base: string;
  if (info.plugin_root !== null) {
    base = info.plugin_root;
  } else if (path.basename(path.dirname(info.agents_dir)) === ".github") {
    base = path.dirname(info.agents_dir);
  } else {
    return [];
  }
  const out: string[] = [];
  for (const sub of ["skills", "instructions"]) {
    const src = path.join(base, sub);
    if (existsSync(src)) out.push(src);
  }
  return out;
}
