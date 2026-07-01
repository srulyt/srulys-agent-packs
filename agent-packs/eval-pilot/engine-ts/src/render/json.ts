/**
 * Canonical JSON serialisation of an {@link EvalRunReport}.
 *
 * This is the source-of-truth render: the terminal and HTML views are derived
 * from the same object, and `evalpilot show` / the `--check` CI gate reload a
 * run straight from this file.
 */

import { mkdirSync, readFileSync, writeFileSync } from "node:fs";
import * as path from "node:path";
import { reportToDict, runReportFromDict, type EvalRunReport } from "../model.js";

export function toJsonStr(report: EvalRunReport, indent = 2): string {
  return JSON.stringify(reportToDict(report), null, indent);
}

export function writeJson(report: EvalRunReport, file: string): string {
  mkdirSync(path.dirname(file), { recursive: true });
  writeFileSync(file, toJsonStr(report), "utf-8");
  return file;
}

export function readJson(file: string): EvalRunReport {
  const data = JSON.parse(readFileSync(file, "utf-8"));
  return runReportFromDict(data);
}
