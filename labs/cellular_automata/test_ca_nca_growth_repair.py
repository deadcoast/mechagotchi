import json
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
LAB_DIR = Path(__file__).resolve().parent
GRID_GENOME = ROOT / "labs" / "grid_genome"
if str(LAB_DIR) not in sys.path:
    sys.path.insert(0, str(LAB_DIR))
if str(GRID_GENOME) not in sys.path:
    sys.path.insert(0, str(GRID_GENOME))

from ca_nca_growth_repair import (  # noqa: E402
    apply_damage,
    apply_stochastic_damage,
    grow_from_seed,
    matrix_overlap,
    repair_with_local_attractor,
    repair_with_neighborhood_model,
    repair_with_role_prior_model,
    run_ca_nca_lab,
    run_damage_stress_benchmark,
    run_learned_repair_comparison,
    run_repeated_stochastic_damage_benchmark,
    run_persistence_rollout,
    run_trained_repair_benchmark,
    structural_agreement,
    train_neighborhood_repair_model,
    train_role_prior_repair_model,
    write_ca_nca_artifacts,
    write_learned_repair_comparison_artifacts,
    write_persistence_damage_artifacts,
    write_repeated_stochastic_damage_artifacts,
    write_trained_repair_artifacts,
)
from corpus_builder import build_seed_grids  # noqa: E402
from validator import validate_grid  # noqa: E402


