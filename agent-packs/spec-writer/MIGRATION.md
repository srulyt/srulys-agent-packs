# Migration: spec-author, spec-creator, prd-pilot to spec-writer (one skill)

## Original capability and scope

All three source packs produce product and technical specifications:

- `spec-author`: Copilot agents and skills in `.github/`. It was the latest of the three and the source of the template.
- `spec-creator`: Roo modes in `.roo/`.
- `prd-pilot`: a skills-only Copilot plugin.

All three were left unmodified. The user authorized a new pack at `agent-packs/spec-writer`.

Files inspected:

- **spec-author:** `prd-template` (`specification-template.md`, `section-catalogue.md`), `versioning-discipline`, `prd-evolution`, `spec-driven-prd-best-practices`, `prd-quality-rubric`, `prd-interview`, and the agent profiles (orchestrator, context detective, drafter, critic, interviewer), along with its state schema and utility skills.
- **spec-creator:** the 9 Roo mode definitions and rules, the spec template, the reviewer and security rules, and the integrate-review command.
- **prd-pilot:** `ears-prd-workflow`, `prd-context-gathering`, `grill-me-interrogation`, and `ears-prd-format`.

Decisions the user made during migration:

- Use spec-author's template, with the duplicated Users & Personas content fixed.
- Drop the Fabric-specific knowledge.
- Keep the full draft/publish lifecycle.
- Drop the docx/vtt utilities.
- Interview to close P0 gaps, then draft directly, with no outline-approval stop.
- Remove the dangling Alternatives Considered reference.
- Make Assumptions an optional section in any spec.
- Add proactive what-if coverage, written as plain FRs with no special tag.

## Preserved information

| Rule/knowledge/contract | Original file and section | New destination | Validation |
| --- | --- | --- | --- |
| 9 mandatory sections, verbatim and in order; spec_kind; gated sections and axes | spec-author `prd-template/section-catalogue.md`; prd-pilot `ears-prd-format` | `references/sections-and-gating.md`, `assets/spec-template.md` | Static eval checks heading order |
| Template structure, ID schemes (FR/NFR/AC/R/OQ/TS/A) | spec-author `specification-template.md` | `assets/spec-template.md` | Static eval |
| Single persona table (bug fix: duplicate persona content removed) | spec-author template, Users & Personas + UX section | `assets/spec-template.md` | Static eval: exactly one persona table |
| EARS six patterns, one shall per FR, named system, P0/P1/P2, nested Given/When/Then ACs | spec-author best-practices §4/§4a/§5; prd-pilot `ears-prd-format` | `references/requirements-writing.md` | Unverified (live eval proposed) |
| Outcome goals with baseline/target/window; SMART metrics; NFR deltas over the platform baseline | spec-author best-practices §3; spec-creator template; spec-author Fabric NFR guidance (neutralized) | `references/requirements-writing.md` | Unverified |
| Voice, sentence craft, filler/buzzword lists, word budgets, upper-section signal density | spec-author best-practices §9–§10 | `references/writing-quality.md` | Unverified |
| Out-of-Scope adjacency test; OQ as first-class | spec-author best-practices §6–§7 | `references/writing-quality.md` | Unverified |
| Citation discipline (sparse, primary, durable, footnotes, never gitignored paths) | spec-author best-practices §8 | `references/writing-quality.md` | Unverified |
| JTBD, opportunity score, journeys → FRs, RBAC deny-by-default | spec-author best-practices §11; section catalogue UX | `references/writing-quality.md`, template | Unverified |
| Draft/publish lifecycle, SemVer, ID immutability, deprecation stubs, CHANGELOG, re-draft window | spec-author `versioning-discipline` V1–V17, `prd-evolution` §0–§3 | `references/lifecycle.md` | Unverified (live eval proposed) |
| Minimal-edit discipline; upper-section edit scrutiny; transactional cross-references | spec-author `prd-evolution`, rubric D10 | `references/lifecycle.md` | Unverified |
| Consolidate source material before deleting it | spec-creator rules | `references/lifecycle.md` | Unverified |
| Review feedback: propose, don't modify without authorization | spec-creator integrate-review command | `SKILL.md`, `references/lifecycle.md` | Unverified |
| Gap interview: P0 first, one gap per question, MC only for enumerable decisions, retry → TBD + OQ | prd-pilot `grill-me-interrogation`; spec-author `prd-interview` | `references/interviewing.md` | Unverified |
| Tool degradation: missing tools never block | prd-pilot `prd-context-gathering` | `references/interviewing.md` | Unverified |
| Quality review: rubric dimensions, traceability, P0-on-P2 dependency, security checks | spec-author rubric D1–D11; spec-creator reviewer; prd-pilot self-check | `references/quality-checklist.md` | Unverified |
| **New:** proactive what-if coverage as normal FRs | User request in this migration | `references/what-if-coverage.md`, template FR examples, checklist | Static eval checks links; live eval proposed |

