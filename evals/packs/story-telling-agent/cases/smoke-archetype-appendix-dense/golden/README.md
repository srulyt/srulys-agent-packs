# Golden — smoke-archetype-appendix-dense

Pass conditions:

- `deck-spec.json` exists at the expected path.
- `output.pptx` exists, opens, and is non-empty.
- `qa-report.json` records that QA ran (verdict `pass` or `revise`).
- **Archetype check**: Deck includes one slide with `style_recipe: appendix_dense`, `appendix: true`, and `panels[]` length in [2,4].
- The `appendix_dense` recipe name appears in the build log
  (`output.log` line `[slide N] styled/appendix_dense`).

This case is rated **info** severity in the spec rubrics for the
first iteration — we are establishing baseline coverage of the new
builders, not gating on rubric scores.
