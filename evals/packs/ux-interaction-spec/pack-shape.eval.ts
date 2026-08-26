/**
 * Structural conformance for the ux-interaction-spec plugin.
 *
 * No SUT (kind: none) — reads the shipped pack files and the eval suite
 * directly and asserts they are mechanically loadable and internally
 * consistent. Runs offline via `evalpilot run`: no copilot binary, no LLM
 * judge, no staging. Every assertion is deterministic.
 *
 * This spec is the pack's structural contract. The five behavioural specs
 * beside it test what the pack *produces*; this one tests what the pack *is*.
 */

import * as path from "node:path";
import { Eval } from "evalpilot";

const PACK = "agent-packs/ux-interaction-spec";
const EVALS = "evals/packs/ux-interaction-spec";
const MARKETPLACE = ".github/plugin/marketplace.json";
const CONTRACTS = `${PACK}/skills/eis-document-contracts/references`;
const QUALITY = `${PACK}/skills/eis-quality-bar/references`;

const ORCHESTRATOR = "ux-interaction-spec";
const SUBAGENTS = [
  "eis-context-analyst",
  "ux-pattern-researcher",
  "eis-author",
  "eis-critic",
];
const EXPECTED_AGENTS = [ORCHESTRATOR, ...SUBAGENTS];

const EXPECTED_SKILLS = [
  "eis-document-contracts",
  "interaction-modeling",
  "ux-research-method",
  "eis-quality-bar",
];

/** Entries that existed before this pack was registered. They must survive. */
const PRIOR_MARKETPLACE_ENTRIES = [
  "prd-pilot",
  "product-knowledge-brain",
  "eval-pilot",
  "context-pack-builder",
  "story-telling-agent",
];

const SUPPORTED_AGENT_KEYS = new Set([
  "name",
  "description",
  "tools",
  "disable-model-invocation",
  "user-invocable",
  "model",
  "target",
]);
const SUPPORTED_SKILL_KEYS = new Set(["name", "description", "license"]);

/**
 * ---- mojibake (double-encoding) detection --------------------------------
 *
 * Round 6 shipped three files whose UTF-8 bytes had been decoded as CP1252 and
 * re-encoded as UTF-8: U+00A7 became <U+00C2,U+00A7>, U+2014 became
 * <U+00E2,U+20AC,U+201D>, U+2192 became <U+00E2,U+2020,U+2019>.
 * The suite was blind to it because every notation assertion matched either an
 * ASCII phrase (/never appear on a `##` line/) or an ASCII literal
 * ("## 8. State Models") — both survive corruption untouched.
 *
 * That blindness was not cosmetic. `eis-skeleton.md` step 4 orders pass A to
 * confirm no heading contains `EIS-` + U+00A7; corrupted, it ordered a search
 * for `EIS-` + <U+00C2,U+00A7>, a string the author can never emit. The
 * self-check reported clean precisely when the defect it exists to catch was
 * present — the P1 enforcement mechanism inverted into a no-op.
 *
 * NOTE: this commentary deliberately writes the corrupt sequences as codepoint
 * notation rather than as literal glyphs. Quoting them literally would make
 * this very file fail the check below — which is exactly what happened on the
 * first attempt, and is a small proof that the check is not vacuous.
 *
 * Detection is a ROUND-TRIP TEST, not a list of known-bad literals: encode the
 * decoded text back to CP1252 and ask whether those bytes are themselves valid
 * UTF-8 that decodes to something shorter. Any double-encoded sequence answers
 * yes; legitimately non-ASCII prose answers no. A literal blacklist would have
 * to be extended for every new corrupted glyph, which is the same
 * asserted-but-unenforced trap one level up.
 */
const CP1252_HIGH: number[] = [
  0x20ac, 0x81, 0x201a, 0x0192, 0x201e, 0x2026, 0x2020, 0x2021,
  0x02c6, 0x2030, 0x0160, 0x2039, 0x0152, 0x8d, 0x017d, 0x8f,
  0x90, 0x2018, 0x2019, 0x201c, 0x201d, 0x2022, 0x2013, 0x2014,
  0x02dc, 0x2122, 0x0161, 0x203a, 0x0153, 0x9d, 0x017e, 0x0178,
];
const UNI_TO_CP1252 = new Map<number, number>();
for (let i = 0; i < 32; i++) UNI_TO_CP1252.set(CP1252_HIGH[i]!, 0x80 + i);

/** Encode to CP1252 bytes; null if any character is unmappable. */
function toCp1252(str: string): Buffer | null {
  const out = Buffer.alloc(str.length);
  for (let i = 0; i < str.length; i++) {
    const c = str.codePointAt(i)!;
    if (c > 0xffff) return null;
    if (c < 0x80 || (c >= 0xa0 && c <= 0xff)) out[i] = c;
    else if (UNI_TO_CP1252.has(c)) out[i] = UNI_TO_CP1252.get(c)!;
    else return null;
  }
  return out;
}

interface Mojibake {
  line: number;
  mojibake: string;
  repaired: string;
}

/** Every double-encoded run in `text`, located by line. */
function findMojibake(text: string): Mojibake[] {
  const dec = new TextDecoder("utf-8", { fatal: true });
  const found: Mojibake[] = [];
  text.split(/\r?\n/).forEach((line, li) => {
    if (!/[\u0080-\uffff]/.test(line)) return;
    for (const m of line.matchAll(/[\u0080-\uffff]+/g)) {
      const run = m[0];
      const bytes = toCp1252(run);
      if (!bytes) continue;
      let repaired: string;
      try {
        repaired = dec.decode(bytes);
      } catch {
        continue; // not valid UTF-8 => genuine non-ASCII text
      }
      if (repaired === run || repaired.length >= run.length) continue;
      if (/[\u0000-\u0008\u000b\u000c\u000e-\u001f]/.test(repaired)) continue;
      found.push({ line: li + 1, mojibake: run, repaired });
    }
  });
  return found;
}


/**
 * ---- shared closed sets (the anti-drift table) --------------------------
 *
 * Arch §2.6 deliberately has each agent prompt restate the rules it must obey
 * rather than only pointing at a skill reference — an agent that has to
 * re-derive its own contract mid-run is an agent that gets it wrong. The cost
 * of that decision is duplication, and duplication drifts: a round-5 review
 * found five separate defects that were all the same failure, an enum spelled
 * one way in a skill reference and another way in the agent prompt that reads
 * it. The agent writes vocabulary A, the critic audits for vocabulary B, and
 * the check either fails spuriously or fails to fire at all.
 *
 * These checks make that class CI-detectable. For each shared closed set:
 * every file listed in `declaredIn` must carry a *declaring block* — one
 * blank-line-delimited block that names the field's anchor token AND every
 * value in `values`, each matched with word delimiters. No file anywhere in
 * the pack may use a retired spelling, and no file may carry a declaring block
 * without being listed in `declaredIn`.
 *
 * The delimiter and co-occurrence rules are not decoration. A round-6 review
 * found the first version of this check used a bare `text.includes(value)`,
 * which passed whenever a value appeared *anywhere* in the same file as a
 * substring: `adjacent` matched inside `adjacent-domain`, `competitor` inside
 * `competitors`, and `adopt`/`adapt`/`reject` matched the marketing prose in a
 * SKILL.md frontmatter description. Renaming a value would still have passed.
 * The check that exists to catch drift was itself blind to drift.
 */
interface SharedEnum {
  /** Field this closed set belongs to, for error messages. */
  field: string;
  /**
   * The field's own name as it is written where the set is declared. It must
   * co-occur with the values in the declaring block, which is what stops a
   * passing prose mention ("adopt/adapt/reject pattern verdicts" in a
   * frontmatter blurb) from standing in for the real declaration.
   */
  anchor: string;
  /** The canonical values. Every declaring block must name all of them. */
  values: string[];
  /** Pack-relative files that restate the set and must therefore agree. */
  declaredIn: string[];
  /** Why the set is closed — surfaced in the failure message. */
  because: string;
}

const SHARED_ENUMS: SharedEnum[] = [
  {
    field: "EV-GAP-###.category",
    anchor: "category",
    values: ["host-product", "competitor", "adjacent"],
    declaredIn: [
      `${CONTRACTS}/ledger-format.md`,
      `${PACK}/skills/ux-research-method/references/evidence-discipline.md`,
      `${PACK}/agents/ux-pattern-researcher.agent.md`,
    ],
    because:
      "the critic reads category to decide whether definition-of-done points 11/12 are n/a-eligible; a value it does not recognise cannot corroborate n/a and becomes a spurious BLOCKING",
  },
  {
    field: "EV-GAP-###.reason",
    anchor: "reason",
    values: [
      "unpublished-internal",
      "paywalled",
      "no-comparable-product",
      "search-unavailable",
      "time-boxed-out",
    ],
    declaredIn: [
      `${CONTRACTS}/ledger-format.md`,
      `${PACK}/skills/ux-research-method/references/evidence-discipline.md`,
    ],
    because:
      "reason is descriptive and nothing branches on it, but it must stay distinct from category — collapsing the two is what produced the original defect",
  },
  {
    field: "PAT-###.verdict",
    anchor: "verdict",
    values: ["adopt", "adapt", "reject", "context-only"],
    declaredIn: [
      `${CONTRACTS}/ledger-format.md`,
      `${PACK}/skills/ux-research-method/references/competitor-and-adjacent.md`,
      `${PACK}/skills/ux-research-method/references/synthesis-and-precedent.md`,
      `${PACK}/skills/ux-research-method/SKILL.md`,
      `${PACK}/agents/ux-pattern-researcher.agent.md`,
    ],
    because:
      "'context-only' is the degradation verdict the researcher must emit in degraded and skipped modes; a three-value spelling leaves the mode the eval suite actually runs with no legal verdict",
  },
  {
    field: "open-questions[].classification",
    anchor: "classification",
    values: ["blocking", "important", "can-safely-default"],
    declaredIn: [
      `${CONTRACTS}/question-format.md`,
      `${CONTRACTS}/ledger-format.md`,
      `${PACK}/agents/${ORCHESTRATOR}.agent.md`,
      `${PACK}/agents/eis-context-analyst.agent.md`,
      `${PACK}/agents/ux-pattern-researcher.agent.md`,
      `${PACK}/agents/eis-author.agent.md`,
    ],
    because:
      "the orchestrator's gate protocol branches three ways; a boolean 'important' flag cannot express can-safely-default and strands the never-ask branch entirely",
  },
  {
    field: "REQ-###.kind",
    anchor: "kind",
    values: [
      "functional",
      "constraint",
      "business-rule",
      "technical-limit",
      "governance",
      "success-criterion",
      "non-goal",
    ],
    declaredIn: [
      `${CONTRACTS}/ledger-format.md`,
      `${PACK}/skills/interaction-modeling/references/input-triage.md`,
      `${PACK}/agents/eis-context-analyst.agent.md`,
    ],
    because:
      "the analyst loads input-triage.md before extracting and ledger-format.md before writing; a short set silently drops requirement kinds on the floor",
  },
  {
    field: "Coverage.host_product",
    anchor: "host_product",
    values: ["high", "partial", "none"],
    declaredIn: [
      `${CONTRACTS}/ledger-format.md`,
      `${PACK}/agents/ux-pattern-researcher.agent.md`,
      `${PACK}/agents/eis-critic.agent.md`,
      `${QUALITY}/definition-of-done.md`,
    ],
    because:
      "the schema file said none|partial|full while its writer (the researcher) and its reader (the critic) both said high|partial|none; nothing branches on the top value today, which is exactly why the disagreement survived a full review round",
  },
];

/**
 * Spellings that were wrong and are now fixed. They must not reappear
 * anywhere in the pack — including in a stray example or a half-updated
 * paragraph the enum-agreement check above would not notice, because that
 * check only asserts presence, never absence.
 */
const RETIRED_LITERALS: { literal: string; why: string }[] = [
  {
    literal: "kind: quality",
    why: "REQ kind 'quality' never existed in the architecture; the analyst's seven-value set has no such member",
  },
  {
    literal: "important: true",
    why: "the boolean question form was replaced by the three-way `classification` enum",
  },
  {
    literal: "important: false",
    why: "the boolean question form was replaced by the three-way `classification` enum",
  },
  {
    literal: "default_if_unanswered",
    why: "renamed to `recommended_default` when question-format.md was aligned to the analyst's JSON contract",
  },
  {
    literal: "category: unpublished-internal",
    why: "that value belongs to EV-GAP.reason; category is host-product|competitor|adjacent",
  },
  {
    literal: "category: paywalled",
    why: "that value belongs to EV-GAP.reason; category is host-product|competitor|adjacent",
  },
  {
    literal: "category: no-comparable-product",
    why: "that value belongs to EV-GAP.reason; category is host-product|competitor|adjacent",
  },
  {
    literal: "category: search-unavailable",
    why: "that value belongs to EV-GAP.reason; category is host-product|competitor|adjacent",
  },
  {
    literal: "category: time-boxed-out",
    why: "that value belongs to EV-GAP.reason; category is host-product|competitor|adjacent",
  },
  // Retired *heading* spellings. These are here because of a live incident:
  // a behavioural spec was written asserting `## 2. Method and Source
  // Hierarchy` and `## 3. Host Product Findings` against ux-pattern-research.md,
  // neither of which the document contract defines. It failed by construction,
  // and the tempting repair was to "fix" the skeleton — which would have broken
  // a verbatim REQ-§32 contract. The heading-membership check below catches
  // this in eval specs; these literals catch it in prose anywhere, including a
  // judge criterion or a skill that names a section by a name it no longer has.
  {
    literal: "## 2. Method and Source Hierarchy",
    why: "RES-§2 is 'Host Product Analysis'; this spelling never existed in the research-doc contract",
  },
  {
    literal: "## 3. Host Product Findings",
    why: "RES-§3 is 'Competitive Products'; host-product content lives in RES-§2",
  },
  {
    literal: "## 4. Competitor Analysis",
    why: "RES-§4 is 'Adjacent Patterns'; competitor content lives in RES-§3",
  },
  // The §20 assumptions column, retired in round 8. This is the orchestrator's
  // spelling of the obligation, and it is very likely how run 4's document came
  // to render the column as "What changes if false" while the author's own pass
  // guide said "what would change if it were false". Two spellings of one
  // contracted label in the files a single agent reads is a drift generator;
  // the canonical spelling is now pinned in matrices.md § 5 and held by the
  // PINNED_LITERALS check above.
  {
    literal: "what changes if this is false",
    why: "the EIS-§20 column is pinned as the verbatim literal `What would change if it were false` in matrices.md § 5; a second spelling in the orchestrator is what let run 4 and run 5 render the same column two different ways",
  },
];

/**
 * ---- pinned literals: one fact, two files, no drift --------------------
 *
 * `SHARED_ENUMS` above binds closed *value sets*. This binds closed *spellings*
 * — a literal that one file pins and other files must copy character for
 * character, including at least one eval assertion that searches for it.
 *
 * It exists because of a live incident. Section 20's assumptions table carries
 * a column whose obligation — *every assumption states what would change if it
 * were false* — is audited by critic check C-12 and scored by
 * Definition-of-Done point 14. The obligation was stated in prose at four
 * sites; the column's actual *spelling* was pinned nowhere. Run 4 emitted
 * "What changes if false", run 5 emitted "What would change if false", and the
 * eval needle — written once against run 4 — matched the first and not the
 * second. Both documents were correct. The assertion was correct in intent.
 * The pack's own wording had drifted, and nothing could see it.
 *
 * Note what the tempting fix would have been: widen the needle. That leaves
 * the drift in place and buys one round. The 22 EIS headings, the 10 RES
 * headings and the 6 DL headings are not defended that way — they are pinned
 * as literals and compared by exact string equality, precisely because "the
 * heading is the contract, not merely the title it carries". A load-bearing
 * column header in a mandated table is the same class of object, and this
 * table was the one mandated table whose load-bearing literal no contract
 * pinned. Pinning it is contract completion, not test-fitting.
 *
 * Direction of authority: `owner` is where the literal is defined and the only
 * file a change may originate in. `restatedIn` files copy it. `assertedIn`
 * specs search for it. All three are checked in one place so that a rename
 * fails offline instead of after a 70-minute run.
 *
 * Tokens must appear together on ONE line at every site. Line-scoping is not
 * decoration: these files are hard-wrapped at ~78 columns, and a literal
 * broken across a wrap is invisible to the reader who is meant to copy it and
 * to any downstream `includes()`. It also stops a five-column contract being
 * "satisfied" by five common words scattered through a file.
 *
 * No inverse check ("no file restates a pinned literal without being
 * declared") is paired with this one, unlike `SHARED_ENUMS`. An inverse scan
 * for a free-text English phrase would fire on every legitimate discussion of
 * the obligation — including this comment and the eval spec's own Description.
 * The drift direction that actually bites is a *retired* spelling surviving,
 * and `RETIRED_LITERALS` already scans the whole pack for exactly that.
 */
