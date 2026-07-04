import argparse
import json
import re
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]

ARTIFACT_ID = "mecha_engine_runtime_boundary_gate_stage0"
STATUS = "research_runtime_boundary_gate_no_package_code"
REPORT_PATH = Path("data/architecture/mecha_engine_runtime_boundary_gate_stage0.json")
DEFAULT_OUTPUT_DIR = Path("data/architecture/mecha_engine_runtime_boundary_gate_stage0")


SOURCE_ARTIFACTS = [
    "docs/01-brainstorming.md",
    "docs/02-research_plan.md",
    "research/decision_records/0004-mecha-engine-package-scaffold.md",
    "research/package_specs/mecha_engine_module_interfaces.md",
    "research/package_specs/mecha_engine_lifecycle_contract_gate.md",
    "research/package_specs/mecha_engine_archive_contract_gate.md",
    "research/package_specs/mecha_engine_contract_traceability_matrix.md",
    "research/package_specs/mecha_engine_formal_invariant_dependency_gate.md",
    "research/package_specs/mecha_engine_runtime_boundary_gate.md",
    "research/experiment_reports/2026-05-13-mecha-engine-runtime-boundary-gate.md",
    "research/slip/profile_compatibility_tests.md",
    "data/slips/slip_profile_compatibility_matrix_stage0.json",
    "data/readability/slip_readability_calibration_gate_stage0.json",
    "data/package_promotion/mecha_engine_package_promotion_gate_stage0.json",
    "data/workshop_editor/slip_runtime_selection_policy_stage0.json",
    "data/workshop_editor/slip_offspring_lineage_gate_stage0.json",
    "data/workshop_editor/slip_long_horizon_behavior_gate_stage0.json",
    "data/workshop_editor/slip_multigeneration_lineage_runner_stage0.json",
]


EXTERNAL_ANCHORS = [
    {
        "source": "Python Packaging User Guide - src layout vs flat layout",
        "url": "https://packaging.python.org/en/latest/discussions/src-layout-vs-flat-layout/",
        "used_for": (
            "Package runtime imports must be exercised through an installed "
            "src-layout import surface, not repository-root lab imports."
        ),
    },
    {
        "source": "Python Packaging User Guide - Writing your pyproject.toml",
        "url": "https://packaging.python.org/en/latest/guides/writing-pyproject-toml/",
        "used_for": (
            "The future package dependency and metadata boundary belongs in "
            "pyproject.toml, not in a research artifact."
        ),
    },
    {
        "source": "JSON Schema Draft 2020-12",
        "url": "https://json-schema.org/draft/2020-12",
        "used_for": (
            "Runtime SLIP/profile schema validation remains blocked until a "
            "package dependency policy chooses and declares a validator."
        ),
    },
]


