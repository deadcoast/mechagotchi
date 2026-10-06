"""mecha_engine.slip — the SLIP authority (decision record 0027).

The tenth promoted module: ONE in-package SLIP authority replacing the
four private ``_slip.py`` mirrors that ``generation``, ``lifecycle``,
``repair``, and ``runtime`` each carried (DR 0027's gate 1 measured the
mirrors behaviorally identical over 118 profiles x corruption cases and
104 profiles x 20 seeds before the collapse — zero divergences).

Contract sources:

- research/decision_records/0027-slip-module-disposition.md
- labs/grid_genome/slip.py (the Stage 0 lab authority, pinned by
  ``labs/grid_genome/test_package_slip_parity.py``)
- research/decision_records/0012/0013 (the schema ladder the fields
  implement)

``validate_slip`` judges a profile against the ratified schema
(v0.1 baseline + every v0.2 ladder rung: forbidden_traits,
risk_tolerances, learning_switches, lineage_preferences, species_class,
visual_grammar, deliberation, mechanics); ``is_grid_aligned`` judges a grid
against a profile (palettes, body mass, required organ roles, material
grammar). Pure stdlib; deterministic; inputs never mutated.
"""

from __future__ import annotations

from dataclasses import dataclass

# Mirrors the palette enum in research/slip/slip.schema.json.
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
# The SLIP schema extension ladder (decision record 0012): "0.1.0" is the
# frozen baseline the promoted modules consume; ladder fields are legal
# only under "0.2.0" and are all optional.
VALID_SLIP_VERSIONS = {"0.1.0", "0.2.0"}
LADDER_KEYS = {
    "forbidden_traits",
    "risk_tolerances",
    "learning_switches",
    "lineage_preferences",
    "species_class",
    "visual_grammar",
    "deliberation",
    "mechanics",
}
DELIBERATION_KEYS = {"max_ticks", "confidence_threshold"}
VISUAL_GRAMMAR_KEYS = {"allowed_materials", "animation_vocab"}
ANIMATION_VOCAB = ["idle", "blink", "sleep", "beg", "ill"]
PARENT_SELECTION_MODES = {"uniform", "fitness_weighted"}
LINEAGE_PREFERENCES_KEYS = {"parent_selection"}
RISK_TOLERANCES_KEYS = {"mutation"}
# Mirrors the switchboard thread registry (the lab authority's
# micro_switchboard.SWITCHBOARD_THREAD_NAMES; identical to the package's
# learning ``_switchboard`` registry), pinned by the lab-side parity test.
SWITCHBOARD_THREAD_NAMES = {
    "recent_interaction_ewma",
    "hidden_mood_estimator",
    "action_preference_bandit",
    "mutation_risk_scorer",
}
FORBIDDEN_TRAITS_KEYS = {"roles", "materials"}
# Mirrors of the grid genome schema's cell enums minus the empty values
# (empty/void cannot be forbidden); pinned against
# research/grid_genome/grid_genome.schema.json by the lab authority's test.
FORBIDDABLE_ROLES = {
    "body",
    "shell",
    "sensor",
    "eye",
    "mouth",
    "joint",
    "limb",
    "antenna",
    "decoration",
    "effect",
    "anchor",
}
FORBIDDABLE_MATERIALS = {"soft", "hard", "glass", "joint", "light", "signal"}
# A profile may not require an organ whose cell role it forbids.
ALLOWABLE_MATERIALS = {"void"} | set(FORBIDDABLE_MATERIALS)
CELL_ROLE_FOR_ORGAN_ROLE = {
    "sensor": "eye",
    "expression": "mouth",
    "body_core": "body",
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
# X8: optional permission vocabulary, separate from the frozen required roles.
ALLOWED_ORGAN_ROLES = ORGAN_ROLES | {"locomotion", "ornament", "effect"}


@dataclass(frozen=True)
class SlipResult:
    """Structured SLIP outcome: ok plus ordered error strings."""

    ok: bool
    errors: list[str]


def validate_slip(profile: dict) -> SlipResult:
    """Validate a SLIP profile dictionary without mutating it."""
    errors: list[str] = []
    if not isinstance(profile, dict):
        return SlipResult(False, ["profile must be an object"])
    version = profile.get("slip_version")
    ladder_present = sorted(set(profile) & LADDER_KEYS)
    base_keys = {
        key: value for key, value in profile.items() if key not in LADDER_KEYS
    }
    _require_exact_keys(base_keys, TOP_LEVEL_KEYS, "profile", errors)

    if version not in VALID_SLIP_VERSIONS:
        errors.append(
            "slip_version must be one of "
            + ", ".join(sorted(VALID_SLIP_VERSIONS))
        )
    elif ladder_present and version != "0.2.0":
        for key in ladder_present:
            errors.append(f"profile {key} requires slip_version 0.2.0")
    if "forbidden_traits" in profile:
        _validate_forbidden_traits(profile, errors)
    if "risk_tolerances" in profile:
        _validate_risk_tolerances(profile, errors)
    if "learning_switches" in profile:
        _validate_learning_switches(profile, errors)
    if "lineage_preferences" in profile:
        _validate_lineage_preferences(profile, errors)
    if "species_class" in profile:
        species = profile.get("species_class")
        if not isinstance(species, str) or not species or not all(
            ch.islower() or ch.isdigit() or ch == "_" for ch in species
        ):
            errors.append(
                "species_class must be a non-empty lowercase identifier"
            )
    if "visual_grammar" in profile:
        _validate_visual_grammar(profile, errors)
    if "deliberation" in profile:
        _validate_deliberation(profile, errors)
    if "mechanics" in profile:
        _validate_mechanics(profile, errors)
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
        _require_exact_keys({key: value for key, value in grid.items()
                             if key != "allowed_organ_roles"}, GRID_KEYS, "grid", errors)
        if "allowed_organ_roles" in grid:
            _validate_allowed_organ_roles(grid, version, errors)

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


# DR 0030: SLIP mass bounds are denominated at the 8x8 reference canvas.
SLIP_MASS_REFERENCE_AREA = 64


def _scaled_mass_bound(bound: int, grid: dict) -> int:
    grid_size = grid.get("grid_size")
    if (
        isinstance(grid_size, list)
        and len(grid_size) == 2
        and all(
            isinstance(dimension, int)
            and not isinstance(dimension, bool)
            and dimension > 0
            for dimension in grid_size
        )
    ):
        return (bound * grid_size[0] * grid_size[1]) // SLIP_MASS_REFERENCE_AREA
    return bound


def is_grid_aligned(grid: dict, profile: dict) -> SlipResult:
    """Check a grid genome against a SLIP profile's constraint surfaces."""
    errors = validate_slip(profile).errors
    if errors:
        return SlipResult(False, errors)

    grid_rules = profile["grid"]
    palette_id = grid.get("palette", {}).get("palette_id")
    if palette_id not in grid_rules["allowed_palettes"]:
        errors.append(f"palette {palette_id} not allowed by SLIP")

    body_mass = sum(1 for cell in grid.get("cells", []) if cell.get("organ") == "core")
    # DR 0030: mass bounds are denominated at the 8x8 reference canvas
    # and scale by area (an exact identity at 8x8, so every historical
    # verdict and error string is unchanged). The message reports the
    # EFFECTIVE bounds actually applied.
    min_mass = _scaled_mass_bound(grid_rules["body_mass_min"], grid)
    max_mass = _scaled_mass_bound(grid_rules["body_mass_max"], grid)
    if body_mass < min_mass or body_mass > max_mass:
        errors.append(
            "body mass "
            f"{body_mass} outside SLIP bounds "
            f"{min_mass}..{max_mass}"
        )

    if "allowed_organ_roles" in grid_rules:
        # Admission also visits structurally invalid founders. Optional role
        # permissions must refuse malformed roles without masking that receipt.
        present_roles = set()
        for organ in grid.get("organs", {}).values():
            if isinstance(organ, dict):
                role = organ.get("role")
                if isinstance(role, str):
                    present_roles.add(role)
                else:
                    errors.append(f"organ role must be a string for SLIP: {role!r}")
    else:
        present_roles = {
            organ.get("role") for organ in grid.get("organs", {}).values() if isinstance(organ, dict)
        }
    for role in grid_rules["required_organ_roles"]:
        if role not in present_roles:
            errors.append(f"required organ role missing for SLIP: {role}")

    if "allowed_organ_roles" in grid_rules:
        for role in sorted(present_roles - set(grid_rules["allowed_organ_roles"])):
            errors.append(f"organ role not allowed by SLIP: {role}")

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

    grammar = profile.get("visual_grammar") or {}
    allowed_materials = grammar.get("allowed_materials")
    if isinstance(allowed_materials, list) and allowed_materials:
        present = {cell.get("material") for cell in grid.get("cells", [])}
        for material in sorted(present - set(allowed_materials)):
            errors.append(
                f"material not allowed by SLIP visual grammar: {material}"
            )

    forbidden = profile.get("forbidden_traits") or {}
    forbidden_roles = set(forbidden.get("roles", []))
    forbidden_materials = set(forbidden.get("materials", []))
    if forbidden_roles or forbidden_materials:
        cells = grid.get("cells", [])
        for role in sorted(
            {cell.get("role") for cell in cells} & forbidden_roles
        ):
            errors.append(f"forbidden role present in grid: {role}")
        for material in sorted(
            {cell.get("material") for cell in cells} & forbidden_materials
        ):
            errors.append(f"forbidden material present in grid: {material}")

    return SlipResult(not errors, errors)


def _validate_mechanics(profile: dict, errors: list[str]) -> None:
    mechanics = profile["mechanics"]
    if not isinstance(mechanics, dict):
        errors.append("mechanics must be an object")
        return
    for key in sorted(set(mechanics) - {"cleanliness"}):
        errors.append(f"mechanics has unexpected key: {key}")
    if "cleanliness" in mechanics and not isinstance(mechanics["cleanliness"], bool):
        errors.append("mechanics cleanliness must be a boolean")


def _validate_deliberation(profile: dict, errors: list[str]) -> None:
    deliberation = profile.get("deliberation")
    if not isinstance(deliberation, dict):
        errors.append("deliberation must be an object")
        return
    _require_exact_keys(
        deliberation, DELIBERATION_KEYS, "deliberation", errors
    )
    ticks = deliberation.get("max_ticks")
    if "max_ticks" in deliberation and (
        isinstance(ticks, bool)
        or not isinstance(ticks, int)
        or not 2 <= ticks <= 8
    ):
        errors.append("deliberation max_ticks must be an integer in 2..8")
    if "confidence_threshold" in deliberation:
        _validate_unit_interval(
            deliberation["confidence_threshold"],
            "deliberation confidence_threshold",
            errors,
        )


def _validate_visual_grammar(profile: dict, errors: list[str]) -> None:
    grammar = profile.get("visual_grammar")
    if not isinstance(grammar, dict):
        errors.append("visual_grammar must be an object")
        return
    for key in sorted(set(grammar) - VISUAL_GRAMMAR_KEYS):
        errors.append(f"visual_grammar {key} is not allowed")
    if not set(grammar) & VISUAL_GRAMMAR_KEYS:
        errors.append(
            "visual_grammar must name allowed_materials and/or "
            "animation_vocab"
        )
    materials = grammar.get("allowed_materials")
    if "allowed_materials" in grammar:
        if not isinstance(materials, list) or not materials:
            errors.append(
                "visual_grammar allowed_materials must be a non-empty array"
            )
        else:
            for value in materials:
                if value not in ALLOWABLE_MATERIALS:
                    errors.append(
                        f"visual_grammar allowed material not in "
                        f"vocabulary: {value}"
                    )
    vocab = grammar.get("animation_vocab")
    if "animation_vocab" in grammar:
        if not isinstance(vocab, list) or not vocab:
            errors.append(
                "visual_grammar animation_vocab must be a non-empty array"
            )
        else:
            for value in vocab:
                if value not in ANIMATION_VOCAB:
                    errors.append(
                        f"visual_grammar animation state not in "
                        f"vocabulary: {value}"
                    )
            if "idle" not in vocab:
                errors.append(
                    "visual_grammar animation_vocab must include idle"
                )


def _validate_lineage_preferences(profile: dict, errors: list[str]) -> None:
    preferences = profile.get("lineage_preferences")
    if not isinstance(preferences, dict):
        errors.append("lineage_preferences must be an object")
        return
    _require_exact_keys(
        preferences, LINEAGE_PREFERENCES_KEYS, "lineage_preferences", errors
    )
    mode = preferences.get("parent_selection")
    if "parent_selection" in preferences and mode not in PARENT_SELECTION_MODES:
        errors.append(
            "lineage_preferences parent_selection must be one of "
            + ", ".join(sorted(PARENT_SELECTION_MODES))
        )


def _validate_learning_switches(profile: dict, errors: list[str]) -> None:
    switches = profile.get("learning_switches")
    if not isinstance(switches, dict) or not switches:
        errors.append(
            "learning_switches must be a non-empty object of thread switches"
        )
        return
    for name in sorted(set(switches) - SWITCHBOARD_THREAD_NAMES):
        errors.append(f"learning switch names an unknown thread: {name}")
    for name, value in sorted(switches.items()):
        if not isinstance(value, bool):
            errors.append(f"learning switch {name} must be a boolean")


def _validate_risk_tolerances(profile: dict, errors: list[str]) -> None:
    tolerances = profile.get("risk_tolerances")
    if not isinstance(tolerances, dict):
        errors.append("risk_tolerances must be an object")
        return
    _require_exact_keys(
        tolerances, RISK_TOLERANCES_KEYS, "risk_tolerances", errors
    )
    if "mutation" in tolerances:
        _validate_unit_interval(
            tolerances["mutation"], "risk_tolerances mutation", errors
        )


def _validate_forbidden_traits(profile: dict, errors: list[str]) -> None:
    traits = profile.get("forbidden_traits")
    if not isinstance(traits, dict):
        errors.append("forbidden_traits must be an object")
        return
    for key in sorted(set(traits) - FORBIDDEN_TRAITS_KEYS):
        errors.append(f"forbidden_traits {key} is not allowed")
    if not set(traits) & FORBIDDEN_TRAITS_KEYS:
        errors.append("forbidden_traits must name roles and/or materials")
    for key, vocabulary, label in [
        ("roles", FORBIDDABLE_ROLES, "forbidden role"),
        ("materials", FORBIDDABLE_MATERIALS, "forbidden material"),
    ]:
        if key not in traits:
            continue
        values = traits[key]
        if not isinstance(values, list) or not values:
            errors.append(f"forbidden_traits {key} must be a non-empty array")
            continue
        for value in values:
            if value not in vocabulary:
                errors.append(f"{label} not in vocabulary: {value}")
        if len(set(values)) != len(values):
            errors.append(f"forbidden_traits {key} must not repeat values")
    grid_rules = profile.get("grid")
    required_roles = (
        grid_rules.get("required_organ_roles", [])
        if isinstance(grid_rules, dict)
        else []
    )
    forbidden_roles = set(
        traits.get("roles", []) if isinstance(traits.get("roles"), list) else []
    )
    for organ_role in required_roles:
        cell_role = CELL_ROLE_FOR_ORGAN_ROLE.get(organ_role)
        if cell_role in forbidden_roles:
            errors.append(
                f"forbidden role {cell_role} contradicts required organ "
                f"role {organ_role}"
            )


def _validate_allowed_organ_roles(grid: dict, version: str, errors: list[str]) -> None:
    """X8 organ_role_permissions_v1; optional absence changes no legacy verdict."""
    allowed = grid["allowed_organ_roles"]
    if version != "0.2.0":
        errors.append("grid allowed_organ_roles requires slip_version 0.2.0")
    _validate_enum_array(allowed, ALLOWED_ORGAN_ROLES, "grid allowed_organ_roles",
                         "grid allowed organ role", errors)
    required = grid.get("required_organ_roles")
    if isinstance(allowed, list) and isinstance(required, list):
        for role in required:
            if isinstance(role, str) and role not in allowed:
                errors.append(f"required organ role is not allowed by SLIP: {role}")


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
