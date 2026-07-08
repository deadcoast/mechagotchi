import json
import tempfile
import unittest
from pathlib import Path

from animation_bandit_hmm_mood import (
    build_bandit_hmm_report,
    evaluate_bandit_keepers,
    evaluate_hmm_on_replay,
    load_clip_catalog,
    write_bandit_hmm_artifacts,
)

LAB_DIR = Path(__file__).resolve().parent
REPO_ROOT = LAB_DIR.parents[1]
SAMPLE = (
    REPO_ROOT
    / "data"
    / "datasets"
    / "replay_100k_ticks"
    / "replay_sample_first_200.jsonl"
)


class ClipCatalogTests(unittest.TestCase):
    def test_animstate_950_yields_a_five_clip_catalog_per_creature(self):
        catalog = load_clip_catalog()
        self.assertGreaterEqual(len(catalog), 50)
        for grid_id, clips in list(catalog.items())[:5]:
            self.assertEqual(
                ["beg", "blink", "idle", "ill", "sleep"], sorted(clips)
            )
            for clip, frame_count in clips.items():
                self.assertGreater(frame_count, 0)


class BanditKeeperTests(unittest.TestCase):
    evaluation: dict

    @classmethod
    def setUpClass(cls):
        cls.evaluation = evaluate_bandit_keepers()

    def test_deterministic_under_seeds(self):
        self.assertEqual(self.evaluation, evaluate_bandit_keepers())

    def test_bandit_beats_the_rotation_baseline_for_every_keeper(self):
        for keeper in self.evaluation["keepers"]:
            with self.subTest(keeper=keeper["keeper_id"]):
                self.assertLess(
                    keeper["bandit_regret"], keeper["rotation_regret"]
                )

    def test_bandit_converges_on_the_preferred_clips(self):
        for keeper in self.evaluation["keepers"]:
            with self.subTest(keeper=keeper["keeper_id"]):
                self.assertGreaterEqual(
                    keeper["final_quarter_best_arm_rate"], 0.6
                )
                self.assertLess(
                    keeper["final_quarter_regret_rate"],
                    keeper["first_quarter_regret_rate"],
                )


class HmmReplayTests(unittest.TestCase):
    evaluation: dict

    @classmethod
    def setUpClass(cls):
        cls.evaluation = evaluate_hmm_on_replay(SAMPLE)

    def test_oscillation_is_reduced(self):
        self.assertLess(
            self.evaluation["hmm_switch_rate"],
            self.evaluation["raw_switch_rate"],
        )

    def test_next_mood_prediction_beats_persistence(self):
        self.assertLess(
            self.evaluation["hmm_next_mood_brier"],
            self.evaluation["persistence_next_mood_brier"],
        )

    def test_uncertainty_is_honest(self):
        # Confidence must be lower exactly where the filter disagrees
        # with the raw label — uncertainty concentrated at the seams.
        self.assertLess(
            self.evaluation["mean_confidence_on_disagreement"],
            self.evaluation["mean_confidence_on_agreement"],
        )

    def test_agreement_stays_high_on_stable_segments(self):
        # Raw labels in runs of >=3 are trustworthy ground truth; the
        # filter must track them. (Overall agreement is capped by the
        # flicker ticks the filter exists to smooth — recorded, not
        # asserted.)
        self.assertGreaterEqual(self.evaluation["stable_agreement_rate"], 0.9)


class ReportTests(unittest.TestCase):
    report: dict

    @classmethod
    def setUpClass(cls):
        cls.report = build_bandit_hmm_report()

    def test_report_shape_and_gates(self):
        for key in [
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
        ]:
            self.assertIn(key, self.report)
        self.assertEqual(
            "animation_bandit_hmm_mood_stage0", self.report["artifact_id"]
        )
        self.assertEqual("complete", self.report["status"])
        self.assertEqual(self.report, json.loads(json.dumps(self.report)))
        self.assertTrue(self.report["blocked_states"])
        self.assertEqual(
            2501, self.report["metrics"]["hmm_replay"]["episodes"]
        )

    def test_write_artifacts_round_trips(self):
        with tempfile.TemporaryDirectory() as tmp:
            output_dir = Path(tmp)
            write_bandit_hmm_artifacts(output_dir, self.report)
            written = output_dir / "animation_bandit_hmm_mood_stage0.json"
            self.assertTrue(written.exists())
            self.assertEqual(
                self.report,
                json.loads(written.read_text(encoding="utf-8")),
            )


if __name__ == "__main__":
    unittest.main()
