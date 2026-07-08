import json
import tempfile
import unittest
from pathlib import Path

from synthetic_keepers import (
    KEEPER_IDS,
    build_synthetic_keeper_report,
    keeper_action,
    run_benchmark,
    run_keeper_lifecycle,
)

LAB_DIR = Path(__file__).resolve().parent
REPO_ROOT = LAB_DIR.parents[1]


def _seed_grid() -> dict:
    import sys

    grid_genome = REPO_ROOT / "labs" / "grid_genome"
    if str(grid_genome) not in sys.path:
        sys.path.insert(0, str(grid_genome))
    from corpus_builder import build_seed_grids

    return build_seed_grids()[0]


class KeeperPolicyTests(unittest.TestCase):
    def test_the_five_documented_models_exist(self):
        self.assertEqual(
            ["attentive", "neglectful", "erratic", "punitive", "exploratory"],
            KEEPER_IDS,
        )

    def test_lifecycles_are_deterministic_under_seeds(self):
        grid = _seed_grid()
        for keeper_id in KEEPER_IDS:
            with self.subTest(keeper=keeper_id):
                first = run_keeper_lifecycle(
                    grid, keeper_id, ticks=60, rng_seed=7, fleet_enabled=True
                )
                second = run_keeper_lifecycle(
                    grid, keeper_id, ticks=60, rng_seed=7, fleet_enabled=True
                )
                self.assertEqual(first, second)

    def test_attentive_interacts_more_and_fares_better_than_neglectful(self):
        grid = _seed_grid()
        attentive = run_keeper_lifecycle(
            grid, "attentive", ticks=120, rng_seed=11, fleet_enabled=False
        )
        neglectful = run_keeper_lifecycle(
            grid, "neglectful", ticks=120, rng_seed=11, fleet_enabled=False
        )
        self.assertGreater(
            attentive["keeper_overrides"], neglectful["keeper_overrides"]
        )
        self.assertGreater(attentive["mean_balance"], neglectful["mean_balance"])

    def test_keeper_action_returns_only_interactions_or_none(self):
        import random

        grid = _seed_grid()
        rng = random.Random(3)
        state = {"hunger": 0.7, "energy": 0.5, "bond": 0.4, "age_ticks": 4}
        for keeper_id in KEEPER_IDS:
            action = keeper_action(keeper_id, state, rng)
            self.assertIn(action, ["feed", "play", None])


class BenchmarkTests(unittest.TestCase):
    def test_pilot_benchmark_shape_and_pairing(self):
        benchmark = run_benchmark(lifecycles_per_keeper=4, ticks=30)
        self.assertEqual(
            5 * 4, benchmark["lifecycles_per_arm"]
        )
        self.assertEqual(5 * 4 * 30, benchmark["ticks_requested_per_arm"])
        for keeper in benchmark["keepers"]:
            self.assertIn(keeper["keeper_id"], KEEPER_IDS)
            for arm in ["frozen", "fleet"]:
                self.assertIn("mean_balance", keeper[arm])
                self.assertIn("survival_rate", keeper[arm])
            self.assertIn("welfare_delta_pct", keeper)


class ReportTests(unittest.TestCase):
    report: dict

    @classmethod
    def setUpClass(cls):
        # Pilot scale for the suite; the artifact run (main) is full scale.
        cls.report = build_synthetic_keeper_report(
            lifecycles_per_keeper=4, ticks=30
        )

    def test_report_shape(self):
        for key in [
            "artifact_id",
            "status",
            "date",
            "purpose",
            "source_artifacts",
            "metrics",
            "closed_states",
            "blocked_states",
            "decision",
            "next_research_step",
        ]:
            self.assertIn(key, self.report)
        self.assertEqual(
            "synthetic_keepers_stage0", self.report["artifact_id"]
        )
        self.assertEqual(self.report, json.loads(json.dumps(self.report)))

    def test_wallclock_is_measured_first_and_the_dependency_decision_recorded(self):
        wallclock = self.report["metrics"]["wallclock"]
        self.assertGreater(wallclock["pilot_seconds"], 0.0)
        self.assertGreater(wallclock["pilot_ticks"], 0)
        self.assertGreater(wallclock["projected_full_benchmark_seconds"], 0.0)
        self.assertIn("stdlib_holds", wallclock)
        self.assertIn(
            "dependency_decision", self.report["metrics"]
        )

    def test_welfare_is_measured_per_keeper_both_arms(self):
        benchmark = self.report["metrics"]["benchmark"]
        self.assertEqual(5, len(benchmark["keepers"]))
        for keeper in benchmark["keepers"]:
            self.assertIsInstance(keeper["welfare_delta_pct"], float)

    def test_write_artifacts_round_trips(self):
        from synthetic_keepers import write_synthetic_keeper_artifacts

        with tempfile.TemporaryDirectory() as tmp:
            output_dir = Path(tmp)
            write_synthetic_keeper_artifacts(output_dir, self.report)
            written = output_dir / "synthetic_keepers_stage0.json"
            self.assertTrue(written.exists())
            self.assertEqual(
                self.report,
                json.loads(written.read_text(encoding="utf-8")),
            )


if __name__ == "__main__":
    unittest.main()
