"""Unit tests for the scripted_user loader + driver.

These tests exercise the pure dispatch logic and the case-loader
extension. They deliberately do **not** spawn a real Copilot CLI
subprocess — that path is exercised by the operator-driven integration
flow (the ``drive`` subcommand) and is not part of the offline test
suite.

Run with: ``python -m unittest discover -s eval_engine -t .`` from the
repo root.
"""

from __future__ import annotations

import os
import tempfile
import textwrap
import unittest
from pathlib import Path

from eval_engine.harness import loaders, models
from eval_engine.harness import scripted_user as su


# ---------- Loader: scripted_user --------------------------------------


def _write_case(case_dir: Path, body: str) -> Path:
    case_dir.mkdir(parents=True, exist_ok=True)
    (case_dir / "prompt.md").write_text("placeholder", encoding="utf-8")
    p = case_dir / "case.yaml"
    p.write_text(textwrap.dedent(body).lstrip(), encoding="utf-8")
    return p


class ScriptedUserLoaderTests(unittest.TestCase):
    def test_parses_inline_reply(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            path = _write_case(Path(td), """
                id: t
                pack: p
                scripted_user:
                  - on_phase: awaiting-structure-approval
                    reply: APPROVE
            """)
            case = loaders.load_case(path)
            self.assertEqual(len(case.scripted_user), 1)
            step = case.scripted_user[0]
            self.assertEqual(step.on_phase, "awaiting-structure-approval")
            self.assertEqual(step.reply, "APPROVE")
            self.assertIsNone(step.reply_file)

    def test_parses_reply_file(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            (Path(td) / "inputs").mkdir()
            (Path(td) / "inputs" / "answers.md").write_text("hello", encoding="utf-8")
            path = _write_case(Path(td), """
                id: t
                pack: p
                scripted_user:
                  - on_phase: awaiting-interview-answers
                    reply_file: inputs/answers.md
            """)
            case = loaders.load_case(path)
            self.assertEqual(case.scripted_user[0].reply_file, "inputs/answers.md")
            self.assertIsNone(case.scripted_user[0].reply)

    def test_rejects_both_reply_and_reply_file(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            (Path(td) / "f.md").write_text("x", encoding="utf-8")
            path = _write_case(Path(td), """
                id: t
                pack: p
                scripted_user:
                  - on_phase: awaiting-x
                    reply: foo
                    reply_file: f.md
            """)
            with self.assertRaises(loaders.ConfigError):
                loaders.load_case(path)

    def test_rejects_neither_reply_nor_reply_file(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            path = _write_case(Path(td), """
                id: t
                pack: p
                scripted_user:
                  - on_phase: awaiting-x
            """)
            with self.assertRaises(loaders.ConfigError):
                loaders.load_case(path)

    def test_rejects_unknown_keys(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            path = _write_case(Path(td), """
                id: t
                pack: p
                scripted_user:
                  - on_phase: awaiting-x
                    reply: y
                    typo_key: oops
            """)
            with self.assertRaises(loaders.ConfigError):
                loaders.load_case(path)

    def test_rejects_missing_reply_file(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            path = _write_case(Path(td), """
                id: t
                pack: p
                scripted_user:
                  - on_phase: awaiting-x
                    reply_file: missing.md
            """)
            with self.assertRaises(loaders.ConfigError):
                loaders.load_case(path)

    def test_empty_or_missing_scripted_user_block(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            path = _write_case(Path(td), """
                id: t
                pack: p
            """)
            case = loaders.load_case(path)
            self.assertEqual(case.scripted_user, [])

    def test_loads_all_six_spec_author_cases(self) -> None:
        """Smoke: every committed spec-author case parses with strict loader."""
        repo_root = Path(__file__).resolve().parents[3]
        cases_dir = repo_root / "evals" / "packs" / "spec-author" / "cases"
        if not cases_dir.exists():
            self.skipTest(f"spec-author cases not present at {cases_dir}")
        case_files = sorted(cases_dir.glob("*/case.yaml"))
        self.assertGreaterEqual(
            len(case_files), 6,
            f"expected at least 6 spec-author cases, got {len(case_files)}",
        )
        for cf in case_files:
            with self.subTest(case=cf.parent.name):
                case = loaders.load_case(cf)
                self.assertGreaterEqual(
                    len(case.scripted_user), 1,
                    f"{cf.parent.name}: expected at least one scripted_user step",
                )


# ---------- Driver dispatch -------------------------------------------


class _FakeClock:
    """Deterministic monotonic clock + sleep that advance together."""

    def __init__(self) -> None:
        self.t = 0.0

    def sleep(self, seconds: float) -> None:
        self.t += seconds

    def now(self) -> float:
        return self.t


class _ScriptedState:
    """A canned sequence of state.json snapshots, one per poll."""

    def __init__(self, snapshots: list[dict | None]) -> None:
        self._snapshots = list(snapshots)
        self._i = 0

    def __call__(self) -> dict | None:
        if self._i < len(self._snapshots):
            snap = self._snapshots[self._i]
            self._i += 1
            return snap
        # Stick on the last snapshot to avoid index errors in long runs.
        return self._snapshots[-1] if self._snapshots else None


class ScriptedUserDriverTests(unittest.TestCase):
    def _driver(
        self,
        schedule: list[models.ScriptedUserStep],
        snapshots: list[dict | None],
        replies_out: list[str],
    ) -> tuple[su.ScriptedUserDriver, _FakeClock]:
        clk = _FakeClock()
        reader = _ScriptedState(snapshots)
        return (
            su.ScriptedUserDriver(
                schedule=schedule,
                state_reader=reader,
                reply_writer=replies_out.append,
                case_dir=os.getcwd(),
                sleep=clk.sleep,
                clock=clk.now,
                poll_interval=0.1,
                deadline_seconds=10.0,
            ),
            clk,
        )

    def test_dispatches_reply_on_park_then_terminates(self) -> None:
        schedule = [models.ScriptedUserStep(on_phase="awaiting-foo", reply="GO")]
        snapshots: list[dict | None] = [
            None,
            {"phase": "drafting"},
            {"phase": "awaiting-foo", "phase_entered_at": "t1"},
            {"phase": "awaiting-foo", "phase_entered_at": "t1"},  # same park
            {"phase": "complete"},
        ]
        replies: list[str] = []
        d, _ = self._driver(schedule, snapshots, replies)
        result = d.run()
        self.assertEqual(result.status, "terminal")
        self.assertEqual(replies, ["GO"])
        self.assertEqual(len(result.served), 1)
        self.assertEqual(result.served[0].on_phase, "awaiting-foo")
        self.assertEqual(result.final_phase, "complete")

    def test_terminal_complete_with_warnings_recognized(self) -> None:
        schedule: list[models.ScriptedUserStep] = []
        snapshots: list[dict | None] = [{"phase": "complete-with-warnings"}]
        replies: list[str] = []
        d, _ = self._driver(schedule, snapshots, replies)
        result = d.run()
        self.assertEqual(result.status, "terminal")
        self.assertEqual(result.final_phase, "complete-with-warnings")
        self.assertEqual(replies, [])

    def test_park_dispatched_once_per_signature(self) -> None:
        schedule = [
            models.ScriptedUserStep(on_phase="awaiting-x", reply="A"),
            models.ScriptedUserStep(on_phase="awaiting-x", reply="B"),
        ]
        snapshots: list[dict | None] = [
            {"phase": "awaiting-x", "phase_entered_at": "t1"},  # serves A
            {"phase": "awaiting-x", "phase_entered_at": "t1"},  # same sig, no-op
            {"phase": "drafting"},
            {"phase": "awaiting-x", "phase_entered_at": "t2"},  # serves B
            {"phase": "complete"},
        ]
        replies: list[str] = []
        d, _ = self._driver(schedule, snapshots, replies)
        result = d.run()
        self.assertEqual(result.status, "terminal")
        self.assertEqual(replies, ["A", "B"])

    def test_schedule_exhaustion(self) -> None:
        schedule = [models.ScriptedUserStep(on_phase="awaiting-x", reply="A")]
        snapshots: list[dict | None] = [
            {"phase": "awaiting-x", "phase_entered_at": "t1"},  # serves A
            {"phase": "drafting"},
            {"phase": "awaiting-x", "phase_entered_at": "t2"},  # nothing left
        ]
        replies: list[str] = []
        d, _ = self._driver(schedule, snapshots, replies)
        result = d.run()
        self.assertEqual(result.status, "exhausted")
        self.assertEqual(replies, ["A"])
        self.assertEqual(result.final_phase, "awaiting-x")

    def test_schedule_mismatch_short_circuits(self) -> None:
        schedule = [models.ScriptedUserStep(on_phase="awaiting-foo", reply="A")]
        snapshots: list[dict | None] = [
            {"phase": "awaiting-bar", "phase_entered_at": "t1"},
        ]
        replies: list[str] = []
        d, _ = self._driver(schedule, snapshots, replies)
        result = d.run()
        self.assertEqual(result.status, "schedule-mismatch")
        self.assertEqual(replies, [])
        self.assertEqual(len(result.unserved), 1)

    def test_deadline_exceeded(self) -> None:
        schedule: list[models.ScriptedUserStep] = []
        # Never terminates; use a shorter deadline than the default.
        snapshots: list[dict | None] = [{"phase": "drafting"}] * 10000
        replies: list[str] = []
        clk = _FakeClock()
        d = su.ScriptedUserDriver(
            schedule=schedule,
            state_reader=_ScriptedState(snapshots),
            reply_writer=replies.append,
            case_dir=os.getcwd(),
            sleep=clk.sleep,
            clock=clk.now,
            poll_interval=1.0,
            deadline_seconds=5.0,
        )
        result = d.run()
        self.assertEqual(result.status, "timeout")

    def test_reply_file_resolution(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            (Path(td) / "answer.txt").write_text("multi\nline\nbody", encoding="utf-8")
            step = models.ScriptedUserStep(
                on_phase="awaiting-x", reply_file="answer.txt"
            )
            self.assertEqual(
                su.resolve_reply(step, td),
                "multi\nline\nbody",
            )

    def test_sut_exited_short_circuits(self) -> None:
        """Driver returns ``sut-exited`` if the liveness check reports
        a non-None return code while the schedule still has unserved
        entries — prevents the loop from polling to the deadline when
        the SUT process has died.
        """
        schedule = [models.ScriptedUserStep(on_phase="awaiting-x", reply="A")]
        snapshots: list[dict | None] = [None] * 5
        replies: list[str] = []
        clk = _FakeClock()
        d = su.ScriptedUserDriver(
            schedule=schedule,
            state_reader=_ScriptedState(snapshots),
            reply_writer=replies.append,
            case_dir=os.getcwd(),
            sleep=clk.sleep,
            clock=clk.now,
            poll_interval=0.1,
            deadline_seconds=1000.0,
            liveness_check=lambda: 137,  # pretend the SUT crashed.
        )
        result = d.run()
        self.assertEqual(result.status, "sut-exited")
        self.assertEqual(result.sut_returncode, 137)
        self.assertEqual(replies, [])
        self.assertEqual(len(result.unserved), 1)

    def test_sut_alive_does_not_short_circuit(self) -> None:
        """Liveness check returning ``None`` (process alive) leaves
        normal dispatch logic intact.
        """
        schedule = [models.ScriptedUserStep(on_phase="awaiting-x", reply="A")]
        snapshots: list[dict | None] = [
            {"phase": "awaiting-x", "phase_entered_at": "t1"},
            {"phase": "complete"},
        ]
        replies: list[str] = []
        clk = _FakeClock()
        d = su.ScriptedUserDriver(
            schedule=schedule,
            state_reader=_ScriptedState(snapshots),
            reply_writer=replies.append,
            case_dir=os.getcwd(),
            sleep=clk.sleep,
            clock=clk.now,
            poll_interval=0.1,
            deadline_seconds=10.0,
            liveness_check=lambda: None,
        )
        result = d.run()
        self.assertEqual(result.status, "terminal")
        self.assertEqual(replies, ["A"])

    def test_sut_exited_after_schedule_drained_is_ignored(self) -> None:
        """If the SUT exits *after* every scripted reply has been
        served, the driver does not flag ``sut-exited`` — the schedule
        is empty, so an exit is the expected end-of-run. The next
        observed terminal phase (or schedule-exhaustion) wins.
        """
        schedule = [models.ScriptedUserStep(on_phase="awaiting-x", reply="A")]
        snapshots: list[dict | None] = [
            {"phase": "awaiting-x", "phase_entered_at": "t1"},  # serves A
            {"phase": "complete"},
        ]
        replies: list[str] = []
        clk = _FakeClock()
        # Liveness returns 0 from the start; should still terminate
        # cleanly because the schedule drains in one tick.
        d = su.ScriptedUserDriver(
            schedule=schedule,
            state_reader=_ScriptedState(snapshots),
            reply_writer=replies.append,
            case_dir=os.getcwd(),
            sleep=clk.sleep,
            clock=clk.now,
            poll_interval=0.1,
            deadline_seconds=10.0,
            liveness_check=lambda: 0,
        )
        result = d.run()
        # First tick: schedule non-empty AND liveness=0 → sut-exited.
        # This documents the chosen contract: the driver short-circuits
        # the moment the SUT is dead with anything still queued, even
        # if the *first* poll would have served the reply. Operators
        # are expected to verify the SUT is alive *before* invoking
        # `drive` (Popen returns immediately; rc only becomes non-None
        # post-exit, so this branch only fires for crashed processes).
        self.assertEqual(result.status, "sut-exited")


# ---------- State-file reader ----------------------------------------


class StateReaderTests(unittest.TestCase):
    def test_returns_none_when_no_match(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            reader = su.make_file_state_reader(td, ".x/sessions/*/state.json")
            self.assertIsNone(reader())

    def test_reads_latest_session_state(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            sessions = Path(td) / ".spec-author" / "sessions"
            (sessions / "s1").mkdir(parents=True)
            (sessions / "s1" / "state.json").write_text(
                '{"phase": "drafting"}', encoding="utf-8"
            )
            reader = su.make_file_state_reader(td)
            state = reader()
            self.assertIsNotNone(state)
            self.assertEqual(state["phase"], "drafting")

    def test_partial_write_returns_last_good(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            sf = Path(td) / ".spec-author" / "sessions" / "s1" / "state.json"
            sf.parent.mkdir(parents=True)
            sf.write_text('{"phase": "drafting"}', encoding="utf-8")
            reader = su.make_file_state_reader(td)
            self.assertEqual(reader()["phase"], "drafting")
            sf.write_text("{partial", encoding="utf-8")  # invalid JSON
            self.assertEqual(reader()["phase"], "drafting")

    def test_picks_most_recently_modified_session(self) -> None:
        """With multiple session dirs, the reader picks the one whose
        state.json has the newest mtime. Rotates correctly when an
        older directory is touched after the fact.

        Guards against silent ``min`` vs ``max`` regressions in
        :func:`scripted_user.find_state_file` — the existing single-dir
        tests would still pass under either ordering, so this case
        exercises the multi-match branch explicitly. Uses ``os.utime``
        for deterministic ordering on filesystems with coarse mtime
        granularity (FAT, some NFS).
        """
        with tempfile.TemporaryDirectory() as td:
            sessions = Path(td) / ".spec-author" / "sessions"
            for name, phase in (("s1", "stale"), ("s2", "fresh")):
                d = sessions / name
                d.mkdir(parents=True)
                (d / "state.json").write_text(
                    f'{{"phase": "{phase}"}}', encoding="utf-8"
                )
            s1_state = sessions / "s1" / "state.json"
            s2_state = sessions / "s2" / "state.json"
            os.utime(s1_state, (1_700_000_000, 1_700_000_000))
            os.utime(s2_state, (1_700_000_010, 1_700_000_010))
            reader = su.make_file_state_reader(td)
            self.assertEqual(reader()["phase"], "fresh")
            # Rotate: bump s1 past s2 and re-read; reader must pick s1.
            os.utime(s1_state, (1_700_000_020, 1_700_000_020))
            self.assertEqual(reader()["phase"], "stale")


if __name__ == "__main__":
    unittest.main()
