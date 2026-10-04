import json
import unittest
from pathlib import Path

from slip_validator import (
    SCHEMA_PATH,
    validate_profile,
    validate_profile_file,
    validate_profile_corpus,
)


ROOT = Path(__file__).resolve().parents[2]


VALID_PROFILE_PATHS = sorted((ROOT / "data/slips/valid").glob("*.json"))
FAILURE_CASE_PATHS = sorted((ROOT / "data/slips/failure_cases").glob("*.json"))
EXAMPLE_PROFILE_PATHS = sorted((ROOT / "research/slip/slip_examples").glob("*.json"))


class SlipValidatorTests(unittest.TestCase):
    def test_schema_is_draft_2020_12_and_names_required_fields(self):
        schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))

        self.assertEqual("https://json-schema.org/draft/2020-12/schema", schema["$schema"])
        self.assertEqual("https://mechagotchi.local/schema/slip/0.1.0", schema["$id"])
        self.assertIn("slip_version", schema["required"])
        self.assertIn("profile_id", schema["required"])
        self.assertIn("grid", schema["required"])
        self.assertIn("mutation", schema["required"])

    def test_all_current_valid_profiles_pass_schema_and_semantic_validation(self):
        self.assertEqual(5, len(VALID_PROFILE_PATHS))

        for path in VALID_PROFILE_PATHS:
            with self.subTest(path=str(path)):
                result = validate_profile_file(path)
                self.assertTrue(result["ok"], result["errors"])
                self.assertEqual([], result["errors"])

    def test_expanded_failure_corpus_is_rejected_with_named_error_families(self):
        self.assertGreaterEqual(len(FAILURE_CASE_PATHS), 10)

        report = validate_profile_corpus(
            VALID_PROFILE_PATHS,
            FAILURE_CASE_PATHS,
            EXAMPLE_PROFILE_PATHS,
        )

        self.assertEqual(len(VALID_PROFILE_PATHS), report["valid_profile_count"])
        self.assertEqual(len(FAILURE_CASE_PATHS), report["failure_case_count"])
        self.assertEqual(len(EXAMPLE_PROFILE_PATHS), report["example_profile_count"])
        self.assertEqual(len(VALID_PROFILE_PATHS), report["accepted_valid_profiles"])
        self.assertEqual(len(FAILURE_CASE_PATHS), report["rejected_failure_cases"])
        self.assertEqual(len(EXAMPLE_PROFILE_PATHS), report["accepted_example_profiles"])
        self.assertEqual([], report["unexpected_acceptances"])
        self.assertEqual([], report["unexpected_rejections"])
        self.assertEqual([], report["unexpected_example_rejections"])

        observed = set(report["observed_error_families"])
        expected = {
            "schema_required",
            "schema_type",
            "schema_enum",
            "schema_range",
            "schema_min_items",
            "schema_additional_properties",
            "semantic_body_mass_bounds",
            "semantic_numeric_bool",
            "semantic_version_gate",
            "semantic_forbidden_traits",
        }
        self.assertTrue(expected.issubset(observed), observed)

    def test_boolean_weights_are_rejected_as_semantic_numeric_errors(self):
        profile = json.loads((ROOT / "data/slips/valid/slip_lcd_seed.json").read_text(encoding="utf-8"))
        profile["behavior"]["curiosity"] = True

        result = validate_profile(profile)

        self.assertFalse(result["ok"])
        self.assertIn("semantic_numeric_bool", result["error_families"])

    def test_research_plan_slip_examples_are_valid_schema_examples(self):
        self.assertEqual(5, len(EXAMPLE_PROFILE_PATHS))

        expected_ids = {
            json.loads(path.read_text(encoding="utf-8"))["profile_id"]
            for path in VALID_PROFILE_PATHS
        }
        observed_ids = set()

        for path in EXAMPLE_PROFILE_PATHS:
            with self.subTest(path=str(path)):
                profile = json.loads(path.read_text(encoding="utf-8"))
                observed_ids.add(profile["profile_id"])
                result = validate_profile(profile, source_path=path)
                self.assertTrue(result["ok"], result["errors"])

        self.assertEqual(expected_ids, observed_ids)


if __name__ == "__main__":
    unittest.main()
