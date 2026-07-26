"""Cycle 22 L5 (DR 0045): density as pressure, judged at its consumer.

DR 0043 clause 2's named record. I3 measured that the checkpoint
forecast inverts the biology — post-takeover soup arrives MILDER than
early — because `replication_scores` and `lineage_events` are
structurally absent from the checkpoint format, leaving pressure driven
by entropy and instruction diversity, both of which FALL as a soup
organizes.

These pins fix the consumer contract: the rider is off by default and
byte-identical there, the study measures both arms over the SAME
records, the callback corpus rides as the lit-channel ground truth, and
the verdict is the pre-registered rule applied — never a stored answer.
"""

import json
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
for path in (
    ROOT / "game",
    ROOT / "game" / "src",
    ROOT / "packages" / "mecha_engine" / "src",
):
    if str(path) not in sys.path:
        sys.path.insert(0, str(path))

from evidence import (  # noqa: E402
    DENSITY_PRESSURE_ARTIFACT_ID,
    build_density_pressure_report,
    write_density_pressure_artifacts,
)
from mecha_engine.runtime.evolve import _cubff_generation_pressure  # noqa: E402
from mecha_game.campaign import load_real_weather_source  # noqa: E402


class SeamLawTests(unittest.TestCase):
    def test_the_rider_is_off_by_default_and_byte_identical(self):
        # DR 0045 G3: the incumbent pressure math is untouched unless
        # the rider is explicitly asked for.
        for record in load_real_weather_source():
            with self.subTest(snapshot=record["snapshot_id"]):
                self.assertEqual(
                    _cubff_generation_pressure(record),
                    _cubff_generation_pressure(record, density_pressure=False),
                )

    def test_the_rider_never_lowers_pressure(self):
        # Density is a departure-from-randomness signal clamped at 0
        # below chance, so it can only ever ADD pressure — it must not
        # be able to make an organized soup calmer.
        for record in load_real_weather_source():
            off = _cubff_generation_pressure(record)[0]
            on = _cubff_generation_pressure(record, density_pressure=True)[0]
            with self.subTest(snapshot=record["snapshot_id"]):
                self.assertGreaterEqual(on, off)


class DensityPressureReportTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.report = build_density_pressure_report()

    def test_the_report_carries_the_stage0_contract(self):
        for key in (
            "artifact_id",
            "status",
            "date",
            "purpose",
            "source_artifacts",
            "metrics",
            "closed_states",
            "blocked_states",
            "decision",
            "next_research_step",
        ):
            with self.subTest(key=key):
                self.assertIn(key, self.report)
        self.assertEqual(DENSITY_PRESSURE_ARTIFACT_ID, self.report["artifact_id"])

    def test_the_defect_is_reproduced_before_it_is_corrected(self):
        # The I3 inversion must still be visible with the rider OFF —
        # otherwise the study is measuring something else entirely.
        self.assertLess(self.report["metrics"]["inversion_off"], 0.0)

    def test_the_callback_corpus_rides_as_the_lit_channel_ground_truth(self):
        # I3 lit the replication channel through the callback path;
        # that ordering is the truth the checkpoint proxy must match.
        self.assertEqual(
            "post_takeover_harsher",
            self.report["metrics"]["callback_ground_truth_direction"],
        )

    def test_density_never_synthesizes_the_silent_channels(self):
        # DR 0045 G4 / DR 0043 clause 3: the checkpoint path's
        # replication and lineage channels stay honestly absent.
        from mecha_engine.runtime._cubff import extract_cubff_features

        for record in load_real_weather_source():
            features = extract_cubff_features(record, include_density=True)
            with self.subTest(snapshot=record["snapshot_id"]):
                self.assertEqual(0, features["replication_rate"])
                self.assertEqual(0, features["lineage_churn"])

    def test_every_multiplier_stays_inside_the_documented_band(self):
        for row in (
            self.report["metrics"]["checkpoint_per_snapshot"]
            + self.report["metrics"]["callback_per_snapshot"]
        ):
            with self.subTest(snapshot=row["snapshot_id"]):
                self.assertGreaterEqual(row["dropout_multiplier_on"], 0.5)
                self.assertLessEqual(row["dropout_multiplier_on"], 1.6)

    def test_the_verdict_is_the_pre_registered_rule_applied(self):
        decision = self.report["decision"]
        expected = (
            "adopt"
            if (
                decision["g1_inversion_corrected"]
                and decision["g2_agrees_with_callback_ground_truth"]
                and decision["g5_within_documented_band"]
            )
            else "refuse"
        )
        self.assertEqual(expected, decision["verdict"])

    def test_the_artifact_writes_and_reloads(self):
        with tempfile.TemporaryDirectory() as tmp:
            written = write_density_pressure_artifacts(Path(tmp), self.report)
            reloaded = json.loads(Path(written).read_text(encoding="utf-8"))
            self.assertEqual(DENSITY_PRESSURE_ARTIFACT_ID, reloaded["artifact_id"])


if __name__ == "__main__":
    unittest.main()
