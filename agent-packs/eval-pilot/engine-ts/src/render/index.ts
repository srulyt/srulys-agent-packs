/**
 * Renderers that turn an {@link EvalRunReport} into output.
 *
 * All three renderers read the **same** modeled result, so the JSON file is the
 * canonical record and the terminal/HTML views are pure projections of it.
 */

export { renderHtml } from "./html.js";
export { readJson, toJsonStr, writeJson } from "./json.js";
export { renderTerminal, type RenderTerminalOptions } from "./terminal.js";
