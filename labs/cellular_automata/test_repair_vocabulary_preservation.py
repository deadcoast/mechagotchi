"""Cycle 20 / DR 0039 gates — repair preserves what it cannot yet spell.

DR 0038 taught the GENERATION path the ratified vocabulary; the era
loop then exposed a second vocabulary-blind surface: repair's 5-token
projection coerced every rich cell to body on contact, wholesale
destroying limbs/shells/decorations and breaking slip alignment. The
interim law, recorded: repair's PROJECTION and RECONSTRUCTION speak
the full alphabet (surviving cells keep their roles verbatim), its
PERCEPTION coarsens rich tokens to their palette-family legacy class
(body-family -> B, sensory/light-family -> E), and its 5-class
REGROWTH head stays — the 11-class retrain is a named future record.
"""

import json
import sys
import unittest
from pathlib import Path

LAB_DIR = Path(__file__).resolve().parent
GRID_GENOME = LAB_DIR.parent / "grid_genome"
for _path in (LAB_DIR, GRID_GENOME):
    if str(_path) not in sys.path:
        sys.path.insert(0, str(_path))

from ca_nca_growth_repair import (  # noqa: E402
    _neighborhood_features,
    apply_damage,
    grid_from_matrix,
    matrix_from_grid,
)
from validator import validate_grid  # noqa: E402

REPO_ROOT = LAB_DIR.parents[1]
RICH_ROLE_TOKENS = {
    "shell": "S",
    "joint": "J",
    "limb": "L",
    "antenna": "N",
    "sensor": "P",
    "decoration": "D",
    "effect": "F",
}


def _argus() -> dict:
    return json.loads(
        (
            REPO_ROOT / "data" / "vocabulary_exemplars" / "vocab_argus.json"
        ).read_text(encoding="utf-8")
    )


class ProjectionPreservationTests(unittest.TestCase):
    def test_rich_roles_project_to_their_own_tokens(self):
        argus = _argus()
        matrix = matrix_from_grid(argus)
        for cell in argus["cells"]:
            token = matrix[cell["y"]][cell["x"]]
            role = cell["role"]
            with self.subTest(role=role, at=(cell["x"], cell["y"])):
                if role in RICH_ROLE_TOKENS:
                    self.assertEqual(RICH_ROLE_TOKENS[role], token)
                else:
                    self.assertIn(token, {"B", "A", "E", "M"})

    def test_round_trip_preserves_rich_roles_and_validates(self):
        argus = _argus()
        rebuilt = grid_from_matrix(
            grid_id="repair_roundtrip",
            matrix=matrix_from_grid(argus),
            palette=argus["palette"],
            parent_grid_id=argus["grid_id"],
            source="repair_vocabulary_test",
            mutation_events=["repair_vocabulary_test"],
            generation_delta=1,
        )
        self.assertTrue(validate_grid(rebuilt).ok)
        rebuilt_roles = {
            (cell["x"], cell["y"]): cell["role"]
            for cell in rebuilt["cells"]
        }
        for cell in argus["cells"]:
            if cell["role"] not in RICH_ROLE_TOKENS:
                continue
            with self.subTest(at=(cell["x"], cell["y"])):
                self.assertEqual(
                    cell["role"], rebuilt_roles[(cell["x"], cell["y"])]
                )

    def test_damage_survivors_keep_their_rich_roles(self):
        argus = _argus()
        damaged = apply_damage(argus, pattern="center_cut")
        surviving = {
            (cell["x"], cell["y"]): cell["role"]
            for cell in damaged["cells"]
        }
        original_rich = {
            (cell["x"], cell["y"]): cell["role"]
            for cell in argus["cells"]
            if cell["role"] in RICH_ROLE_TOKENS
        }
        preserved = [
            position
            for position, role in original_rich.items()
            if surviving.get(position) == role
        ]
        # Damage removes some cells; every rich cell that SURVIVES must
        # keep its role (before DR 0039, all of them came back "body").
        self.assertTrue(preserved)
        for position, role in original_rich.items():
            if position in surviving:
                with self.subTest(at=position):
                    self.assertEqual(role, surviving[position])


class PerceptionCoarseningTests(unittest.TestCase):
    def test_rich_neighbors_encode_as_their_palette_family_class(self):
        base = [["." for _ in range(8)] for _ in range(8)]
        base[3][3] = "B"
        rich = [row[:] for row in base]
        rich[3][4] = "S"  # body-family
        legacy = [row[:] for row in base]
        legacy[3][4] = "B"
        self.assertEqual(
            _neighborhood_features(legacy, 3, 3),
            _neighborhood_features(rich, 3, 3),
        )
        rich_sensory = [row[:] for row in base]
        rich_sensory[3][4] = "D"  # light/sensory-family
        legacy_sensory = [row[:] for row in base]
        legacy_sensory[3][4] = "E"
        self.assertEqual(
            _neighborhood_features(legacy_sensory, 3, 3),
            _neighborhood_features(rich_sensory, 3, 3),
        )


if __name__ == "__main__":
    unittest.main()
