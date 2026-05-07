"""In-memory dataclasses for the harness.

These mirror the YAML/JSON schemas documented in ``eval_engine/docs/`` (with v2
revisions in ``05-design-revisions-v2.md`` taking precedence). They are
intentionally lightweight: no validation logic lives here — that is in
``loaders.py`` — and no I/O. Tests can construct them directly.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


# ---------- Pack spec ----------------------------------------------------


@dataclass
class InvocationExpectation:
    min: int = 0
    max: int = 1
    must_complete: bool = True


@dataclass
class PromptContract:
    required_sections: list[str] = field(default_factory=list)
    required_fields: list[str] = field(default_factory=list)
    forbidden_input: list[str] = field(default_factory=list)
    forbidden_downstream: list[str] = field(default_factory=list)


@dataclass
class OutputContract:
    must_contain_sections: list[str] = field(default_factory=list)
    forbidden: list[str] = field(default_factory=list)
    schema_ref: str | None = None  # path to a schema file (relative to spec)


@dataclass
class AgentSpec:
    name: str
    invocations: InvocationExpectation = field(default_factory=InvocationExpectation)
    allowed_tools: list[str] = field(default_factory=list)
    write_scope_allow: list[str] = field(default_factory=list)
    read_scope_allow: list[str] = field(default_factory=list)
    scope_deny: list[str] = field(default_factory=list)
    prompt_contract: PromptContract = field(default_factory=PromptContract)
    output_contract: OutputContract = field(default_factory=OutputContract)
    token_budget_max: int | None = None
    no_subagent_reinvocation: bool = True


@dataclass
class FlowConstraints:
    ordering: list[tuple[str, str]] = field(default_factory=list)  # (before, after)
    no_unexpected_agents: bool = True


@dataclass
class RubricRef:
    id: str
    apply_to: str  # "artifact:<artifact_id>" | "per_agent:<agent>" | "pack"
    severity: str = "info"  # info | warn | blocker
    threshold: float | None = None


@dataclass
class LoopConvergence:
    """Pack-level convergence rules consumed by ``run-pack``.

    ``required_status``:
      * ``pass`` (default) — case passes iff ``CaseVerdict.status == "pass"``
        (blocker-clean; warn rubric fails tolerated).
      * ``strict-pass`` — case must additionally have no warn-severity
        rubric fails. Warn rubrics also get judge double-invoke under
        this mode (see ``apply_double_invoke``).
    ``warn_promotes_to_blocker`` is an alias for ``strict-pass`` semantics.
    ``allow_failing_cases`` lists case ids that don't contribute to a
    fail verdict (each entry is ``{case_id: ..., reason: ..., max_runs_to_tolerate: ...}``;
    the engine honours ``case_id`` only — ``max_runs_to_tolerate`` is
    runner/orchestrator-owned because it requires prior-loop state the
    engine does not track).
    """

    required_status: str = "pass"  # pass | strict-pass
    warn_promotes_to_blocker: bool = False
    allow_failing_cases: list[dict[str, Any]] = field(default_factory=list)

    @property
    def is_strict(self) -> bool:
        return self.required_status == "strict-pass" or self.warn_promotes_to_blocker

    def is_case_allowed_to_fail(self, case_id: str) -> bool:
        return any(
            isinstance(e, dict) and e.get("case_id") == case_id
            for e in self.allow_failing_cases
        )


@dataclass
class Budgets:
    """Pack-level budget guards consumed by ``run-pack``.

    The engine enforces ``max_judge_calls_per_loop`` (pre-count manifest
    size before invoking the judge) and ``max_wall_clock_seconds_per_loop``
    (wall-clock since ``run-pack`` start). ``max_total_wall_clock_seconds``
    is across-loop and is NOT enforced in-engine — the runner / orchestrator
    tracks it. ``bail_action`` is metadata for the runner.
    """

    max_judge_calls_per_loop: int | None = None
    max_wall_clock_seconds_per_loop: int | None = None
    max_total_wall_clock_seconds: int | None = None
    bail_action: str = "surface-partial"


@dataclass
class PackSpec:
    pack: str
    orchestrator: str
    agents: list[AgentSpec]
    flow: FlowConstraints
    rubrics: list[RubricRef] = field(default_factory=list)
    models: dict[str, str] = field(default_factory=dict)
    loops: dict[str, Any] = field(default_factory=dict)  # max_orchestrator_turns, etc.
    loop_convergence: LoopConvergence = field(default_factory=LoopConvergence)
    budgets: Budgets = field(default_factory=Budgets)

    def agent(self, name: str) -> AgentSpec | None:
        return next((a for a in self.agents if a.name == name), None)


# ---------- Case + workspace --------------------------------------------


@dataclass
class WorkspaceStep:
    kind: str
    args: dict[str, Any] = field(default_factory=dict)


@dataclass
class TeardownPolicy:
    policy: str = "delete-on-pass"  # delete-on-pass | delete | keep | move-to-archive
    hooks: list[WorkspaceStep] = field(default_factory=list)


@dataclass
class ExpectedArtifact:
    id: str
    path_pattern: str
    required: bool = True


@dataclass
class ArtifactContentAssertion:
    """Regex content checks against a named artifact's text payload.

    ``artifact`` references an ``ExpectedArtifact.id`` declared in the same
    case's ``expected.artifacts`` list.

    * ``must_match`` — every pattern must match (``re.search``) at least once.
    * ``must_contain_any`` — at least ONE pattern must match (disjunction).
    * ``must_not_match`` — no pattern may match anywhere.

    Patterns are consumed verbatim — no anchor-injection.
    """

    artifact: str
    must_match: list[str] = field(default_factory=list)
    must_contain_any: list[str] = field(default_factory=list)
    must_not_match: list[str] = field(default_factory=list)


@dataclass
class StateAssertion:
    """Typed JSON-state checks against an artifact whose file is JSON.

    ``artifact`` references an ``ExpectedArtifact.id``. Each matcher is a
    mapping from a dotted JSON key-path (e.g. ``phase`` or
    ``counters.retries``) to an expected value:

    * ``equals``  — Python ``==`` against the JSON-decoded value.
    * ``matches`` — ``re.search`` of the (string-coerced) value.
    * ``exists``  — list of key-paths that must resolve.
    * ``gt`` / ``lt`` — numeric comparisons.

    A missing key counts as a failure for every matcher that references it
    (except ``exists`` itself, which expresses the missingness check).
    """

    artifact: str
    equals: dict[str, Any] = field(default_factory=dict)
    matches: dict[str, str] = field(default_factory=dict)
    exists: list[str] = field(default_factory=list)
    gt: dict[str, float] = field(default_factory=dict)
    lt: dict[str, float] = field(default_factory=dict)


@dataclass
class CaseExpected:
    artifacts: list[ExpectedArtifact] = field(default_factory=list)
    invocations: dict[str, InvocationExpectation] = field(default_factory=dict)
    allowed_agent_types: list[str] | None = None  # None = use spec
    rubric_targets: dict[str, str] = field(default_factory=dict)
    artifact_content_assertions: list[ArtifactContentAssertion] = field(default_factory=list)
    state_assertions: list[StateAssertion] = field(default_factory=list)


@dataclass
class ScriptedUserStep:
    """One scripted reply queued against the SUT orchestrator.

    The harness's scripted_user driver iterates the case's
    ``scripted_user:`` list in order. When it observes the SUT
    transition into a phase whose name matches the next pending step's
    ``on_phase``, it writes the resolved reply text to the SUT's stdin
    and pops the step. Each step must specify exactly one of ``reply``
    (literal string) or ``reply_file`` (a path resolved relative to
    the case directory).
    """

    on_phase: str
    reply: str | None = None
    reply_file: str | None = None  # case-relative path

    def has_inline_reply(self) -> bool:
        return self.reply is not None


@dataclass
class CaseSpec:
    id: str
    pack: str
    description: str
    prompt_file: str
    prompt_template_vars: dict[str, str]
    workspace_isolation: str  # copy-tree | empty | repo-clone
    inputs_dir: str | None
    golden_dir: str | None
    steps: list[WorkspaceStep]
    teardown: TeardownPolicy
    expected: CaseExpected
    case_dir: str = ""  # absolute path to the corpus case dir; filled by loader
    scripted_user: list[ScriptedUserStep] = field(default_factory=list)
    # When False, this case is pulled out of the parallel batch and run
    # sequentially (after the parallel batch completes). Defaults True
    # since per-run workspaces are already filesystem-isolated.
    parallel_safe: bool = True


# ---------- Rubric -------------------------------------------------------


@dataclass
class Rubric:
    id: str
    description: str
    prompt_template: str
    output_schema: dict[str, Any]
    scoring_anchors: dict[str, str] = field(default_factory=dict)
    inputs: list[str] = field(default_factory=list)  # required input keys


# ---------- Fixture ------------------------------------------------------


@dataclass
class Actor:
    kind: str  # "orchestrator" | "subagent"
    name: str | None = None
    invocation_id: str | None = None


@dataclass
class ToolCall:
    call_id: str
    name: str  # raw runtime name; resolve() to canonical category
    actor: Actor
    arguments: dict[str, Any] = field(default_factory=dict)
    success: bool | None = None
    started_at: str | None = None
    ended_at: str | None = None
    result_summary: str | None = None


@dataclass
class FileAccess:
    path: str  # POSIX, workspace-relative
    op: str  # "read" | "write"
    actor: Actor
    confidence: str = "high"  # high | medium | low (read inference is medium)
    call_id: str | None = None


@dataclass
class AgentInvocation:
    invocation_id: str
    name: str  # agent name
    mode: str = "sync"  # "sync" | "background"
    started_at: str | None = None
    ended_at: str | None = None
    completed: bool = False  # background-agent finalisation marker
    prompt: str = ""
    response: str | None = None
    parent_invocation_id: str | None = None
    tokens: int | None = None


@dataclass
class Fixture:
    schema_version: str
    pack: str
    case_id: str
    session_id: str
    run_id: str
    workspace_root: str  # absolute (used to remap `${WORKSPACE_ROOT}` tokens)
    captured_at: str
    cli_version: str | None
    os: str | None
    models: dict[str, str]
    invocations: list[AgentInvocation]
    tool_calls: list[ToolCall]
    file_accesses: list[FileAccess]
    background_reads: list[dict[str, Any]] = field(default_factory=list)
    session_store: dict[str, Any] = field(default_factory=dict)
    raw: dict[str, Any] = field(default_factory=dict)  # untouched original


# ---------- Verdict ------------------------------------------------------


@dataclass
class AssertionVerdict:
    assertion_id: str
    layer: str  # "L1" | "L2" | "L3"
    severity: str  # info | warn | blocker
    status: str  # pass | fail | skip | error
    message: str = ""
    agent: str | None = None
    evidence: list[dict[str, Any]] = field(default_factory=list)
    score: float | None = None


@dataclass
class RubricVerdict:
    rubric_id: str
    apply_to: str
    severity: str
    threshold: float | None
    score: float | None
    rationale: str = ""
    evidence: list[dict[str, Any]] = field(default_factory=list)
    status: str = "pass"  # pass | fail | error
    message: str = ""


@dataclass
class CaseVerdict:
    pack: str
    case_id: str
    run_id: str
    session_id: str
    git_sha: str
    timestamp: str
    status: str  # pass | fail | error
    cli_version: str | None
    os: str | None
    models: dict[str, str]
    judge_model: str | None
    temperature_recorded: dict[str, float] = field(default_factory=dict)
    counts: dict[str, int] = field(default_factory=dict)
    metrics: dict[str, Any] = field(default_factory=dict)
    rubric_scores: dict[str, RubricVerdict] = field(default_factory=dict)
    assertions: list[AssertionVerdict] = field(default_factory=list)
    prompt_hash: str | None = None
    spec_hash: str | None = None
    rubric_hashes: dict[str, str] = field(default_factory=dict)
    agent_file_hashes: dict[str, str] = field(default_factory=dict)
    repeat_group_id: str | None = None
    repeat_index: int | None = None
    run_kind: str = "local"  # "local" | "promoted"
    supersedes_run_id: str | None = None
    notes: str = ""
