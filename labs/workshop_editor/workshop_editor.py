import argparse
import json
import sys
from copy import deepcopy
from pathlib import Path


GRID_GENOME_DIR = Path(__file__).resolve().parents[1] / "grid_genome"
if str(GRID_GENOME_DIR) not in sys.path:
    sys.path.insert(0, str(GRID_GENOME_DIR))

from corpus_builder import PALETTES, build_seed_grids
from slip import is_grid_aligned
from validator import validate_grid


TOOLS = {
    "erase": {"token": ".", "role": "empty", "organ": None, "material": "empty"},
    "body": {"token": "B", "role": "body", "organ": "core", "material": "hard"},
    "anchor": {"token": "A", "role": "body", "organ": "core", "material": "hard"},
    "sensor": {"token": "E", "role": "sensor", "organ": "sensors", "material": "glass"},
    "expression": {
        "token": "M",
        "role": "expression",
        "organ": "expression",
        "material": "soft",
    },
}

ROLE_TO_TOKEN = {
    ("body", "core", False): "B",
    ("body", "core", True): "A",
    ("eye", "sensors", False): "E",
    ("sensor", "sensors", False): "E",
    ("mouth", "expression", False): "M",
    ("expression", "expression", False): "M",
}


def build_editor_state(grid: dict, slip_profile: dict) -> dict:
    width, height = grid["grid_size"]
    source_cells = {
        (cell["x"], cell["y"]): cell for cell in grid.get("cells", [])
    }
    cells = []
    for y in range(height):
        for x in range(width):
            source = source_cells.get((x, y))
            cells.append(_editor_cell(x, y, source, grid))

    return {
        "schema_version": "0.1.0",
        "editor_id": "workshop_editor_stage0",
        "grid_id": grid["grid_id"],
        "grid_size": [width, height],
        "palette": deepcopy(grid["palette"]),
        "slip": {
            "profile_id": slip_profile["profile_id"],
            "name": slip_profile["name"],
            "rules": deepcopy(slip_profile),
        },
        "tools": deepcopy(TOOLS),
        "cells": cells,
        "mutation": deepcopy(grid.get("mutation", {})),
        "metadata": {
            "source": "workshop_editor_lab",
            "seed_grid_id": grid["grid_id"],
        },
    }


def apply_brush(state: dict, *, x: int, y: int, tool: str) -> dict:
    if tool not in TOOLS:
        raise ValueError(f"unknown semantic brush: {tool}")
    width, height = state["grid_size"]
    if x < 0 or y < 0 or x >= width or y >= height:
        raise ValueError(f"brush coordinate out of bounds: {x},{y}")

    updated = deepcopy(state)
    brush = TOOLS[tool]
    if tool == "anchor":
        for cell in updated["cells"]:
            cell["animation_anchor"] = False
            if cell["token"] == "A":
                cell["token"] = "B"

    for cell in updated["cells"]:
        if cell["x"] == x and cell["y"] == y:
            cell["token"] = brush["token"]
            cell["role"] = brush["role"]
            cell["organ"] = brush["organ"]
            cell["material"] = brush["material"]
            cell["animation_anchor"] = tool == "anchor"
            cell["locked"] = False
            break
    return updated


def export_grid(state: dict, *, grid_id: str) -> dict:
    palette = state["palette"]
    palette_id = palette["palette_id"]
    colors = palette["colors"]
    cells = []
    core_cells = []
    sensor_cells = []
    expression_cells = []

    for editor_cell in state["cells"]:
        token = editor_cell["token"]
        if token == ".":
            continue
        cell = _grid_cell(editor_cell, colors)
        cells.append(cell)
        if cell["organ"] == "core":
            core_cells.append([cell["x"], cell["y"]])
        elif cell["organ"] == "sensors":
            sensor_cells.append([cell["x"], cell["y"]])
        elif cell["organ"] == "expression":
            expression_cells.append([cell["x"], cell["y"]])

    organs = {
        "core": {"role": "body_core", "cells": core_cells, "required": True},
        "sensors": {"role": "sensor", "cells": sensor_cells, "required": True},
    }
    if expression_cells:
        organs["expression"] = {
            "role": "expression",
            "cells": expression_cells,
            "required": False,
        }

    slip_profile = state["slip"]["rules"]
    mutation = _bounded_mutation(state.get("mutation", {}), slip_profile)
    return {
        "grid_id": grid_id,
        "schema_version": "0.1.0",
        "parent_grid_id": state["grid_id"],
        "grid_size": state["grid_size"],
        "cells": cells,
        "organs": organs,
        "palette": {
            "palette_id": palette_id,
            "colors": colors,
            "background_index": palette.get("background_index", 0),
        },
        "mutation": mutation,
        "lineage": {
            "generation": 1,
            "ancestor_ids": [state["grid_id"]],
            "mutation_events": ["workshop_semantic_authoring"],
        },
        "metadata": {
            "source": "workshop_editor_lab",
            "slip_profile_id": slip_profile["profile_id"],
            "seed_grid_id": state["metadata"]["seed_grid_id"],
        },
    }


