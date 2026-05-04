# Golden — smoke-archetype-flywheel

Pass conditions:

- `deck-spec.json` exists at the expected path.
- `output.pptx` exists, opens, and is non-empty.
- `qa-report.json` records that QA ran (verdict `pass` or `revise`).
- **Archetype check**: Deck includes one slide whose `style_recipe` is `flywheel` with `flywheel_stages[]` length in [3,6].
- The `flywheel` recipe name appears in the build log
  (`output.log` line `[slide N] styled/flywheel`).

This case is rated **info** severity in the spec rubrics for the
first iteration — we are establishing baseline coverage of the new
builders, not gating on rubric scores.
