import tempfile
import unittest
from pathlib import Path

from archive_comparators import (
    build_archive_comparators_report,
    write_archive_comparators_artifacts,
)


class ArchiveComparatorTests(unittest.TestCase):
    """T18: the RUN TWO keep-gate, measured at Stage 0 scale."""

    @classmethod
    def setUpClass(cls):
        cls.report = build_archive_comparators_report(
            budget=40, ticks=8, rng_seeds=(20260512, 20260612)
        )

    def test_matched_budgets_over_identical_streams(self):
        for run in self.report["runs"]:
            for comparator in ("ga_truncation", "novelty_search", "map_elites"):
                self.assertLessEqual(
                    run[comparator]["survivor_count"], 40
                )
        self.assertEqual(2, len(self.report["runs"]))

    def test_gate_derives_from_measurements(self):
        gate = self.report["gate"]
        summary = self.report["summary"]
        ga = summary["ga_truncation"]["coverage"]
        me = summary["map_elites"]["coverage"]
        self.assertEqual(
            round((me - ga) / ga, 6), gate["coverage_advantage_over_ga"]
        )
        expected = (
            gate["coverage_advantage_over_ga"] >= 0.25
            and gate["best_fitness_gap_to_strongest"] <= 0.10
        )
        self.assertEqual(expected, gate["map_elites_confirmed"])
        self.assertEqual(
            "map_elites_confirmed" if expected else "map_elites_challenged",
            self.report["decision"]["status"],
        )

    def test_deterministic(self):
        again = build_archive_comparators_report(
            budget=40, ticks=8, rng_seeds=(20260512, 20260612)
        )
        self.assertEqual(self.report, again)

    def test_artifacts_write(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            output = Path(temp_dir)
            write_archive_comparators_artifacts(output, self.report)
            self.assertTrue(
                (output / "archive_comparators_stage0.json").exists()
            )


if __name__ == "__main__":
    unittest.main()


class GeneratorABTests(unittest.TestCase):
    """T17 follow-up: the constrained-vs-hybrid A/B through the archive."""

    @classmethod
    def setUpClass(cls):
        from archive_comparators import build_generator_ab_report
        cls.report = build_generator_ab_report(
            budget=30, ticks=8, rng_seeds=(20260512,)
        )

    def test_two_arms_matched_budgets(self):
        self.assertEqual(1, len(self.report["runs"]))
        run = self.report["runs"][0]
        self.assertIn("package_hybrid", run)
        self.assertIn("constrained_wfc", run)

    def test_decision_derives_from_measurements(self):
        summary = self.report["summary"]
        hybrid, wfc = summary["package_hybrid"], summary["constrained_wfc"]
        wins = (
            wfc["coverage"] > hybrid["coverage"]
            and wfc["qd_score"] > hybrid["qd_score"]
            and wfc["best_fitness"] >= hybrid["best_fitness"] * 0.95
        )
        self.assertEqual(
            "constrained_arm_wins_dr_gated_switch_proposed"
            if wins
            else "shipped_hybrid_stands",
            self.report["decision"]["status"],
        )
