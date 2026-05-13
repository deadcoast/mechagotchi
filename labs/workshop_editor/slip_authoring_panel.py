import argparse
import json
import sys
from copy import deepcopy
from pathlib import Path


SLIP_VALIDATOR_DIR = Path(__file__).resolve().parents[1] / "slip_validator"
if str(SLIP_VALIDATOR_DIR) not in sys.path:
    sys.path.insert(0, str(SLIP_VALIDATOR_DIR))

from pydantic_contract import _validate_payload
from schema_migration_gate import (
    CURRENT_SLIP_VERSION,
    build_schema_migration_dependency_report,
    evaluate_migration_request,
)
from slip_validator import validate_profile


REPORT_PATH = Path("data/workshop_editor/slip_authoring_panel_stage0.json")
AUTHORING_DATA_PATH = Path("data/workshop_editor/slip_authoring_panel_data.js")


def build_authoring_state(profile: dict) -> dict:
    migration_report = build_schema_migration_dependency_report()
    comparison = migration_report["schema_surface_comparison"]
    profile_copy = deepcopy(profile)
    return {
        "panel_id": "slip_authoring_panel_stage0",
        "status": "research_slip_authoring_panel_no_package_code",
        "profile": profile_copy,
        "surfaces": [
            "profile_metadata_form",
            "grid_constraint_controls",
            "mutation_cap_sliders",
            "behavior_weight_sliders",
            "survival_weight_sliders",
            "schema_validation_panel",
            "migration_gate_panel",
            "json_profile_export_panel",
        ],
        "schema_constraints": {
            "slip_version": CURRENT_SLIP_VERSION,
            "profile_id_pattern": "^[a-z0-9_]+$",
            "profile_id_min_length": 1,
            "name_min_length": 1,
            "palette_values": comparison["palette_values"],
            "organ_roles": comparison["organ_roles"],
            "body_mass_minimum": 1,
            "unit_interval": {"minimum": 0, "maximum": 1},
            "mutation_required": comparison["mutation_required"],
            "behavior_required": comparison["behavior_required"],
            "survival_required": comparison["survival_required"],
            "additional_properties": "forbid",
        },
        "migration_gate": {
            "supported_versions": migration_report["supported_versions"],
            "current_version_action": migration_report["migration_policy"][
                "current_version_action"
            ],
            "missing_version_action": migration_report["migration_policy"][
                "missing_version_action"
            ],
            "typed_version_action": migration_report["migration_policy"][
                "typed_version_action"
            ],
            "unknown_version_action": migration_report["migration_policy"][
                "unknown_version_action"
            ],
        },
        "dependency_contracts": {
            "dependency_manifest_present": migration_report[
                "dependency_manifest_present"
            ],
            "pydantic_available": migration_report["pydantic_available"],
            "pydantic_version": migration_report["pydantic_version"],
            "jsonschema_available": migration_report["jsonschema_available"],
            "jsonschema_version": migration_report["jsonschema_version"],
            "runtime_jsonschema_policy": migration_report["dependency_decision"][
                "jsonschema"
            ],
        },
        "validation": validate_authoring_draft(profile_copy),
    }


def apply_authoring_patch(state: dict, patch: dict) -> dict:
    draft = deepcopy(state["profile"])
    for field_path, value in patch.items():
        _assign_path(draft, field_path, value)
    validation = validate_authoring_draft(draft)
    return {
        "ok": validation["ok"],
        "draft": draft,
        "patch": deepcopy(patch),
        "validation": validation,
        "errors": validation["errors"],
    }


def validate_authoring_draft(profile: dict) -> dict:
    migration = evaluate_migration_request(profile)
    dependency_free = validate_profile(profile)
    pydantic = _validate_payload("authoring_draft", profile)
    errors = (
        _normalize_migration_errors(migration)
        + _tagged_errors("dependency_free", dependency_free["errors"])
        + _tagged_errors("pydantic", pydantic["errors"])
    )
    return {
        "ok": migration["ok"] and dependency_free["ok"] and pydantic["ok"],
        "migration": migration,
        "dependency_free": dependency_free,
        "pydantic": pydantic,
        "errors": errors,
        "error_families": sorted({error["family"] for error in errors}),
    }


