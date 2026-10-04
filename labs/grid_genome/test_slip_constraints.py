import json
import sys
import unittest
from pathlib import Path

from constrained_generator import build_constrained_corpus, run_baseline
from corpus_builder import build_seed_grids
from slip import is_grid_aligned, validate_slip

ROOT = Path(__file__).resolve().parents[2]
SLIP_VALIDATOR_DIR = str(ROOT / "labs" / "slip_validator")
if SLIP_VALIDATOR_DIR not in sys.path:
    sys.path.insert(0, SLIP_VALIDATOR_DIR)

from slip_validator import validate_profile  # noqa: E402

VALID_PROFILE_PATHS = sorted((ROOT / "data" / "slips" / "valid").glob("*.json"))
FAILURE_CASE_PATHS = sorted((ROOT / "data" / "slips" / "failure_cases").glob("*.json"))
EXAMPLE_PROFILE_PATHS = sorted(
    (ROOT / "research" / "slip" / "slip_examples").glob("*.json")
)


def valid_slip():
    return {
        "slip_version": "0.1.0",
        "profile_id": "slip_lcd_seed",
        "name": "LCD Seed Companion",
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
        "behavior": {
            "curiosity": 0.6,
            "neediness": 0.4,
            "sleepiness": 0.5,
        },
        "survival_weights": {
            "stability": 0.5,
            "novelty": 0.25,
            "bond": 0.25,
        },
    }


