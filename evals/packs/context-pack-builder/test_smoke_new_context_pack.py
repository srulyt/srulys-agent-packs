"""Happy-path smoke: a NEW context pack is produced from a small seed.

Seeds a tiny fixture feature into the workspace, runs the orchestrator, and
asserts a uniform pack dir with plugin.json, context-pack.json, and a
skills/<slug>-context/SKILL.md carrying the five content areas + confidence.
A judge then checks the content actually maps the seeded feature.
"""

from __future__ import annotations

from pathlib import Path

import pytest

PROMPT = """\
Build a context pack for the "checkout" feature in this repository.
Seed paths: src/checkout/service.py and src/checkout/routes.py.
The feature is the order checkout flow: it exposes a POST /checkout
route that calls CheckoutService.place_order, which validates the cart
and writes an Order row. Produce the pack in context-packs/. Run the
full pipeline to completion.
"""


def _seed_fixture(root: Path) -> None:
    (root / "src" / "checkout").mkdir(parents=True, exist_ok=True)
    (root / "src" / "checkout" / "service.py").write_text(
        "class CheckoutService:\n"
        "    def place_order(self, cart):\n"
        "        # validates the cart and writes an Order row\n"
        "        return Order(cart)\n",
        encoding="utf-8",
    )
    (root / "src" / "checkout" / "routes.py").write_text(
        "from .service import CheckoutService\n\n"
        "def post_checkout(request):\n"
        "    return CheckoutService().place_order(request.cart)\n",
        encoding="utf-8",
    )
    (root / "tests").mkdir(parents=True, exist_ok=True)
    (root / "tests" / "test_checkout.py").write_text(
        "def test_place_order():\n    assert True\n", encoding="utf-8"
    )


@pytest.mark.pack
@pytest.mark.slow
@pytest.mark.judge
def test_new_context_pack(agent_pack, judge):
    ws = agent_pack("context-pack-builder")
    _seed_fixture(ws.root)

    result = ws.run_agent(prompt=PROMPT, agent="cpb-orchestrator", timeout=900)
    if not result.usable:
        pytest.skip(result.unavailable_reason())
    assert result.ok, f"cpb-orchestrator invocation failed; see {result.log_path}"

    pack_jsons = ws.glob("context-packs/*-context/plugin.json")
    assert pack_jsons, f"expected a generated pack plugin.json; see {result.log_path}"
    meta = ws.glob("context-packs/*-context/context-pack.json")
    assert meta, f"expected context-pack.json; see {result.log_path}"
    skill_files = ws.glob("context-packs/*-context/skills/*-context/SKILL.md")
    assert skill_files, f"expected a generated SKILL.md; see {result.log_path}"

    skill = skill_files[0].read_text(encoding="utf-8")
    verdict = judge(
        artifact=skill,
        criteria=(
            "Score 1.0 only if this is a context-pack SKILL.md for a 'checkout' "
            "feature that covers ALL FIVE content areas (entry points; file & "
            "folder locations per layer; glossary; patterns & practices; "
            "architecture & design), shows a per-area confidence score (1-5) for "
            "each, and accurately reflects the seeded feature (a POST /checkout "
            "route calling CheckoutService.place_order that writes an Order). "
            "Score 0.5 if some areas or confidence scores are missing. Score 0.0 "
            "if it is not a coherent checkout context pack. Be strict."
        ),
        threshold=0.7,
    )
    assert verdict.passed, (
        f"context-pack judge failed (score={verdict.score:.2f}): "
        f"{verdict.reasoning}; see {result.log_path}"
    )
