/**
 * Discover agents and skills across Copilot's supported layouts.
 *
 * Understands every layout the Copilot CLI itself loads from, so evalpilot
 * works in an arbitrary repo:
 *
 * Agents (`<name>.agent.md`):
 *   - `.github/agents/`      (repo-level custom agents)
 *   - `<plugin>/agents/`     (plugin-root layout)
 *
 * Skills (`<name>/SKILL.md`):
 *   - `.github/skills/<name>/`
 *   - `<plugin>/skills/<name>/`
 */

import { existsSync, readdirSync, statSync } from "node:fs";
import * as path from "node:path";
import { findRepoRoot } from "./config.js";

const PRUNE = new Set<string>([
  ".git",
  ".hg",
  ".svn",
  "node_modules",
  "__pycache__",
  ".venv",
  "venv",
  ".pytest_cache",
  ".mypy_cache",
  "dist",
  "build",
  ".tox",
  "_runs",
  "_logs",
  "_metrics",
]);

/** A discovered custom agent. */
export interface AgentInfo {
  /** Agent name (filename stem, e.g. `eval-judge`). */
  name: string;
  /** Absolute path to the `.agent.md` file. */
  path: string;
  /** The `agents/` directory containing it. */
  agents_dir: string;
  /** Plugin root if this agent belongs to a plugin, else null. */
  plugin_root: string | null;
}

/** A discovered skill. */
export interface SkillInfo {
  /** Skill name (the `SKILL.md` parent directory name). */
  name: string;
  /** Absolute path to the skill directory (containing `SKILL.md`). */
  path: string;
  /** The `skills/` directory containing it. */
  skills_dir: string;
  /** Plugin root if this skill belongs to a plugin, else null. */
  plugin_root: string | null;
}

/** Yield every directory named `name` under `root` (pruned). */
function* iterDirs(root: string, name: string): Generator<string> {
  if (!existsSync(root)) return;
  const stack: string[] = [root];
  while (stack.length) {
    const dir = stack.pop()!;
    let entries: import("node:fs").Dirent[];
    try {
      entries = readdirSync(dir, { withFileTypes: true });
    } catch {
      continue;
    }
    if (path.basename(dir) === name) yield dir;
    for (const e of entries) {
      if (!e.isDirectory()) continue;
      if (PRUNE.has(e.name)) continue;
      stack.push(path.join(dir, e.name));
    }
  }
}

/** Return the nearest ancestor of `start` containing a `plugin.json`. */
function pluginRootFor(start: string): string | null {
  let current = path.resolve(start);
  // eslint-disable-next-line no-constant-condition
  while (true) {
    const manifest = path.join(current, "plugin.json");
    if (existsSync(manifest) && statSync(manifest).isFile()) return current;
    const parent = path.dirname(current);
    if (parent === current) break;
    current = parent;
  }
  return null;
}

function listFiles(dir: string, suffix: string): string[] {
  try {
    return readdirSync(dir, { withFileTypes: true })
      .filter((e) => e.isFile() && e.name.endsWith(suffix))
      .map((e) => path.join(dir, e.name))
      .sort();
  } catch {
    return [];
  }
}

function listSubdirsWithSkillMd(dir: string): string[] {
  try {
    return readdirSync(dir, { withFileTypes: true })
      .filter((e) => e.isDirectory())
      .map((e) => path.join(dir, e.name))
      .filter((d) => existsSync(path.join(d, "SKILL.md")))
      .sort();
  } catch {
    return [];
  }
}

/** Return all custom agents declared anywhere in the repo. */
export function discoverAgents(repoRoot?: string): AgentInfo[] {
  const rr = repoRoot ?? findRepoRoot();
  const seen = new Map<string, AgentInfo>();
  for (const agentsDir of iterDirs(rr, "agents")) {
    for (const f of listFiles(agentsDir, ".agent.md")) {
      const info: AgentInfo = {
        name: path.basename(f).slice(0, -".agent.md".length),
        path: path.resolve(f),
        agents_dir: path.resolve(agentsDir),
        plugin_root: pluginRootFor(agentsDir),
      };
      seen.set(info.path, info);
    }
  }
  return [...seen.values()].sort(
    (a, b) => a.name.localeCompare(b.name) || a.path.localeCompare(b.path),
  );
}

/** Return all skills declared anywhere in the repo. */
export function discoverSkills(repoRoot?: string): SkillInfo[] {
  const rr = repoRoot ?? findRepoRoot();
  const seen = new Map<string, SkillInfo>();
  for (const skillsDir of iterDirs(rr, "skills")) {
    for (const skillDir of listSubdirsWithSkillMd(skillsDir)) {
      const info: SkillInfo = {
        name: path.basename(skillDir),
        path: path.resolve(skillDir),
        skills_dir: path.resolve(skillsDir),
        plugin_root: pluginRootFor(skillsDir),
      };
      seen.set(info.path, info);
    }
  }
  return [...seen.values()].sort(
    (a, b) => a.name.localeCompare(b.name) || a.path.localeCompare(b.path),
  );
}

/** Return the single agent named `name` or throw. */
export function findAgent(name: string, repoRoot?: string): AgentInfo {
  const all = discoverAgents(repoRoot);
  const matches = all.filter((a) => a.name === name);
  if (matches.length === 1) return matches[0]!;
  if (matches.length === 0) {
    const available = all.map((a) => a.name).join(", ") || "(none)";
    throw new Error(`No agent named '${name}'. Available: ${available}`);
  }
  throw new Error(
    `Agent '${name}' is ambiguous across ${matches.length} locations: ` +
      JSON.stringify(matches.map((m) => m.path)),
  );
}

/** Return the single skill named `name` or throw. */
export function findSkill(name: string, repoRoot?: string): SkillInfo {
  const all = discoverSkills(repoRoot);
  const matches = all.filter((s) => s.name === name);
  if (matches.length === 1) return matches[0]!;
  if (matches.length === 0) {
    const available = all.map((s) => s.name).join(", ") || "(none)";
    throw new Error(`No skill named '${name}'. Available: ${available}`);
  }
  throw new Error(
    `Skill '${name}' is ambiguous across ${matches.length} locations: ` +
      JSON.stringify(matches.map((m) => m.path)),
  );
}