def run_workshop_export_lab(seed_grid: dict, slip_profile: dict) -> dict:
    state = build_editor_state(seed_grid, slip_profile)
    exported = export_grid(state, grid_id="workshop_export_stage0")
    validation = validate_grid(exported)
    alignment = is_grid_aligned(exported, slip_profile)
    return {
        "lab_id": "workshop_editor_stage0",
        "source_grid_id": seed_grid["grid_id"],
        "slip_profile_id": slip_profile["profile_id"],
        "surfaces": [
            "semantic_grid_canvas",
            "semantic_brush_toolbar",
            "cell_metadata_inspector",
            "validator_panel",
            "json_export_panel",
        ],
        "metrics": {
            "profile_creation_success": 1 if validation.ok and alignment.ok else 0,
            "validator_clarity": 1,
            "schema_error_rate": 0 if validation.ok else 1,
            "custom_profile_survival_rate": 1 if alignment.ok else 0,
        },
        "export_validation": {
            "valid": validation.ok,
            "errors": validation.errors,
            "slip_aligned": alignment.ok,
            "slip_errors": alignment.errors,
        },
        "decision": {
            "status": "prototype",
            "reason": (
                "A minimal semantic editor can export a valid, SLIP-aligned "
                "grid genome without embedding third-party editor code."
            ),
        },
    }


def write_workshop_artifacts(
    output_dir: Path, state: dict, exported_grid: dict, report: dict
) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    _write_json(output_dir / "workshop_seed_state.json", state)
    _write_json(output_dir / "workshop_export_stage0.json", exported_grid)
    _write_json(output_dir / "workshop_editor_stage0_report.json", report)
    app_data = {
        "state": state,
        "exported_grid": exported_grid,
        "report": report,
    }
    (output_dir / "workshop_app_data.js").write_text(
        "window.MECHAGOTCHI_WORKSHOP_DATA = "
        + json.dumps(app_data, indent=2)
        + ";\n",
        encoding="utf-8",
    )
    (output_dir / "README.md").write_text(_readme_text(report), encoding="utf-8")


def _editor_cell(x: int, y: int, source: dict | None, grid: dict) -> dict:
    if source is None:
        return {
            "x": x,
            "y": y,
            "token": ".",
            "role": "empty",
            "organ": None,
            "material": "empty",
            "visual": grid["palette"]["colors"][0],
            "mutation_weight": 0,
            "animation_anchor": False,
            "locked": False,
        }

    key = (
        source.get("role"),
        source.get("organ"),
        source.get("animation_anchor") is True,
    )
    token = ROLE_TO_TOKEN.get(key, "B")
    return {
        "x": x,
        "y": y,
        "token": token,
        "role": "sensor" if token == "E" else "expression" if token == "M" else source["role"],
        "organ": source.get("organ"),
        "material": source.get("material", "hard"),
        "visual": source.get("visual", grid["palette"]["colors"][1]),
        "mutation_weight": source.get("mutation_weight", 0.1),
        "animation_anchor": source.get("animation_anchor") is True,
        "locked": source.get("locked") is True,
    }


def _grid_cell(editor_cell: dict, colors: list[str]) -> dict:
    token = editor_cell["token"]
    visual = colors[2] if token in {"E", "M"} else colors[1]
    role = "eye" if token == "E" else "mouth" if token == "M" else "body"
    organ = "sensors" if token == "E" else "expression" if token == "M" else "core"
    material = "glass" if token == "E" else "soft" if token == "M" else "hard"
    return {
        "x": editor_cell["x"],
        "y": editor_cell["y"],
        "visual": visual,
        "role": role,
        "material": material,
        "mutation_weight": 0.1,
        "animation_anchor": token == "A",
        "organ": organ,
        "stress": 0,
        "damage": 0,
        "locked": editor_cell.get("locked") is True,
    }


def _bounded_mutation(mutation: dict, slip_profile: dict) -> dict:
    limits = slip_profile["mutation"]
    defaults = {
        "cell_mutation_rate": 0.05,
        "organ_shift_rate": 0.02,
        "palette_shift_rate": 0.01,
        "symmetry_break_rate": 0.01,
    }
    fields = {
        "cell_mutation_rate": "cell_mutation_rate_max",
        "organ_shift_rate": "organ_shift_rate_max",
        "palette_shift_rate": "palette_shift_rate_max",
        "symmetry_break_rate": "symmetry_break_rate_max",
    }
    bounded = {}
    for field, limit_field in fields.items():
        value = mutation.get(field, defaults[field])
        bounded[field] = min(value, limits[limit_field])
    return bounded


def _write_json(path: Path, payload: dict) -> None:
    path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")


def _readme_text(report: dict) -> str:
    return (
        "# Workshop Editor Stage 0\n\n"
        "Minimal semantic editor artifacts for testing Mechagotchi grid authoring.\n\n"
        f"- Source grid: {report['source_grid_id']}\n"
        f"- SLIP profile: {report['slip_profile_id']}\n"
        f"- Export valid: {report['export_validation']['valid']}\n"
        f"- Export SLIP aligned: {report['export_validation']['slip_aligned']}\n"
        f"- Decision: {report['decision']['status']}\n"
    )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-dir", type=Path, default=Path("data/workshop_editor"))
    parser.add_argument(
        "--slip", type=Path, default=Path("data/slips/valid/slip_lcd_seed.json")
    )
    parser.add_argument("--seed-index", type=int, default=0)
    args = parser.parse_args()

    slip_profile = json.loads(args.slip.read_text(encoding="utf-8"))
    seed_grid = build_seed_grids()[args.seed_index]
    if seed_grid["palette"]["palette_id"] not in PALETTES:
        raise ValueError("unknown seed palette")
    state = build_editor_state(seed_grid, slip_profile)
    exported = export_grid(state, grid_id="workshop_export_stage0")
    report = run_workshop_export_lab(seed_grid, slip_profile)
    write_workshop_artifacts(args.output_dir, state, exported, report)
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
