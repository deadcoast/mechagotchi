import json
import unittest
from pathlib import Path

from animation_states import build_render_packet_v2
from corpus_builder import build_seed_grids
from slip import is_grid_aligned, validate_slip

ROOT = Path(__file__).resolve().parents[2]


def _v2_profile(**overrides) -> dict:
    profile = json.loads(
        (ROOT / "data/slips/valid/slip_lcd_seed.json").read_text(
            encoding="utf-8"
        )
    )
    profile["slip_version"] = "0.2.0"
    profile["profile_id"] = "slip_v2_grammar_test"
    profile["species_class"] = "proto_shell"
    profile["visual_grammar"] = {
        "allowed_materials": ["void", "soft", "hard", "glass"],
        "animation_vocab": ["idle", "blink", "sleep"],
    }
    profile.update(overrides)
    return profile


class SpeciesClassAndGrammarValidationTests(unittest.TestCase):
    """DR 0012 rung T3.5: species_class + visual_grammar, version-gated."""

    def test_v2_profile_validates(self):
        result = validate_slip(_v2_profile())
        self.assertEqual([], result.errors)

    def test_v1_profiles_are_version_gated(self):
        for field in ("species_class", "visual_grammar"):
            profile = _v2_profile(slip_version="0.1.0")
            for other in ("species_class", "visual_grammar"):
                if other != field:
                    del profile[other]
            result = validate_slip(profile)
            self.assertFalse(result.ok, field)
            self.assertTrue(
                any("0.2.0" in error for error in result.errors), field
            )

    def test_bad_shapes_are_rejected(self):
        for overrides in (
            {"species_class": "Proto Shell"},
            {"species_class": ""},
            {"species_class": 7},
            {"visual_grammar": {}},
            {"visual_grammar": {"allowed_materials": []}},
            {"visual_grammar": {"allowed_materials": ["plasma"]}},
            {"visual_grammar": {"animation_vocab": ["dance"]}},
            {"visual_grammar": {"animation_vocab": ["blink"]}},  # no idle
            {"visual_grammar": {"unknown": True}},
        ):
            result = validate_slip(_v2_profile(**overrides))
            self.assertFalse(result.ok, overrides)


class AllowedMaterialsAlignmentTests(unittest.TestCase):
    def setUp(self):
        self.seed = build_seed_grids()[0]  # materials: void/soft/hard/glass

    def test_grid_within_allowed_materials_stays_aligned(self):
        result = is_grid_aligned(self.seed, _v2_profile())
        self.assertEqual([], result.errors)

    def test_grid_with_disallowed_material_fails_alignment(self):
        profile = _v2_profile(
            visual_grammar={"allowed_materials": ["void", "hard", "glass"]}
        )
        self.assertTrue(validate_slip(profile).ok)
        result = is_grid_aligned(self.seed, profile)
        self.assertFalse(result.ok)
        self.assertTrue(
            any(
                "material" in error and "soft" in error
                for error in result.errors
            ),
            result.errors,
        )


class AnimationVocabConsumerTests(unittest.TestCase):
    """The packet-v2 selection honors the species' animation vocabulary."""

    def setUp(self):
        self.grid = build_seed_grids()[0]

    def test_selection_outside_the_vocab_falls_back_to_idle(self):
        # hunger 0.8 selects beg — but this species has no beg.
        lifecycle_state = {
            "alive": True, "energy": 0.6, "hunger": 0.8,
            "stress": 0.2, "age_ticks": 1,
        }
        packet = build_render_packet_v2(
            self.grid, lifecycle_state, slip_profile=_v2_profile()
        )
        self.assertEqual("idle", packet["animation"])
        self.assertEqual("hungry", packet["mood"])  # mood stays honest
        self.assertEqual(
            ["idle", "blink", "sleep"], packet["animation_vocabulary"]
        )

    def test_selection_inside_the_vocab_is_untouched(self):
        lifecycle_state = {
            "alive": True, "energy": 0.1, "hunger": 0.3,
            "stress": 0.2, "age_ticks": 1,
        }
        packet = build_render_packet_v2(
            self.grid, lifecycle_state, slip_profile=_v2_profile()
        )
        self.assertEqual("sleep", packet["animation"])

    def test_no_profile_keeps_the_full_vocabulary(self):
        packet = build_render_packet_v2(self.grid, None)
        self.assertEqual(
            ["idle", "blink", "sleep", "beg", "ill"],
            packet["animation_vocabulary"],
        )


if __name__ == "__main__":
    unittest.main()
