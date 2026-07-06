# spec-author evals

Behavioural and structural eval specs for the `spec-author` agent
pack. Coverage spans the pack's core flows — initial draft / draft
state, adaptive complexity-gated sectioning, the Stop A / Stop B
interview machinery, evidence discipline, upper-section isolation,
update-mode ID stability and change-tracking, and (added in the
2026-07-06 customer/user-awareness + grill-me build) the
`experience-surface` UI-forward axis with its conditional
"User Experience: Personas, Journeys & Roles" section, the woven
persona/JTBD context on non-UI specs, and the no-cap grill-me
interrogation (multiple-choice with a "Not sure / decide later"
deferral and no "Other" bucket, freeform for open-ended gaps).

Key user-context / grill-me specs:

- `test_smoke_ui_forward_ux_section.eval.md` — UI-forward spec fires
  the axis and gets the dedicated UX section with persona/journey/role
  content.
- `test_smoke_non_ui_no_ux_section.eval.md` — non-UI spec does NOT get
  the dedicated section (conditional-omission).
- `test_smoke_greenfield_context_complete.eval.md` — persona/JTBD
  context is woven into Users & Personas without a dedicated section.
- `test_smoke_simple_spec_section_reduction.eval.md` /
  `test_smoke_initial_draft.eval.md` — single-affordance non-fire
  guardrail keeps the UX section omitted.
- `test_smoke_grillme_no_cap_mc_freeform.eval.md` — grill-me interview
  is gap-sized (no 12-cap), MC includes the deferral option and no
  "Other", freeform for open-ended gaps.
- `test_smoke_grillme_ui_context_gaps.eval.md` — UI-forward spec with
  missing context raises persona/JTBD/journey/RBAC questions (P0).

## Running

```
evalpilot run evals/packs/spec-author/
```

or via the repo runner:

```
node scripts/run-evals.mjs spec-author
```

Lint the specs without executing agents:

```
evalpilot lint evals/packs/spec-author/
```
