# Layout Archetype Library

> **Purpose**: Name the recurring **business-consulting** slide forms that
> the existing `presentation-design/SKILL.md` Layout Types table
> under-specifies. Each archetype is documented with structured metadata
> the strategist can cite in the proposal `Visual Treatment` field and
> the builder can use to pick a renderer.
>
> **Source**: research §F (story-telling-theory.md lines 104–142),
> ported in session `2026-05-04-5707a9ef`. The reference is the
> **spec-only** half of the archetype work — *some* archetypes already
> have working renderers in `pptx-engine/scripts/generate_deck.py` (or
> aliases via existing `render-visual` recipes); the others are
> documented here but lack renderer support and should be flagged in
> the proposal as "renderer pending".
>
> **Linked from**: [`presentation-design/SKILL.md`](../SKILL.md)
> (Layout Composition section).

## Renderer Status Legend

| Status | Meaning |
|---|---|
| ✅ **Built** | Direct builder in `pptx-engine/generate_deck.py` |
| 🔁 **Aliased** | No semantic builder, but the existing `render-visual` recipes / styled-recipes cover the layout content |
| ⏳ **Spec-only** | No builder yet. Proposal may reference the archetype but the deck-builder must fall back to the closest available `type` + `style_recipe` and surface the gap in `qa-summary` |

> *Status as of session `2026-05-04-c8d3b2a1`: **11 slide-type
> archetypes built + 1 overlay built** this session — Risk Heatmap,
> 2×2 / Priority Matrix, Waterfall, Flywheel, Funnel, Decision
> Options Table (>3), Org / Operating Model, Customer Journey,
> Architecture Diagram, Three-Card Recommendation, and Appendix
> Dense are slide-type ✅ Built; Footer Source is an overlay /
> partial ✅ Built (rendered on top of any slide whose spec carries
> a `footer` block). See per-archetype rows below for the exact
> builder function name. The previous "no archetype currently
> carries ✅ Built" note is therefore obsolete.*

## The 11 Archetypes

### 1. Risk Heatmap

- **Status**: ✅ Built — `_styled_risk_heatmap` (recipe `risk_heatmap`) in `pptx-engine/scripts/generate_deck.py` (session 2026-05-04-c8d3b2a1)
- **Best use**: Risk register, threat assessment, prioritization across
  *probability × impact* (or any 2-axis grid scoring).
- **Required inputs**: `risks: [{name, probability ∈ low|med|high, impact ∈ low|med|high, owner?}]`.
- **Geometry**: 3×3 (or 5×5) grid. X-axis = probability, Y-axis = impact.
  Each risk plotted as a labelled dot; cells colour-coded
  green→yellow→red. Title states the dominant risk; legend in lower
  margin.
- **Copy budget**: title ≤14w, axis labels ≤4w each, per-risk label
  ≤6w, source ≤12w.
- **Visual evidence**: matrix grid (no chart), explicit colour semantics.
- **Failure modes**: too many risks (>9 in a 3×3); colour-only encoding
  (fails contrast + a11y); axis polarity inconsistent across decks.
- **QA checks**: `risk_count <= cells`; `colour_semantic_legend_present`;
  `axes_labelled`; `each_risk_has_owner`.

### 2. 2×2 / Priority Matrix

- **Status**: ✅ Built — `_styled_priority_matrix` (recipe `priority_matrix`) in `pptx-engine/scripts/generate_deck.py` (session 2026-05-04-c8d3b2a1)
- **Best use**: Strategic options framed as two binary axes
  (effort × value, urgency × importance, build × buy).
- **Required inputs**: `axes: {x_label, y_label}`, `quadrant_labels[4]`,
  `items: [{name, x ∈ low|high, y ∈ low|high}]`.
- **Geometry**: 2×2 grid filling slide body. Labelled axes; quadrant
  names in faint type at quadrant centres; items as labelled dots.
  Recommended quadrant tinted; rest neutral.
- **Copy budget**: title ≤14w, axis labels ≤4w, quadrant labels ≤6w,
  per-item label ≤8w.
- **Visual evidence**: matrix.
- **Failure modes**: items only in one quadrant (the matrix wasn't the
  right form); axes that are not orthogonal in meaning;
  recommendation not visually emphasised.
