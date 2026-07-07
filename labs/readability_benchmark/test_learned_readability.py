import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
GRID_GENOME = ROOT / "labs" / "grid_genome"
if str(GRID_GENOME) not in sys.path:
    sys.path.insert(0, str(GRID_GENOME))

from corpus_builder import build_seed_grids  # noqa: E402

from learned_readability import (  # noqa: E402
    DEGRADATION_FAMILIES,
    build_degradation_pairs,
    build_learned_readability_report,
    extract_readability_features,
    learned_readability_score,
    train_pairwise_ranker,
    write_learned_readability_artifacts,
)
from readability_benchmark import score_readability  # noqa: E402


GRIDS = build_seed_grids()


class FeatureExtractionTests(unittest.TestCase):
    def test_features_are_raw_measurables_not_the_heuristic_mix(self):
        features = extract_readability_features(GRIDS[0])
        self.assertEqual(
            [
                "inverse_component_count",
                "body_mass_ratio",
                "silhouette_entropy",
                "symmetry_score",
                "organ_detectability",
                "palette_contrast",
                "animation_anchor_coverage",
            ],
            list(features),
        )
        for name, value in features.items():
            self.assertIsInstance(value, float, name)
        # The heuristic's blended score must NOT be a feature — the
        # model learns its own mix or it isn't learning.
        self.assertNotIn("proxy_readability_score", features)


class DegradationPairTests(unittest.TestCase):
    def test_every_family_produces_physics_verified_pairs(self):
        self.assertEqual(
            [
                "contrast_collapse",
                "organ_scatter",
                "silhouette_noise",
                "anchor_erosion",
            ],
            list(DEGRADATION_FAMILIES),
        )
        pairs = build_degradation_pairs(
            GRIDS[:10], pairs_per_family=2, rng_seed=11
        )
        families = {pair["family"] for pair in pairs}
        self.assertEqual(set(DEGRADATION_FAMILIES), families)
        for pair in pairs:
            metric = DEGRADATION_FAMILIES[pair["family"]]
            better = pair["better_features"]
            worse = pair["worse_features"]
            # The physics label: the targeted metric strictly decreased.
            self.assertGreater(
                better[metric], worse[metric],
                f"{pair['family']} pair not physics-verified",
            )

    def test_pairs_are_deterministic(self):
        first = build_degradation_pairs(GRIDS[:6], pairs_per_family=2, rng_seed=7)
        second = build_degradation_pairs(GRIDS[:6], pairs_per_family=2, rng_seed=7)
        self.assertEqual(first, second)


class TrainerTests(unittest.TestCase):
    def test_the_model_actually_learns(self):
        pairs = build_degradation_pairs(GRIDS[:20], pairs_per_family=2, rng_seed=3)
        model = train_pairwise_ranker(pairs, rng_seed=3)
        # Weights moved away from the zero initialization.
        self.assertTrue(any(abs(w) > 1e-3 for w in model["weights"].values()))
        # And the trained model ranks its own training pairs well
        # above chance.
        self.assertGreater(model["train_accuracy"], 0.8)

    def test_training_is_deterministic(self):
        pairs = build_degradation_pairs(GRIDS[:10], pairs_per_family=2, rng_seed=3)
        first = train_pairwise_ranker(pairs, rng_seed=3)
        second = train_pairwise_ranker(pairs, rng_seed=3)
        self.assertEqual(first, second)

    def test_learned_score_is_a_float_from_learned_weights(self):
        pairs = build_degradation_pairs(GRIDS[:10], pairs_per_family=2, rng_seed=3)
        model = train_pairwise_ranker(pairs, rng_seed=3)
        score = learned_readability_score(GRIDS[0], model)
        self.assertIsInstance(score, float)


class ReportTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.report = build_learned_readability_report(rng_seed=20260706)

    def test_heldout_accuracy_well_above_chance(self):
        self.assertGreater(self.report["metrics"]["heldout_accuracy"], 0.75)

    def test_generalizes_to_an_unseen_degradation_family(self):
        loo = self.report["metrics"]["leave_one_family_out"]
        self.assertEqual(set(DEGRADATION_FAMILIES), set(loo))
        for family, entry in loo.items():
            # Trained WITHOUT this family's pairs, evaluated ON them:
            # above chance = the model learned readability, not the
            # degradation trick.
            self.assertGreater(
                entry["unseen_family_accuracy"], 0.5,
                f"no generalization to {family}",
            )

    def test_reports_agreement_with_heuristic_but_does_not_copy_it(self):
        metrics = self.report["metrics"]
        self.assertIn("heuristic_rank_agreement", metrics)
        weights = self.report["model"]["weights"]
        heuristic_mix = {
            "validity": 0.18, "component_score": 0.14,
            "body_mass_score": 0.12, "silhouette_score": 0.12,
            "symmetry_score": 0.1, "organ_detectability": 0.18,
            "palette_contrast": 0.1, "animation_anchor_coverage": 0.06,
        }
        self.assertNotEqual(set(heuristic_mix), set(weights))

    def test_anchored_score_discriminates_original_from_degraded(self):
        # Without the corpus anchor the sigmoid saturates at 1.0 for
        # every healthy grid; the anchored score must separate a grid
        # from its physics-verified foil.
        from learned_readability import (
            build_degradation_pairs,
            _DEGRADERS,
        )
        import random

        model = self.report["model"]
        self.assertIn("reference_features", model)
        rng = random.Random(5)
        grid = GRIDS[0]
        degraded = _DEGRADERS["contrast_collapse"](grid, rng)
        self.assertGreater(
            learned_readability_score(grid, model),
            learned_readability_score(degraded, model),
        )
        self.assertLess(learned_readability_score(grid, model), 1.0)

    def test_fallback_status_recorded_not_blocked(self):
        self.assertEqual(
            "learned_model_primary_manual_rating_fallback",
            self.report["readability_authority"],
        )
        self.assertIn("manual_calibration_check", self.report["closed_states"] + self.report["blocked_states"])

    def test_report_shape_and_artifacts(self):
        report = self.report
        for key in ["artifact_id", "status", "date", "purpose",
                    "source_artifacts", "closed_states", "blocked_states",
                    "decision", "next_research_step"]:
            self.assertIn(key, report)
        with tempfile.TemporaryDirectory() as tmp:
            write_learned_readability_artifacts(Path(tmp), report)
            out = Path(tmp) / "learned_readability_stage0.json"
            self.assertTrue(out.exists())


if __name__ == "__main__":
    unittest.main()