def build_runtime_boundary_contracts(root: Path) -> list[dict]:
    source_presence = _source_presence(root)
    return [
        {
            "contract_id": "package_import_boundary",
            "runtime_surface": "mecha_engine package import surface",
            "package_target": "packages/mecha_engine/src/mecha_engine",
            "source_artifacts": [
                "research/decision_records/0004-mecha-engine-package-scaffold.md",
                "research/package_specs/mecha_engine_contract_traceability_matrix.md",
                "research/package_specs/mecha_engine_formal_invariant_dependency_gate.md",
            ],
            "required_runtime_inputs": [
                "installed mecha_engine import package",
                "pyproject.toml dependency and metadata boundary",
                "package tests that import mecha_engine directly",
            ],
            "required_runtime_outputs": [
                "importable mecha_engine package",
                "no import-time Stage 0 artifact writes",
                "no copied lab implementation during scaffold creation",
            ],
            "forbidden_dependencies": [
                "labs",
                "sys.path lab adapters",
                "research artifact writers",
            ],
            "blocked_until": [
                "packages/mecha_engine exists",
                "scaffold verification gate passes through package imports",
                "package-promotion gate reruns after scaffold exists",
            ],
            "evidence_present": _all_present(source_presence, [
                "research/decision_records/0004-mecha-engine-package-scaffold.md",
                "research/package_specs/mecha_engine_contract_traceability_matrix.md",
                "research/package_specs/mecha_engine_formal_invariant_dependency_gate.md",
            ]),
        },
        {
            "contract_id": "lifecycle_runtime_boundary",
            "runtime_surface": "mecha_engine.lifecycle",
            "package_target": "packages/mecha_engine/src/mecha_engine/lifecycle",
            "source_artifacts": [
                "research/package_specs/mecha_engine_lifecycle_contract_gate.md",
                "data/workshop_editor/slip_runtime_selection_policy_stage0.json",
                "data/workshop_editor/slip_long_horizon_behavior_gate_stage0.json",
                "data/workshop_editor/slip_multigeneration_lineage_runner_stage0.json",
            ],
            "required_runtime_inputs": [
                "package-validated grid genome",
                "package-validated SLIP profile when supplied",
                "policy or action stream",
                "tick horizon and reproducibility seed",
            ],
            "required_runtime_outputs": [
                "bounded episode summary",
                "per-tick history",
                "explicit death cause on terminal state",
                "no online learner memory writes",
            ],
            "forbidden_dependencies": [
                "labs",
                "workshop_editor selector internals",
                "readability proxy threshold lock",
            ],
            "blocked_until": [
                "package genome validator exists",
                "package lifecycle module exists",
                "package tests reject invalid grids before simulation",
                "manual readability calibration is available before evolution claims",
            ],
            "evidence_present": _all_present(source_presence, [
                "research/package_specs/mecha_engine_lifecycle_contract_gate.md",
                "data/workshop_editor/slip_runtime_selection_policy_stage0.json",
                "data/workshop_editor/slip_long_horizon_behavior_gate_stage0.json",
                "data/workshop_editor/slip_multigeneration_lineage_runner_stage0.json",
            ]),
        },
        {
            "contract_id": "slip_profile_runtime_validation_boundary",
            "runtime_surface": "future mecha_engine SLIP/profile validation surface",
            "package_target": "deferred packages/mecha_engine/src/mecha_engine/slip",
            "source_artifacts": [
                "research/slip/profile_compatibility_tests.md",
                "data/slips/slip_profile_compatibility_matrix_stage0.json",
                "research/slip/schema_migration_dependency_gate.md",
                "data/slips/slip_schema_migration_dependency_gate_stage0.json",
            ],
            "required_runtime_inputs": [
                "declared JSON Schema runtime validator dependency",
                "declared Pydantic package dependency policy if retained",
                "versioned SLIP profile payload",
            ],
            "required_runtime_outputs": [
                "runtime schema validation result",
                "migration or explicit rejection for unsupported versions",
                "profile/grid alignment result",
            ],
            "forbidden_dependencies": [
                "labs",
                "dependency-free lab validator as runtime proof",
                "undeclared package dependencies",
            ],
            "blocked_until": [
                "runtime JSON Schema dependency is selected and declared",
                "Pydantic package dependency decision exists",
                "package import-surface tests cover SLIP validation",
            ],
            "evidence_present": _all_present(source_presence, [
                "research/slip/profile_compatibility_tests.md",
                "data/slips/slip_profile_compatibility_matrix_stage0.json",
                "research/slip/schema_migration_dependency_gate.md",
                "data/slips/slip_schema_migration_dependency_gate_stage0.json",
            ]),
        },
        {
            "contract_id": "archive_readability_boundary",
            "runtime_surface": "mecha_engine.archive readability-aware descriptor use",
            "package_target": "packages/mecha_engine/src/mecha_engine/archive",
            "source_artifacts": [
                "research/package_specs/mecha_engine_archive_contract_gate.md",
                "research/experiment_reports/2026-05-13-slip-readability-calibration-gate.md",
                "data/readability/slip_readability_calibration_gate_stage0.json",
            ],
            "required_runtime_inputs": [
                "package-validated candidate grid",
                "lifecycle episode summary",
                "manual-readability calibration status",
                "profile alignment result when profile-weighted descriptors are used",
            ],
            "required_runtime_outputs": [
                "descriptor metadata",
                "bounded fitness components",
                "explicit readability calibration status",
                "blocked descriptor threshold lock when ratings are absent",
            ],
            "forbidden_dependencies": [
                "labs",
                "proxy readability as human calibration",
                "scalar top-k replacement for archive behavior",
            ],
            "blocked_until": [
                "63 completed SLIP readability reviewer rows exist",
                "inter-reviewer agreement and proxy-human correlation pass",
                "package archive tests preserve calibration status",
            ],
            "evidence_present": _all_present(source_presence, [
                "research/package_specs/mecha_engine_archive_contract_gate.md",
                "research/experiment_reports/2026-05-13-slip-readability-calibration-gate.md",
                "data/readability/slip_readability_calibration_gate_stage0.json",
            ]),
        },
        {
            "contract_id": "lineage_runtime_state_boundary",
            "runtime_surface": "future package lineage/runtime state persistence",
            "package_target": "deferred package runtime state surface",
            "source_artifacts": [
                "research/slip/profile_compatibility_tests.md",
                "research/experiment_reports/2026-05-13-slip-multigeneration-lineage-runner.md",
                "data/workshop_editor/slip_multigeneration_lineage_runner_stage0.json",
            ],
            "required_runtime_inputs": [
                "package-selected parent candidate",
                "package-generated offspring candidate",
                "package lifecycle and archive decision records",
            ],
            "required_runtime_outputs": [
                "persistent lineage state with parent links",
                "archive action trace",
                "explicit lab-only boundary if package runtime state is absent",
            ],
            "forbidden_dependencies": [
                "labs",
                "workshop_editor lineage runner as runtime state",
                "unbounded generation without package validation",
            ],
            "blocked_until": [
                "package lifecycle/archive modules exist",
                "runtime state persistence contract is defined",
                "manual readability calibration is available before evolution claims",
            ],
            "evidence_present": _all_present(source_presence, [
                "research/slip/profile_compatibility_tests.md",
                "research/experiment_reports/2026-05-13-slip-multigeneration-lineage-runner.md",
                "data/workshop_editor/slip_multigeneration_lineage_runner_stage0.json",
            ]),
        },
    ]


