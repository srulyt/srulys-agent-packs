"""Judge orchestration package.

The harness cannot programmatically invoke ``@eval-judge`` from outside the
Copilot CLI runtime, so the judge layer operates in a human-in-the-loop
mode: the harness emits a *judge manifest* that the operator follows by
running ``@eval-judge`` once per rubric, then pastes the JSON responses
into a file the harness reads back.

See ``eval_engine/docs/05-design-revisions-v2.md`` §judge for the protocol.
"""

from .orchestration import (
    JudgeManifest,
    JudgeRequest,
    JudgeResponse,
    build_manifest,
    load_responses,
    apply_double_invoke,
)
from .subprocess_runner import (
    CopilotBinNotFound,
    JudgeRunResult,
    run_manifest,
    run_one_judge_request,
)

__all__ = [
    "JudgeManifest",
    "JudgeRequest",
    "JudgeResponse",
    "build_manifest",
    "load_responses",
    "apply_double_invoke",
    "CopilotBinNotFound",
    "JudgeRunResult",
    "run_manifest",
    "run_one_judge_request",
]
