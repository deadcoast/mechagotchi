"""CuBFF pressure contract for ``mecha_engine.runtime.evolve`` (R2.5).

Traceability: research/decision_records/0020-cubff-pressure-runtime-promotion.md
(the plan), research/decision_records/0018-cubff-live-lineage-pressure.md
(the R2 semantics being promoted), and
research/package_specs/mecha_engine_runtime_interface_spec.md.

Import mechanics match every contract suite: the probes run in one
``python -B`` subprocess whose PYTHONPATH points at this package's own
``src`` directory, executed by
``tests/helpers/cubff_pressure_contract_driver.py``. The verbatim
equality of ``runtime/_cubff.py`` with the lab authority is pinned
lab-side (``labs/cubff_transducer/test_package_cubff_parity.py``); this
suite proves the promoted contract directly. Real ingested snapshots
are absent (``awaiting_real_cubff_snapshots``) — a recorded blocked
state, not a probe.
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
DRIVER = (
    Path(__file__).resolve().parent
    / "helpers"
    / "cubff_pressure_contract_driver.py"
)

REQUIRED_CHECKS = [
    "accepts_cubff_pressure_source_keyword",
    "absent_source_byte_identical",
    "report_block_present",
    "scalars_only_cross_the_boundary",
    "snapshots_cycle_in_order",
    "deterministic",
    "directional_effect",
    "rejects_non_list_source",
    "rejects_empty_source",
]


class CubffPressureContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        environment = dict(os.environ)
        environment["PYTHONPATH"] = str(SRC_DIR)
        completed = subprocess.run(
            [sys.executable, "-B", str(DRIVER), str(REPO_ROOT)],
            capture_output=True,
            text=True,
            env=environment,
            check=False,
        )
        if completed.returncode != 0:
            raise AssertionError(
                "cubff pressure contract driver failed:\n"
                f"stdout: {completed.stdout}\nstderr: {completed.stderr}"
            )
        cls.checks = json.loads(completed.stdout)

    def test_every_contract_check_passes(self):
        for check in REQUIRED_CHECKS:
            with self.subTest(check=check):
                self.assertTrue(
                    self.checks.get(check),
                    f"contract check failed: {check} "
                    f"(detail: {self.checks.get('directional_detail')})",
                )


if __name__ == "__main__":
    unittest.main()
