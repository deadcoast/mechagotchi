import unittest

from constrained_generator import build_constrained_corpus
from corpus_builder import build_seed_grids
from darwin_archive import (
    build_map_elites_archive,
    compare_with_scalar_baseline,
    descriptor_for_grid,
    score_grid,
)


class DarwinArchiveTests(unittest.TestCase):
    def test_descriptor_for_grid_returns_niche_coordinates(self):
        grid = build_seed_grids()[0]

        descriptor = descriptor_for_grid(grid)

        self.assertEqual(3, len(descriptor))
        self.assertTrue(all(isinstance(value, int) for value in descriptor))

    def test_score_grid_returns_bounded_fitness(self):
        grid = build_seed_grids()[0]

        score = score_grid(grid)

        self.assertGreaterEqual(score, 0)
        self.assertLessEqual(score, 1)

    def test_archive_keeps_only_best_elite_per_niche(self):
        candidates = build_constrained_corpus(build_seed_grids(), count=60, rng_seed=505)

        archive = build_map_elites_archive(candidates)

        self.assertEqual(len(archive["elites"]), archive["occupied_niches"])
        self.assertGreater(archive["occupied_niches"], 1)
        for elite in archive["elites"].values():
            self.assertIn("grid_id", elite)
            self.assertIn("fitness", elite)
            self.assertIn("descriptor", elite)

    def test_map_elites_coverage_beats_scalar_top_selection(self):
        candidates = build_constrained_corpus(build_seed_grids(), count=100, rng_seed=606)

        comparison = compare_with_scalar_baseline(candidates, top_k=20)

        self.assertGreater(
            comparison["map_elites_occupied_niches"],
            comparison["scalar_top_occupied_niches"],
        )


if __name__ == "__main__":
    unittest.main()
