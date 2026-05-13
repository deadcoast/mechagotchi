import json
import tempfile
import unittest
from pathlib import Path

from ctm_inspired_ticks import (
    run_ctm_tick_lab,
    run_deliberative_switchboard,
    write_ctm_tick_artifacts,
)


def ambiguous_state():
    return {
        "hunger": 0.58,
        "energy": 0.42,
        "bond": 0.6,
        "stress": 0.48,
        "grid_stability": 0.66,
        "recent_interactions": [1, 0, 1, 0, 1],
        "action_rewards": {
            "feed": [0.5],
            "play": [0.55],
            "sleep": [0.52],
            "idle": [0.48],
            "mutate": [0.5],
        },
    }


class CtmInspiredTickTests(unittest.TestCase):
    def test_deliberative_switchboard_spends_extra_ticks_when_confidence_is_low(self):
        result = run_deliberative_switchboard(
            ambiguous_state(),
            max_ticks=4,
            confidence_threshold=0.72,
        )

        self.assertGreater(result["tick_count"], 1)
        self.assertLessEqual(result["tick_count"], 4)
        self.assertEqual(result["tick_count"], len(result["trace"]))
        self.assertGreaterEqual(
            result["final_decision"]["confidence"],
            result["baseline_decision"]["confidence"],
        )
        self.assertIn(result["final_decision"]["action"], result["final_utilities"])

    def test_deliberative_switchboard_stops_after_one_tick_when_confidence_is_high(self):
        state = ambiguous_state()
        state["hunger"] = 0.18
        state["energy"] = 0.08
        state["action_rewards"]["sleep"] = [0.9, 0.8]

        result = run_deliberative_switchboard(
            state,
            max_ticks=4,
            confidence_threshold=0.72,
        )

        self.assertEqual(1, result["tick_count"])
        self.assertEqual("sleep", result["final_decision"]["action"])

    def test_run_ctm_tick_lab_compares_single_pass_and_deliberative_results(self):
        report = run_ctm_tick_lab(max_ticks=4, confidence_threshold=0.72)

        self.assertEqual("ctm_inspired_ticks_stage0", report["lab_id"])
        self.assertGreaterEqual(report["summary"]["scenario_count"], 4)
        self.assertGreaterEqual(
            report["summary"]["deliberative_accuracy"],
            report["summary"]["baseline_accuracy"],
        )
        self.assertGreater(report["summary"]["mean_confidence_gain"], 0)
        self.assertGreater(report["summary"]["extra_tick_case_count"], 0)
        self.assertIn(report["decision"]["status"], {"prototype", "watch"})

    def test_write_ctm_tick_artifacts_creates_report(self):
        report = run_ctm_tick_lab(max_ticks=3, confidence_threshold=0.72)
        with tempfile.TemporaryDirectory() as temp_dir:
            output_dir = Path(temp_dir)
            write_ctm_tick_artifacts(output_dir, report)

            report_path = output_dir / "ctm_inspired_ticks_stage0.json"
            self.assertTrue(report_path.exists())
            loaded = json.loads(report_path.read_text(encoding="utf-8"))
            self.assertEqual("ctm_inspired_ticks_stage0", loaded["lab_id"])


if __name__ == "__main__":
    unittest.main()
