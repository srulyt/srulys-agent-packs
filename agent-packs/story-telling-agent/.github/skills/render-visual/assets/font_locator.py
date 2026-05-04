"""font_locator.py — single source of truth for the bundled fallback font.

Per architecture critic concern C3: instead of duplicating
DejaVuSans.ttf across two skills (pptx-structural-asserts and
render-visual), every consumer resolves the font via this helper.

Resolution order:
  1. Sibling asset: ``render-visual/assets/DejaVuSans.ttf`` (canonical
     bundled location — when actually committed).
  2. matplotlib's bundled DejaVuSans.ttf (always present when
     matplotlib is installed; ships under the same Bitstream Vera /
     DejaVu permissive license).
  3. PIL ImageFont.load_default() (last-resort bitmap font).

Returns either an absolute path string (cases 1 and 2) or ``None``
(case 3 — caller falls back to ``ImageFont.load_default()``).
"""
from __future__ import annotations

from pathlib import Path

CANONICAL = Path(__file__).resolve().parent / "DejaVuSans.ttf"


def find_dejavu_sans() -> str | None:
    """Return absolute path to a usable DejaVuSans.ttf, or None.

    None means the caller should fall back to PIL's bitmap default
    font (``ImageFont.load_default()``). Pixel-accuracy will degrade
    but the script will not crash on hosts missing both bundled and
    matplotlib fonts.
    """
    if CANONICAL.is_file():
        return str(CANONICAL)
    # Try matplotlib's bundled copy — present whenever matplotlib is
    # available, which is a transitive dep of the render-visual skill.
    try:
        import matplotlib  # type: ignore

        mpl_data = Path(matplotlib.get_data_path()) / "fonts" / "ttf" / "DejaVuSans.ttf"
        if mpl_data.is_file():
            return str(mpl_data)
    except ImportError:
        pass
    return None


if __name__ == "__main__":  # pragma: no cover
    import sys

    p = find_dejavu_sans()
    print(p or "<not-found>")
    sys.exit(0 if p else 1)
