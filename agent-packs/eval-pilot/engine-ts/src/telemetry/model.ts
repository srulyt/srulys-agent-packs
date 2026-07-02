/**
 * Normalised run telemetry — the structured record of *what the SUT did*.
 *
 * The runner captures this from the copilot CLI's OpenTelemetry output (see
 * {@link ./otelFile}) and attaches it to a {@link ../runners/base.RunResult}.
 * Assertions then inspect it through the {@link ../assertions.AssertContext}
 * (`ctx.tools`, `ctx.tokens`, `ctx.filesRead()`, …).
 *
 * Everything here is plain, JSON-round-trippable data.
 */

/** A single tool invocation observed during the run. */
export interface ToolCall {
  /** Tool name, e.g. "view", "create", "str_replace_editor", "ask_user". */
  name: string;
  /** Copilot tool-call id, when known. */
  callId?: string;
  /** Raw JSON string of the tool arguments (only with content capture on). */
  argsRaw?: string;
  /** Parsed tool arguments (best-effort JSON.parse of {@link argsRaw}). */
  args?: unknown;
  /** File path the tool acted on, when the tool exposes one. */
  filePath?: string;
  /** Whether the tool call succeeded (span status), when known. */
  ok?: boolean;
  /** 0-based turn index the call belongs to, when known. */
  turn?: number;
  /** Wall-clock duration of the call in milliseconds, when known. */
  durationMs?: number;
}

/** Token usage for a single LLM call (or the run total). */
export interface TokenUsage {
  model?: string;
  input?: number;
  output?: number;
  cacheRead?: number;
  cacheCreation?: number;
  reasoning?: number;
  /** input + output. */
  total?: number;
  turn?: number;
}

/** Run-level roll-ups. */
export interface TelemetryTotals {
  toolCalls: number;
  turns?: number;
  inputTokens?: number;
  outputTokens?: number;
  totalTokens?: number;
}

/** The full normalised telemetry for one SUT run. */
export interface RunTelemetry {
  /**
   * True when telemetry was actually captured. When false, telemetry-based
   * assertions *skip* (neutral) rather than fail — see {@link reason}.
   */
  available: boolean;
  /** Which capture layers contributed, e.g. ["otel-file"]. */
  sources: string[];
  /** copilot session/conversation id, when known. */
  sessionId?: string;
  tools: ToolCall[];
  tokens: TokenUsage[];
  totals: TelemetryTotals;
  /** One-line explanation when {@link available} is false. */
  reason?: string;
}

/** An empty, unavailable telemetry record (the graceful-degradation default). */
export function emptyTelemetry(reason = "telemetry not captured"): RunTelemetry {
  return {
    available: false,
    sources: [],
    tools: [],
    tokens: [],
    totals: { toolCalls: 0 },
    reason,
  };
}

/** Tool names that read a specific file's contents. */
export const READ_TOOLS = new Set(["view", "read", "cat", "open"]);

/** Tool names that create or modify a file. */
export const WRITE_TOOLS = new Set([
  "create",
  "edit",
  "write",
  "str_replace",
  "str_replace_editor",
  "apply_patch",
  "insert",
]);

/** All tool calls matching `name` (case-sensitive). */
export function toolCallsNamed(t: RunTelemetry, name: string): ToolCall[] {
  return t.tools.filter((c) => c.name === name);
}

/** File paths read during the run (from {@link READ_TOOLS} calls). */
export function filesRead(t: RunTelemetry): string[] {
  return t.tools
    .filter((c) => READ_TOOLS.has(c.name) && c.filePath)
    .map((c) => c.filePath as string);
}

/** File paths written/created during the run (from {@link WRITE_TOOLS} calls). */
export function filesWritten(t: RunTelemetry): string[] {
  return t.tools
    .filter((c) => WRITE_TOOLS.has(c.name) && c.filePath)
    .map((c) => c.filePath as string);
}

/** Distinct model names used during the run. */
export function modelsUsed(t: RunTelemetry): string[] {
  const seen = new Set<string>();
  for (const u of t.tokens) if (u.model) seen.add(u.model);
  return [...seen].sort();
}
