# ux-interaction-spec — eval suite

Seven specs. Six behavioural (`kind: agent`, they drive the real
`@ux-interaction-spec` orchestrator end to end) and one structural
(`pack-shape.eval.ts`, `kind: none`, offline, no LLM judge). Together they
cover the pack's two failure surfaces: *does it produce the right documents*,
and *is it mechanically loadable and internally consistent*.

| Spec | Covers |
|---|---|
| `smoke-prd-to-eis.eval.md` | The happy path. A complete PRD in, three deliverables out at the confirmed location: a 22-section `eis.md`, a 10-section `ux-pattern-research.md`, and a 6-section `decision-log.md`. Asserts the full EIS heading set survives, that the skeleton was filled in place rather than appended to, that the traceability section maps REQ ids to EIS sections, and — via judge — that the actors, permissions and state models are actually derived from the PRD rather than restated from it. |
| `smoke-rough-concept.eval.md` | The thin-input path. A three-paragraph concept note, nowhere near enough to specify from. Asserts the pack does not hallucinate its way to a full spec *and* does not ship a half-finished one: the EIS carries all 22 headings with **no surviving `EIS-PENDING` sentinel and no `_Pending — pass` marker** (the spec `not_contains` both — an unresolved sentinel in a delivered document is a contract violation, not honesty), while the assumption and open-question sections carry real content and the decision log records what was assumed and why. Honesty is expressed as labelled assumptions and open questions, never as leftover scaffolding. |
| `smoke-no-premature-visual-design.eval.md` | Layer separation (the pack's sharpest quality bar). The input deliberately dangles visual hints — a colour, a component name, a layout. Asserts the EIS specifies *behaviour and intent* and does not leak into pixel-level design: no colour tokens, no component library names, no layout prescriptions in the interaction sections. This is the check most likely to catch a regression in the author's pass protocol. |
| `smoke-existing-ui-input.eval.md` | Host-product grounding. Notes describing an already-shipped UI go in. Asserts the pack treats them as *observed current state* — recorded, attributed, and distinguished from the proposed experience — instead of silently adopting today's design as tomorrow's requirement. |
| `smoke-conflict-and-gap-surfacing.eval.md` | Three inputs that disagree (a PRD, an ops runbook, and a provisioning API contract). Asserts the contradictions reach the decision log's *Contradictions / Risks* section by name rather than being smoothed over, and that each gap is resolved **visibly** — as an open question in `EIS-§21` *or* as an explicitly labelled assumption in `EIS-§20`. The spec pins `Interaction mode: non-interactive`, where a blocking question becomes a labelled assumption by construction, so the judge accepts either form; what it does not accept is a gap silently decided and presented as a requirement. |
| `smoke-degraded-research.eval.md` | The only spec that runs a research mode other than `skipped`, and the only one where Document 2 carries real content. A bundle of dated first-party host-product sources goes in; the bundle states plainly that no competitor and no adjacent-domain material could be obtained. Deterministic and offline — the fixture *is* the evidence. Asserts the asymmetry is honoured: host findings grounded and attributed, competitor/adjacent areas recorded as named categorised gaps rather than filled with plausible prose, an honest precedent matrix, and the memo's hard limits (25 grants per request, no rollback, per-row partial failure) surviving into the specification. This is the spec that exercises evidence labelling, the source hierarchy, pattern verdicts, a matrix with real rows, the critic's research checks against non-empty input, and asymmetric `n/a` eligibility in the definition-of-done. |
| `pack-shape.eval.ts` | Structural conformance, offline. Plugin packaging (`plugin.json`, `agents/` + `skills/` at the pack root, no pack-local `.github/`), additive marketplace registration with the five prior entries intact, agent inventory and invocation flags, least-privilege tool grants, the two-part `ask_user` discipline, ceiling-not-target framing, the three verbatim document skeletons (22 / 10 / 6 headings, in order), **cross-file agreement on every shared closed enum** (see below), and a set of self-checks over the six behavioural specs above. |

## Running

```
evalpilot run evals/packs/ux-interaction-spec/
```

or, through the repo's runner:

```
node scripts/run-evals.mjs ux-interaction-spec
```

`pack-shape.eval.ts` runs offline in well under a second and needs no
`copilot` binary — run it alone during development:

```
evalpilot run evals/packs/ux-interaction-spec/pack-shape.eval.ts
```

The six behavioural specs each drive a full orchestrator run and are tagged
`slow` and `judge`. Budget roughly an hour and a quarter for the set.

## Two things about these specs that are easy to get wrong

**Every behavioural spec needs both `target:` and an explicit `## Setup`.**
These do different jobs and neither substitutes for the other.

`target: ux-interaction-spec` selects the system under test. It also
auto-stages the agent and its skills into the temp workspace — that part is
handled for you. What it does *not* do is stage any fixture files. So the
explicit `## Setup` block exists to copy fixtures in, and every `Inputs:` path
in a prompt is **workspace-relative** (`inputs/access-request-prd.md`), never
repo-relative. A repo-relative path like
`evals/packs/ux-interaction-spec/fixtures/access-request-prd.md` does not
resolve inside the temp workspace and the run will fail to find its own input.

Omitting `target:` is the more dangerous mistake of the two, because it fails
*silently*: spec validation still passes, and the executor falls back to the
default Copilot agent. The spec runs, produces plausible-looking output, and
tests something other than this pack. `pack-shape.eval.ts` asserts every
behavioural spec declares it.

**Five of the six behavioural specs pin `Research mode: skipped`; the sixth
pins `degraded`.** No spec runs `full`, and that is deliberate: a `full`-mode
run makes live web calls, so it is neither offline nor deterministic and has no
place in a smoke suite.

Skipped mode alone would leave a real hole. It exercises the complete
10-heading Document 2 contract, the pinned `host_product: none; competitors: 0;
adjacent: 0` coverage record, and the definition-of-done arithmetic — but
everything downstream of *actually having evidence* is vacuous in it: the
evidence-labelling contract, the source hierarchy, `PAT-###` verdicts, a
precedent matrix with real rows, the nine-axis rationale, the critic's
research-verification checks with non-empty input, and the definition-of-done
points that are scored rather than `n/a`.

`smoke-degraded-research.eval.md` closes that hole without a network call. Its
fixture supplies substantial dated host-product material and states that
competitor and adjacent material could not be obtained, so the run produces
real evidence records for one research area and named gap records for the other
two. That asymmetry is what makes the `n/a`-eligibility logic testable at all:
one coverage point is scored, another is legitimately `n/a`, and the critic has
to tell them apart. What remains uncovered is live research *quality* — that
belongs in a separate, explicitly network-dependent spec, not here.

## Conventions these specs follow

- Every `contains` / `not_contains` entry is a single-line flow mapping
  carrying `path:`. An unscoped text assertion matches any file in the
  workspace — including the fixture the text was copied from — so it can pass
  without the pack having produced anything. `pack-shape.eval.ts` line-scans
  for this.
- `timeout: 3600`, from `(6 phases + 4 × 1 review round) × 360s`.
- Each spec clamps the pack's caps *downward* in its prompt (`Max review
  rounds: 1`, `Max specialist retries: 1`) so a smoke run cannot spend the full
  production ceiling.
- Prompts describe the task and never the expected answer. No spec's `## Act`
  block mentions a section id, a ledger record id, or an assertion string.
- Each behavioural spec makes at least one structural assertion — file
  existence, heading presence, section content — before any judge criterion, so
  a failure tells you *what* broke and not merely that a score dropped.

## Cross-file agreement on shared closed sets

The pack's recurring failure mode is a closed enum defined one way in a skill
reference and another way in the agent prompt that reads it. `pack-shape.eval.ts`
guards it from three directions:

- **Agreement.** `SHARED_ENUMS` lists every closed set that more than one file
  restates — `EV-GAP.category`, `EV-GAP.reason`, `PAT-###.verdict`,
  `open-questions[].classification`, `REQ-###.kind`, `Coverage.host_product` —
  with the files that declare it. A file counts as *declaring* only when its
  own field name (the anchor) and every value of the set appear together in one
  blank-line-delimited block, matched as delimited tokens. Substring matching
  is what made an earlier version of this check vacuous: `adjacent` matched
  inside `adjacent-domain`, `competitor` inside `competitors`, so renaming a
  value still passed.
- **Discovery.** The inverse direction scans *all* pack markdown for a
  declaring block belonging to a set whose `declaredIn` list does not name that
  file. A check whose file list is derived from "what someone edited" can never
  catch the site they missed; this one finds new sites on its own.
- **Absence.** `RETIRED_LITERALS` fails on any retired spelling — enum values
  and retired *heading* names alike — anywhere in the pack or in an eval spec.
  The agreement check only asserts canonical values are present; it cannot see
  a stale spelling sitting beside them.

A related check refuses any behavioural spec that asserts a `## <n>. ` heading
the target document's contract does not define, so a spec can never demand
something the pack is contractually unable to produce — and nobody is tempted
to "fix" it by editing a verbatim REQ-§32 skeleton.
