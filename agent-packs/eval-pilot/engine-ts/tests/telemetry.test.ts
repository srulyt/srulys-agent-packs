/**
 * Telemetry capture + assertions: OTel-file parsing, the new tool/file/token
 * assertion kinds, graceful degradation when telemetry is unavailable, and the
 * Markdown + builder authoring surfaces. No copilot binary required.
 */

import { describe, expect, it } from "vitest";
import { parseOtelTelemetry } from "../src/telemetry/otelFile.js";
import { emptyTelemetry, type RunTelemetry } from "../src/telemetry/model.js";
import { AssertContext, runAssertion } from "../src/assertions.js";
import { Eval } from "../src/loaders/builder.js";
import { parseMarkdownEval } from "../src/loaders/markdown.js";
import { makeAssertionSpec } from "../src/spec.js";

/** A minimal but realistic OTel file-exporter JSONL sample (copilot format). */
function sampleOtel(root: string): string {
  const view = {
    type: "span",
    spanId: "s1",
    name: "execute_tool view",
    startTime: "2025-01-01T00:00:00.000Z",
    endTime: "2025-01-01T00:00:01.000Z",
    status: { code: "OK" },
    attributes: {
      "gen_ai.operation.name": "execute_tool",
      "gen_ai.tool.name": "view",
      "gen_ai.tool.call.id": "toolu_1",
      "gen_ai.tool.call.arguments": JSON.stringify({
        path: `${root}/README.md`,
      }),
      "github.copilot.tool.parameters.file_path": `${root}/README.md`,
      "github.copilot.turn_id": 0,
    },
  };
  const create = {
    type: "span",
    spanId: "s2",
    name: "execute_tool create",
    attributes: {
      "gen_ai.operation.name": "execute_tool",
      "gen_ai.tool.name": "create",
      "gen_ai.tool.call.arguments": JSON.stringify({
        path: `${root}/out/plan.md`,
      }),
      "github.copilot.tool.parameters.file_path": `${root}/out/plan.md`,
    },
  };
  const chat = {
    type: "span",
    spanId: "s3",
    name: "chat claude-opus-4.8",
    attributes: {
      "gen_ai.operation.name": "chat",
      "gen_ai.request.model": "claude-opus-4.8",
      "gen_ai.usage.input_tokens": 1000,
      "gen_ai.usage.output_tokens": 50,
      "github.copilot.turn_id": 0,
    },
  };
  const agent = {
    type: "span",
    spanId: "s4",
    name: "invoke_agent",
    attributes: {
      "gen_ai.operation.name": "invoke_agent",
      "gen_ai.conversation.id": "sess-123",
      "gen_ai.usage.input_tokens": 1000,
      "gen_ai.usage.output_tokens": 50,
      "github.copilot.turn_count": 2,
    },
  };
  const metric = { type: "metric", name: "github.copilot.tool.call.count" };
  return [view, create, chat, agent, metric]
    .map((r) => JSON.stringify(r))
    .join("\n");
}

function ctxWith(root: string): AssertContext {
  const tel = parseOtelTelemetry(sampleOtel(root));
  return new AssertContext({ root, telemetry: tel });
}

describe("OTel file parsing", () => {
  it("extracts tool calls, file paths, tokens, turns, and session id", () => {
    const tel = parseOtelTelemetry(sampleOtel("/ws"));
    expect(tel.available).toBe(true);
    expect(tel.sources).toContain("otel-file");
    expect(tel.tools.map((t) => t.name).sort()).toEqual(["create", "view"]);
    const view = tel.tools.find((t) => t.name === "view")!;
    expect(view.filePath).toBe("/ws/README.md");
    expect(view.callId).toBe("toolu_1");
    expect(tel.tokens[0]!.model).toBe("claude-opus-4.8");
    expect(tel.totals.toolCalls).toBe(2);
    expect(tel.totals.inputTokens).toBe(1000);
    expect(tel.totals.outputTokens).toBe(50);
    expect(tel.totals.totalTokens).toBe(1050);
    expect(tel.totals.turns).toBe(2);
    expect(tel.sessionId).toBe("sess-123");
  });

  it("tolerates malformed lines and empty input", () => {
    expect(parseOtelTelemetry("not json\n\n").available).toBe(false);
    expect(parseOtelTelemetry("").available).toBe(false);
  });
});

describe("tool_called / tool_not_called", () => {
  it("passes when a tool was called and fails when a forbidden tool ran", () => {
    const ctx = ctxWith("/ws");
    expect(
      runAssertion(makeAssertionSpec({ kind: "tool_called", args: { name: "view" } }), ctx)
        .passed,
    ).toBe(true);
    expect(
      runAssertion(
        makeAssertionSpec({ kind: "tool_not_called", args: { name: "create" } }),
        ctx,
      ).passed,
    ).toBe(false);
    expect(
      runAssertion(
        makeAssertionSpec({ kind: "tool_not_called", args: { name: "shell" } }),
        ctx,
      ).passed,
    ).toBe(true);
  });

  it("honours count bounds and args_contain", () => {
    const ctx = ctxWith("/ws");
    expect(
      runAssertion(
        makeAssertionSpec({ kind: "tool_called", args: { name: "view", max: 0 } }),
        ctx,
      ).passed,
    ).toBe(false);
    expect(
      runAssertion(
        makeAssertionSpec({
          kind: "tool_called",
          args: { name: "view", args_contain: "README.md" },
        }),
        ctx,
      ).passed,
    ).toBe(true);
  });
});

