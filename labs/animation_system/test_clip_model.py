import json
import sys
import tempfile
import unittest
from pathlib import Path

from clip_model import (
    CLIP_DECOR_BOB,
    CLIP_JOINT_FLEX,
    CLIP_LIMB_STEP,
    CLIP_STATES,
    build_clip_model_report,
    clip_frame,
    clip_frame_count,
    clip_frames,
    clip_names,
    write_clip_model_artifacts,
)

LAB_DIR = Path(__file__).resolve().parent
REPO_ROOT = LAB_DIR.parents[1]
GRID_GENOME = REPO_ROOT / "labs" / "grid_genome"
if str(GRID_GENOME) not in sys.path:
    sys.path.insert(0, str(GRID_GENOME))

from corpus_builder import build_seed_grids, build_seed_grids_16  # noqa: E402


def _beetle() -> dict:
    return next(
        grid
        for grid in build_seed_grids_16()
        if grid["grid_id"].endswith("beetle")
    )


class ClipVocabularyTests(unittest.TestCase):
    def test_clips_are_grounded_in_the_promoted_state_vocabulary(self):
        # One clip per promoted animation state — SLIP animation_vocab
        # keeps bounding what a species may play (C4 wires it).
        self.assertEqual(
            ["beg", "blink", "idle", "ill", "sleep"], sorted(clip_names())
        )
        for clip in clip_names():
            with self.subTest(clip=clip):
                self.assertGreaterEqual(clip_frame_count(clip), 3)
                self.assertEqual(
                    clip_frame_count(clip), len(CLIP_STATES[clip])
                )

    def test_unknown_clip_and_frame_fail_loudly(self):
        beetle = _beetle()
        with self.assertRaises(ValueError):
            clip_frame(beetle, "wiggle", 0)
        with self.assertRaises(ValueError):
            clip_frame(beetle, "idle", 99)


def _argus() -> dict:
    return json.loads(
        (
            REPO_ROOT / "data" / "vocabulary_exemplars" / "vocab_argus.json"
        ).read_text(encoding="utf-8")
    )


class PerRoleMotionTests(unittest.TestCase):
    """Cycle 19 I4 — the DR 0015 WATCH seam's named increment: limb,

    joint, and decoration motion, recorded per clip (DR 0037), never
    improvised. Amplitudes are the LCD unit step (1px at every
    canvas); limbs step vertically and joints flex horizontally with
    the column-parity sign rule (even column +, odd column −, the
    gait/counter-flex read); decoration bobs uniformly. Every offset
    keeps the collision/bounds skip — pinned below on the exemplar's
    own boxed cells, the honesty visible.
    """

    def test_the_tables_cover_every_clip_at_every_frame(self):
        for table in (CLIP_LIMB_STEP, CLIP_JOINT_FLEX, CLIP_DECOR_BOB):
            self.assertEqual(sorted(table), sorted(CLIP_STATES))
            for clip, offsets in table.items():
                self.assertEqual(len(CLIP_STATES[clip]), len(offsets))
                self.assertEqual(0, offsets[0])  # frame 0 = identity

    def test_idle_decoration_bobs_and_the_blocked_bob_is_skipped(self):
        argus = _argus()
        # idle frame 1: bob +1 (down) — (3,6) -> (3,7) is free.
        moved = clip_frame(argus, "idle", 1)
        decoration = [
            (cell["x"], cell["y"])
            for cell in moved["cells"]
            if cell["role"] == "decoration"
        ]
        self.assertEqual([(3, 7)], decoration)
        # idle frame 3: bob -1 (up) — (3,5) is shell: the skip recorded.
        blocked = clip_frame(argus, "idle", 3)
        decoration = [
            (cell["x"], cell["y"])
            for cell in blocked["cells"]
            if cell["role"] == "decoration"
        ]
        self.assertEqual([(3, 6)], decoration)

    def test_ill_limbs_gait_by_column_parity_with_collision_honesty(self):
        argus = _argus()
        # ill frame 2: body motion (0,0); limb step -1 with the parity
        # sign rule => odd columns +1 (down), even columns -1 (up).
        # On the exemplar only (1,6) -> (1,7) is free; the boxed limbs
        # and the shell-blocked step are skipped — pinned exactly.
        frame = clip_frame(argus, "ill", 2)
        limbs = sorted(
            (cell["x"], cell["y"])
            for cell in frame["cells"]
            if cell["role"] == "limb"
        )
        self.assertEqual([(1, 5), (1, 7), (6, 5), (6, 6)], limbs)

    def test_joints_flex_by_column_parity_in_open_space(self):
        rig = _argus()
        joints = [cell for cell in rig["cells"] if cell["role"] == "joint"]
        self.assertEqual(2, len(joints))
        # Row 7 is genuinely open on the exemplar.
        joints[0]["x"], joints[0]["y"] = 2, 7
        joints[1]["x"], joints[1]["y"] = 5, 7
        # ill frame 2: flex +1 with the parity sign rule => even
        # column (2,7) -> (3,7); odd column (5,7) -> (4,7).
        frame = clip_frame(rig, "ill", 2)
        flexed = sorted(
            (cell["x"], cell["y"])
            for cell in frame["cells"]
            if cell["role"] == "joint"
        )
        self.assertEqual([(3, 7), (4, 7)], flexed)

    def test_grids_without_the_roles_are_untouched_by_the_increment(self):
        # ADDITIVE: a seed with no limb/joint/decoration cells keeps
        # its rows through idle frame 1 (sway is horizontal; no
        # vertical per-role offset may appear from the increment).
        drone = next(
            grid
            for grid in build_seed_grids_16()
            if grid["grid_id"] == "mg_seed16_015_drone"
        )
        roles = {cell["role"] for cell in drone["cells"]}
        self.assertFalse(roles & {"limb", "joint", "decoration"})
        # idle frame 2 carries no offsets at all (body 0, sway 0, the
        # per-role tables 0) and no flicker (even frame): positions
        # must be exactly the pristine silhouette.
        pristine = {(cell["x"], cell["y"]) for cell in drone["cells"]}
        frame = clip_frame(drone, "idle", 2)
        self.assertEqual(
            pristine,
            {(cell["x"], cell["y"]) for cell in frame["cells"]},
        )


class ClipFrameTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.beetle = _beetle()

    def test_frames_are_deterministic_visual_only_projections(self):
        pristine = json.loads(json.dumps(self.beetle))
        first = clip_frame(self.beetle, "ill", 1)
        second = clip_frame(self.beetle, "ill", 1)
        self.assertEqual(first, second)
        # Engine truth: the genome is presentation-input, never mutated.
        self.assertEqual(pristine, self.beetle)

    def test_idle_frame_zero_is_the_identity(self):
        frame = clip_frame(self.beetle, "idle", 0)
        self.assertEqual(self.beetle["cells"], frame["cells"])
        self.assertEqual("idle", frame["clip"])
        self.assertEqual(0, frame["frame_index"])
        self.assertEqual(4, frame["frame_count"])

    def test_frames_carry_the_packet_shape_and_anchors(self):
        for clip in clip_names():
            for index in range(clip_frame_count(clip)):
                with self.subTest(clip=clip, frame=index):
                    frame = clip_frame(self.beetle, clip, index)
                    for key in [
                        "grid_id",
                        "clip",
                        "frame_index",
                        "frame_count",
                        "grid_size",
                        "palette",
                        "cells",
                        "anchors",
                    ]:
                        self.assertIn(key, frame)
                    self.assertEqual([16, 16], frame["grid_size"])
                    self.assertEqual(1, len(frame["anchors"]))

    def test_every_frame_is_a_valid_render_surface(self):
        # In bounds, palette-clean, and never MORE cells than the body
        # (frames may hide cells — blink, flicker — never invent them).
        base_count = len(self.beetle["cells"])
        legal_colors = set(self.beetle["palette"]["colors"])
        for clip in clip_names():
            for frame in clip_frames(self.beetle, clip):
                with self.subTest(clip=clip, frame=frame["frame_index"]):
                    self.assertLessEqual(len(frame["cells"]), base_count)
                    for cell in frame["cells"]:
                        self.assertTrue(0 <= cell["x"] < 16)
                        self.assertTrue(0 <= cell["y"] < 16)
                        self.assertIn(cell["visual"], legal_colors)
                    positions = [
                        (cell["x"], cell["y"]) for cell in frame["cells"]
                    ]
                    self.assertEqual(len(positions), len(set(positions)))

    def test_clips_actually_move(self):
        # A clip whose frames are all identical is a state, not a clip.
        for clip in clip_names():
            frames = clip_frames(self.beetle, clip)
            distinct = {
                json.dumps(frame["cells"], sort_keys=True)
                for frame in frames
            }
            with self.subTest(clip=clip):
                self.assertGreater(len(distinct), 1)

    def test_blink_closes_the_eyes_mid_clip(self):
        open_eyes = clip_frame(self.beetle, "blink", 0)
        closed = clip_frame(self.beetle, "blink", 1)
        background = self.beetle["palette"]["colors"][
            self.beetle["palette"]["background_index"]
        ]
        open_colors = {
            cell["visual"]
            for cell in open_eyes["cells"]
            if cell["role"] == "eye"
        }
        closed_colors = {
            cell["visual"]
            for cell in closed["cells"]
            if cell["role"] == "eye"
        }
        self.assertNotEqual({background}, open_colors)
        self.assertEqual({background}, closed_colors)

    def test_clips_work_at_8x8_too(self):
        # Size-parametric, never size-replacing.
        seed = build_seed_grids()[0]
        for clip in clip_names():
            for frame in clip_frames(seed, clip):
                with self.subTest(clip=clip, frame=frame["frame_index"]):
                    self.assertEqual([8, 8], frame["grid_size"])
                    for cell in frame["cells"]:
                        self.assertTrue(0 <= cell["x"] < 8)
                        self.assertTrue(0 <= cell["y"] < 8)


class ClipReportTests(unittest.TestCase):
    def test_report_is_deterministic_and_gates_hold(self):
        report = build_clip_model_report()
        again = build_clip_model_report()
        self.assertEqual(
            json.dumps(report, sort_keys=True),
            json.dumps(again, sort_keys=True),
        )
        self.assertEqual("clip_model_stage0", report["artifact_id"])
        metrics = report["metrics"]
        self.assertEqual(50, metrics["corpus_size"])
        self.assertEqual(
            50 * sum(clip_frame_count(clip) for clip in clip_names()),
            metrics["frames_rendered"],
        )
        self.assertEqual(1.0, metrics["frames_in_bounds_rate"])
        self.assertEqual(1.0, metrics["frames_palette_clean_rate"])
        self.assertEqual(1.0, metrics["genome_untouched_rate"])
        self.assertGreater(
            metrics["intra_clip_delta"]["mean_fraction"], 0.0
        )
        with tempfile.TemporaryDirectory() as tmp:
            output_dir = Path(tmp)
            write_clip_model_artifacts(output_dir, report)
            loaded = json.loads(
                (output_dir / "clip_model_stage0.json").read_text(
                    encoding="utf-8"
                )
            )
            self.assertEqual(report["metrics"], loaded["metrics"])


if __name__ == "__main__":
    unittest.main()