class SlipConstraintTests(unittest.TestCase):
    def test_valid_slip_profile_passes(self):
        result = validate_slip(valid_slip())

        self.assertTrue(result.ok, result.errors)

    def test_invalid_slip_profile_rejects_bad_weights(self):
        profile = valid_slip()
        profile["behavior"]["curiosity"] = 1.2

        result = validate_slip(profile)

        self.assertFalse(result.ok)
        self.assertIn("behavior curiosity outside 0..1: 1.2", result.errors)

    def test_validate_slip_agrees_with_authoritative_validator_on_full_corpus(self):
        self.assertEqual(15, len(FAILURE_CASE_PATHS))
        self.assertEqual(5, len(VALID_PROFILE_PATHS))
        self.assertEqual(5, len(EXAMPLE_PROFILE_PATHS))

        for path in VALID_PROFILE_PATHS + FAILURE_CASE_PATHS + EXAMPLE_PROFILE_PATHS:
            with self.subTest(path=str(path)):
                payload = json.loads(path.read_text(encoding="utf-8"))
                lab_ok = validate_slip(payload).ok
                authoritative_ok = validate_profile(payload)["ok"]
                self.assertEqual(authoritative_ok, lab_ok)

    def test_validate_slip_rejects_extra_and_missing_section_keys(self):
        extra_key = valid_slip()
        extra_key["survival_weights"]["dominance"] = 0.5
        result = validate_slip(extra_key)
        self.assertFalse(result.ok)
        self.assertIn("survival_weights dominance is not allowed", result.errors)

        missing_key = valid_slip()
        del missing_key["behavior"]["neediness"]
        result = validate_slip(missing_key)
        self.assertFalse(result.ok)
        self.assertIn("behavior neediness is required", result.errors)

    def test_validate_slip_rejects_boolean_body_mass_and_duplicates(self):
        boolean_mass = valid_slip()
        boolean_mass["grid"]["body_mass_min"] = True
        result = validate_slip(boolean_mass)
        self.assertFalse(result.ok)
        self.assertIn("grid body mass bounds must be integers", result.errors)

        duplicate_palette = valid_slip()
        duplicate_palette["grid"]["allowed_palettes"] = ["lcd_green", "lcd_green"]
        result = validate_slip(duplicate_palette)
        self.assertFalse(result.ok)
        self.assertIn("grid allowed palette is duplicated: lcd_green", result.errors)

    def test_validate_slip_rejects_bad_profile_id_pattern(self):
        profile = valid_slip()
        profile["profile_id"] = "Slip-LCD Seed"
        result = validate_slip(profile)
        self.assertFalse(result.ok)
        self.assertIn(
            "profile_id must contain only lowercase letters, digits, and underscores",
            result.errors,
        )

    def test_is_grid_aligned_rejects_each_misaligned_surface(self):
        profile = valid_slip()
        aligned = build_constrained_corpus(
            build_seed_grids(), count=1, rng_seed=313, slip=profile
        )[0]

        wrong_palette = json.loads(json.dumps(aligned))
        wrong_palette["palette"]["palette_id"] = "amber_terminal"
        self.assertFalse(is_grid_aligned(wrong_palette, profile).ok)

        too_light = json.loads(json.dumps(aligned))
        too_light["cells"] = [
            cell for cell in too_light["cells"] if cell.get("organ") != "core"
        ]
        self.assertFalse(is_grid_aligned(too_light, profile).ok)

        missing_role = json.loads(json.dumps(aligned))
        missing_role["organs"] = {
            name: organ
            for name, organ in missing_role["organs"].items()
            if organ.get("role") != "sensor"
        }
        self.assertFalse(is_grid_aligned(missing_role, profile).ok)

        hot_mutation = json.loads(json.dumps(aligned))
        hot_mutation["mutation"]["cell_mutation_rate"] = 0.99
        self.assertFalse(is_grid_aligned(hot_mutation, profile).ok)

    def test_mass_bounds_scale_by_reference_canvas_at_16x16(self):
        # DR 0030: bounds are 8x8-reference-denominated and scale by
        # area — the zoo's 4..24 admits the 16x16 corpus (16..96), and a
        # violation message reports the EFFECTIVE bounds.
        from corpus_builder import build_seed_grids_16

        profile = valid_slip()
        lcd_16 = [
            grid
            for grid in build_seed_grids_16()
            if grid["palette"]["palette_id"] == "lcd_green"
        ]
        self.assertEqual(10, len(lcd_16))
        for grid in lcd_16:
            with self.subTest(grid_id=grid["grid_id"]):
                alignment = is_grid_aligned(grid, profile)
                self.assertTrue(alignment.ok, alignment.errors)

        tight = json.loads(json.dumps(profile))
        tight["grid"]["body_mass_min"] = 4
        tight["grid"]["body_mass_max"] = 5
        heavy = next(
            grid for grid in lcd_16 if grid["grid_id"].endswith("beetle")
        )
        result = is_grid_aligned(heavy, tight)
        self.assertFalse(result.ok)
        self.assertIn("body mass 54 outside SLIP bounds 16..20", result.errors)

    def test_mass_bounds_are_the_authored_values_at_8x8(self):
        # DR 0030 identity gate: at the reference canvas the scaling is
        # exact, so historical verdicts and error strings are unchanged.
        profile = valid_slip()
        aligned = build_constrained_corpus(
            build_seed_grids(), count=1, rng_seed=313, slip=profile
        )[0]
        tight = json.loads(json.dumps(profile))
        tight["grid"]["body_mass_min"] = 1
        tight["grid"]["body_mass_max"] = 2
        result = is_grid_aligned(aligned, tight)
        self.assertFalse(result.ok)
        self.assertTrue(
            any(
                error.endswith("outside SLIP bounds 1..2")
                for error in result.errors
            ),
            result.errors,
        )

    def test_is_grid_aligned_reports_non_numeric_mutation_instead_of_crashing(self):
        profile = valid_slip()
        aligned = build_constrained_corpus(
            build_seed_grids(), count=1, rng_seed=313, slip=profile
        )[0]

        corrupt = json.loads(json.dumps(aligned))
        corrupt["mutation"]["cell_mutation_rate"] = "high"
        result = is_grid_aligned(corrupt, profile)
        self.assertFalse(result.ok)
        self.assertIn("mutation cell_mutation_rate must be a number: high", result.errors)

        boolean = json.loads(json.dumps(aligned))
        boolean["mutation"]["organ_shift_rate"] = True
        result = is_grid_aligned(boolean, profile)
        self.assertFalse(result.ok)
        self.assertIn("mutation organ_shift_rate must be a number: True", result.errors)

    def test_slip_constrained_generation_outputs_valid_aligned_grids(self):
        profile = valid_slip()

        generated = build_constrained_corpus(
            build_seed_grids(), count=50, rng_seed=313, slip=profile
        )
        report = run_baseline(generated)

        self.assertEqual(50, report["candidate_count"])
        self.assertEqual(50, report["valid_count"])
        for grid in generated:
            with self.subTest(grid_id=grid["grid_id"]):
                self.assertTrue(is_grid_aligned(grid, profile).ok)


if __name__ == "__main__":
    unittest.main()
