"""Self-tests for the ``_lib`` helpers.

These don't require the ``copilot`` binary -- they exercise the pure
Python parts (workspace staging, judge JSON extraction). They live under
``evals/static/`` so they run alongside the static linters.
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from _lib import judge as judge_mod
from _lib.workspace import Workspace, REPO_ROOT


def test_judge_extracts_plain_json():
    out = '{"score": 0.9, "rationale": "good", "evidence": []}'
    assert judge_mod._extract_json(out) == {
        "score": 0.9,
        "rationale": "good",
        "evidence": [],
    }


def test_judge_extracts_json_surrounded_by_prose():
    out = "Sure, here is the verdict:\n```\n{\"score\": 0.4, \"rationale\": \"meh\"}\n```\nDone."
    parsed = judge_mod._extract_json(out)
    assert parsed is not None
    assert parsed["score"] == 0.4


def test_judge_returns_none_on_garbage():
    assert judge_mod._extract_json("totally not json") is None


def test_workspace_creates_root(tmp_path: Path):
    ws = Workspace(root=tmp_path / "ws", logs_dir=tmp_path / "_logs")
    assert ws.root.exists()
    assert ws.logs_dir.exists()


def test_workspace_stage_skill_missing_raises(tmp_path: Path):
    ws = Workspace(root=tmp_path / "ws", logs_dir=tmp_path / "_logs")
    with pytest.raises(FileNotFoundError):
        ws.stage_skill("definitely-not-a-real-skill-xyz")


def test_workspace_glob_and_find_one(tmp_path: Path):
    ws = Workspace(root=tmp_path / "ws", logs_dir=tmp_path / "_logs")
    (ws.root / "a").mkdir()
    (ws.root / "a" / "x.md").write_text("hello")
    (ws.root / "a" / "y.md").write_text("world")
    assert len(ws.glob("**/*.md")) == 2
    assert ws.find_one("**/x.md").read_text() == "hello"
    with pytest.raises(AssertionError):
        ws.find_one("**/*.md")  # >1 match
