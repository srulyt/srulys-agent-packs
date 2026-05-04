# Image Direction — Prompt Template & Reject-List

> **Purpose**: Image generation prompts and stock-image selection both
> default to the same generic-corporate slop unless the author writes
> intentional direction. This reference standardises the prompt
> template and names the things to *not* generate.
>
> **Source**: research §H (story-telling-theory.md lines 166–176),
> ported in session `2026-05-04-5707a9ef`.
>
> **Linked from**: [`presentation-design/SKILL.md`](../SKILL.md)
> (Slide Types — Image-Driven / Visual Hero).

## When to Use a Generated or Stock Image

A slide earns an image only when one of these is true:

1. **Emotional context** — set the mood for a customer story or vision.
2. **Concrete example** — show the actual product, the actual customer,
   the actual environment.
3. **Product evidence** — UI screenshot, hardware photo, in-the-wild
   capture.
4. **Metaphor** — a precise visual that compresses a concept (used
   sparingly; metaphors fail more often than they land).
5. **Location / atmosphere** — when *where* matters to the story.

If none of those is true: drop the image and use typography or a
diagram instead.

## The Prompt Template

When generating an image, write the prompt in this seven-part shape:

```
{subject} | {style} | {composition} | {lighting} | {crop} |
  negatives: {reject_list} | business relevance: {one sentence}
```

| Field | What to specify | Example |
|---|---|---|
| **subject** | Concrete noun + identifying detail | *"a senior factory-floor technician inspecting a CNC mill display"* |
| **style** | Photographic / illustrative / line-art; era reference if relevant | *"editorial photography, muted desaturated palette"* |
| **composition** | Framing + focal point + leading lines | *"medium shot, technician left third, machine right two-thirds, eye-line on display"* |
| **lighting** | Direction, hardness, colour temperature | *"side-lit by overhead industrial fluorescents, cool 5500K"* |
| **crop** | Aspect ratio + safe area for overlay text | *"16:9, leave clear upper-right quadrant for headline overlay"* |
| **negatives** | Explicit reject-list (see below) | *"no smiling office people, no handshakes, no clipart, no AI blobs"* |
| **business relevance** | One sentence the slide will be making | *"this image grounds the cost-of-downtime claim in a real maintenance moment"* |

The "business relevance" line is the one that prevents
generic-stock-photo drift. If you cannot write it, the slide doesn't
need an image.

## The Reject-List

Never generate or stock-select these. They are the visual
equivalent of "synergy" — they tell the viewer the deck is on
auto-pilot.

- **Smiling office people in a meeting room.** Universal AI-deck
  signature.
- **Handshakes** of any kind (multi-ethnic, cross-cultural,
  silhouetted, close-up). Never not a cliché.
- **Vague city skylines** at dawn / dusk, especially with light
  beams. Communicates nothing.
- **AI blobs / abstract neural-network swooshes / glowing dots
  connected by lines.** The aesthetic of a stock library that ran
  out of ideas.
- **Hands typing on a laptop.** Generic to the point of
  invisibility.
- **Light bulbs** as "innovation" metaphor. Done.
- **Compass / chess piece / ladder** as "strategy" metaphor.
- **Diverse-team-around-a-table** without a real meeting.
- **Stock photos of "data"** (binary code, holograms, tablets
  glowing).
- **Generic gradients labelled "future of [industry]"**.

If a stakeholder requests one of these explicitly, push back once
in writing; if they insist, comply and note the override in
`qa-summary`.

## Full-Bleed Image Treatment

Use a full-bleed image (no margins, image touches all four edges)
*only* when:

- the image is a real product / customer / location moment, AND
- the slide is a Visual Hero or Quote Pullout (one of the two
  styled recipes that support full-bleed: `hero_full_bleed`,
  `split_image_right`), AND
- the headline overlays the image with a gradient scrim or a
  colour-block panel ensuring 4.5:1 contrast over the image area
  the text occupies.

Otherwise: contained image with margins, treated as a content
element, not a backdrop.

## Icons (separate but related)

Icons clarify *categories*; they do not decorate *bullets*.

- One icon family across the whole deck. Mixing line + filled icons,
  or mixing different stroke weights, looks unprofessional.
- Icons are sized to match adjacent body text height (≤24pt for body,
  ≤40pt for callouts).
- An icon next to a bullet that *every* bullet has is decoration —
  remove or replace with content.

## Alt Text — Required, Not Aspirational

Every image and meaningful icon needs alt text. Default rules:

- Decorative-only images: `alt=""` (explicitly empty so screen
  readers skip).
- Content images: alt text describes *what the image shows in
  service of the assertion*, not the literal pixels.
  Bad: *"Photo of a person at a computer."*
  Good: *"Lab technician reviewing the CNC alarm log mid-shift —
  evidence for the maintenance-burden claim."*
- Charts and diagrams: alt text gives the *takeaway*, not the
  category list. The slide title is your starting point.

These map to the structural-assert `image_alt_present` check (warn
when image lacks alt; blocking when content-image alt is empty
string and the image is not flagged decorative).
