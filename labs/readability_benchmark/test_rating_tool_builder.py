import csv
import json
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
LAB_DIR = Path(__file__).resolve().parent
if str(LAB_DIR) not in sys.path:
    sys.path.insert(0, str(LAB_DIR))

from rating_tool_builder import (  # noqa: E402
    CSV_HEADER,
    build_rating_tool_html,
    build_rating_tool_report,
    collect_rating_samples,
    write_rating_tool_artifacts,
)


TEMPLATE_CSV = ROOT / "data" / "readability" / "slip_readability_calibration_template.csv"


class RatingToolBuilderTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.samples = collect_rating_samples()

    def test_collect_rating_samples_matches_template_order(self):
        with open(TEMPLATE_CSV, encoding="utf-8") as handle:
            template_rows = list(csv.DictReader(handle))
        self.assertEqual(
            [row["sample_id"] for row in template_rows],
            [sample["sample_id"] for sample in self.samples],
        )
        for sample in self.samples:
            self.assertGreater(len(sample["cells"]), 0)
            self.assertIn("colors", sample["palette"])
            for cell in sample["cells"]:
                self.assertIn("x", cell)
                self.assertIn("visual", cell)

    def test_samples_never_leak_proxy_scores(self):
        # Protocol: reviewers rate before seeing proxy readability values,
        # so the tool payload must not contain them.
        for sample in self.samples:
            self.assertNotIn("readability", sample)
            self.assertNotIn("proxy_readability_score", json.dumps(sample))

    def test_build_rating_tool_html_embeds_samples_and_contract(self):
        html = build_rating_tool_html(self.samples)
        self.assertNotIn("__SAMPLES__", html)
        self.assertIn(CSV_HEADER, html)
        self.assertIn("slip_readability_calibration_ratings.csv", html)
        for sample in self.samples:
            self.assertIn(sample["sample_id"], html)
        # Deterministic: same samples give identical bytes.
        self.assertEqual(html, build_rating_tool_html(self.samples))

    def test_report_and_artifacts(self):
        html = build_rating_tool_html(self.samples)
        report = build_rating_tool_report(self.samples, html)
        self.assertEqual("slip_readability_rating_tool_stage0", report["lab_id"])
        self.assertEqual(21, report["sample_count"])
        self.assertEqual(63, report["expected_completed_rows"])
        self.assertIn("decision", report)

        with tempfile.TemporaryDirectory() as temp_dir:
            output_dir = Path(temp_dir)
            write_rating_tool_artifacts(output_dir, report, html)
            tool_path = output_dir / "slip_readability_calibration_rating_tool.html"
            self.assertTrue(tool_path.exists())
            self.assertTrue(
                (output_dir / "slip_readability_rating_tool_stage0.json").exists()
            )
            self.assertIn(CSV_HEADER, tool_path.read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
