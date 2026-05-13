import csv
import json
import tempfile
import unittest
from pathlib import Path

from manual_rating_intake import (
    build_rating_template,
    load_rating_rows,
    run_manual_rating_intake_lab,
    write_manual_rating_intake_artifacts,
)
from readability_benchmark import build_heldout_readability_benchmark


class ManualRatingIntakeTests(unittest.TestCase):
    def test_build_rating_template_has_one_blank_row_per_sample(self):
        benchmark = build_heldout_readability_benchmark(count_per_source=2, rng_seed=7)
        template = build_rating_template(benchmark)

        self.assertEqual(benchmark["summary"]["sample_count"], len(template["rows"]))
        self.assertEqual("readability_rating_v0_1", template["protocol_id"])
        first_row = template["rows"][0]
        self.assertIn("sample_id", first_row)
        self.assertIn("reviewer_id", first_row)
        self.assertEqual("", first_row["silhouette"])
        self.assertEqual("", first_row["companion_appeal"])

    def test_no_rating_file_reports_awaiting_human_ratings(self):
        benchmark = build_heldout_readability_benchmark(count_per_source=2, rng_seed=7)

        report = run_manual_rating_intake_lab(benchmark=benchmark, rating_rows=[])

        self.assertEqual("manual_readability_rating_intake_stage0", report["lab_id"])
        self.assertEqual("awaiting_human_ratings", report["summary"]["status"])
        self.assertEqual(0, report["summary"]["rating_row_count"])
        self.assertEqual(benchmark["summary"]["sample_count"], report["summary"]["template_row_count"])
        self.assertFalse(report["ratings_collected"])

    def test_rating_rows_are_aggregated_and_compared_to_proxy_scores(self):
        benchmark = build_heldout_readability_benchmark(count_per_source=1, rng_seed=7)
        sample_ids = [sample["sample_id"] for sample in benchmark["samples"]]
        rows = []
        for reviewer in ["rater_a", "rater_b", "rater_c"]:
            for sample_id in sample_ids:
                rows.append(
                    {
                        "sample_id": sample_id,
                        "reviewer_id": reviewer,
                        "silhouette": "4",
                        "organ_clarity": "4",
                        "palette_contrast": "5",
                        "animation_readiness": "3",
                        "companion_appeal": "4",
                        "notes": "",
                    }
                )

        report = run_manual_rating_intake_lab(benchmark=benchmark, rating_rows=rows)

        self.assertEqual("ratings_collected", report["summary"]["status"])
        self.assertTrue(report["ratings_collected"])
        self.assertEqual(3, report["summary"]["reviewer_count"])
        self.assertEqual(len(rows), report["summary"]["rating_row_count"])
        self.assertEqual(len(sample_ids), report["summary"]["rated_sample_count"])
        self.assertGreaterEqual(report["summary"]["mean_human_rating"], 1)
        self.assertLessEqual(report["summary"]["mean_human_rating"], 5)
        self.assertIn("proxy_human_spearman", report["summary"])

    def test_load_rating_rows_reads_csv(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            path = Path(temp_dir) / "ratings.csv"
            with path.open("w", newline="", encoding="utf-8") as handle:
                writer = csv.DictWriter(
                    handle,
                    fieldnames=[
                        "sample_id",
                        "reviewer_id",
                        "silhouette",
                        "organ_clarity",
                        "palette_contrast",
                        "animation_readiness",
                        "companion_appeal",
                        "notes",
                    ],
                )
                writer.writeheader()
                writer.writerow(
                    {
                        "sample_id": "seed_holdout:mg_seed_001",
                        "reviewer_id": "rater_a",
                        "silhouette": "4",
                        "organ_clarity": "5",
                        "palette_contrast": "4",
                        "animation_readiness": "3",
                        "companion_appeal": "4",
                        "notes": "clear",
                    }
                )

            rows = load_rating_rows(path)

            self.assertEqual(1, len(rows))
            self.assertEqual("rater_a", rows[0]["reviewer_id"])

    def test_write_manual_rating_intake_artifacts_creates_report_and_template(self):
        benchmark = build_heldout_readability_benchmark(count_per_source=1, rng_seed=7)
        report = run_manual_rating_intake_lab(benchmark=benchmark, rating_rows=[])
        with tempfile.TemporaryDirectory() as temp_dir:
            output_dir = Path(temp_dir)

            write_manual_rating_intake_artifacts(output_dir, report)

            report_path = output_dir / "manual_readability_rating_intake_stage0.json"
            template_path = output_dir / "manual_rating_template.csv"
            self.assertTrue(report_path.exists())
            self.assertTrue(template_path.exists())
            loaded = json.loads(report_path.read_text(encoding="utf-8"))
            self.assertEqual(report["lab_id"], loaded["lab_id"])


if __name__ == "__main__":
    unittest.main()
