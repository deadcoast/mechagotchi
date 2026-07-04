import importlib.metadata
import importlib.util
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


CURRENT_SLIP_VERSION = "0.1.0"
AUTHORED_SCHEMA_PATH = ROOT / "research/slip/slip.schema.json"
PYDANTIC_SCHEMA_PATH = ROOT / "research/slip/slip_pydantic_model.schema.json"
REPORT_PATH = ROOT / "data/slips/slip_schema_migration_dependency_gate_stage0.json"


def build_schema_migration_dependency_report() -> dict:
    comparison = compare_schema_surfaces()
    migration_probes = [
        evaluate_migration_request({"slip_version": CURRENT_SLIP_VERSION}),
        evaluate_migration_request({}),
        evaluate_migration_request({"slip_version": 0.1}),
        evaluate_migration_request({"slip_version": "0.2.0"}),
    ]
    return {
        "artifact_id": "slip_schema_migration_dependency_gate_stage0",
        "status": "research_slip_schema_migration_dependency_gate_no_package_code",
        "current_slip_version": CURRENT_SLIP_VERSION,
        "supported_versions": [CURRENT_SLIP_VERSION],
        "authored_schema_path": AUTHORED_SCHEMA_PATH.relative_to(ROOT).as_posix(),
        "pydantic_schema_path": PYDANTIC_SCHEMA_PATH.relative_to(ROOT).as_posix(),
        "package_root_exists": (ROOT / "packages").exists(),
        "dependency_manifest_present": _dependency_manifest_present(),
        "dependency_manifest_path": "pyproject.toml",
        "dependency_group": "lab",
        "pydantic_available": _module_available("pydantic"),
        "pydantic_version": _module_version("pydantic"),
        "jsonschema_available": _module_available("jsonschema"),
        "jsonschema_version": _module_version("jsonschema"),
        "dependency_decision": {
            "pydantic": "declared_in_lab_dependency_group_for_lab_contract",
            "jsonschema": (
                "declared_in_lab_dependency_group_runtime_validation_proven_by_parity_lab"
            ),
            "decision_record": "research/decision_records/0005-declare-lab-dependency-manifest.md",
        },
        "schema_surface_comparison": comparison,
        "migration_policy": {
            "current_version_action": "accept_current_no_migration",
            "missing_version_action": "reject_before_validation",
            "typed_version_action": "reject_before_validation",
            "unknown_version_action": "reject_before_validation",
            "implicit_upgrade": "forbidden",
            "implicit_downgrade": "forbidden",
            "lossy_migration": "forbidden",
            "migration_requires": [
                "new schema id",
                "explicit source version",
                "explicit target version",
                "fixture corpus for source and target",
                "round-trip or one-way loss report",
                "validator parity report",
            ],
        },
        "migration_probes": migration_probes,
        "closed_states": [
            "schema_surface_parity_between_authored_and_pydantic_schema",
            "schema_migration_policy",
            "declared_dependency_manifest",
            "lab_runtime_jsonschema_validation",
        ],
        "blocked_states": [
            "package_runtime_jsonschema_validation",
            "package_import_surface",
            "behavior_preview",
            "mutation_preview_ui",
            "profile_weighted_evolution",
            "profile_authoring_usability_pilot",
        ],
    }


def compare_schema_surfaces() -> dict:
    authored = _read_json(AUTHORED_SCHEMA_PATH)
    pydantic = _read_json(PYDANTIC_SCHEMA_PATH)
    authored_surface = _authored_surface(authored)
    pydantic_surface = _pydantic_surface(pydantic)
    mismatches = []
    for key in sorted(authored_surface):
        if authored_surface[key] != pydantic_surface.get(key):
            mismatches.append(
                {
                    "field": key,
                    "authored": authored_surface[key],
                    "pydantic": pydantic_surface.get(key),
                }
            )
    return {
        "mismatches": mismatches,
        "top_level_required": authored_surface["top_level_required"],
        "palette_values": authored_surface["palette_values"],
        "organ_roles": authored_surface["organ_roles"],
        "behavior_required": authored_surface["behavior_required"],
        "survival_required": authored_surface["survival_required"],
        "mutation_required": authored_surface["mutation_required"],
        "extra_forbid": {
            "top_level": authored_surface["top_level_extra_forbid"],
            "grid": authored_surface["grid_extra_forbid"],
            "mutation": authored_surface["mutation_extra_forbid"],
            "behavior": authored_surface["behavior_extra_forbid"],
            "survival_weights": authored_surface["survival_extra_forbid"],
        },
    }


