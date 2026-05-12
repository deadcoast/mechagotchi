import unittest

from corpus_builder import build_seed_grids
from random_mutation import build_generated_corpus, mutate_grid, run_baseline
from validator import validate_grid


class RandomMutationTests(unittest.TestCase):
    def test_mutate_grid_creates_child_without_modifying_parent(self):
        parent = build_seed_grids()[0]
        original_cell_count = len(parent["cells"])

        child = mutate_grid(parent, mutation_index=0, rng_seed=123)

        self.assertNotEqual(parent["grid_id"], child["grid_id"])
        self.assertEqual(parent["grid_id"], child["parent_grid_id"])
        self.assertEqual(1, child["lineage"]["generation"])
        self.assertEqual(original_cell_count, len(parent["cells"]))

    def test_build_generated_corpus_creates_100_unique_children(self):
        generated = build_generated_corpus(build_seed_grids(), per_seed=2, rng_seed=123)

        self.assertEqual(100, len(generated))
        self.assertEqual(100, len({grid["grid_id"] for grid in generated}))
        self.assertEqual(
            100,
            sum(1 for grid in generated if grid["parent_grid_id"] is not None),
        )

    def test_run_baseline_reports_validation_counts(self):
        generated = build_generated_corpus(build_seed_grids(), per_seed=2, rng_seed=123)

        report = run_baseline(generated)

        self.assertEqual(100, report["candidate_count"])
        self.assertEqual(
            100,
            report["valid_count"] + report["invalid_count"],
        )
        self.assertGreater(report["invalid_count"], 0)
        for grid in generated:
            self.assertIsInstance(validate_grid(grid).ok, bool)


if __name__ == "__main__":
    unittest.main()
