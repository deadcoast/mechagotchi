"""Vocabulary exemplars: waking the dormant grid-schema vocabulary.

Audit task T15 / decision record 0015. The schema legally admits cell
roles shell/joint/limb/antenna/decoration/effect, materials light/signal,
and organ roles locomotion/ornament/effect — none exercised by any
corpus until now. DR 0011 ratified the rich vocabulary; DR 0015's
verdict is COVER, incrementally: this lab authors exemplar creatures
that exercise every dormant item, proves them against the promoted
validator and the render/animation surfaces, and pins full coverage by
test so the vocabulary can never silently go dormant again. Workshop
authoring affordances for these roles are T9's deliverable.
"""

import argparse
import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
DEFAULT_OUTPUT_DIR = ROOT / "data" / "vocabulary_exemplars"
PACKAGE_SRC = ROOT / "packages" / "mecha_engine" / "src"
if str(PACKAGE_SRC) not in sys.path:
    sys.path.insert(0, str(PACKAGE_SRC))

from mecha_engine.genome import validate_grid  # noqa: E402


LCD = ["#07140d", "#5dbb63", "#d8ffd6"]

# token -> (role, material, organ_id, visual_index)
TOKENS = {
    "A": ("anchor", "hard", "core", 1),
    "B": ("body", "hard", "core", 1),
    "S": ("shell", "hard", "carapace", 1),
    "J": ("joint", "joint", "joints", 1),
    "L": ("limb", "hard", "limbs", 1),
    "E": ("eye", "glass", "sensors", 2),
    "M": ("mouth", "soft", "expression", 2),
    "N": ("antenna", "signal", "antennae", 2),
    "P": ("sensor", "signal", "antennae", 2),
    "D": ("decoration", "light", "trim", 2),
    "F": ("effect", "signal", "aura", 2),
}
ORGAN_ROLES = {
    "core": ("body_core", True),
    "carapace": ("body_core", False),
    "sensors": ("sensor", True),
    "antennae": ("sensor", False),
    "expression": ("expression", False),
    "joints": ("locomotion", False),
    "limbs": ("locomotion", False),
    "trim": ("ornament", False),
    "aura": ("effect", False),
}

ARGUS = [
    ".N.EE.P.",
    ".SSSSSS.",
    ".SBABBS.",
    ".SBBMBS.",
    ".SJBBJS.",
    ".LSSSSL.",
    ".L.DF.L.",
    "........",
]


def build_vocabulary_exemplars() -> list[dict]:
    cells = []
    organ_cells: dict[str, list[list[int]]] = {}
    for y, row in enumerate(ARGUS):
        for x, token in enumerate(row):
            if token == ".":
                continue
            role, material, organ, visual_index = TOKENS[token]
            cells.append(
                {
                    "x": x,
                    "y": y,
                    "visual": LCD[visual_index],
                    "role": role,
                    "material": material,
                    "mutation_weight": 0.1,
                    "animation_anchor": token == "A",
                    "organ": organ,
                    "stress": 0,
                    "damage": 0,
                    "locked": False,
                }
            )
            organ_cells.setdefault(organ, []).append([x, y])
    grid = {
        "grid_id": "vocab_argus",
        "schema_version": "0.1.0",
        "parent_grid_id": None,
        "grid_size": [8, 8],
        "cells": cells,
        "organs": {
            organ: {
                "role": ORGAN_ROLES[organ][0],
                "cells": organ_cells[organ],
                "required": ORGAN_ROLES[organ][1],
            }
            for organ in organ_cells
        },
        "palette": {
            "palette_id": "lcd_green",
            "colors": list(LCD),
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
            "mutation_events": ["vocabulary_exemplar_authored"],
        },
        "metadata": {"source": "vocabulary_exemplar_lab"},
    }
    return [grid]


def main() -> None:
    parser = argparse.ArgumentParser(description="Write vocabulary exemplars.")
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    args = parser.parse_args()
    args.output_dir.mkdir(parents=True, exist_ok=True)
    for grid in build_vocabulary_exemplars():
        result = validate_grid(grid)
        print(grid["grid_id"], "valid:", result.ok, result.errors[:4])
        (args.output_dir / f"{grid['grid_id']}.json").write_text(
            json.dumps(grid, indent=2) + "\n", encoding="utf-8"
        )
    (args.output_dir / "README.md").write_text(
        "# Vocabulary Exemplars\n\n"
        "Creatures exercising the full grid-schema vocabulary (DR 0015 /\n"
        "audit T15): dormant cell roles shell/joint/limb/antenna/\n"
        "decoration/effect, materials light/signal, and organ roles\n"
        "locomotion/ornament/effect. Coverage is pinned by\n"
        "`labs/grid_genome/test_vocabulary_exemplars.py` so the vocabulary\n"
        "cannot silently go dormant again.\n",
        encoding="utf-8",
    )


if __name__ == "__main__":
    main()
