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

from png_private_chunk_policy import (
    PRIVATE_METADATA_CHUNK_TYPE,
    PRIVATE_METADATA_MAGIC,
    corrupt_png_private_chunk_json,
    duplicate_png_private_chunk,
    export_png_private_chunk_bundle,
    import_png_private_chunk,
    remove_png_private_chunks,
    run_png_private_chunk_policy_lab,
    tamper_png_private_chunk_canonical_hash,
    tamper_png_private_chunk_magic,
    tamper_png_private_chunk_safe_to_copy_type,
    tamper_png_private_chunk_sidecar_hash,
    write_png_private_chunk_policy_artifacts,
)
from slip import is_grid_aligned
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


class PNGPrivateChunkPolicyTests(unittest.TestCase):
    def test_export_writes_ancillary_private_unsafe_chunk_without_changing_pixels(self):
        profile = load_profile(VALID_PROFILE_PATHS[0])
        grid = first_grid_for(profile)

        bundle = export_png_private_chunk_bundle(grid, profile)
        decoded = decode_png_rgba(bundle["png_bytes"])
        canonical_decoded = decode_png_rgba(bundle["canonical_png_bytes"])

        self.assertEqual(PRIVATE_METADATA_CHUNK_TYPE, bundle["metadata"]["chunk_type"])
        self.assertEqual(PRIVATE_METADATA_MAGIC, bundle["metadata"]["magic"])
        self.assertIn(PRIVATE_METADATA_CHUNK_TYPE, decoded["chunks"])
        self.assertEqual(canonical_decoded["pixels"], decoded["pixels"])
        self.assertTrue(bundle["metadata"]["chunk_type_properties"]["ancillary"])
        self.assertTrue(bundle["metadata"]["chunk_type_properties"]["private"])
        self.assertTrue(bundle["metadata"]["chunk_type_properties"]["reserved_bit_valid"])
        self.assertFalse(bundle["metadata"]["chunk_type_properties"]["safe_to_copy"])
        self.assertEqual(
            "ancillary_private_unsafe_to_copy_with_magic_prefix",
            bundle["metadata"]["private_chunk_policy"],
        )

    def test_import_restores_valid_grid_from_private_chunk_metadata(self):
        profile = load_profile(VALID_PROFILE_PATHS[0])
        grid = first_grid_for(profile)
        bundle = export_png_private_chunk_bundle(grid, profile)

        imported = import_png_private_chunk(bundle["png_bytes"], source_grid=grid)
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
        self.assertEqual(PRIVATE_METADATA_CHUNK_TYPE, imported["private_chunk_policy"]["chunk_type"])
        self.assertFalse(imported["private_chunk_policy"]["safe_to_copy"])
        self.assertFalse(imported["private_chunk_policy"]["live_external_editor_verified"])

    def test_import_rejects_invalid_private_chunk_policy_cases(self):
        profile = load_profile(VALID_PROFILE_PATHS[0])
        grid = first_grid_for(profile)
        bundle = export_png_private_chunk_bundle(grid, profile)

        probes = [
            (remove_png_private_chunks(bundle["png_bytes"]), "png_private_chunk_missing"),
            (duplicate_png_private_chunk(bundle["png_bytes"]), "png_private_chunk_duplicate"),
            (
                tamper_png_private_chunk_safe_to_copy_type(bundle["png_bytes"]),
                "png_private_chunk_type_policy_violation",
            ),
            (
                tamper_png_private_chunk_magic(bundle["png_bytes"]),
                "png_private_chunk_magic_mismatch",
            ),
            (corrupt_png_private_chunk_json(bundle["png_bytes"]), "png_private_chunk_json_invalid"),
            (
                tamper_png_private_chunk_canonical_hash(bundle["png_bytes"]),
                "png_private_chunk_canonical_hash_mismatch",
            ),
            (
                tamper_png_private_chunk_sidecar_hash(bundle["png_bytes"]),
                "png_private_chunk_sidecar_hash_mismatch",
            ),
        ]

        for png_bytes, family in probes:
            imported = import_png_private_chunk(png_bytes, source_grid=grid)
            self.assertFalse(imported["ok"])
            self.assertIn(family, imported["error_families"])
            self.assertNotIn("restored_grid", imported)

    def test_lab_report_closes_private_chunk_subset_only(self):
        report = run_png_private_chunk_policy_lab(
            VALID_PROFILE_PATHS,
            GENERATED_ROOT,
        )

        self.assertEqual("png_private_chunk_policy_stage0", report["artifact_id"])
        self.assertEqual(3, report["profile_count"])
        self.assertEqual(3, report["private_chunk_roundtrip_count"])
        self.assertEqual(3, report["private_chunk_roundtrip_success_count"])
        self.assertEqual(7, report["invalid_probe_rejected_count"])
        self.assertEqual(1.0, report["metrics"]["private_chunk_roundtrip_success_rate"])
        self.assertEqual(1.0, report["metrics"]["mean_semantic_fidelity"])
        self.assertEqual(1.0, report["metrics"]["mean_pixel_fidelity"])
        self.assertIn("png_private_chunk_type_bits_policy", report["closed_states"])
        self.assertIn("png_private_chunk_magic_prefix_policy", report["closed_states"])
        self.assertIn("png_private_chunk_hash_validation", report["closed_states"])
        self.assertIn("production_import_export_carrier_selection_final_decision", report["blocked_states"])
        self.assertIn("live_external_editor_rewrite_validation", report["blocked_states"])
        self.assertIn("Adam7/APNG/full PNG conformance", report["blocked_states"])
        self.assertIn("package_runtime_lifecycle_integration", report["blocked_states"])
        self.assertEqual("textual_or_external_sidecar_preferred_until_editor_fixtures", report["carrier_selection_inputs"]["provisional_recommendation"])

    def test_write_artifacts_creates_private_chunk_pngs_report_and_app_payload(self):
        report = run_png_private_chunk_policy_lab(
            VALID_PROFILE_PATHS,
            GENERATED_ROOT,
        )

        with tempfile.TemporaryDirectory() as temp_dir:
            output_dir = Path(temp_dir)
            write_png_private_chunk_policy_artifacts(output_dir, report)

            summary_path = output_dir / "png_private_chunk_policy_stage0.json"
            self.assertTrue(summary_path.exists())
            persisted = json.loads(summary_path.read_text(encoding="utf-8"))
            self.assertEqual(report["metrics"], persisted["metrics"])
            self.assertTrue((output_dir / "slip_lcd_seed_private_chunk.png").exists())
            self.assertTrue((output_dir / "slip_gray_stable_private_chunk.png").exists())
            self.assertTrue((output_dir / "slip_amber_social_private_chunk.png").exists())
            self.assertTrue((output_dir / "README.md").exists())
            app_data = (output_dir / "png_private_chunk_policy_data.js").read_text(
                encoding="utf-8"
            )
            self.assertIn("MECHAGOTCHI_PNG_PRIVATE_CHUNK_POLICY", app_data)


if __name__ == "__main__":
    unittest.main()
