/**
 * LLM-as-judge helper (repo-agnostic).
 *
 * Scores a single SUT artifact against free-form criteria by invoking the
 * bundled `eval-judge` agent through the configured {@link SUTRunner}. Returns a
 * {@link Verdict} with a `passed` boolean, a numeric `score` in [0, 1], and the
 * judge's reasoning + cited evidence.
 */

import { copyFileSync, mkdirSync, mkdtempSync, writeFileSync } from "node:fs";
import * as os from "node:os";
import * as path from "node:path";
import { findJudgeAgentFile } from "./config.js";
import { getRunner } from "./runners/index.js";
import { runOk } from "./runners/base.js";

export const DEFAULT_THRESHOLD = 0.7;

/** Structured judge response. */
export interface Verdict {
  passed: boolean;
  score: number;
  reasoning: string;
  evidence: Array<Record<string, unknown>>;
  raw_response: string;
}

/** Raised when the judge subprocess fails or returns unparsable output. */
export class JudgeError extends Error {}

export interface JudgeArgs {
  artifact: string;
  criteria: string;
  threshold?: number;
  golden?: string[];
  logDir?: string;
  timeout?: number;
}

/** Score `artifact` against `criteria` using the eval-judge agent. */
export async function judge(args: JudgeArgs): Promise<Verdict> {
  const threshold =
    args.threshold !== undefined
      ? args.threshold
      : Number(
          process.env.EVALPILOT_JUDGE_THRESHOLD ??
            process.env.EVAL_JUDGE_THRESHOLD ??
            DEFAULT_THRESHOLD,
        );

  const logDir =
    args.logDir ?? mkdtempSync(path.join(os.tmpdir(), "evalpilot-judge-"));
  mkdirSync(logDir, { recursive: true });

  const golden = args.golden ?? [];
  const prompt = buildPrompt(args.artifact, args.criteria, golden);
  writeFileSync(path.join(logDir, "judge-prompt.md"), prompt, "utf-8");

  const workspace = path.join(logDir, "_judge_ws");
  mkdirSync(workspace, { recursive: true });
  stageJudgeAgent(workspace);

  const runner = getRunner();
  const result = await runner.runAgent({
    prompt,
    workspace,
    agent: "eval-judge",
    log_path: path.join(logDir, "judge.log"),
    timeout: args.timeout ?? 180.0,
  });

  if (!runOk(result)) {
    throw new JudgeError(
      `Judge subprocess exited ${result.returncode}. ` +
        `See log: ${result.log_path}`,
    );
  }

  const parsed = extractJson(result.stdout);
  if (parsed === null) {
    throw new JudgeError(
      `Judge returned no parsable JSON. See log: ${result.log_path}\n` +
        `--- stdout ---\n${result.stdout.slice(0, 2000)}`,
    );
  }

  const score = Number(parsed.score ?? 0.0);
  return {
    passed: score >= threshold,
    score,
    reasoning: String(parsed.rationale ?? "").trim(),
    evidence: [...((parsed.evidence as unknown[]) ?? [])] as Array<
      Record<string, unknown>
    >,
    raw_response: result.stdout,
  };
}

// ---- prompt construction ------------------------------------------------

function buildPrompt(
  artifact: string,
  criteria: string,
  golden: string[],
): string {
  let goldenBlock = "";
  if (golden.length) {
    const parts = ["\n## Reference (golden)"];
    golden.forEach((g, i) => {
      parts.push(`\n### Reference ${i + 1}\n\`\`\`\n${g}\n\`\`\``);
    });
    goldenBlock = parts.join("\n");
  }
  return (
    `You are evaluating a single artifact against criteria. Read carefully and\n` +
    `score strictly. If criteria are unmet, score low. Cite concrete evidence.\n\n` +
    `Output **exactly one JSON object** on stdout with the schema:\n` +
    "```json\n" +
    `{\n  "score": 0.0,\n  "rationale": "short prose explanation",\n` +
    `  "evidence": [{"path": "artifact", "quote": "..."}]\n}\n` +
    "```\n\n" +
    `## Criteria\n${criteria.trim()}\n\n` +
    `## Artifact\n` +
    "```\n" +
    `${artifact}\n` +
    "```\n" +
    `${goldenBlock}\n`
  );
}

/** Find the first balanced JSON object in `text`. */
function extractJson(text: string): Record<string, any> | null {
  const trimmed = text.trim();
  try {
    return JSON.parse(trimmed);
  } catch {
    // fall through to bracket scanning
  }
  const start = trimmed.indexOf("{");
  let end = trimmed.lastIndexOf("}");
  while (start !== -1 && end !== -1 && end > start) {
    const chunk = trimmed.slice(start, end + 1);
    try {
      return JSON.parse(chunk);
    } catch {
      end = trimmed.lastIndexOf("}", end - 1);
    }
  }
  return null;
}

/** Stage the bundled eval-judge agent into `workspace/.github/agents`. */
function stageJudgeAgent(workspace: string): void {
  const agentFile = findJudgeAgentFile();
  if (agentFile === null) {
    throw new JudgeError(
      "Bundled eval-judge agent not found. Set EVALPILOT_JUDGE_AGENT to its " +
        "path or reinstall evalpilot.",
    );
  }
  const dest = path.join(workspace, ".github", "agents");
  mkdirSync(dest, { recursive: true });
  copyFileSync(agentFile, path.join(dest, path.basename(agentFile)));
}
