import json
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
LAB_DIR = Path(__file__).resolve().parent
if str(LAB_DIR) not in sys.path:
    sys.path.insert(0, str(LAB_DIR))

from mecha_engine_scaffold_verification_gate import (  # noqa: E402
    ARTIFACT_ID,
    REQUIRED_IMPORT_TARGETS,
    REQUIRED_SCAFFOLD_PATHS,
    build_scaffold_verification_report,
    check_deferred_modules_absent,
    check_placeholder_only,
    check_promotion_gate_rerun,
    check_pyproject_metadata,
    check_required_paths,
    write_scaffold_verification_artifacts,
)


class MechaEngineScaffoldVerificationGateTests(unittest.TestCase):
    def test_gate_passes_against_real_scaffold(self):
        report = build_scaffold_verification_report(ROOT)

        self.assertEqual(ARTIFACT_ID, report["artifact_id"])
        self.assertTrue(report["package_root_exists"])
        self.assertTrue(report["gate_passed"], report["checks"])
        self.assertTrue(report["import_surface_accepted"])
        self.assertEqual("accept_empty_package_scaffold", report["decision"])
        for check in report["checks"]:
            self.assertTrue(check["ok"], check)
        self.assertEqual(
            report["metrics"]["checks_total"], report["metrics"]["checks_passed"]
        )
        self.assertEqual(0, report["metrics"]["lab_import_files"])
        self.assertEqual(0, report["metrics"]["sys_path_lab_files"])
        self.assertEqual(0, report["metrics"]["implementation_files"])
        self.assertEqual(0, report["metrics"]["deferred_modules_present"])
        self.assertGreaterEqual(report["metrics"]["import_suite_tests_run"], 6)
        self.assertEqual(10, len(REQUIRED_SCAFFOLD_PATHS))
        self.assertEqual(6, len(REQUIRED_IMPORT_TARGETS))
        # The empty scaffold never unblocks promotion, license metadata, or
        # deferred modules.
        self.assertIn("lab_code_promotion", report["blocked_states"])
        self.assertIn("release_license_metadata", report["blocked_states"])
        self.assertIn(
            "package_promotion_gate_rerun_after_scaffold", report["closed_states"]
        )

    def test_required_paths_check_reports_missing_scaffold(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            result = check_required_paths(Path(temp_dir))

        self.assertFalse(result["ok"])
        self.assertEqual(
            len(REQUIRED_SCAFFOLD_PATHS),
            len(result["evidence"]["missing_paths"]),
        )

    def test_pyproject_check_rejects_release_license_metadata(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            pyproject = root / "packages/mecha_engine/pyproject.toml"
            pyproject.parent.mkdir(parents=True)
            pyproject.write_text(
                "[build-system]\n"
                'requires = ["setuptools"]\n'
                'build-backend = "setuptools.build_meta"\n'
                "[project]\n"
                'name = "mecha-engine"\n'
                'version = "0.0.0"\n'
                'requires-python = ">=3.13"\n'
                'license = "MIT"\n',
                encoding="utf-8",
            )
            result = check_pyproject_metadata(root)

        self.assertFalse(result["ok"])
        self.assertEqual(["license"], result["evidence"]["declared_license_fields"])

    def test_placeholder_check_rejects_implementation_code(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            module = root / "packages/mecha_engine/src/mecha_engine/genome"
            module.mkdir(parents=True)
            (module / "__init__.py").write_text(
                "def validate_grid(payload):\n    return payload\n",
                encoding="utf-8",
            )
            result = check_placeholder_only(root)

        self.assertFalse(result["ok"])
        self.assertEqual(
            ["packages/mecha_engine/src/mecha_engine/genome/__init__.py"],
            result["evidence"]["implementation_files"],
        )

    def test_deferred_module_check_rejects_premature_modules(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            (root / "packages/mecha_engine/src/mecha_engine/learning").mkdir(
                parents=True
            )
            result = check_deferred_modules_absent(root)

        self.assertFalse(result["ok"])
        self.assertEqual(
            ["learning"], result["evidence"]["present_deferred_modules"]
        )

    def test_promotion_rerun_check_requires_updated_artifact(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            artifact = (
                root
                / "data/package_promotion/mecha_engine_package_promotion_gate_stage0.json"
            )
            artifact.parent.mkdir(parents=True)

            missing = check_promotion_gate_rerun(root)
            artifact.write_text(
                json.dumps({"summary": {"package_root_exists": False}}),
                encoding="utf-8",
            )
            stale = check_promotion_gate_rerun(root)
            artifact.write_text(
                json.dumps(
                    {
                        "summary": {
                            "package_root_exists": True,
                            "promotion_ready_count": 0,
                        }
                    }
                ),
                encoding="utf-8",
            )
            rerun = check_promotion_gate_rerun(root)

        self.assertFalse(missing["ok"])
        self.assertFalse(stale["ok"])
        self.assertTrue(rerun["ok"])
        self.assertEqual(0, rerun["evidence"]["promotion_ready_count"])

    def test_write_artifacts_creates_stage0_json(self):
        report = build_scaffold_verification_report(ROOT)
        with tempfile.TemporaryDirectory() as temp_dir:
            output_dir = Path(temp_dir)
            write_scaffold_verification_artifacts(output_dir, report)
            artifact_path = output_dir / f"{ARTIFACT_ID}.json"
            self.assertTrue(artifact_path.exists())
            loaded = json.loads(artifact_path.read_text(encoding="utf-8"))
        self.assertEqual(report["metrics"], loaded["metrics"])
        self.assertEqual(report["decision"], loaded["decision"])


if __name__ == "__main__":
    unittest.main()
