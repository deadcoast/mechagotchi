import json
import tempfile
import unittest
from pathlib import Path

from wfc_grid import (
    build_wfc_corpus,
    build_wfc_report,
    generate_wfc_grid,
    rich_matrix_from_grid,
    split_corpus,
    train_wfc_model,
    write_wfc_artifacts,
)


import sys

LAB_DIR = Path(__file__).resolve().parent
REPO_ROOT = LAB_DIR.parents[1]
GRID_GENOME = REPO_ROOT / "labs" / "grid_genome"
if str(GRID_GENOME) not in sys.path:
    sys.path.insert(0, str(GRID_GENOME))

from corpus_builder import build_seed_grids, build_seed_grids_16  # noqa: E402
from validator import validate_grid  # noqa: E402


class RichMatrixTests(unittest.TestCase):
    def test_projection_round_trips_the_rich_vocabulary(self):
        # The Phase-A remainder this lab closes: shells, joints, limbs,
        # antennae, sensors, decorations, and effects must survive the
        # matrix projection instead of degrading to body/eye/mouth.
        beetle = next(
            grid
            for grid in build_seed_grids_16()
            if grid["grid_id"].endswith("beetle")
        )
        matrix = rich_matrix_from_grid(beetle)
        self.assertEqual(16, len(matrix))
        tokens = {token for row in matrix for token in row}
        for token in ["S", "J", "L", "E", "M", "N", "P", "B", "A", "."]:
            self.assertIn(token, tokens)
        anchors = sum(row.count("A") for row in matrix)
        self.assertEqual(1, anchors)


class SplitTests(unittest.TestCase):
    def test_split_is_stratified_deterministic_30_10_10(self):
        # The dossier's 72/24/24 protocol adapted to the real corpus:
        # 30/10/10, stratified per palette (6/2/2 of each).
        seeds = build_seed_grids_16()
        train, dev, holdout = split_corpus(seeds)
        self.assertEqual(30, len(train))
        self.assertEqual(10, len(dev))
        self.assertEqual(10, len(holdout))
        ids = [grid["grid_id"] for grid in train + dev + holdout]
        self.assertEqual(50, len(set(ids)))
        for bucket, expected in [(train, 6), (dev, 2), (holdout, 2)]:
            per_palette: dict[str, int] = {}
            for grid in bucket:
                palette = grid["palette"]["palette_id"]
                per_palette[palette] = per_palette.get(palette, 0) + 1
            self.assertEqual({expected} , set(per_palette.values()))
        again = split_corpus(build_seed_grids_16())
        self.assertEqual(
            [grid["grid_id"] for grid in train],
            [grid["grid_id"] for grid in again[0]],
        )


class WfcModelTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.train_grids = split_corpus(build_seed_grids_16())[0]
        cls.model = train_wfc_model(cls.train_grids)

    def test_model_learns_positions_and_adjacency_from_the_corpus(self):
        self.assertEqual(16, self.model["width"])
        self.assertEqual(16, self.model["height"])
        self.assertEqual(
            ["down", "right"], sorted(self.model["adjacency"])
        )
        self.assertEqual(
            16 * 16, len(self.model["position_candidates"])
        )
        center = self.model["position_candidates"]["7,7"]
        self.assertIn("B", center)
        self.assertGreater(self.model["total_pairs"], 0)

    def test_training_is_deterministic_and_rejects_mixed_sizes(self):
        again = train_wfc_model(split_corpus(build_seed_grids_16())[0])
        self.assertEqual(
            json.dumps(self.model, sort_keys=True),
            json.dumps(again, sort_keys=True),
        )
        with self.assertRaises(ValueError):
            train_wfc_model([build_seed_grids()[0], self.train_grids[0]])


class WfcGenerationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.train_grids = split_corpus(build_seed_grids_16())[0]
        cls.model = train_wfc_model(cls.train_grids)
        cls.corpus = build_wfc_corpus(cls.model, count=25, rng_seed=1030)

    def test_generation_is_deterministic_per_seed(self):
        first = generate_wfc_grid(self.model, grid_id="mg_wfc_det", rng_seed=7)
        second = generate_wfc_grid(self.model, grid_id="mg_wfc_det", rng_seed=7)
        self.assertEqual(first, second)
        different = generate_wfc_grid(
            self.model, grid_id="mg_wfc_det", rng_seed=8
        )
        self.assertNotEqual(first["cells"], different["cells"])

    def test_candidates_are_16x16_with_unique_ids_and_single_anchors(self):
        self.assertEqual(25, len(self.corpus))
        self.assertEqual(
            25, len({grid["grid_id"] for grid in self.corpus})
        )
        for grid in self.corpus:
            with self.subTest(grid_id=grid["grid_id"]):
                self.assertEqual([16, 16], grid["grid_size"])
                anchors = sum(
                    1
                    for cell in grid["cells"]
                    if cell["animation_anchor"] is True
                )
                self.assertEqual(1, anchors)
                self.assertEqual(
                    "wfc_grid_lab", grid["metadata"]["source"]
                )

    def test_validity_rate_meets_the_lab_floor(self):
        valid = sum(
            1 for grid in self.corpus if validate_grid(grid).ok
        )
        self.assertGreaterEqual(valid / len(self.corpus), 0.6)

    def test_candidates_emit_the_rich_vocabulary(self):
        # The point of Phase B: generated creatures keep shells, limbs,
        # and the rest of the DR 0015 alphabet.
        roles = {
            cell["role"] for grid in self.corpus for cell in grid["cells"]
        }
        rich = roles - {"body", "eye", "mouth"}
        self.assertGreaterEqual(len(rich), 3, roles)

    def test_candidates_are_not_training_copies(self):
        train_signatures = {
            json.dumps(
                sorted(
                    (cell["x"], cell["y"], cell["role"])
                    for cell in grid["cells"]
                )
            )
            for grid in self.train_grids
        }
        copies = sum(
            1
            for grid in self.corpus
            if json.dumps(
                sorted(
                    (cell["x"], cell["y"], cell["role"])
                    for cell in grid["cells"]
                )
            )
            in train_signatures
        )
        self.assertLessEqual(copies / len(self.corpus), 0.2)


class WfcReportTests(unittest.TestCase):
    def test_report_is_deterministic_and_artifacts_round_trip(self):
        report = build_wfc_report()
        again = build_wfc_report()
        self.assertEqual(
            json.dumps(report, sort_keys=True),
            json.dumps(again, sort_keys=True),
        )
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
            self.assertIn(key, report)
        self.assertEqual("wfc_grid_stage0", report["artifact_id"])
        metrics = report["metrics"]
        self.assertEqual(30, metrics["split"]["train"])
        self.assertGreaterEqual(metrics["validity_rate"], 0.6)
        self.assertGreaterEqual(metrics["rich_role_count"], 3)
        with tempfile.TemporaryDirectory() as tmp:
            output_dir = Path(tmp)
            write_wfc_artifacts(output_dir, report)
            artifact = output_dir / "wfc_grid_stage0.json"
            self.assertTrue(artifact.exists())
            loaded = json.loads(artifact.read_text(encoding="utf-8"))
            self.assertEqual(report["metrics"], loaded["metrics"])


if __name__ == "__main__":
    unittest.main()
