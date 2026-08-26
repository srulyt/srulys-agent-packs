# Competitors and adjacent patterns (REQ-§3.2, §3.3)

## Direct competitors (RES-§3)

Research products that solve the same or a substantially similar problem.
Understand: the concepts they expose · vocabulary · user journeys · access
models · permission models · administrative patterns · lifecycle states ·
approval models · discovery model · common defaults · important constraints ·
patterns that appear across several competitors.

Each product gets a `###` block under RES-§3 with the five fixed lines:

```markdown
### Okta
Observed behavior: an access request names a target application and an
optional duration; the requester picks an approver group, not a person.
Relevant pattern: approver *group* rather than approver *individual*.
Strengths: survives staff turnover; no orphaned requests.
Weaknesses: accountability is diffuse; requesters cannot chase a named person.
Applicability: high — REQ-012 asks what happens if the approver leaves.
```

**Do not simply copy a competitor.** The value of competitor research is
identifying established user expectations. When several products
independently converge on a concept, users likely already hold a mental model
for it — that is a reason to consider it, not an instruction to adopt it.

## Adjacent patterns (RES-§4)

Sometimes the best precedent is not a direct competitor. Analogous experiences
worth reaching for:

GitHub pull-request permissions · cloud resource IAM · document sharing ·
app-store publishing · API key management · SaaS invitations · ecommerce
checkout · approval workflows · data catalogs · package registries · role
delegation · subscription management · ticket workflows

Use an adjacent system when it supplies a useful **conceptual model**, not
because it is famous. State which structural feature of the problem makes the
analogy hold:

> Package registry publishing is analogous here because both involve an
> irreversible-in-practice grant to an audience the granter cannot enumerate
> in advance.

An analogy without that sentence is decoration.

## How many is enough

There is no target count. The bar is **coverage of the decision space**: every
row in the RES-§5 matrix should have at least two independent cells filled, or
carry an explicit `EV-GAP-###`. If two products answer every problem row the
same way, a third adds little; if they disagree, a third is worth reaching
for.

Record what was reached in the cumulative `Coverage — round N` record in
`{stm}/ledger/evidence.md` — `competitors: <count>`, `adjacent: <count>`.

## Familiarity is not the same as good (REQ-§41)

Do not assume a common pattern is the best pattern. For every established
pattern, evaluate all **nine axes**, as a closed list:

`familiarity` · `cognitive-load` · `scalability` · `reversibility` ·
`discoverability` · `admin-burden` · `error-risk` · `host-consistency` ·
`strategic-fit`

Every `PAT-###` record carries `axes_considered` as this exact list and
`axes_rationale` with one line per axis. The critic's check C-10a reads
`axes_rationale` from `{stm}/ledger/evidence.md` — a verdict without it is
BLOCKING, because a verdict nobody can audit is indistinguishable from a
preference.

Explicitly identify cases where competitors appear to be carrying **historical
complexity that should not be reproduced**. Say so in RES-§8 with the reason:

> Rejected: per-resource approval chains. Three of four competitors have them,
> and in each case the chain exists because the product predates group-based
> identity. Reproducing it would import the migration cost without the
> constraint that caused it. `PAT-009`.

## Verdicts

Each pattern gets exactly one verdict — `adopt`, `adapt`, `reject`, or
`context-only` — recorded as a `PAT-###`. The first three are rendered under
RES-§6, RES-§7 and RES-§8 respectively. `context-only` is the **degradation**
verdict: it is used when evidence could not be obtained well enough to reach
one of the other three, it is rendered as an unverified row in RES-§9 rather
than under §6/§7/§8, and it must carry the `EV-GAP-###` ids explaining why. A
pattern that could have been evidenced but was not thought through does not
earn `context-only` — it does not belong in the matrix at all.
