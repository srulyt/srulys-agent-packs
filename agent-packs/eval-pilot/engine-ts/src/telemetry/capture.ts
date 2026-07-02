/**
 * Telemetry capture orchestration + configuration.
 *
 * Layer A (default): the copilot OTel *file* exporter. The runner points copilot
 * at a per-run JSONL file via {@link telemetryEnv}; after the process exits we
 * parse it with {@link captureFromFile}. This needs no collector, no network,
 * and no session-DB correlation — the file is unique to the run's workspace.
 *
 * Capture is on by default and disabled with `EVALPILOT_TELEMETRY=off`.
 */

import { type RunTelemetry } from "./model.js";
import { parseOtelFile } from "./otelFile.js";

/** True unless `EVALPILOT_TELEMETRY` is off/0/false/none/no. */
export function telemetryEnabled(): boolean {
  const v = (process.env.EVALPILOT_TELEMETRY ?? "").trim().toLowerCase();
  return !(
    v === "off" ||
    v === "0" ||
    v === "false" ||
    v === "none" ||
    v === "no"
  );
}

/**
 * Environment variables to inject so copilot writes full telemetry to
 * `otelPath` as JSON-lines. Content capture is enabled so tool arguments and
 * file paths are recorded (required for file-access / args assertions). The
 * file stays inside the run's workspace/log area and is never committed.
 */
export function telemetryEnv(otelPath: string): Record<string, string> {
  return {
    COPILOT_OTEL_FILE_EXPORTER_PATH: otelPath,
    OTEL_INSTRUMENTATION_GENAI_CAPTURE_MESSAGE_CONTENT: "true",
  };
}

/** Parse a completed run's OTel file into normalised telemetry. */
export function captureFromFile(otelPath: string): RunTelemetry {
  return parseOtelFile(otelPath);
}
