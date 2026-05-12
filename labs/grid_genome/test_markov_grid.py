import unittest

from corpus_builder import build_seed_grids
from markov_grid import build_markov_corpus, generate_grid, run_baseline, train_model
from validator import validate_grid


class MarkovGridTests(unittest.TestCase):
    def test_train_model_collects_local_transitions(self):
        model = train_model(build_seed_grids())

        self.assertGreater(model["global_total"], 0)
        self.assertIn(("START", "START"), model["transitions"])

    def test_generate_grid_returns_grid_genome(self):
        model = train_model(build_seed_grids())

        grid = generate_grid(model, grid_id="mg_markov_test", rng_seed=123)

        self.assertEqual("mg_markov_test", grid["grid_id"])
        self.assertEqual([8, 8], grid["grid_size"])
        self.assertIn("cells", grid)
        self.assertIsInstance(validate_grid(grid).ok, bool)

    def test_build_markov_corpus_creates_100_candidates(self):
        generated = build_markov_corpus(build_seed_grids(), count=100, rng_seed=123)

        self.assertEqual(100, len(generated))
        self.assertEqual(100, len({grid["grid_id"] for grid in generated}))

    def test_run_baseline_reports_counts(self):
        generated = build_markov_corpus(build_seed_grids(), count=100, rng_seed=123)

        report = run_baseline(generated)

        self.assertEqual(100, report["candidate_count"])
        self.assertEqual(100, report["valid_count"] + report["invalid_count"])


if __name__ == "__main__":
    unittest.main()
