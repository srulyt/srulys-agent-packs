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
from .judge import JudgeError, Verdict, judge
from .metrics import MetricResult, load_history, record_metric, summarize
from .rubric import Check, RubricResult, check_judge, rubric
from .runners.base import RunResult, SUTRunner, get_runner
from .workspace import FixtureMissingError, Workspace

__version__ = "0.1.0"

__all__ = [
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
