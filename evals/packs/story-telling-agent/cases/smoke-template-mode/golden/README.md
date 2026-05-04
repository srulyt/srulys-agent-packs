# Golden — smoke-template-mode

- `deck-spec.json` field `template_path` resolves to
  `templates/corporate-2026.pptx`.
- `deck-builder` invocation includes `--template` flag (visible in agent
  trace).
- `output.pptx` exists and opens.
- `qa-report.json` records that QA ran successfully (verdict pass or
  revise).
