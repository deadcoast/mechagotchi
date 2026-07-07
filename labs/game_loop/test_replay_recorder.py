"""R5 gates: the replay artifact is recorded engine truth end to end,
and the `record_frames` engine seam defaults to byte-identical."""

import json
import sys
import tempfile
import unittest
from pathlib import Path

LAB_DIR = Path(__file__).resolve().parent
ROOT = LAB_DIR.parents[1]
if str(LAB_DIR) not in sys.path:
    sys.path.insert(0, str(LAB_DIR))

from replay_recorder import (  # noqa: E402
    REPLAY_FORMAT,
    build_recorder_report,
    build_replay,
    packet_or_errors,
    write_replay_artifacts,
)

from mecha_engine.repair import train_repair_model  # noqa: E402
from mecha_engine.runtime import live_cycle  # noqa: E402

RNG_SEED = 20260707
REPLAY_KW = dict(damage_cycles=2, ticks=12, rng_seed=RNG_SEED)


class ReplayRecorderTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.grid = json.loads(
            (ROOT / "data" / "seed_grids" / "mg_seed_001.json").read_text(
                encoding="utf-8"
            )
        )
        cls.slip_profile = json.loads(
            (
                ROOT / "data" / "slips" / "valid" / "slip_lcd_seed.json"
            ).read_text(encoding="utf-8")
        )
        seed_grids = [
            json.loads(path.read_text(encoding="utf-8"))
            for path in sorted(
                (ROOT / "data" / "seed_grids").glob("mg_seed_*.json")
            )
        ]
        cls.repair_model = train_repair_model(
            seed_grids[:40], epochs=20, rng_seed=RNG_SEED
        )
        cls.replay = build_replay(
            cls.grid, cls.slip_profile, cls.repair_model, **REPLAY_KW
        )

    # -- the engine seam (DR 0023) ------------------------------------

    def test_record_frames_default_is_byte_identical(self):
        kw = dict(
            damage_cycles=2, ticks=12, dropout_rate=0.2, rng_seed=RNG_SEED
        )
        plain = live_cycle(
            self.grid, self.slip_profile, self.repair_model, **kw
        )
        recorded = live_cycle(
            self.grid,
            self.slip_profile,
            self.repair_model,
            record_frames=True,
            **kw,
        )
        for cycle in plain["cycles"]:
            self.assertNotIn("frames", cycle)
        stripped = {
            key: (
                [
                    {k: v for k, v in cycle.items() if k != "frames"}
                    for cycle in value
                ]
                if key == "cycles"
                else value
            )
            for key, value in recorded.items()
        }
        self.assertEqual(plain, stripped)

    def test_recorded_frames_carry_engine_truth_only(self):
        recorded = live_cycle(
            self.grid,
            self.slip_profile,
            self.repair_model,
            damage_cycles=2,
            ticks=12,
            rng_seed=RNG_SEED,
            record_frames=True,
        )
        for cycle in recorded["cycles"]:
            frames = cycle["frames"]
            self.assertEqual(
                {"removed_cells", "repaired_grid", "episode_history"},
                set(frames),
            )
            self.assertEqual(
                cycle["removed_cell_count"], len(frames["removed_cells"])
            )
            if cycle["episode"] is not None:
                self.assertEqual(
                    cycle["episode"]["survival_ticks"],
                    len(frames["episode_history"]),
                )

    # -- the replay artifact -------------------------------------------

    def test_deterministic_replay(self):
        again = build_replay(
            self.grid, self.slip_profile, self.repair_model, **REPLAY_KW
        )
        self.assertEqual(self.replay, again)

    def test_replay_is_json_serializable_and_indexed(self):
        payload = json.loads(json.dumps(self.replay))
        self.assertEqual(self.replay, payload)
        self.assertEqual(REPLAY_FORMAT, payload["replay_format"])
        for index, frame in enumerate(payload["frames"]):
            self.assertEqual(index, frame["frame"])

    def test_timeline_shape_birth_then_wound_repair_ticks_per_cycle(self):
        frames = self.replay["frames"]
        self.assertEqual("birth", frames[0]["phase"])
        self.assertIsNotNone(frames[0]["packet"])
        cycles = self.replay["live"]["cycles"]
        wounds = [f for f in frames if f["phase"] == "wound"]
        repairs = [f for f in frames if f["phase"] == "repair"]
        self.assertEqual(len(cycles), len(wounds))
        self.assertEqual(len(cycles), len(repairs))
        expected_ticks = sum(
            cycle["episode"]["survival_ticks"]
            for cycle in cycles
            if cycle["episode"] is not None
        )
        self.assertEqual(expected_ticks, self.replay["tick_frame_count"])

    def test_wound_frames_are_the_damage_events_own_records(self):
        by_cycle = {
            frame["cycle"]: frame
            for frame in self.replay["frames"]
            if frame["phase"] == "wound"
        }
        for cycle in self.replay["live"]["cycles"]:
            wound = by_cycle[cycle["cycle"]]
            self.assertEqual(
                cycle["removed_cell_count"], wound["removed_cell_count"]
            )
            self.assertEqual(
                cycle["removed_cell_count"], len(wound["removed_cells"])
            )

    def test_repair_frames_pin_their_cycle_digests(self):
        by_cycle = {
            frame["cycle"]: frame
            for frame in self.replay["frames"]
            if frame["phase"] == "repair"
        }
        for cycle in self.replay["live"]["cycles"]:
            repair = by_cycle[cycle["cycle"]]
            self.assertEqual(cycle["valid"], repair["valid"])
            self.assertEqual(cycle["aligned"], repair["aligned"])
            self.assertEqual(
                cycle["position_restoration"],
                repair["position_restoration"],
            )
            if repair["valid"]:
                self.assertIsNotNone(repair["packet"])
                self.assertEqual([], repair["validation_errors"])

    def test_episode_tick_frames_carry_the_lifecycle_history_verbatim(self):
        ticks = [
            frame
            for frame in self.replay["frames"]
            if frame["phase"] == "episode_tick"
        ]
        self.assertTrue(ticks)
        for frame in ticks:
            entry = frame["entry"]
            self.assertEqual(frame["tick"], entry["tick"])
            for field in ("action", "balance", "alive", "state"):
                self.assertIn(field, entry)

    def test_invalid_bodies_carry_validator_errors_never_fake_packets(self):
        invalid_files = sorted(
            (ROOT / "data" / "invalid_grids").glob("*.json")
        )
        self.assertTrue(invalid_files)
        invalid = json.loads(invalid_files[0].read_text(encoding="utf-8"))
        # Corpus files may wrap the grid with counterexample metadata.
        grid = invalid.get("grid", invalid)
        packet, errors = packet_or_errors(grid)
        self.assertIsNone(packet)
        self.assertTrue(errors)

    def test_a_thinking_covenant_shows_its_thoughts_in_the_replay(self):
        # F1 end-to-end: under a deliberation covenant, the recorded
        # tick frames carry the R1 record — the scrubber renders
        # "thought N ticks" from exactly this field.
        profile = json.loads(json.dumps(self.slip_profile))
        profile["slip_version"] = "0.2.0"
        profile["deliberation"] = {
            "max_ticks": 4,
            "confidence_threshold": 0.72,
        }
        replay = build_replay(
            self.grid, profile, self.repair_model, **REPLAY_KW
        )
        thoughts = [
            frame["entry"]["deliberation"]
            for frame in replay["frames"]
            if frame["phase"] == "episode_tick"
            and "deliberation" in frame["entry"]
        ]
        self.assertTrue(thoughts)
        for thought in thoughts:
            self.assertGreaterEqual(thought["tick_count"], 1)
            self.assertLessEqual(thought["tick_count"], 4)
        # The v0.1 replay (setUpClass) stays thought-free — the
        # rung-conditional key keeps frozen replays byte-identical.
        for frame in self.replay["frames"]:
            if frame["phase"] == "episode_tick":
                self.assertNotIn("deliberation", frame["entry"])

    def test_artifacts_round_trip(self):
        report = build_recorder_report(self.replay)
        self.assertEqual(
            "replay_recorder_composed", report["decision"]["status"]
        )
        with tempfile.TemporaryDirectory() as tmp:
            write_replay_artifacts(tmp, report, self.replay)
            written = json.loads(
                (Path(tmp) / "replay_sample.json").read_text(
                    encoding="utf-8"
                )
            )
            self.assertEqual(self.replay, written)


if __name__ == "__main__":
    unittest.main()
