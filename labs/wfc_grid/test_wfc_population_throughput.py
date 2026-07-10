import json
import sys
import tempfile
import unittest
from pathlib import Path


LAB_DIR = Path(__file__).resolve().parent
REPO_ROOT = LAB_DIR.parents[1]
for sub in [
    "labs/wfc_grid",
    "labs/grid_genome",
    "labs/readability_benchmark",
    "labs/lifecycle_sim",
    "labs/map_elites_archive",
]:
    path = str(REPO_ROOT / sub)
    if path not in sys.path:
        sys.path.insert(0, path)
PACKAGE_SRC = REPO_ROOT / "packages" / "mecha_engine" / "src"
if str(PACKAGE_SRC) not in sys.path:
    sys.path.insert(0, str(PACKAGE_SRC))

from corpus_builder import build_seed_grids_16  # noqa: E402
from niche_scale_archive import (  # noqa: E402
    insert_scale_candidate,
    new_scale_archive,
)
from validator import validate_grid  # noqa: E402
from wfc_population_throughput import (  # noqa: E402
    TIME_BAR_MS,
    arm_metrics,
    build_population_throughput_report,
    constrained_population,
    load_frozen_scale_edges,
    measure_population_throughput,
    parents_from_archive,
    wfc_population,
    write_population_throughput_artifacts,
)

from mecha_engine.generation import train_generation_model  # noqa: E402


RNG_SEED = 20260709


class FrozenEdgeTests(unittest.TestCase):
    def test_edges_come_from_the_committed_e1_artifact(self):
        edges = load_frozen_scale_edges()
        artifact = json.loads(
            (
                REPO_ROOT / "data" / "archives" / "niche_scale_archive_stage0.json"
            ).read_text(encoding="utf-8")
        )
        self.assertEqual(artifact["metrics"]["edge_derivation"]["edges"], edges)


class ParentSelectionTests(unittest.TestCase):
    def test_parents_follow_the_promoted_elite_ordering(self):
        # runtime.evolve's default branch: parents = elites' grids in
        # sorted(niche) order.
        grids = build_seed_grids_16()[:3]
        archive = new_scale_archive()
        insert_scale_candidate(archive, grids[0], {"fitness": 0.5}, (7, 0, 0))
        insert_scale_candidate(archive, grids[1], {"fitness": 0.5}, (0, 0, 1))
        insert_scale_candidate(archive, grids[2], {"fitness": 0.5}, (0, 0, 0))
        grids_by_id = {grid["grid_id"]: grid for grid in grids}
        parents = parents_from_archive(archive, grids_by_id)
        self.assertEqual(
            [grids[2]["grid_id"], grids[1]["grid_id"], grids[0]["grid_id"]],
            [parent["grid_id"] for parent in parents],
        )


class WfcPopulationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.parents = build_seed_grids_16()[:12]

    def test_population_is_deterministic_and_accounted(self):
        first, first_failures = wfc_population(
            self.parents, population=6, generation_index=1, rng_seed=RNG_SEED
        )
        second, second_failures = wfc_population(
            self.parents, population=6, generation_index=1, rng_seed=RNG_SEED
        )
        self.assertEqual(
            json.dumps(first, sort_keys=True), json.dumps(second, sort_keys=True)
        )
        self.assertEqual(first_failures, second_failures)
        self.assertEqual(6, len(first) + len(first_failures))

    def test_candidates_are_16x16_with_unique_ids(self):
        candidates, _ = wfc_population(
            self.parents, population=6, generation_index=2, rng_seed=RNG_SEED
        )
        ids = [candidate["grid_id"] for candidate in candidates]
        self.assertEqual(len(ids), len(set(ids)))
        for candidate in candidates:
            self.assertEqual([16, 16], candidate["grid_size"])


class ConstrainedPopulationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.parents = build_seed_grids_16()[:5]
        cls.model = train_generation_model(build_seed_grids_16())

    def test_round_robin_parentage_matches_evolve(self):
        candidates, failures = constrained_population(
            self.parents,
            self.model,
            population=8,
            generation_index=1,
            rng_seed=RNG_SEED,
        )
        self.assertEqual([], failures)
        for index, candidate in enumerate(candidates):
            expected_parent = self.parents[index % len(self.parents)]
            with self.subTest(index=index):
                self.assertEqual(
                    expected_parent["grid_id"], candidate["parent_grid_id"]
                )

    def test_population_is_deterministic_and_valid(self):
        first, _ = constrained_population(
            self.parents,
            self.model,
            population=4,
            generation_index=1,
            rng_seed=RNG_SEED,
        )
        second, _ = constrained_population(
            self.parents,
            self.model,
            population=4,
            generation_index=1,
            rng_seed=RNG_SEED,
        )
        self.assertEqual(
            json.dumps(first, sort_keys=True), json.dumps(second, sort_keys=True)
        )
        for candidate in first:
            self.assertTrue(validate_grid(candidate).ok)


