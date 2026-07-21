"""Cycle 20 J2 / DR 0038 gates — the vocabulary-complete generation

alphabet. The generator's projection must spell every ratified role
(one token per role, the RICH_TOKENS pairings the seed corpus itself
was authored with), reconstruction must synthesize validator-legal
structure for every token, and legacy-only matrices must reconstruct
EXACTLY as before (the additivity gate's unit face; the byte-level
face is the 8×8 artifact regeneration).
"""

import sys
import unittest
from pathlib import Path

LAB_DIR = Path(__file__).resolve().parent
if str(LAB_DIR) not in sys.path:
    sys.path.insert(0, str(LAB_DIR))

import json  # noqa: E402

from constrained_generator import (  # noqa: E402
    TOKENS,
    build_constrained_corpus,
    generate_constrained_grid,
    train_constraints,
)
from grid_helpers import (  # noqa: E402
    RICH_ORGAN_ROLES,
    RICH_TOKENS,
    grid_from_matrix,
)
from markov_grid import _matrix_from_grid  # noqa: E402
from corpus_builder import build_seed_grids, build_seed_grids_16  # noqa: E402
from validator import validate_grid  # noqa: E402

REPO_ROOT = LAB_DIR.parents[1]
ROLE_TO_TOKEN = {
    "shell": "S",
    "joint": "J",
    "limb": "L",
    "eye": "E",
    "mouth": "M",
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


class ProjectionTests(unittest.TestCase):
    def test_the_alphabet_covers_every_ratified_token(self):
        self.assertEqual(sorted(TOKENS), sorted({".", *RICH_TOKENS}))

    def test_projection_spells_every_role_on_the_exemplar(self):
        argus = _argus()
        matrix = _matrix_from_grid(argus)
        for cell in argus["cells"]:
            token = matrix[cell["y"]][cell["x"]]
            with self.subTest(role=cell["role"], at=(cell["x"], cell["y"])):
                if cell["role"] == "body":
                    self.assertEqual(
                        "A" if cell["animation_anchor"] else "B", token
                    )
                elif cell["role"] == "anchor":
                    # The standalone anchor role normalizes to "A" (the
                    # seed corpus's anchor-flagged-body convention).
                    self.assertEqual("A", token)
                else:
                    self.assertEqual(ROLE_TO_TOKEN[cell["role"]], token)

    def test_projection_stays_the_identity_on_legacy_roles(self):
        beetle = build_seed_grids()[0]  # the 8x8 corpus is legacy-only
        matrix = _matrix_from_grid(beetle)
        tokens = {token for row in matrix for token in row}
        self.assertLessEqual(tokens, {".", "B", "A", "E", "M"})


class ReconstructionTests(unittest.TestCase):
    def test_round_trip_preserves_roles_and_passes_the_validator(self):
        argus = _argus()
        matrix = _matrix_from_grid(argus)
        rebuilt = grid_from_matrix(
            "vocab_roundtrip",
            matrix,
            "lcd_green",
            source="vocabulary_alphabet_test",
        )
        self.assertTrue(validate_grid(rebuilt).ok)
        rebuilt_roles = {
            (cell["x"], cell["y"]): cell["role"]
            for cell in rebuilt["cells"]
        }
        for cell in argus["cells"]:
            expected_role = (
                "body" if cell["role"] == "anchor" else cell["role"]
            )
            with self.subTest(at=(cell["x"], cell["y"])):
                self.assertEqual(
                    expected_role, rebuilt_roles[(cell["x"], cell["y"])]
                )

    def test_new_tokens_join_ratified_organs_with_ratified_materials(self):
        argus = _argus()
        rebuilt = grid_from_matrix(
            "vocab_organs",
            _matrix_from_grid(argus),
            "lcd_green",
            source="vocabulary_alphabet_test",
        )
        for organ_id, organ in rebuilt["organs"].items():
            with self.subTest(organ=organ_id):
                self.assertEqual(
                    RICH_ORGAN_ROLES[organ_id][0], organ["role"]
                )
        by_position = {
            (cell["x"], cell["y"]): cell for cell in rebuilt["cells"]
        }
        for cell in argus["cells"]:
            if cell["role"] == "anchor" or (
                cell["role"] == "body" and cell["animation_anchor"]
            ):
                token = "A"
            else:
                token = ROLE_TO_TOKEN.get(cell["role"], "B")
            role, material, organ, _ = RICH_TOKENS[token]
            rebuilt_cell = by_position[(cell["x"], cell["y"])]
            with self.subTest(at=(cell["x"], cell["y"])):
                self.assertEqual(material, rebuilt_cell["material"])
                self.assertEqual(organ, rebuilt_cell["organ"])

    def test_legacy_matrices_reconstruct_exactly_as_before(self):
        matrix = [
            list(".BA."),
            list(".BB."),
            list("E..M"),
            list("...."),
        ]
        grid = grid_from_matrix(
            "legacy_shape",
            matrix,
            "lcd_green",
            source="vocabulary_alphabet_test",
        )
        self.assertEqual(
            ["core", "sensors", "expression"], list(grid["organs"])
        )
        self.assertTrue(grid["organs"]["core"]["required"])
        self.assertTrue(grid["organs"]["sensors"]["required"])
        self.assertFalse(grid["organs"]["expression"]["required"])
        self.assertEqual(
            {"body", "eye", "mouth"},
            {cell["role"] for cell in grid["cells"]},
        )


class GenerationEmissionTests(unittest.TestCase):
    def test_the_constrained_path_can_now_spell_the_motion_trio(self):
        # Trained on the rich 16x16 seeds, a modest batch must emit at
        # least one limb/joint/decoration cell somewhere — the
        # vocabulary flows end to end (the full emission-rate gate is
        # the role_emission artifact re-run).
        seeds = build_seed_grids_16()
        corpus = build_constrained_corpus(seeds, count=24, rng_seed=41)
        emitted = {
            cell["role"] for grid in corpus for cell in grid["cells"]
        }
        self.assertTrue(
            emitted & {"limb", "joint", "decoration"},
            f"no motion-trio roles in {sorted(emitted)}",
        )
        for grid in corpus:
            self.assertTrue(validate_grid(grid).ok)


class ResampleTemperatureTests(unittest.TestCase):
    """DR 0038's rider: an explicit, capped structural-resample

    temperature — OFF by default (byte-identical when unset).
    """

    @classmethod
    def setUpClass(cls):
        cls.seeds = build_seed_grids_16()
        cls.model = train_constraints(cls.seeds)

    def test_unset_temperature_is_byte_identical_to_omitted(self):
        base = generate_constrained_grid(
            self.model, self.seeds, "temp_off", rng_seed=7
        )
        explicit = generate_constrained_grid(
            self.model,
            self.seeds,
            "temp_off",
            rng_seed=7,
            resample_temperature=None,
        )
        self.assertEqual(
            json.dumps(base, sort_keys=True),
            json.dumps(explicit, sort_keys=True),
        )

    def test_temperature_is_capped_and_loud(self):
        for bad in (-0.5, 0.0, 2.5):
            with self.subTest(temperature=bad):
                with self.assertRaises(ValueError):
                    generate_constrained_grid(
                        self.model,
                        self.seeds,
                        "temp_bad",
                        rng_seed=7,
                        resample_temperature=bad,
                    )

    def test_a_hot_candidate_is_still_validator_legal(self):
        hot = generate_constrained_grid(
            self.model,
            self.seeds,
            "temp_hot",
            rng_seed=7,
            resample_temperature=2.0,
        )
        self.assertTrue(validate_grid(hot).ok)


if __name__ == "__main__":
    unittest.main()
