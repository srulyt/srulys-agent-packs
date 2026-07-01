"""Unit tests for the evalpilot DSL layer (no copilot binary required).

Covers the modeled result round-trip, the Markdown loader, the fluent Python
builder, the assertion registry, the executor end-to-end (via the offline mock
runner), and the three renderers. These run in plain CI.
"""

from __future__ import annotations

import json
import os
from pathlib import Path

import pytest

from evalpilot import Eval, load_markdown_eval, parse_markdown_eval, run_eval, run_specs
from evalpilot.model import (
    AssertionResult, EvalResult, EvalRunReport, JudgeResult, MetricRecord,
    PASSED, FAILED,
)
from evalpilot.assertions import assertion, run_assertion, AssertContext
from evalpilot.spec import AssertionSpec, EvalSpec
from evalpilot.loaders.markdown import EvalParseError
from evalpilot.render import render_terminal, render_html, to_json_str
from evalpilot.render.json_report import read_json, write_json
from evalpilot.runners import mock as mock_runner
from evalpilot.runners.base import get_runner


# ---- model round-trip ---------------------------------------------------


def test_model_json_round_trip():
    result = EvalResult(
        name="demo", status=PASSED, duration_seconds=1.5,
        assertions=[AssertionResult(kind="contains", name="a", passed=True)],
        judges=[JudgeResult(name="judge", score=0.9, threshold=0.7, passed=True)],
        metrics=[MetricRecord(name="judge_score", value=0.9)],
    )
    report = EvalRunReport(run_id="r1", results=[result])
    assert report.ok

    text = to_json_str(report)
    back = EvalRunReport.from_dict(json.loads(text))
    assert back.run_id == "r1"
    assert back.results[0].name == "demo"
    assert back.results[0].assertions[0].kind == "contains"
    assert back.results[0].judges[0].score == 0.9


# ---- markdown loader ----------------------------------------------------


_MD = """\
---
name: demo-eval
target: demo-agent
kind: agent
tags: [smoke, judge]
timeout: 42
---

# Title
> the description line

## Act
```prompt
do the thing
```

## Assert
```yaml
stdout_contains:
  - { text: "hello" }
judge:
  threshold: 0.6
  criteria: |
    Be strict.
metrics:
  - { name: score, value: $judge.score, direction: higher_is_better,
      baseline: rolling_mean, tolerance: 0.1 }
```
"""


def test_markdown_parses_all_sections():
    spec = parse_markdown_eval(_MD)
    assert spec.name == "demo-eval"
    assert spec.kind == "agent"
    assert spec.timeout == 42
    assert "smoke" in spec.tags
    assert spec.act.prompt.strip() == "do the thing"
    assert any(a.kind == "stdout_contains" for a in spec.assertions)
    assert spec.judges[0].threshold == 0.6
    assert spec.metrics[0].value == "$judge.score"
    assert spec.validate() == []


def test_markdown_empty_setup_is_valid():
    md = _MD.replace("## Act", "## Setup\n```yaml\n# only comments\n```\n\n## Act")
    spec = parse_markdown_eval(md)
    assert spec.validate() == []


def test_markdown_bad_yaml_raises():
    bad = _MD.replace('stdout_contains:', 'stdout_contains: : :')
    with pytest.raises(EvalParseError):
        parse_markdown_eval(bad)


_MD_DESC = """\
---
name: desc-eval
target: demo-agent
kind: agent
tags: [smoke]
---

# Human Title
> short summary line

## Description
First paragraph explaining the scenario in plain English.

Second paragraph with more detail about the expected outcome.

## Act
```prompt
do the thing
```

## Assert
```yaml
stdout_contains:
  - { text: "hello" }
```
"""


def test_markdown_description_and_summary():
    spec = parse_markdown_eval(_MD_DESC)
    assert spec.summary == "short summary line"
    assert spec.description.startswith("First paragraph")
    assert "Second paragraph" in spec.description
    # blockquote is the summary, not folded into the long description
    assert "short summary line" not in spec.description
    assert spec.validate() == []


def test_frontmatter_summary_overrides_blockquote():
    md = _MD_DESC.replace("kind: agent\n", "kind: agent\nsummary: from frontmatter\n")
    spec = parse_markdown_eval(md)
    assert spec.summary == "from frontmatter"


def test_stub_detection_and_lint(tmp_path):
    stub_md = """\
---
name: stub-eval
target: demo-agent
kind: agent
---

# Stub
> a described-but-unimplemented eval

## Description
We want to check that the agent refuses unsafe requests. Not implemented yet.
"""
    spec = parse_markdown_eval(stub_md)
    assert spec.is_stub()
    assert not spec.is_implemented()
    # an implemented spec is not a stub
    assert not parse_markdown_eval(_MD_DESC).is_stub()


def test_builder_summary_and_describe():
    spec = (
        Eval("b", target="a", kind="agent")
        .summarize("one liner")
        .describe("the long form")
        .prompt("go")
        .expect_stdout("x")
        .build()
    )
    assert spec.summary == "one liner"
    assert spec.description == "the long form"


# ---- builder ------------------------------------------------------------


