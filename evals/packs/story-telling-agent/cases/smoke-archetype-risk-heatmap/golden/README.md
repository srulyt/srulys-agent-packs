# Golden — smoke-archetype-risk-heatmap

Pass conditions:

- `deck-spec.json` exists at the expected path.
- `output.pptx` exists, opens, and is non-empty.
- `qa-report.json` records that QA ran (verdict `pass` or `revise`).
- **Archetype check**: Deck includes one slide whose `style_recipe` is `risk_heatmap` with at least 3 entries in `risks[]` and `axes.x_label` / `axes.y_label` populated.
- The `risk_heatmap` recipe name appears in the build log
  (`output.log` line `[slide N] styled/risk_heatmap`).

This case is rated **info** severity in the spec rubrics for the
first iteration — we are establishing baseline coverage of the new
builders, not gating on rubric scores.
