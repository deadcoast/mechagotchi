import unittest

from animation_states import ANIMATION_STATES, project_animation_state
from vocabulary_exemplars import build_vocabulary_exemplars

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]

import sys
PACKAGE_SRC = ROOT / "packages" / "mecha_engine" / "src"
if str(PACKAGE_SRC) not in sys.path:
    sys.path.insert(0, str(PACKAGE_SRC))

from mecha_engine.genome import render_packet_from_grid, validate_grid  # noqa: E402


class VocabularyExemplarTests(unittest.TestCase):
    """DR 0015: the dormant vocabulary is covered and pinned awake."""

    @classmethod
    def setUpClass(cls):
        cls.grids = build_vocabulary_exemplars()
        cls.schema = json.loads(
            (ROOT / "research/grid_genome/grid_genome.schema.json").read_text(
                encoding="utf-8"
            )
        )

    def test_every_schema_role_material_and_organ_role_is_exercised(self):
        cell_props = self.schema["$defs"]["cell"]["properties"]
        organ_props = self.schema["$defs"]["organ"]["properties"]
        want_roles = set(cell_props["role"]["enum"]) - {"empty"}
        want_materials = set(cell_props["material"]["enum"]) - {"void"}
        want_organ_roles = set(organ_props["role"]["enum"])
        have_roles, have_materials, have_organ_roles = set(), set(), set()
        seed_dir = ROOT / "data" / "seed_grids"
        corpora = list(self.grids) + [
            json.loads(p.read_text(encoding="utf-8"))
            for p in sorted(seed_dir.glob("*.json"))[:3]
        ]
        for grid in corpora:
            for cell in grid["cells"]:
                have_roles.add(cell["role"])
                have_materials.add(cell["material"])
            for organ in grid["organs"].values():
                have_organ_roles.add(organ["role"])
        self.assertEqual(set(), want_roles - have_roles)
        self.assertEqual(set(), want_materials - have_materials)
        self.assertEqual(set(), want_organ_roles - have_organ_roles)

    def test_exemplars_pass_the_promoted_validator(self):
        for grid in self.grids:
            result = validate_grid(grid)
            self.assertEqual([], result.errors, grid["grid_id"])

    def test_exemplars_render_and_animate(self):
        for grid in self.grids:
            packet = render_packet_from_grid(grid)
            self.assertEqual(len(grid["cells"]), len(packet["cells"]))
            for state in ANIMATION_STATES:
                projected = project_animation_state(grid, state)
                self.assertTrue(validate_grid(projected).ok, state)

    def test_committed_corpus_matches_the_builder(self):
        for grid in self.grids:
            committed = ROOT / "data" / "vocabulary_exemplars" / (
                grid["grid_id"] + ".json"
            )
            self.assertTrue(committed.exists(), grid["grid_id"])
            self.assertEqual(
                grid, json.loads(committed.read_text(encoding="utf-8"))
            )


if __name__ == "__main__":
    unittest.main()
