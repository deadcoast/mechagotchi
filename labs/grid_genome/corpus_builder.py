import argparse
import json
from copy import deepcopy
from pathlib import Path

# PALETTES and _cell are re-exported here for backward compatibility:
# markov_grid, constrained_generator, and cross-lab consumers
# (workshop_editor, cellular_automata) import them from corpus_builder.
from grid_helpers import PALETTES, _cell, grid_from_matrix


ROOT = Path(__file__).resolve().parents[2]


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

    # strict_tokens: hand-authored blueprints must reject unknown tokens
    # (generator paths in markov_grid/constrained_generator skip them).
    return grid_from_matrix(
        grid_id,
        rows,
        palette_id,
        source="stage0_hand_authored_blueprint",
        strict_tokens=True,
    )


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
    parser.add_argument("--seed-dir", type=Path, default=ROOT / "data/seed_grids")
    parser.add_argument("--invalid-dir", type=Path, default=ROOT / "data/invalid_grids")
    args = parser.parse_args()
    write_corpus(args.seed_dir, args.invalid_dir)


if __name__ == "__main__":
    main()
