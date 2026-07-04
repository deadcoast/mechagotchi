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

from png_variant_sidecar_decoder import (
    decode_png_variant,
    export_png_variant_suite_with_sidecars,
    import_png_variant_with_sidecar,
    run_png_variant_sidecar_decoder_lab,
    write_png_variant_sidecar_decoder_artifacts,
)
from slip import is_grid_aligned
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


class PNGVariantSidecarDecoderTests(unittest.TestCase):
    def test_decoder_supports_explicit_png_color_type_and_filter_variants(self):
        profile = load_profile(VALID_PROFILE_PATHS[0])
        grid = first_grid_for(profile)

        exports = export_png_variant_suite_with_sidecars(grid, profile)
        decoded = {
            variant["variant_id"]: decode_png_variant(variant["png_bytes"])
            for variant in exports
        }

        self.assertEqual(
            {
                "rgba_filter_none",
                "rgba_filter_cycle",
                "rgb_truecolor_sub",
                "grayscale_up",
                "indexed_palette_average_paeth",
            },
            set(decoded.keys()),
        )
        self.assertEqual(6, decoded["rgba_filter_none"]["color_type"])
        self.assertEqual([0], decoded["rgba_filter_none"]["filter_types_seen"])
        self.assertEqual([0, 1, 2, 3, 4], decoded["rgba_filter_cycle"]["filter_types_seen"])
        self.assertEqual(2, decoded["rgb_truecolor_sub"]["color_type"])
        self.assertEqual([1], decoded["rgb_truecolor_sub"]["filter_types_seen"])
        self.assertEqual(0, decoded["grayscale_up"]["color_type"])
        self.assertEqual([2], decoded["grayscale_up"]["filter_types_seen"])
        self.assertEqual(3, decoded["indexed_palette_average_paeth"]["color_type"])
        self.assertEqual([3, 4], decoded["indexed_palette_average_paeth"]["filter_types_seen"])
        self.assertEqual(grid["grid_size"][0] * grid["grid_size"][1], decoded["indexed_palette_average_paeth"]["pixel_count"])

    def test_import_variants_with_sidecars_restore_valid_slip_aligned_grids(self):
        profile = load_profile(VALID_PROFILE_PATHS[0])
        grid = first_grid_for(profile)

        for exported in export_png_variant_suite_with_sidecars(grid, profile):
            with self.subTest(variant_id=exported["variant_id"]):
                imported = import_png_variant_with_sidecar(
                    exported["png_bytes"],
                    exported["sidecar"],
                )
                restored = imported["restored_grid"]
                diff = compare_semantic_grid_fidelity(grid, restored)

                self.assertTrue(imported["ok"], imported["errors"])
                self.assertTrue(validate_grid(restored).ok, validate_grid(restored).errors)
                self.assertTrue(is_grid_aligned(restored, profile).ok)
                self.assertEqual([], diff["changed_cells"])
                self.assertEqual([], diff["missing_cells"])
                self.assertEqual([], diff["added_cells"])
                self.assertEqual(1.0, imported["semantic_fidelity"])
                self.assertEqual(1.0, imported["pixel_fidelity"])

    def test_import_rejects_unsupported_or_unbound_png_variants(self):
        profile = load_profile(VALID_PROFILE_PATHS[0])
        grid = first_grid_for(profile)
        report = run_png_variant_sidecar_decoder_lab(
            VALID_PROFILE_PATHS,
            GENERATED_ROOT,
        )
        families = {
            family
            for result in report["invalid_probe_results"]
            for family in result["error_families"]
        }

        exported = export_png_variant_suite_with_sidecars(grid, profile)[0]
        wrong_hash_sidecar = json.loads(json.dumps(exported["sidecar"]))
        wrong_hash_sidecar["asset_binding"]["content_hash"] = "sha256:not-the-png"
        wrong_hash_result = import_png_variant_with_sidecar(
            exported["png_bytes"],
            wrong_hash_sidecar,
        )

        self.assertIn("png_interlace_unsupported", families)
        self.assertIn("png_plte_missing", families)
        self.assertFalse(wrong_hash_result["ok"])
        self.assertIn("asset_hash_mismatch", wrong_hash_result["error_families"])

    def test_lab_report_closes_variant_coverage_without_full_png_conformance_claim(self):
        report = run_png_variant_sidecar_decoder_lab(
            VALID_PROFILE_PATHS,
            GENERATED_ROOT,
        )

        self.assertEqual("png_variant_sidecar_decoder_stage0", report["artifact_id"])
        self.assertEqual(3, report["profile_count"])
        self.assertEqual(15, report["variant_roundtrip_success_count"])
        self.assertEqual(3, report["invalid_probe_rejected_count"])
        self.assertEqual(1.0, report["metrics"]["mean_semantic_fidelity"])
        self.assertIn("png_color_type_0_2_3_6_8bit_decoder", report["closed_states"])
        self.assertIn("png_filter_types_0_to_4_decoder", report["closed_states"])
        self.assertIn("png_variant_sidecar_semantic_restore", report["closed_states"])
        self.assertNotIn("png_variant_decoder_coverage", report["blocked_states"])
        self.assertIn("png_adam7_interlace_decoder", report["blocked_states"])
        self.assertIn("apng_decoder", report["blocked_states"])
        self.assertIn("full_png_conformance", report["blocked_states"])
        self.assertNotIn("spritesheet_variant_layout_coverage", report["blocked_states"])
        self.assertIn("spritesheet_packed_rotation_trim_decoder", report["blocked_states"])
        self.assertIn("runtime_animation_playback", report["blocked_states"])

    def test_write_artifacts_creates_variant_pngs_sidecars_report_and_app_payload(self):
        report = run_png_variant_sidecar_decoder_lab(
            VALID_PROFILE_PATHS,
            GENERATED_ROOT,
        )

        with tempfile.TemporaryDirectory() as temp_dir:
            output_dir = Path(temp_dir)
            write_png_variant_sidecar_decoder_artifacts(output_dir, report)

            summary_path = output_dir / "png_variant_sidecar_decoder_stage0.json"
            self.assertTrue(summary_path.exists())
            persisted = json.loads(summary_path.read_text(encoding="utf-8"))
            self.assertEqual(report["metrics"], persisted["metrics"])
            self.assertTrue((output_dir / "slip_lcd_seed_rgba_filter_none.png").exists())
            self.assertTrue((output_dir / "slip_lcd_seed_rgba_filter_none_sidecar.json").exists())
            self.assertTrue((output_dir / "README.md").exists())
            app_data = (output_dir / "png_variant_sidecar_decoder_data.js").read_text(
                encoding="utf-8"
            )
            self.assertIn("MECHAGOTCHI_PNG_VARIANT_SIDECAR_DECODER", app_data)


if __name__ == "__main__":
    unittest.main()
