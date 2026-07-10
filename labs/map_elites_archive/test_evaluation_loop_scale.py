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

from evaluation_loop_scale import (  # noqa: E402
    PRE_REGISTERED_BOUND_S,
    build_evaluation_loop_report,
    measure_loop_pilot,
    run_evaluation_loop,
    write_evaluation_loop_artifacts,
)


RNG_SEED = 20260709


class LoopDeterminismTests(unittest.TestCase):
    """The documented requirement: determinism pinned under seeds."""

    @classmethod
    def setUpClass(cls):
        cls.first = run_evaluation_loop(
            population=8, target_evaluations=32, rng_seed=RNG_SEED
        )
        cls.second = run_evaluation_loop(
            population=8, target_evaluations=32, rng_seed=RNG_SEED
        )

    def test_identical_seeds_produce_identical_loops(self):
        self.assertEqual(
            json.dumps(self.first["trajectory"], sort_keys=True),
            json.dumps(self.second["trajectory"], sort_keys=True),
        )
        self.assertEqual(
            sorted(self.first["archive"]["elites"]),
            sorted(self.second["archive"]["elites"]),
        )
        for niche, elite in self.first["archive"]["elites"].items():
            with self.subTest(niche=niche):
                self.assertEqual(
                    elite["grid_id"],
                    self.second["archive"]["elites"][niche]["grid_id"],
                )

    def test_evaluation_accounting_is_exact(self):
        # bootstrap population + population per generation, run until the
        # target is reached.
        result = self.first
        self.assertGreaterEqual(result["evaluations_total"], 32)
        self.assertEqual(
            result["evaluations_total"],
            8 + 8 * len(result["trajectory"]),
        )
        self.assertEqual(
            result["evaluations_total"],
            result["archive"]["candidate_count"],
        )

    def test_occupancy_never_shrinks_across_generations(self):
        occupancies = [
            entry["occupied_niches"] for entry in self.first["trajectory"]
        ]
        self.assertEqual(occupancies, sorted(occupancies))

    def test_elite_records_carry_what_e5_needs(self):
        # E5 clusters families over elites: descriptor + axis values +
        # a morphology signature, without shipping full grids.
        elites = self.first["elite_records"]
        self.assertEqual(
            len(elites), self.first["archive_summary"]["occupied_niches"]
        )
        for record in elites[:5]:
            for field in (
                "grid_id",
                "niche",
                "fitness",
                "descriptor",
                "axis_values",
                "signature_hash",
            ):
                self.assertIn(field, record)


class ReportTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.report = build_evaluation_loop_report(
            population=8, target_evaluations=24, rng_seed=RNG_SEED
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
        self.assertEqual(
            "evaluation_loop_scale_stage0", self.report["artifact_id"]
        )

    def test_protocol_pre_registers_the_wall_clock_bound(self):
        protocol = self.report["metrics"]["protocol"]
        self.assertEqual(PRE_REGISTERED_BOUND_S, protocol["wall_clock_bound_s"])
        self.assertEqual("wfc", protocol["parent_path"])
        self.assertIn("E2", protocol["parent_path_evidence"])

    def test_trajectory_and_final_archive_are_consistent(self):
        metrics = self.report["metrics"]
        final = metrics["final_archive"]
        self.assertEqual(
            final["occupied_niches"],
            metrics["trajectory"][-1]["occupied_niches"],
        )
        self.assertEqual(
            round(final["occupied_niches"] / 512, 6), final["coverage"]
        )

    def test_report_body_carries_no_wall_clock(self):
        self.assertNotIn("measured", self.report)
        self.assertNotIn("measured", self.report["metrics"])

    def test_artifact_writer_emits_report_and_measured(self):
        measured = measure_loop_pilot(
            population=8, generations=1, rng_seed=RNG_SEED
        )
        with tempfile.TemporaryDirectory() as tmp:
            output_dir = Path(tmp)
            write_evaluation_loop_artifacts(output_dir, self.report, measured)
            payload = json.loads(
                (output_dir / "evaluation_loop_scale_stage0.json").read_text(
                    encoding="utf-8"
                )
            )
        self.assertIn("measured", payload)


class PilotMeasurementTests(unittest.TestCase):
    def test_pilot_shape_projections_and_bound_arithmetic(self):
        measured = measure_loop_pilot(
            population=8, generations=1, rng_seed=RNG_SEED
        )
        self.assertIn("context", measured)
        pilot = measured["pilot"]
        self.assertGreater(pilot["mean_ms_per_evaluation"], 0)
        projections = measured["projections"]
        self.assertEqual(
            round(pilot["mean_ms_per_evaluation"] * 20_000 / 1000, 2),
            projections["evaluations_20k_s"],
        )
        self.assertEqual(
            round(pilot["mean_ms_per_evaluation"] * 50_000 / 1000, 2),
            projections["evaluations_50k_s"],
        )
        self.assertEqual(
            projections["evaluations_20k_s"] <= PRE_REGISTERED_BOUND_S,
            projections["projection_meets_bound_20k"],
        )


class Stage0ArtifactConsistencyTests(unittest.TestCase):
    """Pins the committed full-scale evidence artifact.

    The E3 claim — the loop ran at 20k+ documented evaluations,
    deterministic under its recorded seed, inside the pre-registered
    wall-clock bound — is earned by the artifact.
    """

    @classmethod
    def setUpClass(cls):
        cls.artifact = json.loads(
            (
                REPO_ROOT
                / "data"
                / "archives"
                / "evaluation_loop_scale_stage0.json"
            ).read_text(encoding="utf-8")
        )

    def test_loop_reached_the_documented_evaluation_budget(self):
        metrics = self.artifact["metrics"]
        self.assertGreaterEqual(metrics["evaluations_total"], 20_000)
        self.assertGreaterEqual(
            metrics["final_archive"]["occupied_niches"], 200
        )

    def test_full_run_wall_clock_is_recorded_against_the_bound(self):
        measured = self.artifact["measured"]
        full_run = measured["full_run"]
        self.assertIn("wall_clock_s", full_run)
        self.assertEqual(
            full_run["wall_clock_s"] <= PRE_REGISTERED_BOUND_S,
            full_run["meets_bound"],
        )

    def test_seed_and_protocol_support_replay(self):
        protocol = self.artifact["metrics"]["protocol"]
        for field in (
            "rng_seed",
            "population",
            "target_evaluations",
            "lifecycle_ticks",
        ):
            self.assertIn(field, protocol)


if __name__ == "__main__":
    unittest.main()
