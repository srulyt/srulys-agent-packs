---
description: "Resume an interrupted Copilot Factory session from where it left off"
agent: "Copilot Factory"
---

## Resume Factory Session

I need to resume a previous factory session.

### Instructions

1. Check `.copilot-factory/current-session.json` for the active session
2. Load the session's `state.json` to determine the current phase
3. Report the session ID, phase, and target platform
4. Continue from the recorded phase

If no active session exists, let me know and offer to start a new one.
