import argparse
import json
from copy import deepcopy
from pathlib import Path


PALETTES = {
    "lcd_green": ["#07140d", "#5dbb63", "#d8ffd6"],
    "gameboy_gray": ["#111814", "#7e8f76", "#d7dfc7"],
    "amber_terminal": ["#1c1005", "#d98428", "#ffe0a3"],
    "crt_blue": ["#06131f", "#3e8fbf", "#d6f3ff"],
    "pocket_plum": ["#160e1f", "#7e5aa6", "#f2dcff"],
}


BLUEPRINTS = [
    ("mg_seed_001", "lcd_green", [".E..E...", "..BB....", ".BABB...", "..BB.M..", "...BB...", "........", "........", "........"]),
    ("mg_seed_002", "gameboy_gray", ["........", "..E.E...", "..BBB...", ".BBABB..", "..BMB...", "...B....", "........", "........"]),
    ("mg_seed_003", "amber_terminal", ["........", "...E....", "..BBB...", ".BBABB..", "..BMB...", "...E....", "........", "........"]),
    ("mg_seed_004", "crt_blue", ["..E..E..", "...B....", "..BAB...", ".BBBB...", "..BMB...", "...B....", "........", "........"]),
    ("mg_seed_005", "pocket_plum", ["........", "..E..E..", ".BBBB...", ".BABBB..", "..BMB...", "..BBB...", "........", "........"]),
    ("mg_seed_006", "lcd_green", ["........", "...E....", "..BBB...", "..BAB...", "..BBB...", ".E.M.E..", "........", "........"]),
    ("mg_seed_007", "gameboy_gray", ["........", ".E....E.", "..BBBB..", "..BABB..", "...BM...", "...BB...", "........", "........"]),
    ("mg_seed_008", "amber_terminal", ["........", "..E.E...", ".BBBB...", "...AB...", ".BBBB...", "...M....", "........", "........"]),
    ("mg_seed_009", "crt_blue", ["........", "...E.E..", "..BBBB..", ".BBAB...", "..BMB...", "..B.....", "........", "........"]),
    ("mg_seed_010", "pocket_plum", ["........", ".E.E....", "..BBB...", "..BABB..", "..BMB...", "....B...", "........", "........"]),
    ("mg_seed_011", "lcd_green", ["........", "...E....", ".BBBB...", "..BAB...", ".BBBB...", "...M.E..", "........", "........"]),
    ("mg_seed_012", "gameboy_gray", ["........", "..E..E..", "...BB...", "..BABB..", "...BM...", "..BBB...", "........", "........"]),
    ("mg_seed_013", "amber_terminal", ["........", ".E..E...", ".BBBB...", ".BABB...", "..BM....", "..BB....", "........", "........"]),
    ("mg_seed_014", "crt_blue", ["........", "..E.....", "..BBB...", ".BBABB..", "..BMB...", ".....E..", "........", "........"]),
    ("mg_seed_015", "pocket_plum", ["........", "....E...", "..BBBB..", "..BABB..", "..BMB...", "..E.....", "........", "........"]),
    ("mg_seed_016", "lcd_green", ["........", "..E.E...", "...BBB..", "..BABB..", "..BMB...", "...BB...", "........", "........"]),
    ("mg_seed_017", "gameboy_gray", ["........", ".E...E..", "..BBBB..", ".BBAB...", "..BMB...", "...B....", "........", "........"]),
    ("mg_seed_018", "amber_terminal", ["........", "..E.....", ".BBBB...", ".BABBB..", "...BM...", ".....E..", "........", "........"]),
    ("mg_seed_019", "crt_blue", ["........", "...E.E..", "..BBB...", ".BABB...", ".BBM....", "..B.....", "........", "........"]),
    ("mg_seed_020", "pocket_plum", ["........", ".E..E...", "..BBB...", "..BABB..", "...BM...", "...BB...", "........", "........"]),
    ("mg_seed_021", "lcd_green", ["........", "..E..E..", ".BBBB...", "..BABB..", ".BBM....", "...B....", "........", "........"]),
    ("mg_seed_022", "gameboy_gray", ["........", "...E....", "..BBBB..", ".BBABB..", "..BMB...", ".E......", "........", "........"]),
    ("mg_seed_023", "amber_terminal", ["........", ".E.E....", "..BBBB..", "..BABB..", "...BM...", "....B...", "........", "........"]),
    ("mg_seed_024", "crt_blue", ["........", "..E...E.", "...BBB..", "..BABB..", ".BBM....", "..BB....", "........", "........"]),
    ("mg_seed_025", "pocket_plum", ["........", "...E.E..", ".BBBB...", ".BABB...", "..BMB...", "...B....", "........", "........"]),
    ("mg_seed_026", "lcd_green", ["........", "..E.....", "..BBBB..", "..BABB..", ".BBM....", "....E...", "........", "........"]),
    ("mg_seed_027", "gameboy_gray", ["........", "...E.E..", "..BBBB..", ".BBAB...", "...BM...", "...BB...", "........", "........"]),
    ("mg_seed_028", "amber_terminal", ["........", ".E..E...", "...BBB..", "..BABB..", "..BMB...", "..BB....", "........", "........"]),
    ("mg_seed_029", "crt_blue", ["........", "..E.E...", ".BBBB...", "...AB...", "..BMB...", "...BB...", "........", "........"]),
    ("mg_seed_030", "pocket_plum", ["........", "...E....", "..BBB...", ".BBABB..", ".BBM....", "....E...", "........", "........"]),
    ("mg_seed_031", "lcd_green", ["........", ".E...E..", "..BBBB..", "..BAB...", "..BMB...", "...BB...", "........", "........"]),
    ("mg_seed_032", "gameboy_gray", ["........", "...E....", ".BBBB...", ".BABBB..", "..BM....", "..E.....", "........", "........"]),
    ("mg_seed_033", "amber_terminal", ["........", "..E..E..", "...BBB..", "..BABB..", ".BBM....", "...B....", "........", "........"]),
    ("mg_seed_034", "crt_blue", ["........", ".E.E....", ".BBBB...", ".BBAB...", "...BM...", "...BB...", "........", "........"]),
    ("mg_seed_035", "pocket_plum", ["........", "..E...E.", "..BBB...", "..BABB..", "..BMB...", "..B.....", "........", "........"]),
    ("mg_seed_036", "lcd_green", ["........", "...E.E..", ".BBBB...", "..BAB...", ".BBM....", "...B....", "........", "........"]),
    ("mg_seed_037", "gameboy_gray", ["........", "..E.....", "...BBB..", "..BABB..", "..BMB...", ".....E..", "........", "........"]),
    ("mg_seed_038", "amber_terminal", ["........", ".E..E...", "..BBBB..", ".BBAB...", "..BM....", "...BB...", "........", "........"]),
    ("mg_seed_039", "crt_blue", ["........", "...E....", "..BBBB..", "..BABB..", "..BMB...", ".E......", "........", "........"]),
    ("mg_seed_040", "pocket_plum", ["........", "..E.E...", ".BBBB...", ".BAB....", "..BMB...", "...BB...", "........", "........"]),
    ("mg_seed_041", "lcd_green", ["........", "..E..E..", "...BBB..", ".BBABB..", "..BM....", "...B....", "........", "........"]),
    ("mg_seed_042", "gameboy_gray", ["........", ".E...E..", ".BBBB...", "..BABB..", "...BM...", "...B....", "........", "........"]),
    ("mg_seed_043", "amber_terminal", ["........", "...E....", "..BBB...", ".BBAB...", "..BMB...", ".....E..", "........", "........"]),
    ("mg_seed_044", "crt_blue", ["........", "..E.E...", ".BBBB...", "..BAB...", "..BMB...", "....B...", "........", "........"]),
    ("mg_seed_045", "pocket_plum", ["........", ".E..E...", "..BBBB..", "..BABB..", ".BBM....", "........", "........", "........"]),
    ("mg_seed_046", "lcd_green", ["........", "...E.E..", "..BBB...", ".BBABB..", "...BM...", "...B....", "........", "........"]),
    ("mg_seed_047", "gameboy_gray", ["........", "..E.....", ".BBBB...", ".BABB...", "..BMB...", "....E...", "........", "........"]),
    ("mg_seed_048", "amber_terminal", ["........", "...E....", "..BBBB..", "..BABB..", ".BBM....", ".....E..", "........", "........"]),
    ("mg_seed_049", "crt_blue", ["........", ".E.E....", "...BBB..", "..BABB..", "..BMB...", "..BB....", "........", "........"]),
    ("mg_seed_050", "pocket_plum", ["........", "..E..E..", ".BBBB...", ".BBAB...", "..BM....", "...BB...", "........", "........"]),
]