## Removed scaffolding

| Material | Why removal preserves capability |
| --- | --- |
| Persona agents (orchestrator, Context Detective, Drafter, Critic, Interviewer) and the 9 Roo modes | Current models handle routing directly. Each persona's domain rules moved into references. |
| Stops 0/V/A/B, handoffs, mode switching, retry counters | Sequencing is left to the model. The only ordered rules kept are "close P0 gaps before drafting" and "publish only on explicit instruction". |
| `state-schema.json`, `.spec-author/sessions`, discovery.json, synthesis index, write chunks | Session state isn't needed. Publish stubs are now derived by diffing against the last published version, so no state file is required. |
| Fenced JSON control blocks (ready-for-review, coverage-json, edit-audit-json, prd-outline, prd-summary, spec-status, pre-merge-reminder) | These were inter-agent protocol only. The user-visible summary moved to SKILL.md's completion criteria. |
| Weighted critic scoring (average < 0.7 triggers revision) | Replaced with a qualitative blocker/major/minor checklist with the same dimensions. |
| Outline-approval loop (prd-pilot, spec-author Stop A) | The user chose direct drafting after the gap interview. |
| `mcp-cli-discovery` skill, shell tool probing | Tools are now discovered from the runtime tool list; tool degradation is still covered. |
| Fabric-specific platform knowledge | Dropped at the user's direction. The neutral "NFR deltas over baseline" principle is kept. |
| docx-to-markdown (markitdown) and vtt-reducer utilities | Dropped at the user's direction. The skill now asks for pre-converted input. |
| spec-creator template sections (Executive Summary, Market/Competitive, Technical Foundation Goals, Critical Success Criteria, Platform-Provided Requirements, Timeline & Milestones, Future Considerations) | spec-author's template is the user-chosen contract. These concepts either map onto its sections or were intentionally not carried over. |

## Uncertainty and host-specific survivors

- **Change-tracking in re-drafts:** prd-template allowed `Changes since vN` in re-drafts, but versioning-discipline forbids change-tracking in drafts. The stricter rule was kept.
- **Citation criteria:** sources disagree on three vs four citation conditions. The stricter four-condition version was kept.
- **Rubric D11:** numeric deductions were made qualitative. The legacy critic agent listed only D1–D10.
- **Branch-based status:** branch inference is now advisory only (a pre-merge reminder) and never changes status.
- **Interview safety bound:** the interview's structural safety bound was dropped. The interview now stops when P0 gaps are closed or deferred.
- **Host dependencies:** `user-invocable: true` frontmatter and the `/spec-writer:spec-writer` invocation depend on Copilot plugin support.

## Recommended evaluations

**Executed:**

- **Static pack-shape eval** (`evals/packs/spec-writer/`). It checks the manifest, skill layout, link resolution, mandatory heading order, the single persona table, the absence of Alternatives Considered, what-if linkage, and the install docs.
- **Seven live behavioural evals** in the same folder, run with the Copilot CLI: what-if coverage, no fabrication, backend gating, UI roles, update-published, publish, and review-proposes-only.
  - Final run: 8/8 passed.
  - The first runs exposed two real skill gaps:
    - On "publish", the skill expanded the spec with new FRs. Now publishing changes only lifecycle bookkeeping.
    - What-if FRs deferred obvious safe defaults to TBD. Now what-if-coverage prefers established safe defaults and keeps TBD for genuine business decisions.
  - The remaining first-run failures were over-strict checks, which were corrected.

**Proposed, not run:**

1. **Comparison:** run old spec-author, spec-writer, and a bare model on the same model and briefs.
2. **Repeat runs:** run each behavioural eval several times to measure variance. The judge metrics use a rolling-mean baseline.
