import json
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
LAB_DIR = Path(__file__).resolve().parent
if str(LAB_DIR) not in sys.path:
    sys.path.insert(0, str(LAB_DIR))

from stress_learning_benchmark import (  # noqa: E402
    run_stress_learning_benchmark,
    write_stress_learning_artifacts,
)


class StressLearningBenchmarkTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.report = run_stress_learning_benchmark(
            count=6,
            ticks=24,
            rng_seed=20260512,
        )

    def test_both_arms_run_for_every_candidate(self):
        report = self.report
        self.assertEqual("stress_learning_benchmark_stage0", report["lab_id"])
        self.assertEqual(6, len(report["candidates"]))
        for record in report["candidates"]:
            self.assertGreaterEqual(record["stress_load"], 0.0)
            self.assertLessEqual(record["stress_load"], 1.0)
            for arm in ("feedback", "frozen"):
                episode = record[arm]
                self.assertGreaterEqual(episode["survival_ticks"], 0)
                self.assertLessEqual(episode["survival_ticks"], 24)
                self.assertIn("need_balance", episode)
            # Feedback is the ONLY difference between the arms.
            self.assertGreater(record["feedback"]["reward_update_count"], 0)
            self.assertEqual(0, record["frozen"]["reward_update_count"])

    def test_summary_measures_the_falsifiable_bar(self):
        summary = self.report["summary"]
        for key in (
            "feedback_survival_rate",
            "frozen_survival_rate",
            "mean_survival_ratio_delta",
            "mean_need_balance_delta",
            "saved_by_feedback_count",
            "lost_by_feedback_count",
        ):
            self.assertIn(key, summary)
        thresholds = self.report["decision"]["thresholds"]
        self.assertIn("feedback_beats_frozen_survival", thresholds)
        self.assertIsInstance(thresholds["feedback_beats_frozen_survival"], bool)
        # The verdict must derive from the measured rates, not a constant.
        expected = (
            summary["feedback_survival_rate"] > summary["frozen_survival_rate"]
        )
        self.assertEqual(expected, thresholds["feedback_beats_frozen_survival"])

    def test_benchmark_is_deterministic(self):
        again = run_stress_learning_benchmark(count=6, ticks=24, rng_seed=20260512)
        self.assertEqual(self.report, again)

    def test_write_artifacts_creates_report_and_readme(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            output_dir = Path(temp_dir)
            write_stress_learning_artifacts(output_dir, self.report)
            artifact = output_dir / "stress_learning_benchmark_stage0.json"
            self.assertTrue(artifact.exists())
            self.assertTrue(
                (output_dir / "stress_learning_README.md").exists()
            )
            loaded = json.loads(artifact.read_text(encoding="utf-8"))
            self.assertEqual("stress_learning_benchmark_stage0", loaded["lab_id"])


if __name__ == "__main__":
    unittest.main()
