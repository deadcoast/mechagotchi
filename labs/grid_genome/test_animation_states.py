import json
import tempfile
import unittest
from pathlib import Path

from animation_states import (
    ANIMATION_STATES,
    build_animation_states_report,
    project_animation_state,
    write_animation_states_artifacts,
)
from corpus_builder import build_seed_grids
from validator import validate_grid


class AnimationStateSemanticsTests(unittest.TestCase):
    """T4: the og five states as deterministic genome projections."""

    @classmethod
    def setUpClass(cls):
        cls.seeds = build_seed_grids()

    def test_vocabulary_is_the_og_five(self):
        self.assertEqual(
            ["idle", "blink", "sleep", "beg", "ill"], ANIMATION_STATES
        )

    def test_idle_is_the_identity(self):
        grid = self.seeds[0]
        self.assertEqual(grid, project_animation_state(grid, "idle"))

    def test_projections_are_visual_only_and_valid_for_every_seed(self):
        for grid in self.seeds:
            base_positions = [
                (cell["x"], cell["y"], cell["role"], cell["organ"])
                for cell in grid["cells"]
            ]
            for state in ANIMATION_STATES:
                projected = project_animation_state(grid, state)
                with self.subTest(grid=grid["grid_id"], state=state):
                    self.assertTrue(validate_grid(projected).ok)
                    self.assertEqual(
                        base_positions,
                        [
                            (c["x"], c["y"], c["role"], c["organ"])
                            for c in projected["cells"]
                        ],
                    )

    def test_blink_closes_the_eyes(self):
        grid = self.seeds[0]
        background = grid["palette"]["colors"][
            grid["palette"]["background_index"]
        ]
        projected = project_animation_state(grid, "blink")
        for cell in projected["cells"]:
            if cell["role"] == "eye":
                self.assertEqual(background, cell["visual"])

    def test_beg_highlights_the_mouth(self):
        grid = self.seeds[0]
        accent = grid["palette"]["colors"][-1]
        projected = project_animation_state(grid, "beg")
        mouths = [
            cell for cell in projected["cells"] if cell["role"] == "mouth"
        ]
        self.assertTrue(mouths)
        for cell in mouths:
            self.assertEqual(accent, cell["visual"])

    def test_projection_is_deterministic_and_never_mutates_the_grid(self):
        grid = self.seeds[0]
        snapshot = json.loads(json.dumps(grid))
        first = project_animation_state(grid, "ill")
        second = project_animation_state(grid, "ill")
        self.assertEqual(first, second)
        self.assertEqual(snapshot, grid)

    def test_unknown_state_fails_loudly(self):
        with self.assertRaises(ValueError):
            project_animation_state(self.seeds[0], "dance")


class AnimstateDatasetTests(unittest.TestCase):
    def test_report_and_animstate_300_dataset(self):
        report = build_animation_states_report()
        self.assertEqual(
            "animation_states_stage0", report["artifact_id"]
        )
        summary = report["summary"]
        self.assertEqual(60, summary["creature_count"])
        self.assertEqual(300, summary["sequence_count"])  # animstate_300
        self.assertEqual(1.0, summary["projection_valid_rate"])
        with tempfile.TemporaryDirectory() as temp_dir:
            output = Path(temp_dir)
            write_animation_states_artifacts(output, report)
            self.assertTrue(
                (output / "animation_states_stage0.json").exists()
            )
            dataset = json.loads(
                (output / "animstate_300.json").read_text(encoding="utf-8")
            )
            self.assertEqual(300, len(dataset["sequences"]))
            sample = dataset["sequences"][0]
            for key in ("grid_id", "state", "cells"):
                self.assertIn(key, sample)


if __name__ == "__main__":
    unittest.main()
