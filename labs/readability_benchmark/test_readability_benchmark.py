import json
import sys
import tempfile
import unittest
from copy import deepcopy
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
GRID_GENOME = ROOT / "labs" / "grid_genome"
for path in [ROOT, GRID_GENOME]:
    if str(path) not in sys.path:
        sys.path.insert(0, str(path))

from corpus_builder import build_seed_grids
from readability_benchmark import (
    build_heldout_readability_benchmark,
    manual_rating_protocol,
    score_readability,
    write_readability_artifacts,
)


class ReadabilityBenchmarkTests(unittest.TestCase):
    def test_score_readability_returns_required_metrics(self):
        grid = build_seed_grids()[0]

        result = score_readability(grid)

        self.assertEqual(grid["grid_id"], result["grid_id"])
        self.assertIn("proxy_readability_score", result)
        self.assertIn("connected_components", result["metrics"])
        self.assertIn("body_mass_ratio", result["metrics"])
        self.assertIn("silhouette_entropy", result["metrics"])
        self.assertIn("symmetry_score", result["metrics"])
        self.assertIn("organ_detectability", result["metrics"])
        self.assertIn("palette_contrast", result["metrics"])
        self.assertIn("animation_anchor_coverage", result["metrics"])
        self.assertGreaterEqual(result["proxy_readability_score"], 0)
        self.assertLessEqual(result["proxy_readability_score"], 1)

    def test_palette_contrast_penalizes_low_contrast_grid(self):
        grid = build_seed_grids()[0]
        low_contrast = deepcopy(grid)
        low_contrast["grid_id"] = "low_contrast_fixture"
        low_contrast["palette"]["colors"] = ["#222222", "#242424", "#252525"]
        for cell in low_contrast["cells"]:
            cell["visual"] = "#242424"

        normal_score = score_readability(grid)
        low_score = score_readability(low_contrast)

        self.assertGreater(
            normal_score["metrics"]["palette_contrast"],
            low_score["metrics"]["palette_contrast"],
        )
        self.assertGreater(
            normal_score["proxy_readability_score"],
            low_score["proxy_readability_score"],
        )

    def test_manual_rating_protocol_has_no_synthetic_human_ratings(self):
        protocol = manual_rating_protocol()

        self.assertEqual("readability_rating_v0_1", protocol["protocol_id"])
        self.assertEqual([1, 2, 3, 4, 5], protocol["rating_scale"])
        self.assertIn("silhouette", protocol["questions"])
        self.assertIn("organ_clarity", protocol["questions"])
        self.assertFalse(protocol["ratings_collected"])

    def test_heldout_benchmark_contains_multiple_sources_and_rating_packet(self):
        benchmark = build_heldout_readability_benchmark(count_per_source=6, rng_seed=20260512)

        self.assertEqual("readability_benchmark_stage0", benchmark["lab_id"])
        self.assertFalse(benchmark["manual_rating_protocol"]["ratings_collected"])
        source_names = {entry["source"] for entry in benchmark["samples"]}
        self.assertGreaterEqual(len(source_names), 3)
        self.assertEqual(18, len(benchmark["samples"]))
        self.assertEqual(18, benchmark["summary"]["sample_count"])
        self.assertIn("mean_proxy_readability", benchmark["summary"]["by_source"]["seed_holdout"])

    def test_write_readability_artifacts_creates_json_and_protocol(self):
        benchmark = build_heldout_readability_benchmark(count_per_source=2, rng_seed=7)
        with tempfile.TemporaryDirectory() as temp_dir:
            output_dir = Path(temp_dir)

            write_readability_artifacts(output_dir, benchmark)

            report = output_dir / "readability_stage0.json"
            protocol = output_dir / "manual_rating_protocol.md"
            self.assertTrue(report.exists())
            self.assertTrue(protocol.exists())
            written = json.loads(report.read_text(encoding="utf-8"))
            self.assertEqual(benchmark["lab_id"], written["lab_id"])


if __name__ == "__main__":
    unittest.main()
