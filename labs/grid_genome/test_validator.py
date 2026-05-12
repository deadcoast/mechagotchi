import json
import tempfile
import unittest
from pathlib import Path

from validator import validate_grid, validate_grid_file


def valid_grid():
    return {
        "grid_id": "mg_seed_test",
        "schema_version": "0.1.0",
        "parent_grid_id": None,
        "grid_size": [8, 8],
        "cells": [
            cell(3, 2, "body", "hard", organ="core", anchor=True),
            cell(4, 2, "body", "hard", organ="core"),
            cell(3, 3, "body", "hard", organ="core"),
            cell(4, 3, "body", "hard", organ="core"),
            cell(2, 3, "eye", "glass", organ="left_sensor"),
            cell(5, 3, "eye", "glass", organ="right_sensor"),
        ],
        "organs": {
            "core": {
                "role": "body_core",
                "cells": [[3, 2], [4, 2], [3, 3], [4, 3]],
                "required": True,
            },
            "left_sensor": {
                "role": "sensor",
                "cells": [[2, 3]],
                "required": True,
            },
            "right_sensor": {
                "role": "sensor",
                "cells": [[5, 3]],
                "required": True,
            },
        },
        "palette": {
            "palette_id": "lcd_green",
            "colors": ["#0b1f12", "#6fbf73", "#d7ffd9"],
            "background_index": 0,
        },
        "mutation": {
            "cell_mutation_rate": 0.05,
            "organ_shift_rate": 0.02,
            "palette_shift_rate": 0.01,
            "symmetry_break_rate": 0.01,
        },
        "lineage": {
            "generation": 0,
            "ancestor_ids": [],
            "mutation_events": [],
        },
    }


def cell(x, y, role, material, organ=None, anchor=False):
    return {
        "x": x,
        "y": y,
        "visual": "#6fbf73" if role != "eye" else "#d7ffd9",
        "role": role,
        "material": material,
        "mutation_weight": 0.1,
        "animation_anchor": anchor,
        "organ": organ,
        "stress": 0,
        "damage": 0,
        "locked": False,
    }


class GridValidatorTests(unittest.TestCase):
    def test_valid_grid_passes_core_invariants(self):
        result = validate_grid(valid_grid())

        self.assertTrue(result.ok, result.errors)
        self.assertEqual([], result.errors)

    def test_rejects_duplicate_cell_coordinates(self):
        grid = valid_grid()
        grid["cells"].append(dict(grid["cells"][0]))

        result = validate_grid(grid)

        self.assertFalse(result.ok)
        self.assertIn("duplicate coordinate: 3,2", result.errors)

    def test_rejects_out_of_bounds_cells(self):
        grid = valid_grid()
        grid["cells"][0]["x"] = 8

        result = validate_grid(grid)

        self.assertFalse(result.ok)
        self.assertIn("cell out of bounds: 8,2 for grid 8x8", result.errors)

    def test_rejects_required_organ_cell_mismatch(self):
        grid = valid_grid()
        grid["organs"]["core"]["cells"].append([7, 7])

        result = validate_grid(grid)

        self.assertFalse(result.ok)
        self.assertIn("organ core references missing cell: 7,7", result.errors)

    def test_rejects_missing_sensor_or_expression_organ(self):
        grid = valid_grid()
        grid["organs"] = {
            "core": grid["organs"]["core"],
        }

        result = validate_grid(grid)

        self.assertFalse(result.ok)
        self.assertIn("missing required sensor or expression organ", result.errors)

    def test_rejects_disconnected_required_body_core(self):
        grid = valid_grid()
        grid["cells"][3]["x"] = 7
        grid["cells"][3]["y"] = 7
        grid["organs"]["core"]["cells"] = [[3, 2], [4, 2], [3, 3], [7, 7]]

        result = validate_grid(grid)

        self.assertFalse(result.ok)
        self.assertIn("required body core is disconnected", result.errors)

    def test_rejects_missing_animation_anchor(self):
        grid = valid_grid()
        for entry in grid["cells"]:
            entry["animation_anchor"] = False

        result = validate_grid(grid)

        self.assertFalse(result.ok)
        self.assertIn("missing animation anchor", result.errors)

    def test_rejects_mutation_rates_outside_unit_interval(self):
        grid = valid_grid()
        grid["mutation"]["cell_mutation_rate"] = 1.2

        result = validate_grid(grid)

        self.assertFalse(result.ok)
        self.assertIn("mutation cell_mutation_rate outside 0..1: 1.2", result.errors)

    def test_validate_grid_file_loads_json(self):
        grid = valid_grid()
        with tempfile.TemporaryDirectory() as tmp_dir:
            path = Path(tmp_dir) / "grid.json"
            path.write_text(json.dumps(grid), encoding="utf-8")

            result = validate_grid_file(path)

        self.assertTrue(result.ok, result.errors)


if __name__ == "__main__":
    unittest.main()
