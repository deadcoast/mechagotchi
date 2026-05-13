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

from external_metadata_sidecar import (
    build_external_asset_stub,
    build_sidecar_for_grid,
    restore_grid_from_sidecar,
    run_external_metadata_sidecar_lab,
    validate_sidecar_binding,
    write_external_metadata_sidecar_artifacts,
)
from slip import is_grid_aligned
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


class ExternalMetadataSidecarTests(unittest.TestCase):
    def test_sidecar_records_asset_binding_semantic_overlay_and_slip_snapshot(self):
        profile = load_profile(VALID_PROFILE_PATHS[0])
        grid = first_grid_for(profile)
        asset = build_external_asset_stub(grid, "png")

        sidecar = build_sidecar_for_grid(grid, profile, asset)

        self.assertEqual("0.1.0", sidecar["sidecar_version"])
        self.assertEqual("png", sidecar["asset_binding"]["format_id"])
        self.assertEqual("sidecar_required", sidecar["asset_binding"]["semantic_policy"])
        self.assertEqual(grid["grid_size"], sidecar["grid_contract"]["grid_size"])
        self.assertEqual(len(grid["cells"]), sidecar["grid_contract"]["cell_count"])
        self.assertEqual(len(grid["cells"]), len(sidecar["semantic_overlay"]["cells"]))
        self.assertEqual(profile["profile_id"], sidecar["slip_binding"]["profile_id"])
        self.assertEqual(profile, sidecar["slip_binding"]["profile_snapshot"])
        self.assertEqual(64, len(sidecar["pixel_bindings"]))

    def test_sidecar_restore_preserves_valid_slip_aligned_semantics(self):
        profile = load_profile(VALID_PROFILE_PATHS[0])
        grid = first_grid_for(profile)
        asset = build_external_asset_stub(grid, "pixelorama_pxo")
        sidecar = build_sidecar_for_grid(grid, profile, asset)

        restored = restore_grid_from_sidecar(sidecar, asset)
        diff = compare_semantic_grid_fidelity(grid, restored)

        self.assertTrue(validate_grid(restored).ok, validate_grid(restored).errors)
        self.assertTrue(is_grid_aligned(restored, profile).ok)
        self.assertEqual([], diff["changed_cells"])
        self.assertEqual([], diff["missing_cells"])
        self.assertEqual([], diff["added_cells"])
        self.assertEqual("external_sidecar_restore", restored["metadata"]["source"])

    def test_sidecar_validation_rejects_asset_hash_and_dimension_mismatch(self):
        profile = load_profile(VALID_PROFILE_PATHS[0])
        grid = first_grid_for(profile)
        asset = build_external_asset_stub(grid, "spritesheet_png")
        sidecar = build_sidecar_for_grid(grid, profile, asset)
        wrong_hash_asset = {**asset, "content_hash": "sha256:not-the-bound-asset"}
        wrong_size_asset = {**asset, "width": asset["width"] + 1}

        hash_result = validate_sidecar_binding(sidecar, wrong_hash_asset)
        size_result = validate_sidecar_binding(sidecar, wrong_size_asset)

        self.assertFalse(hash_result["ok"])
        self.assertIn("asset_hash_mismatch", hash_result["error_families"])
        self.assertFalse(size_result["ok"])
        self.assertIn("asset_dimension_mismatch", size_result["error_families"])

    def test_lab_report_closes_sidecar_strategy_without_claiming_decoders(self):
        report = run_external_metadata_sidecar_lab(VALID_PROFILE_PATHS, GENERATED_ROOT)

        self.assertEqual("external_metadata_sidecar_stage0", report["artifact_id"])
        self.assertEqual(3, report["profile_count"])
        self.assertEqual(3, report["sidecar_roundtrip_success_count"])
        self.assertEqual(2, report["invalid_probe_rejected_count"])
        self.assertEqual(1.0, report["metrics"]["mean_semantic_fidelity"])
        self.assertIn("external_metadata_sidecar_strategy", report["closed_states"])
        self.assertNotIn("standard_image_decoder", report["blocked_states"])
        self.assertNotIn("spritesheet_decoder", report["blocked_states"])
        self.assertNotIn("png_variant_decoder_coverage", report["blocked_states"])
        self.assertIn("png_adam7_interlace_decoder", report["blocked_states"])
        self.assertIn("apng_decoder", report["blocked_states"])
        self.assertIn("full_png_conformance", report["blocked_states"])
        self.assertNotIn("spritesheet_variant_layout_coverage", report["blocked_states"])
        self.assertIn("spritesheet_packed_rotation_trim_decoder", report["blocked_states"])
        self.assertIn("runtime_animation_playback", report["blocked_states"])
        self.assertNotIn("third_party_project_decoder", report["blocked_states"])
        self.assertIn("full_project_format_coverage", report["blocked_states"])
        self.assertNotIn(
            "external_image_project_metadata_sidecar_strategy",
            report["blocked_states"],
        )

    def test_adapter_matrix_requires_sidecars_for_images_and_project_formats(self):
        report = run_external_metadata_sidecar_lab(VALID_PROFILE_PATHS, GENERATED_ROOT)
        formats = {item["format_id"]: item for item in report["adapter_matrix"]}

        self.assertEqual("sidecar_required", formats["png"]["semantic_policy"])
        self.assertEqual("sidecar_required", formats["spritesheet_png"]["semantic_policy"])
        self.assertEqual("sidecar_required", formats["piskel_project"]["semantic_policy"])
        self.assertEqual("sidecar_required", formats["pixelorama_pxo"]["semantic_policy"])
        self.assertEqual("sidecar_required", formats["libresprite_project"]["semantic_policy"])
        self.assertEqual("study_only_do_not_embed", formats["libresprite_project"]["code_reuse_policy"])

    def test_write_artifacts_creates_summary_sidecars_matrix_and_app_payload(self):
        report = run_external_metadata_sidecar_lab(VALID_PROFILE_PATHS, GENERATED_ROOT)

        with tempfile.TemporaryDirectory() as temp_dir:
            output_dir = Path(temp_dir)
            write_external_metadata_sidecar_artifacts(output_dir, report)

            summary_path = output_dir / "external_metadata_sidecar_stage0.json"
            self.assertTrue(summary_path.exists())
            persisted = json.loads(summary_path.read_text(encoding="utf-8"))
            self.assertEqual(report["metrics"], persisted["metrics"])
            self.assertTrue((output_dir / "slip_lcd_seed_external_sidecar.json").exists())
            self.assertTrue((output_dir / "adapter_matrix.json").exists())
            self.assertTrue((output_dir / "README.md").exists())
            app_data = (output_dir / "external_metadata_sidecar_data.js").read_text(
                encoding="utf-8"
            )
            self.assertIn("MECHAGOTCHI_EXTERNAL_METADATA_SIDECAR", app_data)


if __name__ == "__main__":
    unittest.main()