def test_builder_matches_markdown_shape():
    spec = (
        Eval("demo-eval", target="demo-agent", kind="agent",
             tags=["smoke", "judge"], timeout=42)
        .describe("the description line")
        .prompt("do the thing")
        .expect_stdout("hello")
        .judge("Be strict.", threshold=0.6)
        .metric("score", "$judge.score", direction="higher_is_better",
                baseline="rolling_mean", tolerance=0.1)
        .build()
    )
    assert isinstance(spec, EvalSpec)
    assert spec.act.prompt.strip() == "do the thing"
    assert spec.judges[0].threshold == 0.6
    assert spec.metrics[0].baseline_strategy == "rolling_mean"
    assert spec.validate() == []


# ---- assertion registry -------------------------------------------------


def test_custom_assertion_registers_and_runs():
    @assertion("two_lines_min")
    def _two_lines(ctx: AssertContext, args: dict) -> AssertionResult:
        n = len(ctx.stdout.splitlines())
        return AssertionResult(
            kind="two_lines_min", name="two_lines_min",
            passed=n >= 2, detail=f"lines={n}",
        )

    ctx = AssertContext(root=Path("."), stdout="a\nb\nc", stderr="")
    res = run_assertion(AssertionSpec(kind="two_lines_min"), ctx)
    assert res.passed


def test_json_empty_assertion(tmp_path):
    (tmp_path / "state.json").write_text(
        json.dumps({"mcps_detected": [], "count": 3}), encoding="utf-8"
    )
    ctx = AssertContext(root=tmp_path)
    # empty list -> passes
    ok = run_assertion(
        AssertionSpec(kind="json_empty", args={"path": "state.json",
                                               "query": "mcps_detected"}), ctx)
    assert ok.passed, ok.detail
    # absent key -> passes (treated as empty)
    absent = run_assertion(
        AssertionSpec(kind="json_empty", args={"path": "state.json",
                                               "query": "missing"}), ctx)
    assert absent.passed, absent.detail
    # non-empty value -> fails
    nonempty = run_assertion(
        AssertionSpec(kind="json_empty", args={"path": "state.json",
                                               "query": "count"}), ctx)
    assert not nonempty.passed


def test_section_scoped_assertions(tmp_path):
    spec = (
        "## Problem Statement\n"
        "The rotation is drowning in pages.\n\n"
        "## Solution Summary\n"
        "A dashboard showing SLO state per service.\n"
    )
    (tmp_path / "spec.md").write_text(spec, encoding="utf-8")
    ctx = AssertContext(root=tmp_path)
    # leak check: 'drowning' must NOT appear in Solution Summary -> passes
    isolated = run_assertion(
        AssertionSpec(kind="section_not_contains",
                      args={"path": "spec.md", "section": "Solution Summary",
                            "text": "drowning"}), ctx)
    assert isolated.passed, isolated.detail
    # 'dashboard' IS in Solution Summary -> section_contains passes
    present = run_assertion(
        AssertionSpec(kind="section_contains",
                      args={"path": "spec.md", "section": "Solution Summary",
                            "text": "dashboard"}), ctx)
    assert present.passed, present.detail
    # leak actually present -> section_not_contains fails
    leak = run_assertion(
        AssertionSpec(kind="section_not_contains",
                      args={"path": "spec.md", "section": "Problem Statement",
                            "text": "drowning"}), ctx)
    assert not leak.passed


# ---- executor end-to-end (mock runner) ----------------------------------


@pytest.fixture(autouse=True)
def _reset_mock():
    mock_runner.reset_mock()
    yield
    mock_runner.reset_mock()


def _nostage_spec() -> EvalSpec:
    return (
        Eval("nostage", kind="none", tags=["smoke"])
        .prompt("say hi")
        .expect_stdout("STATUS=ok")
        .metric("out_chars", "$stdout.chars", direction="higher_is_better",
                baseline="last")
        .build()
    )


def test_executor_pass_path(tmp_path, monkeypatch):
    monkeypatch.setenv("EVALPILOT_METRICS_ROOT", str(tmp_path / "_metrics"))
    mock_runner.configure_mock(stdout="hello STATUS=ok")
    result = run_eval(_nostage_spec(), work_root=tmp_path / "_runs",
                      runner=get_runner("mock"))
    assert result.status == PASSED
    assert result.assertions[0].passed
    assert result.metrics[0].value == len("hello STATUS=ok")


def test_executor_fail_path(tmp_path, monkeypatch):
    monkeypatch.setenv("EVALPILOT_METRICS_ROOT", str(tmp_path / "_metrics"))
    mock_runner.configure_mock(stdout="nothing useful here")
    result = run_eval(_nostage_spec(), work_root=tmp_path / "_runs",
                      runner=get_runner("mock"))
    assert result.status == FAILED


def test_run_specs_and_renderers(tmp_path, monkeypatch):
    monkeypatch.setenv("EVALPILOT_METRICS_ROOT", str(tmp_path / "_metrics"))
    mock_runner.configure_mock(stdout="hello STATUS=ok")
    report = run_specs([_nostage_spec()], work_root=tmp_path / "_runs",
                       runner=get_runner("mock"))
    assert report.ok

    # JSON round-trip from disk.
    jpath = write_json(report, tmp_path / "report.json")
    assert read_json(jpath).ok

    # Renderers produce non-empty output referencing the eval.
    term = render_terminal(report)
    assert "nostage" in term
    html = render_html(report)
    assert "<html" in html.lower() and "nostage" in html
