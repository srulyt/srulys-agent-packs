# Small evaluations with meaningful evidence

The objective is task quality and rule preservation with minimum unnecessary scaffolding, not maximum prompt compression.

For a creation scenario, evaluate the identified delta and primitive choice. For a migration, additionally evaluate original user-visible capability and retained domain rules against source-grounded expectations.

| Dimension | Useful evidence |
| --- | --- |
| Domain correctness | Correct terms, rules, exceptions, and output contracts; no invented facts |
| Rule preservation | Every material preserved constraint exercised or explicitly unverified |
| Artifact quality | A real representative deliverable, not just a plausible directory tree |
| Ambiguity robustness | Unknown decisions surfaced without fabricating inputs |
| Instruction following | Domain-required ordering and approvals preserved |
| Activation | Explicit invocation works; adjacent ordinary tasks do not over-trigger |
| Autonomy/complexity | No unnecessary phases, specialists, duplicated work, or needless checking |
| Context overhead | Actual text/line/word counts; tokens only with a named tokenizer |
| Maintainability | Canonical knowledge, thin adapters, usable installation and update behavior |

Where feasible, run the same task and model/settings with **old pack**, **modernized pack**, and **bare frontier agent**. Do not compare different model generations and attribute the difference to the customization. A legacy pack interpreted as context is not proof of its original harness runtime behavior.

A small ablation removes one questionable instruction/resource and repeats a representative task. If quality does not meaningfully decline, consider removal. Do not count a self-authored expected answer, mock runner, or static phrase match as behavioral evidence.

## Minimum factory exercises

Cover a substantial legacy pack with non-obvious knowledge, a simple reusable need, a no-customization case, and a scenario where enduring context/tool isolation actually justifies a custom agent. Check that these produce genuinely different solutions. Supplement with ordered-domain-procedure and adjacent-trigger cases.

Golden rules must come from source/user contracts rather than the factory's generated migration record alone. Check generated outputs and migration provenance. A skill missing a business rule fails even when its metadata and packaging pass.

Use the repository's Eval Pilot when available; structural `kind: none` specs run offline. Its built-in live Copilot runner currently uses `--allow-all`: scratch working directories are not a write sandbox. For sensitive or preservation-sensitive work, use native scoped permissions/tool filtering or an actual sandbox; do not claim confinement from an after-the-fact mutation check.

Stage only the necessary skill and fixture content. Avoid `stage: all`, which loads unrelated legacy customizations. Source and installed copies may share a name; explicit canonical-path staging avoids ambiguous discovery.

## Reporting

Record scenario, selected artifacts, model/runtime/settings when exposed, outcome, observed constraints, evidence paths, and limitations. Separate:

- static contract checks;
- discovery/load checks;
- live behavioral results;
- hypothetical integration checks;
- skipped, failed, or unavailable runs.

Missing evidence is not a pass. Tool activity and token/cost metrics may be unavailable; report that rather than infer them from elapsed time. Do not create a large framework, judge dependency, or mandatory eval roster for a trivial generated customization.
