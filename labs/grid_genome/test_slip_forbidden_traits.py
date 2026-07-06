import json
import unittest
from copy import deepcopy
from pathlib import Path

from corpus_builder import build_seed_grids
from slip import (
    FORBIDDABLE_MATERIALS,
    FORBIDDABLE_ROLES,
    is_grid_aligned,
    validate_slip,
)


ROOT = Path(__file__).resolve().parents[2]
GRID_SCHEMA_PATH = ROOT / "research" / "grid_genome" / "grid_genome.schema.json"


def _v2_profile(**overrides) -> dict:
    profile = {
        "slip_version": "0.2.0",
        "profile_id": "slip_v2_test",
        "name": "V2 Test Profile",
        "grid": {
            "allowed_palettes": ["lcd_green"],
            "body_mass_min": 4,
            "body_mass_max": 24,
            "required_organ_roles": ["sensor", "expression"],
        },
        "mutation": {
            "cell_mutation_rate_max": 0.15,
            "organ_shift_rate_max": 0.05,
            "palette_shift_rate_max": 0.05,
            "symmetry_break_rate_max": 0.05,
        },
        "behavior": {"curiosity": 0.6, "neediness": 0.4, "sleepiness": 0.5},
        "survival_weights": {"stability": 0.5, "novelty": 0.25, "bond": 0.25},
        "forbidden_traits": {"roles": ["shell"], "materials": ["light"]},
    }
    profile.update(overrides)
    return profile


class ForbiddenTraitsValidationTests(unittest.TestCase):
    """DR 0012 rung T3.1: the first ladder field, version-gated."""

    def test_v2_profile_with_forbidden_traits_validates(self):
        result = validate_slip(_v2_profile())
        self.assertEqual([], result.errors)
        self.assertTrue(result.ok)

    def test_v2_profile_without_ladder_fields_still_validates(self):
        profile = _v2_profile()
        del profile["forbidden_traits"]
        self.assertTrue(validate_slip(profile).ok)

    def test_v1_profile_with_forbidden_traits_is_version_gated(self):
        profile = _v2_profile(slip_version="0.1.0")
        result = validate_slip(profile)
        self.assertFalse(result.ok)
        self.assertTrue(
            any("0.2.0" in error for error in result.errors),
            result.errors,
        )

    def test_unknown_version_is_rejected(self):
        result = validate_slip(_v2_profile(slip_version="9.9.9"))
        self.assertFalse(result.ok)

    def test_empty_and_void_cannot_be_forbidden(self):
        for traits in (
            {"roles": ["empty"]},
            {"materials": ["void"]},
        ):
            result = validate_slip(_v2_profile(forbidden_traits=traits))
            self.assertFalse(result.ok, traits)

    def test_unknown_role_material_and_keys_are_rejected(self):
        for traits in (
            {"roles": ["wings"]},
            {"materials": ["plasma"]},
            {"colors": ["#ff0000"]},
            {"roles": []},
        ):
            result = validate_slip(_v2_profile(forbidden_traits=traits))
            self.assertFalse(result.ok, traits)

    def test_forbidding_a_required_organ_cell_role_is_a_contradiction(self):
        # The profile requires the sensor organ; forbidding eye cells
        # would make every compliant grid impossible.
        result = validate_slip(
            _v2_profile(forbidden_traits={"roles": ["eye"]})
        )
        self.assertFalse(result.ok)
        self.assertTrue(
            any("required" in error for error in result.errors),
            result.errors,
        )

    def test_vocabularies_pin_to_the_grid_genome_schema(self):
        schema = json.loads(GRID_SCHEMA_PATH.read_text(encoding="utf-8"))
        cell = schema["$defs"]["cell"]["properties"]
        self.assertEqual(
            set(cell["role"]["enum"]) - {"empty"}, FORBIDDABLE_ROLES
        )
        self.assertEqual(
            set(cell["material"]["enum"]) - {"void"}, FORBIDDABLE_MATERIALS
        )


class ForbiddenTraitsAlignmentTests(unittest.TestCase):
    def setUp(self):
        self.seed = build_seed_grids()[0]  # body/eye/mouth cells, lcd

    def test_clean_grid_stays_aligned_under_forbidden_traits(self):
        profile = _v2_profile()  # forbids shell/light; the seed has neither
        result = is_grid_aligned(self.seed, profile)
        self.assertEqual([], result.errors)

    def test_grid_containing_a_forbidden_role_fails_alignment(self):
        profile = _v2_profile(
            grid={
                "allowed_palettes": ["lcd_green"],
                "body_mass_min": 4,
                "body_mass_max": 24,
                "required_organ_roles": ["expression"],
            },
            forbidden_traits={"roles": ["eye"]},
        )
        self.assertTrue(validate_slip(profile).ok)
        result = is_grid_aligned(self.seed, profile)
        self.assertFalse(result.ok)
        self.assertTrue(
            any("eye" in error and "forbidden" in error for error in result.errors),
            result.errors,
        )

    def test_grid_containing_a_forbidden_material_fails_alignment(self):
        materials = {cell["material"] for cell in self.seed["cells"]}
        target = sorted(materials - {"void"})[0]
        profile = _v2_profile(forbidden_traits={"materials": [target]})
        result = is_grid_aligned(self.seed, profile)
        self.assertFalse(result.ok)
        self.assertTrue(
            any(target in error for error in result.errors), result.errors
        )

    def test_v1_profiles_are_untouched_by_the_ladder(self):
        profile = _v2_profile(slip_version="0.1.0")
        del profile["forbidden_traits"]
        self.assertTrue(validate_slip(profile).ok)
        self.assertTrue(is_grid_aligned(self.seed, profile).ok)


class ForbiddenTraitsFixtureTests(unittest.TestCase):
    def test_v2_fixture_validates_and_failure_fixtures_fail(self):
        valid = ROOT / "data" / "slips" / "valid" / "slip_v2_no_shell.json"
        self.assertTrue(valid.exists())
        self.assertTrue(
            validate_slip(json.loads(valid.read_text(encoding="utf-8"))).ok
        )
        for name in (
            "slip_v1_with_forbidden_traits.json",
            "slip_v2_forbids_required.json",
        ):
            path = ROOT / "data" / "slips" / "failure_cases" / name
            self.assertTrue(path.exists(), name)
            self.assertFalse(
                validate_slip(
                    json.loads(path.read_text(encoding="utf-8"))
                ).ok,
                name,
            )


if __name__ == "__main__":
    unittest.main()
