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

from png_deep_color_sidecar_decoder import (
    DEEP_COLOR_VARIANT_SPECS,
    decode_png_deep_color,
    export_png_deep_color_suite_with_sidecars,
    import_png_deep_color_with_sidecar,
    run_png_deep_color_sidecar_decoder_lab,
    write_png_deep_color_sidecar_decoder_artifacts,
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
EXPECTED_VARIANTS = {
    "grayscale_1bit",
    "grayscale_2bit",
    "grayscale_4bit",
    "grayscale_16bit",
    "indexed_1bit",
    "indexed_2bit",
    "indexed_4bit",
    "truecolor_16bit",
    "grayscale_alpha_8bit",
    "grayscale_alpha_16bit",
    "rgba_16bit",
}


def load_profile(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def first_grid_for(profile: dict) -> dict:
    grid_path = sorted((GENERATED_ROOT / profile["profile_id"]).glob("*.json"))[0]
    return json.loads(grid_path.read_text(encoding="utf-8"))


def expected_scanline_bytes(width: int, color_type: int, bit_depth: int) -> int:
    channels = {0: 1, 2: 3, 3: 1, 4: 2, 6: 4}[color_type]
    return (width * channels * bit_depth + 7) // 8


class PNGDeepColorSidecarDecoderTests(unittest.TestCase):
    def test_decoder_supports_low_bit_16bit_and_grayscale_alpha_variants(self):
        profile = load_profile(VALID_PROFILE_PATHS[0])
        grid = first_grid_for(profile)
        width = grid["grid_size"][0]

        exports = export_png_deep_color_suite_with_sidecars(grid, profile)
        decoded = {
            variant["variant_id"]: decode_png_deep_color(variant["png_bytes"])
            for variant in exports
        }

        self.assertEqual(EXPECTED_VARIANTS, set(decoded.keys()))
        self.assertEqual(EXPECTED_VARIANTS, {spec["variant_id"] for spec in DEEP_COLOR_VARIANT_SPECS})
        for spec in DEEP_COLOR_VARIANT_SPECS:
            with self.subTest(variant_id=spec["variant_id"]):
                item = decoded[spec["variant_id"]]
                self.assertEqual(spec["color_type"], item["color_type"])
                self.assertEqual(spec["bit_depth"], item["bit_depth"])
                self.assertEqual(
                    expected_scanline_bytes(width, spec["color_type"], spec["bit_depth"]),
                    item["scanline_byte_length"],
                )
                self.assertEqual([0, 1, 2, 3, 4], item["filter_types_seen"])
                self.assertEqual(grid["grid_size"][0] * grid["grid_size"][1], item["pixel_count"])

        self.assertEqual(4, decoded["grayscale_alpha_8bit"]["color_type"])
        self.assertEqual(8, decoded["grayscale_alpha_8bit"]["bit_depth"])
        self.assertEqual(4, decoded["grayscale_alpha_16bit"]["color_type"])
        self.assertEqual(16, decoded["grayscale_alpha_16bit"]["bit_depth"])
        self.assertEqual(16, decoded["rgba_16bit"]["bit_depth"])

    def test_import_variants_restore_semantics_even_when_visual_carrier_is_quantized(self):
        profile = load_profile(VALID_PROFILE_PATHS[0])
        grid = first_grid_for(profile)

        for exported in export_png_deep_color_suite_with_sidecars(grid, profile):
            with self.subTest(variant_id=exported["variant_id"]):
                imported = import_png_deep_color_with_sidecar(
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

    def test_import_rejects_malformed_or_unbound_deep_color_png_variants(self):
        profile = load_profile(VALID_PROFILE_PATHS[0])
        grid = first_grid_for(profile)
        report = run_png_deep_color_sidecar_decoder_lab(
            VALID_PROFILE_PATHS,
            GENERATED_ROOT,
        )
        families = {
            family
            for result in report["invalid_probe_results"]
            for family in result["error_families"]
        }

        exported = export_png_deep_color_suite_with_sidecars(grid, profile)[0]
        wrong_hash_sidecar = json.loads(json.dumps(exported["sidecar"]))
        wrong_hash_sidecar["asset_binding"]["content_hash"] = "sha256:not-the-png"
        wrong_hash_result = import_png_deep_color_with_sidecar(
            exported["png_bytes"],
            wrong_hash_sidecar,
        )

        self.assertIn("png_bit_depth_color_type_invalid", families)
        self.assertIn("png_scanline_length_mismatch", families)
        self.assertIn("png_filter_type_unsupported", families)
        self.assertIn("png_deep_color_bit_depth_mismatch", families)
        self.assertIn("png_deep_color_pixel_hash_mismatch", families)
        self.assertIn("asset_hash_mismatch", families)
        self.assertFalse(wrong_hash_result["ok"])
        self.assertIn("asset_hash_mismatch", wrong_hash_result["error_families"])

    def test_lab_report_closes_deep_color_subset_without_full_png_conformance_claim(self):
        report = run_png_deep_color_sidecar_decoder_lab(
            VALID_PROFILE_PATHS,
            GENERATED_ROOT,
        )

        self.assertEqual("png_deep_color_sidecar_decoder_stage0", report["artifact_id"])
        self.assertEqual(3, report["profile_count"])
        self.assertEqual(33, report["variant_roundtrip_success_count"])
        self.assertEqual(6, report["invalid_probe_rejected_count"])
        self.assertEqual(1.0, report["metrics"]["mean_semantic_fidelity"])
        self.assertEqual([1, 2, 4, 8, 16], report["metrics"]["supported_bit_depths"])
        self.assertEqual([0, 2, 3, 4, 6], report["metrics"]["supported_color_types"])
        self.assertIn("png_grayscale_low_bit_depth_decoder", report["closed_states"])
        self.assertIn("png_indexed_low_bit_depth_decoder", report["closed_states"])
        self.assertIn("png_16bit_sample_decoder", report["closed_states"])
        self.assertIn("png_color_type_4_grayscale_alpha_decoder", report["closed_states"])
        self.assertIn("png_deep_color_sidecar_semantic_restore", report["closed_states"])
        self.assertNotIn("png_bit_depth_1_2_4_16_decoder", report["blocked_states"])
        self.assertNotIn("png_color_type_4_grayscale_alpha_decoder", report["blocked_states"])
        self.assertIn("apng_decoder", report["blocked_states"])
        self.assertIn("full_png_conformance", report["blocked_states"])
        self.assertIn("live_external_editor_rewrite_validation", report["blocked_states"])
        self.assertIn("final_png_production_carrier_selection", report["blocked_states"])

    def test_write_artifacts_creates_pngs_sidecars_report_and_app_payload(self):
        report = run_png_deep_color_sidecar_decoder_lab(
            VALID_PROFILE_PATHS,
            GENERATED_ROOT,
        )

        with tempfile.TemporaryDirectory() as temp_dir:
            output_dir = Path(temp_dir)
            write_png_deep_color_sidecar_decoder_artifacts(output_dir, report)

            summary_path = output_dir / "png_deep_color_sidecar_decoder_stage0.json"
            self.assertTrue(summary_path.exists())
            persisted = json.loads(summary_path.read_text(encoding="utf-8"))
            self.assertEqual(report["metrics"], persisted["metrics"])
            self.assertTrue((output_dir / "slip_lcd_seed_grayscale_1bit.png").exists())
            self.assertTrue((output_dir / "slip_lcd_seed_grayscale_1bit_sidecar.json").exists())
            self.assertTrue((output_dir / "README.md").exists())
            app_data = (output_dir / "png_deep_color_sidecar_decoder_data.js").read_text(
                encoding="utf-8"
            )
            self.assertIn("MECHAGOTCHI_PNG_DEEP_COLOR_SIDECAR_DECODER", app_data)


if __name__ == "__main__":
    unittest.main()
