"""The fleet's public surface (cycle 14 F3b — the game is the consumer).

Phase D promoted the thread fleet into ``learning.threads`` (verbatim
port, cycle 12 D1–D4) and wired it through ``decide``'s additive seam;
the Phase-D gate named the GAME as where the kept threads' value
cashes out. This pins the additive export that lets that consumer
reach the fleet through the public surface — and the load-bearing
opt-in rule: without an explicit ``learning_switches[name] is True``
the fleet is silent, so every frozen path stays byte-identical.

Import mechanics match ``tests/test_package_imports.py``: probes run
in a ``python -B -c`` subprocess whose PYTHONPATH points at this
package's own ``src`` directory; this module never mutates the
interpreter module search path and never points the subprocess at
research lab directories.
"""

import json
import os
import subprocess
import sys
import unittest
from pathlib import Path

PACKAGE_ROOT = Path(__file__).resolve().parents[1]
SRC_DIR = PACKAGE_ROOT / "src"

PROBE = """
import json
from mecha_engine.learning import (
    FLEET_THREAD_NAMES,
    fleet_signals,
    observe_fleet,
)

calm = {"hunger": 0.5, "energy": 0.5, "stress": 0.0}
silent_observe = observe_fleet(calm)
silent_signals = fleet_signals(calm)

opted = dict(calm)
opted["learning_switches"] = {"hunger_forecast": True}
observed = observe_fleet(opted)
opted["thread_states"] = observed
signals = fleet_signals(opted)

print(json.dumps({
    "names": FLEET_THREAD_NAMES,
    "silent_observe": silent_observe,
    "silent_signals": silent_signals,
    "opted_observed": sorted(observed),
    "opted_signal_names": [signal["name"] for signal in signals],
}))
"""


def _probe() -> dict:
    env = dict(os.environ)
    env["PYTHONPATH"] = str(SRC_DIR)
    result = subprocess.run(
        [sys.executable, "-B", "-c", PROBE],
        capture_output=True,
        text=True,
        env=env,
        cwd=str(PACKAGE_ROOT),
        timeout=120,
    )
    if result.returncode != 0:
        raise AssertionError(
            "fleet surface probe failed: " + result.stderr
        )
    return json.loads(result.stdout)


class FleetSurfaceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.report = _probe()

    def test_the_documented_fleet_is_named(self):
        names = self.report["names"]
        self.assertIn("hunger_forecast", names)
        self.assertIn("animation_bandit", names)
        self.assertIn("hidden_mood_hmm", names)
        self.assertEqual(11, len(names))

    def test_without_opt_in_the_fleet_is_silent(self):
        self.assertEqual({}, self.report["silent_observe"])
        self.assertEqual([], self.report["silent_signals"])

    def test_opted_in_threads_run_and_only_those(self):
        self.assertEqual(
            ["hunger_forecast"], self.report["opted_observed"]
        )
        self.assertEqual(
            ["hunger_forecast"], self.report["opted_signal_names"]
        )


if __name__ == "__main__":
    unittest.main()
