from dataclasses import dataclass


# Mirrors the palette enum in research/slip/slip.schema.json (and the literal
# set in labs/slip_validator/slip_validator.py). Previously imported from
# corpus_builder.PALETTES, which coupled contract validation to the corpus
# generator (review finding L-05); the cross-validator agreement test in
# test_slip_constraints.py pins this set against the authoritative validator.
VALID_PALETTES = {
    "lcd_green",
    "gameboy_gray",
    "amber_terminal",
    "crt_blue",
    "pocket_plum",
}

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
ORGAN_ROLES = {"sensor", "expression", "body_core"}


@dataclass(frozen=True)
class SlipResult:
    ok: bool
    errors: list[str]


def validate_slip(profile: dict) -> SlipResult:
    errors: list[str] = []
    if not isinstance(profile, dict):
        return SlipResult(False, ["profile must be an object"])
    _require_exact_keys(profile, TOP_LEVEL_KEYS, "profile", errors)

    if profile.get("slip_version") != "0.1.0":
        errors.append("slip_version must be 0.1.0")
    _require_string(profile, "profile_id", errors)
    _require_string(profile, "name", errors)
    profile_id = profile.get("profile_id")
    if isinstance(profile_id, str) and not all(
        char.islower() or char.isdigit() or char == "_" for char in profile_id
    ):
        errors.append(
            "profile_id must contain only lowercase letters, digits, and underscores"
        )

    grid = profile.get("grid")
    if not isinstance(grid, dict):
        errors.append("grid must be an object")
        grid = {}
    else:
        _require_exact_keys(grid, GRID_KEYS, "grid", errors)

    _validate_enum_array(
        grid.get("allowed_palettes"),
        VALID_PALETTES,
        "grid allowed_palettes",
        "grid allowed palette",
        errors,
    )

    min_mass = grid.get("body_mass_min")
    max_mass = grid.get("body_mass_max")
    if (
        isinstance(min_mass, bool)
        or isinstance(max_mass, bool)
        or not isinstance(min_mass, int)
        or not isinstance(max_mass, int)
    ):
        errors.append("grid body mass bounds must be integers")
    elif min_mass < 1 or max_mass < min_mass:
        errors.append(f"grid body mass bounds invalid: {min_mass}..{max_mass}")

    _validate_enum_array(
        grid.get("required_organ_roles"),
        ORGAN_ROLES,
        "grid required_organ_roles",
        "grid required organ role",
        errors,
    )

    for section_name, required_keys in [
        ("behavior", BEHAVIOR_KEYS),
        ("survival_weights", SURVIVAL_KEYS),
    ]:
        section = profile.get(section_name, {})
        if not isinstance(section, dict):
            errors.append(f"{section_name} must be an object")
            continue
        _require_exact_keys(section, required_keys, section_name, errors)
        for key in sorted(required_keys):
            if key in section:
                _validate_unit_interval(section[key], f"{section_name} {key}", errors)

    mutation = profile.get("mutation", {})
    if not isinstance(mutation, dict):
        errors.append("mutation must be an object")
        mutation = {}
    else:
        _require_exact_keys(mutation, MUTATION_KEYS, "mutation", errors)
    for key in sorted(MUTATION_KEYS):
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
    if not isinstance(mutation_values, dict):
        errors.append("grid mutation must be an object")
        mutation_values = {}
    field_map = {
        "cell_mutation_rate": "cell_mutation_rate_max",
        "organ_shift_rate": "organ_shift_rate_max",
        "palette_shift_rate": "palette_shift_rate_max",
        "symmetry_break_rate": "symmetry_break_rate_max",
    }
    for grid_key, limit_key in field_map.items():
        value = mutation_values.get(grid_key)
        limit = mutation_limits[limit_key]
        if isinstance(value, bool) or not isinstance(value, int | float):
            errors.append(f"mutation {grid_key} must be a number: {value}")
        elif value > limit:
            errors.append(f"mutation {grid_key} exceeds SLIP max {limit}: {value}")

    return SlipResult(not errors, errors)


def _require_exact_keys(
    value: dict,
    required: set[str],
    name: str,
    errors: list[str],
) -> None:
    for key in sorted(required - set(value)):
        errors.append(f"{name} {key} is required")
    for key in sorted(set(value) - required):
        errors.append(f"{name} {key} is not allowed")


def _require_string(profile: dict, key: str, errors: list[str]) -> None:
    if not isinstance(profile.get(key), str) or not profile.get(key):
        errors.append(f"{key} must be a non-empty string")


def _validate_enum_array(
    value: object,
    allowed_values: set[str],
    array_name: str,
    item_name: str,
    errors: list[str],
) -> None:
    if not isinstance(value, list) or not value:
        errors.append(f"{array_name} must be a non-empty array")
        return
    seen: set[object] = set()
    for item in value:
        if not isinstance(item, str):
            errors.append(f"{item_name} must be a string: {item}")
            continue
        if item in seen:
            errors.append(f"{item_name} is duplicated: {item}")
        seen.add(item)
        if item not in allowed_values:
            errors.append(f"{item_name} is unknown: {item}")


def _validate_unit_interval(value: object, name: str, errors: list[str]) -> None:
    if not isinstance(value, int | float) or isinstance(value, bool):
        errors.append(f"{name} must be a number")
        return
    if value < 0 or value > 1:
        errors.append(f"{name} outside 0..1: {value}")