- **QA checks**: `each_quadrant_labelled`; `recommendation_quadrant_emphasised`;
  `axis_polarity_explicit`.

### 3. Waterfall / Value Bridge

- **Status**: ✅ Built — `_styled_waterfall` (recipe `waterfall`) in `pptx-engine/scripts/generate_deck.py` (session 2026-05-04-c8d3b2a1). Structural assert: `check_archetypes.py::waterfall_zero_baseline`.
- **Best use**: Decompose a delta — "$10M → $14M, here are the four
  contributing components."
- **Required inputs**: `start: {label, value}`, `steps: [{label, delta, sign}]`,
  `end: {label, value}`.
- **Geometry**: floating bars across slide body; positive deltas in one
  colour, negative in another, terminals in neutral. Each bar labelled
  above with delta value; running total annotated underneath.
- **Copy budget**: title ≤14w, per-bar label ≤6w, units in axis title.
- **Visual evidence**: chart.
- **Failure modes**: signs not colour-coded; final value not visually
  emphasised; missing source; axis truncated below zero.
- **QA checks**: `signs_colour_coded`; `final_bar_emphasised`; `axis_starts_at_zero`;
  `source_present`.

### 4. Flywheel

- **Status**: ✅ Built — `_styled_flywheel` (recipe `flywheel`) in `pptx-engine/scripts/generate_deck.py` (session 2026-05-04-c8d3b2a1)
- **Best use**: Self-reinforcing loop where each stage feeds the next
  ("more users → more data → better model → more users").
- **Required inputs**: `stages: [{label, evidence?}]` (3–6 stages).
- **Geometry**: circular arrangement, arrows between stages going one
  direction, optional centre label naming the loop. Stage labels
  outside the circle for legibility.
- **Copy budget**: title ≤14w, stage label ≤6w, centre label ≤4w.
- **Visual evidence**: diagram.
- **Failure modes**: arrows ambiguous about direction; >6 stages
  (becomes a wheel of fortune); the loop doesn't actually close.
- **QA checks**: `stage_count_in_3_to_6`; `arrows_unidirectional`;
  `loop_closes`.

### 5. Funnel

- **Status**: ✅ Built — `_styled_funnel` (recipe `funnel`) in `pptx-engine/scripts/generate_deck.py` (session 2026-05-04-c8d3b2a1)
- **Best use**: Conversion / drop-off through ordered stages
  (acquisition → activation → retention; pipeline stages).
- **Required inputs**: `stages: [{label, count, rate?}]` (top-down).
- **Geometry**: trapezoidal stack. Each stage labelled with absolute
  count and % conversion from prior stage. Largest leak highlighted.
- **Copy budget**: title ≤14w, per-stage label ≤6w, per-stage metric
  ≤4w.
- **Visual evidence**: chart.
- **Failure modes**: misleading proportional widths (must scale
  faithfully); missing rates; no leak called out.
- **QA checks**: `widths_proportional`; `every_stage_has_count`;
  `largest_leak_emphasised`.

### 6. Decision Options Table (>3 options)

- **Status**: ✅ Built — `_styled_decision_options` (recipe `decision_options`) in `pptx-engine/scripts/generate_deck.py` (session 2026-05-04-c8d3b2a1). Supports N options × M criteria with a recommended-row highlight; the ≤3-option case continues to be served by `_simple_comparison_columns`. Structural assert: `check_archetypes.py::decision_options_columns_sum_to_slide_width`.
- **Best use**: Side-by-side option comparison with explicit
  recommendation.
- **Required inputs**: `options: [{name, criteria_scores: {[criterion]: score}, summary, owner}]`,
  `criteria: [name]`, `recommendation: option_name`.
- **Geometry**: dense table; rows = criteria, columns = options;
  recommended column highlighted with accent; criteria
  ordered by importance top-to-bottom; bottom row = "Recommendation".
- **Copy budget**: column header ≤4w, per-cell ≤8w, summary row ≤14w.
- **Visual evidence**: table.
- **Failure modes**: table that doesn't lead to a recommendation;
  >5 options (becomes unreadable); criteria that aren't comparable.
