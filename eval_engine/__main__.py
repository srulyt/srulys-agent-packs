"""Allow ``python -m eval_engine ...`` as a synonym for
``python -m eval_engine.harness.run ...``.

The handoff prompt's acceptance test runs::

    python -m eval_engine run-pack copilot-factory --results-out /tmp/results.json

The factory's ``@factory-eval-runner`` agent uses the longer module
path. Both must work.
"""

from __future__ import annotations

import sys

from eval_engine.harness.run import main


if __name__ == "__main__":
    sys.exit(main())
