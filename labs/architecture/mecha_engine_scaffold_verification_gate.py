"""Executable scaffold verification gate for packages/mecha_engine.

Executes the acceptance checklist defined by
research/package_specs/mecha_engine_scaffold_verification_gate.md against the
real repository: required scaffold paths, pyproject metadata rules (including
the DR 0028 Apache-2.0 license declaration, which replaced the original
release-license prohibition), the promoted-module import surface, import-time
side-effect freedom, lab-boundary negative checks, placeholder-only source,
deferred-module absence, the package import test suite, and the
package-promotion-gate rerun requirement. It regenerates
data/architecture/mecha_engine_scaffold_verification_gate_stage0.json, which
previously recorded the gate definition authored while the scaffold was
absent.
"""

import argparse
import json
import os
import re
import subprocess
import sys
import tomllib
from pathlib import Path

from mecha_engine_runtime_boundary_gate import inspect_package_lab_boundary


REPO_ROOT = Path(__file__).resolve().parents[2]

ARTIFACT_ID = "mecha_engine_scaffold_verification_gate_stage0"
DEFAULT_OUTPUT_DIR = REPO_ROOT / "data/architecture"

INITIAL_MODULES = ["genome", "generation", "lifecycle", "archive", "provenance"]
# Modules promoted after the initial five, each authorized by its own
# decision record: repair by 0006-create-mecha-engine-repair-target.md
# (wound-site stability blocker cleared); runtime by
# 0008-propose-mecha-engine-runtime-target.md (accepted 2026-07-05,
# composed-loop evidence); learning by
# 0009-create-mecha-engine-learning-target.md (accepted 2026-07-05,
# stress learning benchmark: wellbeing claim only); storage by
# 0022-storage-module.md (C3 port, 2026-07-07); slip by
# 0027-slip-module-disposition.md (F2 port, 2026-07-07, four private
# mirrors collapsed after zero-divergence reconciliation).
LATER_PROMOTED_MODULES = ["repair", "runtime", "learning", "storage", "slip"]
PACKAGE_MODULES = INITIAL_MODULES + LATER_PROMOTED_MODULES
# render is the whole deferred set: dispositioned REJECTED-until-consumer
# by decision record 0026, with its re-opener named there.
DEFERRED_MODULES = ["render"]

REQUIRED_SCAFFOLD_PATHS = [
    "packages/mecha_engine/pyproject.toml",
    "packages/mecha_engine/README.md",
    "packages/mecha_engine/src/mecha_engine/__init__.py",
    "packages/mecha_engine/src/mecha_engine/py.typed",
    *[
        f"packages/mecha_engine/src/mecha_engine/{module}/__init__.py"
        for module in PACKAGE_MODULES
    ],
    "packages/mecha_engine/tests/test_package_imports.py",
]

REQUIRED_IMPORT_TARGETS = ["mecha_engine"] + [
    f"mecha_engine.{module}" for module in PACKAGE_MODULES
]

# DR 0028 (2026-07-07) closed the original license prohibition: metadata
# must now DECLARE Apache-2.0, pointing at the repo-root LICENSE (the
# same pin test_package_imports.test_pyproject_metadata_boundary holds).
REQUIRED_LICENSE = "Apache-2.0"
REQUIRED_LICENSE_FILES = ["../../LICENSE"]

SOURCE_ARTIFACTS = [
    "research/decision_records/0004-mecha-engine-package-scaffold.md",
    "research/decision_records/0006-create-mecha-engine-repair-target.md",
    "research/decision_records/0008-propose-mecha-engine-runtime-target.md",
    "research/decision_records/0009-create-mecha-engine-learning-target.md",
    "research/decision_records/0022-storage-module.md",
    "research/decision_records/0026-render-module-disposition.md",
    "research/decision_records/0027-slip-module-disposition.md",
    "research/decision_records/0028-license-and-dependency-policy.md",
    "research/package_specs/mecha_engine_scaffold_verification_gate.md",
    "research/package_specs/mecha_engine_contract_traceability_matrix.md",
    "data/architecture/mecha_engine_package_scaffold_decision_stage0.json",
    "data/package_promotion/mecha_engine_package_promotion_gate_stage0.json",
]

EXTERNAL_REFERENCES = [
    {
        "name": "Python Packaging User Guide - src layout vs flat layout",
        "url": "https://packaging.python.org/en/latest/discussions/src-layout-vs-flat-layout/",
    },
    {
        "name": "Python Packaging User Guide - pyproject.toml specification",
        "url": "https://packaging.python.org/en/latest/specifications/pyproject-toml/",
    },
]

_TOP_LEVEL_IMPLEMENTATION = re.compile(r"^(?:def |class )", re.MULTILINE)


