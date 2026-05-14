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
from spritesheet_multi_page_atlas import (
    MULTI_PAGE_ATLAS_POLICY,
    export_multi_page_atlas_bundle,
    import_multi_page_atlas_bundle,
    run_spritesheet_multi_page_atlas_lab,
    write_spritesheet_multi_page_atlas_artifacts,
)
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


class SpritesheetMultiPageAtlasTests(unittest.TestCase):
    def test_exports_multiple_pages_with_page_manifest_and_frame_page_bindings(self):
        profile = load_profile(VALID_PROFILE_PATHS[0])
        grid = first_grid_for(profile)

        exported = export_multi_page_atlas_bundle(grid, profile)
        sidecar = exported["sidecar"]
        animation = sidecar["animation_binding"]
        pages = exported["pages"]

        self.assertEqual("multi_page_atlas_sidecar_v1", animation["animation_model"])
        self.assertEqual(MULTI_PAGE_ATLAS_POLICY["algorithm_id"], animation["page_policy"]["algorithm_id"])
        self.assertGreaterEqual(len(pages), 2)
        self.assertEqual(len(pages), sidecar["asset_binding"]["page_count"])
        self.assertEqual(len(pages), len(animation["pages"]))
        self.assertEqual(7, animation["frame_count"])
        self.assertTrue(any(frame["rotation_degrees"] == 90 for frame in animation["frames"]))
        page_indices = {page["page_index"] for page in pages}
        self.assertEqual(page_indices, {page["page_index"] for page in animation["pages"]})
        self.assertEqual(page_indices, {frame["page_index"] for frame in animation["frames"]})
        for page in pages:
            decoded = decode_png_rgba(page["png_bytes"])
            self.assertLessEqual(decoded["width"], MULTI_PAGE_ATLAS_POLICY["max_page_width"])
            self.assertLessEqual(decoded["height"], MULTI_PAGE_ATLAS_POLICY["max_page_height"])
            self.assertEqual(decoded["width"], page["asset"]["width"])
            self.assertEqual(decoded["height"], page["asset"]["height"])
            self.assertTrue(page["asset"]["content_hash"].startswith("sha256:"))
        for frame in animation["frames"]:
            self.assertIn(frame["page_index"], page_indices)
            self.assertTrue(frame["page_content_hash"].startswith("sha256:"))
            self.assertTrue(frame["canonical_pixel_hash"].startswith("sha256:"))
            self.assertTrue(frame["packed_pixel_hash"].startswith("sha256:"))

    def test_import_reconstructs_semantics_frames_and_page_switching_playback(self):
        profile = load_profile(VALID_PROFILE_PATHS[0])
        grid = first_grid_for(profile)
        exported = export_multi_page_atlas_bundle(grid, profile)

        imported = import_multi_page_atlas_bundle(
            exported["pages"],
            exported["sidecar"],
            source_grid=grid,
        )
        restored = imported["restored_grid"]
        diff = compare_semantic_grid_fidelity(grid, restored)
        timeline = imported["runtime_playback"]["timeline"]

        self.assertTrue(imported["ok"], imported["errors"])
        self.assertTrue(validate_grid(restored).ok, validate_grid(restored).errors)
        self.assertTrue(is_grid_aligned(restored, profile).ok)
        self.assertEqual(1.0, imported["semantic_fidelity"])
        self.assertEqual(1.0, imported["reconstructed_frame_fidelity"])
        self.assertEqual(1.0, imported["runtime_frame_fidelity"])
        self.assertEqual([], diff["changed_cells"])
        self.assertEqual([], diff["missing_cells"])
        self.assertEqual([], diff["added_cells"])
        self.assertEqual([0, 1, 2, 3, 4, 5, 6, 0], [event["frame_index"] for event in timeline])
        self.assertGreater(len({event["page_index"] for event in timeline}), 1)
        self.assertTrue(all(event["page_hash_match"] for event in timeline))

    def test_lab_report_closes_multi_page_fixture_without_editor_or_package_claims(self):
        report = run_spritesheet_multi_page_atlas_lab(
            VALID_PROFILE_PATHS,
            GENERATED_ROOT,
        )

        self.assertEqual("spritesheet_multi_page_atlas_stage0", report["artifact_id"])
        self.assertEqual(3, report["profile_count"])
        self.assertEqual(3, report["bundle_roundtrip_success_count"])
        self.assertEqual(6, report["invalid_probe_rejected_count"])
        self.assertEqual(1.0, report["metrics"]["bundle_roundtrip_success_rate"])
        self.assertEqual(1.0, report["metrics"]["mean_semantic_fidelity"])
        self.assertEqual(1.0, report["metrics"]["mean_reconstructed_frame_fidelity"])
        self.assertEqual(1.0, report["metrics"]["mean_runtime_frame_fidelity"])
        self.assertGreaterEqual(report["metrics"]["mean_page_count"], 2.0)
        self.assertIn("multi_page_atlas_page_manifest", report["closed_states"])
        self.assertIn("multi_page_atlas_frame_page_binding", report["closed_states"])
        self.assertNotIn("multi-page atlas fixtures", report["blocked_states"])
        self.assertIn("editor-authored atlas fixtures", report["blocked_states"])
        self.assertIn("production renderer playback", report["blocked_states"])
        self.assertIn("live external editor rewrite validation", report["blocked_states"])
        self.assertIn("package runtime lifecycle integration", report["blocked_states"])

    def test_import_rejects_missing_page_page_hash_unknown_page_rect_hash_and_order_faults(self):
        report = run_spritesheet_multi_page_atlas_lab(
            VALID_PROFILE_PATHS,
            GENERATED_ROOT,
        )
        families = {
            family
            for result in report["invalid_probe_results"]
            for family in result["error_families"]
        }

        self.assertIn("atlas_page_missing", families)
        self.assertIn("atlas_page_hash_mismatch", families)
        self.assertIn("atlas_frame_page_unknown", families)
        self.assertIn("atlas_frame_rect_out_of_bounds", families)
        self.assertIn("atlas_frame_hash_mismatch", families)
        self.assertIn("runtime_frame_order_invalid", families)

    def test_write_artifacts_creates_page_pngs_sidecar_report_and_app_payload(self):
        report = run_spritesheet_multi_page_atlas_lab(
            VALID_PROFILE_PATHS,
            GENERATED_ROOT,
        )

        with tempfile.TemporaryDirectory() as temp_dir:
            output_dir = Path(temp_dir)
            write_spritesheet_multi_page_atlas_artifacts(output_dir, report)

            summary_path = output_dir / "spritesheet_multi_page_atlas_stage0.json"
            self.assertTrue(summary_path.exists())
            persisted = json.loads(summary_path.read_text(encoding="utf-8"))
            self.assertEqual(report["metrics"], persisted["metrics"])
            self.assertTrue((output_dir / "slip_lcd_seed_multi_page_atlas_sidecar.json").exists())
            self.assertTrue((output_dir / "slip_lcd_seed_multi_page_atlas_page_0.png").exists())
            self.assertTrue((output_dir / "README.md").exists())
            app_data = (output_dir / "spritesheet_multi_page_atlas_data.js").read_text(
                encoding="utf-8"
            )
            self.assertIn("MECHAGOTCHI_SPRITESHEET_MULTI_PAGE_ATLAS", app_data)


if __name__ == "__main__":
    unittest.main()
