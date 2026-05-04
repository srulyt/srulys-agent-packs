# F3 Palette Preflight Rollback — Smoke Case

You are the user. Issue the following request to the
`@story-orchestrator` (or, if the orchestrator is not in this
sub-test's flow, directly to `@deck-critic`):

---

Simulate a rollback of `customer-coral.md` to its pre-F3-fix
state. The workspace already contains the rollback overwrite
(`background_accent` reverted to `#F87171`, `secondary_accent`
reverted to `#FB923C`) at:

    .github/skills/slide-design-systems/references/systems/customer-coral.md

Run the **G1 palette preflight** gate before any deck
assembly:

1. Execute
   `python .github/skills/slide-design-systems/scripts/check_palettes.py`
   against the (already-overwritten) systems directory.
2. Capture the exit code and the failing-pair JSON output.
3. Emit your standard `palette-preflight` fenced output
   contract block listing every system that failed, the
   failing token pairs, and the actual contrast ratios.
4. Set your overall `status` accordingly: a non-zero exit
   from `check_palettes.py` is a BLOCKING gate per
   architecture §3 / G1 — `status` must NOT be `pass` or
   `pass_unverified`.

You do NOT need to assemble a deck. The point of this case is
to verify that `check_palettes.py` would have caught the
rollback before any styled rendering happened, exactly as
expected by F3 of the iteration-1 review.

---

(Test fixture lives at
`fixtures/customer-coral.rollback.md` and is copied into the
isolated workspace by the `workspace.steps` in `case.yaml`.)
