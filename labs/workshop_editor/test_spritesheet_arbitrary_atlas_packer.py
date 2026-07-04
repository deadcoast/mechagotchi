import json
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


WORKSHOP_DIR = Path(__file__).resolve().parent
GRID_GENOME_DIR = WORKSHOP_DIR.parents[0] / "grid_genome"
for import_path in [WORKSHOP_DIR, GRID_GENOME_DIR]:
    if str(import_path) not in sys.path:
        sys.path.insert(0, str(import_path))

from slip import is_grid_aligned
from spritesheet_arbitrary_atlas_packer import (
    ARBITRARY_ATLAS_POLICIES,
    export_arbitrary_atlas_suite_with_sidecars,
    import_arbitrary_atlas_with_sidecar,
    run_spritesheet_arbitrary_atlas_packer_lab,
    write_spritesheet_arbitrary_atlas_packer_artifacts,
)
from standard_image_sidecar_decoder import decode_png_rgba
from validator import validate_grid
from workshop_editor import compare_semantic_grid_fidelity


VALID_PROFILE_PATHS = [
    ROOT / "data/slips/valid/slip_lcd_seed.json",
    ROOT / "data/slips/valid/slip_gray_stable.json",
    ROOT / "data/slips/valid/slip_amber_social.json",
]
GENERATED_ROOT = ROOT / "data/slips/multi_profile_generation_stage0"


