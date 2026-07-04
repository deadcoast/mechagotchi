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
from spritesheet_layout_variant_decoder import (
    export_spritesheet_layout_variant_suite_with_sidecars,
    import_spritesheet_layout_variant_with_sidecar,
    run_spritesheet_layout_variant_decoder_lab,
    write_spritesheet_layout_variant_decoder_artifacts,
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


class SpritesheetLayoutVariantDecoderTests(unittest.TestCase):
    def test_exports_vertical_matrix_padded_and_sparse_atlas_layouts(self):
        profile = load_profile(VALID_PROFILE_PATHS[0])
        grid = first_grid_for(profile)

        exports = export_spritesheet_layout_variant_suite_with_sidecars(grid, profile)
        decoded_by_layout = {
            item["layout_id"]: decode_png_rgba(item["png_bytes"])
            for item in exports
        }
        rects_by_layout = {
            item["layout_id"]: [
                frame["rect"]
                for frame in item["sidecar"]["animation_binding"]["frames"]
            ]
            for item in exports
        }

        self.assertEqual(
            {
                "vertical_strip",
                "row_major_matrix",
                "padded_grid",
                "sparse_atlas",
            },
            set(decoded_by_layout.keys()),
        )
        self.assertEqual((8, 24), (decoded_by_layout["vertical_strip"]["width"], decoded_by_layout["vertical_strip"]["height"]))
        self.assertEqual([0, 8, 16], [rect["y"] for rect in rects_by_layout["vertical_strip"]])
        self.assertEqual((16, 16), (decoded_by_layout["row_major_matrix"]["width"], decoded_by_layout["row_major_matrix"]["height"]))
        self.assertEqual([{"x": 0, "y": 0, "w": 8, "h": 8}, {"x": 8, "y": 0, "w": 8, "h": 8}, {"x": 0, "y": 8, "w": 8, "h": 8}], rects_by_layout["row_major_matrix"])
        self.assertEqual((28, 10), (decoded_by_layout["padded_grid"]["width"], decoded_by_layout["padded_grid"]["height"]))
        self.assertEqual([1, 10, 19], [rect["x"] for rect in rects_by_layout["padded_grid"]])
        self.assertEqual((19, 21), (decoded_by_layout["sparse_atlas"]["width"], decoded_by_layout["sparse_atlas"]["height"]))
        self.assertEqual([{"x": 0, "y": 0, "w": 8, "h": 8}, {"x": 11, "y": 1, "w": 8, "h": 8}, {"x": 1, "y": 13, "w": 8, "h": 8}], rects_by_layout["sparse_atlas"])

    def test_import_layout_variants_restore_valid_slip_aligned_grids(self):
        profile = load_profile(VALID_PROFILE_PATHS[0])
        grid = first_grid_for(profile)

        for exported in export_spritesheet_layout_variant_suite_with_sidecars(grid, profile):
            with self.subTest(layout_id=exported["layout_id"]):
                imported = import_spritesheet_layout_variant_with_sidecar(
                    exported["png_bytes"],
                    exported["sidecar"],
                    source_grid=grid,
                )
                restored = imported["restored_grid"]
                diff = compare_semantic_grid_fidelity(grid, restored)

                self.assertTrue(imported["ok"], imported["errors"])
                self.assertTrue(validate_grid(restored).ok, validate_grid(restored).errors)
                self.assertTrue(is_grid_aligned(restored, profile).ok)
                self.assertEqual(3, imported["frame_count"])
                self.assertEqual(1.0, imported["semantic_fidelity"])
                self.assertEqual(1.0, imported["frame_pixel_fidelity"])
                self.assertEqual([], diff["changed_cells"])
                self.assertEqual([], diff["missing_cells"])
                self.assertEqual([], diff["added_cells"])

    def test_import_rejects_invalid_layout_rectangles_and_frame_hashes(self):
        report = run_spritesheet_layout_variant_decoder_lab(
            VALID_PROFILE_PATHS,
            GENERATED_ROOT,
        )
        families = {
            family
            for result in report["invalid_probe_results"]
            for family in result["error_families"]
        }

        self.assertIn("spritesheet_frame_rect_out_of_bounds", families)
        self.assertIn("spritesheet_frame_rect_overlap", families)
        self.assertIn("spritesheet_frame_hash_mismatch", families)

    def test_lab_report_closes_layout_variants_without_project_or_runtime_claims(self):
        report = run_spritesheet_layout_variant_decoder_lab(
            VALID_PROFILE_PATHS,
            GENERATED_ROOT,
        )

        self.assertEqual("spritesheet_layout_variant_decoder_stage0", report["artifact_id"])
        self.assertEqual(3, report["profile_count"])
        self.assertEqual(12, report["layout_roundtrip_success_count"])
        self.assertEqual(3, report["invalid_probe_rejected_count"])
        self.assertEqual(1.0, report["metrics"]["mean_semantic_fidelity"])
        self.assertEqual(1.0, report["metrics"]["mean_frame_pixel_fidelity"])
        self.assertIn("spritesheet_vertical_matrix_padded_sparse_layout_decoder", report["closed_states"])
        self.assertNotIn("spritesheet_variant_layout_coverage", report["blocked_states"])
        self.assertIn("spritesheet_packed_rotation_trim_decoder", report["blocked_states"])
        self.assertIn("full_project_format_coverage", report["blocked_states"])
        self.assertIn("runtime_animation_playback", report["blocked_states"])
        self.assertIn("profile_weighted_evolution", report["blocked_states"])

    def test_write_artifacts_creates_layout_pngs_sidecars_report_and_app_payload(self):
        report = run_spritesheet_layout_variant_decoder_lab(
            VALID_PROFILE_PATHS,
            GENERATED_ROOT,
        )

        with tempfile.TemporaryDirectory() as temp_dir:
            output_dir = Path(temp_dir)
            write_spritesheet_layout_variant_decoder_artifacts(output_dir, report)

            summary_path = output_dir / "spritesheet_layout_variant_decoder_stage0.json"
            self.assertTrue(summary_path.exists())
            persisted = json.loads(summary_path.read_text(encoding="utf-8"))
            self.assertEqual(report["metrics"], persisted["metrics"])
            self.assertTrue((output_dir / "slip_lcd_seed_vertical_strip_spritesheet.png").exists())
            self.assertTrue((output_dir / "slip_lcd_seed_vertical_strip_sidecar.json").exists())
            self.assertTrue((output_dir / "README.md").exists())
            app_data = (output_dir / "spritesheet_layout_variant_decoder_data.js").read_text(
                encoding="utf-8"
            )
            self.assertIn("MECHAGOTCHI_SPRITESHEET_LAYOUT_VARIANTS", app_data)


if __name__ == "__main__":
    unittest.main()
