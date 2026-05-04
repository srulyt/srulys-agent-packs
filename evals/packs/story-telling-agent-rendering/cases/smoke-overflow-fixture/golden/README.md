# Golden

This smoke test does not pin a golden artifact. It asserts on the
critic's `critic-verdict` fence content (must contain
`overflow_violations`) via the case's `expectations` block. The
exact byte content of `structural-report.json` may drift across
Pillow / font versions; the regression we care about is that
`overflow_violations` is non-empty for the staged fixture.
