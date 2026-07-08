import json
import re
from collections import deque
from dataclasses import dataclass
from pathlib import Path


# Mirrors research/grid_genome/grid_genome.schema.json (hard invariant 1:
# schema validity). Keep these in sync with the schema's $defs.
ID_PATTERN = re.compile(r"^[a-z0-9][a-z0-9_-]{2,63}$")
SCHEMA_VERSION = "0.1.0"
GRID_SIZE_MIN = 8
GRID_SIZE_MAX = 64
CELL_ROLES = {
    "empty",
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
CELL_MATERIALS = {"void", "soft", "hard", "glass", "joint", "light", "signal"}
ORGAN_ROLES = {"body_core", "sensor", "expression", "locomotion", "ornament", "effect"}
COLOR_PATTERN = re.compile(r"^#[0-9A-Fa-f]{6}$")
# Hard invariant 5: minimum required body-core mass. BODY_CORE_MIN_CELLS
# is the ratified 8x8 floor; body_core_min_cells applies the DR 0029
# size-parametric law (evidence: labs/grid_genome/invariant_scaling.py),
# which reproduces this constant at 8x8 so every historical outcome and
# error string is unchanged there.
BODY_CORE_MIN_CELLS = 4


def body_core_min_cells(width: int | None, height: int | None) -> int:
    """DR 0029 floor law: max(4, 18*w*h // 256) — 4 at 8x8, 18 at 16x16.

    Malformed sizes fall back to the 8x8 floor, preserving the historical
    error path for grids whose grid_size already failed validation.
    """
    if not isinstance(width, int) or not isinstance(height, int):
        return BODY_CORE_MIN_CELLS
    return max(BODY_CORE_MIN_CELLS, (18 * width * height) // 256)


@dataclass(frozen=True)
class ValidationResult:
    ok: bool
    errors: list[str]
    warnings: list[str]


def validate_grid(grid: dict) -> ValidationResult:
    errors: list[str] = []
    warnings: list[str] = []

    grid_id = grid.get("grid_id")
    if not isinstance(grid_id, str) or not ID_PATTERN.match(grid_id):
        errors.append(f"grid_id must match {ID_PATTERN.pattern}: {grid_id}")
    if grid.get("schema_version") != SCHEMA_VERSION:
        errors.append(f"schema_version must be {SCHEMA_VERSION}")

    width, height = _grid_size(grid, errors)
    cells = grid.get("cells", [])
    if not isinstance(cells, list):
        errors.append("cells must be an array")
        cells = []

    coordinates: dict[tuple[int, int], dict] = {}
    has_anchor = False
    for entry in cells:
        if not isinstance(entry, dict):
            errors.append("cell entry must be an object")
            continue

        x = entry.get("x")
        y = entry.get("y")
        if not isinstance(x, int) or not isinstance(y, int):
            errors.append(f"cell coordinate must be integers: {x},{y}")
            continue

        key = (x, y)
        if key in coordinates:
            errors.append(f"duplicate coordinate: {x},{y}")
        else:
            coordinates[key] = entry

        if width is not None and height is not None:
            if x < 0 or y < 0 or x >= width or y >= height:
                errors.append(f"cell out of bounds: {x},{y} for grid {width}x{height}")

        if entry.get("animation_anchor") is True:
            has_anchor = True

        role = entry.get("role")
        if role not in CELL_ROLES:
            errors.append(f"cell role is unknown at {x},{y}: {role}")
        material = entry.get("material")
        if material not in CELL_MATERIALS:
            errors.append(f"cell material is unknown at {x},{y}: {material}")

        _validate_unit_interval(entry.get("mutation_weight"), "cell mutation_weight", errors)
        _validate_unit_interval(entry.get("stress", 0), "cell stress", errors)
        _validate_unit_interval(entry.get("damage", 0), "cell damage", errors)

    if not has_anchor:
        errors.append("missing animation anchor")

    organs = grid.get("organs", {})
    if not isinstance(organs, dict):
        errors.append("organs must be an object")
        organs = {}

    required_body_core: set[tuple[int, int]] = set()
    has_required_sensor_or_expression = False
    for organ_name, organ in organs.items():
        if not isinstance(organ, dict):
            errors.append(f"organ {organ_name} must be an object")
            continue

        role = organ.get("role")
        if role not in ORGAN_ROLES:
            errors.append(f"organ {organ_name} role is unknown: {role}")
        required = organ.get("required") is True
        if required and role in {"sensor", "expression"}:
            has_required_sensor_or_expression = True

        organ_cells = organ.get("cells", [])
        if not isinstance(organ_cells, list):
            errors.append(f"organ {organ_name} cells must be an array")
            continue

        for coordinate in organ_cells:
            point = _coordinate_tuple(coordinate)
            if point is None:
                errors.append(f"organ {organ_name} has invalid coordinate: {coordinate}")
                continue

            if point not in coordinates:
                errors.append(
                    f"organ {organ_name} references missing cell: {point[0]},{point[1]}"
                )
                continue

            cell_organ = coordinates[point].get("organ")
            if cell_organ not in {organ_name, None}:
                errors.append(
                    "organ "
                    f"{organ_name} coordinate {point[0]},{point[1]} belongs to {cell_organ}"
                )

            if role == "body_core" and required:
                required_body_core.add(point)

    if not has_required_sensor_or_expression:
        errors.append("missing required sensor or expression organ")

    body_core_floor = body_core_min_cells(width, height)
    if len(required_body_core) < body_core_floor:
        errors.append(
            "body mass below minimum: required body core has fewer than "
            f"{body_core_floor} cells"
        )
    elif not _is_connected(required_body_core):
        errors.append("required body core is disconnected")

    _validate_palette(grid.get("palette"), errors)

    mutation = grid.get("mutation", {})
    if not isinstance(mutation, dict):
        errors.append("mutation must be an object")
        mutation = {}
    for key in [
        "cell_mutation_rate",
        "organ_shift_rate",
        "palette_shift_rate",
        "symmetry_break_rate",
    ]:
        _validate_unit_interval(mutation.get(key), f"mutation {key}", errors)

    return ValidationResult(not errors, errors, warnings)


def validate_grid_file(path: str | Path) -> ValidationResult:
    with Path(path).open("r", encoding="utf-8") as handle:
        return validate_grid(json.load(handle))


def _grid_size(grid: dict, errors: list[str]) -> tuple[int | None, int | None]:
    grid_size = grid.get("grid_size")
    if (
        not isinstance(grid_size, list)
        or len(grid_size) != 2
        or not isinstance(grid_size[0], int)
        or not isinstance(grid_size[1], int)
    ):
        errors.append("grid_size must be [width, height]")
        return None, None
    for dimension in grid_size:
        if dimension < GRID_SIZE_MIN or dimension > GRID_SIZE_MAX:
            errors.append(
                "grid_size dimension outside "
                f"{GRID_SIZE_MIN}..{GRID_SIZE_MAX}: {dimension}"
            )
            return None, None
    return grid_size[0], grid_size[1]


def _validate_palette(palette: object, errors: list[str]) -> None:
    if not isinstance(palette, dict):
        errors.append("palette must be an object")
        return
    palette_id = palette.get("palette_id")
    if not isinstance(palette_id, str) or not ID_PATTERN.match(palette_id):
        errors.append(f"palette_id must match {ID_PATTERN.pattern}: {palette_id}")
    colors = palette.get("colors")
    if not isinstance(colors, list) or not 2 <= len(colors) <= 16:
        errors.append("palette colors must be an array of 2..16 entries")
        return
    for color in colors:
        if not isinstance(color, str) or not COLOR_PATTERN.match(color):
            errors.append(f"palette color must be #RRGGBB hex: {color}")


def _coordinate_tuple(value: object) -> tuple[int, int] | None:
    if (
        isinstance(value, list)
        and len(value) == 2
        and isinstance(value[0], int)
        and isinstance(value[1], int)
    ):
        return value[0], value[1]
    return None


def _validate_unit_interval(value: object, name: str, errors: list[str]) -> None:
    if not isinstance(value, int | float) or isinstance(value, bool):
        errors.append(f"{name} must be a number")
        return
    if value < 0 or value > 1:
        errors.append(f"{name} outside 0..1: {value}")


def _is_connected(points: set[tuple[int, int]]) -> bool:
    start = next(iter(points))
    seen = {start}
    queue: deque[tuple[int, int]] = deque([start])
    while queue:
        x, y = queue.popleft()
        neighbors = (
            (x - 1, y - 1),
            (x, y - 1),
            (x + 1, y - 1),
            (x - 1, y),
            (x + 1, y),
            (x - 1, y + 1),
            (x, y + 1),
            (x + 1, y + 1),
        )
        for neighbor in neighbors:
            if neighbor in points and neighbor not in seen:
                seen.add(neighbor)
                queue.append(neighbor)
    return seen == points