def _import_probe_env(root: Path) -> dict:
    env = os.environ.copy()
    src_dir = root / "packages/mecha_engine/src"
    existing = env.get("PYTHONPATH")
    env["PYTHONPATH"] = str(src_dir) + (os.pathsep + existing if existing else "")
    return env


def _run_import_subprocess(root: Path, code: str) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, "-B", "-c", code],
        capture_output=True,
        text=True,
        env=_import_probe_env(root),
        cwd=root,
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


def check_required_paths(root: Path) -> dict:
    missing = [
        path for path in REQUIRED_SCAFFOLD_PATHS if not (root / path).exists()
    ]
    return {
        "check_id": "required_scaffold_paths_present",
        "ok": not missing,
        "evidence": {
            "required_path_count": len(REQUIRED_SCAFFOLD_PATHS),
            "missing_paths": missing,
        },
    }


def check_pyproject_metadata(root: Path) -> dict:
    pyproject_path = root / "packages/mecha_engine/pyproject.toml"
    if not pyproject_path.exists():
        return {
            "check_id": "package_metadata_boundary",
            "ok": False,
            "evidence": {"pyproject_exists": False},
        }
    payload = tomllib.loads(pyproject_path.read_text(encoding="utf-8"))
    project = payload.get("project", {})
    license_classifiers = [
        classifier
        for classifier in project.get("classifiers", [])
        if classifier.startswith("License")
    ]
    version = project.get("version", "")
    evidence = {
        "pyproject_exists": True,
        "build_system_present": "build-system" in payload,
        "project_present": "project" in payload,
        "name": project.get("name"),
        "version": version,
        "requires_python": project.get("requires-python"),
        "declared_license": project.get("license"),
        "declared_license_files": project.get("license-files"),
        "license_classifiers": license_classifiers,
    }
    # DR 0028: the license must be DECLARED (Apache-2.0 via the root
    # LICENSE); License classifiers stay out so the license field is the
    # single source of truth.
    ok = (
        evidence["build_system_present"]
        and evidence["project_present"]
        and project.get("name") == "mecha-engine"
        and isinstance(version, str)
        and version.startswith("0.")
        and bool(project.get("requires-python"))
        and project.get("license") == REQUIRED_LICENSE
        and project.get("license-files") == REQUIRED_LICENSE_FILES
        and not license_classifiers
    )
    return {"check_id": "package_metadata_boundary", "ok": ok, "evidence": evidence}


def check_import_surface(root: Path) -> dict:
    code = (
        "import sys\n"
        "import " + ", ".join(REQUIRED_IMPORT_TARGETS) + "\n"
        "lab_modules = sorted(\n"
        "    name for name in sys.modules\n"
        "    if name == 'labs' or name.startswith('labs.')\n"
        ")\n"
        "print(','.join(lab_modules))"
    )
    result = _run_import_subprocess(root, code)
    lab_modules = [name for name in result.stdout.strip().split(",") if name]
    return {
        "check_id": "package_import_surface",
        "ok": result.returncode == 0 and not lab_modules,
        "evidence": {
            "import_targets": REQUIRED_IMPORT_TARGETS,
            "returncode": result.returncode,
            "stderr": result.stderr.strip(),
            "lab_modules_loaded": lab_modules,
        },
    }


def check_import_side_effects(root: Path) -> dict:
    packages_before = _snapshot(root / "packages")
    data_before = _snapshot(root / "data")
    result = _run_import_subprocess(
        root, "import " + ", ".join(REQUIRED_IMPORT_TARGETS)
    )
    new_package_files = sorted(_snapshot(root / "packages") - packages_before)
    new_data_files = sorted(_snapshot(root / "data") - data_before)
    return {
        "check_id": "import_writes_no_stage0_artifacts",
        "ok": (
            result.returncode == 0
            and not new_package_files
            and not new_data_files
        ),
        "evidence": {
            "returncode": result.returncode,
            "new_package_files": new_package_files,
            "new_data_files": new_data_files,
        },
    }


def check_lab_boundary(root: Path) -> dict:
    inspection = inspect_package_lab_boundary(root)
    return {
        "check_id": "no_lab_imports_or_sys_path_lab_bypass",
        "ok": (
            inspection["package_root_exists"]
            and not inspection["lab_import_files"]
            and not inspection["sys_path_lab_files"]
        ),
        "evidence": inspection,
    }


def promoted_modules(root: Path) -> list[str]:
    """Modules promoted past the scaffold step.

    A module counts as promoted once its package contract test exists
    (packages/mecha_engine/tests/test_<module>_contract.py), per the
    per-module contract gates in the contract traceability matrix. The
    scaffold-stage placeholder-only rule keeps applying to everything else.
    """
    tests_dir = root / "packages/mecha_engine/tests"
    return [
        module
        for module in PACKAGE_MODULES
        if (tests_dir / f"test_{module}_contract.py").exists()
    ]


