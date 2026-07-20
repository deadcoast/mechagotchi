"""Cycle 19 I5b: occupancy saturation past ~62% — measured, not guessed.

The Phase-E remainder (narrowed by DR 0036's coverage jump) asks what
bounds coverage. The instruments, pre-registered:

- SUPPORT CEILING: distinct descriptor bins present in the evaluation
  population under the run's own edges — the hard upper bound on
  occupancy for ANY selection scheme over that population.
- IN-SAMPLE EDGES: the same population binned by edges derived from
  itself — the calibration lever's maximum.
- NOVELTY-FIRST POOL: the same evaluation budget drawn novelty-first
  from a larger generation pool — the generation-diversity lever
  (generation is cheap; scored evaluation is the budget, explicit).

The mutation-heavy arm is NAMED, not run: the constrained generator
exposes no temperature knob, and adding one is a generator change
with its own record — this lab only measures what exists.
"""

import json
import sys
import tempfile
import unittest
from pathlib import Path

LAB_DIR = Path(__file__).resolve().parent
if str(LAB_DIR) not in sys.path:
    sys.path.insert(0, str(LAB_DIR))

from occupancy_saturation import (  # noqa: E402
    build_occupancy_report,
    write_occupancy_artifacts,
)


class OccupancySaturationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # Small deterministic counts: the instruments' arithmetic and
        # honesty rules are the pins; the full-scale numbers live in
        # the committed artifact (H-01: never pin per-run scale).
        cls.report = build_occupancy_report(
            derivation_count=64,
            evaluation_count=96,
            pool_factor=2,
            rng_seed=41,
        )

    def test_support_ceiling_bounds_every_selection_arm(self):
        metrics = self.report["metrics"]
        support = metrics["support_ceiling"]["distinct_descriptors"]
        self.assertGreaterEqual(
            support, metrics["arms"]["baseline"]["occupied_niches"]
        )
        self.assertLessEqual(
            metrics["arms"]["novelty_pool"]["occupied_niches"],
            metrics["novelty_pool_support"]["distinct_descriptors"],
        )

    def test_every_arm_spends_the_same_evaluation_budget(self):
        for arm, summary in self.report["metrics"]["arms"].items():
            with self.subTest(arm=arm):
                self.assertEqual(96, summary["candidate_count"])

    def test_novelty_pool_is_larger_but_the_budget_is_not(self):
        novelty = self.report["metrics"]["novelty_pool_support"]
        self.assertEqual(192, novelty["pool_size"])
        self.assertGreaterEqual(
            novelty["distinct_descriptors"],
            self.report["metrics"]["support_ceiling"][
                "distinct_descriptors"
            ],
        )

    def test_the_levers_are_the_measured_differences(self):
        metrics = self.report["metrics"]
        base = metrics["arms"]["baseline"]["coverage"]
        self.assertAlmostEqual(
            metrics["levers"]["in_sample_edges"],
            round(
                metrics["arms"]["in_sample_edges"]["coverage"] - base, 6
            ),
            places=9,
        )
        self.assertAlmostEqual(
            metrics["levers"]["novelty_pool"],
            round(metrics["arms"]["novelty_pool"]["coverage"] - base, 6),
            places=9,
        )
        self.assertAlmostEqual(
            metrics["support_utilization"],
            round(
                metrics["arms"]["baseline"]["occupied_niches"]
                / metrics["support_ceiling"]["distinct_descriptors"],
                6,
            ),
            places=9,
        )

    def test_the_mutation_heavy_arm_stays_named_not_run(self):
        blocked = " ".join(self.report["blocked_states"])
        self.assertIn("mutation", blocked)

    def test_artifacts_are_written(self):
        with tempfile.TemporaryDirectory() as tmp:
            write_occupancy_artifacts(Path(tmp), self.report)
            payload = json.loads(
                (
                    Path(tmp) / "occupancy_saturation_stage0.json"
                ).read_text(encoding="utf-8")
            )
        self.assertEqual(
            "occupancy_saturation_stage0", payload["artifact_id"]
        )
        self.assertIn("decision", payload)


if __name__ == "__main__":
    unittest.main()
