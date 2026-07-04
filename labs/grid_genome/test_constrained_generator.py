import json
import unittest
from pathlib import Path

from constrained_generator import (
    DEFAULT_MUTATION_RATE_CAPS,
    SLIP_MUTATION_CAP_KEYS,
    build_constrained_corpus,
    generate_constrained_grid,
    run_baseline,
    train_constraints,
)
from corpus_builder import build_seed_grids
from slip import is_grid_aligned
from validator import validate_grid


ROOT = Path(__file__).resolve().parents[2]


def load_lcd_slip() -> dict:
    return json.loads(
        (ROOT / "data" / "slips" / "valid" / "slip_lcd_seed.json").read_text(
            encoding="utf-8"
        )
    )


class ConstrainedGeneratorTests(unittest.TestCase):
    def test_train_constraints_collects_adjacency_rules(self):
        model = train_constraints(build_seed_grids())

        self.assertGreater(model["total_pairs"], 0)
        self.assertIn("right", model["adjacency"])
        self.assertIn("down", model["adjacency"])

    def test_generate_constrained_grid_returns_valid_grid(self):
        model = train_constraints(build_seed_grids())

        grid = generate_constrained_grid(
            model,
            build_seed_grids(),
            grid_id="mg_constrained_test",
            rng_seed=77,
        )

        self.assertEqual("mg_constrained_test", grid["grid_id"])
        self.assertTrue(validate_grid(grid).ok, validate_grid(grid).errors)

    def test_build_constrained_corpus_beats_random_validity_gate(self):
        generated = build_constrained_corpus(build_seed_grids(), count=100, rng_seed=77)
        report = run_baseline(generated)

        self.assertEqual(100, report["candidate_count"])
        self.assertGreater(report["valid_count"], 42)
        self.assertEqual(100, len({grid["grid_id"] for grid in generated}))

    def test_mutation_rate_jitter_is_deterministic_and_varies_per_candidate(self):
        # Review finding L-12: candidates must not all share one fixed
        # mutation vector, and the jitter must be reproducible per seed.
        first = build_constrained_corpus(build_seed_grids(), count=12, rng_seed=77)
        second = build_constrained_corpus(build_seed_grids(), count=12, rng_seed=77)

        self.assertEqual(first, second)
        vectors = {
            tuple(sorted(grid["mutation"].items())) for grid in first
        }
        self.assertGreater(len(vectors), 1)

    def test_jittered_mutation_rates_respect_default_caps_without_slip(self):
        generated = build_constrained_corpus(build_seed_grids(), count=12, rng_seed=77)

        for grid in generated:
            with self.subTest(grid_id=grid["grid_id"]):
                self.assertTrue(validate_grid(grid).ok, validate_grid(grid).errors)
                for rate_key, cap in DEFAULT_MUTATION_RATE_CAPS.items():
                    rate = grid["mutation"][rate_key]
                    self.assertGreater(rate, 0)
                    self.assertLessEqual(rate, cap)

    def test_jittered_mutation_rates_stay_slip_aligned(self):
        profile = load_lcd_slip()
        generated = build_constrained_corpus(
            build_seed_grids(), count=12, rng_seed=77, slip=profile
        )

        for grid in generated:
            with self.subTest(grid_id=grid["grid_id"]):
                alignment = is_grid_aligned(grid, profile)
                self.assertTrue(alignment.ok, alignment.errors)
                for rate_key, cap_key in SLIP_MUTATION_CAP_KEYS.items():
                    self.assertLessEqual(
                        grid["mutation"][rate_key], profile["mutation"][cap_key]
                    )


if __name__ == "__main__":
    unittest.main()
