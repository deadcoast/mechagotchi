import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
LAB_DIR = Path(__file__).resolve().parent
GRID_GENOME = ROOT / "labs" / "grid_genome"
for path in [LAB_DIR, GRID_GENOME]:
    if str(path) not in sys.path:
        sys.path.insert(0, str(path))

from slip import v01_projection, validate_slip  # noqa: E402

from mecha_engine_runtime_loop import (  # noqa: E402
    run_mecha_engine_evolution_loop,
)


def _v2_profile(parent_selection: str) -> dict:
    profile = json.loads(
        (ROOT / "data/slips/valid/slip_lcd_seed.json").read_text(
            encoding="utf-8"
        )
    )
    profile["slip_version"] = "0.2.0"
    profile["profile_id"] = "slip_v2_lineage_test"
    profile["lineage_preferences"] = {"parent_selection": parent_selection}
    return profile


class LineagePreferencesValidationTests(unittest.TestCase):
    """DR 0012 rung T3.4, version-gated like every ladder field."""

    def test_v2_profile_with_lineage_preferences_validates(self):
        result = validate_slip(_v2_profile("fitness_weighted"))
        self.assertEqual([], result.errors)

    def test_v1_profile_with_lineage_preferences_is_version_gated(self):
        profile = _v2_profile("uniform")
        profile["slip_version"] = "0.1.0"
        result = validate_slip(profile)
        self.assertFalse(result.ok)
        self.assertTrue(any("0.2.0" in error for error in result.errors))

    def test_bad_shapes_are_rejected(self):
        for preferences in (
            {"parent_selection": "strongest"},
            {"parent_selection": True},
            {"unknown": "uniform"},
            {},
            "uniform",
        ):
            profile = _v2_profile("uniform")
            profile["lineage_preferences"] = preferences
            self.assertFalse(validate_slip(profile).ok, preferences)


class V01ProjectionTests(unittest.TestCase):
    """The package-boundary adapter (DR 0012 rule 4)."""

    def test_v1_profiles_pass_through_unchanged(self):
        profile = json.loads(
            (ROOT / "data/slips/valid/slip_lcd_seed.json").read_text(
                encoding="utf-8"
            )
        )
        self.assertIs(profile, v01_projection(profile))

    def test_v2_profiles_project_to_a_valid_v1_baseline(self):
        profile = _v2_profile("fitness_weighted")
        projected = v01_projection(profile)
        self.assertEqual("0.1.0", projected["slip_version"])
        self.assertNotIn("lineage_preferences", projected)
        self.assertTrue(validate_slip(projected).ok)
        # The source profile is not mutated.
        self.assertEqual("0.2.0", profile["slip_version"])


class FitnessWeightedParentingTests(unittest.TestCase):
    """The rung's consumer: v0.2 profiles steer evolution parenting."""

    KW = dict(
        generations=2,
        population=4,
        damage_cycles=1,
        ticks=8,
        repair_epochs=20,
        rng_seed=20260512,
    )

    def test_v2_profile_drives_evolution_through_the_projection(self):
        report = run_mecha_engine_evolution_loop(
            slip_profile=_v2_profile("fitness_weighted"), **self.KW
        )
        self.assertEqual(
            "fitness_weighted", report["parent_selection"]
        )
        self.assertEqual(
            "archive_elites_fitness_weighted",
            report["generations"][1]["parent_source"],
        )

    def test_selection_modes_pick_different_parents(self):
        uniform = run_mecha_engine_evolution_loop(
            slip_profile=_v2_profile("uniform"), **self.KW
        )
        weighted = run_mecha_engine_evolution_loop(
            slip_profile=_v2_profile("fitness_weighted"), **self.KW
        )
        self.assertEqual("uniform", uniform["parent_selection"])
        uniform_parents = [
            c["parent_grid_id"]
            for c in uniform["generations"][1]["creatures"]
        ]
        weighted_parents = [
            c["parent_grid_id"]
            for c in weighted["generations"][1]["creatures"]
        ]
        self.assertNotEqual(uniform_parents, weighted_parents)

    def test_default_run_carries_no_rung_keys(self):
        report = run_mecha_engine_evolution_loop(**self.KW)
        self.assertNotIn("parent_selection", report)
        self.assertEqual(
            "archive_elites", report["generations"][1]["parent_source"]
        )


if __name__ == "__main__":
    unittest.main()
