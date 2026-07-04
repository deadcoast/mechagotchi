import argparse
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


SCHEMA_PATH = ROOT / "research/slip/slip.schema.json"
VALID_PALETTES = {
    "lcd_green",
    "gameboy_gray",
    "amber_terminal",
    "crt_blue",
    "pocket_plum",
}
ORGAN_ROLES = {"sensor", "expression", "body_core"}
TOP_LEVEL_KEYS = {
    "slip_version",
    "profile_id",
    "name",
    "grid",
    "mutation",
    "behavior",
    "survival_weights",
}
GRID_KEYS = {
    "allowed_palettes",
    "body_mass_min",
    "body_mass_max",
    "required_organ_roles",
}
MUTATION_KEYS = {
    "cell_mutation_rate_max",
    "organ_shift_rate_max",
    "palette_shift_rate_max",
    "symmetry_break_rate_max",
}
BEHAVIOR_KEYS = {"curiosity", "neediness", "sleepiness"}
SURVIVAL_KEYS = {"stability", "novelty", "bond"}


def validate_profile_file(path: Path) -> dict:
    return validate_profile(json.loads(path.read_text(encoding="utf-8")), source_path=path)


def validate_profile(profile: dict, source_path: Path | None = None) -> dict:
    errors: list[dict] = []
    _validate_object(profile, [], TOP_LEVEL_KEYS, TOP_LEVEL_KEYS, errors)
    if not isinstance(profile, dict):
        return _result(source_path, errors)

    _validate_const(profile.get("slip_version"), "0.1.0", ["slip_version"], errors)
    _validate_string(profile.get("profile_id"), ["profile_id"], errors, pattern="profile_id")
    _validate_string(profile.get("name"), ["name"], errors)

    grid = profile.get("grid")
    _validate_object(grid, ["grid"], GRID_KEYS, GRID_KEYS, errors)
    if isinstance(grid, dict):
        _validate_string_array(
            grid.get("allowed_palettes"),
            ["grid", "allowed_palettes"],
            VALID_PALETTES,
            errors,
        )
        _validate_integer(grid.get("body_mass_min"), ["grid", "body_mass_min"], errors, minimum=1)
        _validate_integer(grid.get("body_mass_max"), ["grid", "body_mass_max"], errors, minimum=1)
        _validate_string_array(
            grid.get("required_organ_roles"),
            ["grid", "required_organ_roles"],
            ORGAN_ROLES,
            errors,
        )
        if (
            isinstance(grid.get("body_mass_min"), int)
            and not isinstance(grid.get("body_mass_min"), bool)
            and isinstance(grid.get("body_mass_max"), int)
            and not isinstance(grid.get("body_mass_max"), bool)
            and grid["body_mass_max"] < grid["body_mass_min"]
        ):
            _add(
                errors,
                "semantic_body_mass_bounds",
                ["grid", "body_mass_max"],
                "grid.body_mass_max must be greater than or equal to grid.body_mass_min",
            )

    mutation = profile.get("mutation")
    _validate_object(mutation, ["mutation"], MUTATION_KEYS, MUTATION_KEYS, errors)
    if isinstance(mutation, dict):
        for key in sorted(MUTATION_KEYS):
            _validate_unit_interval(mutation.get(key), ["mutation", key], errors)

    behavior = profile.get("behavior")
    _validate_object(behavior, ["behavior"], BEHAVIOR_KEYS, BEHAVIOR_KEYS, errors)
    if isinstance(behavior, dict):
        for key in sorted(BEHAVIOR_KEYS):
            _validate_unit_interval(behavior.get(key), ["behavior", key], errors)

    survival = profile.get("survival_weights")
    _validate_object(survival, ["survival_weights"], SURVIVAL_KEYS, SURVIVAL_KEYS, errors)
    if isinstance(survival, dict):
        for key in sorted(SURVIVAL_KEYS):
            _validate_unit_interval(survival.get(key), ["survival_weights", key], errors)

    return _result(source_path, errors)


def validate_profile_corpus(
    valid_paths: list[Path],
    failure_paths: list[Path],
    example_paths: list[Path] | None = None,
) -> dict:
    example_paths = example_paths or []
    valid_results = [validate_profile_file(path) for path in valid_paths]
    failure_results = [validate_profile_file(path) for path in failure_paths]
    example_results = [validate_profile_file(path) for path in example_paths]
    unexpected_rejections = [
        result["source_path"] for result in valid_results if not result["ok"]
    ]
    unexpected_acceptances = [
        result["source_path"] for result in failure_results if result["ok"]
    ]
    unexpected_example_rejections = [
        result["source_path"] for result in example_results if not result["ok"]
    ]
    observed_families = sorted(
        {
            family
            for result in valid_results + failure_results + example_results
            for family in result["error_families"]
        }
    )
    return {
        "artifact_id": "slip_schema_validation_stage0",
        "status": "research_slip_schema_failure_corpus_no_package_code",
        "schema_path": SCHEMA_PATH.relative_to(ROOT).as_posix(),
        "schema_dialect": "https://json-schema.org/draft/2020-12/schema",
        "schema_engine": "dependency_free_stage0_structural_validator",
        "jsonschema_dependency_available": False,
        "valid_profile_count": len(valid_paths),
        "failure_case_count": len(failure_paths),
        "example_profile_count": len(example_paths),
        "accepted_valid_profiles": sum(1 for result in valid_results if result["ok"]),
        "rejected_failure_cases": sum(1 for result in failure_results if not result["ok"]),
        "accepted_example_profiles": sum(1 for result in example_results if result["ok"]),
        "unexpected_rejections": unexpected_rejections,
        "unexpected_acceptances": unexpected_acceptances,
        "unexpected_example_rejections": unexpected_example_rejections,
        "observed_error_families": observed_families,
        "valid_results": valid_results,
        "failure_results": failure_results,
        "example_results": example_results,
        "related_pydantic_contract_report": "data/slips/slip_pydantic_contract_stage0.json",
        "related_migration_dependency_report": "data/slips/slip_schema_migration_dependency_gate_stage0.json",
        "blocked_states": [
            "jsonschema_runtime_dependency_selection",
            "pydantic_package_dependency_declaration",
            "behavior_preview",
            "mutation_preview_ui",
        ],
    }


