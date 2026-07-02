/**
 * Parse the copilot CLI's OpenTelemetry file-exporter output into
 * {@link RunTelemetry}.
 *
 * The runner sets `COPILOT_OTEL_FILE_EXPORTER_PATH` (and content capture) for a
 * run; copilot writes one JSON object per line — spans first, then metric
 * snapshots. We read the spans (traces) because they carry everything the
 * assertions need:
 *
 *  - `execute_tool <tool>` spans  → tool calls (name, args, file path, id).
 *  - `chat <model>` spans         → per-call token usage + model.
 *  - `invoke_agent` span          → run totals + turn count + session id.
 *
 * Attribute names follow the OTel GenAI semantic conventions
 * (`gen_ai.*`) plus copilot's `github.copilot.*` extensions. The parser is
 * deliberately defensive: it tolerates missing attributes and both the flat
 * value form copilot emits today and the wrapped OTLP value form
 * (`{ stringValue }`, `{ intValue }`, …).
 */

import { readFileSync } from "node:fs";
import {
  emptyTelemetry,
  type RunTelemetry,
  type TokenUsage,
  type ToolCall,
} from "./model.js";

/** Unwrap an OTLP attribute value (flat primitive or `{ *Value }` wrapper). */
function av(v: unknown): unknown {
  if (v === null || v === undefined) return undefined;
  if (typeof v === "object" && !Array.isArray(v)) {
    const o = v as Record<string, unknown>;
    for (const key of [
      "stringValue",
      "intValue",
      "doubleValue",
      "boolValue",
    ]) {
      if (key in o) return o[key];
    }
  }
  return v;
}

/** Normalise a span's `attributes` (object map or OTLP key/value array). */
function attrMap(raw: unknown): Record<string, unknown> {
  const out: Record<string, unknown> = {};
  if (Array.isArray(raw)) {
    for (const kv of raw) {
      if (kv && typeof kv === "object" && "key" in kv) {
        out[String((kv as any).key)] = av((kv as any).value);
      }
    }
  } else if (raw && typeof raw === "object") {
    for (const [k, v] of Object.entries(raw as Record<string, unknown>)) {
      out[k] = av(v);
    }
  }
  return out;
}

function num(v: unknown): number | undefined {
  if (v === null || v === undefined || v === "") return undefined;
  const n = Number(v);
  return Number.isFinite(n) ? n : undefined;
}

function str(v: unknown): string | undefined {
  if (v === null || v === undefined) return undefined;
  const s = String(v);
  return s === "" ? undefined : s;
}

/** Best-effort span duration in ms from start/end (ISO, epoch, or hrtime). */
function durationMs(start: unknown, end: unknown): number | undefined {
  const toMs = (v: unknown): number | undefined => {
    if (Array.isArray(v) && v.length === 2) {
      // hrtime-style [seconds, nanos]
      return Number(v[0]) * 1000 + Number(v[1]) / 1e6;
    }
    if (typeof v === "number") return v > 1e14 ? v / 1e6 : v; // ns vs ms heuristic
    const d = Date.parse(String(v));
    return Number.isNaN(d) ? undefined : d;
  };
  const a = toMs(start);
  const b = toMs(end);
  if (a === undefined || b === undefined) return undefined;
  const d = b - a;
  return d >= 0 ? d : undefined;
}

function isSpan(rec: any): boolean {
  return rec?.type === "span" || typeof rec?.spanId === "string";
}

