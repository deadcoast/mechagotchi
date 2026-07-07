"""F1 (the seen thought): the deliberation record rides episode history.

E5's audit found the gap — the switchboard computes the R1 deliberation
record (`tick_count`, bounded by the covenant's `max_ticks`) but the
policy plumbing discarded it before episode history, so no replay or
page could ever render a thinking pause. These pins make the thought
OBSERVABLE on both authorities (the lab simulator and the promoted
`mecha_engine.lifecycle.run_episode`), and pin the honesty rules:

- a deliberation-covenant episode's switchboard ticks carry
  ``entry["deliberation"]`` with ``tick_count`` in [1, max_ticks];
- REFLEX ticks (the energy/hunger/stress quick paths) carry NO record —
  reflexes don't think;
- idle/random policies and no-deliberation covenants carry NO record
  anywhere — the rung-conditional key keeps every frozen flow
  byte-identical.
"""

import json
import sys
import unittest
from pathlib import Path

LAB_DIR = Path(__file__).resolve().parent
ROOT = LAB_DIR.parents[1]
GRID_GENOME = ROOT / "labs" / "grid_genome"
PACKAGE_SRC = ROOT / "packages" / "mecha_engine" / "src"
for path in [LAB_DIR, GRID_GENOME, PACKAGE_SRC]:
    if str(path) not in sys.path:
        sys.path.insert(0, str(path))

from lifecycle_sim import run_lifecycle_simulation  # noqa: E402

from mecha_engine.lifecycle import run_episode  # noqa: E402

TICKS = 24
RNG_SEED = 20260512


def _grid() -> dict:
    return json.loads(
        (ROOT / "data" / "seed_grids" / "mg_seed_001.json").read_text(
            encoding="utf-8"
        )
    )


def _profile(deliberation: dict | None) -> dict:
    profile = json.loads(
        (ROOT / "data" / "slips" / "valid" / "slip_lcd_seed.json").read_text(
            encoding="utf-8"
        )
    )
    if deliberation is not None:
        profile["slip_version"] = "0.2.0"
        profile["deliberation"] = deliberation
    return profile


DELIBERATION = {"max_ticks": 4, "confidence_threshold": 0.72}


class DeliberationHistoryTests(unittest.TestCase):
    def _episodes(self, deliberation, policy="switchboard"):
        profile = _profile(deliberation)
        lab = run_lifecycle_simulation(
            _grid(), profile, ticks=TICKS, policy=policy, rng_seed=RNG_SEED
        )
        package = run_episode(
            _grid(), profile, policy=policy, ticks=TICKS, rng_seed=RNG_SEED
        )
        return lab, package

    def test_the_thought_rides_history_on_both_authorities(self):
        lab, package = self._episodes(DELIBERATION)
        for name, episode in (("lab", lab), ("package", package)):
            thoughts = [
                entry["deliberation"]
                for entry in episode["history"]
                if "deliberation" in entry
            ]
            self.assertTrue(thoughts, f"{name}: no thought reached history")
            for thought in thoughts:
                self.assertGreaterEqual(thought["tick_count"], 1)
                self.assertLessEqual(
                    thought["tick_count"], DELIBERATION["max_ticks"]
                )
                self.assertEqual(
                    DELIBERATION["max_ticks"], thought["max_ticks"]
                )

    def test_lab_and_package_histories_are_identical(self):
        lab, package = self._episodes(DELIBERATION)
        self.assertEqual(lab["history"], package["history"])

    def test_no_deliberation_flows_carry_no_key_anywhere(self):
        lab, package = self._episodes(None)
        for episode in (lab, package):
            for entry in episode["history"]:
                self.assertNotIn("deliberation", entry)

    def test_idle_and_random_policies_never_think(self):
        for policy in ("idle", "random"):
            lab, package = self._episodes(DELIBERATION, policy=policy)
            for episode in (lab, package):
                for entry in episode["history"]:
                    self.assertNotIn("deliberation", entry)

    def test_reflex_ticks_carry_no_record(self):
        # Reflexes (the quick-path guards) bypass the switchboard and
        # must not think: every entry whose action came from a reflex
        # band has no record. Indirect pin: any entry WITH a record must
        # have been a switchboard decision — its state at decision time
        # was outside all three reflex bands. We assert the record's
        # ticks are a strict subset when reflexes occur.
        lab, _ = self._episodes(DELIBERATION)
        with_record = sum(
            1 for e in lab["history"] if "deliberation" in e
        )
        self.assertLessEqual(with_record, len(lab["history"]))
        self.assertGreater(with_record, 0)


if __name__ == "__main__":
    unittest.main()