def load_profile(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def first_grid_for(profile: dict) -> dict:
    grid_path = sorted((GENERATED_ROOT / profile["profile_id"]).glob("*.json"))[0]
    return json.loads(grid_path.read_text(encoding="utf-8"))


def rects_overlap(left: dict, right: dict) -> bool:
    return not (
        left["x"] + left["w"] <= right["x"]
        or right["x"] + right["w"] <= left["x"]
        or left["y"] + left["h"] <= right["y"]
        or right["y"] + right["h"] <= left["y"]
    )


class SpritesheetArbitraryAtlasPackerTests(unittest.TestCase):
    def test_exports_shelf_and_maxrects_arbitrary_atlases_with_valid_geometry(self):
        profile = load_profile(VALID_PROFILE_PATHS[0])
        grid = first_grid_for(profile)

        exports = export_arbitrary_atlas_suite_with_sidecars(grid, profile)
        algorithms = [export["packing_policy"]["algorithm_id"] for export in exports]

        self.assertEqual([policy["algorithm_id"] for policy in ARBITRARY_ATLAS_POLICIES], algorithms)
        self.assertEqual(2, len(exports))
        for export in exports:
            decoded = decode_png_rgba(export["png_bytes"])
            animation = export["sidecar"]["animation_binding"]
            frames = animation["frames"]
            rects = [frame["rect"] for frame in frames]
            y_values = {rect["y"] for rect in rects}
            sizes = {(rect["w"], rect["h"]) for rect in rects}

            self.assertEqual("arbitrary_atlas_sidecar_v1", animation["animation_model"])
            self.assertEqual(export["packing_policy"]["algorithm_id"], animation["packing_policy"]["algorithm_id"])
            self.assertEqual({"w": 8, "h": 8}, animation["source_frame_size"])
            self.assertGreaterEqual(len(frames), 5)
            self.assertGreater(len(sizes), 2)
            self.assertGreater(len(y_values), 1)
            self.assertLess(decoded["width"] * decoded["height"], 8 * 8 * len(frames))
            self.assertGreater(export["packing_policy"]["occupancy_rate"], 0.45)
            self.assertTrue(any(frame["rotation_degrees"] == 90 for frame in frames))
            for frame in frames:
                rect = frame["rect"]
                self.assertGreaterEqual(rect["x"], 0)
                self.assertGreaterEqual(rect["y"], 0)
                self.assertGreater(rect["w"], 0)
                self.assertGreater(rect["h"], 0)
                self.assertLessEqual(rect["x"] + rect["w"], decoded["width"])
                self.assertLessEqual(rect["y"] + rect["h"], decoded["height"])
                self.assertTrue(frame["canonical_pixel_hash"].startswith("sha256:"))
                self.assertTrue(frame["packed_pixel_hash"].startswith("sha256:"))
            for index, left in enumerate(rects):
                for right in rects[index + 1 :]:
                    self.assertFalse(rects_overlap(left, right), (left, right))

    def test_import_reconstructs_semantic_grid_and_canonical_frames_for_each_policy(self):
        profile = load_profile(VALID_PROFILE_PATHS[0])
        grid = first_grid_for(profile)

        for exported in export_arbitrary_atlas_suite_with_sidecars(grid, profile):
            imported = import_arbitrary_atlas_with_sidecar(
                exported["png_bytes"],
                exported["sidecar"],
                source_grid=grid,
            )
            restored = imported["restored_grid"]
            diff = compare_semantic_grid_fidelity(grid, restored)

            self.assertTrue(imported["ok"], imported["errors"])
            self.assertTrue(validate_grid(restored).ok, validate_grid(restored).errors)
            self.assertTrue(is_grid_aligned(restored, profile).ok)
            self.assertEqual(1.0, imported["semantic_fidelity"])
            self.assertEqual(1.0, imported["reconstructed_frame_fidelity"])
            self.assertEqual(1.0, imported["runtime_frame_fidelity"])
            self.assertEqual([], diff["changed_cells"])
            self.assertEqual([], diff["missing_cells"])
            self.assertEqual([], diff["added_cells"])
            self.assertEqual(
                [0, 1, 2, 3, 4, 0],
                [event["frame_index"] for event in imported["runtime_playback"]["timeline"]],
            )

    def test_lab_report_records_policy_comparison_without_production_claims(self):
        report = run_spritesheet_arbitrary_atlas_packer_lab(
            VALID_PROFILE_PATHS,
            GENERATED_ROOT,
        )

        self.assertEqual("spritesheet_arbitrary_atlas_packer_stage0", report["artifact_id"])
        self.assertEqual(3, report["profile_count"])
        self.assertEqual(2, report["packing_policy_count"])
        self.assertEqual(6, report["atlas_roundtrip_success_count"])
        self.assertEqual(6, report["invalid_probe_rejected_count"])
        self.assertEqual(1.0, report["metrics"]["atlas_roundtrip_success_rate"])
        self.assertEqual(1.0, report["metrics"]["mean_semantic_fidelity"])
        self.assertEqual(1.0, report["metrics"]["mean_reconstructed_frame_fidelity"])
        self.assertEqual(1.0, report["metrics"]["mean_runtime_frame_fidelity"])
        self.assertEqual(
            "maxrects_best_short_side_fit",
            report["policy_comparison"]["best_occupancy_policy"],
        )
        self.assertIn("arbitrary_atlas_packing_geometry", report["closed_states"])
        self.assertIn("maxrects_best_short_side_fit_policy", report["closed_states"])
        self.assertIn("shelf_height_desc_baseline_policy", report["closed_states"])
        self.assertNotIn("arbitrary atlas packing", report["blocked_states"])
        self.assertIn("production renderer playback", report["blocked_states"])
        self.assertIn("live external editor rewrite validation", report["blocked_states"])
        self.assertIn("package runtime lifecycle integration", report["blocked_states"])
        self.assertIn("profile-weighted evolution", report["blocked_states"])

    def test_import_rejects_overlap_bounds_hash_duration_algorithm_and_rotation_policy_faults(self):
        report = run_spritesheet_arbitrary_atlas_packer_lab(
            VALID_PROFILE_PATHS,
            GENERATED_ROOT,
        )
        families = {
            family
            for result in report["invalid_probe_results"]
            for family in result["error_families"]
        }

        self.assertIn("atlas_frame_rect_overlap", families)
        self.assertIn("atlas_frame_rect_out_of_bounds", families)
        self.assertIn("atlas_frame_hash_mismatch", families)
        self.assertIn("runtime_frame_duration_invalid", families)
        self.assertIn("atlas_packing_algorithm_unsupported", families)
        self.assertIn("atlas_frame_rotation_policy_violation", families)

    def test_write_artifacts_creates_pngs_sidecars_report_and_app_payload(self):
        report = run_spritesheet_arbitrary_atlas_packer_lab(
            VALID_PROFILE_PATHS,
            GENERATED_ROOT,
        )

        with tempfile.TemporaryDirectory() as temp_dir:
            output_dir = Path(temp_dir)
            write_spritesheet_arbitrary_atlas_packer_artifacts(output_dir, report)

            summary_path = output_dir / "spritesheet_arbitrary_atlas_packer_stage0.json"
            self.assertTrue(summary_path.exists())
            persisted = json.loads(summary_path.read_text(encoding="utf-8"))
            self.assertEqual(report["metrics"], persisted["metrics"])
            self.assertTrue((output_dir / "slip_lcd_seed_maxrects_arbitrary_atlas.png").exists())
            self.assertTrue((output_dir / "slip_lcd_seed_maxrects_arbitrary_atlas_sidecar.json").exists())
            self.assertTrue((output_dir / "slip_lcd_seed_shelf_arbitrary_atlas.png").exists())
            self.assertTrue((output_dir / "README.md").exists())
            app_data = (output_dir / "spritesheet_arbitrary_atlas_packer_data.js").read_text(
                encoding="utf-8"
            )
            self.assertIn("MECHAGOTCHI_SPRITESHEET_ARBITRARY_ATLAS_PACKER", app_data)


if __name__ == "__main__":
    unittest.main()