describe("file access assertions", () => {
  it("detects reads and writes by glob", () => {
    const ctx = ctxWith("/ws");
    expect(
      runAssertion(
        makeAssertionSpec({ kind: "file_read", args: { paths: ["**/README.md"] } }),
        ctx,
      ).passed,
    ).toBe(true);
    expect(
      runAssertion(
        makeAssertionSpec({
          kind: "file_not_written",
          args: { paths: ["**/*.agent.md"] },
        }),
        ctx,
      ).passed,
    ).toBe(true);
    expect(
      runAssertion(
        makeAssertionSpec({
          kind: "file_not_written",
          args: { paths: ["**/plan.md"] },
        }),
        ctx,
      ).passed,
    ).toBe(false);
    expect(
      runAssertion(
        makeAssertionSpec({
          kind: "file_not_read",
          args: { paths: ["**/secrets.*"] },
        }),
        ctx,
      ).passed,
    ).toBe(true);
  });
});

describe("token_budget", () => {
  it("passes within budget and fails when exceeded or model disallowed", () => {
    const ctx = ctxWith("/ws");
    expect(
      runAssertion(
        makeAssertionSpec({ kind: "token_budget", args: { max_total: 5000 } }),
        ctx,
      ).passed,
    ).toBe(true);
    expect(
      runAssertion(
        makeAssertionSpec({ kind: "token_budget", args: { max_total: 100 } }),
        ctx,
      ).passed,
    ).toBe(false);
    expect(
      runAssertion(
        makeAssertionSpec({ kind: "token_budget", args: { models: ["claude-*"] } }),
        ctx,
      ).passed,
    ).toBe(true);
    expect(
      runAssertion(
        makeAssertionSpec({ kind: "token_budget", args: { models: ["gpt-*"] } }),
        ctx,
      ).passed,
    ).toBe(false);
  });
});

describe("graceful degradation", () => {
  it("skips (neutral) all telemetry assertions when telemetry is unavailable", () => {
    const ctx = new AssertContext({ root: "/ws", telemetry: emptyTelemetry() });
    for (const spec of [
      makeAssertionSpec({ kind: "tool_called", args: { name: "view" } }),
      makeAssertionSpec({ kind: "tool_not_called", args: { name: "view" } }),
      makeAssertionSpec({ kind: "file_read", args: { paths: ["**/*"] } }),
      makeAssertionSpec({ kind: "file_not_written", args: { paths: ["**/*"] } }),
      makeAssertionSpec({ kind: "token_budget", args: { max_total: 1 } }),
    ]) {
      const res = runAssertion(spec, ctx);
      expect(res.skipped).toBe(true);
      expect(res.passed).toBe(true); // skipped never fails an eval
    }
  });

  it("defaults telemetry to unavailable when none is supplied", () => {
    const ctx = new AssertContext({ root: "/ws" });
    expect(ctx.telemetryAvailable).toBe(false);
  });
});

describe("authoring surfaces", () => {
  it("builder compiles telemetry assertions", () => {
    const spec = new Eval("t", { kind: "agent", target: "x" })
      .prompt("do it")
      .expectToolCalled("ask_user")
      .expectToolNotCalled("str_replace_editor")
      .expectFileNotWritten("agent-packs/**/*.agent.md")
      .expectTokenBudget({ maxTotal: 50000, models: ["claude-*"] })
      .build();
    const kinds = spec.assertions.map((a) => a.kind);
    expect(kinds).toEqual([
      "tool_called",
      "tool_not_called",
      "file_not_written",
      "token_budget",
    ]);
  });

  it("markdown parses tools/files_accessed/tokens blocks", () => {
    const md = [
      "---",
      "name: tel-md",
      "kind: agent",
      "target: x",
      "---",
      "# tel",
      "## Act",
      "```prompt",
      "go",
      "```",
      "## Assert",
      "```yaml",
      "tools:",
      "  called: [ask_user]",
      "  not_called: [str_replace_editor]",
      "files_accessed:",
      "  not_written: ['agent-packs/**/*.agent.md']",
      "tokens:",
      "  max_total: 50000",
      "  models: [claude-*]",
      "```",
    ].join("\n");
    const spec = parseMarkdownEval(md, "tel.eval.md");
    const kinds = spec.assertions.map((a) => a.kind).sort();
    expect(kinds).toEqual([
      "file_not_written",
      "token_budget",
      "tool_called",
      "tool_not_called",
    ]);
  });
});
