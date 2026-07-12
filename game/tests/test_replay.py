"""F10 gates — the Review step: a REAL recorded life plays back.

The R5 recorder's contract mirrored over engine publics (DR 0023:
`live_cycle(record_frames=True)` is the engine seam; the replay never
invents a displayable body — packets only for validator-passing
states, errors verbatim otherwise). The scrubber invariant is the
shared drawer's: the body at frame i is the latest packet-bearing
frame ≤ i. The Review replays an era ELITE (a gate survivor) at the
era's own seed — raw seeds under the weak test-scale repair model hit
the G2-measured aligned-but-invalid boundary and honestly record a
truncated life, which is pinned here too.
"""

import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
for _src in (ROOT / "game" / "src", ROOT / "packages" / "mecha_engine" / "src"):
    if str(_src) not in sys.path:
        sys.path.insert(0, str(_src))

from mecha_game.campaign import (  # noqa: E402
    TINY_ERA_CONFIG,
    KeeperCampaign,
    load_campaign_inputs,
)
from mecha_game.replay import (  # noqa: E402
    REPLAY_FORMAT,
    ReplayPlayer,
    build_replay,
    overlay_wounds,
)

SEED_DIR = ROOT / "data" / "seed_grids_16x16"
SLIP_PATH = ROOT / "data" / "slips" / "valid" / "slip_lcd_seed.json"
ADOPTED = (
    ROOT / "data" / "readability_benchmark" / "adopted_readability_model.json"
)


class ReplayTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.inputs = load_campaign_inputs(
            SEED_DIR, SLIP_PATH, ADOPTED, repair_epochs=6, seed_limit=12
        )
        cls.campaign = KeeperCampaign(
            cls.inputs, era_config=TINY_ERA_CONFIG, campaign_id="review"
        )
        cls.era = cls.campaign.advance_era("calm")
        cls.replay = cls.campaign.record_review_replay()

    def test_the_recorded_life_is_the_engines(self):
        self.assertEqual(REPLAY_FORMAT, self.replay["replay_format"])
        self.assertEqual(
            "mecha_engine.runtime.live_cycle(record_frames=True)",
            self.replay["engine_surface"],
        )
        self.assertEqual("birth", self.replay["frames"][0]["phase"])
        self.assertIsNotNone(self.replay["frames"][0]["packet"])
        phases = {frame["phase"] for frame in self.replay["frames"]}
        # The elite is a gate survivor: its recorded life carries the
        # full phase vocabulary, episode ticks included.
        self.assertEqual(
            {"birth", "wound", "repair", "episode_tick"}, phases
        )
        self.assertGreater(self.replay["tick_frame_count"], 0)
        self.assertEqual(
            self.replay["frame_count"], len(self.replay["frames"])
        )

    def test_the_review_replays_the_best_elite_at_the_eras_seed(self):
        best_id = max(
            self.era["elites"],
            key=lambda e: (e["fitness"], e["niche_key"]),
        )["grid"]["grid_id"]
        self.assertEqual(best_id, self.replay["creature"]["grid_id"])
        self.assertEqual(
            self.era["rng_seed"], self.replay["parameters"]["rng_seed"]
        )
        self.assertIn("recorded", self.replay["honest_label"])

    def test_wound_frames_carry_the_engines_removed_cells(self):
        wounds = [
            frame
            for frame in self.replay["frames"]
            if frame["phase"] == "wound"
        ]
        self.assertTrue(wounds)
        self.assertEqual(
            wounds[0]["removed_cell_count"],
            len(wounds[0]["removed_cells"]),
        )

    def test_replays_are_deterministic(self):
        twin = self.campaign.record_review_replay()
        self.assertEqual(
            json.dumps(self.replay, sort_keys=True),
            json.dumps(twin, sort_keys=True),
        )

    def test_an_unaligned_repair_records_a_truncated_life_honestly(self):
        # The G2-measured boundary: a raw seed under the weak
        # test-scale repair model repairs aligned-but-invalid or
        # unaligned — the replay records the truncated life verbatim
        # (no episode ticks), never smoothing it into a full one.
        replay = build_replay(
            self.inputs["seed_grids"][0],
            self.inputs["slip_profile"],
            self.inputs["repair_model"],
            damage_cycles=1,
            ticks=6,
            dropout_rate=0.2,
            rng_seed=20260712,
        )
        self.assertEqual(0, replay["tick_frame_count"])
        self.assertFalse(
            replay["live"]["all_cycles_valid"]
            and replay["live"]["all_cycles_aligned"]
        )


class ReplayPlayerTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        ReplayTests.setUpClass()
        cls.replay = ReplayTests.replay

    def test_the_scrubber_invariant(self):
        player = ReplayPlayer(self.replay)
        wound_index = next(
            frame["frame"]
            for frame in self.replay["frames"]
            if frame["phase"] == "wound"
        )
        body = player.body_packet_at(wound_index)
        self.assertIsNotNone(body)
        self.assertEqual(self.replay["frames"][0]["packet"], body)

    def test_step_and_back_clamp_to_the_recording(self):
        player = ReplayPlayer(self.replay)
        self.assertEqual(0, player.index)
        player.back()
        self.assertEqual(0, player.index)
        for _ in range(self.replay["frame_count"] + 5):
            player.step()
        self.assertEqual(self.replay["frame_count"] - 1, player.index)

    def test_frame_caption_is_engine_truth(self):
        player = ReplayPlayer(self.replay)
        self.assertIn("birth", player.caption())
        player.step()
        self.assertIn(
            self.replay["frames"][1]["phase"], player.caption()
        )

    def test_wound_overlay_marks_exactly_the_removed_cells(self):
        buffer = tuple(
            tuple((100, 100, 100) for _ in range(3)) for _ in range(3)
        )
        marked = overlay_wounds(buffer, [(1, 2), (0, 0)])
        expected = (
            round(100 * 0.25 + 200 * 0.75),
            round(100 * 0.25 + 60 * 0.75),
            round(100 * 0.25 + 40 * 0.75),
        )
        self.assertEqual(expected, marked[2][1])
        self.assertEqual(expected, marked[0][0])
        self.assertEqual((100, 100, 100), marked[1][1])

    def test_wound_cells_surface_only_at_wound_frames(self):
        player = ReplayPlayer(self.replay)
        self.assertIsNone(player.wound_cells())
        while player.current()["phase"] != "wound":
            player.step()
        self.assertTrue(player.wound_cells())


if __name__ == "__main__":
    unittest.main()