interface PinnedLiteral {
  /** Human name of the fact, surfaced in the failure message. */
  what: string;
  /** Exact spellings that must appear together on one line at every site. */
  tokens: string[];
  /** The contract file that owns the spelling. */
  owner: string;
  /** Pack files that restate it and must copy it character for character. */
  restatedIn: string[];
  /** Eval specs carrying a `pattern:` that must contain every token verbatim. */
  assertedIn: string[];
  /** Why the spelling is load-bearing — surfaced in the failure message. */
  because: string;
}

const PINNED_LITERALS: PinnedLiteral[] = [
  {
    what: "EIS-§20 assumptions table — first and last column headers",
    tokens: ["What would change if it were false"],
    owner: `${CONTRACTS}/matrices.md`,
    restatedIn: [
      `${PACK}/agents/eis-author.agent.md`,
      `${PACK}/agents/eis-author.passes.md`,
      `${PACK}/agents/eis-critic.agent.md`,
    ],
    assertedIn: [`${EVALS}/smoke-rough-concept.eval.md`],
    because:
      "the author writes this column, the critic's C-12 audits it, Definition-of-Done point 14 scores it and an eval assertion searches for it — four readers of one string, which drifted twice in two runs while it was specified only as a sentence to paraphrase",
  },
  {
    what: "RES-§9 evidence-to-recommendation matrix — the five column names",
    tokens: [
      "Decision area",
      "Host product precedent",
      "External precedent",
      "Recommendation",
      "Rationale",
    ],
    owner: `${CONTRACTS}/matrices.md`,
    restatedIn: [
      `${PACK}/agents/ux-pattern-researcher.agent.md`,
      `${PACK}/skills/ux-research-method/references/synthesis-and-precedent.md`,
    ],
    assertedIn: [],
    because:
      "found by the round-8 sweep for siblings of the §20 defect: matrices.md pins 'Five columns, exactly these names, in this order' and two other files restate all five verbatim, with nothing comparing the three — the same hand-copied-fact class. synthesis-and-precedent.md had already broken 'Host product precedent' across a hard wrap, which is how a five-column contract becomes a six-column table",
  },
];

/**
 * Axes along which a counterfactual phrasing realistically drifts, used to
 * *derive* the near-miss spellings of a pinned literal rather than hand-listing
 * them.
 *
 * Round 8's mutation test found the containment check above has a blind spot:
 * it asks whether each declared site carries the literal *somewhere*, so a file
 * holding it twice — matrices.md and eis-critic.agent.md both do — can drift in
 * one place and stay green on the other. That is not hypothetical. The critic
 * states the column in C-12's body and again in the non-interactive severity
 * table; an author who reads C-12 and a critic who reads the table would then
 * be working from two different strings, which is the original defect exactly.
 *
 * Substituting each axis member for each other member across the pinned literal
 * yields a closed variant set covering the two ways this label has been seen to
 * vary in pack files: the tense/aspect of the verb, and the subject of the
 * conditional. It therefore contains the orchestrator's superseded wording,
 * `What changes if this is false`, and the halfway form
 * `What changes if it were false`. It does NOT contain the subject-eliding
 * forms — `What changes if false`, `What would change if false` — which have
 * only ever appeared in generated output, never in a pack file, and so are out
 * of this check's scope: it guards what the pack SAYS, and the eval assertion
 * guards what the pack PRODUCES. No elision axis is added, because a check
 * earns its complexity from the defects it can actually see.
 * Deriving beats enumerating here: an enumeration is one more hand-copied fact,
 * and the enumeration would have to be revised every time the literal is
 * re-worded. Axes that do not occur in a literal contribute nothing, so the
 * RES-§9 column names pass through untouched.
 */
const DRIFT_AXES: string[][] = [
  ["would change", "changes", "change", "changed", "would be different", "would differ"],
  ["it were", "it is", "it was", "this is", "this were", "this was", "they were", "that were"],
];

function driftVariants(literal: string): string[] {
  let forms = [literal];
  for (const axis of DRIFT_AXES) {
    const next = new Set<string>(forms);
    for (const f of forms) {
      for (const a of axis) {
        const re = new RegExp(a.replace(/[.*+?^${}()|[\]\\]/g, "\\$&"), "gi");
        if (!re.test(f)) continue;
        for (const b of axis) {
          if (a !== b) next.add(f.replace(new RegExp(re.source, "gi"), b));
        }
      }
    }
    forms = [...next];
  }
  const canon = literal.toLowerCase();
  return forms.filter((f) => f.toLowerCase() !== canon);
}

/**
 * The agents that own a file on disk, and the artifact each must create.
 *
 * Membership rule: **every agent granted `edit` owes an affirmative write
 * duty** — no exceptions, enforced mechanically by the companion check
 * "every agent granted `edit` is accounted for as a writing agent". Do not
 * hand-curate this list by what "feels like a deliverable".
 *
 * `eis-critic` was excluded here until eval run 3, on the reasoning that it
 * writes "only a review artifact under `{stm}/artifacts/`, which no eval
 * assertion reads". That reasoning was wrong twice over. Reachability by an
 * assertion is not what makes a write load-bearing: run 3 created no
 * `{stm}/artifacts/` directory at all, so the pipeline recorded
 * `last_verdict.artifact = "UNAVAILABLE"`, `status =
 * "phase-failed-after-retry"`, and pushed review into `skipped_phases` —
 * leaving a BLOCKING verdict the run could not clear even though the document
 * set was complete. A spec that writes every deliverable still cannot finish.
 * The exclusion also made the list a judgement call, which is exactly how a
 * gap survives three fix turns.
 *
 * Why this check exists. Eval runs 1 and 2 both delivered zero documents. Run
 * 2's trace settled the mechanism: sub-agents issued 836 tool calls and every
 * single one was `view` — not one write, in ~30 sub-agent invocations across
 * four agents and six specs. A two-agent probe then isolated the cause. The
 * `task` runtime DOES offer sub-agents `apply_patch` (the probe sub-agent
 * enumerated its own toolset as `functions.view, functions.apply_patch,
 * multi_tool_use.parallel`), but it also injects an instruction the probe
 * quoted verbatim: *"CRITICAL: Do NOT write output to files."* Under a mild
 * "you may create this file" prompt the sub-agent obeyed the runtime and never
 * attempted a write; under an explicit first-action mandate it wrote
 * immediately and successfully. Run 3 confirmed the fix at scale: 31
 * `code.lines_added` events and a complete document set from the three agents
 * that had been given a mandate — and nothing from the one that had not.
 *
 * The lesson this check encodes: **granting `edit` in frontmatter is not
 * enough.** Permission is not obligation. An agent that owns a file on disk
 * needs an affirmative, unmistakable duty to produce it, or it will politely
 * report that writes are unavailable and ship nothing.
 */
const WRITING_AGENTS: { agent: string; deliverable: string }[] = [
  { agent: "eis-context-analyst", deliverable: "{stm}/ledger/context-ledger.md" },
  { agent: "ux-pattern-researcher", deliverable: "{out}/ux-pattern-research.md" },
  { agent: "eis-author", deliverable: "{out}/eis.md" },
  { agent: "eis-critic", deliverable: "{stm}/artifacts/review-full-{round}.md" },
];

/** The literally-titled `##` headings each agent prompt must carry. */
const EXPECTED_SECTIONS: Record<string, string[]> = {
  "ux-interaction-spec": [
    "## Skills to Load",
    "## How to Delegate (Task Tool Mechanics)",
    "## Hard Delegation Rule (STOP-and-delegate)",
    "## Output Location Protocol",
    "## Non-Interactive Mode",
    "## File Access Boundaries",
    "## Must NOT",
  ],
  "eis-context-analyst": [
    "## Invocation Guard",
    "## Skills to Load",
    "## Output Location Inference",
    "## File Access Boundaries",
    "## Must NOT",
    "## Output Contract",
  ],
  "ux-pattern-researcher": [
    "## Invocation Guard",
    "## Skills to Load",
    "## Degradation Protocol",
    "## File Access Boundaries",
    "## Must NOT",
    "## Output Contract",
  ],
  "eis-author": [
    "## Invocation Guard",
    "## Skills to Load",
    "## Pass Protocol",
    "## File Access Boundaries",
    "## Must NOT",
    "## Output Contract",
  ],
  "eis-critic": [
    "## Invocation Guard",
    "## Skills to Load",
    "## Severity Model",
    "## File Access Boundaries",
    "## Must NOT",
    "## Output Contract",
  ],
};

const ORCHESTRATOR_TOOLS = ["read", "edit", "search", "agent"];

/**
 * The orchestrator's working character budget, CRLF-normalised.
 *
 * 26,000 against the hard 30,000 ceiling enforced one check above — a real
 * early-warning line, not a second wall.
 *
 * Slack is deliberately NOT restated here. It is derived by the check below as
 * `ORCHESTRATOR_BUDGET - lfLength(orchestrator)`, and that check's failure
 * message prints both operands. A literal in a comment drifts silently, and
 * this one did: it advertised "~700 chars of slack at the file's current
 * 25,302" and was still saying so at round 7 with the real figure at 89 — an
 * ~8x OVERSTATEMENT of headroom, on the one file every change lands in, aimed
 * squarely at the reader most likely to act on it. Same defect class as the
 * hand-maintained notation site list removed in the same round: a fact copied
 * by hand where it could have been computed.
 *
 * Point-in-time observation (round 7, 2026-08-26): the file is effectively AT
 * this budget. Future additions must reclaim space from duplicated prose and
 * push detail into the skill reference that already owns it — NOT raise this
 * constant. Raising it converts an early-warning line back into the second
 * wall it was created to replace.
 *
 * Why 26,000 (historical). The previous limit was 27,000 with the file at
 * 26,997: three characters of slack, measured with `\r` included, so a Windows
 * checkout — this repo's normal case — added ~535 chars and would have failed
 * the check on line endings alone. Both defects are fixed: `lfLength`
 * normalises, and the budget warns early. A review suggested 25,500;
 * compressing to fit that with meaningful slack would mean cutting
 * load-bearing delegation and gate content from an already dense prompt. The
 * file has come down from 29,817 at the initial build, all of it duplicated
 * prose. What remains is content, not fat.
 *
 * Scope: this is the ORCHESTRATOR's budget, not the pack's largest agent.
 * Those were the same file once and are not any more — `eis-critic` is larger
 * and is governed solely by the 30,000 ceiling above. Do not read this
 * constant, or the orchestrator's count, as a pack-wide maximum; the build
 * manifest tracks `max_agent_chars` and `orchestrator_chars` separately for
 * exactly this reason.
 */
const ORCHESTRATOR_BUDGET = 26000;

/**
 * Phrasings that turn a ceiling into a target or a budget. Every one of these
 * is a prompt-engineering defect, not a style preference: an agent that can
 * see how much of an allowance is unspent will spend it.
 */
const FORBIDDEN_CEILING_PHRASINGS = [
  "ask up to 14 questions",
  "perform 4 review rounds",
  "questions left",
  "questions remaining",
  "budget remaining",
];

/** The 22 EIS headings, verbatim and in order. */
const EIS_HEADINGS = [
  "## 1. Executive Summary",
  "## 2. Scope",
  "## 3. Experience Goals",
  "## 4. Actors and Roles",
  "## 5. Conceptual Model",
  "## 6. Terminology",
  "## 7. Permissions and Capabilities",
  "## 8. State Models",
  "## 9. Entry Points and Discovery",
  "## 10. User Journeys",
  "## 11. Business / System Workflows",
  "## 12. Service Blueprint",
  "## 13. Interaction Scenarios",
  "## 14. System Feedback and Notifications",
  "## 15. Error and Recovery Behavior",
  "## 16. Edge Cases",
  "## 17. Accessibility / Localization Considerations",
  "## 18. UX Requirements for Design Handoff",
  "## 19. Confirmed Decisions",
  "## 20. Assumptions",
  "## 21. Open Questions",
  "## 22. Requirements Traceability",
];

/** The 10 research-document headings, verbatim and in order. */
const RES_HEADINGS = [
  "## 1. Research Objective",
  "## 2. Host Product Analysis",
  "## 3. Competitive Products",
  "## 4. Adjacent Patterns",
  "## 5. Cross-Product Pattern Matrix",
  "## 6. Patterns We Recommend Adopting",
  "## 7. Patterns We Recommend Adapting",
  "## 8. Patterns We Recommend Rejecting",
  "## 9. Implications for the EIS",
  "## 10. Sources",
];

/** The 6 decision-log headings, verbatim and in order. */
const DL_HEADINGS = [
  "## Confirmed Decisions",
  "## Recommendations Awaiting Decision",
  "## Blocking Questions",
  "## Non-Blocking Questions",
  "## Assumptions",
  "## Contradictions / Risks",
];

const DL_ENTRY_FIELDS = [
  "Status:",
  "Decision:",
  "Rationale:",
  "Evidence:",
  "Implications:",
];

/**
 * Deliverable filename -> the closed heading set its contract defines. Any
 * `## n. Title` a behavioural spec asserts against one of these documents must
 * be a member: a spec that asserts a heading the contract does not define
 * fails by construction, and the tempting "fix" is to change the contract.
 */
const DOC_HEADINGS: Record<string, string[]> = {
  "eis.md": EIS_HEADINGS,
  "ux-pattern-research.md": RES_HEADINGS,
  "decision-log.md": DL_HEADINGS,
};

/**
 * Every file that states the RES-§9 header-row rule. The `skipped`-mode
 * carve-out — a header row with no data rows is the *contracted* form, not a
 * vacuity finding — must appear in all of them.
 *
 * This list is deliberately NOT "the files the last fix pass edited". A
 * round-6 review found the carve-out had landed in three of four sites: the
 * critic's own quality-bar SKILL.md still listed "a table with header rows and
 * no data rows" as empty, so a correct header-only RES-§9 could draw a
 * spurious C-5 `fail`. The agreement check at the time inspected exactly the
 * three files that had been edited, and was therefore structurally incapable
 * of noticing the fourth. An agreement check whose file list is derived from
 * what someone changed can never catch the site they missed.
 */
const CARVEOUT_OWNER = `${CONTRACTS}/research-doc-skeleton.md`;
const CARVEOUT_SITES: { file: string; label: string }[] = [
  { file: `${PACK}/agents/eis-critic.agent.md`, label: "the critic's C-10 non-vacuity floor" },
  {
    file: `${PACK}/skills/ux-research-method/references/evidence-discipline.md`,
    label: "evidence-discipline.md's vacuity rule",
  },
  { file: CARVEOUT_OWNER, label: "research-doc-skeleton.md (the owner of the rule)" },
  {
    file: `${PACK}/skills/eis-quality-bar/SKILL.md`,
    label: "the quality bar's C-5 emptiness detection — the critic's primary skill",
  },
];

