# spec-writer evals

## Static

`pack-shape.eval.ts` runs offline structural checks with no SUT. It covers:

- the manifest and single-skill layout;
- link resolution;
- mandatory heading order and the single persona table;
- the absence of Alternatives Considered;
- what-if wiring and install docs;
- marketplace registration.

## Behavioural (business logic)

Each behavioural eval stages the `spec-writer` skill into a temp workspace and runs the live Copilot CLI with `--no-ask-user`. Prompts tell the skill that no further input will come, so gaps must be handled as `[TBD]` + Open Question.

- Deterministic checks are in `spec-checks.ts`.
- The rubric judge is used only where structure can't capture the outcome.
- Fixtures live in `fixtures/`.

| Eval | Expected outcome it proves |
| --- | --- |
| `what_if_coverage` | A happy-path-only brief (CSV export) still yields ≥ 3 derived `If…, then…` FRs with negative ACs. They sit inside Functional Requirements, not a separate section. Obvious cases get safe defaults; policy choices become TBD + OQ. |
| `no_fabrication` | A vague brief produces TBD goals and ≥ 3 OQs, not invented metrics, percentages, or survey data. |
| `backend_gating` | A no-UI gRPC rate-limit spec omits the UX/journey section and has ≤ 1 persona table. It includes NFRs with IDs and derives limiter failure modes (store unavailable, unknown tenant, …). |
| `ui_roles` | A multi-role UI spec has a UX section, exactly one persona table, a role matrix, and deny-path ACs. |
| `update_published` | Editing a published `1.0.0` spec opens a `1.x.0-draft` / `2.0.0-draft`. Published IDs are kept, the new FR gets the next ID, and the removed FR is not active. Unrelated FRs and upper sections are unchanged. There is no change-tracking and no CHANGELOG write. |
| `publish` | "Publish as 0.1.0" sets `published` / `0.1.0`, strips `-draft`, and leaves FR IDs untouched (no rewriting at publish). It writes a Keep-a-Changelog `CHANGELOG.md`. |
| `review_proposes_only` | Given review notes, the skill proposes concrete changes, including reviewers' what-ifs, keeps undecided items as OQs, and does not edit the spec without authorization. |

## Running

```bash
node scripts/run-evals.mjs spec-writer                                  # everything (behavioural evals take ~5 min with --parallel 7)
node scripts/run-evals.mjs spec-writer -- --parallel 7
node scripts/run-evals.mjs spec-writer -- --tags behaviour --parallel 7  # behavioural only
node scripts/run-evals.mjs spec-writer --list                            # lint/load only
node scripts/run-evals.mjs spec-writer -- --tags structural               # static only
```

Behavioural evals need the `copilot` CLI on PATH and consume AI credits. Results land in `evals/_runs/<timestamp>/`.
