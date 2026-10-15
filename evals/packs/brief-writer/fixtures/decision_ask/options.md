# Implementation Options

Two viable paths have been costed. A third path (do nothing /
incremental tweaks) is documented at the end for completeness but is
not recommended.

## Option A — Build in-house

**One-time cost:** $1.4M (FY26)
**Ongoing cost:** absorbed into existing pod operating budget
**Time to GA:** ~9 months from approval

### Scope

Redesign of the onboarding flow inside the Lumetric product, owned
end-to-end by the Activation pod. Includes:

- Role-aware setup track (admin vs analyst vs finance lead) chosen
  at first login.
- Embedded sample workspace pre-loaded with synthetic but realistic
  finance data.
- Admin-led "first close" milestone with progress signaling.
- Replacement of the existing checklist component with a new
  guidance surface that the rest of the product can also reuse.

### Cost breakdown (rounded)

- Activation pod, fully loaded, 9 months: ~$960K
- Two contract senior product designers, 7 months: ~$280K
- Onboarding-content writer, part-time, 9 months: ~$70K
- Sample-data engineering and legal review of synthetic content: ~$50K
- Measurement, iteration tail, contingency: ~$40K

### Trade-offs

- Pro: We own the surface, the data model, and the guidance
  component. It composes with future product work — the same
  guidance surface unblocks the in-product upgrade flow we deferred
  in FY25.
- Pro: No ongoing per-seat fee.
- Con: Highest one-time cost.
- Con: Opportunity cost on the Activation pod — they do not ship
  other roadmap items for three quarters.

## Option B — Buy and integrate (Stepwise-class third-party)

**One-time cost:** ~$900K (FY26)
**Ongoing cost:** ~$650K / year, scaling roughly with seat count
**Time to GA:** ~5 months from approval

### Scope

License a third-party onboarding-and-guidance SaaS, integrate it
into the Lumetric shell, and author Lumetric-specific content inside
the vendor's authoring tool. Sample workspace and "first close"
milestone would still be built in-house because the vendor cannot
provide them.

### Cost breakdown (rounded)

- Vendor license, year one: ~$420K
- Integration engineering (2 engineers, 4 months): ~$240K
- Sample workspace + first-close milestone (in-house): ~$180K
- Content authoring and QA: ~$60K

### Trade-offs

- Pro: Faster GA by roughly four months.
- Pro: Lower one-time cost.
- Pro: Vendor handles A/B testing, analytics, and content versioning
  out of the box.
- Con: $650K/year ongoing fee, growing with seats. Five-year TCO
  crosses Option A around month 22.
- Con: We do not own the guidance surface. The upgrade-flow reuse
  story disappears.
- Con: Procurement, security review, and DPA will consume roughly six
  weeks of calendar time before integration work can begin.
- Con: Vendor lock-in. Migrating off later is non-trivial.

## Option C — Do nothing / incremental

Continue tuning the existing checklist. Estimated lift on
trial-to-paid conversion based on prior small experiments: 1–2
percentage points at most. This does not close the gap to the FY26
plan and is not recommended. Documented here for completeness.

## Open question for leadership

Is the strategic preference to own the guidance surface (Option A)
or to optimize for time-to-GA and lower one-time spend (Option B)?
The answer materially changes the FY26 Activation pod roadmap.
