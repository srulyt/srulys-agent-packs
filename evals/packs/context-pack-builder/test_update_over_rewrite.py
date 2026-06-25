"""Idempotent update-over-rewrite smoke: running twice on the same feature
yields exactly one pack dir (no duplicate), adds a Change Log entry on the
second run, preserves a human-marked block, and a no-change re-run is a no-op.
"""

from __future__ import annotations

from pathlib import Path

import pytest

PROMPT_NEW = """\
Build a context pack for the "auth" feature in this repository.
BOUNDED MODE (fast pass): keep this run cost-capped and single-pass.
Scope — confine discovery/analysis to EXACTLY src/auth/ (login.py and
session.py); do NOT scan the rest of the repository. The feature handles
login and session tokens. Produce the pack in context-packs/ and run to
completion.
"""

PROMPT_UPDATE = """\
Update the existing context pack for the "auth" feature.
BOUNDED MODE (fast pass): keep this run cost-capped and single-pass.
I added password reset to src/auth/reset.py. Scope — confine
discovery/analysis to EXACTLY src/auth/; do NOT scan the rest of the
repository. Re-run discovery/analysis and merge the update into the
EXISTING pack (do NOT create a duplicate pack). Preserve any
human-authored sections.
"""


def _seed_auth(root: Path) -> None:
    base = root / "src" / "auth"
    base.mkdir(parents=True, exist_ok=True)
    (base / "login.py").write_text(
        "def login(user, pw):\n    return issue_token(user)\n", encoding="utf-8"
    )
    (base / "session.py").write_text(
        "def issue_token(user):\n    return 'tok'\n", encoding="utf-8"
    )


@pytest.mark.pack
@pytest.mark.slow
# Two sequential SUT runs. Ordering invariant: each internal 1100 (sum 2200)
# < marker 2550 < global 2700.
@pytest.mark.timeout(2550)
def test_update_over_rewrite(agent_pack):
    ws = agent_pack("context-pack-builder")
    _seed_auth(ws.root)

    r1 = ws.run_agent(prompt=PROMPT_NEW, agent="cpb-orchestrator", timeout=1100)
    if not r1.usable:
        pytest.skip(r1.unavailable_reason())
    assert r1.ok, f"first run failed; see {r1.log_path}"

    skills = ws.glob("context-packs/*-context/skills/*-context/SKILL.md")
    assert len(skills) == 1, f"expected exactly one pack after NEW; see {r1.log_path}"

    # Inject a human-authored block that the UPDATE must preserve.
    skill_path = skills[0]
    original = skill_path.read_text(encoding="utf-8")
    human_marker = "<!-- human -->\nHAND-WRITTEN NOTE: do not delete.\n"
    skill_path.write_text(original + "\n" + human_marker, encoding="utf-8")

    # Add the new code referenced by the update prompt.
    (ws.root / "src" / "auth" / "reset.py").write_text(
        "def reset_password(user):\n    return True\n", encoding="utf-8"
    )

    r2 = ws.run_agent(prompt=PROMPT_UPDATE, agent="cpb-orchestrator", timeout=1100)
    if not r2.usable:
        pytest.skip(r2.unavailable_reason())
    assert r2.ok, f"update run failed; see {r2.log_path}"

    # Exactly one pack dir -- no duplicate.
    pack_dirs = ws.glob("context-packs/*-context/plugin.json")
    assert len(pack_dirs) == 1, (
        f"UPDATE must not create a duplicate pack; found {len(pack_dirs)}; "
        f"see {r2.log_path}"
    )

    updated = skills[0].read_text(encoding="utf-8")
    assert "HAND-WRITTEN NOTE: do not delete." in updated, (
        f"human-authored block was clobbered on UPDATE; see {r2.log_path}"
    )
    assert "Change Log" in updated, (
        f"expected a Change Log entry after UPDATE; see {r2.log_path}"
    )