- **QA checks**: `recommendation_present`; `recommendation_column_emphasised`;
  `option_count <= 5`; `criteria_consistent`.

### 7. Org / Operating Model

- **Status**: 🔁 Aliased — `system_diagram` recipe in
  `render-visual/scripts/render_diagram.py` (Graphviz `dot`).
- **Best use**: Reporting structure, RACI, function-to-team mapping.
- **Required inputs**: `nodes: [{id, label, role}]`,
  `edges: [{from, to, kind}]`.
- **Geometry**: top-down hierarchy or layered swim-lane. Lead node
  larger; supporting roles in a row underneath. Use icons for role
  type only when it clarifies, not as decoration.
- **Copy budget**: per-node label ≤4w, per-edge label ≤4w.
- **Visual evidence**: diagram.
- **Failure modes**: graceful-degrades to a `.skipped.json` sentinel
  when Graphviz `dot` is missing — surface to user, build slide
  without the diagram.
- **QA checks**: `node_count <= 12`; `every_node_has_role_label`;
  `edges_unambiguous`.

### 8. Customer Journey

- **Status**: 🔁 Aliased — `progress_dots` styled recipe + `progress_strip`
  chart recipe (linear journeys). ⏳ Spec-only for swim-lane / persona-row
  variants.
- **Best use**: Time-ordered customer experience with emotional or
  metric overlay.
- **Required inputs**: `phases: [{name, customer_action, system_response, emotion?}]`,
  optional `kpi_overlay`.
- **Geometry**: horizontal stepper across slide; each phase a card with
  customer-action top, system-response bottom, optional emotion
  emoji/curve underneath.
- **Copy budget**: phase name ≤4w, per-card text ≤12w each row.
- **Visual evidence**: composite (stepper + optional metric overlay).
- **Failure modes**: too many phases (>6); steps that aren't time-ordered;
  emotion arc not differentiated from neutral.
- **QA checks**: `phase_count_in_3_to_6`; `phases_time_ordered`;
  `emotion_layer_distinct_when_present`.

### 9. Architecture Diagram

- **Status**: 🔁 Aliased — `flow_diagram` and `system_diagram` recipes
  in `render-visual/scripts/render_diagram.py` (graceful-degrade
  per OQ2 when Graphviz `dot` is unavailable).
- **Best use**: Technical-review slides showing system topology,
  data flow, deployment model.
- **Required inputs**: `nodes: [{id, label, kind}]`,
  `edges: [{from, to, label?, async?}]`, optional `boundary_groups`.
- **Geometry**: left-to-right flow or layered (client → API → service
  → store). Async edges dashed; sync edges solid; trust boundaries
  drawn as enclosing rounded rectangles.
- **Copy budget**: per-node label ≤4w, per-edge label ≤6w.
- **Visual evidence**: diagram.
- **Failure modes**: arrow directionality unclear; sync vs async
  visually identical; trust boundaries omitted; >12 nodes.
- **QA checks**: `node_count <= 12`; `arrows_directed`;
  `async_visually_distinct`; `trust_boundaries_explicit_when_relevant`.

### 10. Three-Card Recommendation

- **Status**: 🔁 Aliased — `_simple_comparison_columns` (3-column form)
  in `pptx-engine/scripts/generate_deck.py`. ⏳ Spec-only for the
  recommendation-flagging variant (verdict / score / owner per card).
- **Best use**: Closing recommendation slide presenting the chosen
  approach alongside the two alternatives that were rejected, each
  with a one-line rationale.
- **Required inputs**: `cards: [{verdict ∈ recommended|considered|rejected, name, summary, owner?, score?}]`
  (exactly 3 cards).
- **Geometry**: three equal columns; recommended card visually
  emphasised (filled background, accent header); other two
  desaturated. Each card has verdict pill, name, summary, optional
  owner / score.
- **Copy budget**: card name ≤4w, summary ≤16w, owner ≤4w.
- **Visual evidence**: cards (composite).
- **Failure modes**: no card emphasised; verdicts identical; rationale
  missing on rejected cards.
- **QA checks**: `exactly_three_cards`; `exactly_one_recommended`;
  `recommended_emphasised`; `rejected_cards_have_rationale`.

