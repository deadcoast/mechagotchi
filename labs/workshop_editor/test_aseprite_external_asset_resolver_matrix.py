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

from aseprite_external_asset_resolver_matrix import (
    RESOLVER_POLICY_IDS,
    export_aseprite_external_asset_resolver_matrix_bundle,
    import_aseprite_document_variant_with_resolver,
    make_ambiguous_resolver_input,
    make_missing_asset_resolver_input,
    make_path_traversal_resolver_input,
    make_tampered_payload_resolver_input,
    resolve_aseprite_external_assets,
    run_aseprite_external_asset_resolver_matrix_lab,
    write_aseprite_external_asset_resolver_matrix_artifacts,
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


class AsepriteExternalAssetResolverMatrixTests(unittest.TestCase):
    def test_export_builds_direct_relative_content_addressed_and_multi_root_resolvers(self):
        profile = load_profile(VALID_PROFILE_PATHS[0])
        grid = first_grid_for(profile)

        bundle = export_aseprite_external_asset_resolver_matrix_bundle(grid, profile)

        self.assertEqual(RESOLVER_POLICY_IDS, [case["policy_id"] for case in bundle["resolver_cases"]])
        self.assertEqual(["indexed_8", "grayscale_alpha_16", "rgba_32"], [variant["variant_id"] for variant in bundle["document_variants"]])
        self.assertEqual(3, len(bundle["external_asset_manifest"]))
        for case in bundle["resolver_cases"]:
            resolved = resolve_aseprite_external_assets(bundle["external_asset_manifest"], case["resolver_input"])
            self.assertEqual(3, len(resolved))
            self.assertEqual(
                sorted(entry["name"] for entry in bundle["external_asset_manifest"]),
                sorted(asset["name"] for asset in resolved),
            )
            self.assertEqual(case["policy_id"], case["resolver_input"]["policy_id"])

    def test_import_restores_all_document_variants_through_each_resolver_policy(self):
        profile = load_profile(VALID_PROFILE_PATHS[0])
        grid = first_grid_for(profile)
        bundle = export_aseprite_external_asset_resolver_matrix_bundle(grid, profile)

        for variant in bundle["document_variants"]:
            for case in bundle["resolver_cases"]:
                imported = import_aseprite_document_variant_with_resolver(
                    variant["project_bytes"],
                    case["resolver_input"],
                    source_grid=grid,
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
                self.assertEqual(3, imported["project_policy"]["resolved_external_asset_count"])
                self.assertEqual(case["policy_id"], imported["project_policy"]["external_asset_resolver_policy"])
                self.assertFalse(imported["project_policy"]["live_external_editor_verified"])

    def test_resolver_rejects_missing_hash_ambiguity_traversal_and_unknown_policy(self):
        profile = load_profile(VALID_PROFILE_PATHS[0])
        grid = first_grid_for(profile)
        bundle = export_aseprite_external_asset_resolver_matrix_bundle(grid, profile)
        variant = bundle["document_variants"][0]
        manifest = bundle["external_asset_manifest"]
        base_input = bundle["resolver_cases"][1]["resolver_input"]

        probes = [
            (
                make_missing_asset_resolver_input(base_input),
                "aseprite_resolver_asset_missing",
            ),
            (
                make_tampered_payload_resolver_input(base_input),
                "aseprite_resolver_asset_hash_mismatch",
            ),
            (
                make_ambiguous_resolver_input(base_input),
                "aseprite_resolver_asset_ambiguous",
            ),
            (
                make_path_traversal_resolver_input(base_input),
                "aseprite_resolver_path_traversal",
            ),
            (
                {"policy_id": "unsupported_policy", "assets": []},
                "aseprite_resolver_policy_unsupported",
            ),
        ]

        for resolver_input, family in probes:
            imported = import_aseprite_document_variant_with_resolver(
                variant["project_bytes"],
                resolver_input,
                source_grid=grid,
            )
            self.assertFalse(imported["ok"])
            self.assertIn(family, imported["error_families"])
            self.assertNotIn("restored_grid", imported)

        direct_missing = resolve_aseprite_external_assets(
            manifest,
            make_missing_asset_resolver_input(bundle["resolver_cases"][0]["resolver_input"]),
            strict=False,
        )
        self.assertEqual(2, len(direct_missing))

    def test_lab_report_closes_only_bounded_resolver_matrix_subset(self):
        report = run_aseprite_external_asset_resolver_matrix_lab(
            VALID_PROFILE_PATHS,
            GENERATED_ROOT,
        )

        self.assertEqual("aseprite_external_asset_resolver_matrix_stage0", report["artifact_id"])
        self.assertEqual(3, report["profile_count"])
        self.assertEqual(36, report["resolver_roundtrip_count"])
        self.assertEqual(36, report["resolver_roundtrip_success_count"])
        self.assertEqual(5, report["invalid_probe_rejected_count"])
        self.assertEqual(1.0, report["metrics"]["resolver_roundtrip_success_rate"])
        self.assertEqual(1.0, report["metrics"]["mean_semantic_fidelity"])
        self.assertEqual(1.0, report["metrics"]["external_asset_resolution_rate"])
        self.assertIn("aseprite_relative_file_asset_resolver_subset", report["closed_states"])
        self.assertIn("aseprite_content_addressed_asset_resolver_subset", report["closed_states"])
        self.assertIn("live_external_editor_rewrite_validation", report["blocked_states"])
        self.assertIn("editor_authored_aseprite_document_variants", report["blocked_states"])
        self.assertIn("arbitrary_aseprite_project_schema_coverage", report["blocked_states"])

    def test_write_artifacts_creates_report_resolver_sources_projects_and_app_payload(self):
        report = run_aseprite_external_asset_resolver_matrix_lab(
            VALID_PROFILE_PATHS,
            GENERATED_ROOT,
        )

        with tempfile.TemporaryDirectory() as temp_dir:
            output_dir = Path(temp_dir)
            write_aseprite_external_asset_resolver_matrix_artifacts(output_dir, report)

            summary_path = output_dir / "aseprite_external_asset_resolver_matrix_stage0.json"
            self.assertTrue(summary_path.exists())
            persisted = json.loads(summary_path.read_text(encoding="utf-8"))
            self.assertEqual(report["metrics"], persisted["metrics"])
            self.assertTrue((output_dir / "projects" / "slip_lcd_seed_indexed_8.aseprite").exists())
            self.assertTrue((output_dir / "resolver_sources" / "slip_lcd_seed" / "assets" / "slip_lcd_seed_palette.gpl").exists())
            self.assertTrue((output_dir / "resolver_sources" / "content_addressed").exists())
            self.assertTrue((output_dir / "README.md").exists())
            app_data = (output_dir / "aseprite_external_asset_resolver_matrix_data.js").read_text(
                encoding="utf-8"
            )
            self.assertIn("MECHAGOTCHI_ASEPRITE_EXTERNAL_ASSET_RESOLVER_MATRIX", app_data)


if __name__ == "__main__":
    unittest.main()
