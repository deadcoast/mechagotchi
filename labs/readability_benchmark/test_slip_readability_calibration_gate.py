import json
import sys
import tempfile
import unittest
from pathlib import Path


LAB_DIR = Path(__file__).resolve().parent
WORKSHOP_DIR = LAB_DIR.parent / "workshop_editor"
for path in [LAB_DIR, WORKSHOP_DIR]:
    if str(path) not in sys.path:
        sys.path.insert(0, str(path))

from slip_readability_calibration_gate import (
    build_slip_long_horizon_readability_benchmark,
    run_slip_readability_calibration_gate_lab,
    write_slip_readability_calibration_gate_artifacts,
)


LONG_HORIZON_PATH = Path("data/workshop_editor/slip_long_horizon_behavior_gate_stage0.json")


class SLIPReadabilityCalibrationGateTests(unittest.TestCase):
    def test_benchmark_uses_current_long_horizon_selected_and_held_out_samples(self):
        benchmark = build_slip_long_horizon_readability_benchmark(LONG_HORIZON_PATH)

        self.assertEqual("slip_readability_calibration_gate_stage0", benchmark["lab_id"])
        self.assertEqual(21, benchmark["summary"]["sample_count"])
        self.assertEqual(3, benchmark["summary"]["by_source"]["selected_offspring"]["count"])
        self.assertEqual(18, benchmark["summary"]["by_source"]["held_out_long_horizon"]["count"])
        self.assertEqual(3, benchmark["manual_rating_protocol"]["minimum_reviewers"])
        self.assertTrue(
            all(
                "proxy_readability_score" in sample["readability"]
                for sample in benchmark["samples"]
            )
        )

    def test_gate_prepares_template_without_claiming_manual_calibration(self):
        report = run_slip_readability_calibration_gate_lab(
            long_horizon_path=LONG_HORIZON_PATH,
            rating_rows=[],
        )

        self.assertEqual("slip_readability_calibration_gate_stage0", report["artifact_id"])
        self.assertFalse(report["ratings_collected"])
        self.assertFalse(report["manual_readability_calibration_ready"])
        self.assertEqual("awaiting_human_ratings", report["manual_intake"]["summary"]["status"])
        self.assertEqual(21, report["template"]["template_row_count"])
        self.assertEqual(63, report["expected_completed_rating_rows"])
        self.assertIn("slip_long_horizon_readability_packet", report["closed_states"])
        self.assertIn("manual_readability_calibration", report["blocked_states"])
        self.assertIn("profile_weighted_evolution", report["blocked_states"])
        self.assertNotIn("manual_readability_calibration", report["closed_states"])

    def test_complete_in_memory_ratings_can_unlock_calibration_readiness_decision(self):
        benchmark = build_slip_long_horizon_readability_benchmark(LONG_HORIZON_PATH)
        ranked_samples = sorted(
            benchmark["samples"],
            key=lambda sample: sample["readability"]["proxy_readability_score"],
        )
        rows = []
        for reviewer in ["rater_a", "rater_b", "rater_c"]:
            for index, sample in enumerate(ranked_samples):
                rating = str(1 + min(4, index * 5 // len(ranked_samples)))
                rows.append(
                    {
                        "sample_id": sample["sample_id"],
                        "reviewer_id": reviewer,
                        "silhouette": rating,
                        "organ_clarity": rating,
                        "palette_contrast": rating,
                        "animation_readiness": rating,
                        "companion_appeal": rating,
                        "notes": "synthetic unit-test row",
                    }
                )

        report = run_slip_readability_calibration_gate_lab(
            long_horizon_path=LONG_HORIZON_PATH,
            rating_rows=rows,
        )

        self.assertTrue(report["ratings_collected"])
        self.assertTrue(report["manual_readability_calibration_ready"])
        self.assertEqual(3, report["manual_intake"]["summary"]["reviewer_count"])
        self.assertEqual(21, report["manual_intake"]["summary"]["rated_sample_count"])
        self.assertEqual(63, report["manual_intake"]["summary"]["rating_row_count"])
        self.assertEqual(0, report["manual_intake"]["summary"]["row_error_count"])
        self.assertIsNotNone(report["manual_intake"]["summary"]["proxy_human_spearman"])
        self.assertIn("manual_readability_calibration", report["closed_states"])

    def test_partial_or_invalid_ratings_keep_calibration_blocked(self):
        benchmark = build_slip_long_horizon_readability_benchmark(LONG_HORIZON_PATH)
        rows = [
            {
                "sample_id": benchmark["samples"][0]["sample_id"],
                "reviewer_id": "rater_a",
                "silhouette": "5",
                "organ_clarity": "5",
                "palette_contrast": "bad",
                "animation_readiness": "5",
                "companion_appeal": "5",
                "notes": "invalid value",
            }
        ]

        report = run_slip_readability_calibration_gate_lab(
            long_horizon_path=LONG_HORIZON_PATH,
            rating_rows=rows,
        )

        self.assertFalse(report["manual_readability_calibration_ready"])
        self.assertIn("manual_readability_calibration", report["blocked_states"])
        self.assertEqual(1, len(report["manual_intake"]["row_errors"]))

    def test_write_artifacts_creates_report_template_packet_and_readme(self):
        report = run_slip_readability_calibration_gate_lab(
            long_horizon_path=LONG_HORIZON_PATH,
            rating_rows=[],
        )

        with tempfile.TemporaryDirectory() as temp_dir:
            output_dir = Path(temp_dir)
            write_slip_readability_calibration_gate_artifacts(output_dir, report)

            summary_path = output_dir / "slip_readability_calibration_gate_stage0.json"
            template_path = output_dir / "slip_readability_calibration_template.csv"
            packet_path = output_dir / "slip_readability_calibration_reviewer_packet.md"
            self.assertTrue(summary_path.exists())
            self.assertTrue(template_path.exists())
            self.assertTrue(packet_path.exists())
            loaded = json.loads(summary_path.read_text(encoding="utf-8"))
            self.assertEqual(report["metrics"], loaded["metrics"])
            template_lines = template_path.read_text(encoding="utf-8").splitlines()
            self.assertEqual(22, len(template_lines))
            self.assertTrue((output_dir / "slip_readability_calibration_README.md").exists())


if __name__ == "__main__":
    unittest.main()