def evaluate_migration_request(profile: dict) -> dict:
    if not isinstance(profile, dict):
        return _migration_result(
            ok=False,
            source_version=None,
            target_version=None,
            action="reject_before_validation",
            family="schema_profile_type",
            message="SLIP profile payload must be an object",
        )
    if "slip_version" not in profile:
        return _migration_result(
            ok=False,
            source_version=None,
            target_version=None,
            action="reject_before_validation",
            family="schema_version_missing",
            message="slip_version is required before validation or migration",
        )
    source_version = profile["slip_version"]
    if not isinstance(source_version, str):
        return _migration_result(
            ok=False,
            source_version=None,
            target_version=None,
            action="reject_before_validation",
            family="schema_version_type",
            message="slip_version must be a string before migration",
        )
    if source_version != CURRENT_SLIP_VERSION:
        return _migration_result(
            ok=False,
            source_version=source_version,
            target_version=None,
            action="reject_before_validation",
            family="schema_version_unsupported",
            message=f"unsupported SLIP version: {source_version}",
        )
    return {
        "ok": True,
        "source_version": source_version,
        "target_version": CURRENT_SLIP_VERSION,
        "action": "accept_current_no_migration",
        "errors": [],
    }


def write_schema_migration_dependency_report() -> dict:
    report = build_schema_migration_dependency_report()
    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    REPORT_PATH.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    return report


def _migration_result(
    *,
    ok: bool,
    source_version: str | None,
    target_version: str | None,
    action: str,
    family: str,
    message: str,
) -> dict:
    return {
        "ok": ok,
        "source_version": source_version,
        "target_version": target_version,
        "action": action,
        "errors": [{"family": family, "message": message}],
    }


def _authored_surface(schema: dict) -> dict:
    properties = schema["properties"]
    grid = properties["grid"]
    mutation = properties["mutation"]
    behavior = properties["behavior"]
    survival = properties["survival_weights"]
    return {
        "top_level_required": sorted(schema["required"]),
        "top_level_extra_forbid": schema.get("additionalProperties") is False,
        "grid_extra_forbid": grid.get("additionalProperties") is False,
        "mutation_extra_forbid": mutation.get("additionalProperties") is False,
        "behavior_extra_forbid": behavior.get("additionalProperties") is False,
        "survival_extra_forbid": survival.get("additionalProperties") is False,
        "palette_values": sorted(
            grid["properties"]["allowed_palettes"]["items"]["enum"]
        ),
        "organ_roles": sorted(
            grid["properties"]["required_organ_roles"]["items"]["enum"]
        ),
        "behavior_required": sorted(behavior["required"]),
        "survival_required": sorted(survival["required"]),
        "mutation_required": sorted(mutation["required"]),
    }


def _pydantic_surface(schema: dict) -> dict:
    defs = schema["$defs"]
    grid = defs["GridContract"]
    mutation = defs["MutationContract"]
    behavior = defs["BehaviorContract"]
    survival = defs["SurvivalWeightsContract"]
    return {
        "top_level_required": sorted(schema["required"]),
        "top_level_extra_forbid": schema.get("additionalProperties") is False,
        "grid_extra_forbid": grid.get("additionalProperties") is False,
        "mutation_extra_forbid": mutation.get("additionalProperties") is False,
        "behavior_extra_forbid": behavior.get("additionalProperties") is False,
        "survival_extra_forbid": survival.get("additionalProperties") is False,
        "palette_values": sorted(defs["PaletteId"]["enum"]),
        "organ_roles": sorted(defs["OrganRole"]["enum"]),
        "behavior_required": sorted(behavior["required"]),
        "survival_required": sorted(survival["required"]),
        "mutation_required": sorted(mutation["required"]),
    }


def _dependency_manifest_present() -> bool:
    manifest_names = {
        "pyproject.toml",
        "requirements.txt",
        "requirements-dev.txt",
        "setup.py",
        "setup.cfg",
        "Pipfile",
        "poetry.lock",
        "uv.lock",
    }
    return any((ROOT / name).exists() for name in manifest_names)


def _module_available(name: str) -> bool:
    return importlib.util.find_spec(name) is not None


def _module_version(name: str) -> str | None:
    if not _module_available(name):
        return None
    try:
        return importlib.metadata.version(name)
    except importlib.metadata.PackageNotFoundError:
        return "unknown"


def _read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def main() -> None:
    print(json.dumps(write_schema_migration_dependency_report(), indent=2))


if __name__ == "__main__":
    main()
