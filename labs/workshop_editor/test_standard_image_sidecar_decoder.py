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

from slip import is_grid_aligned
from standard_image_sidecar_decoder import (
    PNG_SIGNATURE,
    decode_png_rgba,
    export_standard_png_with_sidecar,
    import_standard_png_with_sidecar,
    render_grid_rgba_pixels,
    run_standard_image_sidecar_decoder_lab,
    write_standard_image_sidecar_decoder_artifacts,
)
from validator import validate_grid
from workshop_editor import compare_semantic_grid_fidelity


VALID_PROFILE_PATHS = [
    Path("data/slips/valid/slip_lcd_seed.json"),
    Path("data/slips/valid/slip_gray_stable.json"),
    Path("data/slips/valid/slip_amber_social.json"),
]
GENERATED_ROOT = Path("data/slips/multi_profile_generation_stage0")


def load_profile(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def first_grid_for(profile: dict) -> dict:
    grid_path = sorted((GENERATED_ROOT / profile["profile_id"]).glob("*.json"))[0]
    return json.loads(grid_path.read_text(encoding="utf-8"))


class StandardImageSidecarDecoderTests(unittest.TestCase):
    def test_export_writes_real_static_rgba_png_bound_to_sidecar(self):
        profile = load_profile(VALID_PROFILE_PATHS[0])
        grid = first_grid_for(profile)

        exported = export_standard_png_with_sidecar(grid, profile)
        decoded = decode_png_rgba(exported["png_bytes"])

        self.assertTrue(exported["png_bytes"].startswith(PNG_SIGNATURE))
        self.assertEqual("png", exported["asset"]["format_id"])
        self.assertEqual("image/png", exported["asset"]["media_type"])
        self.assertEqual(grid["grid_size"][0], decoded["width"])
        self.assertEqual(grid["grid_size"][1], decoded["height"])
        self.assertEqual(render_grid_rgba_pixels(grid), decoded["pixels"])
        self.assertEqual(
            exported["asset"]["content_hash"],
            exported["sidecar"]["asset_binding"]["content_hash"],
        )

    def test_import_png_with_sidecar_restores_valid_slip_aligned_grid(self):
        profile = load_profile(VALID_PROFILE_PATHS[0])
        grid = first_grid_for(profile)
        exported = export_standard_png_with_sidecar(grid, profile)

        imported = import_standard_png_with_sidecar(
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

    def test_import_rejects_corrupt_png_and_sidecar_hash_mismatch(self):
        profile = load_profile(VALID_PROFILE_PATHS[0])
        grid = first_grid_for(profile)
        exported = export_standard_png_with_sidecar(grid, profile)
        corrupt_png = b"not-a-png" + exported["png_bytes"][8:]
        wrong_hash_sidecar = json.loads(json.dumps(exported["sidecar"]))
        wrong_hash_sidecar["asset_binding"]["content_hash"] = "sha256:not-the-png"

        corrupt_result = import_standard_png_with_sidecar(
            corrupt_png,
            exported["sidecar"],
        )
        wrong_hash_result = import_standard_png_with_sidecar(
            exported["png_bytes"],
            wrong_hash_sidecar,
        )

        self.assertFalse(corrupt_result["ok"])
        self.assertIn("png_signature_invalid", corrupt_result["error_families"])
        self.assertFalse(wrong_hash_result["ok"])
        self.assertIn("asset_hash_mismatch", wrong_hash_result["error_families"])

    def test_lab_report_closes_static_rgba_png_decoder_only(self):
        report = run_standard_image_sidecar_decoder_lab(
            VALID_PROFILE_PATHS,
            GENERATED_ROOT,
        )

        self.assertEqual("standard_image_sidecar_decoder_stage0", report["artifact_id"])
        self.assertEqual(3, report["profile_count"])
        self.assertEqual(3, report["png_roundtrip_success_count"])
        self.assertEqual(2, report["invalid_probe_rejected_count"])
        self.assertEqual(1.0, report["metrics"]["mean_semantic_fidelity"])
        self.assertIn("standard_image_static_rgba_png_decoder", report["closed_states"])
        self.assertNotIn("standard_image_decoder", report["blocked_states"])
        self.assertNotIn("png_variant_decoder_coverage", report["blocked_states"])
        self.assertIn("png_adam7_interlace_decoder", report["blocked_states"])
        self.assertIn("apng_decoder", report["blocked_states"])
        self.assertIn("full_png_conformance", report["blocked_states"])
        self.assertNotIn("spritesheet_decoder", report["blocked_states"])
        self.assertIn("spritesheet_variant_layout_coverage", report["blocked_states"])
        self.assertNotIn("third_party_project_decoder", report["blocked_states"])
        self.assertIn("full_project_format_coverage", report["blocked_states"])

    def test_write_artifacts_creates_pngs_sidecars_report_and_app_payload(self):
        report = run_standard_image_sidecar_decoder_lab(
            VALID_PROFILE_PATHS,
            GENERATED_ROOT,
        )

        with tempfile.TemporaryDirectory() as temp_dir:
            output_dir = Path(temp_dir)
            write_standard_image_sidecar_decoder_artifacts(output_dir, report)

            summary_path = output_dir / "standard_image_sidecar_decoder_stage0.json"
            self.assertTrue(summary_path.exists())
            persisted = json.loads(summary_path.read_text(encoding="utf-8"))
            self.assertEqual(report["metrics"], persisted["metrics"])
            self.assertTrue((output_dir / "slip_lcd_seed_standard_image.png").exists())
            self.assertTrue((output_dir / "slip_lcd_seed_standard_image_sidecar.json").exists())
            self.assertTrue((output_dir / "README.md").exists())
            app_data = (output_dir / "standard_image_sidecar_decoder_data.js").read_text(
                encoding="utf-8"
            )
            self.assertIn("MECHAGOTCHI_STANDARD_IMAGE_SIDECAR_DECODER", app_data)


if __name__ == "__main__":
    unittest.main()
