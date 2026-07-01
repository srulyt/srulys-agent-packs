/**
 * Static linter for agent pack contracts (dependency-free Node port of the
 * legacy `scripts/lint_pack.py`).
 *
 * Runs once per pack (not once per eval) and validates that each `.agent.md`
 * file has well-formed YAML front-matter declaring the fields the multi-agent
 * system relies on. Consumed both from the CLI and from the structural eval
 * `evals/static/pack_contract.eval.ts`.
 *
 * Usage:
 *   node scripts/lint-pack.mjs <pack>     # one pack under agent-packs/
 *   node scripts/lint-pack.mjs --all      # every pack
 *
 * Exit codes: 0 = clean, 1 = violations found, 2 = bad invocation.
 */

import { readFileSync, existsSync, statSync, readdirSync } from "node:fs";
import * as path from "node:path";
import { fileURLToPath } from "node:url";

const HERE = path.dirname(fileURLToPath(import.meta.url));
export const REPO_ROOT = path.resolve(HERE, "..");
const PACKS_ROOT = path.join(REPO_ROOT, "agent-packs");

// Required front-matter keys for every .agent.md file.
const REQUIRED_AGENT_FIELDS = ["description", "tools"];

// Tools allow-list. Any tool name outside this set is flagged (warn).
const KNOWN_TOOLS = new Set([
  "read", "edit", "search", "execute", "agent", "shell",
  "create", "view", "grep", "glob", "task",
  "write", "delete", "list", "session_store_sql",
  "web_fetch", "web_search", "web", "data",
  "*",
]);

// Soft caps from the factory's quality standards (warnings, not errors).
const AGENT_MAX_CHARS = 30_000;
const SKILL_MAX_WORDS = 5_000;

export class Issue {
  /** @param {"error"|"warn"} severity @param {string} filePath @param {string} message */
  constructor(severity, filePath, message) {
    this.severity = severity;
    this.path = filePath;
    this.message = message;
  }

  format() {
    let rel = this.path;
    if (path.isAbsolute(rel)) rel = path.relative(REPO_ROOT, rel);
    rel = rel.split(path.sep).join("/");
    return `${this.severity.toUpperCase().padEnd(5)} ${rel}: ${this.message}`;
  }
}

/** A pack is an agent pack iff it ships `.github/agents/` or `.github/skills/`. */
export function isAgentPack(packDir) {
  return (
    existsSync(path.join(packDir, ".github", "agents")) ||
    existsSync(path.join(packDir, ".github", "skills"))
  );
}

function isDir(p) {
  try {
    return statSync(p).isDirectory();
  } catch {
    return false;
  }
}

function globFiles(dir, predicate, recurse) {
  /** @type {string[]} */
  const out = [];
  if (!isDir(dir)) return out;
  for (const entry of readdirSync(dir, { withFileTypes: true })) {
    const full = path.join(dir, entry.name);
    if (entry.isDirectory()) {
      if (recurse) out.push(...globFiles(full, predicate, recurse));
    } else if (predicate(entry.name)) {
      out.push(full);
    }
  }
  return out.sort();
}

/** @returns {Issue[]} */
export function lintPack(packDir) {
  /** @type {Issue[]} */
  const issues = [];

  if (!isDir(packDir)) {
    return [new Issue("error", packDir, "Pack directory does not exist")];
  }
  if (!isAgentPack(packDir)) {
    return []; // Roo-only / unknown layout: out of scope, skip silently.
  }
  if (!existsSync(path.join(packDir, "README.md"))) {
    issues.push(new Issue("error", packDir, "Pack is missing README.md"));
  }

  const agentsDir = path.join(packDir, ".github", "agents");
  const skillsDir = path.join(packDir, ".github", "skills");

  for (const agentFile of globFiles(agentsDir, (n) => n.endsWith(".agent.md"), false)) {
    issues.push(...lintAgentFile(agentFile));
  }
  for (const skillMd of globFiles(skillsDir, (n) => n === "SKILL.md", true)) {
    issues.push(...lintSkillFile(skillMd));
  }
  return issues;
}

function lintAgentFile(filePath) {
  /** @type {Issue[]} */
  const issues = [];
  const text = readFileSync(filePath, "utf-8");

  if (text.length > AGENT_MAX_CHARS) {
    issues.push(
      new Issue(
        "warn",
        filePath,
        `Agent file is ${text.length} chars (>${AGENT_MAX_CHARS} soft cap)`,
      ),
    );
  }

  const [frontMatter, body] = splitFrontMatter(text);
  if (frontMatter === null) {
    issues.push(new Issue("error", filePath, "Missing YAML front-matter (--- block)"));
    return issues;
  }

  let meta;
  try {
    meta = parseFrontMatter(frontMatter);
  } catch (exc) {
    issues.push(new Issue("error", filePath, `Invalid YAML front-matter: ${exc}`));
    return issues;
  }
  if (meta === null || typeof meta !== "object" || Array.isArray(meta)) {
    issues.push(new Issue("error", filePath, "Front-matter must be a mapping"));
    return issues;
  }

  for (const field of REQUIRED_AGENT_FIELDS) {
    if (!(field in meta)) {
      issues.push(new Issue("error", filePath, `Front-matter missing required key: ${field}`));
    }
  }

  const desc = meta.description ?? "";
  if (typeof desc === "string" && desc.trim().length < 30) {
    issues.push(
      new Issue(
        "warn",
        filePath,
        "Description is very short (< 30 chars); descriptions need triggers/keywords",
      ),
    );
  }

  const tools = meta.tools;
  if (tools !== undefined && tools !== null) {
    if (!Array.isArray(tools)) {
      issues.push(new Issue("error", filePath, "tools must be a YAML list"));
    } else {
      for (const t of tools) {
        if (typeof t !== "string") {
          issues.push(new Issue("error", filePath, `tools entry not a string: ${JSON.stringify(t)}`));
          continue;
        }
        if (KNOWN_TOOLS.has(t) || t.includes("-")) continue; // allow MCP-prefixed tools
        issues.push(new Issue("warn", filePath, `Unknown tool: ${JSON.stringify(t)}`));
      }
    }
  }

  if (!body.trim()) {
    issues.push(new Issue("error", filePath, "Agent body is empty"));
  }
  return issues;
}