class CaNcaGrowthRepairTests(unittest.TestCase):
    def test_apply_damage_reduces_target_overlap_and_preserves_metadata(self):
        target = build_seed_grids()[0]
        damaged = apply_damage(target, pattern="center_cut")

        self.assertEqual("ca_damage_center_cut", damaged["metadata"]["source"])
        self.assertLess(matrix_overlap(damaged, target), 1.0)
        self.assertGreater(matrix_overlap(damaged, target), 0.25)
        self.assertIn("ca_damage_center_cut", damaged["lineage"]["mutation_events"])

    def test_repair_with_local_attractor_recovers_valid_grid(self):
        target = build_seed_grids()[0]
        damaged = apply_damage(target, pattern="center_cut")
        repaired = repair_with_local_attractor(damaged, target, steps=8, rng_seed=20260512)

        self.assertTrue(validate_grid(repaired).ok, validate_grid(repaired).errors)
        self.assertGreater(matrix_overlap(repaired, target), matrix_overlap(damaged, target))
        self.assertGreaterEqual(matrix_overlap(repaired, target), 0.95)
        self.assertIn("nca_inspired_local_attractor_repair", repaired["lineage"]["mutation_events"])

    def test_persistence_rollout_preserves_validity_and_overlap(self):
        target = build_seed_grids()[0]
        damaged = apply_damage(target, pattern="lower_body")
        repaired = repair_with_local_attractor(damaged, target, steps=8, rng_seed=20260512)

        rollout = run_persistence_rollout(
            repaired,
            target,
            steps=10,
            rng_seed=20260512,
        )

        self.assertEqual(10, rollout["step_count"])
        self.assertTrue(rollout["final_valid"], rollout["final_errors"])
        self.assertGreaterEqual(rollout["min_overlap"], 0.95)
        self.assertGreaterEqual(rollout["final_overlap"], 0.95)
        self.assertEqual(
            "nca_inspired_persistence_rollout",
            rollout["final_grid"]["metadata"]["source"],
        )

    def test_apply_stochastic_damage_is_seeded_and_records_removed_cells(self):
        target = build_seed_grids()[0]

        first = apply_stochastic_damage(
            target,
            dropout_rate=0.35,
            rng_seed=20260512,
            event_index=1,
        )
        second = apply_stochastic_damage(
            target,
            dropout_rate=0.35,
            rng_seed=20260512,
            event_index=1,
        )

        self.assertEqual(first["cells"], second["cells"])
        self.assertEqual("ca_stochastic_damage", first["metadata"]["source"])
        self.assertEqual("stochastic_dropout", first["metadata"]["damage_pattern"])
        self.assertGreater(first["metadata"]["removed_cell_count"], 0)
        self.assertLess(matrix_overlap(first, target), 1.0)

    def test_repeated_stochastic_damage_benchmark_repairs_multiple_cycles(self):
        report = run_repeated_stochastic_damage_benchmark(
            count=3,
            cycles=4,
            dropout_rate=0.22,
            repair_steps=8,
            rng_seed=20260512,
        )

        self.assertEqual("ca_nca_repeated_stochastic_damage_stage0", report["lab_id"])
        self.assertEqual(3, report["summary"]["sample_count"])
        self.assertEqual(4, report["summary"]["cycle_count"])
        self.assertEqual(12, report["summary"]["total_damage_events"])
        self.assertGreaterEqual(report["summary"]["final_validity_rate"], 0.75)
        self.assertGreaterEqual(report["summary"]["mean_final_overlap"], 0.9)
        self.assertGreaterEqual(
            report["summary"]["mean_repair_gain_per_event"],
            0,
        )
        self.assertIn(report["decision"]["status"], {"prototype_repeated_stress", "watch_repeated_stress"})

    def test_role_prior_model_repairs_without_target_template(self):
        seed_grids = build_seed_grids()
        target = seed_grids[0]
        model = train_role_prior_repair_model(seed_grids[1:])
        damaged = apply_damage(target, pattern="center_cut")

        repaired = repair_with_role_prior_model(
            damaged,
            model,
            steps=8,
            rng_seed=20260512,
        )

        self.assertFalse(model["target_template_used"])
        self.assertGreater(model["training_grid_count"], 0)
        self.assertEqual("learned_role_prior_repair", repaired["metadata"]["source"])
        self.assertTrue(validate_grid(repaired).ok, validate_grid(repaired).errors)
        self.assertGreaterEqual(
            matrix_overlap(repaired, target),
            matrix_overlap(damaged, target),
        )

    def test_learned_repair_comparison_reports_assisted_baseline_gap(self):
        report = run_learned_repair_comparison(
            count=3,
            cycles=3,
            dropout_rate=0.2,
            repair_steps=8,
            rng_seed=20260512,
        )

        self.assertEqual("ca_nca_learned_repair_comparison_stage0", report["lab_id"])
        self.assertEqual(3, report["summary"]["sample_count"])
        self.assertEqual(9, report["summary"]["total_damage_events"])
        self.assertFalse(report["summary"]["target_template_used_by_learned"])
        self.assertGreaterEqual(
            report["summary"]["mean_assisted_final_overlap"],
            report["summary"]["mean_learned_final_overlap"],
        )
        self.assertGreaterEqual(report["summary"]["learned_final_validity_rate"], 0.75)
        self.assertIn(
            report["decision"]["status"],
            {"promote_less_assisted_repair", "watch_learned_repair", "keep_assisted_baseline"},
        )

    def test_train_neighborhood_repair_model_is_deterministic_and_templateless(self):
        training_grids = build_seed_grids()[:8]

        first = train_neighborhood_repair_model(
            training_grids,
            epochs=20,
            rng_seed=20260512,
        )
        second = train_neighborhood_repair_model(
            training_grids,
            epochs=20,
            rng_seed=20260512,
        )

        self.assertFalse(first["target_template_used"])
        self.assertEqual(first["weights"], second["weights"])
        self.assertEqual(8, first["training_grid_count"])
        self.assertGreater(first["example_count"], 0)
        self.assertLess(first["final_loss"], first["initial_loss"])

    def test_neighborhood_model_repairs_heldout_damage_without_template(self):
        seed_grids = build_seed_grids()
        model = train_neighborhood_repair_model(
            seed_grids[:12],
            epochs=60,
            rng_seed=20260512,
        )
        # Held-out grid never seen during training.
        target = seed_grids[45]
        damaged = apply_stochastic_damage(
            target,
            dropout_rate=0.2,
            rng_seed=20260512,
            event_index=1,
        )

        repaired = repair_with_neighborhood_model(damaged, model, steps=8)

        self.assertEqual(
            "learned_neighborhood_softmax_repair",
            repaired["metadata"]["source"],
        )
        self.assertFalse(repaired["metadata"]["target_template_used"])
        self.assertTrue(validate_grid(repaired).ok, validate_grid(repaired).errors)
        self.assertGreater(
            matrix_overlap(repaired, target),
            matrix_overlap(damaged, target),
        )
        # Deterministic repair: same inputs give identical cells.
        again = repair_with_neighborhood_model(damaged, model, steps=8)
        self.assertEqual(repaired["cells"], again["cells"])

    def test_structural_agreement_penalises_spurious_fills(self):
        target = build_seed_grids()[0]
        damaged = apply_damage(target, pattern="center_cut")

        self.assertEqual(1.0, structural_agreement(target, target))
        self.assertLess(structural_agreement(damaged, target), 1.0)
        # Overgrown grid: perfect one-sided overlap can hide spurious cells,
        # but structural agreement must not.
        overgrown = json.loads(json.dumps(target))
        overgrown["cells"] = list(overgrown["cells"]) + [
            {
                "x": 7,
                "y": 7,
                "visual": overgrown["cells"][0]["visual"],
                "role": "body",
                "material": "hard",
                "mutation_weight": 0.1,
                "animation_anchor": False,
                "organ": "core",
                "stress": 0,
                "damage": 0,
                "locked": False,
            }
        ]
        self.assertEqual(1.0, matrix_overlap(overgrown, target))
        self.assertLess(structural_agreement(overgrown, target), 1.0)

    def test_run_trained_repair_benchmark_compares_all_arms_on_heldout_grids(self):
        report = run_trained_repair_benchmark(
            training_count=10,
            holdout_count=2,
            cycles=2,
            dropout_rate=0.2,
            repair_steps=8,
            epochs=30,
            rng_seed=20260512,
        )

        self.assertEqual("ca_nca_trained_repair_stage0", report["lab_id"])
        self.assertEqual(2, report["summary"]["holdout_target_count"])
        self.assertEqual(4, report["summary"]["total_damage_events"])
        self.assertFalse(report["summary"]["target_template_used_by_trained"])
        arms = report["summary"]["arms"]
        self.assertEqual(
            {"no_repair", "role_prior", "trained", "assisted"},
            set(arms.keys()),
        )
        # Training grids must not appear among held-out targets.
        self.assertTrue(
            set(report["trained_model"]["training_grid_ids"]).isdisjoint(
                set(report["holdout_target_ids"])
            )
        )
        self.assertGreater(
            arms["trained"]["mean_final_overlap"],
            arms["no_repair"]["mean_final_overlap"],
        )
        self.assertGreaterEqual(
            arms["assisted"]["mean_final_overlap"],
            arms["trained"]["mean_final_overlap"],
        )
        self.assertIn(
            report["decision"]["status"],
            {
                "promote_less_assisted_repair",
                "prototype_learned_repair_gap_narrowed",
                "keep_assisted_baseline",
            },
        )

    def test_write_trained_repair_artifacts_creates_report_and_samples(self):
        report = run_trained_repair_benchmark(
            training_count=10,
            holdout_count=2,
            cycles=2,
            dropout_rate=0.2,
            repair_steps=6,
            epochs=20,
            rng_seed=7,
        )
        with tempfile.TemporaryDirectory() as temp_dir:
            output_dir = Path(temp_dir)
            write_trained_repair_artifacts(output_dir, report)

            self.assertTrue(
                (output_dir / "ca_nca_trained_repair_stage0.json").exists()
            )
            self.assertTrue((output_dir / "trained_repair_README.md").exists())
            self.assertTrue((output_dir / "trained_repair_samples").is_dir())
            loaded = json.loads(
                (output_dir / "ca_nca_trained_repair_stage0.json").read_text(
                    encoding="utf-8"
                )
            )
            self.assertEqual("ca_nca_trained_repair_stage0", loaded["lab_id"])
            self.assertEqual(
                2 * 4,
                len(list((output_dir / "trained_repair_samples").glob("*.json"))),
            )

    def test_grow_from_seed_reaches_valid_target_like_grid(self):
        target = build_seed_grids()[0]
        grown = grow_from_seed(target, steps=12, rng_seed=20260512)

        self.assertTrue(validate_grid(grown).ok, validate_grid(grown).errors)
        self.assertGreaterEqual(matrix_overlap(grown, target), 0.95)
        self.assertEqual("nca_inspired_seed_growth", grown["metadata"]["source"])

    def test_run_ca_nca_lab_reports_growth_repair_and_lifecycle_metrics(self):
        report = run_ca_nca_lab(count=4, growth_steps=12, repair_steps=8, rng_seed=20260512)

        self.assertEqual("ca_nca_growth_repair_stage0", report["lab_id"])
        self.assertEqual(4, report["summary"]["sample_count"])
        self.assertGreaterEqual(report["summary"]["growth_validity_rate"], 0.75)
        self.assertGreaterEqual(report["summary"]["repair_validity_rate"], 0.75)
        self.assertGreater(
            report["summary"]["mean_attractor_repair_overlap"],
            report["summary"]["mean_damaged_overlap"],
        )
        self.assertIn("lifecycle_after_repair", report["summary"])

    def test_run_damage_stress_benchmark_covers_multiple_patterns(self):
        patterns = ("center_cut", "left_sensor", "lower_body")
        report = run_damage_stress_benchmark(
            count=3,
            damage_patterns=patterns,
            repair_steps=8,
            persistence_steps=10,
            rng_seed=20260512,
        )

        self.assertEqual("ca_nca_persistence_damage_stage0", report["lab_id"])
        self.assertEqual(9, report["summary"]["sample_count"])
        self.assertEqual(3, report["summary"]["pattern_count"])
        self.assertEqual(set(patterns), set(report["summary"]["patterns"].keys()))
        self.assertGreaterEqual(report["summary"]["repair_validity_rate"], 0.75)
        self.assertGreaterEqual(report["summary"]["persistence_validity_rate"], 0.75)
        self.assertGreater(
            report["summary"]["mean_repair_overlap"],
            report["summary"]["mean_damaged_overlap"],
        )
        self.assertIn(report["summary"]["hardest_pattern"], patterns)

    def test_write_ca_nca_artifacts_creates_report_and_sample_grids(self):
        report = run_ca_nca_lab(count=2, growth_steps=10, repair_steps=6, rng_seed=7)
        with tempfile.TemporaryDirectory() as temp_dir:
            output_dir = Path(temp_dir)
            write_ca_nca_artifacts(output_dir, report)

            self.assertTrue((output_dir / "ca_nca_growth_repair_stage0.json").exists())
            self.assertTrue((output_dir / "README.md").exists())
            self.assertTrue((output_dir / "samples").is_dir())
            loaded = json.loads(
                (output_dir / "ca_nca_growth_repair_stage0.json").read_text(
                    encoding="utf-8"
                )
            )
            self.assertEqual("ca_nca_growth_repair_stage0", loaded["lab_id"])
            self.assertGreater(len(list((output_dir / "samples").glob("*.json"))), 0)

    def test_write_persistence_damage_artifacts_creates_report_and_stress_samples(self):
        report = run_damage_stress_benchmark(
            count=2,
            damage_patterns=("center_cut", "left_sensor"),
            repair_steps=6,
            persistence_steps=6,
            rng_seed=7,
        )
        with tempfile.TemporaryDirectory() as temp_dir:
            output_dir = Path(temp_dir)
            write_persistence_damage_artifacts(output_dir, report)

            self.assertTrue((output_dir / "ca_nca_persistence_damage_stage0.json").exists())
            self.assertTrue((output_dir / "stress_samples").is_dir())
            loaded = json.loads(
                (output_dir / "ca_nca_persistence_damage_stage0.json").read_text(
                    encoding="utf-8"
                )
            )
            self.assertEqual("ca_nca_persistence_damage_stage0", loaded["lab_id"])
            self.assertGreater(len(list((output_dir / "stress_samples").glob("*.json"))), 0)

    def test_write_repeated_stochastic_damage_artifacts_creates_report_and_samples(self):
        report = run_repeated_stochastic_damage_benchmark(
            count=2,
            cycles=3,
            dropout_rate=0.2,
            repair_steps=6,
            rng_seed=7,
        )
        with tempfile.TemporaryDirectory() as temp_dir:
            output_dir = Path(temp_dir)
            write_repeated_stochastic_damage_artifacts(output_dir, report)

            self.assertTrue(
                (output_dir / "ca_nca_repeated_stochastic_damage_stage0.json").exists()
            )
            self.assertTrue((output_dir / "repeated_stress_samples").is_dir())
            loaded = json.loads(
                (
                    output_dir / "ca_nca_repeated_stochastic_damage_stage0.json"
                ).read_text(encoding="utf-8")
            )
            self.assertEqual("ca_nca_repeated_stochastic_damage_stage0", loaded["lab_id"])
            self.assertGreater(
                len(list((output_dir / "repeated_stress_samples").glob("*.json"))),
                0,
            )

    def test_write_learned_repair_comparison_artifacts_creates_report_and_samples(self):
        report = run_learned_repair_comparison(
            count=2,
            cycles=2,
            dropout_rate=0.2,
            repair_steps=6,
            rng_seed=7,
        )
        with tempfile.TemporaryDirectory() as temp_dir:
            output_dir = Path(temp_dir)
            write_learned_repair_comparison_artifacts(output_dir, report)

            self.assertTrue(
                (output_dir / "ca_nca_learned_repair_comparison_stage0.json").exists()
            )
            self.assertTrue((output_dir / "learned_repair_samples").is_dir())
            loaded = json.loads(
                (
                    output_dir / "ca_nca_learned_repair_comparison_stage0.json"
                ).read_text(encoding="utf-8")
            )
            self.assertEqual("ca_nca_learned_repair_comparison_stage0", loaded["lab_id"])
            self.assertGreater(
                len(list((output_dir / "learned_repair_samples").glob("*.json"))),
                0,
            )


if __name__ == "__main__":
    unittest.main()
