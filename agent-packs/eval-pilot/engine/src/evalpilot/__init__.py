"""evalpilot — portable eval engine for GitHub Copilot agents and skills.

Public API (stable surface for eval authors)::

    from evalpilot import (
        Workspace,                 # isolated per-test workspace
        judge, Verdict,            # LLM-as-judge
        rubric, Check, check_judge,# binary pass/fail rubric
        record_metric, MetricResult,  # numeric metrics + JSONL history
        assert_prose_contains, assert_prose_not_contains,
        get_runner, RunResult,     # pluggable SUT runner
        Config,
    )

Most eval authors interact with the engine through the pytest fixtures the
bundled plugin provides (``workspace``, ``agent_pack``, ``skill``,
``judge``, ``metric``) and only import ``rubric`` / ``check_judge`` /
``record_metric`` / the assert helpers directly.
"""

from __future__ import annotations

from .asserts import assert_prose_contains, assert_prose_not_contains
from .config import Config, find_eval_root, find_metrics_root, find_repo_root
from .executor import run_eval, run_specs
from .judge import JudgeError, Verdict, judge
from .loaders import Eval, load_markdown_eval, parse_markdown_eval
from .metrics import MetricResult, load_history, record_metric, summarize
from .model import (
    AssertionResult,
    EvalResult,
    EvalRunReport,
    JudgeResult,
    MetricRecord,
)
from .rubric import Check, RubricResult, check_judge, rubric
from .runners.base import RunResult, SUTRunner, get_runner
from .spec import EvalSpec
from .workspace import FixtureMissingError, Workspace

__version__ = "0.2.0"

__all__ = [
    # authoring surfaces
    "Eval",
    "load_markdown_eval",
    "parse_markdown_eval",
    "EvalSpec",
    # execution
    "run_eval",
    "run_specs",
    # result model
    "EvalResult",
    "EvalRunReport",
    "AssertionResult",
    "JudgeResult",
    "MetricRecord",
    # primitives (still public)
    "Workspace",
    "FixtureMissingError",
    "judge",
    "Verdict",
    "JudgeError",
    "rubric",
    "Check",
    "RubricResult",
    "check_judge",
    "record_metric",
    "MetricResult",
    "load_history",
    "summarize",
    "assert_prose_contains",
    "assert_prose_not_contains",
    "get_runner",
    "RunResult",
    "SUTRunner",
    "Config",
    "find_repo_root",
    "find_eval_root",
    "find_metrics_root",
    "__version__",
]
