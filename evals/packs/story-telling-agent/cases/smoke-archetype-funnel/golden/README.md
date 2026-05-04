# Golden — smoke-archetype-funnel

Pass conditions:

- `deck-spec.json` exists at the expected path.
- `output.pptx` exists, opens, and is non-empty.
- `qa-report.json` records that QA ran (verdict `pass` or `revise`).
- **Archetype check**: Deck includes one slide whose `style_recipe` is `funnel` with `funnel_stages[]` length in [3,6] and every stage has a numeric `count`.
- The `funnel` recipe name appears in the build log
  (`output.log` line `[slide N] styled/funnel`).

This case is rated **info** severity in the spec rubrics for the
first iteration — we are establishing baseline coverage of the new
builders, not gating on rubric scores.
