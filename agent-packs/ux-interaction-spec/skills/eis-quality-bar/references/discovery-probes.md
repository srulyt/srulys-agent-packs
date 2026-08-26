# Discovery probes — the 14 questions a good EIS provokes (REQ-§45)

The final result must not feel like a reformatted PRD. It must be a
**meaningful additional layer of product design**. These fourteen probes are
the test: a good EIS causes a team to discover and resolve them.

## The 14 probes

| # | Probe |
|---|---|
| 1 | What actually owns this permission? |
| 2 | Who can see that this object exists? |
| 3 | What happens while approval is pending? |
| 4 | What happens if two people perform this operation simultaneously? |
| 5 | Does administrative permission imply usage permission? |
| 6 | What happens to existing users when the policy changes? |
| 7 | How does the user return to an unfinished workflow? |
| 8 | Is the action attached to the user, organization, workspace, or resource? |
| 9 | Is this status transient or part of the object's lifecycle? |
| 10 | Can this action be undone? |
| 11 | What does a rejected user see? |
| 12 | What happens if the approver no longer exists? |
| 13 | Is this concept already represented elsewhere in the product? |
| 14 | Are we asking users to understand an implementation detail that should be hidden? |

## The sweep (author, pass C)

Walk all fourteen in order. For each, decide one of:

- **answered** — the EIS already answers it. Record which `EIS-§n` section.
- **now-answered** — it was not answered; answer it now, then record where.
- **open** — it is a genuine product decision. Raise a `Q-MD-###`, record the
  default used, and list it in EIS-§21.
- **not-applicable** — it genuinely cannot arise for this feature. Record a
  one-sentence reason grounded in the feature. "No approval flow exists in
  this feature" is a reason; "not relevant" is not.

The sweep is written to `{stm}/ledger/coverage.md` under
`## Pass C — discovery_probes` as a 14-row table, `# | Probe | Answered in |
Note`, and mirrored into `coverage-json.discovery_probes`.

## Why it is written to disk

The critic cannot read the author's fenced output block. Check C-9 reads
`{stm}/ledger/coverage.md § Pass C — discovery_probes` (highest round). Two
distinct BLOCKING failures:

| Rule | When |
|---|---|
| `§45 — probe sweep not recorded` | the section is missing, or has fewer than 14 rows |
| `§45 — reformatted PRD` | the sweep is recorded but the EIS restates the input's structure and adds no resolved probe |

A missing sweep is **never** scored `pass` and never silently skipped.

## What "reformatted PRD" looks like

- EIS-§n sections that mirror the input document's own section order and
  content, with headings renamed.
- No state that the input did not already name.
- No permission rule the input did not already state.
- EIS-§16 `Edge Cases` populated only with cases the input listed.
- EIS-§21 `Open Questions` empty on a feature with real ambiguity.
- Every probe marked `answered` with a citation to a section that merely
  quotes the input.

Any three of those together are enough for check C-9 to fail.

## What a resolved probe looks like

> **Probe 4 — simultaneous operation.** The input does not say what happens
> when an owner revokes access at the moment a requester's approval is being
> provisioned. EIS-§8 now defines `Provisioning → Revoked` as a legal
> transition, EIS-§15 defines what the requester sees (the grant never becomes
> active and the reason is stated), and EIS-§16 records the race. `DRV-004`.

It names the gap, closes it in a specific section, and creates a derived
requirement that was not in the input.
