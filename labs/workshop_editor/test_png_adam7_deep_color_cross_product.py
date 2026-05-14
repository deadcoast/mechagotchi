import json
import sys
import tempfile
import unittest
from pathlib import Path


WORKSHOP_DIR = Path(__file__).resolve().parent
GRID_GENOME_DIR = WORKSHOP_DIR.parents[0] / "grid_genome"
for import_path in [WORKSHOP_DIR, GRID_GENOME_DIR]:
    if str(import_path) not in sys.path:
        sys.path.insert(0, str(import_path))

from png_adam7_deep_color_cross_product import (
    ADAM7_DEEP_COLOR_VARIANT_SPECS,
    decode_png_adam7_deep_color,
    export_png_adam7_deep_color_suite_with_sidecars,
    import_png_adam7_deep_color_with_sidecar,
    run_png_adam7_deep_color_cross_product_lab,
    write_png_adam7_deep_color_cross_product_artifacts,
)
from png_adam7_interlace_decoder import ADAM7_PASSES
from png_deep_color_sidecar_decoder import DEEP_COLOR_VARIANT_SPECS
from slip import is_grid_aligned
from validator import validate_grid
from workshop_editor import compare_semantic_grid_fidelity


VALID_PROFILE_PATHS = [
    Path("data/slips/valid/slip_lcd_seed.json"),
    Path("data/slips/valid/slip_gray_stable.json"),
    Path("data/slips/valid/slip_amber_social.json"),
]
GENERATED_ROOT = Path("data/slips/multi_profile_generation_stage0")
EXPECTED_VARIANTS = {
    f"adam7_{spec['variant_id']}"
    for spec in DEEP_COLOR_VARIANT_SPECS
}