def run_slip_authoring_panel_lab(profile_paths: list[Path]) -> dict:
    states = [
        build_authoring_state(_read_json(path)) | {"profile_path": _portable(path)}
        for path in profile_paths
    ]
    valid_drafts = [
        apply_authoring_patch(
            state,
            {
                "name": f"{state['profile']['name']} Authoring Draft",
                "behavior.curiosity": min(
                    1.0,
                    round(state["profile"]["behavior"]["curiosity"] + 0.05, 4),
                ),
            },
        )
        for state in states
    ]
    invalid_probes = [
        apply_authoring_patch(states[0], {"slip_version": "0.2.0"}),
        apply_authoring_patch(states[0], {"grid.allowed_palettes": ["unknown_palette"]}),
        apply_authoring_patch(states[0], {"mutation.cell_mutation_rate_max": 1.4}),
    ]
    valid_draft_count = sum(1 for result in valid_drafts if result["ok"])
    invalid_rejected_count = sum(1 for result in invalid_probes if not result["ok"])
    return {
        "artifact_id": "slip_authoring_panel_stage0",
        "status": "research_slip_authoring_panel_no_package_code",
        "date": "2026-05-12",
        "purpose": (
            "Prove a minimal workshop SLIP authoring panel can draft current "
            "0.1.0 profiles against the Stage 0 schema, Pydantic contract, "
            "and migration policy without package code."
        ),
        "source_artifacts": [
            "docs/01-brainstorming.md",
            "docs/02-research_plan.md",
            "research/slip/slip.schema.json",
            "research/slip/slip_pydantic_model.schema.json",
            "data/slips/slip_schema_validation_stage0.json",
            "data/slips/slip_pydantic_contract_stage0.json",
            "data/slips/slip_schema_migration_dependency_gate_stage0.json",
            "labs/workshop_editor/index.html",
            "labs/workshop_editor/app.js",
            "labs/workshop_editor/styles.css",
        ],
        "external_anchors": [
            {
                "source": "MDN FormData",
                "url": "https://developer.mozilla.org/docs/Web/API/FormData",
                "used_for": "Static browser form draft extraction.",
            },
            {
                "source": "MDN input element constraint validation",
                "url": "https://developer.mozilla.org/en-US/docs/Web/HTML/Element/input",
                "used_for": "Browser min/max/required profile control constraints.",
            },
        ],
        "profile_count": len(states),
        "valid_draft_count": valid_draft_count,
        "invalid_probe_count": len(invalid_probes),
        "invalid_probe_rejected_count": invalid_rejected_count,
        "metrics": {
            "profile_authoring_success_rate": _ratio(valid_draft_count, len(valid_drafts)),
            "invalid_probe_rejection_rate": _ratio(
                invalid_rejected_count,
                len(invalid_probes),
            ),
            "dependency_free_valid_draft_acceptance": sum(
                1 for result in valid_drafts if result["validation"]["dependency_free"]["ok"]
            ),
            "pydantic_valid_draft_acceptance": sum(
                1 for result in valid_drafts if result["validation"]["pydantic"]["ok"]
            ),
            "migration_valid_draft_acceptance": sum(
                1 for result in valid_drafts if result["validation"]["migration"]["ok"]
            ),
        },
        "authoring_states": states,
        "valid_draft_results": [_compact_authoring_result(result) for result in valid_drafts],
        "invalid_probe_results": [
            _compact_authoring_result(result) for result in invalid_probes
        ],
        "closed_states": [
            "minimal_profile_authoring_panel",
            "current_profile_draft_validation",
            "schema_migration_gate_consumed_by_authoring",
            "pydantic_contract_consumed_by_authoring",
        ],
        "blocked_states": [
            "runtime_jsonschema_validation",
            "declared_dependency_manifest",
            "profile_weighted_evolution",
            "package_runtime_lifecycle_integration",
            "real_image_project_decoder",
            "embedded_native_metadata_writer",
            "profile_authoring_usability_pilot",
        ],
        "decision": "prototype_minimal_slip_authoring_panel",
        "next_research_step": (
            "Run a usability pilot for the profile-authoring panel, then "
            "run held-out long-horizon behavior tests and manual readability "
            "calibration before claiming profile-weighted evolution."
        ),
    }


