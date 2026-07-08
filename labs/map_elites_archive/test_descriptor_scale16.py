"""16x16 descriptor-bin gates (cycle 09 A4, DR 0029/0030 pattern).

The body-mass bin edges ([6, 9, 12, 16]) are 8x8 cell counts: at 16x16
every corpus creature (core 18-85) landed in the top bin and the mass
axis collapsed. These tests pin the reference-canvas scaling
(edge * w*h // 64 — an exact identity at 8x8) at all three binning
sites: the lab extended descriptors, the lab darwin baseline, and the
promoted package archive — in agreement with each other.
"""

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
from darwin_archive import descriptor_for_grid  # noqa: E402
from extended_descriptors import extended_descriptor_for_grid  # noqa: E402

from mecha_engine.archive import descriptor_for_candidate  # noqa: E402


def _metrics_bundle() -> dict:
    return {
        "readability": 0.5,
        "lifecycle": {
            "survival_ratio": 1.0,
            "need_balance": 0.5,
            "recovery_events": 0,
            "final_state": {"bond": 0.5},
        },
    }


def _core_mass(grid: dict) -> int:
    return sum(
        len(organ["cells"])
        for organ in grid["organs"].values()
        if organ.get("role") == "body_core" and organ.get("required") is True
    )


def _expected_mass_bin(mass: int, area: int) -> int:
    edges = [edge * area // 64 for edge in [6, 9, 12, 16]]
    for index, edge in enumerate(edges):
        if mass <= edge:
            return index
    return len(edges)


class DescriptorScale16Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.seeds_16 = build_seed_grids_16()
        cls.seeds_8 = build_seed_grids()

    def test_mass_axis_spreads_at_16x16_in_the_package_archive(self):
        bins = set()
        for grid in self.seeds_16:
            descriptor = descriptor_for_candidate(
                {"grid": grid}, _metrics_bundle(), mode="baseline"
            )
            with self.subTest(grid_id=grid["grid_id"]):
                self.assertEqual(
                    _expected_mass_bin(_core_mass(grid), 256), descriptor[0]
                )
            bins.add(descriptor[0])
        # The re-derivation's whole point: the axis must not collapse.
        self.assertGreaterEqual(len(bins), 4)

    def test_darwin_baseline_agrees_with_the_package_at_16x16(self):
        for grid in self.seeds_16[:10]:
            with self.subTest(grid_id=grid["grid_id"]):
                lab = descriptor_for_grid(grid)
                package = descriptor_for_candidate(
                    {"grid": grid}, _metrics_bundle(), mode="baseline"
                )
                self.assertEqual(lab, tuple(package))

    def test_extended_lab_descriptor_uses_the_scaled_mass_edges(self):
        for grid in self.seeds_16[:10]:
            with self.subTest(grid_id=grid["grid_id"]):
                record = extended_descriptor_for_grid(grid)
                self.assertEqual(
                    _expected_mass_bin(_core_mass(grid), 256),
                    record["values"][0],
                )

    def test_8x8_descriptors_are_the_historical_identity(self):
        # The scaling is an exact identity at the reference canvas: the
        # historical edges apply unchanged to the proven corpus.
        for grid in self.seeds_8[:10]:
            with self.subTest(grid_id=grid["grid_id"]):
                lab = descriptor_for_grid(grid)
                self.assertEqual(
                    _expected_mass_bin(_core_mass(grid), 64), lab[0]
                )
                package = descriptor_for_candidate(
                    {"grid": grid}, _metrics_bundle(), mode="baseline"
                )
                self.assertEqual(lab, tuple(package))


if __name__ == "__main__":
    unittest.main()
