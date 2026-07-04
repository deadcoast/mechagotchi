import json
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


GRID_GENOME_DIR = Path(__file__).resolve().parents[1] / "grid_genome"
if str(GRID_GENOME_DIR) not in sys.path:
    sys.path.insert(0, str(GRID_GENOME_DIR))

from corpus_builder import build_seed_grids
from slip import is_grid_aligned
from validator import validate_grid

from cubff_transducer import (
    _decision,
    compile_semantic_grid,
    direct_tape_to_grid,
    extract_cubff_features,
    run_transducer_lab,
)


def sample_snapshot() -> dict:
    return {
        "snapshot_id": "cubff_synth_001",
        "epoch": 128,
        "language": "bff_noheads",
        "program_size": 64,
        "tape": [0, 1, 2, 3, 2, 3, 7, 7, 7, 11, 13, 17, 19, 23, 29, 31] * 4,
        "replication_scores": [0, 4, 12, 48, 64, 64, 12, 4],
        "brotli_size": 41,
        "lineage_events": [
            {"parent": 1, "child": 3},
            {"parent": 3, "child": 4},
            {"parent": 3, "child": 5},
        ],
    }


class CubffTransducerTests(unittest.TestCase):
    def test_extract_cubff_features_returns_life_process_signals(self):
        features = extract_cubff_features(sample_snapshot())

        self.assertEqual("cubff_synth_001", features["snapshot_id"])
        self.assertGreater(features["symbol_entropy"], 0)
        self.assertGreater(features["instruction_diversity"], 0)
        self.assertGreater(features["replication_rate"], 0)
        self.assertGreater(features["replication_dominance"], 0)
        self.assertGreater(features["lineage_churn"], 0)
        self.assertGreaterEqual(features["instability"], 0)
        self.assertLessEqual(features["instability"], 1)

    def test_direct_tape_to_grid_is_raw_visual_baseline_not_semantic_genome(self):
        grid = direct_tape_to_grid(sample_snapshot(), grid_id="cubff_direct_test")

        self.assertEqual("cubff_direct_test", grid["grid_id"])
        self.assertEqual([8, 8], grid["grid_size"])
        self.assertEqual("cubff_direct_visual_baseline", grid["metadata"]["source"])
        self.assertFalse(validate_grid(grid).ok)

    def test_compile_semantic_grid_returns_valid_slip_aligned_genome(self):
        profile = json.loads(
            (ROOT / "data/slips/valid/slip_lcd_seed.json").read_text(encoding="utf-8")
        )
        grid = compile_semantic_grid(
            sample_snapshot(),
            build_seed_grids(),
            profile,
            grid_id="cubff_semantic_test",
            rng_seed=5150,
        )

        self.assertTrue(validate_grid(grid).ok, validate_grid(grid).errors)
        self.assertTrue(is_grid_aligned(grid, profile).ok, is_grid_aligned(grid, profile).errors)
        self.assertEqual("cubff_semantic_transducer", grid["metadata"]["source"])
        self.assertIn("cubff_features", grid["metadata"])
        self.assertIn("cubff_semantic_pressure", grid["lineage"]["mutation_events"])

    def test_run_transducer_lab_compares_direct_and_semantic_pipelines(self):
        profile = json.loads(
            (ROOT / "data/slips/valid/slip_lcd_seed.json").read_text(encoding="utf-8")
        )
        report = run_transducer_lab(
            [sample_snapshot()],
            build_seed_grids(),
            profile,
            rng_seed=5150,
        )

        self.assertEqual(1, report["snapshot_count"])
        self.assertEqual(0, report["direct_visual_baseline"]["valid_count"])
        self.assertEqual(1, report["hybrid_semantic_compiler"]["valid_count"])
        self.assertEqual(1, report["hybrid_semantic_compiler"]["slip_aligned_count"])
        self.assertGreater(
            report["hybrid_semantic_compiler"]["mean_readability"],
            report["direct_visual_baseline"]["mean_readability"],
        )
        self.assertEqual("watch_synthetic_only", report["decision"]["status"])
        self.assertIn("beats direct tape projection", report["decision"]["reason"])

    def test_decision_reason_matches_reject_status(self):
        direct = {"mean_readability": 0.5, "validity_rate": 1.0}
        hybrid = {"mean_readability": 0.4, "validity_rate": 1.0}

        decision = _decision(direct, hybrid)

        self.assertEqual("reject_direct_mapping", decision["status"])
        self.assertIn("did not beat", decision["reason"])
        self.assertNotIn("beats direct tape projection here", decision["reason"])

    def test_run_transducer_lab_accepts_precompiled_semantic_grids(self):
        profile = json.loads(
            (ROOT / "data/slips/valid/slip_lcd_seed.json").read_text(encoding="utf-8")
        )
        seed_grids = build_seed_grids()
        snapshots = [sample_snapshot()]
        precompiled = [
            compile_semantic_grid(
                snapshots[0],
                seed_grids,
                profile,
                grid_id="cubff_semantic_000",
                rng_seed=5150,
            )
        ]

        report_precompiled = run_transducer_lab(
            snapshots,
            seed_grids,
            profile,
            rng_seed=5150,
            semantic_grids=precompiled,
        )
        report_internal = run_transducer_lab(
            snapshots,
            seed_grids,
            profile,
            rng_seed=5150,
        )

        self.assertEqual(report_internal, report_precompiled)


if __name__ == "__main__":
    unittest.main()
