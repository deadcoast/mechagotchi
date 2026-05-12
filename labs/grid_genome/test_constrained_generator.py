import unittest

from constrained_generator import (
    build_constrained_corpus,
    generate_constrained_grid,
    run_baseline,
    train_constraints,
)
from corpus_builder import build_seed_grids
from validator import validate_grid


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


if __name__ == "__main__":
    unittest.main()
