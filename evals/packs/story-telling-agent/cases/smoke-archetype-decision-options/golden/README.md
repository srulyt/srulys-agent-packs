# Golden — smoke-archetype-decision-options

Pass conditions:

- `deck-spec.json` exists at the expected path.
- `output.pptx` exists, opens, and is non-empty.
- `qa-report.json` records that QA ran (verdict `pass` or `revise`).
- **Archetype check**: Deck includes one slide whose `style_recipe` is `decision_options` with `options[]` length >=4 (proving the >3 path is exercised), `criteria[]` non-empty, and `recommendation` set to one of the option names.
- The `decision_options` recipe name appears in the build log
  (`output.log` line `[slide N] styled/decision_options`).

This case is rated **info** severity in the spec rubrics for the
first iteration — we are establishing baseline coverage of the new
builders, not gating on rubric scores.
