"""Lab-side parity pin: ``runtime/_cubff.py`` mirrors the lab authority
verbatim (R2.5, decision record 0020 — the ``_slip`` mirror discipline).

Labs may import the package; that is how a port is pinned to lab
semantics. If the authority (``cubff_transducer.py``) changes, the
package mirror must be resynced verbatim — this suite is the drift
guard. It also pins the promoted multiplier formula and constants to
the R2 lab loop's."""

import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
for path in [
    Path(__file__).resolve().parent,
    ROOT / "labs" / "runtime_integration",
    ROOT / "packages" / "mecha_engine" / "src",
]:
    if str(path) not in sys.path:
        sys.path.insert(0, str(path))

import importlib  # noqa: E402

import cubff_transducer as lab_authority  # noqa: E402
import mecha_engine_runtime_loop as lab_loop  # noqa: E402

package_mirror = importlib.import_module("mecha_engine.runtime._cubff")
# The package re-exports ``evolve`` the function over the submodule
# name, so the module must be resolved explicitly.
package_evolve = importlib.import_module("mecha_engine.runtime.evolve")


EDGE_SNAPSHOTS = [
    {},  # everything missing
    {"snapshot_id": "empty_tape", "tape": [], "replication_scores": []},
    {
        "snapshot_id": "strings_and_junk",
        "tape": ["7", 3.5, None, 12, -4, 999],
        "replication_scores": ["64", None, 12],
        "brotli_size": "not-a-number",
        "lineage_events": [{"parent": 1, "child": 2}, "junk"],
        "program_size": 0,
    },
    {
        "snapshot_id": "single_symbol",
        "tape": [5] * 64,
        "replication_scores": [64] * 8,
        "brotli_size": 4,
        "lineage_events": [],
        "program_size": 64,
    },
]


class CubffMirrorParityTests(unittest.TestCase):
    def setUp(self):
        self.snapshots = (
            lab_authority.build_synthetic_snapshots(12, rng_seed=20260707)
            + EDGE_SNAPSHOTS
        )

    def test_extract_cubff_features_identical(self):
        for snapshot in self.snapshots:
            self.assertEqual(
                lab_authority.extract_cubff_features(snapshot),
                package_mirror.extract_cubff_features(snapshot),
                snapshot.get("snapshot_id", "<missing>"),
            )

    def test_features_to_traits_identical(self):
        for snapshot in self.snapshots:
            features = lab_authority.extract_cubff_features(snapshot)
            self.assertEqual(
                lab_authority.features_to_traits(features),
                package_mirror.features_to_traits(features),
                snapshot.get("snapshot_id", "<missing>"),
            )


class PromotedFormulaParityTests(unittest.TestCase):
    def test_constants_match_the_lab_loop(self):
        self.assertEqual(
            lab_loop.CUBFF_PRESSURE_GAIN, package_evolve.CUBFF_PRESSURE_GAIN
        )
        self.assertEqual(
            lab_loop.CUBFF_MULTIPLIER_BAND,
            package_evolve.CUBFF_MULTIPLIER_BAND,
        )

    def test_generation_pressure_identical(self):
        for snapshot in lab_authority.build_synthetic_snapshots(
            8, rng_seed=20260707
        ):
            self.assertEqual(
                lab_loop._cubff_generation_pressure(snapshot),
                package_evolve._cubff_generation_pressure(snapshot),
                snapshot["snapshot_id"],
            )


if __name__ == "__main__":
    unittest.main()
