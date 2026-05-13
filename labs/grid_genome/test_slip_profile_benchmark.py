import json
import tempfile
import unittest
from pathlib import Path

from slip_profile_benchmark import (
    run_profile_compatibility_suite,
    write_profile_compatibility_artifacts,
)


class SlipProfileBenchmarkTests(unittest.TestCase):
    def test_suite_generates_valid_aligned_corpus_for_each_profile(self):
        profiles = [
            Path("data/slips/valid/slip_lcd_seed.json"),
            Path("data/slips/valid/slip_gray_stable.json"),
            Path("data/slips/valid/slip_amber_social.json"),
        ]

        report = run_profile_compatibility_suite(
            profiles, count_per_profile=12, rng_seed=214
        )

        self.assertEqual(
            [
                "slip_lcd_seed",
                "slip_gray_stable",
                "slip_amber_social",
            ],
            [item["profile_id"] for item in report["profile_results"]],
        )
        self.assertEqual(36, report["totals"]["candidate_count"])
        self.assertEqual(36, report["totals"]["valid_count"])
        self.assertEqual(36, report["totals"]["aligned_count"])
        self.assertEqual(0, report["totals"]["invalid_count"])
        self.assertEqual(0, report["totals"]["misaligned_count"])

        for result in report["profile_results"]:
            self.assertEqual(12, result["candidate_count"])
            self.assertEqual(12, result["valid_count"])
            self.assertEqual(12, result["aligned_count"])
            self.assertEqual(1.0, result["validity_rate"])
            self.assertEqual(1.0, result["alignment_rate"])
            self.assertGreater(result["unique_signatures"], 1)

    def test_writer_creates_report_and_profile_corpora(self):
        profiles = [
            Path("data/slips/valid/slip_lcd_seed.json"),
            Path("data/slips/valid/slip_gray_stable.json"),
        ]
        report = run_profile_compatibility_suite(
            profiles, count_per_profile=3, rng_seed=214
        )

        with tempfile.TemporaryDirectory() as tmpdir:
            output_dir = Path(tmpdir)
            write_profile_compatibility_artifacts(output_dir, report)

            report_path = output_dir / "slip_multi_profile_generation_stage0.json"
            self.assertTrue(report_path.exists())
            persisted = json.loads(report_path.read_text(encoding="utf-8"))
            self.assertEqual(report["totals"], persisted["totals"])

            for result in report["profile_results"]:
                corpus_dir = output_dir / result["profile_id"]
                self.assertTrue(corpus_dir.exists())
                self.assertEqual(3, len(list(corpus_dir.glob("*.json"))))


if __name__ == "__main__":
    unittest.main()
