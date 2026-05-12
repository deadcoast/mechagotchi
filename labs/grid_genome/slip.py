from dataclasses import dataclass

from corpus_builder import PALETTES


@dataclass(frozen=True)
class SlipResult:
    ok: bool
    errors: list[str]


def validate_slip(profile: dict) -> SlipResult:
    errors: list[str] = []
    if profile.get("slip_version") != "0.1.0":
        errors.append("slip_version must be 0.1.0")
    _require_string(profile, "profile_id", errors)
    _require_string(profile, "name", errors)

    grid = profile.get("grid")
    if not isinstance(grid, dict):
        errors.append("grid must be an object")
        grid = {}

    allowed_palettes = grid.get("allowed_palettes")
    if not isinstance(allowed_palettes, list) or not allowed_palettes:
        errors.append("grid allowed_palettes must be a non-empty array")
    else:
        for palette in allowed_palettes:
            if palette not in PALETTES:
                errors.append(f"grid allowed palette is unknown: {palette}")

    min_mass = grid.get("body_mass_min")
    max_mass = grid.get("body_mass_max")
    if not isinstance(min_mass, int) or not isinstance(max_mass, int):
        errors.append("grid body mass bounds must be integers")
    elif min_mass < 1 or max_mass < min_mass:
        errors.append(f"grid body mass bounds invalid: {min_mass}..{max_mass}")

    required_roles = grid.get("required_organ_roles")
    if not isinstance(required_roles, list) or not required_roles:
        errors.append("grid required_organ_roles must be a non-empty array")
    else:
        for role in required_roles:
            if role not in {"sensor", "expression", "body_core"}:
                errors.append(f"grid required organ role is unknown: {role}")

    for section_name in ["behavior", "survival_weights"]:
        section = profile.get(section_name, {})
        if not isinstance(section, dict):
            errors.append(f"{section_name} must be an object")
            continue
        for key, value in section.items():
            _validate_unit_interval(value, f"{section_name} {key}", errors)

    mutation = profile.get("mutation", {})
    if not isinstance(mutation, dict):
        errors.append("mutation must be an object")
        mutation = {}
    for key in [
        "cell_mutation_rate_max",
        "organ_shift_rate_max",
        "palette_shift_rate_max",
        "symmetry_break_rate_max",
    ]:
        _validate_unit_interval(mutation.get(key), f"mutation {key}", errors)

    return SlipResult(not errors, errors)


def is_grid_aligned(grid: dict, profile: dict) -> SlipResult:
    errors = validate_slip(profile).errors
    if errors:
        return SlipResult(False, errors)

    grid_rules = profile["grid"]
    palette_id = grid.get("palette", {}).get("palette_id")
    if palette_id not in grid_rules["allowed_palettes"]:
        errors.append(f"palette {palette_id} not allowed by SLIP")

    body_mass = sum(1 for cell in grid.get("cells", []) if cell.get("organ") == "core")
    if body_mass < grid_rules["body_mass_min"] or body_mass > grid_rules["body_mass_max"]:
        errors.append(
            "body mass "
            f"{body_mass} outside SLIP bounds "
            f"{grid_rules['body_mass_min']}..{grid_rules['body_mass_max']}"
        )

    present_roles = {
        organ.get("role") for organ in grid.get("organs", {}).values() if isinstance(organ, dict)
    }
    for role in grid_rules["required_organ_roles"]:
        if role not in present_roles:
            errors.append(f"required organ role missing for SLIP: {role}")

    mutation_limits = profile["mutation"]
    mutation_values = grid.get("mutation", {})
    field_map = {
        "cell_mutation_rate": "cell_mutation_rate_max",
        "organ_shift_rate": "organ_shift_rate_max",
        "palette_shift_rate": "palette_shift_rate_max",
        "symmetry_break_rate": "symmetry_break_rate_max",
    }
    for grid_key, limit_key in field_map.items():
        value = mutation_values.get(grid_key)
        limit = mutation_limits[limit_key]
        if value is None or value > limit:
            errors.append(f"mutation {grid_key} exceeds SLIP max {limit}: {value}")

    return SlipResult(not errors, errors)


def _require_string(profile: dict, key: str, errors: list[str]) -> None:
    if not isinstance(profile.get(key), str) or not profile.get(key):
        errors.append(f"{key} must be a non-empty string")


def _validate_unit_interval(value: object, name: str, errors: list[str]) -> None:
    if not isinstance(value, int | float) or isinstance(value, bool):
        errors.append(f"{name} must be a number")
        return
    if value < 0 or value > 1:
        errors.append(f"{name} outside 0..1: {value}")