def evaluate_runtime_boundary_gate(root: Path) -> dict:
    root = root.resolve()
    package_root_exists = (root / "packages" / "mecha_engine").exists()
    package_directory_exists = (root / "packages").exists()
    readability = _read_json(root / "data/readability/slip_readability_calibration_gate_stage0.json")
    profile_matrix = _read_json(root / "data/slips/slip_profile_compatibility_matrix_stage0.json")
    promotion = _read_json(root / "data/package_promotion/mecha_engine_package_promotion_gate_stage0.json")
    contracts = build_runtime_boundary_contracts(root)
    manual_readability_ready = bool(readability.get("manual_readability_calibration_ready"))
    package_runtime_ready = package_root_exists and _package_contracts_promotable(contracts)
    profile_weighted_ready = package_runtime_ready and manual_readability_ready
    negative_probes = _negative_probes(
        root=root,
        package_root_exists=package_root_exists,
        manual_readability_ready=manual_readability_ready,
        package_runtime_ready=package_runtime_ready,
        dependency_manifest_exists=False,
    )
    rejected_probe_count = sum(
        1 for probe in negative_probes if probe["result"] == "rejected"
    )
    lab_boundary_probe_ids = {
        "package_runtime_imports_labs",
        "package_test_mutates_sys_path_to_lab",
    }
    lab_import_probes_rejected = all(
        probe["result"] == "rejected"
        for probe in negative_probes
        if probe["probe_id"] in lab_boundary_probe_ids
    )
    metrics = {
        "contract_count": len(contracts),
        "contracts_with_source_evidence": sum(
            1 for contract in contracts if contract["evidence_present"]
        ),
        "package_directory_exists": package_directory_exists,
        "package_root_exists": package_root_exists,
        "manual_readability_rating_rows": _metric(
            readability,
            ["metrics", "rating_row_count"],
            0,
        ),
        "expected_manual_readability_rows": readability.get(
            "expected_completed_rating_rows",
            0,
        ),
        "manual_readability_calibration_ready": manual_readability_ready,
        "package_runtime_integration_ready": package_runtime_ready,
        "profile_weighted_evolution_ready": profile_weighted_ready,
        "negative_probe_count": len(negative_probes),
        "negative_probe_rejected_count": rejected_probe_count,
        "promotion_ready_contracts": 0 if not package_runtime_ready else len(contracts),
        "package_promotion_ready_count": _metric(
            promotion,
            ["summary", "promotion_ready_count"],
            0,
        ),
        "slip_blocked_state_count": len(profile_matrix.get("blocked_states", [])),
    }
    return {
        "artifact_id": ARTIFACT_ID,
        "status": STATUS,
        "date": "2026-05-13",
        "purpose": (
            "Integrate the current package/runtime lifecycle boundary research "
            "without creating packages, moving lab code, fabricating readability "
            "ratings, or claiming profile-weighted evolution."
        ),
        "package_root": "packages/mecha_engine",
        "package_root_exists": package_root_exists,
        "package_runtime_integration_ready": package_runtime_ready,
        "manual_readability_calibration_ready": manual_readability_ready,
        "profile_weighted_evolution_ready": profile_weighted_ready,
        "source_artifacts": SOURCE_ARTIFACTS,
        "external_anchors": EXTERNAL_ANCHORS,
        "runtime_boundary_contracts": contracts,
        "negative_probes": negative_probes,
        "metrics": metrics,
        "closed_states": [
            "package_runtime_boundary_contracts_defined",
            *(
                ["lab_import_negative_probe_rejected"]
                if lab_import_probes_rejected
                else []
            ),
            "premature_profile_weighted_evolution_claim_rejected",
            "manual_readability_row_requirement_preserved",
        ],
        "blocked_states": [
            "runtime_jsonschema_validation",
            "declared_pydantic_package_dependency",
            "package_runtime_lifecycle_integration",
            "manual_readability_calibration",
            "profile_weighted_evolution",
            "package_import_surface_tests",
            "package_promotion",
        ],
        "decision": "adopt_runtime_boundary_gate_research_only",
        "next_research_step": (
            "Keep package/runtime lifecycle integration blocked until package "
            "implementation is explicitly started; collect 63 SLIP readability "
            "reviewer rows before claiming profile-weighted evolution."
        ),
        "limitations": [
            "This gate does not create packages/ or packages/mecha_engine.",
            "This gate does not run future package tests because no package surface exists.",
            "This gate rejects lab imports as package runtime evidence.",
            "This gate does not fabricate or infer human readability ratings.",
        ],
    }


