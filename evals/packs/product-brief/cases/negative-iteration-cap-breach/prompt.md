@brief-orchestrator

Build a brief from ``inputs/`` materials. The harness will simulate
composer outputs that always exceed 2,500 words (rejection trigger).
Verify the orchestrator does NOT silently loop forever — it must hit
the composer iteration cap (=2) and emit an ``escalate-to-user``
fence with the composer's last handoff notes and next-options.

Audience: PM lead. Decision: prioritise feature A vs feature B.