def load_profile(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def first_grid_for(profile: dict) -> dict:
    grid_path = sorted((GENERATED_ROOT / profile["profile_id"]).glob("*.json"))[0]
    return json.loads(grid_path.read_text(encoding="utf-8"))


class PNGAdam7DeepColorCrossProductTests(unittest.TestCase):
    def test_decoder_extracts_adam7_passes_for_each_deep_color_variant(self):
        profile = load_profile(VALID_PROFILE_PATHS[0])
        grid = first_grid_for(profile)

        exports = export_png_adam7_deep_color_suite_with_sidecars(grid, profile)
        decoded = {
            item["variant_id"]: decode_png_adam7_deep_color(item["png_bytes"])
            for item in exports
        }

        self.assertEqual(EXPECTED_VARIANTS, set(decoded.keys()))
        self.assertEqual(EXPECTED_VARIANTS, {spec["variant_id"] for spec in ADAM7_DEEP_COLOR_VARIANT_SPECS})
        for spec in ADAM7_DEEP_COLOR_VARIANT_SPECS:
            with self.subTest(variant_id=spec["variant_id"]):
                item = decoded[spec["variant_id"]]
                self.assertEqual(1, item["interlace_method"])
                self.assertEqual(spec["color_type"], item["color_type"])
                self.assertEqual(spec["bit_depth"], item["bit_depth"])
                self.assertEqual(
                    [pass_spec["pass_index"] for pass_spec in ADAM7_PASSES],
                    item["pass_order"],
                )
                self.assertEqual(7, item["non_empty_pass_count"])
                self.assertEqual([0, 1, 2, 3, 4], item["filter_types_seen"])
                self.assertEqual(grid["grid_size"][0] * grid["grid_size"][1], item["pixel_count"])
                self.assertEqual(7, len(item["pass_summaries"]))
                for pass_summary in item["pass_summaries"]:
                    self.assertIn("scanline_byte_length", pass_summary)
                    self.assertIn("filter_bpp", pass_summary)

        self.assertEqual(4, decoded["adam7_grayscale_alpha_8bit"]["color_type"])
        self.assertEqual(16, decoded["adam7_grayscale_alpha_16bit"]["bit_depth"])
        self.assertEqual(16, decoded["adam7_rgba_16bit"]["bit_depth"])

    def test_import_adam7_deep_color_variants_restore_sidecar_semantics(self):
        profile = load_profile(VALID_PROFILE_PATHS[0])
        grid = first_grid_for(profile)

        for exported in export_png_adam7_deep_color_suite_with_sidecars(grid, profile):
            with self.subTest(variant_id=exported["variant_id"]):
                imported = import_png_adam7_deep_color_with_sidecar(
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

    def test_import_rejects_cross_product_png_and_binding_faults(self):
        profile = load_profile(VALID_PROFILE_PATHS[0])
        grid = first_grid_for(profile)
        report = run_png_adam7_deep_color_cross_product_lab(
            VALID_PROFILE_PATHS,
            GENERATED_ROOT,
        )
        families = {
            family
            for result in report["invalid_probe_results"]
            for family in result["error_families"]
        }

        exported = export_png_adam7_deep_color_suite_with_sidecars(grid, profile)[0]
        wrong_hash_sidecar = json.loads(json.dumps(exported["sidecar"]))
        wrong_hash_sidecar["asset_binding"]["content_hash"] = "sha256:not-the-png"
        wrong_hash_result = import_png_adam7_deep_color_with_sidecar(
            exported["png_bytes"],
            wrong_hash_sidecar,
        )

        self.assertIn("png_adam7_deep_color_interlace_required", families)
        self.assertIn("png_adam7_deep_color_scanline_length_mismatch", families)
        self.assertIn("png_filter_type_unsupported", families)
        self.assertIn("png_adam7_deep_color_pass_manifest_mismatch", families)
        self.assertIn("png_adam7_deep_color_bit_depth_mismatch", families)
        self.assertIn("png_adam7_deep_color_pixel_hash_mismatch", families)
        self.assertIn("asset_hash_mismatch", families)
        self.assertFalse(wrong_hash_result["ok"])
        self.assertIn("asset_hash_mismatch", wrong_hash_result["error_families"])

    def test_lab_report_closes_cross_product_without_apng_or_full_conformance_claim(self):
        report = run_png_adam7_deep_color_cross_product_lab(
            VALID_PROFILE_PATHS,
            GENERATED_ROOT,
        )

        self.assertEqual("png_adam7_deep_color_cross_product_stage0", report["artifact_id"])
        self.assertEqual(3, report["profile_count"])
        self.assertEqual(33, report["variant_roundtrip_success_count"])
        self.assertEqual(7, report["invalid_probe_rejected_count"])
        self.assertEqual(1.0, report["metrics"]["mean_semantic_fidelity"])
        self.assertEqual(1.0, report["metrics"]["mean_pixel_fidelity"])
        self.assertEqual(7.0, report["metrics"]["mean_non_empty_pass_count"])
        self.assertEqual([1, 2, 4, 8, 16], report["metrics"]["supported_bit_depths"])
        self.assertEqual([0, 2, 3, 4, 6], report["metrics"]["supported_color_types"])
        self.assertIn("png_adam7_deep_color_cross_product_decoder", report["closed_states"])
        self.assertIn("png_adam7_deep_color_pass_manifest", report["closed_states"])
        self.assertIn("png_adam7_deep_color_sidecar_semantic_restore", report["closed_states"])
        self.assertNotIn("adam7_deep_color_cross_product_decoder", report["blocked_states"])
        self.assertIn("apng_decoder", report["blocked_states"])
        self.assertIn("full_png_conformance", report["blocked_states"])
        self.assertIn("live_external_editor_rewrite_validation", report["blocked_states"])
        self.assertIn("final_png_production_carrier_selection", report["blocked_states"])

    def test_write_artifacts_creates_cross_product_pngs_sidecars_report_and_app_payload(self):
        report = run_png_adam7_deep_color_cross_product_lab(
            VALID_PROFILE_PATHS,
            GENERATED_ROOT,
        )

        with tempfile.TemporaryDirectory() as temp_dir:
            output_dir = Path(temp_dir)
            write_png_adam7_deep_color_cross_product_artifacts(output_dir, report)

            summary_path = output_dir / "png_adam7_deep_color_cross_product_stage0.json"
            self.assertTrue(summary_path.exists())
            persisted = json.loads(summary_path.read_text(encoding="utf-8"))
            self.assertEqual(report["metrics"], persisted["metrics"])
            self.assertTrue((output_dir / "slip_lcd_seed_adam7_grayscale_1bit.png").exists())
            self.assertTrue((output_dir / "slip_lcd_seed_adam7_grayscale_1bit_sidecar.json").exists())
            self.assertTrue((output_dir / "README.md").exists())
            app_data = (output_dir / "png_adam7_deep_color_cross_product_data.js").read_text(
                encoding="utf-8"
            )
            self.assertIn("MECHAGOTCHI_PNG_ADAM7_DEEP_COLOR_CROSS_PRODUCT", app_data)


if __name__ == "__main__":
    unittest.main()
