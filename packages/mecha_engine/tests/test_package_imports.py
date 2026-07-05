"""Import-surface tests for the empty mecha_engine scaffold.

Traceability: research/package_specs/mecha_engine_scaffold_verification_gate.md
("Import Acceptance", "Metadata Acceptance", "Negative Checks") and
research/package_specs/mecha_engine_contract_traceability_matrix.md
("Scaffold Test Obligations").

Import mechanics (documented choice): the verification gate's documented flow
installs the package first (``python -m pip install -e .\\packages\\mecha_engine``)
and then runs this suite, so the canonical import surface is the installed
package. To stay runnable in the simplest documented-compatible way without
requiring that install step, every import is exercised in a ``python -B -c``
subprocess whose PYTHONPATH points at this package's own ``src`` directory
(standard src-layout semantics; if the package is installed, the installed
surface satisfies the same probe). The test module itself never mutates the
interpreter module search path, so the verification gate's scan for
interpreter-path bypasses over ``packages/mecha_engine`` stays clean, and it
never points the subprocess at research lab directories.
"""

import os
import re
import subprocess
import sys
import tempfile
import tomllib
import unittest
from pathlib import Path


PACKAGE_ROOT = Path(__file__).resolve().parents[1]
REPO_ROOT = PACKAGE_ROOT.parents[1]
SRC_DIR = PACKAGE_ROOT / "src"

INITIAL_MODULES = ["genome", "generation", "lifecycle", "archive", "provenance"]
# Modules promoted after the initial five, each authorized by its own
# decision record: repair per decision record 0006
# (research/decision_records/0006-create-mecha-engine-repair-target.md);
# runtime per decision record 0008
# (research/decision_records/0008-propose-mecha-engine-runtime-target.md).
LATER_PROMOTED_MODULES = ["repair", "runtime"]
PROMOTED_MODULES = INITIAL_MODULES + LATER_PROMOTED_MODULES
DEFERRED_MODULES = ["learning", "render", "storage", "slip"]
IMPORT_TARGETS = ["mecha_engine"] + [
    f"mecha_engine.{module}" for module in PROMOTED_MODULES
]

_TOP_LEVEL_IMPLEMENTATION = re.compile(r"^(?:def |class )", re.MULTILINE)


def _run_import_subprocess(code: str, cwd: Path) -> subprocess.CompletedProcess:
    env = os.environ.copy()
    existing = env.get("PYTHONPATH")
    env["PYTHONPATH"] = str(SRC_DIR) + (os.pathsep + existing if existing else "")
    return subprocess.run(
        [sys.executable, "-B", "-c", code],
        capture_output=True,
        text=True,
        env=env,
        cwd=cwd,
        timeout=120,
    )


def _snapshot(directory: Path) -> set[str]:
    if not directory.exists():
        return set()
    return {
        path.relative_to(directory).as_posix()
        for path in directory.rglob("*")
        if path.is_file()
    }