### 11. Appendix Dense

- **Status**: ✅ Built — `_styled_appendix_dense` (recipe `appendix_dense`) in `pptx-engine/scripts/generate_deck.py` (session 2026-05-04-c8d3b2a1). Pair with `appendix: true` on the slide spec to bypass the `body_word_max=30` density check.
- **Best use**: Read-along reference / data appendix where stand-alone
  density is the *point* (board pre-reads, regulatory filings, deep
  technical docs).
- **Required inputs**: `panels: [{kind ∈ table|chart|text, payload}]`
  (2–4 panels), `appendix_label: true` (mandatory).
- **Geometry**: 2-up or 4-up grid. Smaller type than ordinary slides
  (12–14pt body OK in this archetype only); footnotes used freely;
  visible "Appendix" tag in upper-right corner.
- **Copy budget**: panel title ≤6w; panel body ≤80w; footnote ≤12w.
  *Body word budget is intentionally relaxed for this archetype only;
  `pptx-structural-asserts.body_word_max` should ignore slides
  flagged `appendix: true`.*
- **Visual evidence**: mixed (tables + charts + footnoted text).
- **Failure modes**: dense slide that *isn't* labelled appendix
  (becomes a regular-slide failure); type below 11pt; missing source
  attributions on dense data.
- **QA checks**: `appendix_label_visible`; `min_font_size >= 11pt`;
  `every_data_panel_has_source`.

### 12. Footer Source

> **Note**: Footer Source is no longer #12 in the slide-type catalog
> — it has moved to the `## Overlays / Partials` subsection below
> (it is a partial that rides on top of any slide spec carrying a
> `footer` block, not a standalone slide-type). The content
> previously here is preserved verbatim in that section.

## Overlays / Partials

These are not standalone slide types; they are partial overlays a
slide spec opts into via a sub-block (e.g. `slide.footer = {...}`).
The renderer applies them after the primary builder.

### Footer Source

- **Status**: ✅ Built (partial) — `_apply_footer_source` (recipe key
  `footer_source`) in `pptx-engine/scripts/generate_deck.py`
  (session 2026-05-04-c8d3b2a1). Applied as an OVERLAY on any slide
  whose spec includes a `footer` block — not a standalone slide-type.
- **Best use**: Consistent source-citation / page-number /
  confidentiality band across content slides. Reused on every slide
  that cites external data.
- **Required inputs**: `footer: {source?, page?, confidentiality?}`.
  All three sub-fields optional; the partial renders only what is
  supplied. `source` carries the citation string, `page` an integer
  (auto-emitted as "Page N / total" when total is known), and
  `confidentiality` a short marker (e.g. `Confidential`,
  `Internal`).
- **Geometry**: 0.35"-tall band along the bottom edge of the slide.
  `source` left-aligned, `page` right-aligned, `confidentiality`
  centred. Caption-size type (14pt by default).
- **Copy budget**: source ≤14w, confidentiality ≤3w.
- **Visual evidence**: text band; reuses pack tokens
  (`text_secondary` / `text_secondary_on_*`).
- **Failure modes**: footer collides with body text on dense slides
  (mitigated by the 0.35" reservation); caption type below 11pt
  fails contrast on light surface (use the resolved
  `text_secondary_on_light` token).
- **QA checks**: caption ≥11pt; band height ≥ 0.30"; doesn't
  overlap body shapes (TODO check in `check_archetypes.py`).

## Using Archetypes from the Strategist's Proposal

In the per-slide outline (see `proposal.schema.md` Section 2), use the
archetype name verbatim in the `Visual Treatment` field, e.g.

```
- Visual Treatment: Risk Heatmap (3×3, probability × impact); top-3
  risks labelled; legend bottom-right.
```

When the archetype's status is ⏳ **Spec-only**, the strategist must
add a parenthetical note: *"renderer pending — builder will use closest
existing layout"*. The builder reads this and falls back to a
`type`+`style_recipe` pair from the canonical 11 enum + 8 styled
recipes; the gap is reported in `qa-summary`.

When status is 🔁 **Aliased**, the builder uses the named recipe
without further note.