def check_placeholder_only(root: Path) -> dict:
    # Scaffold-stage negative check: "no copied lab implementation" applies
    # to the scaffold step only (scaffold verification gate, "Expected
    # scaffold-stage result"). Modules promoted through their own contract
    # gate carry implementation legitimately, so the placeholder-only scan
    # covers only the unpromoted package source.
    src_root = root / "packages/mecha_engine/src/mecha_engine"
    promoted = promoted_modules(root)
    implementation_files = []
    promoted_implementation_files = []
    if src_root.exists():
        for path in sorted(src_root.rglob("*.py")):
            if not _TOP_LEVEL_IMPLEMENTATION.search(
                path.read_text(encoding="utf-8")
            ):
                continue
            relative = path.relative_to(root).as_posix()
            module_parts = path.relative_to(src_root).parts
            if module_parts[0] in promoted:
                promoted_implementation_files.append(relative)
            else:
                implementation_files.append(relative)
    return {
        "check_id": "no_copied_lab_implementation",
        "ok": src_root.exists() and not implementation_files,
        "evidence": {
            "src_root_exists": src_root.exists(),
            "promoted_modules": promoted,
            "promoted_implementation_files": promoted_implementation_files,
            "implementation_files": implementation_files,
        },
    }


def check_deferred_modules_absent(root: Path) -> dict:
    present = [
        module
        for module in DEFERRED_MODULES
        if (root / "packages/mecha_engine/src/mecha_engine" / module).exists()
    ]
    return {
        "check_id": "deferred_modules_absent",
        "ok": not present,
        "evidence": {
            "deferred_modules": DEFERRED_MODULES,
            "present_deferred_modules": present,
        },
    }


def check_import_test_suite(root: Path) -> dict:
    result = subprocess.run(
        [
            sys.executable,
            "-B",
            "-m",
            "unittest",
            "discover",
            "-s",
            str(root / "packages/mecha_engine/tests"),
            "-p",
            "test_*.py",
        ],
        capture_output=True,
        text=True,
        cwd=root,
        timeout=300,
    )
    ran_match = re.search(r"Ran (\d+) tests?", result.stderr)
    return {
        "check_id": "package_import_test_suite_passes",
        "ok": result.returncode == 0,
        "evidence": {
            "returncode": result.returncode,
            "tests_run": int(ran_match.group(1)) if ran_match else 0,
        },
    }


def check_promotion_gate_rerun(root: Path) -> dict:
    artifact_path = (
        root / "data/package_promotion/mecha_engine_package_promotion_gate_stage0.json"
    )
    summary = {}
    if artifact_path.exists():
        summary = json.loads(artifact_path.read_text(encoding="utf-8")).get(
            "summary", {}
        )
    rerun_after_scaffold = bool(summary.get("package_root_exists"))
    return {
        "check_id": "package_promotion_gate_rerun_after_scaffold",
        "ok": rerun_after_scaffold,
        "evidence": {
            "artifact_exists": artifact_path.exists(),
            "summary_package_root_exists": summary.get("package_root_exists"),
            "promotion_ready_count": summary.get("promotion_ready_count"),
        },
    }


