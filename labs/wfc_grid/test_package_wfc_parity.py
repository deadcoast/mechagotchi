"""Parity pin: the WFC lab vs the promoted mecha_engine.generation.wfc.

B3 (DR 0031) adopted the bake-off winner into the package as an
additive seam. This lab-side pin holds the port verbatim: identical
trained models and identical candidate corpora for the same corpus and
seeds. Direction note: labs may import the package for regression
evidence; the reverse stays forbidden by the boundary scan.
"""

import json
import sys
import unittest
from pathlib import Path


LAB_DIR = Path(__file__).resolve().parent
REPO_ROOT = LAB_DIR.parents[1]
GRID_GENOME = REPO_ROOT / "labs" / "grid_genome"
PACKAGE_SRC = REPO_ROOT / "packages" / "mecha_engine" / "src"
for path in [LAB_DIR, GRID_GENOME, PACKAGE_SRC]:
    if str(path) not in sys.path:
        sys.path.insert(0, str(path))

from corpus_builder import build_seed_grids, build_seed_grids_16  # noqa: E402
from wfc_grid import (  # noqa: E402
    build_wfc_corpus as lab_build_wfc_corpus,
    split_corpus,
    train_wfc_model as lab_train_wfc_model,
)

from mecha_engine.generation import (  # noqa: E402
    build_wfc_corpus as package_build_wfc_corpus,
    generate_wfc_grid as package_generate_wfc_grid,
    train_wfc_model as package_train_wfc_model,
)


class PackageWfcParityTests(unittest.TestCase):
    train_grids: list[dict]

    @classmethod
    def setUpClass(cls):
        cls.train_grids = split_corpus(build_seed_grids_16())[0]
        cls.lab_model = lab_train_wfc_model(cls.train_grids)
        cls.package_model = package_train_wfc_model(cls.train_grids)

    def test_trained_models_are_identical(self):
        self.assertEqual(
            json.dumps(self.lab_model, sort_keys=True),
            json.dumps(self.package_model, sort_keys=True),
        )

    def test_generated_corpora_are_identical(self):
        lab_corpus = lab_build_wfc_corpus(
            self.lab_model, count=25, rng_seed=1030
        )
        package_corpus = package_build_wfc_corpus(
            self.package_model, count=25, rng_seed=1030
        )
        self.assertEqual(lab_corpus, package_corpus)

    def test_single_candidate_parity_and_package_source_label(self):
        candidate = package_generate_wfc_grid(
            self.package_model, grid_id="mg_wfc_pin", rng_seed=9
        )
        lab_candidate = None
        from wfc_grid import generate_wfc_grid as lab_generate

        lab_candidate = lab_generate(
            self.lab_model, grid_id="mg_wfc_pin", rng_seed=9
        )
        self.assertEqual(lab_candidate, candidate)
        self.assertEqual("wfc_grid_lab", candidate["metadata"]["source"])

    def test_mixed_size_training_raises_identically(self):
        mixed = [build_seed_grids()[0], self.train_grids[0]]
        with self.assertRaises(ValueError) as lab_error:
            lab_train_wfc_model(mixed)
        with self.assertRaises(ValueError) as package_error:
            package_train_wfc_model(mixed)
        self.assertEqual(str(lab_error.exception), str(package_error.exception))


if __name__ == "__main__":
    unittest.main()
