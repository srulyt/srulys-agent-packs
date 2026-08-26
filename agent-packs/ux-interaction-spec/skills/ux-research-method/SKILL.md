---
name: ux-research-method
description: "How the ux-interaction-spec pack researches: the three research categories (host product, direct competitors, adjacent patterns), the REQ-§4 source-tier hierarchy and observed-fact versus inference versus recommendation discipline, evidence and gap records, the nine REQ-§41 evaluation axes, and REQ-§5 synthesis into adopt/adapt/reject verdicts that actually change the specification. Load when gathering, recording, or synthesising UX evidence. Keywords: UX research, competitive analysis, host product, adjacent patterns, evidence, sources, pattern matrix, adopt adapt reject, research mode."
---

# UX research method

Research is a **required** part of the work (REQ-§3). Do not build the
specification exclusively from the supplied requirements when external or
host-product context can materially improve it.

## Three categories

| Category | Question it answers | Lands in |
|---|---|---|
| **Host product** (REQ-§3.1) | How does the product this feature lives in already behave? | RES-§2 |
| **Direct competitors** (REQ-§3.2) | What do products solving the same problem do? | RES-§3 |
| **Adjacent patterns** (REQ-§3.3) | What analogous system supplies a useful conceptual model? | RES-§4 |

## Three claim types — never blurred

**Observed fact** (a reliable source supports it directly) · **Inference** (a
conclusion drawn from observed behavior or documentation) · **Recommendation**
(a proposed behavior for the product being specified).

Never claim that a product behaves in a particular way without evidence. When
evidence cannot be reached, record an `EV-GAP-###` with a `category` and a
`consequence` — that is a result, not a failure.

## Three research modes

`full` · `degraded` (attempted, partially reached, every gap recorded) ·
`skipped` (not performed). The mode is declared in `research-summary`,
recorded in the cumulative `Coverage — round N` record in
`{stm}/ledger/evidence.md`, and for `skipped` declared verbatim at the top of
`{out}/ux-pattern-research.md`.

A degraded run that presents itself as full is the failure this method exists
to prevent.

## Nine evaluation axes (REQ-§41) — closed list

`familiarity` · `cognitive-load` · `scalability` · `reversibility` ·
`discoverability` · `admin-burden` · `error-risk` · `host-consistency` ·
`strategic-fit`

Every `PAT-###` verdict carries `axes_considered` (this exact list) and
`axes_rationale` (one line per axis) in `{stm}/ledger/evidence.md`. A common
pattern is not automatically a good pattern — call out competitors carrying
historical complexity that should not be reproduced.

## Research must change something

For each meaningful pattern: adopt, adapt, reject, or context-only. Prefer the
host
product's mental model unless there is a strong reason to change; where host
and industry conventions conflict, surface the tradeoff rather than resolving
it silently. Research that produces no `RES-§9` implication and no `PAT-###`
verdict did not happen, however many words it produced.

## References

| File | Use it for |
|---|---|
| [host-product-interrogation.md](references/host-product-interrogation.md) | What to investigate in the host product, the nine behavioural questions, RES-§2's six sub-headings, and the no-host-product case. |
| [competitor-and-adjacent.md](references/competitor-and-adjacent.md) | RES-§3 per-product blocks, the adjacent-pattern list, how many is enough, and the nine axes in practice. |
| [evidence-discipline.md](references/evidence-discipline.md) | The seven source tiers, `EV-RS-###` / `EV-GAP-###` records, conflicting sources, research modes, and the vacuity rule. |
| [synthesis-and-precedent.md](references/synthesis-and-precedent.md) | The six synthesis questions, RES-§9, preserving the user's product intent, deferred answers, and top-ups. |

## Path resolution

Reference files resolve through the ladder in each agent's
`## Skills to Load` section: already-in-context, then
`.github/skills/ux-research-method/references/<file>`, then
`agent-packs/ux-interaction-spec/skills/ux-research-method/references/<file>`,
then `skills/ux-research-method/references/<file>` relative to the parent of
the agent directory.
