# Golden — smoke-archetype-footer-source

Pass conditions:

- `deck-spec.json` exists at the expected path.
- `output.pptx` exists, opens, and is non-empty.
- `qa-report.json` records that QA ran (verdict `pass` or `revise`).
- **Archetype check**: Deck includes >=1 slide with a non-null `footer` object on a slide whose `style_recipe` is anything OTHER than the 7 archetype recipes added this session (proving the partial composes with existing builders). At least one of `footer.source`, `footer.page`, or `footer.confidentiality` must be set.
- The `footer_source` recipe name appears in the build log
  (`output.log` line `[slide N] styled/footer_source`).

This case is rated **info** severity in the spec rubrics for the
first iteration — we are establishing baseline coverage of the new
builders, not gating on rubric scores.
