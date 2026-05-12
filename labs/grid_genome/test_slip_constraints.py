import unittest

from constrained_generator import build_constrained_corpus, run_baseline
from corpus_builder import build_seed_grids
from slip import is_grid_aligned, validate_slip


def valid_slip():
    return {
        "slip_version": "0.1.0",
        "profile_id": "slip_lcd_seed",
        "name": "LCD Seed Companion",
        "grid": {
            "allowed_palettes": ["lcd_green"],
            "body_mass_min": 4,
            "body_mass_max": 24,
            "required_organ_roles": ["sensor", "expression"],
        },
        "mutation": {
            "cell_mutation_rate_max": 0.15,
            "organ_shift_rate_max": 0.05,
            "palette_shift_rate_max": 0.05,
            "symmetry_break_rate_max": 0.05,
        },
        "behavior": {
            "curiosity": 0.6,
            "neediness": 0.4,
            "sleepiness": 0.5,
        },
        "survival_weights": {
            "stability": 0.5,
            "novelty": 0.25,
            "bond": 0.25,
        },
    }


class SlipConstraintTests(unittest.TestCase):
    def test_valid_slip_profile_passes(self):
        result = validate_slip(valid_slip())

        self.assertTrue(result.ok, result.errors)

    def test_invalid_slip_profile_rejects_bad_weights(self):
        profile = valid_slip()
        profile["behavior"]["curiosity"] = 1.2

        result = validate_slip(profile)

        self.assertFalse(result.ok)
        self.assertIn("behavior curiosity outside 0..1: 1.2", result.errors)

    def test_slip_constrained_generation_outputs_valid_aligned_grids(self):
        profile = valid_slip()

        generated = build_constrained_corpus(
            build_seed_grids(), count=50, rng_seed=313, slip=profile
        )
        report = run_baseline(generated)

        self.assertEqual(50, report["candidate_count"])
        self.assertEqual(50, report["valid_count"])
        for grid in generated:
            with self.subTest(grid_id=grid["grid_id"]):
                self.assertTrue(is_grid_aligned(grid, profile).ok)


if __name__ == "__main__":
    unittest.main()