/**
 * ---- the guard/caller cross-check ---------------------------------------
 *
 * Eval run 1 failed every behavioural spec with zero documents written. The
 * orchestrator loaded, built its session state, and delegated correctly — and
 * `@eis-author` replied with its Invocation Guard refusal text verbatim. The
 * guard's first condition is a *conjunction*: the prompt must come from
 * `@ux-interaction-spec` AND carry `Session:`, `Pass:` and the STM paths. The
 * worked call supplied every token — and opened with "You are being invoked as
 * @eis-author", which names the **callee** and never the **caller**. The one
 * conjunct the guard could not verify was the only one no worked call stated.
 *
 * That defect survived three review rounds and a 36-check structural suite
 * because nothing compared the two sides. The critic verified each worked
 * call's `Emit fenced blocks:` list against the sub-agent's Output Contract,
 * which is the *return* half of the handshake; nobody checked the *call* half.
 *
 * These two checks close it. `GUARD_CONTRACTS` is the single closed set: the
 * guard side must state what it demands, and the caller side must supply it.
 * Drift in either direction fails offline in milliseconds instead of costing a
 * 23-minute live run.
 */
interface GuardContract {
  /** Sub-agent id: both the filename stem and the frontmatter `name`. */
  agent: string;
  /**
   * Tokens this agent's `## Invocation Guard` demands of its caller, beyond
   * the shared preamble and the STM root. Spelled identically on both sides.
   */
  requires: string[];
  /**
   * Whether this agent's guard has been rewritten to quote the canonical
   * preamble verbatim. All four now do.
   */
  preambleMirrored: boolean;
}

/**
 * The session-state root is required by every guard, but the two sides spell
 * it differently and legitimately so: the guard names the literal path it will
 * look for, while the worked call carries the `{stm}` shorthand that the
 * orchestrator expands to that literal path before sending. The check asserts
 * each side in its own vocabulary rather than pretending one spelling fits
 * both — and a third check pins the definition that connects them.
 */
const STM_IN_GUARD = ".ux-interaction-spec-stm/runs/";
const STM_IN_CALL = "{stm}";

/**
 * The delegation preamble, stated once here and once in the orchestrator's
 * `## How to Delegate (Task Tool Mechanics)`. Every guard mirrors it; no guard
 * invents its own wording.
 */
function delegationPreamble(agent: string): string {
  return `Caller: @ux-interaction-spec (orchestrator) invoking @${agent}. Not a user or proxy invocation.`;
}

const GUARD_CONTRACTS: GuardContract[] = [
  { agent: "eis-context-analyst", requires: ["Session:"], preambleMirrored: true },
  { agent: "ux-pattern-researcher", requires: ["Session:"], preambleMirrored: true },
  { agent: "eis-author", requires: ["Session:", "Pass:"], preambleMirrored: true },
  { agent: "eis-critic", requires: ["Session:", "Round:"], preambleMirrored: true },
];

type Ctx = {
  root: string;
  read(rel: string): string | null;
  glob(pattern: string): string[];
};
type Result = boolean | [boolean, string];

function rel(ctx: Ctx, abs: string): string {
  return path.relative(ctx.root, abs).replace(/\\/g, "/");
}

/**
 * ---- section scoping: the tempered-greedy idiom ------------------------
 *
 * The engine's `sectionBody` is
 *     /#+\s+<name>\s*\n([\s\S]{0,max_chars})/i
 * with NO next-heading bound. `max_chars` is therefore "how far past the
 * heading to read, into whatever follows" — not "how much of the section to
 * read", which is what every author assumes it means. That makes every window
 * wrong in one of two directions, and both directions fail silently:
 *
 *   too small  -> the section is truncated and a needle living past the cutoff
 *                 reports "not present in <section>" when it IS present. Run 4
 *                 lost a check exactly this way: needles at index 4,158 of a
 *                 10,921-char section against a 4,000-char window.
 *   too large  -> the window spills into the sections that follow and the
 *                 assertion passes on THEIR text. Proven by mutation: raising
 *                 that same window to 16,000 passes in 4 of 6 run-4 documents
 *                 with section 8's entire state vocabulary stripped out.
 *
 * A raised window converts a false negative into a vacuous check, which is
 * strictly worse. The fix is to stop windowing and bound the scan at the next
 * H2 with a tempered token. `\s` does not match `#`, so `\n##\s` matches an H2
 * and never an H3 — subsections stay inside the scan, as they should.
 *
 * Measured across all nine section-scoped assertions this pack shipped, not one
 * had a window that was correct by design: four truncated, four spilled, one
 * fitted by luck. There is therefore no legitimate remaining use to carve out,
 * and the checks below ban the construct outright rather than allowing it with
 * conditions that would be re-litigated by the next author.
 */
const TEMPERED_SCAN = "(?:(?!\\n##\\s)[\\s\\S])*";

/** Every decoded `pattern:` literal in a spec, with its line and target doc. */
function specPatterns(
  ctx: Ctx,
  file: string,
): { line: number; pat: string; doc: string | null }[] {
  const out: { line: number; pat: string; doc: string | null }[] = [];
  const lines = ctx.read(rel(ctx, file))!.split(/\r?\n/);
  for (let i = 0; i < lines.length; i++) {
    const ln = lines[i]!;
    if (/^\s*#/.test(ln)) continue; // a YAML comment, not an assertion
    const pm = /path:\s*"([^"]+)"/.exec(ln);
    for (const m of ln.matchAll(/pattern:\s*"((?:[^"\\]|\\.)*)"/g)) {
      let pat: string;
      try {
        pat = JSON.parse(`"${m[1]}"`) as string;
      } catch {
        continue;
      }
      out.push({ line: i + 1, pat, doc: pm ? path.basename(pm[1]!) : null });
    }
  }
  return out;
}

/**
 * Literal heading anchors inside a regex pattern, reconstructed from the regex
 * source: `##\s+8\.\s+State Models(?:...` -> `## 8. State Models`, plus the
 * offset just past the reconstructed title so the caller can inspect what the
 * anchor is followed by.
 *
 * Only `##\s+` starts an anchor. The tempered token's own `\n##\s)` has no `+`,
 * so the scan bound is never mistaken for a second anchor.
 */
function headingAnchorsIn(pat: string): { heading: string; after: number }[] {
  const out: { heading: string; after: number }[] = [];
  const re = /##\\s\+/g;
  let m: RegExpExecArray | null;
  while ((m = re.exec(pat)) !== null) {
    let i = m.index + m[0].length;
    let title = "";
    while (i < pat.length) {
      if (pat.startsWith("\\s+", i)) { title += " "; i += 3; continue; }
      if (pat.startsWith("\\.", i)) { title += "."; i += 2; continue; }
      if ("\\()[]{}|*+?^$".includes(pat[i]!)) break;
      title += pat[i];
      i += 1;
    }
    const t = title.trim();
    if (t) out.push({ heading: `## ${t}`, after: i });
  }
  return out;
}

function splitFrontmatter(text: string): { fmLines: string[]; body: string } {
  const lines = text.split(/\r?\n/);
  if (!lines.length || lines[0]!.trim() !== "---") {
    throw new Error("frontmatter must start at line 1");
  }
  let end = -1;
  for (let i = 1; i < lines.length; i++) {
    if (lines[i]!.trim() === "---") {
      end = i;
      break;
    }
  }
  if (end === -1) throw new Error("frontmatter block is not closed");
  return { fmLines: lines.slice(1, end), body: lines.slice(end + 1).join("\n") };
}

function topLevelKeys(fmLines: string[]): string[] {
  const keys: string[] = [];
  for (const ln of fmLines) {
    if (ln && !/^\s/.test(ln) && ln.includes(":")) {
      keys.push(ln.split(":", 1)[0]!.trim());
    }
  }
  return keys;
}

function fmValue(fmLines: string[], key: string): string | null {
  const ln = fmLines.find((l) => l.startsWith(`${key}:`));
  if (!ln) return null;
  return ln.slice(key.length + 1).trim();
}

/**
 * Assert every needle appears, in order, with strictly increasing position.
 * Tolerates a later duplicate (a worked example quoting a real heading) that a
 * naive count-based check would trip over.
 */
function orderedContains(text: string, needles: string[]): string | null {
  let cursor = 0;
  for (const n of needles) {
    const at = text.indexOf(n, cursor);
    if (at === -1) {
      return text.includes(n)
        ? `heading out of order: ${JSON.stringify(n)}`
        : `missing heading: ${JSON.stringify(n)}`;
    }
    cursor = at + n.length;
  }
  return null;
}

/** Strip fenced code blocks so heading scans see real Markdown headings. */
function stripFences(text: string): string {
  return text.replace(/```[\s\S]*?```/g, "");
}

/** Normalise CRLF away before measuring length. A Windows checkout must not
 *  fail a character-budget check on content-neutral grounds. */
function lfLength(text: string): number {
  return text.replace(/\r/g, "").length;
}

/** Escape a literal for use inside a RegExp. */
function reEscape(s: string): string {
  return s.replace(/[.*+?^${}()|[\]\\]/g, "\\$&");
}

/**
 * Blank-line-delimited blocks. A "declaring block" is the unit of agreement:
 * a value that merely occurs somewhere in the same *file* proves nothing, but
 * a value that occurs in the same paragraph, table, list or fenced record as
 * the field name is a restatement of the set.
 */
function blocksOf(text: string): string[] {
  return text.replace(/\r/g, "").split(/\n[ \t]*\n/);
}

/**
 * Delimiter-safe token match. `[^A-Za-z0-9_-]` on both sides, so `adjacent`
 * does NOT match inside `adjacent-domain` and `competitor` does NOT match
 * inside `competitors`. Substring matching is what made the first version of
 * the agreement check vacuous.
 */
function namesToken(text: string, token: string): boolean {
  return new RegExp(`(^|[^A-Za-z0-9_-])${reEscape(token)}([^A-Za-z0-9_-]|$)`).test(text);
}

/** The first block naming the anchor token and every value, or null. */
function declaringBlock(text: string, e: SharedEnum): string | null {
  return (
    blocksOf(text).find(
      (b) => namesToken(b, e.anchor) && e.values.every((v) => namesToken(b, v)),
    ) ?? null
  );
}

/** Every `*.md` file shipped inside the pack. */
function packMarkdown(ctx: Ctx): string[] {
  return [
    ...ctx.glob(`${PACK}/agents/*.md`),
    ...ctx.glob(`${PACK}/skills/**/*.md`),
    ...ctx.glob(`${PACK}/*.md`),
  ].map((f) => rel(ctx, f));
}

/**
 * Every file the `EIS-§`/`RES-§` notation rules are scanned across.
 *
 * Deliberately a glob, not a hand-maintained list. The notation leak has now
 * been "fixed" three times and reappeared twice, and both reappearances were
 * scope failures rather than logic failures: the instance sat in a file nobody
 * had thought to enumerate. Round 6 added `ux-pattern-researcher.agent.md`
 * after a leak hid there; round 7 then found one in `research-doc-skeleton.md`
 * and another in `synthesis-and-precedent.md`, neither listed — and the
 * orchestrator, the first file the author agent reads, had never been scanned
 * at all. A list that must be remembered is a list that will be forgotten.
 *
 * `*.eval.md` specs are included because a spec's own prose is read by whoever
 * maintains the pack. `*.eval.ts` is excluded: this file quotes the forbidden
 * form on purpose in order to explain it.
 *
 * Round 8 added the eval-suite README and the fixtures, aligning this scope
 * with the mojibake check's, which had scanned both all along. The asymmetry
 * was an oversight rather than a decision, and the fixtures half of it is the
 * part that matters: a fixture is not documentation *about* the pack, it is
 * material an agent **reads as input while writing headings**. A sigil in
 * heading position there is a live teaching vector, and a stronger one than a
 * sigil in a skill file, because the author treats input as ground truth about
 * the domain. Both were verified clean when the scope was widened.
 */
function notationScanSites(ctx: Ctx): string[] {
  return [
    ...packMarkdown(ctx),
    ...ctx.glob(`${EVALS}/*.eval.md`).map((f) => rel(ctx, f)),
    ...ctx.glob(`${EVALS}/README.md`).map((f) => rel(ctx, f)),
    ...ctx.glob(`${EVALS}/fixtures/**/*.md`).map((f) => rel(ctx, f)),
  ];
}

/**
 * The sanctioned way to name the bad form: a `##`-prefixed sigil inside a code
 * span, printed beside the sentence forbidding it (`` `## EIS-§8 State Models`
 * is a contract violation ``). Three teaching sites rely on this, so the
 * juxtaposition scan strips these spans before looking for leaks.
 *
 * The exemption is bounded by the heading-position check, which reads raw text
 * and fails any sigil that reaches a real heading — so a genuine wrong-form
 * heading cannot hide behind the exemption.
 */
const SANCTIONED_COUNTEREXAMPLE = /`#{1,6}\s+(?:EIS|RES)-§[^`]*`/g;


/** Real `## <name>` headings, outside fenced blocks. */
function hasRealHeading(text: string, heading: string): boolean {
  const escaped = heading.replace(/[.*+?^${}()|[\]\\]/g, "\\$&");
  return new RegExp(`^${escaped}\\s*$`, "m").test(stripFences(text));
}

/**
 * Collapse all whitespace runs to one space. A guard requirement that is
 * satisfied must stay satisfied when the surrounding Markdown rewraps, so
 * these comparisons are line-break-insensitive by construction.
 */
function flat(text: string): string {
  return text.replace(/\s+/g, " ").trim();
}

/**
 * The body of a `## <heading>` section, up to the next `## ` heading.
 * Returns null when the section is absent.
 */
function sectionBody(text: string, heading: string): string | null {
  const lines = text.replace(/\r/g, "").split("\n");
  const start = lines.findIndex((l) => l.trim() === heading);
  if (start === -1) return null;
  const rest = lines.slice(start + 1);
  const end = rest.findIndex((l) => /^## /.test(l));
  return (end === -1 ? rest : rest.slice(0, end)).join("\n");
}

/**
 * A guard's *admitting condition* — numbered item 1, up to item 2.
 *
 * Scoping matters. The first version of this check searched the whole
 * `## Invocation Guard` section, and a mutation that deleted the STM root from
 * the admitting condition stayed green: the later "Signs the caller is not the
 * real orchestrator" paragraph mentions the same path, so the token was still
 * present in the section while the condition that actually gates the work had
 * lost it. A check satisfied by prose elsewhere in the file is the same class
 * of vacuity the shared-enum checks were rewritten to avoid.
 */
function admittingCondition(guard: string): string {
  const lines = guard.split("\n");
  const start = lines.findIndex((l) => /^1\.\s/.test(l));
  if (start === -1) return "";
  const rest = lines.slice(start);
  const end = rest.findIndex((l) => /^2\.\s/.test(l));
  return (end === -1 ? rest : rest.slice(0, end)).join("\n");
}

/**
 * The orchestrator's worked `task(...)` calls, keyed by `agent_type`. Each is
 * a fenced block whose first line is `task(`; the delegated prompt is the
 * whole block, which is what the sub-agent's guard will be reading.
 */
function workedCalls(orchestrator: string): Map<string, string> {
  const calls = new Map<string, string>();
  for (const m of orchestrator.replace(/\r/g, "").matchAll(/```\n(task\([\s\S]*?)```/g)) {
    const block = m[1]!;
    const at = block.match(/agent_type:\s*"([^"]+)"/);
    if (at) calls.set(at[1]!, block);
  }
  return calls;
}

