"""Parity pin: lab constrained generator vs promoted mecha_engine.generation.

Runs the Stage 0 lab generator (flat import, the authoritative research
behavior, including the 2026-07-04 mutation-temperature jitter) and the
promoted package generator (mecha_engine.generation through the package src
layout) over the same seed corpus, RNG seeds, and SLIP profile, and asserts
byte-identical grids on every key except ``metadata``.

Documented equivalence scope: the package surface
(``generate_batch(seed_grids, count, slip_profile, rng_seed)``) maps onto the
lab entry point (``build_constrained_corpus(seed_grids, count, rng_seed,
slip)``) with identical candidate naming and RNG consumption, so grid_id,
parent_grid_id, grid_size, cells, organs, palette, mutation, and lineage are
compared for full equality. Only ``metadata`` intentionally diverges: the
package records its own source label plus the generation trace required by
``explain_generation`` (the lab records the lab source label); the shared
``metadata.rng_seed`` value is still asserted equal.

Direction note: labs may import the package for regression evidence; the
reverse (package importing labs) stays forbidden by the generation contract
gate and the traceability matrix, and this file lives on the lab side
precisely so the package tree keeps zero lab references.
"""

import json
import sys
import unittest
from pathlib import Path


LAB_DIR = Path(__file__).resolve().parent
REPO_ROOT = LAB_DIR.parents[1]
PACKAGE_SRC = REPO_ROOT / "packages" / "mecha_engine" / "src"
if str(LAB_DIR) not in sys.path:
    sys.path.insert(0, str(LAB_DIR))
if str(PACKAGE_SRC) not in sys.path:
    sys.path.insert(0, str(PACKAGE_SRC))

from constrained_generator import build_constrained_corpus  # noqa: E402
from corpus_builder import build_seed_grids  # noqa: E402

from mecha_engine.generation import generate_batch  # noqa: E402
from mecha_engine.genome import grid_signature  # noqa: E402


SEMANTIC_KEYS = [
    "grid_id",
    "schema_version",
    "parent_grid_id",
    "grid_size",
    "cells",
    "organs",
    "palette",
    "mutation",
    "lineage",
]


def load_lcd_slip() -> dict:
    return json.loads(
        (REPO_ROOT / "data" / "slips" / "valid" / "slip_lcd_seed.json").read_text(
            encoding="utf-8"
        )
    )


def _without_metadata(grid: dict) -> dict:
    return {key: value for key, value in grid.items() if key != "metadata"}


class PackageGenerationParityTests(unittest.TestCase):
    def assert_corpora_semantically_identical(self, lab_corpus, package_corpus):
        self.assertEqual(len(lab_corpus), len(package_corpus))
        for lab_grid, package_grid in zip(lab_corpus, package_corpus):
            with self.subTest(grid_id=lab_grid["grid_id"]):
                self.assertEqual(set(SEMANTIC_KEYS) | {"metadata"}, set(lab_grid))
                self.assertEqual(
                    _without_metadata(lab_grid), _without_metadata(package_grid)
                )
                # The package signature covers cells, organs, palette, grid
                # size, and schema version; equality pins semantic identity.
                self.assertEqual(
                    grid_signature(lab_grid), grid_signature(package_grid)
                )
                self.assertEqual(
                    lab_grid["metadata"]["rng_seed"],
                    package_grid["metadata"]["rng_seed"],
                )

    def test_unconstrained_corpus_parity_100_candidates(self):
        seeds = build_seed_grids()
        lab_corpus = build_constrained_corpus(seeds, count=100, rng_seed=77)
        package_corpus = generate_batch(build_seed_grids(), 100, rng_seed=77)

        self.assert_corpora_semantically_identical(lab_corpus, package_corpus)

    def test_rich_alphabet_corpus_parity_24_candidates(self):
        # DR 0038: the vocabulary-complete alphabet mirrors verbatim —
        # trained on the RICH 16x16 seeds, lab and package emit
        # semantically identical corpora (motion trio included).
        from corpus_builder import build_seed_grids_16

        seeds = build_seed_grids_16()
        lab_corpus = build_constrained_corpus(seeds, count=24, rng_seed=41)
        package_corpus = generate_batch(
            build_seed_grids_16(), 24, rng_seed=41
        )

        self.assert_corpora_semantically_identical(lab_corpus, package_corpus)
        emitted = {
            cell["role"]
            for grid in package_corpus
            for cell in grid["cells"]
        }
        self.assertTrue(emitted & {"limb", "joint", "decoration"})

    def test_resample_temperature_parity_and_default_identity(self):
        # DR 0038's rider mirrors: the knob unset is byte-identical at
        # both sites; set, both batch surfaces agree with each other
        # (the batch paths share the parent-selection RNG consumption).
        from corpus_builder import build_seed_grids_16
        from mecha_engine.generation import (
            generate_candidate,
            train_generation_model,
        )

        seeds = build_seed_grids_16()
        lab_hot = build_constrained_corpus(
            seeds, count=6, rng_seed=7, resample_temperature=1.5
        )
        package_hot = generate_batch(
            build_seed_grids_16(), 6, rng_seed=7, resample_temperature=1.5
        )
        self.assert_corpora_semantically_identical(lab_hot, package_hot)

        package_model = train_generation_model(seeds)
        parent = seeds[0]
        self.assertEqual(
            grid_signature(generate_candidate(parent, package_model, rng_seed=7)),
            grid_signature(
                generate_candidate(
                    parent, package_model, rng_seed=7, resample_temperature=None
                )
            ),
        )
        with self.assertRaises(ValueError):
            generate_candidate(
                parent, package_model, rng_seed=7, resample_temperature=9.0
            )

    def test_slip_constrained_corpus_parity_50_candidates(self):
        profile = load_lcd_slip()
        seeds = build_seed_grids()
        lab_corpus = build_constrained_corpus(
            seeds, count=50, rng_seed=313, slip=load_lcd_slip()
        )
        package_corpus = generate_batch(
            build_seed_grids(), 50, slip_profile=profile, rng_seed=313
        )

        self.assert_corpora_semantically_identical(lab_corpus, package_corpus)

    def test_mutation_temperature_jitter_parity(self):
        # The deterministic mutation-temperature jitter (review finding
        # L-12) must reproduce the lab's per-candidate mutation vectors
        # exactly, and the corpus must not collapse to one shared vector.
        lab_corpus = build_constrained_corpus(build_seed_grids(), count=20, rng_seed=77)
        package_corpus = generate_batch(build_seed_grids(), 20, rng_seed=77)

        lab_vectors = [tuple(sorted(grid["mutation"].items())) for grid in lab_corpus]
        package_vectors = [
            tuple(sorted(grid["mutation"].items())) for grid in package_corpus
        ]
        self.assertEqual(lab_vectors, package_vectors)
        self.assertGreater(len(set(package_vectors)), 1)


if __name__ == "__main__":
    unittest.main()
