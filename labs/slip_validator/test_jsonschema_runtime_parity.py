import importlib.util
import json
import unittest
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]

JSONSCHEMA_AVAILABLE = importlib.util.find_spec("jsonschema") is not None

if JSONSCHEMA_AVAILABLE:
    from jsonschema_runtime_parity import (
        REPORT_PATH,
        build_parity_report,
        write_parity_report,
    )

VALID_PROFILE_PATHS = sorted((ROOT / "data/slips/valid").glob("*.json"))
FAILURE_CASE_PATHS = sorted((ROOT / "data/slips/failure_cases").glob("*.json"))
EXAMPLE_PROFILE_PATHS = sorted((ROOT / "research/slip/slip_examples").glob("*.json"))


@unittest.skipUnless(
    JSONSCHEMA_AVAILABLE,
    "jsonschema not installed; provision with: uv sync --group lab",
)
class JsonschemaRuntimeParityTests(unittest.TestCase):
    def test_layered_validation_matches_stage0_corpus_expectations(self):
        report = build_parity_report(
            VALID_PROFILE_PATHS, FAILURE_CASE_PATHS, EXAMPLE_PROFILE_PATHS
        )

        self.assertEqual(4, report["layered_outcomes"]["valid_accepted"])
        self.assertEqual(4, report["layered_outcomes"]["examples_accepted"])
        self.assertEqual(14, report["layered_outcomes"]["failures_rejected"])

    def test_only_the_documented_semantic_gap_separates_the_validators(self):
        report = build_parity_report(
            VALID_PROFILE_PATHS, FAILURE_CASE_PATHS, EXAMPLE_PROFILE_PATHS
        )

        self.assertEqual([], report["parity"]["unexplained_disagreements"])
        self.assertEqual(
            [
                "data/slips/failure_cases/slip_body_mass_bounds_reversed.json",
                "data/slips/failure_cases/slip_v2_forbids_required.json",
            ],
            report["parity"]["known_semantic_gap_cases"],
        )
        self.assertEqual(
            report["parity"]["total"] - 2,
            report["parity"]["agreements"],
        )

    def test_report_artifact_is_written(self):
        before = REPORT_PATH.read_bytes()
        with tempfile.TemporaryDirectory() as temporary:
            output = Path(temporary) / 'nested/report.json'
            report = write_parity_report(VALID_PROFILE_PATHS, FAILURE_CASE_PATHS, EXAMPLE_PROFILE_PATHS, report_path=output)
            persisted = json.loads(output.read_text(encoding='utf-8'))
            self.assertEqual(report, persisted)
            self.assertIn('lab_runtime_jsonschema_validation', persisted['closed_states'])
            self.assertIn('package_runtime_jsonschema_validation', persisted['blocked_states'])
        self.assertEqual(before, REPORT_PATH.read_bytes())


if __name__ == "__main__":
    unittest.main()
