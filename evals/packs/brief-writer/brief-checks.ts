/**
 * Shared deterministic predicates for brief-writer behavioural evals.
 * Not an eval itself (no `.eval.` in the name), so the collector skips it.
 */

import { readFileSync } from "node:fs";
import * as path from "node:path";
import { fileURLToPath } from "node:url";

const HERE = path.dirname(fileURLToPath(import.meta.url));

export function fixture(rel: string): string {
  return readFileSync(path.join(HERE, "fixtures", ...rel.split("/")), "utf8");
}

export type Ctx = { root: string; stdout: string; read(rel: string): string | null };
export type Result = boolean | [boolean, string];

export const NO_INPUT =
  "You cannot ask me anything in this session and no further input will come. " +
  "Do not stop to ask questions: make the reasonable assumptions the skill allows, " +
  "do not use web search or other external sources, and complete the request now.";

/** Representative AI-isms and filler from the writing-style reference. */
const AI_ISMS = [
  /fast-paced/i,
  /game[- ]chang/i,
  /cutting[- ]edge/i,
  /\bseamless(ly)?\b/i,
  /it'?s worth noting/i,
  /\bdelve\b/i,
  /\bleverag(e|es|ing)\b/i,
  /\brobust\b/i,
  /in today'?s/i,
  /\bunlock(s|ing)? (the )?(full )?potential/i,
];

export function aiIsms(text: string): string[] {
  return AI_ISMS.filter((re) => re.test(text)).map((re) => re.source);
}

/** Lines whose only content is a bold label, e.g. `**Problem**` or `**Impact:**`. */
export function boldLabelLines(text: string): string[] {
  return text.split(/\r?\n/).filter((l) => /^\s*\*\*[^*]{1,60}\*\*:?\s*$/.test(l));
}

export function headings(text: string): string[] {
  return [...text.matchAll(/^#{1,6}\s+(.+?)\s*$/gm)].map((m) => m[1]!);
}

/** Shared hygiene check: no AI-isms, no bold pseudo-headings, no hyperlinks. */
export function hygiene(text: string | null): Result {
  if (text === null) return [false, "brief not written"];
  const problems: string[] = [];
  const ai = aiIsms(text);
  if (ai.length) problems.push(`AI-isms: ${ai.join(", ")}`);
  const bold = boldLabelLines(text);
  if (bold.length) problems.push(`bold-as-heading: ${bold.join(" | ")}`);
  if (/\]\([^)]+\)/.test(text)) problems.push("contains markdown links");
  return problems.length ? [false, problems.join("; ")] : true;
}

/** The closing heading must describe content, never just name the closing type. */
export function noTypeLabelHeadings(text: string | null): Result {
  const bad = headings(text ?? "").filter((h) =>
    /^(decision ask|call to action|recommendation|next steps|summary)$/i.test(h.trim()),
  );
  return bad.length ? [false, `type-label headings: ${bad.join(", ")}`] : true;
}

export const words = (text: string) => text.split(/\s+/).filter(Boolean).length;
