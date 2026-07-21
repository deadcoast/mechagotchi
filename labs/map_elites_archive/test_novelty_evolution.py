"""Cycle 20 J3 gates — novelty-first at the evolution surface (DR 0040).

The arms ride the E3 loop itself: ``selection`` is an additive loop
parameter whose default is BYTE-IDENTICAL to the historical loop;
novelty_first draws the scored population novelty-first from a larger
generated pool at the SAME scored budget; blend alternates. The
comparison report applies DR 0040's pre-registered rule verbatim —
adopt, blend, and reject all first-class.
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
from novelty_evolution import (  # noqa: E402
    COVERAGE_GAIN_BAR,
    QD_COST_FACTOR,
    build_novelty_evolution_report,
    write_novelty_evolution_artifacts,
)

TINY = dict(population=16, target_evaluations=64, rng_seed=31)


class SelectionArmTests(unittest.TestCase):
    def test_the_default_is_the_adopted_novelty_first_arm(self):
        # DR 0040 adopted novelty_first on the measured verdict; the
        # default IS the adopted arm, and the baseline stays runnable
        # (byte-identical to the historical loop when asked for).
        plain = run_evaluation_loop(**TINY)
        explicit = run_evaluation_loop(**TINY, selection="novelty_first")
        self.assertEqual(
            json.dumps(plain["trajectory"], sort_keys=True),
            json.dumps(explicit["trajectory"], sort_keys=True),
        )
        self.assertEqual(
            plain["archive_summary"], explicit["archive_summary"]
        )
        baseline = run_evaluation_loop(**TINY, selection="baseline")
        for entry in baseline["trajectory"]:
            self.assertNotIn("selection_novelty", entry)

    def test_novelty_first_keeps_the_scored_budget_and_records_the_pool(self):
        novelty = run_evaluation_loop(
            **TINY, selection="novelty_first", pool_factor=2
        )
        baseline = run_evaluation_loop(**TINY)
        self.assertEqual(
            baseline["evaluations_total"], novelty["evaluations_total"]
        )
        for entry in novelty["trajectory"]:
            with self.subTest(generation=entry["generation"]):
                self.assertTrue(entry["selection_novelty"])
                self.assertEqual(entry["pool_size"], 2 * 16)

    def test_blend_alternates_and_records_which_generations_were_novel(self):
        blend = run_evaluation_loop(
            **TINY, selection="blend", pool_factor=2
        )
        for entry in blend["trajectory"]:
            with self.subTest(generation=entry["generation"]):
                self.assertEqual(
                    entry["generation"] % 2 == 0,
                    entry["selection_novelty"],
                )

    def test_unknown_selection_fails_loudly(self):
        with self.assertRaises(ValueError):
            run_evaluation_loop(**TINY, selection="psychic")

    def test_novelty_runs_are_deterministic(self):
        first = run_evaluation_loop(
            **TINY, selection="novelty_first", pool_factor=2
        )
        second = run_evaluation_loop(
            **TINY, selection="novelty_first", pool_factor=2
        )
        self.assertEqual(
            json.dumps(first["trajectory"], sort_keys=True),
            json.dumps(second["trajectory"], sort_keys=True),
        )


class ComparisonReportTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.report = build_novelty_evolution_report(
            population=16,
            target_evaluations=64,
            rng_seed=31,
            pool_factor=2,
        )

    def test_all_three_arms_run_at_the_matched_budget(self):
        arms = self.report["metrics"]["arms"]
        self.assertEqual(
            ["baseline", "blend", "novelty_first"], sorted(arms)
        )
        budgets = {arm["evaluations_total"] for arm in arms.values()}
        self.assertEqual(1, len(budgets))

    def test_the_decision_is_the_pre_registered_rule_applied(self):
        metrics = self.report["metrics"]
        base = metrics["arms"]["baseline"]
        eligible = []
        for name in ("novelty_first", "blend"):
            arm = metrics["arms"][name]
            gain = round(arm["coverage"] - base["coverage"], 6)
            self.assertEqual(gain, metrics["levers"][name]["coverage_gain"])
            if (
                gain >= COVERAGE_GAIN_BAR
                and arm["qd_score"] >= QD_COST_FACTOR * base["qd_score"]
            ):
                eligible.append((arm["coverage"], name))
        expected = (
            "adopt:" + max(eligible)[1] if eligible else "reject"
        )
        self.assertEqual(expected, self.report["decision"]["verdict"])

    def test_artifacts_are_written(self):
        with tempfile.TemporaryDirectory() as tmp:
            write_novelty_evolution_artifacts(Path(tmp), self.report)
            payload = json.loads(
                (
                    Path(tmp) / "novelty_evolution_stage0.json"
                ).read_text(encoding="utf-8")
            )
        self.assertEqual(
            "novelty_evolution_stage0", payload["artifact_id"]
        )
        self.assertIn("verdict", payload["decision"])


if __name__ == "__main__":
    unittest.main()
