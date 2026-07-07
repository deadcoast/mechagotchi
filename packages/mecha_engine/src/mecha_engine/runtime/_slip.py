"""Internal SLIP profile validation and alignment checks for runtime.

Contract sources:

- research/package_specs/mecha_engine_runtime_interface_spec.md
  ("Why a runtime surface": repair must run SLIP-aware, and parents are
  selected from the profile-aligned pool)
- research/slip/slip.schema.json (profile shape, palette enum, 0..1 caps)
- research/decision_records/0013-port-slip-v2-and-packet-v2.md (the SLIP
  v0.2 ladder port; ``lineage_preferences`` steers ``evolve`` parenting)

Scope note (documented factoring): a full ``mecha_engine.slip`` module is a
deferred module per the scaffold verification gate, so runtime carries only
the minimal internal port it needs — profile validation and grid/profile
alignment for parent-pool selection and per-cycle alignment retention. This
mirrors the factoring already promoted for ``mecha_engine.generation``,
``mecha_engine.lifecycle``, and ``mecha_engine.repair`` (each with its own
private ``_slip`` helper; this file is a verbatim copy of the repair
module's port, re-headed for runtime, because private files of other
modules are never imported across module boundaries) and is the same
self-contained semantic port of the Stage 0 research SLIP checks (identical
rule set and error strings); it is private to ``mecha_engine.runtime`` and
is not a package SLIP surface.

Parity note (decision record 0013): this mirror carries the lab
authority's dual-version ``validate_slip`` — ``slip_version`` "0.1.0" is
the frozen baseline (exactly the original key set), "0.2.0" adds the four
optional ladder fields (``forbidden_traits``, ``risk_tolerances``,
``learning_switches``, ``lineage_preferences``) with the lab's exact
validation semantics — and the forbidden-traits enforcement in
``is_grid_aligned``, verbatim (error strings included). Source of truth:
``labs/grid_genome/slip.py``; the lab-side parity pin is
``labs/grid_genome/test_package_slip_parity.py``. The lab's
``v01_projection`` adapter is deliberately not ported: the package now
accepts v0.2 profiles directly.
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
    """Check a grid genome against a SLIP profile's constraint surfaces."""
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