def build_seed_grids() -> list[dict]:
    return [_grid_from_blueprint(*blueprint) for blueprint in BLUEPRINTS]


def build_invalid_grids(seed_grids: list[dict]) -> list[dict]:
    invalid: list[dict] = []
    for grid in seed_grids:
        invalid.extend(
            [
                _duplicate_coordinate(grid),
                _out_of_bounds_cell(grid),
                _missing_animation_anchor(grid),
                _missing_organ_cell(grid),
            ]
        )
    return invalid


def write_corpus(seed_dir: Path, invalid_dir: Path) -> None:
    seed_dir.mkdir(parents=True, exist_ok=True)
    invalid_dir.mkdir(parents=True, exist_ok=True)

    seeds = build_seed_grids()
    invalid_grids = build_invalid_grids(seeds)
    for grid in seeds:
        _write_json(seed_dir / f"{grid['grid_id']}.json", grid)
    for grid in invalid_grids:
        _write_json(invalid_dir / f"{grid['grid_id']}.json", grid)


def _grid_from_blueprint(grid_id: str, palette_id: str, rows: list[str]) -> dict:
    if len(rows) != 8 or any(len(row) != 8 for row in rows):
        raise ValueError(f"{grid_id} must be an 8x8 blueprint")

    cells: list[dict] = []
    core_cells: list[list[int]] = []
    sensor_cells: list[list[int]] = []
    expression_cells: list[list[int]] = []
    palette = PALETTES[palette_id]

    for y, row in enumerate(rows):
        for x, token in enumerate(row):
            if token == ".":
                continue
            if token in {"B", "A"}:
                cells.append(
                    _cell(
                        x,
                        y,
                        visual=palette[1],
                        role="body",
                        material="hard",
                        organ="core",
                        animation_anchor=token == "A",
                    )
                )
                core_cells.append([x, y])
            elif token == "E":
                cells.append(
                    _cell(
                        x,
                        y,
                        visual=palette[2],
                        role="eye",
                        material="glass",
                        organ="sensors",
                    )
                )
                sensor_cells.append([x, y])
            elif token == "M":
                cells.append(
                    _cell(
                        x,
                        y,
                        visual=palette[2],
                        role="mouth",
                        material="soft",
                        organ="expression",
                    )
                )
                expression_cells.append([x, y])
            else:
                raise ValueError(f"{grid_id} has unsupported token {token!r}")

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

    return {
        "grid_id": grid_id,
        "schema_version": "0.1.0",
        "parent_grid_id": None,
        "grid_size": [8, 8],
        "cells": cells,
        "organs": organs,
        "palette": {
            "palette_id": palette_id,
            "colors": palette,
            "background_index": 0,
        },
        "mutation": {
            "cell_mutation_rate": 0.05,
            "organ_shift_rate": 0.02,
            "palette_shift_rate": 0.01,
            "symmetry_break_rate": 0.01,
        },
        "lineage": {
            "generation": 0,
            "ancestor_ids": [],
            "mutation_events": [],
        },
        "metadata": {
            "source": "stage0_hand_authored_blueprint",
        },
    }