def write_runtime_boundary_gate_artifacts(output_dir: Path, report: dict) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    _write_json(output_dir / f"{ARTIFACT_ID}.json", report)
    (output_dir / "README.md").write_text(_readme_text(report), encoding="utf-8")


_LAB_IMPORT_PATTERN = re.compile(r"^\s*(?:from|import)\s+labs\b", re.MULTILINE)
_LAB_PATH_REFERENCE_PATTERN = re.compile(r"labs[/\\.]|[\"']labs[\"']")


def inspect_package_lab_boundary(root: Path | None = None) -> dict:
    """Scan any packages/ root for lab imports and sys.path lab adapters.

    Returns real inspection evidence instead of assuming the boundary holds:
    when no packages/ root exists the boundary holds vacuously, and that is
    derived from repository state, not hardcoded.
    """
    root = (Path(root) if root is not None else REPO_ROOT).resolve()
    package_root = root / "packages"
    package_root_exists = package_root.exists()
    files_scanned = 0
    lab_import_files: list[str] = []
    sys_path_lab_files: list[str] = []
    if package_root_exists:
        for path in sorted(package_root.rglob("*.py")):
            if not path.is_file():
                continue
            files_scanned += 1
            try:
                text = path.read_text(encoding="utf-8")
            except (OSError, UnicodeDecodeError):
                continue
            relative = path.relative_to(package_root).as_posix()
            if _LAB_IMPORT_PATTERN.search(text):
                lab_import_files.append(relative)
            if any(
                "sys.path" in line and _LAB_PATH_REFERENCE_PATTERN.search(line)
                for line in text.splitlines()
            ):
                sys_path_lab_files.append(relative)
    return {
        "package_root_exists": package_root_exists,
        "files_scanned": files_scanned,
        "lab_import_files": lab_import_files,
        "sys_path_lab_files": sys_path_lab_files,
    }


def build_lab_boundary_probes(root: Path | None = None) -> list[dict]:
    """Build the two lab-boundary negative probes from inspected repo state.

    A probe is "rejected" when the forbidden pattern is absent from the
    scanned packages/ tree (or the tree does not exist, so the boundary holds
    vacuously). A probe is "accepted" when the inspection actually found the
    forbidden pattern, which breaks the closed boundary state.
    """
    inspection = inspect_package_lab_boundary(root)
    lab_import_violation = bool(inspection["lab_import_files"])
    sys_path_violation = bool(inspection["sys_path_lab_files"])
    return [
        _probe(
            "package_runtime_imports_labs",
            accepted=lab_import_violation,
            reasons=(
                ["lab_import_violation_present"]
                if lab_import_violation
                else ["forbidden_lab_dependency"]
            ),
            evidence={
                "package_root_exists": inspection["package_root_exists"],
                "files_scanned": inspection["files_scanned"],
                "lab_import_files": inspection["lab_import_files"],
                "policy": (
                    "Future package runtime code must import mecha_engine modules, "
                    "not labs/* research modules."
                ),
            },
        ),
        _probe(
            "package_test_mutates_sys_path_to_lab",
            accepted=sys_path_violation,
            reasons=(
                ["sys_path_lab_mutation_present"]
                if sys_path_violation
                else ["forbidden_sys_path_lab_access"]
            ),
            evidence={
                "package_root_exists": inspection["package_root_exists"],
                "files_scanned": inspection["files_scanned"],
                "sys_path_lab_files": inspection["sys_path_lab_files"],
                "policy": (
                    "Future package tests must exercise the package import surface "
                    "without sys.path adapters to lab directories."
                ),
            },
        ),
    ]


