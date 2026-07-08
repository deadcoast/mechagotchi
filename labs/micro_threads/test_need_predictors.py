import json
import tempfile
import unittest
from pathlib import Path

from need_predictors import (
    PREDICTOR_KEYS,
    build_need_predictor_report,
    evaluate_replay_dataset,
    write_need_predictor_artifacts,
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


class EvaluationHarnessTests(unittest.TestCase):
    def test_sample_evaluation_is_deterministic(self):
        first = evaluate_replay_dataset(SAMPLE)
        second = evaluate_replay_dataset(SAMPLE)
        self.assertEqual(first, second)

    def test_every_predictor_is_scored_with_a_baseline(self):
        evaluation = evaluate_replay_dataset(SAMPLE)
        for key in PREDICTOR_KEYS:
            with self.subTest(predictor=key):
                scores = evaluation["predictors"][key]
                self.assertGreater(scores["predictions"], 0)
                self.assertIn("predictor_error", scores)
                self.assertIn("baseline_error", scores)
                self.assertIn("calibration", scores)
                self.assertEqual(
                    4, len(scores["calibration"]["bins"])
                )


class ReportTests(unittest.TestCase):
    report: dict

    @classmethod
    def setUpClass(cls):
        cls.report = build_need_predictor_report()

    def test_report_shape_and_serializability(self):
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
            "need_predictors_stage0", self.report["artifact_id"]
        )
        self.assertEqual(self.report, json.loads(json.dumps(self.report)))
        self.assertTrue(self.report["blocked_states"])

    def test_full_dataset_coverage(self):
        metrics = self.report["metrics"]
        self.assertEqual(2501, metrics["episodes"])
        self.assertGreater(metrics["rows"], 100_000 - 10)

    def test_every_predictor_beats_its_baseline(self):
        # The D2 bar: each predictor beats its documented online baseline
        # on the engine's own replayed histories.
        for key in PREDICTOR_KEYS:
            with self.subTest(predictor=key):
                scores = self.report["metrics"]["predictors"][key]
                self.assertLess(
                    scores["predictor_error"], scores["baseline_error"]
                )
                self.assertTrue(scores["beats_baseline"])

    def test_confidence_is_calibrated(self):
        # Calibration bar: the top-confidence quartile's error is no worse
        # than the bottom quartile's — confidence must MEAN something.
        for key in PREDICTOR_KEYS:
            with self.subTest(predictor=key):
                calibration = self.report["metrics"]["predictors"][key][
                    "calibration"
                ]
                bins = calibration["bins"]
                self.assertLessEqual(
                    bins[-1]["error"], bins[0]["error"]
                )
                self.assertTrue(calibration["top_bin_no_worse_than_bottom"])

    def test_write_artifacts_round_trips(self):
        with tempfile.TemporaryDirectory() as tmp:
            output_dir = Path(tmp)
            write_need_predictor_artifacts(output_dir, self.report)
            written = output_dir / "need_predictors_stage0.json"
            self.assertTrue(written.exists())
            self.assertEqual(
                self.report,
                json.loads(written.read_text(encoding="utf-8")),
            )


if __name__ == "__main__":
    unittest.main()
