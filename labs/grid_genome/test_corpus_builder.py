import unittest

from corpus_builder import build_invalid_grids, build_seed_grids
from validator import validate_grid


class CorpusBuilderTests(unittest.TestCase):
    def test_builds_50_valid_seed_grids(self):
        seeds = build_seed_grids()

        self.assertEqual(50, len(seeds))
        self.assertEqual(50, len({grid["grid_id"] for grid in seeds}))
        for grid in seeds:
            with self.subTest(grid_id=grid["grid_id"]):
                self.assertTrue(validate_grid(grid).ok, validate_grid(grid).errors)

    def test_builds_200_invalid_counterexamples(self):
        invalid_grids = build_invalid_grids(build_seed_grids())

        self.assertEqual(200, len(invalid_grids))
        self.assertEqual(200, len({grid["grid_id"] for grid in invalid_grids}))
        for grid in invalid_grids:
            with self.subTest(grid_id=grid["grid_id"]):
                self.assertFalse(validate_grid(grid).ok)


if __name__ == "__main__":
    unittest.main()
