"""Progressive-disclosure split smoke: a large feature forces the SKILL.md to
become a lean index plus references/01..05, with the index body under the
single-source token threshold.
"""

from __future__ import annotations

import math
import re
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[3]
THRESHOLD_REF = (
    REPO_ROOT
    / "agent-packs"
    / "context-pack-builder"
    / "skills"
    / "progressive-disclosure"
    / "references"
    / "split-threshold.md"
)

PROMPT = """\
Build a context pack for the large "billing" subsystem in this repository.
Seed paths: the entire src/billing/ tree. This subsystem is intentionally
large: many controllers, services, data models, migrations, config flags,
and tests. Discover ALL related code across all layers, analyze it
thoroughly, and produce a complete, detailed context pack in context-packs/.
Because the content is large, ensure the SKILL.md is split into a
progressively-loading index plus references/ files. Run to completion.
"""


def _read_threshold() -> int:
    text = THRESHOLD_REF.read_text(encoding="utf-8")
    m = re.search(r"SPLIT_THRESHOLD_TOKENS\s*=\s*(\d+)", text)
    assert m
    return int(m.group(1))


def _strip_frontmatter(text: str) -> str:
    lines = text.splitlines()
    if lines and lines[0].strip() == "---":
        for i in range(1, len(lines)):
            if lines[i].strip() == "---":
                return "\n".join(lines[i + 1 :])
    return text


def _token_estimate(body: str) -> int:
    return max(math.ceil(len(body) / 4), math.ceil(len(body.split()) * 1.33))


def _seed_large_fixture(root: Path) -> None:
    base = root / "src" / "billing"
    base.mkdir(parents=True, exist_ok=True)
    for i in range(40):
        (base / f"module_{i:02d}.py").write_text(
            f"# billing module {i}\n"
            f"class Billing{i}:\n"
            f"    \"\"\"Handles billing concern {i}: invoices, charges, refunds.\"\"\"\n"
            f"    def process_{i}(self, account, amount):\n"
            f"        return charge(account, amount)\n" * 6,
            encoding="utf-8",
        )


@pytest.mark.pack
@pytest.mark.slow
def test_progressive_disclosure_split(agent_pack):
    ws = agent_pack("context-pack-builder")
    _seed_large_fixture(ws.root)

    result = ws.run_agent(prompt=PROMPT, agent="cpb-orchestrator", timeout=1200)
    if not result.usable:
        pytest.skip(result.unavailable_reason())
    assert result.ok, f"cpb-orchestrator invocation failed; see {result.log_path}"

    skill_files = ws.glob("context-packs/*-context/skills/*-context/SKILL.md")
    assert skill_files, f"expected a generated SKILL.md; see {result.log_path}"

    refs = ws.glob("context-packs/*-context/skills/*-context/references/*.md")
    assert refs, (
        f"expected references/ files after a split; the split did not fire; "
        f"see {result.log_path}"
    )

    threshold = _read_threshold()
    index_body = _strip_frontmatter(skill_files[0].read_text(encoding="utf-8"))
    est = _token_estimate(index_body)
    assert est <= threshold, (
        f"split index body token estimate {est} exceeds threshold {threshold}; "
        f"see {result.log_path}"
    )
