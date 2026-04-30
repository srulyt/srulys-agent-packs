"""Verdict aggregation + markdown/JSON report rendering."""

from __future__ import annotations

import dataclasses
import datetime as dt
import json
import os
import subprocess
from collections import Counter
from pathlib import Path
from typing import Iterable

from . import models


def _git_sha(repo_root: str) -> str:
    try:
        return subprocess.check_output(
            ["git", "rev-parse", "HEAD"], cwd=repo_root, text=True
        ).strip()
    except Exception:
        return "unknown"


def aggregate(
    *,
    pack: str,
    case_id: str,
    run_id: str,
    session_id: str,
    repo_root: str,
    fixture: models.Fixture,
    spec: models.PackSpec,
    assertions: Iterable[models.AssertionVerdict],
    rubric_verdicts: Iterable[models.RubricVerdict],
    judge_model: str | None,
    prompt_hash: str | None = None,
    spec_hash: str | None = None,
    rubric_hashes: dict[str, str] | None = None,
    agent_file_hashes: dict[str, str] | None = None,
    repeat_group_id: str | None = None,
    repeat_index: int | None = None,
    run_kind: str = "local",
    notes: str = "",
) -> models.CaseVerdict:
    assertions = list(assertions)
    rubric_verdicts = list(rubric_verdicts)
    counts = Counter(a.status for a in assertions)
    blocker_failures = sum(
        1 for a in assertions
        if a.severity == "blocker" and a.status in ("fail", "error")
    )
    rubric_blocker_fail = any(
        rv.severity == "blocker" and rv.status in ("fail", "error")
        for rv in rubric_verdicts
    )
    error_present = any(
        a.status == "error" for a in assertions
    ) or any(rv.status == "error" for rv in rubric_verdicts)
    if blocker_failures == 0 and not rubric_blocker_fail and not error_present:
        status = "pass"
    elif error_present and blocker_failures == 0 and not rubric_blocker_fail:
        status = "error"
    else:
        status = "fail"

    metrics = {
        "subagent_invocations": len([
            i for i in fixture.invocations if i.name != spec.orchestrator
        ]),
        "tool_calls_total": len(fixture.tool_calls),
        "files_written": len([f for f in fixture.file_accesses if f.op == "write"]),
        "files_read": len([f for f in fixture.file_accesses if f.op == "read"]),
        "blocker_failures": blocker_failures,
        "warn_failures": sum(
            1 for a in assertions if a.severity == "warn" and a.status == "fail"
        ),
        "scope_violations": sum(
            1 for a in assertions if a.assertion_id in ("L3-writes", "L3-reads",
                                                          "L3-workspace-escape")
            and a.status == "fail"
        ),
        "unexpected_agents": [
            i.name for i in fixture.invocations
            if i.name != spec.orchestrator and not spec.agent(i.name)
        ],
    }

    rubric_scores = {rv.rubric_id + ":" + rv.apply_to: rv for rv in rubric_verdicts}
    return models.CaseVerdict(
        pack=pack,
        case_id=case_id,
        run_id=run_id,
        session_id=session_id,
        git_sha=_git_sha(repo_root),
        timestamp=dt.datetime.now(dt.timezone.utc).isoformat(),
        status=status,
        cli_version=fixture.cli_version,
        os=fixture.os,
        models=fixture.models,
        judge_model=judge_model,
        counts={
            "assertions_total": len(assertions),
            "assertions_pass": counts.get("pass", 0),
            "assertions_fail": counts.get("fail", 0),
            "assertions_skip": counts.get("skip", 0),
            "assertions_error": counts.get("error", 0),
            "blocker_failures": blocker_failures,
        },
        metrics=metrics,
        rubric_scores=rubric_scores,
        assertions=list(assertions),
        prompt_hash=prompt_hash,
        spec_hash=spec_hash,
        rubric_hashes=rubric_hashes or {},
        agent_file_hashes=agent_file_hashes or {},
        repeat_group_id=repeat_group_id,
        repeat_index=repeat_index,
        run_kind=run_kind,
        notes=notes,
    )


# ---------- Reporters ---------------------------------------------------


def to_dict(verdict: models.CaseVerdict) -> dict:
    return dataclasses.asdict(verdict)


def to_markdown(verdict: models.CaseVerdict) -> str:
    lines: list[str] = []
    lines.append(f"# Eval run: {verdict.pack} / {verdict.case_id}")
    lines.append("")
    lines.append(f"- **Status**: `{verdict.status.upper()}`")
    lines.append(f"- **Run ID**: `{verdict.run_id}`")
    lines.append(f"- **Session ID**: `{verdict.session_id}`")
    lines.append(f"- **Git SHA**: `{verdict.git_sha}`")
    lines.append(f"- **Timestamp**: {verdict.timestamp}")
    lines.append(f"- **Run kind**: {verdict.run_kind}")
    lines.append(f"- **Models**: {verdict.models}")
    lines.append(f"- **Judge model**: {verdict.judge_model}")
    lines.append("")
    lines.append("## Counts")
    for k, v in verdict.counts.items():
        lines.append(f"- {k}: {v}")
    lines.append("")
    lines.append("## Metrics")
    for k, v in verdict.metrics.items():
        lines.append(f"- {k}: {v}")
    lines.append("")
    if verdict.rubric_scores:
        lines.append("## Rubric scores")
        lines.append("| rubric | apply_to | severity | score | threshold | status | message |")
        lines.append("|---|---|---|---|---|---|---|")
        for rv in verdict.rubric_scores.values():
            score_s = "—" if rv.score is None else f"{rv.score:.3f}"
            thr_s = "—" if rv.threshold is None else f"{rv.threshold:.3f}"
            lines.append(
                f"| {rv.rubric_id} | {rv.apply_to} | {rv.severity} | {score_s} | "
                f"{thr_s} | {rv.status} | {rv.message} |"
            )
        lines.append("")
    lines.append("## Assertions")
    lines.append("| id | layer | severity | agent | status | message |")
    lines.append("|---|---|---|---|---|---|")
    for a in verdict.assertions:
        lines.append(
            f"| {a.assertion_id} | {a.layer} | {a.severity} | "
            f"{a.agent or ''} | {a.status} | {a.message} |"
        )
    return "\n".join(lines) + "\n"


def write_report(verdict: models.CaseVerdict, *, reports_root: str) -> str:
    Path(reports_root).mkdir(parents=True, exist_ok=True)
    target = Path(reports_root) / f"{verdict.run_id}.md"
    target.write_text(to_markdown(verdict), encoding="utf-8")
    return str(target)