def build_scaffold_verification_report(root: Path | None = None) -> dict:
    root = (Path(root) if root is not None else REPO_ROOT).resolve()
    checks = [
        check_required_paths(root),
        check_pyproject_metadata(root),
        check_import_surface(root),
        check_import_side_effects(root),
        check_lab_boundary(root),
        check_placeholder_only(root),
        check_deferred_modules_absent(root),
        check_import_test_suite(root),
        check_promotion_gate_rerun(root),
    ]
    checks_by_id = {check["check_id"]: check for check in checks}
    gate_passed = all(check["ok"] for check in checks)
    promoted = promoted_modules(root)
    unpromoted = [module for module in PACKAGE_MODULES if module not in promoted]
    import_surface_accepted = (
        checks_by_id["package_import_surface"]["ok"]
        and checks_by_id["package_import_test_suite_passes"]["ok"]
    )
    metrics = {
        "checks_total": len(checks),
        "checks_passed": sum(1 for check in checks if check["ok"]),
        "required_path_count": len(REQUIRED_SCAFFOLD_PATHS),
        "missing_required_paths": len(
            checks_by_id["required_scaffold_paths_present"]["evidence"][
                "missing_paths"
            ]
        ),
        "import_target_count": len(REQUIRED_IMPORT_TARGETS),
        "lab_import_files": len(
            checks_by_id["no_lab_imports_or_sys_path_lab_bypass"]["evidence"][
                "lab_import_files"
            ]
        ),
        "sys_path_lab_files": len(
            checks_by_id["no_lab_imports_or_sys_path_lab_bypass"]["evidence"][
                "sys_path_lab_files"
            ]
        ),
        "implementation_files": len(
            checks_by_id["no_copied_lab_implementation"]["evidence"][
                "implementation_files"
            ]
        ),
        "deferred_modules_present": len(
            checks_by_id["deferred_modules_absent"]["evidence"][
                "present_deferred_modules"
            ]
        ),
        "import_suite_tests_run": checks_by_id["package_import_test_suite_passes"][
            "evidence"
        ]["tests_run"],
        "promoted_module_count": len(promoted),
    }
    return {
        "artifact_id": ARTIFACT_ID,
        "date": "2026-07-08",
        "status": (
            "package_scaffold_verification_failed"
            if not gate_passed
            else (
                "package_scaffold_verification_executed_promoted_modules_present"
                if promoted
                else "package_scaffold_verification_executed_no_lab_code_promoted"
            )
        ),
        "purpose": (
            "Execute the scaffold verification checklist against the real "
            "packages/mecha_engine scaffold: verify the package boundary "
            "with the DR 0028 license declaration and without unpromoted "
            "implementation or deferred modules; modules that passed their "
            "own contract gate are recorded as promoted instead of failing "
            "the scaffold rule."
        ),
        "target_package_root": "packages/mecha_engine",
        "package_root_exists": (root / "packages" / "mecha_engine").exists(),
        "promoted_modules": promoted,
        "unpromoted_modules": unpromoted,
        "gate_passed": gate_passed,
        "import_surface_accepted": import_surface_accepted,
        "required_scaffold_paths": REQUIRED_SCAFFOLD_PATHS,
        "required_pyproject_fields": [
            "build-system",
            "project",
            "project.name = mecha-engine",
            "project.version",
            "project.requires-python",
            'project.license = "Apache-2.0" (DR 0028)',
            'project.license-files = ["../../LICENSE"] (DR 0028)',
        ],
        "required_import_targets": REQUIRED_IMPORT_TARGETS,
        "checks": checks,
        "metrics": metrics,
        "closed_states": (
            [
                "package_scaffold_created",
                "scaffold_required_paths_present",
                "package_metadata_boundary_accepted",
                "license_declared_apache_2_0",
                "package_import_surface_accepted",
                "import_side_effect_free",
                "lab_boundary_negative_checks_rejected",
                (
                    "scaffold_placeholder_only_outside_promoted_modules"
                    if promoted
                    else "scaffold_placeholder_only"
                ),
                *(
                    [f"module_{module}_promoted_with_contract_tests" for module in promoted]
                ),
                "deferred_modules_absent",
                "package_promotion_gate_rerun_after_scaffold",
            ]
            if gate_passed
            else ["scaffold_verification_executed"]
        ),
        "blocked_states": [
            (
                "unpromoted_package_module_implementations"
                if promoted
                else "package_module_implementations"
            ),
            "deferred_module_render_rejected_until_consumer",
            "lab_code_promotion",
            "package_dependencies_empty_until_a_capability_needs_one",
        ],
        "decision": (
            "reject_package_scaffold"
            if not gate_passed
            else (
                "accept_package_scaffold_with_promoted_modules"
                if promoted
                else "accept_empty_package_scaffold"
            )
        ),
        "next_research_step": (
            (
                "Continue the contract-gate order with the unpromoted modules "
                f"({', '.join(unpromoted)}), rerunning the package-promotion "
                "gate as each surface lands."
            )
            if promoted
            else (
                "Start the genome contract surface first: package-level tests per "
                "research/package_specs/mecha_engine_genome_contract_gate.md, then "
                "generation, lifecycle, archive, and provenance, rerunning the "
                "package-promotion gate as each surface lands."
            )
        ),
        "limitations": [
            "This gate verifies the scaffold boundary only; module contracts are proven by each module's own package contract tests, which this gate records as promotion evidence without re-proving them.",
            "It does not promote lab code or authorize deferred modules.",
            "License metadata is required to match DR 0028 (Apache-2.0 via the root LICENSE); the original prohibition closed with that record.",
            "Import checks run through the src layout via subprocess PYTHONPATH, matching the documented editable-install surface without requiring installation.",
        ],
        "source_artifacts": SOURCE_ARTIFACTS,
        "external_references": EXTERNAL_REFERENCES,
    }


def write_scaffold_verification_artifacts(output_dir: Path, report: dict) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    (output_dir / f"{ARTIFACT_ID}.json").write_text(
        json.dumps(report, indent=2) + "\n",
        encoding="utf-8",
    )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=REPO_ROOT)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    args = parser.parse_args()
    report = build_scaffold_verification_report(args.root)
    write_scaffold_verification_artifacts(args.output_dir, report)
    print(json.dumps(report["metrics"], indent=2))
    print(json.dumps({"gate_passed": report["gate_passed"], "decision": report["decision"]}, indent=2))


if __name__ == "__main__":
    main()
