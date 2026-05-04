# Golden — smoke-archetype-priority-matrix

Pass conditions:

- `deck-spec.json` exists at the expected path.
- `output.pptx` exists, opens, and is non-empty.
- `qa-report.json` records that QA ran (verdict `pass` or `revise`).
- **Archetype check**: Deck includes one slide whose `style_recipe` is `priority_matrix` with `quadrant_labels` length 4, `axes.x_label` and `axes.y_label` set, and >=3 entries in `matrix_items[]` exactly one of which has `recommended: true`.
- The `priority_matrix` recipe name appears in the build log
  (`output.log` line `[slide N] styled/priority_matrix`).

This case is rated **info** severity in the spec rubrics for the
first iteration — we are establishing baseline coverage of the new
builders, not gating on rubric scores.