def _cell(
    x: int,
    y: int,
    *,
    visual: str,
    role: str,
    material: str,
    organ: str,
    animation_anchor: bool = False,
) -> dict:
    return {
        "x": x,
        "y": y,
        "visual": visual,
        "role": role,
        "material": material,
        "mutation_weight": 0.1,
        "animation_anchor": animation_anchor,
        "organ": organ,
        "stress": 0,
        "damage": 0,
        "locked": False,
    }


def _duplicate_coordinate(grid: dict) -> dict:
    invalid = deepcopy(grid)
    invalid["grid_id"] = f"{grid['grid_id']}_invalid_duplicate"
    invalid["cells"].append(deepcopy(invalid["cells"][0]))
    return invalid


def _out_of_bounds_cell(grid: dict) -> dict:
    invalid = deepcopy(grid)
    invalid["grid_id"] = f"{grid['grid_id']}_invalid_bounds"
    invalid["cells"][0]["x"] = invalid["grid_size"][0]
    return invalid


def _missing_animation_anchor(grid: dict) -> dict:
    invalid = deepcopy(grid)
    invalid["grid_id"] = f"{grid['grid_id']}_invalid_anchor"
    for cell in invalid["cells"]:
        cell["animation_anchor"] = False
    return invalid


def _missing_organ_cell(grid: dict) -> dict:
    invalid = deepcopy(grid)
    invalid["grid_id"] = f"{grid['grid_id']}_invalid_organ_ref"
    invalid["organs"]["core"]["cells"].append([0, 0])
    return invalid


def _write_json(path: Path, payload: dict) -> None:
    path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--seed-dir", type=Path, default=Path("data/seed_grids"))
    parser.add_argument("--invalid-dir", type=Path, default=Path("data/invalid_grids"))
    args = parser.parse_args()
    write_corpus(args.seed_dir, args.invalid_dir)


if __name__ == "__main__":
    main()
