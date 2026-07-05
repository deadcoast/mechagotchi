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
    repair_with_wound_sites,
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

    def test_apply_stochastic_damage_records_removed_cell_positions(self):
        target = build_seed_grids()[0]
        damaged = apply_stochastic_damage(
            target,
            dropout_rate=0.35,
            rng_seed=20260512,
            event_index=1,
        )

        removed = damaged["metadata"]["removed_cells"]
        self.assertEqual(len(removed), damaged["metadata"]["removed_cell_count"])
        self.assertGreater(len(removed), 0)
        target_live = {
            (cell["x"], cell["y"]) for cell in target["cells"]
        }
        damaged_live = {
            (cell["x"], cell["y"]) for cell in damaged["cells"]
        }
        for x, y in removed:
            self.assertIn((x, y), target_live)
            self.assertNotIn((x, y), damaged_live)

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

    def test_repair_with_wound_sites_fills_exactly_the_damage_sites(self):
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
        wound_sites = damaged["metadata"]["removed_cells"]
        self.assertGreater(len(wound_sites), 0)

        repaired = repair_with_wound_sites(damaged, model)

        self.assertEqual(
            "learned_wound_site_softmax_repair",
            repaired["metadata"]["source"],
        )
        self.assertFalse(repaired["metadata"]["target_template_used"])
        self.assertEqual(len(wound_sites), repaired["metadata"]["wound_site_count"])
        # Every wound site is refilled with some live token...
        repaired_tokens = {
            (cell["x"], cell["y"]) for cell in repaired["cells"]
        }
        for x, y in wound_sites:
            self.assertIn((x, y), repaired_tokens)
        # ...and no other position changes: live set = damaged live + sites.
        damaged_tokens = {
            (cell["x"], cell["y"]) for cell in damaged["cells"]
        }
        self.assertEqual(
            damaged_tokens | {(x, y) for x, y in wound_sites},
            repaired_tokens,
        )
        # Deterministic repair: same inputs give identical cells.
        again = repair_with_wound_sites(damaged, model)
        self.assertEqual(repaired["cells"], again["cells"])

    def test_wound_site_validity_guard_recovers_from_invalid_refill(self):
        from ca_nca_growth_repair import (
            CLASS_TOKENS,
            NEIGHBORHOOD_FEATURE_COUNT,
            grid_from_matrix,
            matrix_from_grid,
        )

        target = build_seed_grids()[0]  # mg_seed_001
        matrix = matrix_from_grid(target)
        # Wound (2,3)+(3,3): probed fixture — refilling both as expression
        # cells disconnects the required body core, mirroring the
        # mg_seed_046 benchmark failure mode.
        wound_sites = [[2, 3], [3, 3]]
        for x, y in wound_sites:
            self.assertEqual("B", matrix[y][x])
            matrix[y][x] = "."
        damaged = grid_from_matrix(
            grid_id="mg_seed_001_guard_case",
            matrix=matrix,
            palette=target["palette"],
            parent_grid_id=target["grid_id"],
            source="ca_stochastic_damage",
            mutation_events=["ca_stochastic_damage_01"],
            generation_delta=1,
        )
        damaged["metadata"]["removed_cells"] = wound_sites
        # Adversarial model: bias weights force every fill toward "M".
        bias_index = NEIGHBORHOOD_FEATURE_COUNT - 1
        weights = [
            [0.0] * NEIGHBORHOOD_FEATURE_COUNT for _ in CLASS_TOKENS
        ]
        weights[0][bias_index] = -10.0
        weights[CLASS_TOKENS.index("M")][bias_index] = 10.0
        biased_model = {
            "model_id": "biased_probe_model",
            "weights": weights,
        }

        naive = repair_with_wound_sites(
            damaged, biased_model, validity_guard=False
        )
        self.assertFalse(validate_grid(naive).ok)

        guarded = repair_with_wound_sites(damaged, biased_model)
        self.assertTrue(validate_grid(guarded).ok, validate_grid(guarded).errors)
        self.assertGreaterEqual(
            guarded["metadata"]["validity_guard_substitutions"], 1
        )
        # The guard substitutes tokens only; it never abandons a wound site.
        naive_live = {(cell["x"], cell["y"]) for cell in naive["cells"]}
        guarded_live = {(cell["x"], cell["y"]) for cell in guarded["cells"]}
        self.assertEqual(naive_live, guarded_live)
        # Deterministic: same inputs give identical cells.
        again = repair_with_wound_sites(damaged, biased_model)
        self.assertEqual(guarded["cells"], again["cells"])

    def test_wound_site_guard_can_restore_slip_alignment(self):
        # Runtime integration finding (2026-07-05): a destroyed
        # profile-required organ cell (mg_seed_001's only expression cell,
        # at (5,3)) refilled as another organ leaves a validator-valid but
        # SLIP-unaligned creature that lifecycle refuses to simulate. With
        # the active profile supplied, the guard must also repair
        # alignment. The profile is an engine-native constraint set — it
        # carries nothing about this creature's silhouette or destroyed
        # tokens, so the no-template property is preserved.
        import json as json_module

        from ca_nca_growth_repair import (
            CLASS_TOKENS,
            NEIGHBORHOOD_FEATURE_COUNT,
            grid_from_matrix,
            matrix_from_grid,
        )
        from slip import is_grid_aligned

        slip_profile = json_module.loads(
            (ROOT / "data" / "slips" / "valid" / "slip_lcd_seed.json").read_text(
                encoding="utf-8"
            )
        )
        target = build_seed_grids()[0]  # mg_seed_001, lcd_green
        self.assertTrue(is_grid_aligned(target, slip_profile).ok)
        matrix = matrix_from_grid(target)
        self.assertEqual("M", matrix[3][5])
        wound_sites = [[5, 3]]
        matrix[3][5] = "."
        damaged = grid_from_matrix(
            grid_id="mg_seed_001_slip_guard_case",
            matrix=matrix,
            palette=target["palette"],
            parent_grid_id=target["grid_id"],
            source="ca_stochastic_damage",
            mutation_events=["ca_stochastic_damage_01"],
            generation_delta=1,
        )
        damaged["metadata"]["removed_cells"] = wound_sites
        # Adversarial model: bias weights force every fill toward "B".
        bias_index = NEIGHBORHOOD_FEATURE_COUNT - 1
        weights = [
            [0.0] * NEIGHBORHOOD_FEATURE_COUNT for _ in CLASS_TOKENS
        ]
        weights[0][bias_index] = -10.0
        weights[CLASS_TOKENS.index("B")][bias_index] = 10.0
        biased_model = {"model_id": "biased_probe_model", "weights": weights}

        # Without the profile the guard has nothing to object to: the
        # wrong-organ refill is validator-valid but unaligned.
        unaware = repair_with_wound_sites(damaged, biased_model)
        self.assertTrue(validate_grid(unaware).ok)
        self.assertFalse(is_grid_aligned(unaware, slip_profile).ok)

        # With the profile the guard restores alignment too.
        aware = repair_with_wound_sites(
            damaged, biased_model, slip_profile=slip_profile
        )
        self.assertTrue(validate_grid(aware).ok, validate_grid(aware).errors)
        self.assertTrue(
            is_grid_aligned(aware, slip_profile).ok,
            is_grid_aligned(aware, slip_profile).errors,
        )
        self.assertGreaterEqual(
            aware["metadata"]["validity_guard_substitutions"], 1
        )
        # Deterministic, and the wound site is still filled.
        again = repair_with_wound_sites(
            damaged, biased_model, slip_profile=slip_profile
        )
        self.assertEqual(aware["cells"], again["cells"])

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
            {"no_repair", "role_prior", "trained", "site_aware", "assisted"},
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
        self.assertGreater(
            arms["site_aware"]["mean_final_overlap"],
            arms["no_repair"]["mean_final_overlap"],
        )
        # The wound-site arm never overgrows, so its one-sided overlap and
        # two-sided agreement coincide by construction.
        self.assertEqual(
            arms["site_aware"]["mean_final_overlap"],
            arms["site_aware"]["mean_final_structural_agreement"],
        )
        self.assertIn(
            "site_aware_meets_assisted_stability_bar",
            report["decision"]["thresholds"],
        )
        self.assertIsInstance(
            report["decision"]["thresholds"][
                "site_aware_meets_assisted_stability_bar"
            ],
            bool,
        )
        self.assertIn(
            report["decision"]["status"],
            {
                "promote_less_assisted_repair",
                "wound_signal_repair_meets_bar",
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
                2 * 5,
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
