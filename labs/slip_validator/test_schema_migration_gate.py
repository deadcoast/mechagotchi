import json
import unittest
import tempfile
from pathlib import Path

from schema_migration_gate import (
    CURRENT_SLIP_VERSION,
    REPORT_PATH,
    build_schema_migration_dependency_report,
    compare_schema_surfaces,
    evaluate_migration_request,
    write_schema_migration_dependency_report,
)


ROOT = Path(__file__).resolve().parents[2]


class SlipSchemaMigrationGateTests(unittest.TestCase):
    def test_dependency_state_records_available_tools_without_package_assumptions(self):
        report = build_schema_migration_dependency_report()

        self.assertEqual(
            "research_slip_schema_migration_dependency_gate_no_package_code",
            report["status"],
        )
        self.assertTrue(report["pydantic_available"])
        # jsonschema availability is an environment observation, recorded but
        # not pinned: the stable claim is the dependency decision below
        # (decision record 0005 declares the lab dependency group).
        self.assertIsInstance(report["jsonschema_available"], bool)
        self.assertTrue(report["dependency_manifest_present"])
        # The packages/ root exists as of the mecha_engine scaffold step
        # (decision record 0004); package-scoped states below stay blocked
        # because the scaffold carries no implementation or dependencies.
        self.assertTrue(report["package_root_exists"])
        self.assertEqual(
            "declared_in_lab_dependency_group_for_lab_contract",
            report["dependency_decision"]["pydantic"],
        )
        self.assertEqual(
            "declared_in_lab_dependency_group_runtime_validation_proven_by_parity_lab",
            report["dependency_decision"]["jsonschema"],
        )

    def test_authored_and_pydantic_schemas_match_core_contract_surface(self):
        comparison = compare_schema_surfaces()

        self.assertEqual([], comparison["mismatches"])
        self.assertEqual(
            [
                "behavior",
                "grid",
                "mutation",
                "name",
                "profile_id",
                "slip_version",
                "survival_weights",
            ],
            comparison["top_level_required"],
        )
        self.assertEqual(
            ["amber_terminal", "crt_blue", "gameboy_gray", "lcd_green", "pocket_plum"],
            comparison["palette_values"],
        )
        self.assertEqual(["body_core", "expression", "sensor"], comparison["organ_roles"])

    def test_migration_policy_accepts_only_current_version_without_conversion(self):
        payload = json.loads((ROOT / "data/slips/valid/slip_lcd_seed.json").read_text(encoding="utf-8"))

        result = evaluate_migration_request(payload)

        self.assertTrue(result["ok"])
        self.assertEqual(CURRENT_SLIP_VERSION, result["source_version"])
        self.assertEqual(CURRENT_SLIP_VERSION, result["target_version"])
        self.assertEqual("accept_current_no_migration", result["action"])
        self.assertEqual([], result["errors"])

    def test_migration_policy_rejects_missing_typed_or_unknown_versions(self):
        missing_result = evaluate_migration_request({})
        typed_result = evaluate_migration_request({"slip_version": 0.1})
        unknown_result = evaluate_migration_request({"slip_version": "0.2.0"})

        self.assertEqual("schema_version_missing", missing_result["errors"][0]["family"])
        self.assertEqual("schema_version_type", typed_result["errors"][0]["family"])
        self.assertEqual("schema_version_unsupported", unknown_result["errors"][0]["family"])
        self.assertEqual("reject_before_validation", missing_result["action"])
        self.assertEqual("reject_before_validation", typed_result["action"])
        self.assertEqual("reject_before_validation", unknown_result["action"])

    def test_report_artifact_is_written(self):
        before = REPORT_PATH.read_bytes()
        with tempfile.TemporaryDirectory() as temporary:
            output = Path(temporary) / 'nested/report.json'
            report = write_schema_migration_dependency_report(report_path=output)
            persisted = json.loads(output.read_text(encoding='utf-8'))
            self.assertEqual(report, persisted)
            self.assertIn('schema_migration_policy', persisted['closed_states'])
            self.assertIn('lab_runtime_jsonschema_validation', persisted['closed_states'])
            self.assertIn('package_runtime_jsonschema_validation', persisted['blocked_states'])
        self.assertEqual(before, REPORT_PATH.read_bytes())


if __name__ == "__main__":
    unittest.main()
