import io
import json
import sys
import tempfile
import unittest
import zipfile
from pathlib import Path


WORKSHOP_DIR = Path(__file__).resolve().parent
GRID_GENOME_DIR = WORKSHOP_DIR.parents[0] / "grid_genome"
for import_path in [WORKSHOP_DIR, GRID_GENOME_DIR]:
    if str(import_path) not in sys.path:
        sys.path.insert(0, str(import_path))

from project_native_metadata_writer import (
    NATIVE_METADATA_KEY,
    PISKEL_DESCRIPTION_PREFIX,
    ProjectNativeMetadataError,
    extract_project_native_metadata,
    import_project_with_native_metadata,
    remove_project_native_metadata,
    run_project_native_metadata_writer_lab,
    write_project_native_metadata,
    write_project_native_metadata_writer_artifacts,
)
from third_party_project_decoder import (
    export_project_with_sidecar,
    decode_piskel_project,
    decode_pixelorama_pxo,
)
from validator import validate_grid


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


class ProjectNativeMetadataWriterTests(unittest.TestCase):
    def test_piskel_description_metadata_round_trips_without_external_sidecar(self):
        profile = load_profile(VALID_PROFILE_PATHS[0])
        grid = first_grid_for(profile)
        exported = export_project_with_sidecar(grid, profile, "piskel_project")

        embedded = write_project_native_metadata(
            exported["project_bytes"],
            "piskel_project",
            exported["sidecar"],
        )
        payload = json.loads(embedded["project_bytes"].decode("utf-8"))
        description = payload["piskel"]["description"]
        extracted = extract_project_native_metadata(
            embedded["project_bytes"],
            "piskel_project",
        )
        imported = import_project_with_native_metadata(
            embedded["project_bytes"],
            "piskel_project",
            source_grid=grid,
        )
        stripped = remove_project_native_metadata(
            embedded["project_bytes"],
            "piskel_project",
        )

        self.assertTrue(description.startswith(PISKEL_DESCRIPTION_PREFIX))
        self.assertEqual("piskel.description", extracted["metadata"]["native_location"])
        self.assertEqual(embedded["metadata"]["sidecar_hash"], extracted["metadata"]["sidecar_hash"])
        self.assertEqual(
            embedded["metadata"]["canonical_project_hash"],
            extracted["metadata"]["canonical_project_hash"],
        )
        self.assertEqual(stripped["content_hash"], extracted["metadata"]["canonical_project_hash"])
        self.assertEqual(grid["grid_size"], decode_piskel_project(embedded["project_bytes"])["dimensions"])
        self.assertTrue(imported["ok"], imported["errors"])
        self.assertTrue(validate_grid(imported["restored_grid"]).ok)
        self.assertEqual(1.0, imported["semantic_fidelity"])
        self.assertEqual("project_native_metadata", imported["project_policy"]["semantic_policy"])

    def test_pixelorama_data_json_metadata_round_trips_without_external_sidecar(self):
        profile = load_profile(VALID_PROFILE_PATHS[1])
        grid = first_grid_for(profile)
        exported = export_project_with_sidecar(grid, profile, "pixelorama_pxo")

        embedded = write_project_native_metadata(
            exported["project_bytes"],
            "pixelorama_pxo",
            exported["sidecar"],
        )
        with zipfile.ZipFile(io.BytesIO(embedded["project_bytes"]), "r") as archive:
            members = sorted(archive.namelist())
            data = json.loads(archive.read("data.json").decode("utf-8"))
        extracted = extract_project_native_metadata(
            embedded["project_bytes"],
            "pixelorama_pxo",
        )
        imported = import_project_with_native_metadata(
            embedded["project_bytes"],
            "pixelorama_pxo",
            source_grid=grid,
        )

        self.assertIn("data.json", members)
        self.assertIn("image_data/frames/0/cel_0.png", members)
        self.assertIn(NATIVE_METADATA_KEY, data)
        self.assertEqual("data.json.mechagotchi_native_metadata", extracted["metadata"]["native_location"])
        self.assertEqual(grid["grid_size"], decode_pixelorama_pxo(embedded["project_bytes"])["dimensions"])
        self.assertTrue(imported["ok"], imported["errors"])
        self.assertTrue(validate_grid(imported["restored_grid"]).ok)
        self.assertEqual(1.0, imported["semantic_fidelity"])
        self.assertEqual("project_native_metadata", imported["project_policy"]["semantic_policy"])

    def test_import_rejects_missing_tampered_and_unsupported_native_metadata(self):
        profile = load_profile(VALID_PROFILE_PATHS[0])
        grid = first_grid_for(profile)
        exported = export_project_with_sidecar(grid, profile, "piskel_project")
        embedded = write_project_native_metadata(
            exported["project_bytes"],
            "piskel_project",
            exported["sidecar"],
        )

        missing = import_project_with_native_metadata(
            exported["project_bytes"],
            "piskel_project",
            source_grid=grid,
        )
        sidecar_tampered_payload = json.loads(embedded["project_bytes"].decode("utf-8"))
        metadata = json.loads(
            sidecar_tampered_payload["piskel"]["description"][len(PISKEL_DESCRIPTION_PREFIX) :]
        )
        metadata["sidecar"]["asset_binding"]["content_hash"] = "sha256:tampered"
        sidecar_tampered_payload["piskel"]["description"] = (
            PISKEL_DESCRIPTION_PREFIX + json.dumps(metadata, sort_keys=True, separators=(",", ":"))
        )
        sidecar_tampered = import_project_with_native_metadata(
            json.dumps(sidecar_tampered_payload, sort_keys=True, separators=(",", ":")).encode("utf-8"),
            "piskel_project",
            source_grid=grid,
        )
        project_tampered_payload = json.loads(embedded["project_bytes"].decode("utf-8"))
        project_tampered_payload["piskel"]["name"] = "edited-after-metadata"
        project_tampered = import_project_with_native_metadata(
            json.dumps(project_tampered_payload, sort_keys=True, separators=(",", ":")).encode("utf-8"),
            "piskel_project",
            source_grid=grid,
        )
        aseprite_exported = export_project_with_sidecar(grid, profile, "libresprite_project")

        self.assertFalse(missing["ok"])
        self.assertIn("project_native_metadata_missing", missing["error_families"])
        self.assertFalse(sidecar_tampered["ok"])
        self.assertIn("project_native_sidecar_hash_mismatch", sidecar_tampered["error_families"])
        self.assertFalse(project_tampered["ok"])
        self.assertIn("project_native_canonical_hash_mismatch", project_tampered["error_families"])
        with self.assertRaises(ProjectNativeMetadataError):
            write_project_native_metadata(
                aseprite_exported["project_bytes"],
                "libresprite_project",
                aseprite_exported["sidecar"],
            )

    def test_lab_report_closes_supported_native_metadata_subset_only(self):
        report = run_project_native_metadata_writer_lab(
            VALID_PROFILE_PATHS,
            GENERATED_ROOT,
        )

        self.assertEqual("project_native_metadata_writer_stage0", report["artifact_id"])
        self.assertEqual(3, report["profile_count"])
        self.assertEqual(2, report["native_writer_format_count"])
        self.assertEqual(6, report["native_metadata_roundtrip_count"])
        self.assertEqual(6, report["native_metadata_roundtrip_success_count"])
        self.assertEqual(1, report["unsupported_native_writer_policy_count"])
        self.assertEqual(4, report["invalid_probe_rejected_count"])
        self.assertEqual(1.0, report["metrics"]["native_metadata_roundtrip_success_rate"])
        self.assertEqual(1.0, report["metrics"]["mean_semantic_fidelity"])
        self.assertIn("project_file_native_metadata_writer_policy", report["closed_states"])
        self.assertIn("piskel_description_native_metadata_writer", report["closed_states"])
        self.assertIn("pixelorama_data_json_native_metadata_writer", report["closed_states"])
        self.assertNotIn("project_file_native_metadata_writer", report["blocked_states"])
        self.assertNotIn("aseprite_libresprite_user_data_chunk_writer", report["blocked_states"])
        self.assertIn("live_external_editor_rewrite_validation", report["blocked_states"])
        self.assertIn("full_project_format_coverage", report["blocked_states"])
        self.assertIn("package_runtime_lifecycle_integration", report["blocked_states"])

    def test_write_artifacts_creates_embedded_projects_sidecars_report_and_app_payload(self):
        report = run_project_native_metadata_writer_lab(
            VALID_PROFILE_PATHS,
            GENERATED_ROOT,
        )

        with tempfile.TemporaryDirectory() as temp_dir:
            output_dir = Path(temp_dir)
            write_project_native_metadata_writer_artifacts(output_dir, report)

            summary_path = output_dir / "project_native_metadata_writer_stage0.json"
            self.assertTrue(summary_path.exists())
            persisted = json.loads(summary_path.read_text(encoding="utf-8"))
            self.assertEqual(report["metrics"], persisted["metrics"])
            self.assertTrue((output_dir / "slip_lcd_seed_native_metadata.piskel").exists())
            self.assertTrue((output_dir / "slip_lcd_seed_native_metadata.pxo").exists())
            self.assertTrue((output_dir / "slip_lcd_seed_piskel_native_sidecar.json").exists())
            self.assertTrue((output_dir / "README.md").exists())
            app_data = (output_dir / "project_native_metadata_writer_data.js").read_text(
                encoding="utf-8"
            )
            self.assertIn("MECHAGOTCHI_PROJECT_NATIVE_METADATA_WRITER", app_data)


if __name__ == "__main__":
    unittest.main()
