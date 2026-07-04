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

from png_adam7_interlace_decoder import (
    ADAM7_PASSES,
    decode_png_adam7_rgba,
    export_png_adam7_with_sidecar,
    import_png_adam7_with_sidecar,
    run_png_adam7_interlace_decoder_lab,
    write_png_adam7_interlace_decoder_artifacts,
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


class PNGAdam7InterlaceDecoderTests(unittest.TestCase):
    def test_decoder_extracts_all_adam7_passes_and_reconstructs_pixels(self):
        profile = load_profile(VALID_PROFILE_PATHS[0])
        grid = first_grid_for(profile)

        exported = export_png_adam7_with_sidecar(grid, profile)
        decoded = decode_png_adam7_rgba(exported["png_bytes"])

        self.assertEqual(1, decoded["interlace_method"])
        self.assertEqual(6, decoded["color_type"])
        self.assertEqual(8, decoded["bit_depth"])
        self.assertEqual([pass_spec["pass_index"] for pass_spec in ADAM7_PASSES], decoded["pass_order"])
        self.assertEqual(7, decoded["non_empty_pass_count"])
        self.assertEqual(64, decoded["pixel_count"])
        self.assertEqual([0, 1, 2, 3, 4], decoded["filter_types_seen"])
        self.assertEqual(
            decoded["pass_summaries"],
            exported["sidecar"]["adam7_binding"]["pass_summaries"],
        )
        self.assertEqual(
            exported["sidecar"]["adam7_binding"]["source_render_pixel_hash"],
            exported["sidecar"]["adam7_binding"]["visual_carrier_pixel_hash"],
        )

    def test_import_adam7_with_sidecar_restores_valid_slip_aligned_grid(self):
        profile = load_profile(VALID_PROFILE_PATHS[0])
        grid = first_grid_for(profile)
        exported = export_png_adam7_with_sidecar(grid, profile)

        imported = import_png_adam7_with_sidecar(
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

    def test_import_rejects_interlace_scanline_filter_manifest_pixel_and_asset_faults(self):
        profile = load_profile(VALID_PROFILE_PATHS[0])
        grid = first_grid_for(profile)
        exported = export_png_adam7_with_sidecar(grid, profile)
        wrong_hash_sidecar = json.loads(json.dumps(exported["sidecar"]))
        wrong_hash_sidecar["asset_binding"]["content_hash"] = "sha256:not-the-png"
        wrong_hash_result = import_png_adam7_with_sidecar(
            exported["png_bytes"],
            wrong_hash_sidecar,
        )

        report = run_png_adam7_interlace_decoder_lab(
            VALID_PROFILE_PATHS,
            GENERATED_ROOT,
        )
        families = {
            family
            for result in report["invalid_probe_results"]
            for family in result["error_families"]
        }

        self.assertIn("png_adam7_interlace_required", families)
        self.assertIn("png_adam7_scanline_length_mismatch", families)
        self.assertIn("png_filter_type_unsupported", families)
        self.assertIn("png_adam7_pass_manifest_mismatch", families)
        self.assertIn("png_adam7_pixel_hash_mismatch", families)
        self.assertFalse(wrong_hash_result["ok"])
        self.assertIn("asset_hash_mismatch", wrong_hash_result["error_families"])

    def test_lab_report_closes_adam7_without_full_png_or_apng_claims(self):
        report = run_png_adam7_interlace_decoder_lab(
            VALID_PROFILE_PATHS,
            GENERATED_ROOT,
        )

        self.assertEqual("png_adam7_interlace_decoder_stage0", report["artifact_id"])
        self.assertEqual(3, report["profile_count"])
        self.assertEqual(3, report["png_roundtrip_success_count"])
        self.assertEqual(6, report["invalid_probe_rejected_count"])
        self.assertEqual(1.0, report["metrics"]["mean_semantic_fidelity"])
        self.assertEqual(1.0, report["metrics"]["mean_pixel_fidelity"])
        self.assertEqual(7.0, report["metrics"]["mean_non_empty_pass_count"])
        self.assertIn("png_adam7_interlace_decoder", report["closed_states"])
        self.assertIn("png_adam7_pass_manifest", report["closed_states"])
        self.assertIn("png_adam7_sidecar_semantic_restore", report["closed_states"])
        self.assertNotIn("png_adam7_interlace_decoder", report["blocked_states"])
        self.assertIn("apng_decoder", report["blocked_states"])
        self.assertIn("full_png_conformance", report["blocked_states"])
        self.assertIn("png_16bit_channel_decoder", report["blocked_states"])
        self.assertIn("png_color_type_4_grayscale_alpha_decoder", report["blocked_states"])
        self.assertIn("live_external_editor_rewrite_validation", report["blocked_states"])

    def test_write_artifacts_creates_adam7_pngs_sidecars_report_and_app_payload(self):
        report = run_png_adam7_interlace_decoder_lab(
            VALID_PROFILE_PATHS,
            GENERATED_ROOT,
        )

        with tempfile.TemporaryDirectory() as temp_dir:
            output_dir = Path(temp_dir)
            write_png_adam7_interlace_decoder_artifacts(output_dir, report)

            summary_path = output_dir / "png_adam7_interlace_decoder_stage0.json"
            self.assertTrue(summary_path.exists())
            persisted = json.loads(summary_path.read_text(encoding="utf-8"))
            self.assertEqual(report["metrics"], persisted["metrics"])
            self.assertTrue((output_dir / "slip_lcd_seed_adam7_rgba.png").exists())
            self.assertTrue((output_dir / "slip_lcd_seed_adam7_rgba_sidecar.json").exists())
            self.assertTrue((output_dir / "README.md").exists())
            app_data = (output_dir / "png_adam7_interlace_decoder_data.js").read_text(
                encoding="utf-8"
            )
            self.assertIn("MECHAGOTCHI_PNG_ADAM7_INTERLACE_DECODER", app_data)


if __name__ == "__main__":
    unittest.main()
