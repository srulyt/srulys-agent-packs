# Host product interrogation (REQ-§3.1)

The goal is not visual consistency. It is to learn the **behavioural language
of the product** the feature will live in, so the new experience reads as a
natural extension rather than a transplant.

## What to investigate

terminology · information architecture · navigation · object model · user
mental model · roles and permissions · ownership concepts · resource hierarchy
· sharing model · administrative model · settings patterns · creation flows ·
edit flows · delete/archive flows · discovery patterns · access-request flows ·
approval flows · notification patterns · error patterns · empty states ·
asynchronous operation patterns · status terminology · tables, lists, detail
experiences and other common interaction structures · cross-product
conventions · documentation relevant to the proposed feature

## The nine behavioural questions

Answer these explicitly. Each maps directly to an EIS section, so an
unanswered one leaves a hole a designer will have to fill by guessing.

| # | Question | Feeds |
|---|---|---|
| 1 | Does the product call this concept "sharing", "access", "permissions", or "entitlements"? | EIS-§6 |
| 2 | Does ownership automatically imply administrative capability? | EIS-§7 |
| 3 | Are permissions attached to users, groups, roles, resources, workspaces, or policies? | EIS-§7 |
| 4 | Are operations immediate or submitted as background jobs? | EIS-§8, §11 |
| 5 | How are long-running operations communicated? | EIS-§14 |
| 6 | What patterns already exist for requesting elevated access? | EIS-§10, §13 |
| 7 | How does the product expose read-only versus editable objects? | EIS-§7 |
| 8 | How are inherited permissions represented? | EIS-§7 |
| 9 | How does the product distinguish discoverability from usability? | EIS-§7, §9 |

## Where the answers land

RES-§2 `Host Product Analysis` and its six fixed sub-headings:

| Sub-heading | Content |
|---|---|
| `### Existing concepts` | The object model as users encounter it, in the product's own words. |
| `### Relevant workflows` | Existing flows this feature will sit beside or extend. |
| `### Permission conventions` | Answers to questions 2, 3, 7, 8, 9. |
| `### Interaction conventions` | Answers to questions 4, 5, 6 — plus notification, error, and empty-state patterns. |
| `### Terminology` | Answer to question 1, with the exact strings the product uses. |
| `### Constraints` | What the host product makes hard or impossible, and what that costs. |

## Evidence, not memory

Every claim about the host product is an `EV-RS-###` record with a source and
a date. "The product probably does X" is an inference and is labelled as one.
When the host product cannot be reached at all, that is not a licence to
guess: write `EV-GAP-###` records with `category: host-product` and the
accurate `reason`, and set `host_product: none` in the `Coverage — round N`
record.

## Precedence

The host product's established mental model beats a competitor's, unless there
is a strong stated reason to change. When host and industry conventions
conflict, surface the tradeoff explicitly in RES-§9 and raise it as a
`Q-RS-###` — do not silently pick one.

## When there is no identifiable host product

Standalone or greenfield products have no host. Say so in RES-§2 rather than
inventing one:

```
No host product — this is a standalone product. The conventions that would
otherwise constrain this feature are drawn from the adjacent patterns in
RES-§4 instead. host_product: none.
```

Then set `host_product: none` in the coverage record, which is what makes
Definition-of-Done point 11 `n/a`-eligible in a degraded or skipped run — and,
importantly, is *not* enough on its own in a `full` run.
