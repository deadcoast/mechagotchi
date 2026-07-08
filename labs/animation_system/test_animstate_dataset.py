import json
import sys
import tempfile
import unittest
from pathlib import Path

from animstate_dataset import (
    DATASET_ID,
    build_animstate_dataset,
    build_animstate_report,
    write_animstate_artifacts,
)
from clip_model import clip_frame_count, clip_names

LAB_DIR = Path(__file__).resolve().parent
REPO_ROOT = LAB_DIR.parents[1]
GRID_GENOME = REPO_ROOT / "labs" / "grid_genome"
if str(GRID_GENOME) not in sys.path:
    sys.path.insert(0, str(GRID_GENOME))


class AnimstateDatasetTests(unittest.TestCase):
    dataset: dict

    @classmethod
    def setUpClass(cls):
        cls.dataset = build_animstate_dataset()

    def test_dataset_meets_and_names_the_documented_scale(self):
        # The documents name animstate_300 (>=300 labeled samples); at
        # clip-frame resolution over the 16x16 corpus the honest size is
        # 950, and the dataset says so instead of wearing the old size.
        self.assertEqual("animstate_950", DATASET_ID)
        self.assertEqual(DATASET_ID, self.dataset["dataset_id"])
        self.assertEqual(
            "animstate_300", self.dataset["supersedes"]["documented_name"]
        )
        expected = 50 * sum(clip_frame_count(clip) for clip in clip_names())
        self.assertEqual(expected, len(self.dataset["samples"]))
        self.assertGreaterEqual(len(self.dataset["samples"]), 300)

    def test_samples_carry_the_labels_phase_d_consumes(self):
        for sample in self.dataset["samples"][:25]:
            for key in [
                "grid_id",
                "palette_id",
                "clip",
                "state",
                "frame_index",
                "frame_count",
                "cells",
                "anchors",
            ]:
                self.assertIn(key, sample)
            self.assertIn(sample["clip"], clip_names())
            self.assertEqual(1, len(sample["anchors"]))

    def test_coverage_is_complete(self):
        seen = {
            (sample["grid_id"], sample["clip"], sample["frame_index"])
            for sample in self.dataset["samples"]
        }
        self.assertEqual(len(self.dataset["samples"]), len(seen))
        creatures = {sample["grid_id"] for sample in self.dataset["samples"]}
        self.assertEqual(50, len(creatures))
        palettes = {
            sample["palette_id"] for sample in self.dataset["samples"]
        }
        self.assertEqual(5, len(palettes))
        states = {sample["state"] for sample in self.dataset["samples"]}
        self.assertEqual(
            {"idle", "blink", "sleep", "beg", "ill"}, states
        )

    def test_dataset_is_deterministic(self):
        again = build_animstate_dataset()
        self.assertEqual(
            json.dumps(self.dataset, sort_keys=True),
            json.dumps(again, sort_keys=True),
        )

    def test_report_gates_and_artifacts(self):
        report = build_animstate_report()
        metrics = report["metrics"]
        self.assertEqual(950, metrics["sample_count"])
        self.assertEqual(1.0, metrics["frames_in_bounds_rate"])
        self.assertEqual(1.0, metrics["frames_palette_clean_rate"])
        with tempfile.TemporaryDirectory() as tmp:
            output_dir = Path(tmp)
            write_animstate_artifacts(output_dir, report, self.dataset)
            dataset_path = output_dir / f"{DATASET_ID}.json"
            self.assertTrue(dataset_path.exists())
            self.assertTrue(
                (output_dir / "animstate_dataset_stage0.json").exists()
            )
            self.assertTrue((output_dir / "README.md").exists())
            loaded = json.loads(dataset_path.read_text(encoding="utf-8"))
            self.assertEqual(950, len(loaded["samples"]))


if __name__ == "__main__":
    unittest.main()
