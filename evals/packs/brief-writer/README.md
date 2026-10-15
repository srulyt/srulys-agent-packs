# brief-writer evals

## Static

`pack-shape.eval.ts` runs offline structural checks with no SUT. It covers:

- the manifest and single-skill layout;
- the absence of legacy orchestration (STM paths, agent names, fenced contracts);
- link resolution;
- SKILL.md wiring to every reference and the template;
- the presence of preserved business rules (closing types, scope-brief, audience calibration, Decision Posture, no-fabrication labels, AI-ism guidance, headings over bold, the review checklist);
- install docs and marketplace registration.

## Behavioural (business logic)

Each behavioural eval stages the `brief-writer` skill into a temp workspace and runs the live Copilot CLI. Prompts are natural requests with no explicit skill invocation, so they also test activation. Each prompt says that no further input will come and that external research is not allowed.

- Deterministic checks are in `brief-checks.ts`: AI-ism list, bold-as-heading lines, links, type-label headings.
- Each eval has a rubric judge for audience fit and argument quality.
- Fixtures live in `fixtures/`. The legacy product-brief fixtures were copied without their READMEs.

| Eval | Expected outcome it proves |
| --- | --- |
| `decision_ask` | A funding request for VP Product + CFO yields a recommendation-first brief. Build vs buy costs come from the source, and the closing names the decision, the approvers, and yes/no stakes in CFO terms. |
| `scope_brief` | A committed MVP scope description stays a scope-brief. It sets in/out boundaries per surface, keeps the deferred items, and adds no phantom approval or funding ask. |
| `early_stage` | A thin concept note yields a short (≤ 700 words) brief. The unknowns stay open questions, the closing is summary-style, and no cost/plan/FAQ sections are padded in. |
| `edit_existing` | Reviewer comments are applied to an existing brief in place. The rename propagates everywhere, marketing filler, links, and bold labels are removed, and every sourced fact and the ask survive. |
| `no_fabrication` | Number-free notes produce no invented percentages, costs, counts, or owners. Gaps are labeled, and the brief closes with an honest ask. |

## Running

```bash
node scripts/run-evals.mjs brief-writer                                  # everything
node scripts/run-evals.mjs brief-writer -- --tags behaviour --parallel 5  # behavioural only
node scripts/run-evals.mjs brief-writer -- --tags structural              # static only
node scripts/run-evals.mjs brief-writer --list                            # lint/load only
```

Behavioural evals need the `copilot` CLI on PATH and consume AI credits. Results land in `evals/_runs/<timestamp>/`.

## Results

Final full run: 6 evals, 5 passed. The early-stage judge scored 0.5 because it flagged facts from the source note as invented. The judge now gets those source facts and passes at 1.0. Early-stage has scored 1.0, 1.0, 0.5 (judge error), and 1.0 since the last skill fix.

| Eval | Judge score |
| --- | --- |
| pack-shape (static) | 8/8 checks |
| decision_ask | 0.85 |
| scope_brief | 1.00 |
| early_stage | 1.00 (after the judge fix) |
| edit_existing | 1.00 |
| no_fabrication | 1.00 |

**Skill gaps the evals found, and the fixes:**

1. **Restated caveats and narration of the source files** ("The options source includes…"). Fixed with the Voice rule in SKILL.md, the Tone section of `writing-style.md`, and items 4 and 5 of the review checklist.
2. **Thin briefs where summary, problem, and solution say the same thing.** Fixed with the thin-material rule in the Section Distinctness section of `structure.md`.
3. **Judge errors, not skill errors:**
   - The edit and decision judges demanded one exact figure or one crossover month.
   - The early-stage judge, which never sees the sources, flagged source facts as invented.

   These judges now accept equivalent answers and get the relevant source facts.

The judge requests an unavailable model and falls back, so scores vary between runs. Treat a single 0.5 as a reason to read the judge's rationale, not as proof of a regression.
