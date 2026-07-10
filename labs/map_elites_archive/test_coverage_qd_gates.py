import json
import sys
import tempfile
import unittest
from pathlib import Path


LAB_DIR = Path(__file__).resolve().parent
REPO_ROOT = LAB_DIR.parents[1]
for sub in [
    "labs/map_elites_archive",
    "labs/grid_genome",
    "labs/readability_benchmark",
    "labs/lifecycle_sim",
    "labs/wfc_grid",
]:
    path = str(REPO_ROOT / sub)
    if path not in sys.path:
        sys.path.insert(0, path)
PACKAGE_SRC = REPO_ROOT / "packages" / "mecha_engine" / "src"
if str(PACKAGE_SRC) not in sys.path:
    sys.path.insert(0, str(PACKAGE_SRC))

from coverage_qd_gates import (  # noqa: E402
    COVERAGE_GATE,
    GA_COVERAGE_ADVANTAGE_GATE,
    BEST_FITNESS_TOLERANCE,
    build_coverage_gate_report,
    judge_gates,
    run_ga_baseline,
    write_coverage_gate_artifacts,
)


RNG_SEED = 20260709


class GaBaselineTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.first = run_ga_baseline(
            population=8, target_evaluations=24, rng_seed=RNG_SEED
        )
        cls.second = run_ga_baseline(
            population=8, target_evaluations=24, rng_seed=RNG_SEED
        )

    def test_ga_is_deterministic_under_seeds(self):
        self.assertEqual(
            json.dumps(self.first["trajectory"], sort_keys=True),
            json.dumps(self.second["trajectory"], sort_keys=True),
        )
        self.assertEqual(
            self.first["history_coverage"], self.second["history_coverage"]
        )

    def test_ga_spends_the_identical_budget(self):
        self.assertEqual(24, self.first["evaluations_total"])

    def test_ga_has_no_archive_only_scalar_selection(self):
        # The plain GA never keys anything by niche: selection is scalar
        # truncation; coverage is measured EXTERNALLY over its evaluation
        # history (the standard QD comparison).
        self.assertNotIn("archive", self.first)
        self.assertIn("history_niches_touched", self.first)
        self.assertIn("best_fitness", self.first)
        self.assertEqual(
            round(self.first["history_niches_touched"] / 512, 6),
            self.first["history_coverage"],
        )


class GateJudgmentTests(unittest.TestCase):
    def test_documented_gate_constants(self):
        self.assertEqual(0.25, COVERAGE_GATE)
        self.assertEqual(0.25, GA_COVERAGE_ADVANTAGE_GATE)
        self.assertEqual(0.10, BEST_FITNESS_TOLERANCE)

    def test_gates_judged_from_paired_seed_means(self):
        verdict = judge_gates(
            map_elites_runs=[
                {"coverage": 0.5, "best_fitness": 0.9},
                {"coverage": 0.54, "best_fitness": 0.92},
            ],
            ga_runs=[
                {"history_coverage": 0.3, "best_fitness": 0.95},
                {"history_coverage": 0.34, "best_fitness": 0.93},
            ],
        )
        self.assertEqual(0.52, verdict["map_elites_coverage_mean"])
        self.assertEqual(0.32, verdict["ga_coverage_mean"])
        self.assertTrue(verdict["coverage_gate_met"])  # 0.52 >= 0.25
        # advantage = 0.52/0.32 - 1 = 0.625 >= 0.25
        self.assertEqual(0.625, verdict["coverage_advantage_over_ga"])
        self.assertTrue(verdict["ga_advantage_gate_met"])
        # best fitness 0.92 vs strongest 0.95 -> within 10%
        self.assertTrue(verdict["best_fitness_within_tolerance"])

    def test_failed_gates_are_recorded_not_fudged(self):
        verdict = judge_gates(
            map_elites_runs=[{"coverage": 0.2, "best_fitness": 0.5}],
            ga_runs=[{"history_coverage": 0.19, "best_fitness": 0.9}],
        )
        self.assertFalse(verdict["coverage_gate_met"])
        self.assertFalse(verdict["ga_advantage_gate_met"])
        self.assertFalse(verdict["best_fitness_within_tolerance"])


class ReportTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.report = build_coverage_gate_report(
            population=8,
            target_evaluations=24,
            seeds=[RNG_SEED, RNG_SEED + 1],
        )

    def test_report_shape_follows_the_lab_idiom(self):
        for field in (
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
        ):
            self.assertIn(field, self.report)
        self.assertEqual("coverage_qd_gates_stage0", self.report["artifact_id"])

    def test_paired_runs_share_seeds_and_budget(self):
        metrics = self.report["metrics"]
        self.assertEqual(2, len(metrics["map_elites_runs"]))
        self.assertEqual(2, len(metrics["ga_runs"]))
        for map_run, ga_run in zip(
            metrics["map_elites_runs"], metrics["ga_runs"]
        ):
            self.assertEqual(map_run["rng_seed"], ga_run["rng_seed"])
            self.assertEqual(
                map_run["evaluations_total"], ga_run["evaluations_total"]
            )

    def test_verdict_and_per_axis_spread_are_recorded(self):
        metrics = self.report["metrics"]
        self.assertIn("verdict", metrics)
        for run in metrics["map_elites_runs"]:
            self.assertIn("descriptor_bin_spread", run)
            self.assertIn("qd_score", run)

    def test_protocol_records_the_seed_adaptation(self):
        protocol = self.report["metrics"]["protocol"]
        self.assertIn("documented_protocol", protocol)
        self.assertIn("ten", protocol["documented_protocol"])
        self.assertEqual(2, protocol["seeds_run"])

    def test_artifact_writer_round_trip(self):
        with tempfile.TemporaryDirectory() as tmp:
            output_dir = Path(tmp)
            write_coverage_gate_artifacts(output_dir, self.report, None)
            payload = json.loads(
                (output_dir / "coverage_qd_gates_stage0.json").read_text(
                    encoding="utf-8"
                )
            )
        self.assertEqual(self.report["artifact_id"], payload["artifact_id"])


class Stage0ArtifactConsistencyTests(unittest.TestCase):
    """Pins the committed full-scale gate artifact."""

    @classmethod
    def setUpClass(cls):
        cls.artifact = json.loads(
            (
                REPO_ROOT / "data" / "archives" / "coverage_qd_gates_stage0.json"
            ).read_text(encoding="utf-8")
        )

    def test_full_scale_runs_at_documented_budget_and_seeds(self):
        metrics = self.artifact["metrics"]
        self.assertGreaterEqual(len(metrics["map_elites_runs"]), 3)
        for run in metrics["map_elites_runs"]:
            self.assertGreaterEqual(run["evaluations_total"], 20_000)

    def test_verdict_is_recorded_with_all_three_gates(self):
        verdict = self.artifact["metrics"]["verdict"]
        for field in (
            "coverage_gate_met",
            "ga_advantage_gate_met",
            "best_fitness_within_tolerance",
        ):
            self.assertIn(field, verdict)


if __name__ == "__main__":
    unittest.main()
