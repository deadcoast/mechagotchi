"""Parity + rung pins: the clip model in mecha_engine.genome (C4).

The clip functions are a verbatim port of this lab's clip model, and
``render_packet_v2`` gains the documented ``animation`` BLOCK
(clip/frame_index/anchors) as an additive rung — byte-identical when no
clip is requested (the existing animation parity suite is that proof;
these tests pin the rung itself).
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

from clip_model import clip_frame as lab_clip_frame  # noqa: E402
from clip_model import clip_frames as lab_clip_frames  # noqa: E402
from clip_model import clip_names as lab_clip_names  # noqa: E402
from corpus_builder import build_seed_grids_16  # noqa: E402

from mecha_engine.genome import (  # noqa: E402
    clip_frame,
    clip_frame_count,
    clip_names,
    render_packet_v2,
)


class PackageClipParityTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.corpus = build_seed_grids_16()

    def test_clip_vocabulary_matches_the_lab(self):
        self.assertEqual(lab_clip_names(), clip_names())

    def test_clip_frames_are_verbatim_over_corpus_samples(self):
        for grid in self.corpus[:10]:
            for clip in clip_names():
                for index in range(clip_frame_count(clip)):
                    with self.subTest(
                        grid_id=grid["grid_id"], clip=clip, frame=index
                    ):
                        self.assertEqual(
                            lab_clip_frame(grid, clip, index),
                            clip_frame(grid, clip, index),
                        )


class PacketClipRungTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.beetle = next(
            grid
            for grid in build_seed_grids_16()
            if grid["grid_id"].endswith("beetle")
        )

    def test_no_clip_keeps_the_string_animation_field(self):
        packet = render_packet_v2(self.beetle, animation="sleep")
        self.assertEqual("sleep", packet["animation"])
        self.assertNotIn("frame_index", packet)

    def test_clip_request_carries_the_documented_block(self):
        packet = render_packet_v2(self.beetle, clip="ill", frame_index=1)
        block = packet["animation"]
        self.assertEqual(
            {"clip", "frame_index", "frame_count", "anchors"},
            set(block),
        )
        self.assertEqual("ill", block["clip"])
        self.assertEqual(1, block["frame_index"])
        self.assertEqual(4, block["frame_count"])
        self.assertEqual(1, len(block["anchors"]))
        # The packet's cells ARE the frame's cells (motion included).
        frame = lab_clip_frame(self.beetle, "ill", 1)
        self.assertEqual(frame["cells"], packet["cells"])

    def test_clip_defaults_to_frame_zero_and_rejects_bad_frames(self):
        packet = render_packet_v2(self.beetle, clip="idle")
        self.assertEqual(0, packet["animation"]["frame_index"])
        with self.assertRaises(ValueError):
            render_packet_v2(self.beetle, clip="idle", frame_index=99)
        with self.assertRaises(ValueError):
            render_packet_v2(self.beetle, clip="wiggle")

    def test_vocabulary_gate_bounds_clips_with_honest_mood(self):
        profile = {"visual_grammar": {"animation_vocab": ["idle", "sleep"]}}
        packet = render_packet_v2(
            self.beetle,
            {"hunger": 0.9, "energy": 0.5, "stress": 0.0},
            clip="beg",
            slip_profile=profile,
        )
        # The DISPLAYED clip falls back to idle; mood stays honest.
        self.assertEqual("idle", packet["animation"]["clip"])
        self.assertEqual("hungry", packet["mood"])

    def test_clip_frames_scrub_deterministically(self):
        first = [
            render_packet_v2(self.beetle, clip="sleep", frame_index=i)
            for i in range(4)
        ]
        second = [
            render_packet_v2(self.beetle, clip="sleep", frame_index=i)
            for i in range(4)
        ]
        self.assertEqual(
            json.dumps(first, sort_keys=True),
            json.dumps(second, sort_keys=True),
        )
        distinct = {
            json.dumps(packet["cells"], sort_keys=True) for packet in first
        }
        self.assertGreater(len(distinct), 1)


if __name__ == "__main__":
    unittest.main()
