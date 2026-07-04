"""Parity pin: lab validator vs promoted mecha_engine.genome validator.

Runs the Stage 0 lab validator (flat import, the authoritative research
invariants) and the promoted package validator (mecha_engine.genome through
the package src layout) over the full frozen 250-grid corpus
(data/seed_grids: 50, data/invalid_grids: 200) and asserts identical
outcomes. Direction note: labs may import the package for regression
evidence; the reverse (package importing labs) stays forbidden by the
genome contract gate and the traceability matrix, and this file lives on
the lab side precisely so the package tree keeps zero lab references.
"""

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

from validator import validate_grid_file as lab_validate_grid_file  # noqa: E402

from mecha_engine.genome import (  # noqa: E402
    validate_grid_file as package_validate_grid_file,
)


SEED_DIR = REPO_ROOT / "data" / "seed_grids"
INVALID_DIR = REPO_ROOT / "data" / "invalid_grids"


def _corpus_outcomes(validate_file, directory: Path) -> dict[str, tuple[bool, list[str]]]:
    outcomes = {}
    for path in sorted(directory.glob("*.json")):
        result = validate_file(path)
        outcomes[path.name] = (result.ok, list(result.errors))
    return outcomes


class PackageGenomeParityTests(unittest.TestCase):
    def test_seed_corpus_outcomes_identical(self):
        lab = _corpus_outcomes(lab_validate_grid_file, SEED_DIR)
        package = _corpus_outcomes(package_validate_grid_file, SEED_DIR)

        self.assertEqual(50, len(lab))
        self.assertEqual(lab, package)
        self.assertTrue(all(ok for ok, _ in package.values()))

    def test_invalid_corpus_outcomes_identical(self):
        lab = _corpus_outcomes(lab_validate_grid_file, INVALID_DIR)
        package = _corpus_outcomes(package_validate_grid_file, INVALID_DIR)

        self.assertEqual(200, len(lab))
        self.assertEqual(lab, package)
        self.assertTrue(all(not ok for ok, _ in package.values()))
        self.assertTrue(all(errors for _, errors in package.values()))

    def test_full_corpus_ok_and_error_count_totals_match(self):
        lab_ok = 0
        lab_error_total = 0
        package_ok = 0
        package_error_total = 0
        for directory in (SEED_DIR, INVALID_DIR):
            for name, (ok, errors) in _corpus_outcomes(
                lab_validate_grid_file, directory
            ).items():
                lab_ok += int(ok)
                lab_error_total += len(errors)
            for name, (ok, errors) in _corpus_outcomes(
                package_validate_grid_file, directory
            ).items():
                package_ok += int(ok)
                package_error_total += len(errors)

        self.assertEqual(50, package_ok)
        self.assertEqual(lab_ok, package_ok)
        self.assertEqual(lab_error_total, package_error_total)


if __name__ == "__main__":
    unittest.main()
