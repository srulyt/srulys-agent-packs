# Style Gating (Duarte / Reynolds)

When does a slide deserve a `style: "styled"` recipe vs the simpler
`style: "simple"` default?

## The Heuristic (decisions.md OQ4)

> **Default to simple. Promote to styled when the slide carries
> emotional weight, signals a structural transition, or is the
> single load-bearing argument of a section.**

### Defaults by slide type

| Slide type | Default `style` | Default `style_recipe` |
|------------|-----------------|------------------------|
| `title`              | **simple** | — |
| `key-message`        | simple     | — (consider `accent_block_left` if foundational claim) |
| `content`            | simple     | — |
| `metric-spotlight`   | simple     | — (consider `metric_xxl` if it is THE number) |
| `comparison-columns` | simple     | — |
| `quote`              | simple     | — (promote to `quote_pullout` for the keynote pull-quote) |
| `data-callout`       | simple     | — (promote to `chart_callout` when the annotation IS the point) |
| `section-divider`    | **styled** | **`hero_full_bleed`** (per OQ4) |
| `visual-hero`        | styled     | `hero_full_bleed` |
| `question`           | simple     | — |
| `cta-steps`          | simple     | — (consider `progress_dots` if 5 well-bounded steps) |

## Why default to simple?

Two convergent reasons from the canon:

- **Duarte (`Slide:ology` / `Resonate`)**. Duarte's S-curve has the
  audience oscillating between *what is* and *what could be*. The
  inflection points are rare — typically section dividers and the
  big "call to adventure". Most slides should be *information
  carriers* that don't compete with those moments.

- **Reynolds (`Presentation Zen`)**. Restraint is a virtue. If
  every slide is a hero, none are. Simple slides earn the styled
  ones their visual weight.

If you find yourself promoting more than ~30% of slides to styled,
you are diluting the rhythm. Pull back.

## Promotion triggers

A slide should be promoted from simple to styled when **any** of:

1. **Emotional weight**: the slide is meant to land, not inform.
   (Pull-quote, hero claim, "this is the moment.")
2. **Structural transition**: the slide marks a section boundary
   or the start of a new arc movement.
3. **Single-argument**: the slide is the *only* place this
   argument is made — there is no follow-on slide to support it.
4. **Visual proof**: the slide must show something the audience
   couldn't have imagined from words alone (architecture diagram,
   product screenshot, key chart).

## Demotion triggers

Demote a slide to simple when:

1. The styled recipe would interfere with **dense information**
   (bullet lists with > 4 items, table-shaped data, code).
2. The slide is part of a **scan-pattern series** (e.g. five "one
   point each" slides — make them all simple so the audience
   learns the rhythm).
3. The user has **explicitly requested** a low-decoration deck
   (boardroom, financial, regulated industries).

## OQ5 binding (B3 — verify-or-block, no silent pass)

A deck where every slide is `style: "simple"` is the only deck
shape that may reach the **`unverified-needs-user`** verdict when the
render pipeline is unavailable. Any styled slide makes the deck
render-blocking (`render_unverified`, verdict `revise`) on render
failure.

> **`unverified-needs-user` does NOT ship the deck.** It replaces the
> former silent `pass_unverified` downgrade, which contradicted the
> user's explicit rule: *"do not generate slides when output quality
> cannot be assured."* A simple-only deck shipped with zero render
> verification is, by definition, unassured. So instead of auto-passing,
> the critic returns `unverified-needs-user` and the orchestrator
> (Phase 6) surfaces an explicit decision: **install** a render engine
> and retry / **ship unverified with explicit consent** / **abort**.
> The same graceful-block discipline applies to the Marp toolchain
> (`marp_toolchain_unverified`) for `output_mode` `marp` / `both`.
