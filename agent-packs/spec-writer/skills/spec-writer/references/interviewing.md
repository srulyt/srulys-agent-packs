# Gathering input

## Context first

- **Read before asking:** read what the user provided and the relevant workspace material before asking anything. Never ask for facts already present.
- **Tools:**
  - Use available tools (file search, web, MCP servers) only when they feed a section.
  - If a tool is missing or fails, note it and continue with what's available; never block on it.
  - Never present findings from a tool you couldn't use.
- **Input formats:** if source material arrives as `.docx`, `.vtt`, or another format you can't read, ask the user for a Markdown or text export.

## Closing gaps

- **Priority:** ask about gaps that block a useful spec (P0) before those that materially improve it (P1) or polish it (P2).
- **Gap areas:**
  - goal and the problem evidence
  - users and roles
  - expected behaviour and outputs
  - scope boundaries
  - thresholds and quantities
  - failure behaviour
  - success metrics
  - `spec_kind`, if unclear
  - where to save the spec
- **What counts as P0:**
  - On UI-forward specs, missing persona, journey, or role detail is P0.
  - On other specs, that context is woven in and doesn't block drafting.
  - A what-if is worth asking only when its answer changes scope or a P0 behaviour. Otherwise write it as a derived FR, or as TBD + OQ.
- **One gap per question:** ask directly ("What happens when…?", "What's the threshold for…?", "What's expected if this fails?").
  - Multiple choice only for enumerable decisions: 2–6 real options plus "Not sure / decide later". No "Other"; the host provides freeform input.
  - Freeform for quantities, names, narratives, thresholds, and rationale.
  - If the structured question tool is unavailable, ask the same questions conversationally.
- **When to stop:** stop when the P0 gaps are closed or explicitly deferred; there's no fixed question count. Then draft.
- **Never invent answers:**
  - An unresolved P0 becomes `[TBD — reason]` in the affected section, with a verbatim `OQ-NN`.
  - Unanswered P1/P2 questions go straight to Open Questions.
- **Conflicting inputs:** surface them rather than resolving them silently.
