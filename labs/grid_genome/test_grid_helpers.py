import unittest

import constrained_generator
import corpus_builder
import grid_helpers
import markov_grid
import random_mutation
import slip_profile_benchmark


class SharedHelperSingleSourceTests(unittest.TestCase):
    """Pin that former duplicate sites resolve to grid_helpers (L-04)."""

    def test_cell_is_shared(self):
        self.assertIs(corpus_builder._cell, grid_helpers._cell)

    def test_palettes_are_shared(self):
        self.assertIs(corpus_builder.PALETTES, grid_helpers.PALETTES)

    def test_run_baseline_is_shared_where_identical(self):
        self.assertIs(markov_grid.run_baseline, grid_helpers.run_baseline)
        self.assertIs(random_mutation.run_baseline, grid_helpers.run_baseline)

    def test_signature_is_shared(self):
        self.assertIs(constrained_generator._signature, grid_helpers.grid_signature)
        self.assertIs(slip_profile_benchmark._signature, grid_helpers.grid_signature)

    def test_weighted_sample_is_shared(self):
        self.assertIs(markov_grid._sample, grid_helpers.weighted_sample)
        self.assertIs(
            constrained_generator._weighted_sample, grid_helpers.weighted_sample
        )


class SharedHelperDivergenceTests(unittest.TestCase):
    """Pin the deliberate per-module divergences kept behind parameters."""

    def test_constrained_run_baseline_adds_unique_signatures_only(self):
        grids = corpus_builder.build_seed_grids()[:3]
        base = grid_helpers.run_baseline(grids)
        extended = constrained_generator.run_baseline(grids)

        self.assertNotIn("unique_signatures", base)
        self.assertEqual(3, extended["unique_signatures"])
        # Key order matters: reports are JSON-dumped verbatim.
        self.assertEqual(
            [
                "candidate_count",
                "valid_count",
                "invalid_count",
                "validity_rate",
                "unique_signatures",
                "error_counts",
            ],
            list(extended),
        )
        for key, value in base.items():
            self.assertEqual(value, extended[key])

    def test_strict_tokens_divergence(self):
        rows = ["Z" + "." * 7] + ["." * 8] * 7
        lenient = grid_helpers.grid_from_matrix(
            "mg_test_lenient", rows, "lcd_green", source="test"
        )
        self.assertEqual([], lenient["cells"])
        with self.assertRaises(ValueError):
            grid_helpers.grid_from_matrix(
                "mg_test_strict",
                rows,
                "lcd_green",
                source="test",
                strict_tokens=True,
            )
        with self.assertRaises(ValueError):
            corpus_builder._grid_from_blueprint("mg_test_strict", "lcd_green", rows)

    def test_rng_seed_metadata_only_when_provided(self):
        rows = ["." * 8] * 8
        without_seed = grid_helpers.grid_from_matrix(
            "mg_test_noseed", rows, "lcd_green", source="test"
        )
        with_seed = grid_helpers.grid_from_matrix(
            "mg_test_seed", rows, "lcd_green", source="test", rng_seed=0
        )
        self.assertNotIn("rng_seed", without_seed["metadata"])
        self.assertEqual(0, with_seed["metadata"]["rng_seed"])

    def test_module_wrappers_keep_their_labels(self):
        rows = [".BA.....", "..E.....", "..M....."] + ["." * 8] * 5
        markov = markov_grid._grid_from_matrix("mg_test_mk", rows, "lcd_green", 7)
        self.assertEqual("markov_grid_lab", markov["metadata"]["source"])
        self.assertEqual(
            ["markov_local_generation"], markov["lineage"]["mutation_events"]
        )
        self.assertEqual(0, markov["lineage"]["generation"])

        constrained = constrained_generator._grid_from_matrix(
            "mg_test_cg", rows, "lcd_green", 7, ["ev"], parent_grid_id="mg_seed_001"
        )
        self.assertEqual(
            "constrained_wfc_style_lab", constrained["metadata"]["source"]
        )
        self.assertEqual(["ev"], constrained["lineage"]["mutation_events"])
        self.assertEqual(1, constrained["lineage"]["generation"])
        self.assertEqual(["mg_seed_001"], constrained["lineage"]["ancestor_ids"])


if __name__ == "__main__":
    unittest.main()
