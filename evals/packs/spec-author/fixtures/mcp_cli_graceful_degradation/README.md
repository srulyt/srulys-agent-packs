# Inputs for smoke-mcp-cli-graceful-degradation

Reuses the same persona / spike-note fixtures as
smoke-greenfield-context-complete.

The harness disables `mcp_*` tools at runtime (see
`harness_overrides.disabled_tools` in case.yaml). The fixture
`.github/copilot-instructions.md` (intentionally omitted) declares
no MCPs. The user prompt mentions the GitHub MCP — the detective
must record this as an unmet expectation in `discovery.json.skipped`
without hard-failing.
