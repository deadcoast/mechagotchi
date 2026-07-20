"""Cycle 19 I5: behavior_neediness at 16x16 — measured, then judged.

The Phase-E gate named the remainder: behavior_neediness is
MASS-DOMINATED at 16x16 (the -0.01 * body_mass term was calibrated
against 8x8 masses; 16x16 masses are ~4x larger and swamp the sensor
signal). The candidate recalibration is the cycle 09 A4 pattern
exactly — reference-canvas scaling, an EXACT identity at 8x8:

    mass_term = body_mass * 0.01 * (64 / (width * height))

The lab measures both formulas over both committed seed corpora and
judges pre-registered gates on the engine's own numbers; a refuted
recalibration is a first-class finding.
"""

import json
import sys
import tempfile
import unittest
from pathlib import Path

LAB_DIR = Path(__file__).resolve().parent
if str(LAB_DIR) not in sys.path:
    sys.path.insert(0, str(LAB_DIR))

from neediness_scale16 import (  # noqa: E402
    build_neediness_scale_report,
    neediness_recalibrated,
    pearson,
    write_neediness_scale_artifacts,
)
from extended_descriptors import _behavior_neediness  # noqa: E402


class PearsonTests(unittest.TestCase):
    def test_pearson_matches_known_values(self):
        self.assertAlmostEqual(
            1.0, pearson([1, 2, 3], [2, 4, 6]), places=9
        )
        self.assertAlmostEqual(
            -1.0, pearson([1, 2, 3], [6, 4, 2]), places=9
        )
        # A constant series has no variance: correlation is undefined,
        # reported as 0.0 rather than fabricated.
        self.assertEqual(0.0, pearson([1, 1, 1], [2, 4, 6]))


class RecalibrationTests(unittest.TestCase):
    def test_recalibrated_is_the_exact_identity_at_8x8(self):
        grid = _grid(width=8, height=8, core_cells=12, sensors=2)
        self.assertEqual(
            _behavior_neediness(grid, None),
            neediness_recalibrated(grid, None),
        )

    def test_recalibrated_mass_term_scales_by_reference_canvas(self):
        # Same mass fraction at 16x16 as 12/64 at 8x8 => same value.
        small = _grid(width=8, height=8, core_cells=12, sensors=2)
        large = _grid(width=16, height=16, core_cells=48, sensors=2)
        self.assertAlmostEqual(
            neediness_recalibrated(small, None),
            neediness_recalibrated(large, None),
            places=9,
        )

    def test_slip_prior_still_shifts_only(self):
        grid = _grid(width=16, height=16, core_cells=48, sensors=2)
        base = neediness_recalibrated(grid, None)
        shifted = neediness_recalibrated(
            grid, {"behavior": {"neediness": 1.0}}
        )
        self.assertAlmostEqual(base + 0.1, shifted, places=9)


class ApplicationTests(unittest.TestCase):
    """The recalibration decision applies at BOTH parity sites —

    the lab's extended descriptors and the promoted package — and
    they agree with the measurement lab's own formula verbatim.
    """

    def test_both_parity_sites_carry_the_recalibrated_formula(self):
        package_src = LAB_DIR.parents[1] / "packages" / "mecha_engine" / "src"
        if str(package_src) not in sys.path:
            sys.path.insert(0, str(package_src))
        from mecha_engine.archive._metrics import (
            behavior_neediness as package_neediness,
        )

        grid = _grid(width=16, height=16, core_cells=48, sensors=2)
        expected = neediness_recalibrated(grid, None)
        self.assertEqual(expected, _behavior_neediness(grid, None))
        self.assertEqual(expected, package_neediness(grid, None))


class ReportTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.report = build_neediness_scale_report()

    def test_the_measurement_covers_both_scales_and_both_formulas(self):
        for formula in ("original", "recalibrated"):
            for scale in ("scale8", "scale16"):
                block = self.report[formula][scale]
                self.assertGreater(block["grid_count"], 0)
                self.assertIn("pearson_mass", block)
                self.assertIn("pearson_sensors", block)
                self.assertIn("distinct_bins", block)

    def test_the_gates_are_judged_on_the_measured_numbers(self):
        gates = self.report["gates"]
        original_16 = self.report["original"]["scale16"]
        recal_16 = self.report["recalibrated"]["scale16"]
        self.assertEqual(
            gates["identity_8x8"],
            self.report["recalibrated"]["scale8"]["max_abs_diff_vs_original"]
            == 0.0,
        )
        self.assertEqual(
            gates["mass_domination_reduced"],
            abs(recal_16["pearson_mass"]) < abs(original_16["pearson_mass"]),
        )
        self.assertEqual(
            gates["sensor_signal_present"],
            recal_16["pearson_sensors"] > 0,
        )
        expected = (
            "recalibrate"
            if all(
                gates[k]
                for k in (
                    "identity_8x8",
                    "mass_domination_reduced",
                    "sensor_signal_present",
                )
            )
            else "remainder_stands"
        )
        self.assertEqual(expected, self.report["decision"])

    def test_artifacts_are_written(self):
        with tempfile.TemporaryDirectory() as tmp:
            write_neediness_scale_artifacts(Path(tmp), self.report)
            payload = json.loads(
                (Path(tmp) / "neediness_scale16_stage0.json").read_text(
                    encoding="utf-8"
                )
            )
        self.assertEqual(
            "neediness_scale16_stage0", payload["artifact_id"]
        )
        self.assertIn("blocked_states", payload)


def _grid(
    *, width: int, height: int, core_cells: int, sensors: int
) -> dict:
    """The lab descriptor helpers' grid shape (extended_descriptors):

    cells = a list of {x, y, organ, role} dicts; sensors live under
    organs.sensors.cells; the canvas is grid_size.
    """
    cells = []
    sensor_ids = []
    index = 0
    for _ in range(core_cells):
        cells.append(
            {"x": index % width, "y": index // width, "organ": "core", "role": "core"}
        )
        index += 1
    for sensor in range(sensors):
        cell_id = f"s{sensor}"
        cells.append(
            {"x": index % width, "y": index // width, "organ": "sensors", "role": "sensor"}
        )
        sensor_ids.append(cell_id)
        index += 1
    return {
        "grid_id": f"synthetic_{width}x{height}",
        "grid_size": [width, height],
        "cells": cells,
        "organs": {"sensors": {"cells": sensor_ids}},
    }


if __name__ == "__main__":
    unittest.main()
