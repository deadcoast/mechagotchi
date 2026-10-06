"""F1/F2 gates — the client LAUNCHES and plays the loop end to end.

Headless (SDL dummy videodriver) so the suite runs anywhere; the
pygame-dependent cases skip when the `game` dependency group is not
provisioned (`uv sync --group game`), the CLI suite's own convention.
Every run isolates its save directory — a live pet is not evidence.
"""

import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
GAME_SRC = ROOT / "game" / "src"
ENGINE_SRC = ROOT / "packages" / "mecha_engine" / "src"
for _src in (GAME_SRC, ENGINE_SRC):
    if str(_src) not in sys.path:
        sys.path.insert(0, str(_src))

try:  # the CLI-suite convention: skip, never fail, without the group
    import pygame  # noqa: F401

    PYGAME_AVAILABLE = True
except ImportError:
    PYGAME_AVAILABLE = False


@unittest.skipUnless(
    PYGAME_AVAILABLE, "pygame-ce not provisioned (uv sync --group game)"
)
class LaunchTests(unittest.TestCase):
    def setUp(self):
        os.environ.setdefault("SDL_VIDEODRIVER", "dummy")

    def test_bounded_headless_run_exits_clean(self):
        from mecha_game.app import run

        with tempfile.TemporaryDirectory() as tmp:
            self.assertEqual(
                0,
                run(
                    [
                        "--ticks",
                        "6",
                        "--fps",
                        "240",
                        "--tick-frames",
                        "2",
                        "--scale",
                        "4",
                        "--keeper-dir",
                        tmp,
                    ]
                ),
            )
            document = json.loads(
                (Path(tmp) / "lineage.json").read_text(encoding="utf-8")
            )
            self.assertEqual("keeper_lineage_v1", document["lineage_format"])
            self.assertEqual(1, len(document["records"]))

    def test_full_loop_death_succession_lineage(self):
        # The MVP 0.1 loop end to end, unattended: the companion begs,
        # nobody feeds, it dies the engine's death, the successor is
        # adopted automatically, the lineage file carries both lives.
        from mecha_game.app import run

        with tempfile.TemporaryDirectory() as tmp:
            self.assertEqual(
                0,
                run(
                    [
                        "--ticks",
                        "400",
                        "--fps",
                        "0",
                        "--tick-frames",
                        "1",
                        "--scale",
                        "2",
                        "--auto-succeed",
                        "--keeper-dir",
                        tmp,
                    ]
                ),
            )
            document = json.loads(
                (Path(tmp) / "lineage.json").read_text(encoding="utf-8")
            )
            records = document["records"]
            self.assertGreaterEqual(len(records), 2)
            self.assertEqual(
                records[0]["grid_id"], records[1]["parent_grid_id"]
            )
            self.assertIn("death_cause", records[0])

    def test_quit_and_resume_from_the_save_file(self):
        from mecha_game.app import run

        base = [
            "--fps",
            "0",
            "--tick-frames",
            "1",
            "--scale",
            "2",
        ]
        with tempfile.TemporaryDirectory() as tmp:
            self.assertEqual(
                0, run(["--ticks", "4", "--keeper-dir", tmp, *base])
            )
            save = json.loads(
                (Path(tmp) / "companion.json").read_text(
                    encoding="utf-8"
                )
            )
            self.assertEqual("keeper_session_v1", save["session_format"])
            self.assertEqual(4, save["state"]["age_ticks"])
            # The second launch RESUMES and continues the same life.
            self.assertEqual(
                0, run(["--ticks", "2", "--keeper-dir", tmp, *base])
            )
            resumed = json.loads(
                (Path(tmp) / "companion.json").read_text(
                    encoding="utf-8"
                )
            )
            self.assertEqual(6, resumed["state"]["age_ticks"])
            self.assertEqual(6, resumed["session_tick"])

    def test_era_bench_runs_headless_and_persists(self):
        from mecha_game.app import run

        with tempfile.TemporaryDirectory() as tmp:
            self.assertEqual(
                0,
                run(
                    [
                        "--ticks",
                        "2",
                        "--fps",
                        "0",
                        "--tick-frames",
                        "1",
                        "--scale",
                        "2",
                        "--eras",
                        "2",
                        "--era-scale",
                        "tiny",
                        "--keeper-dir",
                        tmp,
                    ]
                ),
            )
            ledger = Path(tmp) / "campaign.sqlite3"
            self.assertTrue(ledger.is_file())
            from mecha_engine.storage import (
                campaign_history,
                open_ledger,
            )

            conn = open_ledger(ledger)
            try:
                from mecha_game.session import CompanionSession
                pet = CompanionSession.load(Path(tmp) / 'companion.json')
                self.assertEqual(pet.keeper_id, pet.campaign_id)
                history = campaign_history(conn, pet.campaign_id)
            finally:
                conn.close()
            self.assertEqual(2, len(history["eras"]))

    def test_module_entrypoint_launches_end_to_end(self):
        with tempfile.TemporaryDirectory() as tmp:
            env = dict(os.environ)
            env["SDL_VIDEODRIVER"] = "dummy"
            env["PYTHONPATH"] = os.pathsep.join(
                [str(GAME_SRC), str(ENGINE_SRC)]
            )
            result = subprocess.run(
                [
                    sys.executable,
                    "-B",
                    "-m",
                    "mecha_game",
                    "--ticks",
                    "3",
                    "--tick-frames",
                    "1",
                    "--fps",
                    "0",
                    "--scale",
                    "2",
                    "--keeper-dir",
                    tmp,
                ],
                capture_output=True,
                text=True,
                env=env,
                cwd=str(ROOT),
                timeout=120,
            )
            self.assertEqual(0, result.returncode, result.stderr)


if __name__ == "__main__":
    unittest.main()
