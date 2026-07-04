import io
import json
import sys
import tempfile
import unittest
import zipfile
from copy import deepcopy
from pathlib import Path


WORKSHOP_DIR = Path(__file__).resolve().parent
GRID_GENOME_DIR = WORKSHOP_DIR.parents[0] / "grid_genome"
for import_path in [WORKSHOP_DIR, GRID_GENOME_DIR]:
    if str(import_path) not in sys.path:
        sys.path.insert(0, str(import_path))

from project_editor_rewrite_preservation import (
    import_project_after_editor_rewrite,
    run_project_editor_rewrite_preservation_lab,
    simulate_editor_rewrite,
    tamper_project_visual_payload,
    write_project_editor_rewrite_preservation_artifacts,
)
from project_native_metadata_writer import (
    ProjectNativeMetadataError,
    extract_project_native_metadata,
    project_visual_hash,
    remove_project_native_metadata,
    write_project_native_metadata,
)
from third_party_project_decoder import PXO_MEMBER_SIZE_CAP, export_project_with_sidecar


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


class ProjectEditorRewritePreservationTests(unittest.TestCase):
    def test_piskel_editor_rewrite_changes_project_hash_but_preserves_metadata_and_visual_hash(self):
        profile = load_profile(VALID_PROFILE_PATHS[0])
        grid = first_grid_for(profile)
        exported = export_project_with_sidecar(grid, profile, "piskel_project")
        embedded = write_project_native_metadata(
            exported["project_bytes"],
            "piskel_project",
            exported["sidecar"],
        )
        rewritten = simulate_editor_rewrite(
            embedded["project_bytes"],
            "piskel_project",
            editor_id="piskel_save_v1",
        )
        rewritten_metadata = extract_project_native_metadata(
            rewritten["project_bytes"],
            "piskel_project",
            allow_rewrite=True,
        )
        imported = import_project_after_editor_rewrite(
            rewritten["project_bytes"],
            "piskel_project",
            source_grid=grid,
        )

        self.assertNotEqual(
            embedded["canonical_project_hash"],
            remove_project_native_metadata(rewritten["project_bytes"], "piskel_project")["content_hash"],
        )
        self.assertEqual(
            embedded["metadata"]["project_visual_hash"],
            project_visual_hash(rewritten["project_bytes"], "piskel_project"),
        )
        self.assertTrue(rewritten_metadata["rewrite_detected"])
        self.assertTrue(imported["ok"], imported["errors"])
        self.assertTrue(imported["rewrite_detected"])
        self.assertEqual(1.0, imported["semantic_fidelity"])
        self.assertEqual("project_editor_rewrite_rebound", imported["project_policy"]["semantic_policy"])

    def test_pixelorama_editor_rewrite_changes_data_json_but_preserves_image_payload_and_imports(self):
        profile = load_profile(VALID_PROFILE_PATHS[1])
        grid = first_grid_for(profile)
        exported = export_project_with_sidecar(grid, profile, "pixelorama_pxo")
        embedded = write_project_native_metadata(
            exported["project_bytes"],
            "pixelorama_pxo",
            exported["sidecar"],
        )
        rewritten = simulate_editor_rewrite(
            embedded["project_bytes"],
            "pixelorama_pxo",
            editor_id="pixelorama_save_v1",
        )
        imported = import_project_after_editor_rewrite(
            rewritten["project_bytes"],
            "pixelorama_pxo",
            source_grid=grid,
        )

        self.assertNotEqual(
            embedded["canonical_project_hash"],
            remove_project_native_metadata(rewritten["project_bytes"], "pixelorama_pxo")["content_hash"],
        )
        self.assertEqual(
            embedded["metadata"]["project_visual_hash"],
            project_visual_hash(rewritten["project_bytes"], "pixelorama_pxo"),
        )
        self.assertTrue(imported["ok"], imported["errors"])
        self.assertTrue(imported["rewrite_detected"])
        self.assertEqual(1.0, imported["semantic_fidelity"])
        self.assertEqual("project_editor_rewrite_rebound", imported["project_policy"]["semantic_policy"])

    def test_rewrite_import_rejects_missing_metadata_tampered_sidecar_and_visual_payload_change(self):
        profile = load_profile(VALID_PROFILE_PATHS[0])
        grid = first_grid_for(profile)
        exported = export_project_with_sidecar(grid, profile, "piskel_project")
        embedded = write_project_native_metadata(
            exported["project_bytes"],
            "piskel_project",
            exported["sidecar"],
        )
        rewritten = simulate_editor_rewrite(
            embedded["project_bytes"],
            "piskel_project",
            editor_id="piskel_save_v1",
        )
        missing_metadata = remove_project_native_metadata(
            rewritten["project_bytes"],
            "piskel_project",
        )["project_bytes"]
        tampered_project = json.loads(rewritten["project_bytes"].decode("utf-8"))
        metadata = extract_project_native_metadata(
            rewritten["project_bytes"],
            "piskel_project",
            allow_rewrite=True,
        )["metadata"]
        metadata = deepcopy(metadata)
        metadata["sidecar"]["asset_binding"]["width"] = 99
        tampered_project["piskel"]["description"] = (
            "MECHAGOTCHI_NATIVE_METADATA_V1:"
            + json.dumps(metadata, sort_keys=True, separators=(",", ":"))
        )
        visual_tampered = tamper_project_visual_payload(
            rewritten["project_bytes"],
            "piskel_project",
        )

        missing = import_project_after_editor_rewrite(
            missing_metadata,
            "piskel_project",
            source_grid=grid,
        )
        sidecar_tampered = import_project_after_editor_rewrite(
            json.dumps(tampered_project, sort_keys=True, separators=(",", ":")).encode("utf-8"),
            "piskel_project",
            source_grid=grid,
        )
        visual_changed = import_project_after_editor_rewrite(
            visual_tampered,
            "piskel_project",
            source_grid=grid,
        )

        self.assertFalse(missing["ok"])
        self.assertIn("project_native_metadata_missing", missing["error_families"])
        self.assertFalse(sidecar_tampered["ok"])
        self.assertIn("project_native_sidecar_hash_mismatch", sidecar_tampered["error_families"])
        self.assertFalse(visual_changed["ok"])
        self.assertIn("project_native_visual_hash_mismatch", visual_changed["error_families"])

    def test_rewrite_simulation_rejects_oversized_pxo_member(self):
        buffer = io.BytesIO()
        with zipfile.ZipFile(buffer, "w", compression=zipfile.ZIP_DEFLATED) as archive:
            archive.writestr("data.json", json.dumps({"name": "member_probe"}))
            archive.writestr(
                "image_data/frames/0/cel_0.png",
                b"\x00" * (PXO_MEMBER_SIZE_CAP + 1),
            )

        with self.assertRaises(ProjectNativeMetadataError) as oversized:
            simulate_editor_rewrite(
                buffer.getvalue(),
                "pixelorama_pxo",
                editor_id="member_probe_editor",
            )

        self.assertEqual("pxo_member_too_large", oversized.exception.family)

    def test_lab_report_closes_simulated_rewrite_subset_only(self):
        report = run_project_editor_rewrite_preservation_lab(
            VALID_PROFILE_PATHS,
            GENERATED_ROOT,
        )

        self.assertEqual("project_editor_rewrite_preservation_stage0", report["artifact_id"])
        self.assertEqual(3, report["profile_count"])
        self.assertEqual(2, report["simulated_editor_format_count"])
        self.assertEqual(6, report["rewrite_roundtrip_count"])
        self.assertEqual(6, report["rewrite_roundtrip_success_count"])
        self.assertEqual(3, report["invalid_probe_rejected_count"])
        self.assertEqual(1.0, report["metrics"]["rewrite_roundtrip_success_rate"])
        self.assertEqual(1.0, report["metrics"]["mean_semantic_fidelity"])
        self.assertEqual(1.0, report["metrics"]["visual_hash_preservation_rate"])
        self.assertIn("project_editor_rewrite_preservation_simulated", report["closed_states"])
        self.assertIn("piskel_description_rewrite_preservation_simulated", report["closed_states"])
        self.assertIn("pixelorama_data_json_rewrite_preservation_simulated", report["closed_states"])
        self.assertIn("live_external_editor_rewrite_validation", report["blocked_states"])
        self.assertIn("arbitrary_aseprite_project_schema_coverage", report["blocked_states"])
        self.assertIn("full_project_format_coverage", report["blocked_states"])
        self.assertIn("package_runtime_lifecycle_integration", report["blocked_states"])

    def test_write_artifacts_creates_rewritten_projects_report_and_app_payload(self):
        report = run_project_editor_rewrite_preservation_lab(
            VALID_PROFILE_PATHS,
            GENERATED_ROOT,
        )

        with tempfile.TemporaryDirectory() as temp_dir:
            output_dir = Path(temp_dir)
            write_project_editor_rewrite_preservation_artifacts(output_dir, report)

            summary_path = output_dir / "project_editor_rewrite_preservation_stage0.json"
            self.assertTrue(summary_path.exists())
            persisted = json.loads(summary_path.read_text(encoding="utf-8"))
            self.assertEqual(report["metrics"], persisted["metrics"])
            self.assertTrue((output_dir / "slip_lcd_seed_piskel_rewritten.piskel").exists())
            self.assertTrue((output_dir / "slip_lcd_seed_pixelorama_rewritten.pxo").exists())
            self.assertTrue((output_dir / "README.md").exists())
            app_data = (output_dir / "project_editor_rewrite_preservation_data.js").read_text(
                encoding="utf-8"
            )
            self.assertIn("MECHAGOTCHI_PROJECT_EDITOR_REWRITE_PRESERVATION", app_data)


if __name__ == "__main__":
    unittest.main()
