/**
 * Runner registry entry point. Importing this module registers the built-in
 * runners (mock + copilot) as a side effect, mirroring Python's import-time
 * registration. Always import `getRunner` from here (not directly from
 * `./base.js`) so the built-ins are guaranteed to be registered.
 */

import "./mock.js";
import "./copilot.js";

export * from "./base.js";
export { MockRunner, configureMock, resetMock } from "./mock.js";
export { CopilotRunner, CopilotNotInstalled, findCopilotBin } from "./copilot.js";
