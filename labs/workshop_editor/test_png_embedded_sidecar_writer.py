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

from png_embedded_sidecar_writer import (
    EMBEDDED_SIDECAR_KEYWORD,
    corrupt_embedded_sidecar_json_for_probe,
    corrupt_embedded_sidecar_hash_for_probe,
    export_png_with_embedded_sidecar,
    extract_embedded_sidecar_from_png,
    import_png_with_embedded_sidecar,
    remove_embedded_sidecar_chunks,
    run_png_embedded_sidecar_writer_lab,
    write_png_embedded_sidecar_writer_artifacts,
)
from slip import is_grid_aligned
from standard_image_sidecar_decoder import decode_png_rgba
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


class PNGEmbeddedSidecarWriterTests(unittest.TestCase):
    def test_embeds_sidecar_text_chunk_without_changing_decoded_pixels(self):
        profile = load_profile(VALID_PROFILE_PATHS[0])
        grid = first_grid_for(profile)

        exported = export_png_with_embedded_sidecar(grid, profile)
        extracted = extract_embedded_sidecar_from_png(exported["embedded_png_bytes"])
        embedded_decoded = decode_png_rgba(exported["embedded_png_bytes"])
        canonical_decoded = decode_png_rgba(exported["canonical_png_bytes"])

        self.assertEqual(EMBEDDED_SIDECAR_KEYWORD, extracted["keyword"])
        self.assertIn("tEXt", embedded_decoded["chunks"])
        self.assertNotEqual(exported["embedded_asset"]["content_hash"], exported["canonical_asset"]["content_hash"])
        self.assertEqual(canonical_decoded["pixels"], embedded_decoded["pixels"])
        self.assertEqual(exported["sidecar"], extracted["sidecar"])
        self.assertEqual(exported["canonical_asset"]["content_hash"], extracted["metadata"]["canonical_png_hash"])

    def test_import_embedded_sidecar_restores_valid_slip_aligned_grid(self):
        profile = load_profile(VALID_PROFILE_PATHS[0])
        grid = first_grid_for(profile)
        exported = export_png_with_embedded_sidecar(grid, profile)

        imported = import_png_with_embedded_sidecar(
            exported["embedded_png_bytes"],
            source_grid=grid,
        )
        restored = imported["restored_grid"]
        diff = compare_semantic_grid_fidelity(grid, restored)

        self.assertTrue(imported["ok"], imported["errors"])
        self.assertTrue(validate_grid(restored).ok, validate_grid(restored).errors)
        self.assertTrue(is_grid_aligned(restored, profile).ok)
        self.assertTrue(imported["embedded_metadata"]["ok"])
        self.assertEqual(1.0, imported["semantic_fidelity"])
        self.assertEqual(1.0, imported["pixel_fidelity"])
        self.assertEqual([], diff["changed_cells"])
        self.assertEqual([], diff["missing_cells"])
        self.assertEqual([], diff["added_cells"])

    def test_import_rejects_missing_corrupt_json_and_hash_mismatch(self):
        report = run_png_embedded_sidecar_writer_lab(
            VALID_PROFILE_PATHS,
            GENERATED_ROOT,
        )
        families = {
            family
            for result in report["invalid_probe_results"]
            for family in result["error_families"]
        }

        self.assertIn("embedded_sidecar_chunk_missing", families)
        self.assertIn("embedded_sidecar_json_invalid", families)
        self.assertIn("embedded_sidecar_canonical_hash_mismatch", families)

    def test_probe_helpers_create_specific_invalid_embedded_pngs(self):
        profile = load_profile(VALID_PROFILE_PATHS[0])
        grid = first_grid_for(profile)
        exported = export_png_with_embedded_sidecar(grid, profile)

        missing = import_png_with_embedded_sidecar(
            remove_embedded_sidecar_chunks(exported["embedded_png_bytes"])
        )
        corrupt_json = import_png_with_embedded_sidecar(
            corrupt_embedded_sidecar_json_for_probe(exported["embedded_png_bytes"])
        )
        corrupt_hash = import_png_with_embedded_sidecar(
            corrupt_embedded_sidecar_hash_for_probe(exported["embedded_png_bytes"])
        )

        self.assertIn("embedded_sidecar_chunk_missing", missing["error_families"])
        self.assertIn("embedded_sidecar_json_invalid", corrupt_json["error_families"])
        self.assertIn("embedded_sidecar_canonical_hash_mismatch", corrupt_hash["error_families"])

    def test_lab_report_closes_embedded_png_metadata_writer_only_for_text_chunk_subset(self):
        report = run_png_embedded_sidecar_writer_lab(
            VALID_PROFILE_PATHS,
            GENERATED_ROOT,
        )

        self.assertEqual("png_embedded_sidecar_writer_stage0", report["artifact_id"])
        self.assertEqual(3, report["profile_count"])
        self.assertEqual(3, report["embedded_roundtrip_success_count"])
        self.assertEqual(3, report["invalid_probe_rejected_count"])
        self.assertEqual(1.0, report["metrics"]["mean_semantic_fidelity"])
        self.assertEqual(1.0, report["metrics"]["mean_pixel_fidelity"])
        self.assertIn("embedded_png_metadata_writer_text_chunk", report["closed_states"])
        self.assertNotIn("embedded PNG metadata writer", report["blocked_states"])
        self.assertIn("Adam7/APNG/full PNG conformance", report["blocked_states"])
        self.assertIn("arbitrary Aseprite project schema coverage", report["blocked_states"])
        self.assertIn("live external editor rewrite validation", report["blocked_states"])
        self.assertIn("full project-format coverage", report["blocked_states"])
        self.assertIn("package runtime lifecycle integration", report["blocked_states"])
        self.assertIn("profile-weighted evolution", report["blocked_states"])

    def test_write_artifacts_creates_embedded_pngs_sidecars_report_and_app_payload(self):
        report = run_png_embedded_sidecar_writer_lab(
            VALID_PROFILE_PATHS,
            GENERATED_ROOT,
        )

        with tempfile.TemporaryDirectory() as temp_dir:
            output_dir = Path(temp_dir)
            write_png_embedded_sidecar_writer_artifacts(output_dir, report)

            summary_path = output_dir / "png_embedded_sidecar_writer_stage0.json"
            self.assertTrue(summary_path.exists())
            persisted = json.loads(summary_path.read_text(encoding="utf-8"))
            self.assertEqual(report["metrics"], persisted["metrics"])
            self.assertTrue((output_dir / "slip_lcd_seed_embedded_sidecar.png").exists())
            self.assertTrue((output_dir / "slip_lcd_seed_embedded_sidecar.json").exists())
            self.assertTrue((output_dir / "README.md").exists())
            app_data = (output_dir / "png_embedded_sidecar_writer_data.js").read_text(
                encoding="utf-8"
            )
            self.assertIn("MECHAGOTCHI_PNG_EMBEDDED_SIDECAR_WRITER", app_data)


if __name__ == "__main__":
    unittest.main()