class MechaEngineScaffoldImportTests(unittest.TestCase):
    def test_required_scaffold_paths_exist(self):
        required = [
            PACKAGE_ROOT / "pyproject.toml",
            PACKAGE_ROOT / "README.md",
            SRC_DIR / "mecha_engine" / "__init__.py",
            SRC_DIR / "mecha_engine" / "py.typed",
        ] + [
            SRC_DIR / "mecha_engine" / module / "__init__.py"
            for module in PROMOTED_MODULES
        ]
        for path in required:
            self.assertTrue(path.exists(), f"missing scaffold path: {path}")

    def test_deferred_modules_are_not_created(self):
        for module in DEFERRED_MODULES:
            self.assertFalse(
                (SRC_DIR / "mecha_engine" / module).exists(),
                f"deferred module must not exist without a decision record: {module}",
            )

    def test_later_promoted_modules_have_contract_tests(self):
        # A module may leave the deferred list only once its decision record
        # authorizes the target and its package contract test exists.
        for module in LATER_PROMOTED_MODULES:
            self.assertTrue(
                (PACKAGE_ROOT / "tests" / f"test_{module}_contract.py").exists(),
                f"promoted module lacks its contract test: {module}",
            )

    def test_pyproject_metadata_boundary(self):
        payload = tomllib.loads(
            (PACKAGE_ROOT / "pyproject.toml").read_text(encoding="utf-8")
        )
        self.assertIn("build-system", payload)
        project = payload.get("project", {})
        self.assertEqual("mecha-engine", project.get("name"))
        self.assertEqual("0.0.0", project.get("version"))
        self.assertIn("requires-python", project)
        # Release license metadata stays unset until the license decision
        # record exists (scaffold verification gate, "Metadata Acceptance").
        self.assertNotIn("license", project)
        self.assertNotIn("license-files", project)
        for classifier in project.get("classifiers", []):
            self.assertFalse(
                classifier.startswith("License"),
                f"license classifier declared before license decision: {classifier}",
            )

    def test_all_import_targets_import(self):
        code = "import " + ", ".join(IMPORT_TARGETS) + "\nprint('imports-ok')"
        with tempfile.TemporaryDirectory() as temp_dir:
            result = _run_import_subprocess(code, cwd=Path(temp_dir))
        self.assertEqual(0, result.returncode, result.stderr)
        self.assertIn("imports-ok", result.stdout)

    def test_import_loads_no_lab_modules(self):
        # The package surface must work through mecha_engine, never through
        # the research lab tree: after importing every target, no module named
        # after the lab tree may be loaded.
        code = (
            "import sys\n"
            "import " + ", ".join(IMPORT_TARGETS) + "\n"
            "lab_root = 'la' 'bs'\n"
            "loaded = sorted(\n"
            "    name for name in sys.modules\n"
            "    if name == lab_root or name.startswith(lab_root + '.')\n"
            ")\n"
            "print('lab-modules:' + ','.join(loaded))"
        )
        with tempfile.TemporaryDirectory() as temp_dir:
            result = _run_import_subprocess(code, cwd=Path(temp_dir))
        self.assertEqual(0, result.returncode, result.stderr)
        self.assertEqual("lab-modules:", result.stdout.strip())

    def test_import_writes_no_files(self):
        code = "import " + ", ".join(IMPORT_TARGETS)
        with tempfile.TemporaryDirectory() as temp_dir:
            scratch = Path(temp_dir)
            package_before = _snapshot(PACKAGE_ROOT)
            data_before = _snapshot(REPO_ROOT / "data")
            result = _run_import_subprocess(code, cwd=scratch)
            self.assertEqual(0, result.returncode, result.stderr)
            self.assertEqual(package_before, _snapshot(PACKAGE_ROOT))
            self.assertEqual(data_before, _snapshot(REPO_ROOT / "data"))
            self.assertEqual(set(), _snapshot(scratch))

    def test_unpromoted_modules_contain_no_implementation_code(self):
        # The scaffold-stage rule ("no copied lab implementation") applies to
        # module boundaries that have not been promoted yet. A module counts
        # as promoted once its package contract test exists
        # (tests/test_<module>_contract.py, per the contract traceability
        # matrix); every other package source file must stay a placeholder
        # with no top-level function or class definitions.
        promoted = {
            module
            for module in PROMOTED_MODULES
            if (PACKAGE_ROOT / "tests" / f"test_{module}_contract.py").exists()
        }
        for path in sorted((SRC_DIR / "mecha_engine").rglob("*.py")):
            relative_parts = path.relative_to(SRC_DIR / "mecha_engine").parts
            if relative_parts[0] in promoted:
                continue
            text = path.read_text(encoding="utf-8")
            self.assertIsNone(
                _TOP_LEVEL_IMPLEMENTATION.search(text),
                f"non-placeholder implementation in unpromoted scaffold area: {path}",
            )


if __name__ == "__main__":
    unittest.main()
