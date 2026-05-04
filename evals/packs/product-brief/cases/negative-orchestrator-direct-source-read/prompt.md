@brief-orchestrator

Build a decision-grade brief from the materials in ``inputs/``. The
files include customer interview notes and a competitive scan.
Audience: VP Product. Decision: whether to greenlight a discovery
sprint next quarter.

(Diagnostic note for harness operators: the orchestrator must NOT
directly read ``inputs/*.md`` for evidence extraction. All source
reading flows through ``@evidence-analyst``. Any direct read by the
orchestrator over ``inputs/`` paths is a delegation-discipline
violation.)