class ArmMetricsTests(unittest.TestCase):
    def test_metrics_over_a_known_batch(self):
        parents = build_seed_grids_16()[:4]
        edges = load_frozen_scale_edges()
        # A copy of a parent counts against novelty, not validity.
        batch = parents[:2] + [json.loads(json.dumps(parents[0]))]
        metrics = arm_metrics(batch, parents, edges)
        self.assertEqual(3, metrics["produced"])
        self.assertEqual(1.0, metrics["validity_rate"])
        self.assertEqual(round(2 / 3, 6), metrics["unique_signature_rate"])
        self.assertEqual(1.0, metrics["parent_copy_rate"])
        self.assertGreaterEqual(metrics["unique_scale_descriptors"], 1)

    def test_empty_batch_is_honest(self):
        metrics = arm_metrics([], build_seed_grids_16()[:2], load_frozen_scale_edges())
        self.assertEqual(0, metrics["produced"])
        self.assertEqual(0.0, metrics["validity_rate"])


class ReportTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.report = build_population_throughput_report(
            initial_count=16,
            population=8,
            generations=2,
            rng_seed=RNG_SEED,
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
            "wfc_population_throughput_stage0", self.report["artifact_id"]
        )

    def test_generations_carry_both_arms_from_shared_parents(self):
        generations = self.report["metrics"]["generations"]
        self.assertEqual(2, len(generations))
        for entry in generations:
            with self.subTest(generation=entry["generation"]):
                self.assertGreater(entry["parent_count"], 0)
                self.assertIn("wfc", entry["arms"])
                self.assertIn("constrained", entry["arms"])
                for arm in entry["arms"].values():
                    self.assertLessEqual(arm["validity_rate"], 1.0)

    def test_archive_refresh_uses_the_wfc_arm(self):
        # The WFC parent path is what E2 proves: its candidates refresh the
        # archive between generations; the constrained arm is the measured
        # comparator from the SAME parents.
        self.assertEqual(
            "wfc", self.report["metrics"]["protocol"]["archive_refresh_arm"]
        )
        archive = self.report["metrics"]["final_archive"]
        self.assertGreaterEqual(archive["occupied_niches"], 1)

    def test_report_body_carries_no_wall_clock(self):
        self.assertNotIn("measured", self.report)
        self.assertNotIn("measured", self.report["metrics"])

    def test_artifact_writer_emits_report_and_measured(self):
        measured = measure_population_throughput(
            population=4, rng_seed=RNG_SEED
        )
        with tempfile.TemporaryDirectory() as tmp:
            output_dir = Path(tmp)
            write_population_throughput_artifacts(
                output_dir, self.report, measured
            )
            payload = json.loads(
                (
                    output_dir / "wfc_population_throughput_stage0.json"
                ).read_text(encoding="utf-8")
            )
        self.assertIn("measured", payload)


class MeasuredThroughputTests(unittest.TestCase):
    def test_measurement_shape_and_time_bar_arithmetic(self):
        measured = measure_population_throughput(population=4, rng_seed=RNG_SEED)
        self.assertIn("context", measured)
        self.assertEqual(250.0, TIME_BAR_MS)
        for arm in ("wfc", "constrained"):
            with self.subTest(arm=arm):
                entry = measured["arms"][arm]
                self.assertGreater(entry["mean_ms_per_candidate"], 0)
                self.assertEqual(
                    entry["mean_ms_per_candidate"] <= TIME_BAR_MS,
                    entry["meets_time_bar"],
                )


class Stage0ArtifactConsistencyTests(unittest.TestCase):
    """Pins the committed full-scale evidence artifact.

    The E2 claim — populations in the HUNDREDS per generation — is earned
    by the artifact, not asserted in prose.
    """

    @classmethod
    def setUpClass(cls):
        cls.artifact = json.loads(
            (
                REPO_ROOT
                / "data"
                / "wfc_grid"
                / "wfc_population_throughput_stage0.json"
            ).read_text(encoding="utf-8")
        )

    def test_populations_are_in_the_hundreds_across_generations(self):
        generations = self.artifact["metrics"]["generations"]
        self.assertGreaterEqual(len(generations), 3)
        for entry in generations:
            with self.subTest(generation=entry["generation"]):
                self.assertGreaterEqual(entry["population"], 200)

    def test_artifact_records_throughput_against_the_documented_bar(self):
        measured = self.artifact["measured"]
        for arm in ("wfc", "constrained"):
            self.assertIn("meets_time_bar", measured["arms"][arm])


if __name__ == "__main__":
    unittest.main()
