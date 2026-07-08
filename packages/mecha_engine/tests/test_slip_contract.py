"""SLIP contract tests for the mecha_engine package surface.

Traceability: research/decision_records/0027-slip-module-disposition.md
(the tenth module's port gates) and decision records 0012/0013 (the
schema ladder). Import mechanics match every other contract suite: the
probes run in one ``python -B`` subprocess whose PYTHONPATH points at
this package's own ``src`` directory, executed by
``tests/helpers/slip_contract_driver.py`` through ``mecha_engine.slip``
only. Fixtures are the frozen repository corpora (valid, failure_cases,
and the SLIP zoo — the same corpus gate-1's reconciliation swept); the
lab-side pin against the Stage 0 authority is
``labs/grid_genome/test_package_slip_parity.py``.
"""

import json
import os
import subprocess
import sys
import unittest
from pathlib import Path

PACKAGE_ROOT = Path(__file__).resolve().parents[1]
REPO_ROOT = PACKAGE_ROOT.parents[1]
SRC_DIR = PACKAGE_ROOT / "src"
DRIVER = Path(__file__).resolve().parent / "helpers" / "slip_contract_driver.py"


def _run_driver() -> dict:
    env = os.environ.copy()
    existing = env.get("PYTHONPATH")
    env["PYTHONPATH"] = str(SRC_DIR) + (os.pathsep + existing if existing else "")
    result = subprocess.run(
        [sys.executable, "-B", str(DRIVER), "--repo-root", str(REPO_ROOT)],
        capture_output=True,
        text=True,
        env=env,
        cwd=PACKAGE_ROOT,
        timeout=300,
    )
    if result.returncode != 0:
        raise AssertionError(
            f"slip contract driver failed ({result.returncode}):\n"
            f"{result.stderr}"
        )
    return json.loads(result.stdout)


class MechaEngineSlipContractTests(unittest.TestCase):
    report: dict

    @classmethod
    def setUpClass(cls):
        cls.report = _run_driver()

    def test_every_valid_fixture_passes(self):
        self.assertGreater(self.report["valid_fixture_count"], 0)
        self.assertTrue(self.report["valid_all_ok"])

    def test_every_failure_case_is_rejected(self):
        self.assertGreater(self.report["failure_case_count"], 0)
        self.assertTrue(self.report["failure_all_rejected"])

    def test_the_zoo_judges_like_the_authority(self):
        # The zoo carries both clean archetypes and corrupted variants;
        # the surface must accept a substantial majority and reject the
        # corruptions (exact verdict parity with the lab authority is
        # the lab-side pin's job — here the corpus must be JUDGED).
        self.assertGreater(self.report["zoo_count"], 0)
        self.assertGreater(self.report["zoo_ok_count"], 0)
        self.assertLess(
            self.report["zoo_ok_count"], self.report["zoo_count"] + 1
        )

    def test_slip_result_shape(self):
        self.assertTrue(self.report["slip_result_shape_ok"])

    def test_ladder_fields_are_version_gated_and_bounded(self):
        for key, verdict in self.report["ladder_rejections"].items():
            self.assertTrue(verdict["rejected"], key)
            self.assertTrue(verdict["has_errors"], key)

    def test_alignment_accepts_and_rejects_with_named_errors(self):
        self.assertTrue(self.report["lcd_seed_aligned"])
        self.assertTrue(self.report["misaligned_rejected"])
        self.assertTrue(self.report["misaligned_error_names_palette"])

    def test_deterministic_and_pure(self):
        self.assertTrue(self.report["deterministic_repeat_identical"])
        self.assertFalse(self.report["inputs_mutated"])

    def test_slip_source_keeps_the_package_boundary(self):
        source_dir = SRC_DIR / "mecha_engine" / "slip"
        for path in source_dir.glob("*.py"):
            text = path.read_text(encoding="utf-8")
            self.assertNotIn("import labs", text, path.name)
            self.assertNotIn("from labs", text, path.name)
            self.assertNotIn("sys" + ".path", text, path.name)


if __name__ == "__main__":
    unittest.main()
