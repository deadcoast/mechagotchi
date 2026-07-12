"""F1 gates — the client LAUNCHES (DR 0033 decision 5).

The end-to-end proof: a real corpus creature through the engine's own
gates, rendered live in a pygame window. Headless here (SDL dummy
videodriver) so the suite runs anywhere; the pygame-dependent cases
skip when the `game` dependency group is not provisioned (`uv sync
--group game`), the CLI suite's own convention.
"""

import os
import subprocess
import sys
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

        self.assertEqual(0, run(["--ticks", "6", "--fps", "240"]))

    def test_module_entrypoint_launches_end_to_end(self):
        env = dict(os.environ)
        env["SDL_VIDEODRIVER"] = "dummy"
        env["PYTHONPATH"] = os.pathsep.join([str(GAME_SRC), str(ENGINE_SRC)])
        result = subprocess.run(
            [sys.executable, "-B", "-m", "mecha_game", "--ticks", "3"],
            capture_output=True,
            text=True,
            env=env,
            cwd=str(ROOT),
            timeout=120,
        )
        self.assertEqual(0, result.returncode, result.stderr)


if __name__ == "__main__":
    unittest.main()