def write_report(path: Path, report: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")


def _validate_object(
    value: object,
    path: list[str],
    required: set[str],
    allowed: set[str],
    errors: list[dict],
) -> None:
    if not isinstance(value, dict):
        _add(errors, "schema_type", path, f"{_path(path)} must be an object")
        return
    missing = sorted(required - set(value))
    for key in missing:
        _add(errors, "schema_required", path + [key], f"{_path(path + [key])} is required")
    extras = sorted(set(value) - allowed)
    for key in extras:
        _add(
            errors,
            "schema_additional_properties",
            path + [key],
            f"{_path(path + [key])} is not allowed",
        )


def _validate_const(value: object, expected: object, path: list[str], errors: list[dict]) -> None:
    if value != expected:
        _add(errors, "schema_enum", path, f"{_path(path)} must equal {expected!r}")


def _validate_string(
    value: object,
    path: list[str],
    errors: list[dict],
    *,
    pattern: str | None = None,
) -> None:
    if not isinstance(value, str):
        _add(errors, "schema_type", path, f"{_path(path)} must be a string")
        return
    if not value:
        _add(errors, "schema_min_length", path, f"{_path(path)} must not be empty")
    if pattern == "profile_id" and not all(
        char.islower() or char.isdigit() or char == "_" for char in value
    ):
        _add(
            errors,
            "schema_pattern",
            path,
            f"{_path(path)} must contain only lowercase letters, digits, and underscores",
        )


def _validate_string_array(
    value: object,
    path: list[str],
    allowed_values: set[str],
    errors: list[dict],
) -> None:
    if not isinstance(value, list):
        _add(errors, "schema_type", path, f"{_path(path)} must be an array")
        return
    if not value:
        _add(errors, "schema_min_items", path, f"{_path(path)} must not be empty")
    seen = set()
    for index, item in enumerate(value):
        item_path = path + [str(index)]
        if not isinstance(item, str):
            _add(errors, "schema_type", item_path, f"{_path(item_path)} must be a string")
            continue
        if item in seen:
            _add(errors, "schema_unique_items", item_path, f"{_path(item_path)} is duplicated")
        seen.add(item)
        if item not in allowed_values:
            _add(errors, "schema_enum", item_path, f"{_path(item_path)} is unknown: {item}")


def _validate_integer(
    value: object,
    path: list[str],
    errors: list[dict],
    *,
    minimum: int,
) -> None:
    if isinstance(value, bool) or not isinstance(value, int):
        family = "semantic_numeric_bool" if isinstance(value, bool) else "schema_type"
        _add(errors, family, path, f"{_path(path)} must be an integer")
        return
    if value < minimum:
        _add(errors, "schema_range", path, f"{_path(path)} must be >= {minimum}")


def _validate_unit_interval(value: object, path: list[str], errors: list[dict]) -> None:
    if isinstance(value, bool):
        _add(errors, "semantic_numeric_bool", path, f"{_path(path)} must be a number, not bool")
        return
    if not isinstance(value, int | float):
        _add(errors, "schema_type", path, f"{_path(path)} must be a number")
        return
    if value < 0 or value > 1:
        _add(errors, "schema_range", path, f"{_path(path)} must be in [0, 1]")


def _portable(path: Path) -> str:
    try:
        return path.relative_to(ROOT).as_posix()
    except ValueError:
        return path.as_posix()


def _result(source_path: Path | None, errors: list[dict]) -> dict:
    return {
        "source_path": _portable(Path(source_path)) if source_path else None,
        "ok": not errors,
        "errors": errors,
        "error_families": sorted({error["family"] for error in errors}),
    }


def _add(errors: list[dict], family: str, path: list[str], message: str) -> None:
    errors.append({"family": family, "path": _path(path), "message": message})


def _path(path: list[str]) -> str:
    return ".".join(path) if path else "$"


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--valid-dir", type=Path, default=ROOT / "data/slips/valid")
    parser.add_argument("--failure-dir", type=Path, default=ROOT / "data/slips/failure_cases")
    parser.add_argument(
        "--examples-dir",
        type=Path,
        default=ROOT / "research/slip/slip_examples",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=ROOT / "data/slips/slip_schema_validation_stage0.json",
    )
    args = parser.parse_args()

    report = validate_profile_corpus(
        sorted(args.valid_dir.glob("*.json")),
        sorted(args.failure_dir.glob("*.json")),
        sorted(args.examples_dir.glob("*.json")) if args.examples_dir.exists() else [],
    )
    write_report(args.output, report)
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
