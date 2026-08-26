# Question format and the three classifications

Questions reach the user only through the orchestrator, only at a **gate**,
and only after passing the test for their classification.

## Gates

| Gate | When | Owner of the raw questions |
|---|---|---|
| 1 | After context analysis, before research | analyst `open-questions` |
| 2 | After research, before modeling | researcher `open-questions` |
| 3 | After the author's passes, before delivery | author + critic `open-questions` |

Questions are **batched per gate**. A specialist never asks the user
anything directly; it emits `open-questions` and the orchestrator decides.

## The `open-questions` block

Every specialist emits this block on every turn, even when empty. It is a
**JSON array** — the same shape every sub-agent declares in its `## Output
Contract`. This file and those contracts are one schema; if they ever
disagree, that is a build defect, not a choice.

```open-questions
[{"id":"Q-IN-002",
  "classification":"important",
  "question":"Is there a cap on how many pending access requests one user may hold?",
  "why_it_matters":"a cap adds a rejection state to EIS-§8 and an edge case to EIS-§16",
  "options":["no cap","a fixed per-user cap","a per-tenant configurable cap"],
  "recommended_default":"no cap; unbounded pending requests"}]
```

Empty form — the **empty array**, never the word `none`:

```open-questions
[]
```

Field rules:

- `id` — `Q-IN-###` (analyst), `Q-RS-###` (researcher), `Q-MD-###` (author).
- `classification` — the closed three-way enum
  `blocking | important | can-safely-default`. Never a boolean.
- `question` — exactly one decision. Never bundle two.
- `why_it_matters` — must name which structural consequence applies (see the
  value test). "It would be good to know" fails review.
- `options` — the enumerable answers, or `[]` when the answer space is open.
  The orchestrator turns these into `ask_user` `choices`.
- `recommended_default` — a real, usable default the run can continue on, or
  the literal `none` when no default is defensible. `unknown` is not a
  default.

## The three classifications

| `classification` | Meaning | Interactive | Non-interactive |
|---|---|---|---|
| `blocking` | The specification cannot be written honestly without an answer. No default is defensible, so `recommended_default` may be `none`. | **Always asked.** The value test does not apply. | Recorded in `context/answers.md` with `assumed: true`; surfaced in EIS-§20, EIS-§21 and under `## Blocking Questions` in `decision-log.md`. |
| `important` | A wrong default would change the shape of the specification. | Asked **when it passes the value test** below. | Same as `blocking`. |
| `can-safely-default` | A wrong default is correctable by a reader without re-shaping anything. | **Never asked.** | **Never asked.** |

Why the enum is three-way and not a boolean: a boolean can separate "ask" from
"do not ask", but it cannot separate a question that **must** be asked from one
that is merely worth asking, and it cannot express the never-ask branch at all.
Collapsing `blocking` into `important` also strands Definition-of-Done point
14, which is scored on how **Blocking** questions were handled, and the
`## Blocking Questions` / `## Non-Blocking Questions` split in
`decision-log.md`.

## The value test — a value test, never a budget test

An `important` question is asked only when a wrong default would change:

- the shape of a flow (a step appears, disappears, or reorders), or
- whether a state exists at all, or
- whether an entry point exists, or
- where a permission boundary sits.

If none of those four change, the question is not `important` — it is
`can-safely-default`: a reader of EIS-§20 can overrule the default simply by
correcting the assumption. Write the assumption into EIS-§20 with a label and
move on.

This test is applied to each candidate **on its own merits**. It is never
relaxed because few questions have been asked so far, and never tightened
because many have. The ceiling is consulted **after** the test, and only ever
as a stop.

## Gate order of operations (the orchestrator's protocol)

1. **Gate 1 only — research-deferral filter.** For each `Q-IN-###`, read
   `why_it_matters`: does it ask *how some product behaves* (host, competitor,
   adjacent) or *what this product should do*? *How a product behaves* →
   **defer** to gate 2, do not ask, and pass the id and text to the researcher
   under `Deferred questions:`.
2. **Branch on `classification`** per the table above.
3. **Apply the value test** to `important` candidates only.
4. **Then, and only then, check the ceiling.**

## Ceilings

The per-gate question **ceiling** is 14. A ceiling is a stop, not a target: a
gate that surfaces three important questions asks three. **Never compute,
state, or reason from unused slots.** When the test yields more candidates than
the ceiling allows, ask the highest-impact ones first and re-gate after the
next phase. Reaching the ceiling with important questions still unasked is
itself a finding — the unasked ones are written to `{stm}/ledger/questions.md`
with `asked: false` and surfaced in EIS-§21 as open questions.

## How the orchestrator phrases a question to the user

- One question per call, in the order they block work.
- Offer the entry's `options` as enumerable choices, plus a free-text escape.
  Never add a literal `"Other"` choice — use the tool's `allow_freeform`
  escape, which is what a free-text answer is for.
- State the `recommended_default` that will be used if the user declines to
  answer, so declining is a real, informed option.
- Never bundle two decisions into one question.
- Append every id and the answer received to `{stm}/context/answers.md`.

## Unanswered questions

An unanswered `blocking` or `important` question becomes:

1. an entry in EIS-§21 `Open Questions`, with its blocking impact;
2. an entry under `## Blocking Questions` (`classification: blocking`) or
   `## Non-Blocking Questions` (`important` or `can-safely-default`) in
   `decision-log.md`;
3. a labelled assumption in EIS-§20 stating the default that was used.

All three. An assumption written without its matching open question hides the
fact that a choice was made.