def write_slip_authoring_panel_artifacts(output_dir: Path, report: dict) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    _write_json(output_dir / "slip_authoring_panel_stage0.json", report)
    for state in report["authoring_states"]:
        profile_id = state["profile"]["profile_id"]
        _write_json(output_dir / f"{profile_id}_authoring_state.json", state)
    (output_dir / "README.md").write_text(
        _readme_text(report),
        encoding="utf-8",
    )
    (output_dir / "slip_authoring_panel_data.js").write_text(
        "window.MECHAGOTCHI_SLIP_AUTHORING_PANEL = "
        + json.dumps(_app_payload(report), indent=2)
        + ";\n",
        encoding="utf-8",
    )


def _assign_path(draft: dict, field_path: str, value: object) -> None:
    parts = field_path.split(".")
    cursor = draft
    for part in parts[:-1]:
        if part not in cursor or not isinstance(cursor[part], dict):
            cursor[part] = {}
        cursor = cursor[part]
    cursor[parts[-1]] = deepcopy(value)


def _normalize_migration_errors(result: dict) -> list[dict]:
    errors = []
    for error in result.get("errors", []):
        errors.append(
            {
                "source": "migration",
                "family": error["family"],
                "path": "slip_version",
                "message": error["message"],
            }
        )
    return errors


def _tagged_errors(source: str, errors: list[dict]) -> list[dict]:
    return [
        {
            "source": source,
            "family": error["family"],
            "path": error.get("path", "$"),
            "message": error["message"],
        }
        for error in errors
    ]


def _compact_authoring_result(result: dict) -> dict:
    return {
        "ok": result["ok"],
        "profile_id": result["draft"].get("profile_id"),
        "slip_version": result["draft"].get("slip_version"),
        "patch": result["patch"],
        "error_families": result["validation"]["error_families"],
        "dependency_free_ok": result["validation"]["dependency_free"]["ok"],
        "pydantic_ok": result["validation"]["pydantic"]["ok"],
        "migration_ok": result["validation"]["migration"]["ok"],
    }


def _app_payload(report: dict) -> dict:
    return {
        "report": {
            key: report[key]
            for key in [
                "artifact_id",
                "status",
                "profile_count",
                "valid_draft_count",
                "invalid_probe_count",
                "invalid_probe_rejected_count",
                "metrics",
                "closed_states",
                "blocked_states",
                "decision",
            ]
        },
        "authoring_states": report["authoring_states"],
    }


def _readme_text(report: dict) -> str:
    metrics = report["metrics"]
    return (
        "# SLIP Authoring Panel Stage 0\n\n"
        "Minimal workshop SLIP profile-authoring panel evidence for the "
        "current Stage 0 profile schema.\n\n"
        f"- Profiles: {report['profile_count']}\n"
        f"- Valid drafts accepted: {report['valid_draft_count']}\n"
        f"- Invalid probes rejected: {report['invalid_probe_rejected_count']}"
        f"/{report['invalid_probe_count']}\n"
        "- Profile authoring success rate: "
        f"{metrics['profile_authoring_success_rate']}\n"
        "- Invalid probe rejection rate: "
        f"{metrics['invalid_probe_rejection_rate']}\n"
        f"- Decision: {report['decision']}\n"
    )


def _read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def _write_json(path: Path, payload: dict) -> None:
    path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")


def _portable(path: Path) -> str:
    return str(path).replace("\\", "/")


def _ratio(numerator: int, denominator: int) -> float:
    if denominator == 0:
        return 0.0
    return round(numerator / denominator, 6)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path("data/workshop_editor/slip_authoring_panel_stage0"),
    )
    parser.add_argument("--profile", type=Path, action="append")
    args = parser.parse_args()

    profile_paths = args.profile or [
        Path("data/slips/valid/slip_lcd_seed.json"),
        Path("data/slips/valid/slip_gray_stable.json"),
        Path("data/slips/valid/slip_amber_social.json"),
    ]
    report = run_slip_authoring_panel_lab(profile_paths)
    write_slip_authoring_panel_artifacts(args.output_dir, report)
    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    _write_json(REPORT_PATH, report)
    AUTHORING_DATA_PATH.write_text(
        "window.MECHAGOTCHI_SLIP_AUTHORING_PANEL = "
        + json.dumps(_app_payload(report), indent=2)
        + ";\n",
        encoding="utf-8",
    )
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
