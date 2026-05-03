# Golden artefacts for smoke-mcp-cli-graceful-degradation

No byte-for-byte golden. The case asserts via:
- artifact_content_assertions on discovery.json
  (graceful_degradation: true; mcps_detected: []; the github-mcp
  expectation recorded in the skipped[] list);
- standard mandatory-coverage rubric on the spec.
