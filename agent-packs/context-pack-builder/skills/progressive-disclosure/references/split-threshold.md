# SKILL.md Split Threshold (single source of truth) — reference

This file is the **one place** the token-split threshold is defined. The indexer
reads it; the conformance eval asserts against it. Correcting the number (e.g.
after re-verifying the live Anthropic Agent Skills / GitHub Copilot plugin docs)
is a **one-line change here** — do not duplicate the constant elsewhere.

## The constant

```
SPLIT_THRESHOLD_TOKENS = 5000
```

**Split a generated `SKILL.md` when its body (excluding YAML frontmatter)
exceeds 5,000 tokens.**

## Rationale + citations

- **Anthropic Agent Skills — progressive disclosure** ("Equipping agents for the
  real world with Agent Skills", Anthropic Engineering, 2025; Claude Docs *Agent
  Skills → Best practices*): the `SKILL.md` should stay a **lean entry point**
  and load detail on demand from bundled resource files. The documented guidance
  keeps the main body small (commonly cited as **under ~5k tokens / ~500
  lines**) and pushes everything else into progressively-loaded files. **~5,000
  tokens** is therefore adopted as the split trigger.
- **In-repo corroborating bound**: the `agent-builder` skill caps a `SKILL.md`
  at **5,000 words** (a hard ceiling). 5,000 tokens ≈ ~3,750 words, comfortably
  inside that ceiling — an index produced at the 5k-token trigger never
  approaches the hard limit.

> **Preview / re-verify note.** The precise published number could not be
> fetched live in the build environment (no web access). It is taken from
> knowledge + verified in-repo precedents and centralised **here** so a
> correction is trivial. Re-confirm against the live docs before publishing.

## Measurement heuristic (deterministic, no tokenizer dependency)

Measure the body **after stripping the YAML frontmatter block** (everything
between the first two `---` lines).

```
body_chars  = len(body_text)
words       = len(body_text.split())
est_a       = ceil(body_chars / 4)      # ~4 chars/token
est_b       = ceil(words * 1.33)        # ~1.33 tokens/word
token_estimate = max(est_a, est_b)
split = token_estimate > SPLIT_THRESHOLD_TOKENS
```

Split if **either** estimate exceeds the threshold (use `max`). Report
`token_estimate` in the indexer's `split` fenced block.

## Why a heuristic (not a real tokenizer)

A real tokenizer (e.g. `tiktoken`) is model-specific and adds a runtime
dependency not guaranteed on every host. The char/word heuristic is
deterministic, dependency-free, and conservative (it slightly over-counts, which
errs toward splitting — the safe direction). The conformance eval uses the same
heuristic so the trigger and the gate agree.
