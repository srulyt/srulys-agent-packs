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
Build a context pack for the "billing" subsystem in this repository.
BOUNDED MODE (fast pass): keep this run cost-capped and single-pass.

Scope — confine discovery/analysis to EXACTLY the src/billing/ tree
listed below; do NOT scan the rest of the repository. The subsystem spans
several layers and many DISTINCT concepts (invoices, charges, refunds,
subscriptions, proration, taxes, dunning, payment methods, the ledger, and
webhooks). Document EACH distinct concept thoroughly across all five
content areas (entry points; file & folder locations per layer; glossary;
patterns & practices; architecture & design).

Because this subsystem has many distinct concepts, the generated SKILL.md
body will exceed the single-source token threshold and MUST be split into a
lean progressively-loading index plus references/ files. Produce the pack
in context-packs/ and run to completion.
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


# A compact, multi-LAYER fixture: a handful of SMALL files, but each carries a
# DISTINCT, well-documented billing concept so the synthesized SKILL.md has
# enough genuine material to cross SPLIT_THRESHOLD_TOKENS and force a split.
# (40 near-identical trivial modules were both slow to analyze and collapsed
# into a tiny pack that never split — distinct concepts, not bulk, drive the
# split.)
_CONCEPTS = [
    ("invoice", "Invoice", "Issues and finalizes customer invoices."),
    ("charge", "Charge", "Captures a payment charge against a payment method."),
    ("refund", "Refund", "Reverses a captured charge in full or part."),
    ("subscription", "Subscription", "Manages recurring billing cycles."),
    ("proration", "Proration", "Computes mid-cycle plan-change adjustments."),
    ("tax", "TaxEngine", "Resolves jurisdictional tax rates per line item."),
    ("dunning", "Dunning", "Retries failed charges and escalates past-due."),
    ("ledger", "Ledger", "Double-entry record of all billing movements."),
]


def _seed_layered_fixture(root: Path) -> None:
    base = root / "src" / "billing"
    for sub in ("controllers", "services", "models", "migrations", "tests"):
        (base / sub).mkdir(parents=True, exist_ok=True)
    for mod, cls, summary in _CONCEPTS:
        (base / "controllers" / f"{mod}_controller.py").write_text(
            f"# Entry point: HTTP controller for {mod}.\n"
            f"from ..services.{mod}_service import {cls}Service\n\n"
            f"def post_{mod}(request):\n"
            f'    """POST /{mod} — {summary}"""\n'
            f"    return {cls}Service().handle(request.body)\n",
            encoding="utf-8",
        )
        (base / "services" / f"{mod}_service.py").write_text(
            f"# Business layer for {mod}.\n"
            f"from ..models.{mod} import {cls}\n\n"
            f"class {cls}Service:\n"
            f'    """{summary} Coordinates the {mod} workflow and writes the ledger."""\n'
            f"    def handle(self, body):\n"
            f"        return {cls}(body).persist()\n",
            encoding="utf-8",
        )
        (base / "models" / f"{mod}.py").write_text(
            f"# Data layer for {mod}.\n"
            f"class {cls}:\n"
            f'    """{summary} Persisted {mod} row with status + amount fields."""\n'
            f"    def __init__(self, body):\n"
            f"        self.body = body\n"
            f"    def persist(self):\n"
            f"        return self\n",
            encoding="utf-8",
        )
        (base / "migrations" / f"create_{mod}.py").write_text(
            f"# Migration: create the {mod} table (id, status, amount, created_at).\n"
            f"def up():\n    create_table('{mod}')\n",
            encoding="utf-8",
        )
        (base / "tests" / f"test_{mod}.py").write_text(
            f"def test_{mod}_handle():\n    assert True  # {summary}\n",
            encoding="utf-8",
        )
    (base / "config.py").write_text(
        "# Config flags for billing.\n"
        "BILLING_FLAGS = {\n"
        + "".join(f"    'enable_{m}': True,\n" for m, _, _ in _CONCEPTS)
        + "}\n",
        encoding="utf-8",
    )
    (root / "docs").mkdir(parents=True, exist_ok=True)
    (root / "docs" / "billing.md").write_text(
        "# Billing subsystem\n\nConcepts: "
        + ", ".join(c[0] for c in _CONCEPTS)
        + ".\nEach has a controller (entry point), service (business), model "
        "(data), migration, and tests.\n",
        encoding="utf-8",
    )


@pytest.mark.pack
@pytest.mark.slow
# Ordering invariant: internal 2100 < marker 2400 < global 2700.
@pytest.mark.timeout(2400)
def test_progressive_disclosure_split(agent_pack):
    ws = agent_pack("context-pack-builder")
    _seed_layered_fixture(ws.root)

    result = ws.run_agent(prompt=PROMPT, agent="cpb-orchestrator", timeout=2100)
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