def _negative_probes(
    *,
    root: Path | None = None,
    package_root_exists: bool,
    manual_readability_ready: bool,
    package_runtime_ready: bool,
    dependency_manifest_exists: bool,
) -> list[dict]:
    return [
        *build_lab_boundary_probes(root),
        _probe(
            "claim_profile_weighted_evolution",
            accepted=package_runtime_ready and manual_readability_ready,
            reasons=_claim_reasons(package_runtime_ready, manual_readability_ready),
            evidence=(
                "Stage 0 selectors, offspring gates, long-horizon probes, and "
                "multigeneration lineage runs are lab artifacts until package "
                "runtime integration and manual readability calibration exist."
            ),
        ),
        _probe(
            "declare_runtime_schema_validation_ready",
            accepted=dependency_manifest_exists,
            reasons=[] if dependency_manifest_exists else ["dependency_manifest_absent"],
            evidence=(
                "Runtime JSON Schema validation requires a declared package "
                "dependency policy in the future package metadata boundary."
            ),
        ),
        _probe(
            "package_promotion_without_package_root",
            accepted=package_root_exists,
            reasons=[] if package_root_exists else ["package_root_absent"],
            evidence=(
                "The package-promotion gate reports zero promotion-ready "
                "candidates while packages/mecha_engine is absent."
            ),
        ),
    ]


def _probe(probe_id: str, *, accepted: bool, reasons: list[str], evidence: object) -> dict:
    return {
        "probe_id": probe_id,
        "accepted": accepted,
        "result": "accepted" if accepted else "rejected",
        "reasons": reasons,
        "evidence": evidence,
    }


def _claim_reasons(package_runtime_ready: bool, manual_readability_ready: bool) -> list[str]:
    reasons = []
    if not package_runtime_ready:
        reasons.append("package_runtime_lifecycle_integration_absent")
    if not manual_readability_ready:
        reasons.append("manual_readability_calibration_absent")
    return reasons


def _package_contracts_promotable(contracts: list[dict]) -> bool:
    return bool(contracts) and all(contract["evidence_present"] for contract in contracts)


def _source_presence(root: Path) -> dict[str, bool]:
    candidates = set(SOURCE_ARTIFACTS)
    candidates.update(
        {
            "research/slip/schema_migration_dependency_gate.md",
            "data/slips/slip_schema_migration_dependency_gate_stage0.json",
            "research/experiment_reports/2026-05-13-slip-readability-calibration-gate.md",
            "research/experiment_reports/2026-05-13-slip-multigeneration-lineage-runner.md",
        }
    )
    return {path: (root / path).exists() for path in sorted(candidates)}


def _all_present(source_presence: dict[str, bool], paths: list[str]) -> bool:
    return all(source_presence.get(path, False) for path in paths)


def _metric(payload: dict, path: list[str], default: object) -> object:
    cursor = payload
    for key in path:
        if not isinstance(cursor, dict) or key not in cursor:
            return default
        cursor = cursor[key]
    return cursor


def _read_json(path: Path) -> dict:
    if not path.exists():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


def _write_json(path: Path, payload: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")


def _readme_text(report: dict) -> str:
    metrics = report["metrics"]
    return (
        "# Mecha Engine Runtime Boundary Gate Stage 0\n\n"
        "Package/runtime lifecycle boundary evidence for the current research state.\n\n"
        "Key results:\n\n"
        f"- Contracts: {metrics['contract_count']}\n"
        f"- Package root exists: {metrics['package_root_exists']}\n"
        f"- Package runtime integration ready: {metrics['package_runtime_integration_ready']}\n"
        f"- Manual readability calibration ready: {metrics['manual_readability_calibration_ready']}\n"
        f"- Profile-weighted evolution ready: {metrics['profile_weighted_evolution_ready']}\n"
        f"- Negative probes rejected: {metrics['negative_probe_rejected_count']} / {metrics['negative_probe_count']}\n"
        f"- Decision: {report['decision']}\n\n"
        "This is not package runtime integration, package promotion, or "
        "profile-weighted evolution. It is a boundary gate that preserves the "
        "blocked states until package implementation and human readability "
        "calibration exist.\n"
    )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=Path("."))
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    parser.add_argument("--report-path", type=Path, default=REPORT_PATH)
    args = parser.parse_args()

    report = evaluate_runtime_boundary_gate(args.root)
    _write_json(args.report_path, report)
    write_runtime_boundary_gate_artifacts(args.output_dir, report)
    print(json.dumps(report["metrics"], indent=2))


if __name__ == "__main__":
    main()
