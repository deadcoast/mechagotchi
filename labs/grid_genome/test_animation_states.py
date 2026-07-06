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


class RenderPacketV2Tests(unittest.TestCase):
    """T16: packets carry animation + mood selected from lifecycle state."""

    @classmethod
    def setUpClass(cls):
        from animation_states import build_render_packet_v2, select_animation_state
        cls.build = staticmethod(build_render_packet_v2)
        cls.select = staticmethod(select_animation_state)
        cls.grid = build_seed_grids()[0]

    def test_selection_mirrors_the_mood_estimator_thresholds(self):
        cases = [
            ({"alive": True, "energy": 0.1, "hunger": 0.3, "stress": 0.2, "age_ticks": 1}, "sleep", "tired"),
            ({"alive": True, "energy": 0.6, "hunger": 0.8, "stress": 0.2, "age_ticks": 1}, "beg", "hungry"),
            ({"alive": True, "energy": 0.6, "hunger": 0.3, "stress": 0.8, "age_ticks": 1}, "ill", "stressed"),
            ({"alive": True, "energy": 0.6, "hunger": 0.3, "stress": 0.2, "age_ticks": 5}, "blink", "curious"),
            ({"alive": True, "energy": 0.6, "hunger": 0.3, "stress": 0.2, "age_ticks": 3}, "idle", "curious"),
        ]
        for state, expected_animation, expected_mood in cases:
            animation, mood = self.select(state)
            self.assertEqual((expected_animation, expected_mood), (animation, mood), state)

    def test_v2_packet_carries_animation_mood_and_projected_visuals(self):
        lifecycle_state = {"alive": True, "energy": 0.1, "hunger": 0.3, "stress": 0.2, "age_ticks": 2}
        packet = self.build(self.grid, lifecycle_state)
        self.assertEqual("sleep", packet["animation"])
        self.assertEqual("tired", packet["mood"])
        background = self.grid["palette"]["colors"][self.grid["palette"]["background_index"]]
        eye_visuals = {c["visual"] for c in packet["cells"] if c["role"] == "eye"}
        self.assertEqual({background}, eye_visuals)

    def test_without_lifecycle_state_the_packet_is_idle_and_base(self):
        packet = self.build(self.grid, None)
        self.assertEqual("idle", packet["animation"])
        self.assertIsNone(packet["mood"])
        from mecha_engine.genome import render_packet_from_grid
        self.assertEqual(render_packet_from_grid(self.grid)["cells"], packet["cells"])

    def test_explicit_animation_override_wins(self):
        packet = self.build(self.grid, None, animation="beg")
        self.assertEqual("beg", packet["animation"])
        accent = self.grid["palette"]["colors"][-1]
        mouths = {c["visual"] for c in packet["cells"] if c["role"] == "mouth"}
        self.assertEqual({accent}, mouths)