/** Parse OTel file-exporter JSONL text into normalised telemetry. */
export function parseOtelTelemetry(text: string): RunTelemetry {
  const tools: ToolCall[] = [];
  const tokens: TokenUsage[] = [];
  let sessionId: string | undefined;
  let agentInput: number | undefined;
  let agentOutput: number | undefined;
  let agentTurns: number | undefined;

  const lines = text.split(/\r?\n/);
  for (const line of lines) {
    const trimmed = line.trim();
    if (!trimmed) continue;
    let rec: any;
    try {
      rec = JSON.parse(trimmed);
    } catch {
      continue; // skip malformed lines defensively
    }
    if (!isSpan(rec)) continue;

    const a = attrMap(rec.attributes);
    const op = str(a["gen_ai.operation.name"]) ?? "";

    if (op === "execute_tool") {
      const argsRaw = str(a["gen_ai.tool.call.arguments"]);
      let parsed: unknown;
      if (argsRaw !== undefined) {
        try {
          parsed = JSON.parse(argsRaw);
        } catch {
          parsed = undefined;
        }
      }
      let filePath =
        str(a["github.copilot.tool.parameters.file_path"]) ??
        str(a["github.copilot.tool.parameters.path"]);
      if (filePath === undefined && parsed && typeof parsed === "object") {
        const po = parsed as Record<string, unknown>;
        filePath = str(po.path ?? po.file ?? po.file_path ?? po.filePath);
      }
      const statusCode = str((rec.status ?? {}).code ?? rec.status);
      const ok =
        statusCode === undefined
          ? undefined
          : !/error|2/i.test(statusCode) || /ok|unset|1|0/i.test(statusCode);
      const call: ToolCall = {
        name: str(a["gen_ai.tool.name"]) ?? str(rec.name) ?? "unknown",
      };
      const callId = str(a["gen_ai.tool.call.id"]);
      if (callId !== undefined) call.callId = callId;
      if (argsRaw !== undefined) call.argsRaw = argsRaw;
      if (parsed !== undefined) call.args = parsed;
      if (filePath !== undefined) call.filePath = filePath;
      if (ok !== undefined) call.ok = ok;
      const dur = durationMs(rec.startTime, rec.endTime);
      if (dur !== undefined) call.durationMs = dur;
      const turn = num(a["github.copilot.turn_id"]);
      if (turn !== undefined) call.turn = turn;
      tools.push(call);
    } else if (op === "chat") {
      const usage: TokenUsage = {};
      const model =
        str(a["gen_ai.request.model"]) ?? str(a["gen_ai.response.model"]);
      if (model !== undefined) usage.model = model;
      const input = num(a["gen_ai.usage.input_tokens"]);
      const output = num(a["gen_ai.usage.output_tokens"]);
      if (input !== undefined) usage.input = input;
      if (output !== undefined) usage.output = output;
      const cacheRead = num(a["gen_ai.usage.cache_read.input_tokens"]);
      const cacheCreation = num(a["gen_ai.usage.cache_creation.input_tokens"]);
      const reasoning = num(a["gen_ai.usage.reasoning.output_tokens"]);
      if (cacheRead !== undefined) usage.cacheRead = cacheRead;
      if (cacheCreation !== undefined) usage.cacheCreation = cacheCreation;
      if (reasoning !== undefined) usage.reasoning = reasoning;
      if (input !== undefined || output !== undefined) {
        usage.total = (input ?? 0) + (output ?? 0);
      }
      const turn = num(a["github.copilot.turn_id"]);
      if (turn !== undefined) usage.turn = turn;
      tokens.push(usage);
    } else if (op === "invoke_agent") {
      sessionId = str(a["gen_ai.conversation.id"]) ?? sessionId;
      agentInput = num(a["gen_ai.usage.input_tokens"]) ?? agentInput;
      agentOutput = num(a["gen_ai.usage.output_tokens"]) ?? agentOutput;
      agentTurns = num(a["github.copilot.turn_count"]) ?? agentTurns;
    }
  }

  // Prefer the invoke_agent roll-up; fall back to summing chat spans.
  const inputTokens =
    agentInput ??
    (tokens.length
      ? tokens.reduce((s, u) => s + (u.input ?? 0), 0)
      : undefined);
  const outputTokens =
    agentOutput ??
    (tokens.length
      ? tokens.reduce((s, u) => s + (u.output ?? 0), 0)
      : undefined);
  const totalTokens =
    inputTokens !== undefined || outputTokens !== undefined
      ? (inputTokens ?? 0) + (outputTokens ?? 0)
      : undefined;
  const turns =
    agentTurns ??
    (tokens.length
      ? Math.max(...tokens.map((u) => (u.turn ?? -1) + 1), 0)
      : undefined);

  if (!tools.length && !tokens.length) {
    return emptyTelemetry("OTel file contained no tool/chat spans");
  }

  const telemetry: RunTelemetry = {
    available: true,
    sources: ["otel-file"],
    tools,
    tokens,
    totals: {
      toolCalls: tools.length,
      ...(turns !== undefined ? { turns } : {}),
      ...(inputTokens !== undefined ? { inputTokens } : {}),
      ...(outputTokens !== undefined ? { outputTokens } : {}),
      ...(totalTokens !== undefined ? { totalTokens } : {}),
    },
  };
  if (sessionId !== undefined) telemetry.sessionId = sessionId;
  return telemetry;
}

/** Read and parse an OTel file-exporter JSONL file into telemetry. */
export function parseOtelFile(filePath: string): RunTelemetry {
  let text: string;
  try {
    text = readFileSync(filePath, "utf-8");
  } catch (e) {
    return emptyTelemetry(
      `OTel file not found (${(e as Error).message}); telemetry unavailable`,
    );
  }
  return parseOtelTelemetry(text);
}
