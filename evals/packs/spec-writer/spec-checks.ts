/**
 * Shared deterministic predicates for spec-writer behavioural evals.
 * Not an eval itself (no `.eval.` in the name), so the collector skips it.
 */

import { readFileSync } from "node:fs";
import * as path from "node:path";
import { fileURLToPath } from "node:url";

const HERE = path.dirname(fileURLToPath(import.meta.url));

/** Read a fixture file shipped next to these evals (the pre-run original). */
export function fixture(rel: string): string {
  return readFileSync(path.join(HERE, "fixtures", ...rel.split("/")), "utf8");
}

export const norm = (s: string) => s.replace(/\r\n/g, "\n").replace(/[ \t]+$/gm, "").trim();

export type Ctx = { root: string; stdout: string; read(rel: string): string | null };
export type Result = boolean | [boolean, string];

export const MANDATORY = [
  "Document Information",
  "Problem Statement",
  "Goals & Success Metrics",
  "Users & Personas",
  "Solution Summary",
  "Functional Requirements",
  "Risks & Mitigations",
  "Open Questions",
  "Out of Scope",
];

export const NO_INPUT =
  "You cannot ask me anything in this session and no further input will come. " +
  "Do not stop to ask questions: handle every unanswered gap the way the skill " +
  "says to, and complete the request now.";

export function headings(text: string): string[] {
  return [...text.matchAll(/^##\s+(.+?)\s*$/gm)].map((m) => m[1]!.replace(/<!--.*$/, "").trim());
}

export function mandatoryInOrder(text: string | null): Result {
  if (text === null) return [false, "spec file not written"];
  const hs = headings(text);
  let last = -1;
  for (const h of MANDATORY) {
    const i = hs.findIndex((x) => x.toLowerCase() === h.toLowerCase());
    if (i < 0) return [false, `missing '## ${h}' (found: ${hs.join(" | ")})`];
    if (i < last) return [false, `'## ${h}' out of order`];
    last = i;
  }
  return true;
}

export function hasHeading(text: string, re: RegExp): boolean {
  return headings(text).some((h) => re.test(h));
}

export function personaTableCount(text: string): number {
  return (text.match(/^\|\s*Persona\s*\|/gim) ?? []).length;
}

export function status(text: string): string | null {
  return text.match(/\*\*Status:\s*([A-Za-z ]+?)\s*\*\*/)?.[1]?.toLowerCase() ?? null;
}

export function version(text: string): string | null {
  return text.match(/\*\*Version:\s*([^*\s]+)\s*\*\*/)?.[1] ?? null;
}

/** Map FR-NN -> its block text (heading through next FR heading or ## section). */
export function frBlocks(text: string): Map<string, string> {
  const out = new Map<string, string>();
  const re = /^#{3,4}\s+(FR-\d+)\b[^\n]*\n([\s\S]*?)(?=^#{2,4}\s+FR-\d+\b|^##\s(?!#)|(?![\s\S]))/gm;
  for (const m of text.matchAll(re)) out.set(m[1]!, m[0]);
  return out;
}

/** The single shall-statement line of an FR block (first line containing "shall"). */
export function shallLine(block: string): string {
  return block.split(/\r?\n/).find((l) => /\bshall\b/i.test(l))?.trim() ?? "";
}

export function section(text: string, name: string): string {
  const re = new RegExp(`^##\\s+${name.replace(/[.*+?^${}()|[\]\\&]/g, "\\$&")}[^\\n]*\\n([\\s\\S]*?)(?=^##\\s|(?![\\s\\S]))`, "mi");
  return text.match(re)?.[1] ?? "";
}

export function openQuestionCount(text: string): number {
  return new Set(text.match(/\bOQ-\d+\b/g) ?? []).size;
}

/** Every FR has exactly one "shall" and at least one Given/When/Then AC. */
export function frShape(text: string | null): Result {
  if (text === null) return [false, "spec file not written"];
  const blocks = frBlocks(text);
  if (blocks.size === 0) return [false, "no FR-NN blocks found"];
  const bad: string[] = [];
  for (const [id, b] of blocks) {
    const body = b.split(/^#{4,5}\s+Acceptance/im)[0]!;
    const shalls = (body.match(/\bshall\b/gi) ?? []).length;
    const hasAc = /AC-\d+\.\d+/.test(b) && /\bgiven\b[\s\S]*\bwhen\b[\s\S]*\bthen\b/i.test(b);
    if (shalls !== 1) bad.push(`${id}: ${shalls} shall`);
    if (!hasAc) bad.push(`${id}: no Given/When/Then AC`);
  }
  return bad.length ? [false, bad.join("; ")] : true;
}

/** Count FRs written in the EARS unwanted-behaviour form ("If …, then the … shall"). */
export function unwantedFrCount(text: string): number {
  let n = 0;
  for (const b of frBlocks(text).values()) {
    if (/^\s*If\b[\s\S]*?\bthen\b[\s\S]*?\bshall\b/im.test(shallLine(b))) n++;
  }
  return n;
}
