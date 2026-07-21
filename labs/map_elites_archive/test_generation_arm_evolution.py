"""K2 (DR 0042): the generation layer revisited in the loop.

Pins the additive `generation` arm on the E3 loop (WFC default
byte-identical, the constrained arm the promoted evolve inner loop
verbatim, unknown arms refused loudly, twin-run determinism, the
elite role-texture observation) and the K2 comparison report's shape,
rule application, and artifacts — DR 0040's arm pattern applied to
DR 0031's revisit, judged at the consumer.
"""

import json
import sys
import tempfile
import unittest
from pathlib import Path

LAB_DIR = Path(__file__).resolve().parent
if str(LAB_DIR) not in sys.path:
    sys.path.insert(0, str(LAB_DIR))

from evaluation_loop_scale import run_evaluation_loop  # noqa: E402

from generation_arm_evolution import (  # noqa: E402
    ARTIFACT_ID,
    build_generation_arm_report,
    write_generation_arm_artifacts,
)

TINY = dict(population=16, target_evaluations=64, rng_seed=31)


class GenerationArmTests(unittest.TestCase):
    def test_the_default_is_the_adopted_constrained_arm(self):
        # DR 0042 (adopted on the measured verdict): constrained is the
        # loop's generation default; naming it changes nothing.
        implicit = run_evaluation_loop(**TINY)
        explicit = run_evaluation_loop(generation="constrained", **TINY)
        self.assertEqual("constrained", implicit["generation"])
        self.assertEqual(implicit, explicit)

    def test_the_wfc_incumbent_stays_runnable_and_deterministic(self):
        # DR 0042 clause 4: the losing arm stays runnable, its path
        # untouched — twin runs byte-equal.
        first = run_evaluation_loop(generation="wfc", **TINY)
        second = run_evaluation_loop(generation="wfc", **TINY)
        self.assertEqual("wfc", first["generation"])
        self.assertEqual(first, second)

    def test_the_constrained_arm_runs_the_promoted_inner_loop(self):
        result = run_evaluation_loop(generation="constrained", **TINY)
        self.assertEqual("constrained", result["generation"])
        self.assertGreaterEqual(
            result["evaluations_total"], TINY["target_evaluations"]
        )
        self.assertGreaterEqual(
            result["archive_summary"]["occupied_niches"], 1
        )

    def test_unknown_generation_fails_loudly(self):
        with self.assertRaises(ValueError) as context:
            run_evaluation_loop(generation="markov", **TINY)
        self.assertIn("generation", str(context.exception))

    def test_constrained_runs_are_deterministic(self):
        first = run_evaluation_loop(generation="constrained", **TINY)
        second = run_evaluation_loop(generation="constrained", **TINY)
        self.assertEqual(first, second)

    def test_elite_role_texture_is_recorded_for_both_arms(self):
        # DR 0042 clause 5 (observation): the loop reports which roles
        # its elites carry and the motion-trio elite fraction.
        for arm in ("wfc", "constrained"):
            with self.subTest(arm=arm):
                result = run_evaluation_loop(generation=arm, **TINY)
                texture = result["elite_role_summary"]
                self.assertIn("roles_present", texture)
                self.assertIn("motion_trio_elite_fraction", texture)
                self.assertGreaterEqual(
                    texture["motion_trio_elite_fraction"], 0.0
                )
                self.assertLessEqual(
                    texture["motion_trio_elite_fraction"], 1.0
                )


class ComparisonReportTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.report = build_generation_arm_report(
            population=16,
            target_evaluations=64,
            rng_seed=31,
        )

    def test_both_arms_run_at_the_matched_budget(self):
        arms = self.report["metrics"]["arms"]
        self.assertEqual({"wfc", "constrained"}, set(arms))
        for name, arm in arms.items():
            with self.subTest(arm=name):
                self.assertGreaterEqual(arm["evaluations_total"], 64)
                self.assertIn("coverage", arm)
                self.assertIn("qd_score", arm)
                self.assertIn("elite_role_summary", arm)

    def test_the_decision_is_the_pre_registered_rule_applied(self):
        self.assertEqual(ARTIFACT_ID, self.report["artifact_id"])
        lever = self.report["metrics"]["lever"]
        decision = self.report["decision"]
        adoptable = (
            lever["meets_coverage_gain_bar"]
            and lever["meets_qd_cost_bar"]
        )
        self.assertEqual(
            "adopt:constrained" if adoptable else "reject",
            decision["verdict"],
        )
        self.assertIn("incumbent", decision["rule"])

    def test_artifacts_are_written(self):
        with tempfile.TemporaryDirectory() as temp:
            path = write_generation_arm_artifacts(Path(temp), self.report)
            self.assertEqual(
                self.report,
                json.loads(path.read_text(encoding="utf-8")),
            )


if __name__ == "__main__":
    unittest.main()
