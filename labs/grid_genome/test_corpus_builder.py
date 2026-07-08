import unittest

from corpus_builder import (
    build_invalid_grids,
    build_invalid_grids_16,
    build_seed_grids,
    build_seed_grids_16,
)
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


class Corpus16Tests(unittest.TestCase):
    """The 16x16 seed corpus gates (cycle 09 A2, DR 0029)."""

    @classmethod
    def setUpClass(cls):
        cls.seeds = build_seed_grids_16()

    def _core_mass(self, grid: dict) -> int:
        return sum(
            len(organ["cells"])
            for organ in grid["organs"].values()
            if organ.get("role") == "body_core" and organ.get("required") is True
        )

    def test_builds_50_valid_16x16_seed_grids(self):
        self.assertEqual(50, len(self.seeds))
        self.assertEqual(50, len({grid["grid_id"] for grid in self.seeds}))
        for grid in self.seeds:
            with self.subTest(grid_id=grid["grid_id"]):
                result = validate_grid(grid)
                self.assertTrue(result.ok, result.errors)
                self.assertEqual([16, 16], grid["grid_size"])

    def test_every_seed_meets_the_ratified_core_floor(self):
        for grid in self.seeds:
            with self.subTest(grid_id=grid["grid_id"]):
                self.assertGreaterEqual(self._core_mass(grid), 18)

    def test_every_seed_carries_a_sensor_pair(self):
        # DR 0029: the dossier's sensor pair is the A2 hard corpus gate.
        for grid in self.seeds:
            with self.subTest(grid_id=grid["grid_id"]):
                eyes = sum(1 for cell in grid["cells"] if cell["role"] == "eye")
                self.assertGreaterEqual(eyes, 2)

    def test_every_seed_carries_exactly_one_anchor(self):
        for grid in self.seeds:
            with self.subTest(grid_id=grid["grid_id"]):
                anchors = sum(
                    1
                    for cell in grid["cells"]
                    if cell["animation_anchor"] is True
                )
                self.assertEqual(1, anchors)

    def test_palettes_ten_creatures_each(self):
        counts: dict[str, int] = {}
        for grid in self.seeds:
            palette = grid["palette"]["palette_id"]
            counts[palette] = counts.get(palette, 0) + 1
        self.assertEqual(
            {
                "lcd_green": 10,
                "gameboy_gray": 10,
                "amber_terminal": 10,
                "crt_blue": 10,
                "pocket_plum": 10,
            },
            counts,
        )

    def test_corpus_exercises_the_dr0015_vocabulary(self):
        roles = {cell["role"] for grid in self.seeds for cell in grid["cells"]}
        for role in [
            "body", "shell", "joint", "limb", "eye", "mouth",
            "antenna", "sensor", "decoration", "effect",
        ]:
            self.assertIn(role, roles)

    def test_morphological_variety_not_upscaled_blobs(self):
        # Distinct silhouettes; a real spread of mass and symmetry; a
        # majority of creatures using vocabulary beyond body/eye/mouth.
        signatures = {
            tuple(
                sorted((cell["x"], cell["y"], cell["role"]) for cell in grid["cells"])
            )
            for grid in self.seeds
        }
        self.assertEqual(50, len(signatures))
        masses = [self._core_mass(grid) for grid in self.seeds]
        self.assertLessEqual(min(masses), 20)
        self.assertGreaterEqual(max(masses), 60)
        rich = sum(
            1
            for grid in self.seeds
            if any(
                cell["role"] not in {"body", "eye", "mouth"}
                for cell in grid["cells"]
            )
        )
        self.assertGreaterEqual(rich, 40)

    def test_builds_200_invalid_16x16_counterexamples(self):
        invalid_grids = build_invalid_grids_16(self.seeds)
        self.assertEqual(200, len(invalid_grids))
        self.assertEqual(200, len({grid["grid_id"] for grid in invalid_grids}))
        for grid in invalid_grids:
            with self.subTest(grid_id=grid["grid_id"]):
                self.assertFalse(validate_grid(grid).ok)


if __name__ == "__main__":
    unittest.main()