function lintSkillFile(filePath) {
  /** @type {Issue[]} */
  const issues = [];
  const text = readFileSync(filePath, "utf-8");
  const wordCount = text.split(/\s+/).filter(Boolean).length;
  if (wordCount > SKILL_MAX_WORDS) {
    issues.push(
      new Issue(
        "warn",
        filePath,
        `Skill is ${wordCount} words (>${SKILL_MAX_WORDS} soft cap); ` +
          "consider splitting into reference docs",
      ),
    );
  }
  return issues;
}

/** @returns {[string|null, string]} (frontMatterYaml, body) or (null, fullText). */
function splitFrontMatter(text) {
  if (!text.startsWith("---")) return [null, text];
  const end = text.indexOf("\n---", 3);
  if (end === -1) return [null, text];
  return [text.slice(3, end).replace(/^\n+/, ""), text.slice(end + 4).replace(/^\n+/, "")];
}

function stripQuotes(v) {
  const s = v.trim();
  if (s.length >= 2 && ((s[0] === '"' && s.endsWith('"')) || (s[0] === "'" && s.endsWith("'")))) {
    return s.slice(1, -1);
  }
  return s;
}

/**
 * Minimal YAML front-matter parser: flat `key: value` pairs, block lists
 * (`- item`), and flow lists (`[a, b]`). Sufficient for `.agent.md` schemas;
 * avoids a yaml dependency so the linter runs with zero installs.
 * @returns {Record<string, unknown>}
 */
export function parseFrontMatter(fm) {
  const lines = fm.replace(/\r\n?/g, "\n").split("\n");
  /** @type {Record<string, unknown>} */
  const out = {};
  for (let i = 0; i < lines.length; i++) {
    const line = lines[i];
    if (!line.trim() || line.trimStart().startsWith("#")) continue;
    if (/^\s/.test(line)) continue; // handled by look-ahead below
    const m = /^([^:\s][^:]*):(.*)$/.exec(line);
    if (!m) continue;
    const key = m[1].trim();
    const rest = m[2].trim();
    if (rest === "") {
      // Block list or nested mapping via look-ahead.
      /** @type {string[]} */
      const items = [];
      let isMapping = false;
      let j = i + 1;
      for (; j < lines.length; j++) {
        const nxt = lines[j];
        if (!nxt.trim()) continue;
        if (!/^\s/.test(nxt)) break; // dedent -> next top-level key
        const li = /^\s+-\s*(.*)$/.exec(nxt);
        if (li) {
          items.push(stripQuotes(li[1]));
        } else {
          isMapping = true; // indented `k: v` -> nested map (contents ignored)
        }
      }
      out[key] = isMapping && items.length === 0 ? {} : items;
      i = j - 1;
    } else if (rest.startsWith("[") && rest.endsWith("]")) {
      const inner = rest.slice(1, -1).trim();
      out[key] = inner ? inner.split(",").map((x) => stripQuotes(x)) : [];
    } else {
      const scalar = stripQuotes(rest);
      if (scalar === "true") out[key] = true;
      else if (scalar === "false") out[key] = false;
      else out[key] = scalar;
    }
  }
  return out;
}

/** Return Copilot packs only (skips Roo-only packs), sorted by path. */
export function discoverPacks() {
  if (!isDir(PACKS_ROOT)) return [];
  return readdirSync(PACKS_ROOT, { withFileTypes: true })
    .filter((e) => e.isDirectory())
    .map((e) => path.join(PACKS_ROOT, e.name))
    .filter(isAgentPack)
    .sort();
}

function main(argv) {
  const args = argv.slice(2);
  const all = args.includes("--all");
  const strict = args.includes("--strict");
  const positional = args.filter((a) => !a.startsWith("--"));

  if (!all && positional.length === 0) {
    console.error("Specify a pack name or --all");
    return 2;
  }

  const packs = all ? discoverPacks() : [path.join(PACKS_ROOT, positional[0])];
  /** @type {Issue[]} */
  const allIssues = [];
  for (const pack of packs) allIssues.push(...lintPack(pack));

  for (const issue of allIssues) console.log(issue.format());

  const hasErrors = allIssues.some((i) => i.severity === "error");
  const hasWarns = allIssues.some((i) => i.severity === "warn");
  if (hasErrors || (strict && hasWarns)) {
    console.error(`\n${allIssues.length} issue(s) found.`);
    return 1;
  }
  return 0;
}

// Run as a script (not when imported by an eval).
if (import.meta.url === `file://${process.argv[1]}` || fileURLToPath(import.meta.url) === process.argv[1]) {
  process.exit(main(process.argv));
}