export default new Eval("ux-interaction-spec-pack-shape", {
  kind: "none",
  tags: ["pack", "structural", "tooling"],
})
  .summarize(
    "ux-interaction-spec ships as a mechanically loadable Copilot plugin " +
      "whose agents, skills, document contracts and eval suite agree with " +
      "each other.",
  )
  .describe(
    "Structural conformance with no SUT: plugin packaging, additive " +
      "marketplace registration, agent inventory and invocation flags, the " +
      "two-part ask_user discipline, ceiling-not-target framing, the three " +
      "verbatim document skeletons, and self-checks over the five " +
      "behavioural eval specs.",
  )

  // ---- group 1: plugin packaging ----------------------------------------

  .check("plugin.json manifest", (ctx: Ctx): Result => {
    const text = ctx.read(`${PACK}/plugin.json`);
    if (text === null) return [false, "missing plugin.json"];
    let m: Record<string, unknown>;
    try {
      m = JSON.parse(text);
    } catch (e) {
      return [false, `plugin.json does not parse: ${(e as Error).message}`];
    }
    for (const key of ["name", "description", "version", "agents", "skills"]) {
      if (!(key in m)) return [false, `plugin.json missing key '${key}'`];
    }
    if (m.name !== "ux-interaction-spec") {
      return [false, `unexpected name ${JSON.stringify(m.name)}`];
    }
    if (m.agents !== "agents/") {
      return [false, `agents must be the string 'agents/', got ${JSON.stringify(m.agents)}`];
    }
    if (m.skills !== "skills/") {
      return [false, `skills must be the string 'skills/', got ${JSON.stringify(m.skills)}`];
    }
    return true;
  })

  .check("pack has no local .github tree", (ctx: Ctx): Result => {
    const strays = ctx.glob(`${PACK}/.github/**/*`);
    if (strays.length) {
      return [
        false,
        `plugin layout uses agents/ + skills/ at the pack root; found ${strays.length} file(s) under ${PACK}/.github/`,
      ];
    }
    return true;
  })

  .check("marketplace registration is additive", (ctx: Ctx): Result => {
    const text = ctx.read(MARKETPLACE);
    if (text === null) return [false, "missing marketplace.json"];
    let plugins: { name: string; version?: string; source?: string }[];
    try {
      plugins = JSON.parse(text).plugins;
    } catch (e) {
      return [false, `marketplace.json does not parse: ${(e as Error).message}`];
    }
    const byName = new Map(plugins.map((p) => [p.name, p]));
    for (const n of PRIOR_MARKETPLACE_ENTRIES) {
      if (!byName.has(n)) return [false, `pre-existing entry '${n}' was removed`];
    }
    const mine = byName.get("ux-interaction-spec");
    if (!mine) return [false, "ux-interaction-spec is not registered"];
    if (mine.source !== PACK) {
      return [false, `source must be '${PACK}', got ${JSON.stringify(mine.source)}`];
    }
    const manifest = JSON.parse(ctx.read(`${PACK}/plugin.json`)!);
    if (mine.version !== manifest.version) {
      return [
        false,
        `marketplace version ${JSON.stringify(mine.version)} != plugin.json version ${JSON.stringify(manifest.version)}`,
      ];
    }
    if (plugins.length !== PRIOR_MARKETPLACE_ENTRIES.length + 1) {
      return [
        false,
        `expected ${PRIOR_MARKETPLACE_ENTRIES.length + 1} entries, found ${plugins.length}`,
      ];
    }
    return true;
  })

  .check("README carries both install commands", (ctx: Ctx): Result => {
    const text = ctx.read(`${PACK}/README.md`);
    if (text === null) return [false, "missing README.md"];
    const needed = [
      "copilot plugin marketplace add srulyt/srulys-agent-packs",
      "copilot plugin install ux-interaction-spec@srulys-agent-packs",
    ];
    for (const n of needed) {
      if (!text.includes(n)) return [false, `README missing: ${n}`];
    }
    if (!/write-once/i.test(text)) {
      return [false, "README must explain the write-once output-location protocol"];
    }
    if (!text.includes("filename stem")) {
      return [
        false,
        "README must record why frontmatter `name` equals the filename stem, so a reviewer does not 'fix' it",
      ];
    }
    return true;
  })

  // ---- group 2: agent inventory and invocation flags --------------------

  .check("five agents plus the author pass plan", (ctx: Ctx): Result => {
    const found = new Set(
      ctx
        .glob(`${PACK}/agents/*.agent.md`)
        .map((p) => path.basename(p).replace(/\.agent\.md$/, "")),
    );
    for (const a of EXPECTED_AGENTS) {
      if (!found.has(a)) return [false, `missing agent: ${a}`];
    }
    if (found.size !== EXPECTED_AGENTS.length) {
      return [false, `expected ${EXPECTED_AGENTS.length} agents, found ${found.size}`];
    }
    const passes = ctx.read(`${PACK}/agents/eis-author.passes.md`);
    if (passes === null) return [false, "missing agents/eis-author.passes.md"];
    if (passes.startsWith("---")) {
      return [
        false,
        "eis-author.passes.md must have NO frontmatter — the loader registers only *.agent.md, and frontmatter would invite it to register this file as an agent",
      ];
    }
    return true;
  })

  .check("agent frontmatter: quoted, supported keys, name == stem", (ctx: Ctx): Result => {
    for (const file of ctx.glob(`${PACK}/agents/*.agent.md`)) {
      const r = rel(ctx, file);
      const stem = path.basename(file).replace(/\.agent\.md$/, "");
      const text = ctx.read(r)!;
      let fmLines: string[];
      try {
        ({ fmLines } = splitFrontmatter(text));
      } catch (e) {
        return [false, `${r}: ${(e as Error).message}`];
      }
      const keys = topLevelKeys(fmLines);
      if (keys.length !== new Set(keys).size) {
        return [false, `${r}: duplicate frontmatter key`];
      }
      for (const k of keys) {
        if (!SUPPORTED_AGENT_KEYS.has(k)) {
          return [false, `${r}: unsupported frontmatter key '${k}'`];
        }
      }
      const desc = fmValue(fmLines, "description");
      if (desc === null) return [false, `${r}: missing description`];
      if (!(desc.startsWith('"') && desc.endsWith('"'))) {
        return [false, `${r}: description must be double-quoted`];
      }
      const name = (fmValue(fmLines, "name") ?? "").replace(/^"|"$/g, "");
      if (name !== stem) {
        return [
          false,
          `${r}: frontmatter name ${JSON.stringify(name)} must equal the filename stem ${JSON.stringify(stem)} — this pack deliberately keeps them identical so task(agent_type: ...) resolves under either documented rule`,
        ];
      }
    }
    return true;
  })

  .check("invocation flags are role-correct", (ctx: Ctx): Result => {
    for (const file of ctx.glob(`${PACK}/agents/*.agent.md`)) {
      const r = rel(ctx, file);
      const stem = path.basename(file).replace(/\.agent\.md$/, "");
      const { fmLines } = splitFrontmatter(ctx.read(r)!);
      const joined = fmLines.join("\n");
      if (stem === ORCHESTRATOR) {
        if (!joined.includes("disable-model-invocation: true")) {
          return [
            false,
            `${r}: orchestrator needs disable-model-invocation: true so another agent cannot proxy-call it`,
          ];
        }
        if (!joined.includes("user-invocable: true")) {
          return [false, `${r}: orchestrator must be user-invocable`];
        }
      } else {
        if (!joined.includes("user-invocable: false")) {
          return [false, `${r}: subagent must set user-invocable: false`];
        }
        if (joined.includes("disable-model-invocation")) {
          return [
            false,
            `${r}: subagent must NOT set disable-model-invocation — it would remove the agent from the orchestrator's task registry and make it un-invokable`,
          ];
        }
      }
    }
    return true;
  })

  .check("orchestrator tools are exactly the least-privilege set", (ctx: Ctx): Result => {
    const { fmLines } = splitFrontmatter(ctx.read(`${PACK}/agents/${ORCHESTRATOR}.agent.md`)!);
    const raw = fmValue(fmLines, "tools");
    if (raw === null) return [false, "orchestrator has no tools list"];
    if (raw.includes("*")) return [false, "tools must not be a wildcard"];
    const got = [...raw.matchAll(/"([a-z_]+)"/g)].map((m) => m[1]!);
    const want = [...ORCHESTRATOR_TOOLS].sort().join(",");
    if ([...got].sort().join(",") !== want) {
      return [false, `orchestrator tools ${JSON.stringify(got)} != ${JSON.stringify(ORCHESTRATOR_TOOLS)}`];
    }
    return true;
  })

  .check("no agent is granted execute", (ctx: Ctx): Result => {
    for (const file of ctx.glob(`${PACK}/agents/*.agent.md`)) {
      const r = rel(ctx, file);
      const { fmLines } = splitFrontmatter(ctx.read(r)!);
      const raw = fmValue(fmLines, "tools") ?? "";
      if (raw.includes("*")) return [false, `${r}: tools must not be a wildcard`];
      if (/"execute"/.test(raw)) {
        return [false, `${r}: no agent in this pack has a justified use for execute`];
      }
    }
    return true;
  })

  .check("every agent carries its mandated sections", (ctx: Ctx): Result => {
    for (const [agent, sections] of Object.entries(EXPECTED_SECTIONS)) {
      const text = ctx.read(`${PACK}/agents/${agent}.agent.md`);
      if (text === null) return [false, `missing agent file for ${agent}`];
      for (const s of sections) {
        if (!text.includes(s)) return [false, `${agent}: missing section '${s}'`];
      }
    }
    const orch = EXPECTED_SECTIONS[ORCHESTRATOR]!;
    if (orch.length !== 7) {
      return [false, `orchestrator section list must have 7 entries, has ${orch.length}`];
    }
    return true;
  })

  .check("every writing agent carries an affirmative write duty, not just permission", (ctx: Ctx): Result => {
    for (const { agent, deliverable } of WRITING_AGENTS) {
      const text = ctx.read(`${PACK}/agents/${agent}.agent.md`);
      if (text === null) return [false, `missing agent file for ${agent}`];

      const start = text.indexOf("## Write Mandate");
      if (start === -1) {
        return [
          false,
          `${agent}: no '## Write Mandate' section. Granting \`edit\` in frontmatter is not enough — ` +
            "the task runtime injects \"CRITICAL: Do NOT write output to files.\" into sub-agent context, " +
            "and eval runs 1 and 2 produced zero documents because every specialist obeyed it.",
        ];
      }
      const next = text.indexOf("\n## ", start + 1);
      const body = flat(text.slice(start, next === -1 ? text.length : next));

      if (!/apply_patch/.test(body)) {
        return [
          false,
          `${agent}: '## Write Mandate' never names \`apply_patch\` — the agent must be told the tool it actually holds, not the \`edit\` alias from its frontmatter`,
        ];
      }
      if (!/has \*\*FAILED\*\*|has FAILED/i.test(body)) {
        return [
          false,
          `${agent}: '## Write Mandate' never states that a run writing no file has FAILED. ` +
            "Without a failure definition the agent can report a complete, honest envelope having written nothing — exactly what run 2 did six times.",
        ];
      }
      if (!/UNAVAILABLE/.test(body) || !/verbatim/.test(body)) {
        return [
          false,
          `${agent}: '## Write Mandate' must make \`UNAVAILABLE\` legal only after a real failed \`apply_patch\` call, quoted verbatim. An unguarded escape hatch is how run 2 reported a capability limit that did not exist.`,
        ];
      }
      if (!/parent director|missing parent|does not exist yet/i.test(body)) {
        return [
          false,
          `${agent}: '## Write Mandate' never authorises creating a missing directory. An absent {out} reads as a boundary violation unless creating it is explicitly expected.`,
        ];
      }
      if (!body.includes(deliverable)) {
        return [
          false,
          `${agent}: '## Write Mandate' never names the deliverable it owns (${deliverable}). A duty with no object is not a duty.`,
        ];
      }
    }
    return true;
  })

  .check("every agent granted `edit` is accounted for as a writing agent", (ctx: Ctx): Result => {
    const mandated = new Set(WRITING_AGENTS.map((w) => w.agent));
    for (const file of ctx.glob(`${PACK}/agents/*.agent.md`)) {
      const r = rel(ctx, file);
      const stem = r.replace(/^.*[\\/]/, "").replace(/\.agent\.md$/, "");
      const { fmLines } = splitFrontmatter(ctx.read(r)!);
      const raw = fmValue(fmLines, "tools") ?? "";
      const hasEdit = /"edit"/.test(raw);

      if (hasEdit && stem !== ORCHESTRATOR && !mandated.has(stem)) {
        return [
          false,
          `${stem}: frontmatter grants \`edit\`, but the agent is absent from WRITING_AGENTS, so no '## Write Mandate' is demanded of it.\n` +
            "    This is the exact hole eis-critic fell through for three fix turns. Its output is an STM artifact rather than a user-facing " +
            "deliverable, so it was hand-waved off the list as unreachable by assertions — and shipped with write permission but no write duty. " +
            "Run 3 then wrote every deliverable correctly and still failed, because the one unmandated agent never created " +
            "{stm}/artifacts/ and the review phase was skipped-with-gap.\n" +
            "    Reachability by an assertion is not what makes a write load-bearing. Either add the agent to WRITING_AGENTS with the artifact " +
            "it owns, or drop `edit` from its tools. An agent may not hold write access with no stated obligation.",
        ];
      }
      if (!hasEdit && mandated.has(stem)) {
        return [
          false,
          `${stem}: listed in WRITING_AGENTS and required to carry a '## Write Mandate', but its frontmatter does not grant \`edit\`.\n` +
            "    A mandate the toolset cannot satisfy is worse than no mandate: the agent tries, fails, and then correctly reports UNAVAILABLE — " +
            "which is indistinguishable from the fabricated UNAVAILABLE the mandate exists to forbid.",
        ];
      }
    }
    return true;
  })

  .check("every writing worked call carries the WRITE MANDATE line", (ctx: Ctx): Result => {
    const text = ctx.read(`${PACK}/agents/${ORCHESTRATOR}.agent.md`);
    if (text === null) return [false, `missing ${ORCHESTRATOR}.agent.md`];
    const calls = workedCalls(text);
    for (const { agent } of WRITING_AGENTS) {
      const call = calls.get(agent);
      if (!call) return [false, `orchestrator has no worked call for ${JSON.stringify(agent)}`];
      if (!/WRITE MANDATE/.test(call)) {
        return [
          false,
          `orchestrator worked call for ${JSON.stringify(agent)} omits the WRITE MANDATE line. ` +
            "The agent file's mandate is the primary lever, but the delegation prompt is what the sub-agent reads first, " +
            "and the probe showed a specialist writes when the call demands it and stays silent when it does not.",
        ];
      }
    }
    return true;
  })

  .check("every agent's Skills to Load names >= 2 path-ladder rungs", (ctx: Ctx): Result => {
    for (const agent of EXPECTED_AGENTS) {
      const text = ctx.read(`${PACK}/agents/${agent}.agent.md`)!;
      const start = text.indexOf("## Skills to Load");
      if (start === -1) return [false, `${agent}: no '## Skills to Load' section`];
      const nextHeading = text.indexOf("\n## ", start + 1);
      const body = text.slice(start, nextHeading === -1 ? text.length : nextHeading);
      const rungs = [
        /\.github\/(skills|agents)\//,
        new RegExp(`agent-packs/ux-interaction-spec/(skills|agents)/`),
        /(^|\n)\s*\d+\.\s+`?(skills|agents)\//,
      ].filter((re) => re.test(body)).length;
      if (rungs < 2) {
        return [
          false,
          `${agent}: '## Skills to Load' must name at least two resolution rungs so the file is findable in both the repo clone and the installed-plugin layout (found ${rungs})`,
        ];
      }
    }
    return true;
  })

  .check("ask_user discipline: orchestrator calls it, sub-agents never do", (ctx: Ctx): Result => {
    const orch = ctx.read(`${PACK}/agents/${ORCHESTRATOR}.agent.md`)!;
    if (!orch.includes("ask_user(")) {
      return [
        false,
        "orchestrator prompt must contain a literal ask_user( call example — it is the only agent that talks to the user",
      ];
    }
    for (const agent of SUBAGENTS) {
      const text = ctx.read(`${PACK}/agents/${agent}.agent.md`)!;
      if (text.includes("ask_user(")) {
        return [
          false,
          `${agent}: sub-agent prompts must not contain a literal ask_user( call — an example is an invitation`,
        ];
      }
      const mustNot = text.slice(text.indexOf("## Must NOT"));
      if (!mustNot.includes("`ask_user`")) {
        return [
          false,
          `${agent}: '## Must NOT' must name \`ask_user\` in backticks so the prohibition is explicit`,
        ];
      }
    }
    return true;
  })

  .check("ceilings are framed as ceilings, never as targets", (ctx: Ctx): Result => {
    const orch = ctx.read(`${PACK}/agents/${ORCHESTRATOR}.agent.md`)!;
    const lower = orch.toLowerCase();
    for (const phrase of FORBIDDEN_CEILING_PHRASINGS) {
      if (lower.includes(phrase.toLowerCase())) {
        return [
          false,
          `orchestrator contains budget-framing phrase ${JSON.stringify(phrase)} — a ceiling an agent can count down is a quota it will spend`,
        ];
      }
    }
    for (const n of ["4", "14", "2"]) {
      const re = new RegExp(`\\b${n}\\b`);
      if (!re.test(orch)) return [false, `orchestrator never mentions the cap value ${n}`];
    }
    if (!/ceiling/i.test(orch)) {
      return [false, "orchestrator never uses the word 'ceiling'"];
    }
    const ceilings = orch.toLowerCase().split("ceiling").length - 1;
    if (ceilings < 4) {
      return [
        false,
        `the word 'ceiling' appears ${ceilings} time(s); each of the four caps (review rounds, specialist retries, research top-ups, questions per gate) must be framed as one`,
      ];
    }
    if (!/value test/i.test(orch)) {
      return [
        false,
        "the 'important' question decision must be a value test, not a budget test — the orchestrator never says 'value test'",
      ];
    }
    return true;
  })

  .check("every agent prompt is under the 30,000-character ceiling", (ctx: Ctx): Result => {
    for (const file of ctx.glob(`${PACK}/agents/*.agent.md`)) {
      const r = rel(ctx, file);
      const len = lfLength(ctx.read(r)!);
      if (len >= 30000) return [false, `${r}: ${len} chars (ceiling 30000)`];
    }
    return true;
  })

  .check("the orchestrator keeps a real slack budget under the ceiling", (ctx: Ctx): Result => {
    const r = `${PACK}/agents/${ORCHESTRATOR}.agent.md`;
    // Measured with CRLF normalised away. A Windows checkout adds ~535 bytes
    // of \r to this file; failing the budget on line endings would be a
    // content-neutral failure, and this repo is developed on Windows.
    const len = lfLength(ctx.read(r)!);
    if (len > ORCHESTRATOR_BUDGET) {
      return [
        false,
        `${r}: ${len} chars — over the ${ORCHESTRATOR_BUDGET} working budget (hard ceiling ${30000}). ` +
          "The orchestrator is the file every change lands in, so it must not sit against the wall: " +
          "a routine edit would breach a hard limit and take the whole pack offline. " +
          "Move detail into the skill reference that already owns it and leave a pointer.",
      ];
    }
    return true;
  })

  // ---- group 3: skills and document contracts ---------------------------

  .check("four skills with supported, quoted frontmatter", (ctx: Ctx): Result => {
    const dirs = new Set(
      ctx.glob(`${PACK}/skills/*/SKILL.md`).map((p) => path.basename(path.dirname(p))),
    );
    for (const s of EXPECTED_SKILLS) {
      if (!dirs.has(s)) return [false, `missing skill: ${s}`];
    }
    if (dirs.size !== EXPECTED_SKILLS.length) {
      return [false, `expected ${EXPECTED_SKILLS.length} skills, found ${dirs.size}`];
    }
    for (const s of EXPECTED_SKILLS) {
      const r = `${PACK}/skills/${s}/SKILL.md`;
      const { fmLines } = splitFrontmatter(ctx.read(r)!);
      const keys = topLevelKeys(fmLines);
      for (const k of keys) {
        if (!SUPPORTED_SKILL_KEYS.has(k)) {
          return [false, `${r}: unsupported frontmatter key '${k}'`];
        }
      }
      const desc = fmValue(fmLines, "description");
      if (desc === null) return [false, `${r}: missing description`];
      if (!(desc.startsWith('"') && desc.endsWith('"'))) {
        return [false, `${r}: description must be double-quoted`];
      }
      const name = (fmValue(fmLines, "name") ?? "").replace(/^"|"$/g, "");
      if (name !== s) return [false, `${r}: name ${JSON.stringify(name)} != directory ${JSON.stringify(s)}`];
    }
    return true;
  })

  .check("EIS skeleton carries all 22 headings in order", (ctx: Ctx): Result => {
    const text = ctx.read(`${CONTRACTS}/eis-skeleton.md`);
    if (text === null) return [false, "missing eis-skeleton.md"];
    const err = orderedContains(text, EIS_HEADINGS);
    if (err) return [false, `eis-skeleton.md: ${err}`];
    if (!text.includes("<!-- EIS-PENDING")) {
      return [false, "eis-skeleton.md must define the EIS-PENDING sentinel"];
    }
    if (!text.includes("# [Feature] Experience Interaction Specification")) {
      return [false, "eis-skeleton.md must carry the verbatim title line"];
    }
    return true;
  })

  .check("research skeleton carries all 10 headings in order", (ctx: Ctx): Result => {
    const text = ctx.read(`${CONTRACTS}/research-doc-skeleton.md`);
    if (text === null) return [false, "missing research-doc-skeleton.md"];
    const err = orderedContains(text, RES_HEADINGS);
    if (err) return [false, `research-doc-skeleton.md: ${err}`];
    if (!text.includes("research_mode: skipped")) {
      return [
        false,
        "research-doc-skeleton.md must pin the verbatim skipped-mode declaration — the document contract is unconditional",
      ];
    }
    for (const pinned of ["host_product: none", "competitors: 0", "adjacent: 0"]) {
      if (!text.includes(pinned)) {
        return [
          false,
          `research-doc-skeleton.md must pin the skipped-mode coverage value '${pinned}' so a skipped run's DoD arithmetic is true by construction`,
        ];
      }
    }
    if (!text.includes("pattern verdicts not recorded")) {
      return [
        false,
        "research-doc-skeleton.md must state the non-vacuity floor rule '§5 — pattern verdicts not recorded'",
      ];
    }
    return true;
  })

  .check("decision-log skeleton carries all 6 headings and 5 entry fields", (ctx: Ctx): Result => {
    const text = ctx.read(`${CONTRACTS}/decision-log-skeleton.md`);
    if (text === null) return [false, "missing decision-log-skeleton.md"];
    const err = orderedContains(text, DL_HEADINGS);
    if (err) return [false, `decision-log-skeleton.md: ${err}`];
    for (const f of DL_ENTRY_FIELDS) {
      if (!text.includes(f)) return [false, `decision-log-skeleton.md: missing entry field '${f}'`];
    }
    return true;
  })

  .check("ledger format defines all six ledgers and the highest-round rule", (ctx: Ctx): Result => {
    const text = ctx.read(`${CONTRACTS}/ledger-format.md`);
    if (text === null) return [false, "missing ledger-format.md"];
    for (const l of [
      "context-ledger.md",
      "requirements.md",
      "evidence.md",
      "coverage.md",
      "decisions.md",
      "questions.md",
    ]) {
      if (!text.includes(l)) return [false, `ledger-format.md: no schema for ${l}`];
    }
    if (!/highest/i.test(text)) {
      return [
        false,
        "ledger-format.md must state that a reader takes the HIGHEST round — the ledgers are append-only, so round 1 survives a revise round",
      ];
    }
    if (!text.includes("Coverage — round")) {
      return [false, "ledger-format.md: missing the Coverage — round N record schema"];
    }
    if (!/cumulative/i.test(text)) {
      return [
        false,
        "ledger-format.md must state that the Coverage record is cumulative for the run, or a top-up round would zero an earlier category",
      ];
    }
    return true;
  })

  .check("output-location reference carries the proposal block tokens", (ctx: Ctx): Result => {
    const text = ctx.read(`${CONTRACTS}/output-location.md`);
    if (text === null) return [false, "missing output-location.md"];
    for (const t of [
      "proposed_path",
      "confidence",
      "rationale",
      "alternatives",
      "supplied_path_consistent",
    ]) {
      if (!text.includes(t)) return [false, `output-location.md: missing field '${t}'`];
    }
    if (!/write-once/i.test(text)) {
      return [false, "output-location.md must state the write-once rule"];
    }
    if (!/diverge/i.test(text)) {
      return [
        false,
        "output-location.md must split the echo case (silent) from the divergence case (a CONCERN in state.errors[])",
      ];
    }
    return true;
  })

  .check("quality bar references are complete", (ctx: Ctx): Result => {
    const antireq = ctx.read(`${QUALITY}/anti-requirements.md`);
    if (antireq === null) return [false, "missing anti-requirements.md"];

    const probes = ctx.read(`${QUALITY}/discovery-probes.md`);
    if (probes === null) return [false, "missing discovery-probes.md"];
    const probeRows = [...probes.matchAll(/^\s*\|\s*\d+\s*\|/gm)].length;
    if (probeRows !== 14) {
      return [false, `discovery-probes.md defines ${probeRows} probes, expected 14`];
    }

    const dod = ctx.read(`${QUALITY}/definition-of-done.md`);
    if (dod === null) return [false, "missing definition-of-done.md"];
    const dodRows = [...dod.matchAll(/^\|\s*\d+\s*\|/gm)].length;
    if (dodRows !== 16) {
      return [false, `definition-of-done.md defines ${dodRows} points, expected 16`];
    }
    if (!dod.includes("n/a")) {
      return [false, "definition-of-done.md must state the n/a rule"];
    }
    if (!/point 14/i.test(dod)) {
      return [
        false,
        "definition-of-done.md must carry the point-14 rule for non-interactive runs, or a headless run burns review rounds on a condition the mode created",
      ];
    }
    return true;
  })

  .check("document-contracts SKILL.md carries the notation table", (ctx: Ctx): Result => {
    const text = ctx.read(`${PACK}/skills/eis-document-contracts/SKILL.md`);
    if (text === null) return [false, "missing eis-document-contracts/SKILL.md"];
    for (const ns of ["REQ-§", "EIS-§", "RES-§", "DL-"]) {
      if (!text.includes(ns)) {
        return [
          false,
          `notation table must define the '${ns}' namespace — a bare section number is ambiguous across four documents`,
        ];
      }
    }
    return true;
  })

  .check("every shared closed set agrees across every file that restates it", (ctx: Ctx): Result => {
    for (const e of SHARED_ENUMS) {
      for (const r of e.declaredIn) {
        const text = ctx.read(r);
        if (text === null) {
          return [false, `${e.field}: declaring file is missing: ${r}`];
        }
        if (declaringBlock(text, e) !== null) continue;

        // Report the most useful diagnosis: which values the file never names
        // in a delimiter-safe position at all, versus a set that is present but
        // scattered across separate blocks.
        const absent = e.values.filter((v) => !namesToken(text, v));
        const detail = absent.length
          ? `never names ${JSON.stringify(absent)} as a delimited token`
          : `names every value somewhere, but never all of them together with the anchor ${JSON.stringify(e.anchor)} in one blank-line-delimited block`;
        return [
          false,
          `${r} is a declaring site for ${e.field} but ${detail}. ` +
            `The full set is ${JSON.stringify(e.values)}. ${e.because}. ` +
            "A declaring block must name the field and every value together — a value that merely appears elsewhere in the file is prose, not a restatement, and substring matches (`adjacent` inside `adjacent-domain`) are how this check went vacuous the first time.",
        ];
      }
    }
    return true;
  })

  .check("no file restates a shared closed set without being declared", (ctx: Ctx): Result => {
    // The B2 lesson, generalised: an agreement check whose file list is the
    // list of files someone edited is blind to the site they missed. This
    // inverts the direction — it searches the whole pack for declaring blocks
    // and fails when it finds one the table does not know about.
    for (const e of SHARED_ENUMS) {
      for (const r of packMarkdown(ctx)) {
        if (e.declaredIn.includes(r)) continue;
        const text = ctx.read(r);
        if (text === null) continue;
        const block = declaringBlock(text, e);
        if (block === null) continue;
        return [
          false,
          `${r} carries a declaring block for ${e.field} but is not in its declaredIn list:\n` +
            `    ${JSON.stringify(block.replace(/\s+/g, " ").slice(0, 160))}\n` +
            "Add it to SHARED_ENUMS.declaredIn so it is held to agreement, or stop restating the set there. " +
            "An undeclared restatement is exactly the site a fix pass forgets.",
        ];
      }
    }
    return true;
  })

  .check("every pinned contract literal is spelled identically wherever it is restated or asserted", (ctx: Ctx): Result => {
    // See the PINNED_LITERALS commentary for why this exists and why widening
    // the eval needle would have been the wrong repair.
    for (const p of PINNED_LITERALS) {
      for (const r of [p.owner, ...p.restatedIn]) {
        const text = ctx.read(r);
        if (text === null) return [false, `${p.what}: site is missing: ${r}`];
        const lines = text.replace(/\r/g, "").split("\n");

        // Drift *within* a site: a file that carries the literal twice can
        // re-word one copy and still satisfy the containment test below. The
        // derived variant set closes that, and closes it in the direction the
        // defect actually travels.
        const hay = text.toLowerCase();
        for (const t of p.tokens) {
          for (const v of driftVariants(t)) {
            const at = hay.indexOf(v.toLowerCase());
            if (at < 0) continue;
            return [
              false,
              `${r} contains "${text.slice(at, at + v.length)}", a near-miss of the pinned literal "${t}".\n` +
                `    ${p.because}.\n` +
                "    Two spellings of one contracted string in one pack is how run 4 and run 5 rendered the same column differently. " +
                "Use the owner's spelling, or re-word the owner and every declared site in a single edit.",
            ];
          }
        }

        if (lines.some((ln) => p.tokens.every((t) => ln.includes(t)))) continue;

        const absent = p.tokens.filter((t) => !text.includes(t));
        const detail = absent.length
          ? `never contains ${JSON.stringify(absent)}`
          : `contains every token somewhere, but never all of them together on one line — a literal split across a hard wrap is one nobody can copy`;
        return [
          false,
          `${r} restates ${p.what} but ${detail}.\n` +
            `    The pinned spelling is ${JSON.stringify(p.tokens)}, owned by ${p.owner}.\n` +
            `    ${p.because}.\n` +
            "    Copy the literal from the owner character for character, or change it in the owner and here in the same edit. " +
            "A near-miss restatement is how run 4 and run 5 rendered the same contracted column two different ways.",
        ];
      }
      for (const spec of p.assertedIn) {
        if (ctx.read(spec) === null) return [false, `${p.what}: asserting spec is missing: ${spec}`];
        const pats = specPatterns(ctx, path.resolve(ctx.root, spec)).map((x) => x.pat);
        if (pats.some((pat) => p.tokens.every((t) => pat.includes(t)))) continue;
        return [
          false,
          `${spec}: no \`pattern:\` contains the pinned literal ${JSON.stringify(p.tokens)} for ${p.what}.\n` +
            `    ${p.because}.\n` +
            "    The assertion and the contract must search for and mandate the same string. " +
            "When they were allowed to differ, the assertion failed against output that satisfied the contract, and the obvious repair — loosening the needle — would have left the drift in place for the next round to rediscover.",
        ];
      }
    }
    return true;
  })

  .check("the ID namespacing table gives every prefix exactly one owner", (ctx: Ctx): Result => {
    const r = `${CONTRACTS}/ledger-format.md`;
    const text = ctx.read(r);
    if (text === null) return [false, `missing ${r}`];

    // Scope to the table itself. Scanning the whole file would let a prefix
    // that is merely *mentioned* in prose satisfy a check about ownership —
    // which is precisely the bug this guards against.
    //
    // The end anchor is `(?=^##\s|$(?![\s\S]))`, not `\Z`. JavaScript has no
    // `\Z`: in a JS RegExp it is an escaped literal `Z`, so the original
    // pattern terminated the capture at the next capital Z in the file and
    // worked only by the accident that there was none.
    const m = text.match(/^##\s+ID namespacing[^\n]*\n([\s\S]*?)(?=^##\s|$(?![\s\S]))/m);
    if (!m) {
      return [
        false,
        `${r}: no '## ID namespacing' section. Arch §8.1 specifies this file as 'STM ledger record schemas + ID namespacing table'; without the table a record type can be defined with no agent authorised to write it.`,
      ];
    }
    const rows = m[1]!
      .split(/\r?\n/)
      .filter((ln) => /^\s*\|/.test(ln) && !/^\s*\|\s*-+/.test(ln));
    if (rows.length < 12) {
      return [false, `${r}: ID namespacing table has ${rows.length} rows, expected at least 12 plus a header`];
    }
    const table = rows.join("\n");

    // Every prefix written during a run needs a row naming its owning agent.
    const prefixes = [
      "REQ-###",
      "CON-###",
      "PROP-###",
      "VIS-###",
      "EV-RS-###",
      "EV-GAP-###",
      "PAT-###",
      "DEC-RS-###",
      "DEC-MD-###",
      "DRV-###",
      "UX-###",
      "RQ-###",
    ];
    const missing = prefixes.filter((p) => !table.includes(p));
    if (missing.length) {
      return [
        false,
        `${r}: the ID namespacing table has no row for ${JSON.stringify(missing)}. ` +
          "A prefix with no owning agent is a record type nothing can legally write — VIS-### was exactly that defect: defined in a schema, instructed in a file whose three readers are all forbidden to write the ledger it lives in.",
      ];
    }

    // A row that names no agent is not an ownership record.
    const OWNERS = ["analyst", "researcher", "author", "critic", "orchestrator"];
    for (const ln of rows) {
      if (!prefixes.some((p) => ln.includes(p))) continue;
      if (!OWNERS.some((o) => ln.toLowerCase().includes(o))) {
        return [
          false,
          `${r}: table row names a prefix but no owning agent: ${JSON.stringify(ln.trim())}`,
        ];
      }
    }
    return true;
  })

  .check("no retired enum or heading spelling survives anywhere in the pack", (ctx: Ctx): Result => {
    // Eval specs are scanned alongside pack markdown: a retired heading in a
    // judge criterion drifts the contract just as effectively as one in a skill,
    // and that is the direction the live incident actually came from.
    const scanned = [...packMarkdown(ctx), ...ctx.glob(`${EVALS}/*.eval.md`).map((f) => rel(ctx, f))];
    for (const r of scanned) {
      const text = ctx.read(r);
      if (text === null) continue;
      // Round 9 (C1): compare case-insensitively. The comparison was
      // `text.includes(literal)` against literals stored in whatever case they
      // were retired in, and the §20 column spelling is stored all-lowercase
      // because that is how the orchestrator's prose read. But the form it
      // would come BACK in is a table header — `What changes if this is
      // false` — which the case-sensitive scan could not see. Nor could
      // driftVariants(), which walks `owner + restatedIn` only, and the
      // orchestrator is neither: it was the file the literal was retired FROM.
      // The one file that most needed the guard was the one file with no guard
      // at all.
      //
      // The same exposure applies in principle to every literal here whose
      // natural re-introduction differs in case from its retired form, so the
      // fix is applied to the comparison rather than to one entry. Store
      // literals in whichever case reads most naturally; case no longer
      // carries meaning for this check.
      const hay = text.toLowerCase();
      for (const { literal, why } of RETIRED_LITERALS) {
        const at = hay.indexOf(literal.toLowerCase());
        if (at >= 0) {
          return [
            false,
            `${r} still uses the retired literal ${JSON.stringify(text.slice(at, at + literal.length))} — ${why}. ` +
              "The agreement check above only asserts that canonical values are present; it cannot see a stale spelling sitting beside them.",
          ];
        }
      }
    }
    return true;
  })

  .check("the skipped-mode research contract is stated once and agreed everywhere", (ctx: Ctx): Result => {
    const skeleton = ctx.read(`${CONTRACTS}/research-doc-skeleton.md`);
    if (skeleton === null) return [false, "missing research-doc-skeleton.md"];

    // The body literal every unresearched heading must carry. The researcher
    // reads it here, the critic's C-7 audits for it; if the two files disagree
    // every skipped run self-inflicts a BLOCKING.
    if (!skeleton.includes("Not performed — research_mode:")) {
      return [
        false,
        "research-doc-skeleton.md must carry the verbatim skipped-form body 'Not performed — research_mode: <mode> (<reason>).' — it is the single source of truth for the form, and the critic's C-7 audits against it",
      ];
    }
    if (!/EV-GAP-###/.test(skeleton)) {
      return [
        false,
        "research-doc-skeleton.md must require trailing EV-GAP-### ids on unresearched headings — C-7 BLOCKS without them, so a stub form that omits them fails every skipped run",
      ];
    }
    // C-10's non-vacuity floor, C-5's emptiness detection and the skeleton
    // must agree on what counts as a row, or a correct skipped run draws a
    // spurious finding. Presence of the phrase is not enough: the carve-out
    // only exists if the header row is named as the thing excluded, the
    // exclusion is tied to `skipped` mode, and the file defers to the one
    // owner of the rule — all inside a single block, so a carve-out stated in
    // one paragraph cannot be contradicted by a bare "empty" bullet elsewhere.
    for (const { file: r, label } of CARVEOUT_SITES) {
      const text = ctx.read(r);
      if (text === null) return [false, `missing ${r}`];
      for (const [needle, why] of [
        ["data row", "the floor must count data rows, not rows"],
        ["header row", "the carve-out only means something if the header row is named as the thing excluded"],
      ] as const) {
        if (!new RegExp(needle, "i").test(text)) {
          return [
            false,
            `${r}: ${label} never says ${JSON.stringify(needle)} — ${why}. ` +
              "A skipped run still renders the RES-§9 header row; if the non-vacuity floor counts that as a row it fires on every correct skipped run, which is five of the six behavioural specs.",
          ];
        }
      }

      // Every block that pronounces on header rows must carry the carve-out.
      // This is what catches the site a fix pass missed: eis-quality-bar's
      // "a table with header rows and no data rows" bullet satisfied both
      // needles above while still calling the contracted form empty.
      const headerBlocks = blocksOf(text).filter((b) => /header rows?/i.test(b));
      const carved = headerBlocks.filter(
        (b) =>
          /skipped/i.test(b) &&
          (r === CARVEOUT_OWNER || b.includes("research-doc-skeleton.md")),
      );
      if (!carved.length) {
        return [
          false,
          `${r}: ${label} talks about header rows in ${headerBlocks.length} block(s), none of which states the skipped-mode carve-out` +
            (r === CARVEOUT_OWNER
              ? "."
              : " and defers to research-doc-skeleton.md, which owns the rule.") +
            " A file that calls a header-only table empty without the carve-out contradicts the document contract, and a header-only RES-§9 on an honest skipped run draws a spurious failure.",
        ];
      }
      const uncarved = headerBlocks.filter((b) => !carved.includes(b) && /empt|vacu|not a scored|fail/i.test(b));
      if (uncarved.length) {
        return [
          false,
          `${r}: ${label} has a block that calls a header row empty or vacuous without the carve-out:\n` +
            `    ${JSON.stringify(uncarved[0]!.replace(/\s+/g, " ").slice(0, 160))}\n` +
            "State the carve-out in that block too, or the reader who stops there gets the pre-carve-out rule.",
        ];
      }

      // The superseded phrasing, in the shape that actually caused the bug.
      const stale = text.match(/(?:≥|>=|at least)\s*(?:1|one)\s+matrix row/i);
      if (stale) {
        return [
          false,
          `${r}: ${label} still uses the superseded floor phrasing ${JSON.stringify(stale[0])}. ` +
            "It must count data rows — counting any row makes an honest header-only skipped run vacuous.",
        ];
      }
    }
    return true;
  })

  // ---- group 4: eval-suite self-checks ----------------------------------

  .check("six behavioural specs plus this one", (ctx: Ctx): Result => {
    const md = ctx.glob(`${EVALS}/*.eval.md`);
    if (md.length !== 6) {
      return [false, `expected 6 behavioural *.eval.md specs, found ${md.length}`];
    }
    const ts = ctx.glob(`${EVALS}/*.eval.ts`);
    if (ts.length !== 1) {
      return [false, `expected exactly 1 structural *.eval.ts spec, found ${ts.length}`];
    }
    if (ctx.read(`${EVALS}/README.md`) === null) {
      return [false, "missing evals/packs/ux-interaction-spec/README.md"];
    }
    return true;
  })

  .check("every behavioural spec sets target: ux-interaction-spec", (ctx: Ctx): Result => {
    for (const file of ctx.glob(`${EVALS}/*.eval.md`)) {
      const r = rel(ctx, file);
      const { fmLines } = splitFrontmatter(ctx.read(r)!);
      const target = (fmValue(fmLines, "target") ?? "").replace(/^"|"$/g, "");
      if (target !== ORCHESTRATOR) {
        return [
          false,
          `${r}: target is ${JSON.stringify(target)}. Without target: ux-interaction-spec the executor falls back to the DEFAULT Copilot agent while validateSpec still passes, so the spec silently tests the wrong thing`,
        ];
      }
      const kind = (fmValue(fmLines, "kind") ?? "").replace(/^"|"$/g, "");
      if (kind !== "agent") return [false, `${r}: kind must be 'agent', got ${JSON.stringify(kind)}`];
      const timeout = Number(fmValue(fmLines, "timeout") ?? 0);
      if (timeout !== 3600) {
        return [
          false,
          `${r}: timeout must be 3600 — (6 phases + 4 x 1 review round) x 360s. Got ${timeout}`,
        ];
      }
    }
    return true;
  })

  .check("every behavioural spec has a real ## Setup heading with stage + files", (ctx: Ctx): Result => {
    for (const file of ctx.glob(`${EVALS}/*.eval.md`)) {
      const r = rel(ctx, file);
      const text = ctx.read(r)!;
      if (!hasRealHeading(text, "## Setup")) {
        return [
          false,
          `${r}: needs a REAL '## Setup' Markdown heading. A '# ## Setup' comment inside a fence satisfies a naive substring check but stages nothing`,
        ];
      }
      if (!hasRealHeading(text, "## Act") || !hasRealHeading(text, "## Assert")) {
        return [false, `${r}: needs real '## Act' and '## Assert' headings`];
      }
      const setupStart = text.indexOf("## Setup");
      const setupBody = text.slice(setupStart, text.indexOf("## Act", setupStart));
      if (!/^\s*stage:/m.test(setupBody)) {
        return [false, `${r}: '## Setup' must declare an explicit stage:`];
      }
      if (!/^\s*files:/m.test(setupBody)) {
        return [
          false,
          `${r}: '## Setup' must declare files: — target: auto-stages the agent and its skills but stages NO fixture files`,
        ];
      }
      if (!/copy:\s*"fixtures\//.test(setupBody)) {
        return [false, `${r}: fixtures must be copied from the spec-relative fixtures/ directory`];
      }
    }
    return true;
  })

  .check("prompts use workspace-relative Inputs and non-interactive mode", (ctx: Ctx): Result => {
    for (const file of ctx.glob(`${EVALS}/*.eval.md`)) {
      const r = rel(ctx, file);
      const text = ctx.read(r)!;
      const actStart = text.indexOf("## Act");
      const act = text.slice(actStart, text.indexOf("## Assert", actStart));
      const inputs = /^Inputs:\s*(.+)$/m.exec(act);
      if (!inputs) return [false, `${r}: '## Act' prompt has no Inputs: line`];
      for (const p of inputs[1]!.split(",").map((s) => s.trim())) {
        if (p.startsWith("evals/") || p.startsWith("agent-packs/") || p.startsWith("/")) {
          return [
            false,
            `${r}: Inputs path ${JSON.stringify(p)} is repo-relative and will not resolve inside the temp workspace`,
          ];
        }
      }
      if (!/^Interaction mode:\s*non-interactive$/m.test(act)) {
        return [false, `${r}: behavioural specs must pin Interaction mode: non-interactive`];
      }
      if (!/^Max review rounds:\s*[12]$/m.test(act)) {
        return [false, `${r}: must clamp Max review rounds downward (1 or 2)`];
      }
      if (!/^Max specialist retries:\s*[01]$/m.test(act)) {
        return [false, `${r}: must clamp Max specialist retries downward (0 or 1)`];
      }
    }
    return true;
  })

  .check("every contains/not_contains assertion is path-scoped", (ctx: Ctx): Result => {
    for (const file of ctx.glob(`${EVALS}/*.eval.md`)) {
      const r = rel(ctx, file);
      const lines = ctx.read(r)!.split(/\r?\n/);
      let inList = false;
      for (let i = 0; i < lines.length; i++) {
        const ln = lines[i]!;
        if (/^(contains|not_contains|section_contains|section_not_contains|matches):\s*$/.test(ln)) {
          inList = true;
          continue;
        }
        if (inList) {
          if (/^\s*-\s/.test(ln)) {
            if (lines[i - 1]?.includes("# unscoped:")) continue;
            if (!/\bpath:\s*"/.test(ln)) {
              return [
                false,
                `${r}:${i + 1}: assertion entry must carry a path: — an unscoped text assertion passes on any file in the workspace, including the fixture it was copied from`,
              ];
            }
          } else if (ln.trim() && !/^\s/.test(ln)) {
            inList = false;
          }
        }
      }
    }
    return true;
  })

  .check("no assertion is scoped by a max_chars window", (ctx: Ctx): Result => {
    // The class this closes was found five separate times by hand across four
    // specs before it was worth a check. See TEMPERED_SCAN above for why every
    // window is wrong in one of two directions, and why there is no carve-out:
    // of the nine section-scoped assertions this pack shipped, four truncated,
    // four spilled past the section, and one fitted by luck. `max_chars` is not
    // "usually fine, occasionally too small" — it is never correct by design.
    //
    // Omitting `max_chars` is NOT the fix: the engine defaults it to 800, which
    // is a smaller bare window, so the construct itself is banned rather than
    // any particular value of it.
    for (const file of ctx.glob(`${EVALS}/*.eval.md`)) {
      const r = rel(ctx, file);
      const lines = ctx.read(r)!.split(/\r?\n/);
      for (let i = 0; i < lines.length; i++) {
        const ln = lines[i]!;
        if (/^\s*#/.test(ln)) continue; // prose about the rule, not a use of it
        const what =
          /^\s*section_not_contains:\s*$/.test(ln) ? "section_not_contains" :
          /^\s*section_contains:\s*$/.test(ln) ? "section_contains" :
          /\bmax_chars\s*:/.test(ln) ? "max_chars" :
          /\bsection:\s*"/.test(ln) ? "section:" : null;
        if (!what) continue;
        return [
          false,
          `${r}:${i + 1}: uses \`${what}\`. Section scoping by character window is banned in this pack.\n` +
            "    The engine's sectionBody is /#+\\s+<name>\\s*\\n([\\s\\S]{0,max_chars})/i with no\n" +
            "    next-heading bound, so max_chars reads PAST the section into whatever follows.\n" +
            "    Too small truncates the section (a real needle reports as absent); too large\n" +
            "    passes on the next section's text (the check goes vacuous). Omitting it is\n" +
            "    worse still — the default is 800.\n" +
            "    Use a heading-bounded matches: assertion instead —\n" +
            '      - { name: "...", path: "...", pattern: "##\\\\s+8\\\\.\\\\s+State Models' +
            '(?:(?!\\\\n##\\\\s)[\\\\s\\\\S])*?NEEDLE", flags: "i" }\n' +
            "    and for an `all:` set, one tempered lookahead per needle anchored after the\n" +
            "    heading: `...State Models\\\\s*\\\\n(?=TEMPER*?A)(?=TEMPER*?B)`.",
        ];
      }
    }
    return true;
  })

  .check("every heading-anchored pattern is bounded by the next heading", (ctx: Ctx): Result => {
    // The check above bans the window; this one stops the ban being satisfied
    // cosmetically. `##\s+8\.\s+State Models[\s\S]*?needle` is a `matches:`
    // assertion, passes the ban, and is exactly as vacuous as max_chars: 16000 —
    // `[\s\S]*?` walks straight through every following heading, so the needle
    // can be satisfied by section 9, 15 or 22. Without this, the landmine moves
    // rather than being removed.
    for (const file of ctx.glob(`${EVALS}/*.eval.md`)) {
      const r = rel(ctx, file);
      for (const { line, pat } of specPatterns(ctx, file)) {
        for (const { heading, after } of headingAnchorsIn(pat)) {
          const rest = pat.slice(after);
          if (rest.startsWith(TEMPERED_SCAN)) continue;
          // `\s*\n` then a lookahead conjunction is the `all:` form; each
          // lookahead must itself carry the temper.
          const conj = /^\\s\*\\n(\(\?=.*\))$/.exec(rest);
          if (conj) {
            const heads = [...conj[1]!.matchAll(/\(\?=/g)];
            const tempers = [...conj[1]!.matchAll(/\(\?:\(\?!\\n##\\s\)\[\\s\\S\]\)\*/g)];
            if (heads.length > 0 && heads.length === tempers.length) continue;
          }
          return [
            false,
            `${r}:${line}: pattern anchors on ${JSON.stringify(heading)} but the scan that follows is not bounded by the next heading.\n` +
              `    found after the anchor: ${JSON.stringify(rest.slice(0, 40))}\n` +
              `    expected it to start with the tempered token ${JSON.stringify(TEMPERED_SCAN)}\n` +
              "    A bare [\\s\\S]* / .* / [^]* walks through every following H2, so the needle\n" +
              "    can be satisfied by a different section — the same vacuity as a too-large\n" +
              "    max_chars window, just spelled as a regex. (\\s does not match #, so the\n" +
              "    temper stops at H2 and leaves H3 subsections inside the scan.)\n" +
              "    If you only want to assert the heading exists, use contains: instead.",
          ];
        }
      }
    }
    return true;
  })

  .check("every regex literal in every spec compiles under JavaScript RegExp", (ctx: Ctx): Result => {
    // Run 4 lost a check to `pattern: "(?i)(adopt|adapt|...)"`. Python accepts
    // inline flags; JavaScript RegExp throws "Invalid group" at COMPILE time,
    // so the assertion failed unconditionally regardless of pack output — a
    // check that can never pass and never reports why. Compiling every pattern
    // offline turns a 70-minute discovery into a one-second one.
    for (const file of ctx.glob(`${EVALS}/*.eval.md`)) {
      const r = rel(ctx, file);
      const lines = ctx.read(r)!.split(/\r?\n/);
      for (let i = 0; i < lines.length; i++) {
        for (const m of lines[i]!.matchAll(/pattern:\s*"((?:[^"\\]|\\.)*)"/g)) {
          let pat: string;
          try {
            pat = JSON.parse(`"${m[1]}"`);
          } catch {
            return [false, `${r}:${i + 1}: pattern is not a decodable string literal`];
          }
          try {
            new RegExp(pat);
          } catch (e) {
            return [
              false,
              `${r}:${i + 1}: pattern does not compile under JavaScript RegExp: /${pat}/ — ${(e as Error).message}. Case-insensitivity goes in flags: "i", not an inline (?i) group.`,
            ];
          }
        }
      }
    }
    return true;
  })

  .check("no spec uses a non-JavaScript regex construct", (ctx: Ctx): Result => {
    // The dangerous half of this class COMPILES but means something else.
    // In JavaScript `\A` and `\Z` are just the literals "A" and "Z" — a
    // Python-style anchored pattern silently becomes a substring match and the
    // assertion goes quietly vacuous. The compile check above cannot see it.
    const BANNED: { re: RegExp; why: string }[] = [
      { re: /\(\?[imsxa]+\)/, why: "inline flag group — JavaScript has no inline flags; use flags: \"i\"" },
      { re: /\\A/, why: "\\A is not a JavaScript anchor — it matches a literal 'A'; use ^ with no m flag" },
      { re: /\\Z/, why: "\\Z is not a JavaScript anchor — it matches a literal 'Z'; use $ with no m flag" },
      { re: /\(\?P[<=]/, why: "Python named-group syntax; JavaScript uses (?<name>...)" },
      { re: /\(\?#/, why: "regex comment group is not supported in JavaScript" },
      { re: /\[:[a-z]+:\]/, why: "POSIX character class is not supported in JavaScript" },
    ];
    for (const file of ctx.glob(`${EVALS}/*.eval.md`)) {
      const r = rel(ctx, file);
      const lines = ctx.read(r)!.split(/\r?\n/);
      for (let i = 0; i < lines.length; i++) {
        for (const m of lines[i]!.matchAll(/pattern:\s*"((?:[^"\\]|\\.)*)"/g)) {
          let pat: string;
          try {
            pat = JSON.parse(`"${m[1]}"`);
          } catch {
            continue;
          }
          for (const b of BANNED) {
            if (b.re.test(pat)) {
              return [false, `${r}:${i + 1}: /${pat}/ uses ${b.why}`];
            }
          }
        }
      }
    }
    return true;
  })

  .check("no negative needle is a bare substring of the document's own vocabulary", (ctx: Ctx): Result => {
    // Run 4 shipped `not_contains: "Inter"` — aimed at the typeface — against a
    // document class titled "Experience Interaction Specification". It
    // substring-matched "Interaction" in the title line and in the heading
    // "13. Interaction Scenarios", so the spec was UNSATISFIABLE at any pack
    // quality. Same delimiter-boundary bug as SHARED_ENUMS' "adjacent" inside
    // "adjacent-domain". The contract headings are the authoritative vocabulary
    // the document is guaranteed to contain, so they are the right oracle.
    const vocab = new Set<string>();
    for (const h of [...EIS_HEADINGS, ...RES_HEADINGS]) {
      for (const w of h.replace(/^##\s*\d+\.\s*/, "").split(/[^A-Za-z]+/)) {
        if (w.length > 2) vocab.add(w);
      }
    }
    for (const w of ["Experience", "Interaction", "Specification"]) vocab.add(w);

    for (const file of ctx.glob(`${EVALS}/*.eval.md`)) {
      const r = rel(ctx, file);
      const lines = ctx.read(r)!.split(/\r?\n/);
      let negated = false;
      for (let i = 0; i < lines.length; i++) {
        const ln = lines[i]!;
        if (/^(not_contains|section_not_contains):\s*$/.test(ln)) { negated = true; continue; }
        if (/^[a-z_]+:\s*$/.test(ln)) { negated = false; continue; }
        if (!negated || !/^\s*-\s/.test(ln)) continue;
        const needles: string[] = [];
        const t = /\btext:\s*"((?:[^"\\]|\\.)*)"/.exec(ln);
        if (t) needles.push(JSON.parse(`"${t[1]}"`));
        const anyBlock = /\bany:\s*\[([^\]]*)\]/.exec(ln);
        if (anyBlock) {
          for (const m of anyBlock[1]!.matchAll(/"((?:[^"\\]|\\.)*)"/g)) {
            needles.push(JSON.parse(`"${m[1]}"`));
          }
        }
        for (const n of needles) {
          if (!/^[A-Za-z]+$/.test(n)) continue;
          for (const w of vocab) {
            if (w.length > n.length && w.toLowerCase().startsWith(n.toLowerCase())) {
              return [
                false,
                `${r}:${i + 1}: negative needle "${n}" is a bare substring of "${w}", which the document contract guarantees will be present — this assertion can never pass. Match it as a delimited token via a matches: pattern with \\b instead.`,
              ];
            }
          }
        }
      }
    }
    return true;
  })

  .check("the heading-vs-shorthand notation rule is stated wherever headings are authored", (ctx: Ctx): Result => {
    // Run 4's structural defect: one author in six emitted `## EIS-§7 ...`
    // instead of `## 7. ...`. The cause was notation leakage — the contract
    // called the headings "`EIS-§n` headings" and the pass guide introduced
    // each section as `EIS-§2 Scope`, a sigil and a title printed as one token,
    // which reads exactly like a heading you can paste. At roughly 1-in-6 a
    // re-run can pass on luck, so the rule itself is what must be pinned.
    const SITES: { file: string; label: string }[] = [
      { file: `${CONTRACTS}/eis-skeleton.md`, label: "eis-skeleton.md (the verbatim contract)" },
      { file: `${PACK}/agents/eis-author.agent.md`, label: "eis-author.agent.md (the agent that writes headings)" },
      { file: `${PACK}/agents/eis-author.passes.md`, label: "eis-author.passes.md (the per-pass guide)" },
    ];
    for (const s of SITES) {
      const text = ctx.read(s.file);
      if (text === null) return [false, `missing ${s.file}`];
      if (!/never\s+appear\s+on\s+a\s+`##`\s+line/i.test(text)) {
        return [
          false,
          `${s.label}: must state that the reference sigil \`EIS-§\` never appears on a \`##\` line. Without it the sigil and the heading literal stay confusable, which is how run 4 produced "## EIS-§7 Permissions and Capabilities".`,
        ];
      }
      // The ASCII phrase above survives mojibake corruption untouched, so it
      // cannot witness that the sigil itself is intact. Round 6 shipped
      // `eis-skeleton.md` with every U+00A7 double-encoded to <U+00C2,U+00A7>,
      // which turned the pass-A self-check into a search for a string the
      // author can never emit — it reported clean exactly when the defect was
      // present. Assert the LITERAL, not the sentence describing it.
      if (!text.includes("EIS-\u00A7")) {
        return [
          false,
          `${s.label}: does not contain the literal "EIS-\u00A7" (U+00A7 SECTION SIGN). The prose rule about the sigil is present but the sigil itself is missing or corrupted, so anything this file tells the author to search for cannot match what the author actually writes.`,
        ];
      }
      if (!text.includes("## 8. State Models")) {
        return [
          false,
          `${s.label}: must show the canonical heading literal (e.g. "## 8. State Models") so the author copies a literal instead of reconstructing one from the shorthand.`,
        ];
      }
    }
    // No site may introduce a section as a bare `EIS-§n Title` juxtaposition —
    // that form reads as a pasteable heading and is what leaked in run 4.
    //
    // Round 7 widened this in two independent directions, because each of the
    // previous two fixes closed one instance and left the class open:
    //
    //   SCOPE — the site list was hand-maintained. It is now `notationScanSites`,
    //   every `*.md` in the pack. See that function for why.
    //
    //   SHAPE — the regex required a LEADING backtick, so it matched
    //   `` `EIS-§2 Scope` `` but was blind to **RES-§10 Sources**. Bold, plain
    //   and backticked juxtapositions are the same hazard; the requirement is
    //   gone. The pack's safe idiom `` `RES-§2` Title `` survives the widening
    //   because a backtick sits between the digit and the space, so
    //   `\d+ [A-Z]` cannot match across it.
    //
    // Both namespaces are scanned. The research document's canonical headings
    // are `## 10. Sources`, not `## RES-§10 Sources`, so RES carries exactly
    // the same hazard as EIS.
    for (const file of notationScanSites(ctx)) {
      const text = ctx.read(file);
      if (text === null) continue;
      const leak = /(EIS|RES)-§\d+ [A-Z]/.exec(text.replace(SANCTIONED_COUNTEREXAMPLE, ""));
      if (leak) {
        return [
          false,
          `${file}: "${leak[0]}…" prints the sigil and the section title as one token, which reads as a pasteable heading. Write the heading literal first, then the id: \`## 2. Scope\` (\`${leak[1]}-§2\`).`,
        ];
      }
    }
    // The researcher document uses the parallel `RES-` + U+00A7 namespace and
    // was corrupted in the same round, which would have told it to emit ten
    // `RES-` + <U+00C2,U+00A7> headings.
    const researcher = ctx.read(`${PACK}/agents/ux-pattern-researcher.agent.md`);
    if (researcher !== null && !researcher.includes("RES-\u00A7")) {
      return [
        false,
        `ux-pattern-researcher.agent.md: does not contain the literal "RES-\u00A7" (U+00A7 SECTION SIGN). The research-document namespace sigil is missing or corrupted.`,
      ];
    }
    return true;
  })

  .check("no file puts the reference sigil in real heading position", (ctx: Ctx): Result => {
    // The juxtaposition scan above exempts the sanctioned teaching form — a
    // `##`-prefixed sigil inside a code span, shown as forbidden. This check
    // bounds that exemption from the other side, on RAW text: nothing may put
    // the sigil in an ACTUAL heading, fenced or not.
    //
    // That distinction matters because a real wrong-form heading is the run-4
    // defect itself rather than a description of it, and round 7 found one
    // shipped: `## RES-§9 — Implications for the EIS` in
    // `synthesis-and-precedent.md` — the wrong form carrying the right title,
    // sitting in a reference the researcher reads *while writing headings*.
    // The old backtick-anchored scan could not see it (no leading backtick),
    // and the site list did not include the file. It is the strongest instance
    // found to date and it survived two rounds of "fixing" this class.
    //
    // Fences are scanned deliberately: the verbatim skeleton block is the
    // highest-value place for a wrong heading to hide, and it is fenced.
    for (const file of notationScanSites(ctx)) {
      const text = ctx.read(file);
      if (text === null) continue;
      const m = /^[ \t]*#{1,6}[ \t]+(EIS|RES)-§/m.exec(text);
      if (m) {
        return [
          false,
          `${file}: "${m[0].trim()}…" puts the reference sigil in real heading position. Headings are canonical (\`## 9. Implications for the EIS\`); the sigil belongs in the body or a trailing parenthetical — \`## Implications for the EIS\` (\`${m[1]}-§9\`).`,
        ];
      }
    }
    return true;
  })

  .check("no file names the canonical headings by their reference sigil", (ctx: Ctx): Result => {
    // The C2 defect, and the one the other two detectors cannot see.
    //
    // Round 7 was asked to add the orchestrator to the juxtaposition scan so
    // its "all 22 EIS-§n headings" phrasing would be "mechanically covered
    // from now on". Adding it would have been theatre: that scan matches
    // sigil + DIGITS + space + CAPITAL, and every phrasing in this class —
    // `EIS-§n headings`, `` `RES-§n` headings ``, `RES-§1..§10 headings` —
    // fails at least one of those requirements. The site would have been in
    // scope of a regex structurally unable to see the defect that put it there.
    //
    // Why the phrasing is a defect and not a style quibble: the pack's own
    // diagnosis of run 4 names it as half the root cause. Calling the headings
    // "EIS-§n headings" tells the author the sigil IS the heading vocabulary,
    // and one author in six then wrote `## EIS-§7 …`. The sigil is a reference
    // id for cross-referencing; the heading is `## 7. <Title>`. Prose may
    // reference a section by sigil freely — `see EIS-§20` is correct and
    // stays legal — but it may not call the headings themselves by it.
    //
    // Round 7 found six live instances, five of them in the researcher and
    // critic. The EIS side had been cleaned up after run 4; the RES side,
    // which no one had looked at, was saturated.
    // Round 8 tightened the whitespace and the sigil tail. `\s+` spans blank
    // lines, and `[^\s`]*` swallows a sentence-ending period, so a paragraph
    // closing "…see EIS-§22." followed by a new paragraph opening "Headings
    // are copied verbatim…" matched — two unrelated sentences, one spurious
    // failure, on a check whose whole value is that a failure means something.
    // `(?:[ \t]|\n(?!\n))+` still crosses a single hard wrap, which is the case
    // that motivated `\s+` (the researcher's "the ten `RES-§n`\nheadings"), but
    // stops at a paragraph break. Requiring the tail to end in a non-`.`
    // character closes the same-paragraph variant of the same false positive
    // while leaving every real form — `EIS-§n`, `` `RES-§n` ``, `RES-§1..§10`
    // — matched, since each ends in a letter or a digit.
    const SIGIL_HEADINGS =
      /(EIS|RES)-§[^\s`]*[^\s`.]`?(?:[ \t]|\n(?!\n))+(?:level-\d+(?:[ \t]|\n(?!\n))+)?headings/i;
    for (const file of notationScanSites(ctx)) {
      const text = ctx.read(file);
      if (text === null) continue;
      const m = SIGIL_HEADINGS.exec(text.replace(SANCTIONED_COUNTEREXAMPLE, ""));
      if (m) {
        return [
          false,
          `${file}: "${m[0]}" names the canonical headings by their reference sigil. The headings are \`## <n>. <Title>\`; \`${m[1]}-§n\` is a cross-reference id, not a heading. Say "all ten canonical \`## <n>. <Title>\` headings". Referring to a section as \`${m[1]}-§20\` remains correct.`,
        ];
      }
    }
    return true;
  })

  .check("no pack or eval file contains double-encoded (mojibake) text", (ctx: Ctx): Result => {
    // See the findMojibake() commentary above for why this is a round-trip
    // test rather than a blacklist of the four known-bad glyph pairs.
    //
    // Scope is every file a human or an agent reads: a corrupted skill
    // reference silently retargets an agent's self-check, and a corrupted
    // eval spec silently retargets an assertion.
    const files = [
      ...ctx.glob(`${PACK}/agents/*.md`),
      ...ctx.glob(`${PACK}/skills/**/*.md`),
      ...ctx.glob(`${PACK}/README.md`),
      ...ctx.glob(`${EVALS}/*.eval.md`),
      ...ctx.glob(`${EVALS}/*.eval.ts`),
      ...ctx.glob(`${EVALS}/README.md`),
      ...ctx.glob(`${EVALS}/fixtures/**/*.md`),
    ];
    for (const file of files) {
      const r = rel(ctx, file);
      const text = ctx.read(r);
      if (text === null) continue;
      const hits = findMojibake(text);
      if (hits.length > 0) {
        const h = hits[0]!;
        return [
          false,
          `${r}:${h.line}: contains ${JSON.stringify(h.mojibake)}, which is ${JSON.stringify(h.repaired)} double-encoded (UTF-8 bytes decoded as CP1252, then re-encoded as UTF-8). ` +
            `${hits.length} corrupted run(s) in this file. ` +
            `This is never cosmetic: it silently rewrites every literal an agent is told to search for or emit — a self-check that hunts "EIS-\u00C2\u00A7" reports clean exactly when the defect it guards is present. ` +
            `Re-save the file as UTF-8, taking the correct glyphs from an uncorrupted sibling, and verify by reading the bytes back rather than by trusting the write.`,
        ];
      }
    }
    return true;
  })

  .check("no pack file carries a fixture-specific identifier", (ctx: Ctx): Result => {
    // The mirror of "no behavioural spec leaks the expected answer into its
    // prompt". A worked example in a skill or agent file that quotes the eval
    // fixture's own identifiers teaches to the test: the agent can satisfy an
    // assertion by copying the example rather than by doing the work, and the
    // check goes quietly vacuous. Illustrative examples must use a neutral
    // domain.
    //
    // This guard is the only thing standing between a worked example and a
    // silently-vacuous assertion, so it registers every identifier SHAPE the
    // fixtures actually contain, not just the shapes that have leaked so far.
    // Each shape below was derived by extracting it from the fixtures and
    // diffing against the pack; the counts are asserted so that a fixture
    // rewrite which drops a shape fails loudly instead of weakening the guard.
    const tokens = new Map<string, string>();
    const counts: Record<string, number> = {
      filename: 0, host: 0, memo: 0, route: 0, snake: 0, dotted: 0,
    };
    const add = (tok: string, shape: string): void => {
      if (!tok || tokens.has(tok)) return;
      tokens.set(tok, shape);
      counts[shape] = (counts[shape] ?? 0) + 1;
    };

    for (const file of ctx.glob(`${EVALS}/fixtures/**/*.md`)) {
      const r = rel(ctx, file);
      const text = ctx.read(r);
      if (text === null) continue;

      // filenames — a spec stages `fixtures/x.md` to `inputs/x.md`, so a worked
      // example citing `inputs/x.md` hands the agent the eval's own provenance
      // string. Registered WITH the extension: the bare stem `rough-concept`
      // collides with the pack's own input-shape enum, which is legitimate pack
      // vocabulary and predates the fixture.
      add(r.split("/").pop()!, "filename");

      // hosts and full URLs (reserved TLDs only, so real prose is untouched)
      for (const m of text.matchAll(
        /\b(?:[a-z0-9-]+\.)+(?:example|internal|invalid|test|localhost)\b[^\s`"',)]*/g,
      )) {
        add(m[0], "host");
        // Register the bare host too. Matching only the full URL lets a pack
        // file paste just "ds.acme.internal" and slip through — mutation FL-M3.
        const host = m[0].split("/")[0]!;
        if (host.length >= 8) add(host, "host");
      }

      // memo / document ids: PLAT-2026-114
      for (const m of text.matchAll(/\b[A-Z]{2,}-\d{4}-\d{2,}\b/g)) add(m[0], "memo");

      // API route paths: /v1/grants, /v1/grants/{grant_id}
      for (const m of text.matchAll(/(?<![\w./-])\/v\d+\/[a-z][a-z0-9/_{}-]*/g)) {
        add(m[0], "route");
      }

      // snake_case field and reason codes: unknown_principal, already_granted
      for (const m of text.matchAll(/\b[a-z]{3,}(?:_[a-z]{2,})+\b/g)) add(m[0], "snake");

      // dotted config and event keys: access.request.pending_max
      for (const m of text.matchAll(/\b[a-z][a-z0-9]*(?:\.[a-z][a-z0-9_]*)+\b/g)) {
        if (m[0].length >= 12) add(m[0], "dotted");
      }
    }

    const empty = Object.entries(counts).filter(([, n]) => n === 0).map(([s]) => s);
    if (empty.length) {
      return [
        false,
        `fixture identifier shapes discovered nothing for: ${JSON.stringify(empty)}. ` +
          "Either the fixtures changed shape or a discovery regex rotted — in both cases this " +
          "guard is now weaker than it reads. Re-derive the shape against the fixtures rather " +
          "than deleting it.",
      ];
    }

    const packFiles = [
      ...ctx.glob(`${PACK}/agents/*.md`),
      ...ctx.glob(`${PACK}/skills/**/*.md`),
      ...ctx.glob(`${PACK}/README.md`),
    ];
    for (const file of packFiles) {
      const r = rel(ctx, file);
      const text = ctx.read(r);
      if (text === null) continue;
      for (const [tok, shape] of tokens) {
        if (text.includes(tok)) {
          return [
            false,
            `${r}: contains ${JSON.stringify(tok)} (shape: ${shape}), an identifier that appears in an eval fixture. A worked example must not quote fixture content — an agent can then satisfy the assertion by copying the example instead of doing the work. Use a neutral illustrative value.`,
          ];
        }
      }
    }
    return true;
  })

  .check("no behavioural spec asserts a heading the document contract does not define", (ctx: Ctx): Result => {
    // A spec that asserts `## 3. Host Product Findings` against a document
    // whose contract says `## 3. Competitive Products` fails by construction —
    // and the tempting repair is from the eval side, which would break a
    // verbatim REQ-§32 contract. This check makes the spec wrong, loudly,
    // instead of the pack.
    for (const file of ctx.glob(`${EVALS}/*.eval.md`)) {
      const r = rel(ctx, file);
      const lines = ctx.read(r)!.split(/\r?\n/);
      for (let i = 0; i < lines.length; i++) {
        const ln = lines[i]!;
        const pathMatch = /path:\s*"([^"]+)"/.exec(ln);
        if (!pathMatch) continue;
        const doc = path.basename(pathMatch[1]!);
        const headings = DOC_HEADINGS[doc];
        if (!headings) continue;

        const claimed: string[] = [];
        // `all: [...]` / `any: [...]` / `text: "..."` entries that look like headings.
        for (const m of ln.matchAll(/"((?:##\s)[^"]*)"/g)) claimed.push(m[1]!);
        // `section: "9. Implications for the EIS"` — stored without the `## `.
        const sec = /section:\s*"([^"]+)"/.exec(ln);
        if (sec) claimed.push(`## ${sec[1]!}`);
        // Heading anchors inside a `matches:` pattern. Converting the section
        // assertions to the tempered-greedy idiom moved every heading name from
        // a `section:` field, which this check reads, into a regex literal,
        // which it did not — so a typo like `## 8. State Model` would have gone
        // from "caught offline" to "70-minute discovery". Reconstructing the
        // anchor from the regex source keeps the oracle attached.
        for (const m of ln.matchAll(/pattern:\s*"((?:[^"\\]|\\.)*)"/g)) {
          let pat: string;
          try {
            pat = JSON.parse(`"${m[1]}"`) as string;
          } catch {
            continue;
          }
          for (const a of headingAnchorsIn(pat)) claimed.push(a.heading);
        }

        for (const h of claimed) {
          if (headings.includes(h)) continue;
          return [
            false,
            `${r}:${i + 1}: asserts ${JSON.stringify(h)} against ${doc}, which is not one of its contracted headings.\n` +
              `    ${doc} defines exactly: ${JSON.stringify(headings)}\n` +
              "Fix the SPEC, not the contract — the heading sets are verbatim REQ-§31/§32/decision-log contracts, mirrored here from the same constants the skeleton checks use.",
          ];
        }
      }
    }
    return true;
  })

  .check("every staged fixture exists", (ctx: Ctx): Result => {
    for (const file of ctx.glob(`${EVALS}/*.eval.md`)) {
      const r = rel(ctx, file);
      const text = ctx.read(r)!;
      for (const m of text.matchAll(/copy:\s*"(fixtures\/[^"]+)"/g)) {
        const target = `${EVALS}/${m[1]!}`;
        if (ctx.read(target) !== null) continue; // a single file
        if (ctx.glob(`${target}/*`).length === 0) {
          return [false, `${r}: staged fixture '${m[1]!}' does not exist`];
        }
      }
    }
    return true;
  })

  .check("no behavioural spec leaks the expected answer into its prompt", (ctx: Ctx): Result => {
    for (const file of ctx.glob(`${EVALS}/*.eval.md`)) {
      const r = rel(ctx, file);
      const text = ctx.read(r)!;
      const actStart = text.indexOf("## Act");
      const act = text.slice(actStart, text.indexOf("## Assert", actStart));
      for (const leak of ["EIS-§", "capability matrix", "DRV-", "Q-MD-", "EV-GAP"]) {
        if (act.includes(leak)) {
          return [
            false,
            `${r}: '## Act' prompt mentions ${JSON.stringify(leak)} — the prompt must describe the task, never the answer the assertions look for`,
          ];
        }
      }
    }
    return true;
  })

  // ---- group 8: the guard/caller handshake -------------------------------

  .check("every Invocation Guard states the preamble and keys it demands", (ctx: Ctx): Result => {
    for (const { agent, requires, preambleMirrored } of GUARD_CONTRACTS) {
      const r = `${PACK}/agents/${agent}.agent.md`;
      const text = ctx.read(r);
      if (text === null) return [false, `missing ${r}`];
      const guard = sectionBody(text, "## Invocation Guard");
      if (guard === null) return [false, `${r}: no '## Invocation Guard' section`];
      const body = flat(admittingCondition(guard));
      if (!body) return [false, `${r}: '## Invocation Guard' has no numbered admitting condition '1.'`];

      const preamble = flat(delegationPreamble(agent));
      if (preambleMirrored && !body.includes(preamble)) {
        return [
          false,
          `${r}: '## Invocation Guard' never states the delegation preamble it admits callers on.\n` +
            `    expected the guard to quote: ${JSON.stringify(preamble)}\n` +
            "A guard whose admitting condition is not written down cannot be satisfied on purpose — it is satisfied by luck. Mirror the preamble from the orchestrator's '## How to Delegate (Task Tool Mechanics)'.",
        ];
      }
      if (!preambleMirrored && body.includes(preamble)) {
        return [
          false,
          `${r}: '## Invocation Guard' now quotes the canonical preamble, but GUARD_CONTRACTS still marks it preambleMirrored: false.\n` +
            "Flip the flag — the exemption existed only because this file was outside the eval-run-1 fix turn's write scope.",
        ];
      }
      if (!preambleMirrored && !body.includes("@ux-interaction-spec")) {
        return [
          false,
          `${r}: '## Invocation Guard' names no caller at all. Even the un-migrated prose form must require the call to come from '@ux-interaction-spec'.`,
        ];
      }
      for (const token of [...requires, STM_IN_GUARD]) {
        if (!body.includes(token)) {
          return [
            false,
            `${r}: '## Invocation Guard' demands tokens the suite does not know about, or has dropped ${JSON.stringify(token)} from its admitting condition.\n` +
              `    GUARD_CONTRACTS says this guard requires: ${JSON.stringify([...requires, STM_IN_GUARD])}\n` +
              "The token must appear in numbered condition 1 — the clause that actually gates the work — not merely somewhere in the section. Update the guard and GUARD_CONTRACTS together, or the caller-side check below goes vacuous.",
          ];
        }
      }
    }
    return true;
  })

  .check("every worked call satisfies the guard of the agent it invokes", (ctx: Ctx): Result => {
    const text = ctx.read(`${PACK}/agents/${ORCHESTRATOR}.agent.md`);
    if (text === null) return [false, `missing ${ORCHESTRATOR}.agent.md`];
    const calls = workedCalls(text);

    for (const { agent, requires } of GUARD_CONTRACTS) {
      const call = calls.get(agent);
      if (!call) {
        return [
          false,
          `orchestrator has no worked task(...) call with agent_type: ${JSON.stringify(agent)} — ` +
            `every delegated agent needs one, and it is the only place the guard contract is exercised`,
        ];
      }
      const body = flat(call);

      const preamble = flat(delegationPreamble(agent));
      if (!body.includes(preamble)) {
        return [
          false,
          `orchestrator worked call for ${JSON.stringify(agent)} omits the delegation preamble.\n` +
            `    expected the prompt to open with: ${JSON.stringify(preamble)}\n` +
            "This is eval run 1's defect exactly: the guard's first conjunct is that the call comes from @ux-interaction-spec, and naming the callee ('You are being invoked as @" +
            agent +
            "') does not state the caller. The specialist refuses, the phase is lost, and no document is written.",
        ];
      }
      for (const token of [...requires, STM_IN_CALL]) {
        if (!body.includes(token)) {
          return [
            false,
            `orchestrator worked call for ${JSON.stringify(agent)} omits ${JSON.stringify(token)}, which that agent's '## Invocation Guard' requires.\n` +
              `    guard requires: ${JSON.stringify([`Caller: ...@${agent}...`, ...requires, STM_IN_CALL])}\n` +
              "Fix the CALLER, not the guard: the guards are arch §2.6's defence against specialists being run standalone with no session state and no traceability.",
          ];
        }
      }
    }

    for (const agent of calls.keys()) {
      if (!GUARD_CONTRACTS.some((g) => g.agent === agent)) {
        return [
          false,
          `orchestrator delegates to unknown agent_type ${JSON.stringify(agent)} — add it to GUARD_CONTRACTS so its guard is cross-checked too`,
        ];
      }
    }
    return true;
  })

  .check("the orchestrator defines {stm} and orders it expanded before sending", (ctx: Ctx): Result => {
    const text = ctx.read(`${PACK}/agents/${ORCHESTRATOR}.agent.md`);
    if (text === null) return [false, `missing ${ORCHESTRATOR}.agent.md`];
    const body = flat(text);
    if (!body.includes("`{stm}` = `.ux-interaction-spec-stm/runs/{sid}/`")) {
      return [
        false,
        "orchestrator no longer defines `{stm}` as `.ux-interaction-spec-stm/runs/{sid}/` — " +
          "every guard admits callers on those literal paths, so the definition is load-bearing",
      ];
    }
    if (!/Expand it to the literal\s+path in every `task` prompt/.test(flat(text))) {
      return [
        false,
        "orchestrator no longer orders `{stm}` expanded to a literal path in every `task` prompt. " +
          "A sub-agent that receives the raw token sees no STM path, fails its guard, and refuses.",
      ];
    }
    return true;
  })

  .build();
