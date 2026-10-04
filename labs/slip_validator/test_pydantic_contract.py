import json
import unittest
import tempfile
from pathlib import Path

from pydantic_contract import (
    CONTRACT_STATUS,
    GENERATED_SCHEMA_PATH,
    REPORT_PATH,
    SLIPProfile,
    build_pydantic_contract_report,
    write_pydantic_contract_artifacts,
)


ROOT = Path(__file__).resolve().parents[2]


VALID_PROFILE_PATHS = sorted((ROOT / "data/slips/valid").glob("*.json"))
FAILURE_CASE_PATHS = sorted((ROOT / "data/slips/failure_cases").glob("*.json"))
EXAMPLE_PROFILE_PATHS = sorted((ROOT / "research/slip/slip_examples").glob("*.json"))


class SlipPydanticContractTests(unittest.TestCase):
    def test_pydantic_model_accepts_current_valid_profiles_and_examples(self):
        self.assertEqual(4, len(VALID_PROFILE_PATHS))
        self.assertEqual(4, len(EXAMPLE_PROFILE_PATHS))

        for path in VALID_PROFILE_PATHS + EXAMPLE_PROFILE_PATHS:
            with self.subTest(path=str(path)):
                payload = json.loads(path.read_text(encoding="utf-8"))
                model = SLIPProfile.model_validate(payload)
                self.assertEqual(payload["profile_id"], model.profile_id)
                # Ladder fields (DR 0012) are optional-additive: they dump only
            # when set, so the roundtrip excludes unset Nones.
            self.assertEqual(
                payload, model.model_dump(mode="json", exclude_none=True)
            )

    def test_pydantic_model_rejects_expanded_failure_corpus(self):
        self.assertEqual(14, len(FAILURE_CASE_PATHS))

        report = build_pydantic_contract_report(
            valid_paths=VALID_PROFILE_PATHS,
            failure_paths=FAILURE_CASE_PATHS,
            example_paths=EXAMPLE_PROFILE_PATHS,
        )

        self.assertEqual(CONTRACT_STATUS, report["status"])
        self.assertEqual(4, report["accepted_valid_profiles"])
        self.assertEqual(4, report["accepted_example_profiles"])
        self.assertEqual(14, report["rejected_failure_cases"])
        self.assertEqual([], report["unexpected_valid_rejections"])
        self.assertEqual([], report["unexpected_example_rejections"])
        self.assertEqual([], report["unexpected_failure_acceptances"])
        self.assertTrue(report["pydantic_available"])
        # jsonschema availability is an environment observation, recorded but
        # not pinned: the stable claim is the dependency policy, which defers
        # jsonschema until a repository dependency manifest exists.
        self.assertIsInstance(report["jsonschema_available"], bool)

    def test_pydantic_model_rejects_numeric_string_coercion(self):
        payload = json.loads((ROOT / "data/slips/valid/slip_lcd_seed.json").read_text(encoding="utf-8"))
        payload["grid"]["body_mass_min"] = "4"
        payload["behavior"]["curiosity"] = "0.6"

        report = build_pydantic_contract_report(
            valid_paths=[],
            failure_paths=[],
            example_paths=[],
            ad_hoc_payloads=[("numeric_string_payload", payload)],
        )

        result = report["ad_hoc_results"][0]
        self.assertFalse(result["ok"])
        self.assertEqual(["schema_type"], result["error_families"])

    def test_pydantic_generated_schema_preserves_core_contract_shape(self):
        report = build_pydantic_contract_report(
            valid_paths=VALID_PROFILE_PATHS,
            failure_paths=FAILURE_CASE_PATHS,
            example_paths=EXAMPLE_PROFILE_PATHS,
        )

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
            report["generated_schema_summary"]["top_level_required"],
        )
        self.assertTrue(report["generated_schema_summary"]["top_level_forbid_extra"])
        self.assertEqual(
            ["amber_terminal", "crt_blue", "gameboy_gray", "lcd_green", "pocket_plum"],
            report["generated_schema_summary"]["palette_values"],
        )
        self.assertEqual(
            ["body_core", "expression", "sensor"],
            report["generated_schema_summary"]["organ_role_values"],
        )

    def test_contract_artifacts_are_written(self):
        before = {p: p.read_bytes() for p in (REPORT_PATH, GENERATED_SCHEMA_PATH)}
        with tempfile.TemporaryDirectory() as temporary:
            output = Path(temporary) / 'nested/report.json'
            schema = Path(temporary) / 'schema/generated.json'
            report = write_pydantic_contract_artifacts(VALID_PROFILE_PATHS, FAILURE_CASE_PATHS, EXAMPLE_PROFILE_PATHS, report_path=output, schema_path=schema)
            self.assertEqual(CONTRACT_STATUS, report['status'])
            self.assertEqual(report, json.loads(output.read_text(encoding='utf-8')))
            generated = json.loads(schema.read_text(encoding='utf-8'))
            self.assertEqual('Mechagotchi SLIP Pydantic Contract', generated['title'])
        self.assertEqual(before, {p: p.read_bytes() for p in before})


if __name__ == "__main__":
    unittest.main()
