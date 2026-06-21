"""Unit tests for evalpilot's pure logic (no copilot binary required).

These run in plain CI. They cover discovery, the metric JSONL store +
regression compare, the rubric model, and the runner registry.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from evalpilot import rubric, check_judge
from evalpilot import metrics as M
from evalpilot import discovery
from evalpilot.runners.base import get_runner, RunResult


# ---- rubric -------------------------------------------------------------


def test_rubric_all_pass():
    r = rubric(("a", True), ("b", True, "detail"))
    assert r.passed and r.pass_rate == 1.0
    r.assert_passed()


def test_rubric_failure_lists_failed():
    r = rubric(("a", True), ("b", False, "nope"))
    assert not r.passed
    assert [c.name for c in r.failed] == ["b"]
    with pytest.raises(AssertionError) as ei:
        r.assert_passed(log_path="x.log")
    assert "nope" in str(ei.value) and "x.log" in str(ei.value)


def test_check_judge_maps_verdict():
    class V:
        passed = False
        score = 0.42
        reasoning = "weak"
    c = check_judge("semantic", V())
    assert not c.passed and "0.42" in c.detail and "weak" in c.detail


def test_rubric_bad_check_type():
    with pytest.raises(TypeError):
        rubric(123)


# ---- metrics: store + baseline + regression -----------------------------


def _root(tmp_path: Path) -> Path:
    return tmp_path / "_metrics"


def test_metric_first_record_has_no_baseline(tmp_path):
    res = M.record_metric(name="lat", value=100.0, eval_id="t",
                          direction="lower_is_better", metrics_root=_root(tmp_path))
    assert res.baseline is None and res.delta is None and not res.regressed
    assert res.history_path.exists()
    line = json.loads(res.history_path.read_text().splitlines()[0])
    assert line["value"] == 100.0 and line["name"] == "lat"


def test_metric_last_baseline_and_regression_lower_is_better(tmp_path):
    root = _root(tmp_path)
    M.record_metric(name="lat", value=100.0, eval_id="t",
                    direction="lower_is_better", metrics_root=root)
    res = M.record_metric(name="lat", value=130.0, eval_id="t",
                          direction="lower_is_better", tolerance=10,
                          metrics_root=root)
    assert res.baseline == 100.0 and res.delta == 30.0 and res.regressed


def test_metric_tolerance_absorbs_small_drift(tmp_path):
    root = _root(tmp_path)
    M.record_metric(name="lat", value=100.0, eval_id="t",
                    direction="lower_is_better", metrics_root=root)
    res = M.record_metric(name="lat", value=105.0, eval_id="t",
                          direction="lower_is_better", tolerance=10,
                          metrics_root=root)
    assert not res.regressed


def test_metric_higher_is_better_regression(tmp_path):
    root = _root(tmp_path)
    M.record_metric(name="score", value=0.9, eval_id="t",
                    direction="higher_is_better", metrics_root=root)
    res = M.record_metric(name="score", value=0.6, eval_id="t",
                          direction="higher_is_better", tolerance_pct=0.1,
                          metrics_root=root)
    assert res.regressed and res.delta == pytest.approx(-0.3)


def test_metric_neutral_never_regresses(tmp_path):
    root = _root(tmp_path)
    M.record_metric(name="n", value=1, eval_id="t", direction="neutral",
                    metrics_root=root)
    res = M.record_metric(name="n", value=1000, eval_id="t", direction="neutral",
                          metrics_root=root)
    assert not res.regressed


def test_metric_rolling_mean_baseline(tmp_path):
    root = _root(tmp_path)
    for v in (10, 20, 30):
        M.record_metric(name="r", value=v, eval_id="t",
                        direction="higher_is_better",
                        baseline_strategy="rolling_mean", metrics_root=root)
    res = M.record_metric(name="r", value=25, eval_id="t",
                          direction="higher_is_better",
                          baseline_strategy="rolling_mean", metrics_root=root)
    assert res.baseline == pytest.approx(20.0)  # mean(10,20,30)


def test_metric_best_baseline(tmp_path):
    root = _root(tmp_path)
    for v in (0.5, 0.8, 0.6):
        M.record_metric(name="b", value=v, eval_id="t",
                        direction="higher_is_better",
                        baseline_strategy="best", metrics_root=root)
    res = M.record_metric(name="b", value=0.7, eval_id="t",
                          direction="higher_is_better",
                          baseline_strategy="best", metrics_root=root)
    assert res.baseline == 0.8


def test_metric_pinned_baseline(tmp_path):
    res = M.record_metric(name="p", value=5, eval_id="t",
                          baseline_strategy="pinned", baseline=10,
                          direction="higher_is_better", tolerance=0,
                          metrics_root=_root(tmp_path))
    assert res.baseline == 10 and res.regressed


def test_metric_assert_no_regression_raises(tmp_path):
    root = _root(tmp_path)
    M.record_metric(name="g", value=100, eval_id="t",
                    direction="lower_is_better", metrics_root=root)
    res = M.record_metric(name="g", value=200, eval_id="t",
                          direction="lower_is_better", metrics_root=root)
    with pytest.raises(AssertionError):
        res.assert_no_regression()


def test_metric_summarize_and_iter_series(tmp_path):
    root = _root(tmp_path)
    for v in (1, 2, 3):
        M.record_metric(name="s", value=v, eval_id="t",
                        direction="higher_is_better", metrics_root=root)
    s = M.summarize("t", "s", metrics_root=root)
    assert s["count"] == 3 and s["latest"] == 3 and s["min"] == 1 and s["max"] == 3
    slugs = [slug for slug, _ in M.iter_series(root)]
    assert slugs == [M.metric_slug("t", "s")]


def test_metric_bad_direction(tmp_path):
    with pytest.raises(ValueError):
        M.record_metric(name="x", value=1, direction="sideways",
                        metrics_root=_root(tmp_path))


# ---- discovery ----------------------------------------------------------


def _write(p: Path, text: str = "x") -> None:
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(text, encoding="utf-8")


def test_discover_agents_and_skills_across_layouts(tmp_path):
    repo = tmp_path / "repo"
    (repo / ".git").mkdir(parents=True)
    # repo-level agent
    _write(repo / ".github" / "agents" / "alpha.agent.md", "---\nname: alpha\n---\n")
    # plugin-layout agent + skill
    _write(repo / "plugins" / "p" / "plugin.json", "{}")
    _write(repo / "plugins" / "p" / "agents" / "beta.agent.md", "---\nname: beta\n---\n")
    _write(repo / "plugins" / "p" / "skills" / "do-thing" / "SKILL.md", "---\nname: do-thing\n---\n")
    # repo-level skill
    _write(repo / ".github" / "skills" / "shared" / "SKILL.md", "---\nname: shared\n---\n")

    agents = {a.name: a for a in discovery.discover_agents(repo)}
    assert set(agents) == {"alpha", "beta"}
    assert agents["beta"].plugin_root == (repo / "plugins" / "p").resolve()
    assert agents["alpha"].plugin_root is None

    skills = {s.name: s for s in discovery.discover_skills(repo)}
    assert set(skills) == {"do-thing", "shared"}
    assert skills["do-thing"].plugin_root == (repo / "plugins" / "p").resolve()


def test_find_agent_missing_and_ambiguous(tmp_path):
    repo = tmp_path / "repo"
    (repo / ".git").mkdir(parents=True)
    with pytest.raises(LookupError):
        discovery.find_agent("nope", repo)
    _write(repo / "a" / "agents" / "dup.agent.md")
    _write(repo / "b" / "agents" / "dup.agent.md")
    with pytest.raises(LookupError):
        discovery.find_agent("dup", repo)


def test_discovery_prunes_noise_dirs(tmp_path):
    repo = tmp_path / "repo"
    (repo / ".git").mkdir(parents=True)
    _write(repo / "node_modules" / "x" / "agents" / "ghost.agent.md")
    _write(repo / ".github" / "agents" / "real.agent.md")
    names = {a.name for a in discovery.discover_agents(repo)}
    assert names == {"real"}


# ---- runner registry ----------------------------------------------------


def test_copilot_runner_registered():
    r = get_runner("copilot")
    assert r.name == "copilot"


def test_unknown_runner_raises():
    with pytest.raises(LookupError):
        get_runner("does-not-exist")


def test_runresult_helpers():
    r = RunResult(returncode=0, stdout="", stderr="", duration_seconds=1.0,
                  log_path=Path("x"))
    assert r.ok and r.usable and r.unavailable_reason() == ""
    sk = RunResult(returncode=125, stdout="", stderr="", duration_seconds=0.0,
                   log_path=Path("x"), skipped=True)
    assert not sk.usable and "not launched" in sk.unavailable_reason()
