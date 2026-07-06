"""Parity pin: lab SLIP authority vs the four promoted ``_slip`` mirrors.

Runs the Stage 0 lab authority (``labs/grid_genome/slip.py`` — dual-version
``validate_slip`` per decision records 0012/0013 and the forbidden-traits
enforcement in ``is_grid_aligned``) and the four private package mirrors
(``mecha_engine.generation._slip``, ``mecha_engine.lifecycle._slip``,
``mecha_engine.repair._slip``, ``mecha_engine.runtime._slip`` through the
package src layout) over the same profiles and grids, and asserts the
error lists identical verbatim on BOTH v0.1 (frozen) and v0.2 (ladder)
inputs.

Documented equivalence scope: each mirror is a verbatim semantic port of
the lab authority minus ``v01_projection`` (the projection adapter is not
needed package-side — decision record 0013 lets the package consume v0.2
profiles directly). The mirrors are private modules; this pin deliberately
imports them by their private paths because the whole point is that all
four private copies stay byte-equivalent to the lab authority — the
public consumers (generation, lifecycle, repair, runtime contract suites)
prove the surfaces, this file proves the source semantics.

Direction note: labs may import the package for regression evidence; the
reverse (package importing labs) stays forbidden, and this file lives on
the lab side precisely so the package tree keeps zero lab references.
"""

import json
import sys
import unittest
from copy import deepcopy
from pathlib import Path


LAB_DIR = Path(__file__).resolve().parent
REPO_ROOT = LAB_DIR.parents[1]
PACKAGE_SRC = REPO_ROOT / "packages" / "mecha_engine" / "src"
if str(LAB_DIR) not in sys.path:
    sys.path.insert(0, str(LAB_DIR))
if str(PACKAGE_SRC) not in sys.path:
    sys.path.insert(0, str(PACKAGE_SRC))

import slip as lab_slip  # noqa: E402
from corpus_builder import build_seed_grids  # noqa: E402

from mecha_engine.generation import _slip as generation_slip  # noqa: E402
from mecha_engine.lifecycle import _slip as lifecycle_slip  # noqa: E402
from mecha_engine.repair import _slip as repair_slip  # noqa: E402
from mecha_engine.runtime import _slip as runtime_slip  # noqa: E402


MIRRORS = {
    "generation": generation_slip,
    "lifecycle": lifecycle_slip,
    "repair": repair_slip,
    "runtime": runtime_slip,
}
VALID_DIR = REPO_ROOT / "data" / "slips" / "valid"
FAILURE_DIR = REPO_ROOT / "data" / "slips" / "failure_cases"


def _load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def _v2_profile(**overrides) -> dict:
    profile = _load(VALID_DIR / "slip_lcd_seed.json")
    profile["slip_version"] = "0.2.0"
    profile["profile_id"] = "slip_v2_parity_probe"
    profile.update(overrides)
    return profile


def _synthetic_profiles() -> list[tuple[str, dict]]:
    """v0.1 and v0.2 probes covering every ladder rung, both directions."""
    profiles: list[tuple[str, dict]] = [
        ("v1_baseline", _load(VALID_DIR / "slip_lcd_seed.json")),
        ("v2_bare", _v2_profile()),
        (
            "v2_full_ladder",
            _v2_profile(
                forbidden_traits={"roles": ["shell"], "materials": ["light"]},
                risk_tolerances={"mutation": 0.6},
                learning_switches={"mutation_risk_scorer": True},
                lineage_preferences={"parent_selection": "fitness_weighted"},
            ),
        ),
        ("unknown_version", _v2_profile(slip_version="0.3.0")),
        ("not_an_object", "not a profile"),  # type: ignore[list-item]
    ]
    # Every ladder key on a v0.1 profile is version-gated.
    for key, value in [
        ("forbidden_traits", {"roles": ["shell"]}),
        ("risk_tolerances", {"mutation": 0.5}),
        ("learning_switches", {"mutation_risk_scorer": False}),
        ("lineage_preferences", {"parent_selection": "uniform"}),
    ]:
        gated = _load(VALID_DIR / "slip_lcd_seed.json")
        gated[key] = deepcopy(value)
        profiles.append((f"v1_gated_{key}", gated))
    # Bad ladder shapes, one rung at a time.
    for name, field, value in [
        ("bad_tolerance_range", "risk_tolerances", {"mutation": 1.5}),
        ("bad_tolerance_bool", "risk_tolerances", {"mutation": True}),
        ("bad_tolerance_key", "risk_tolerances", {"unknown": 0.5}),
        ("bad_tolerance_shape", "risk_tolerances", "high"),
        ("bad_switch_thread", "learning_switches", {"unknown_thread": False}),
        ("bad_switch_value", "learning_switches", {"mutation_risk_scorer": 0}),
        ("bad_switch_empty", "learning_switches", {}),
        ("bad_switch_shape", "learning_switches", ["mutation_risk_scorer"]),
        ("bad_mode", "lineage_preferences", {"parent_selection": "strongest"}),
        ("bad_mode_key", "lineage_preferences", {"unknown": "uniform"}),
        ("bad_mode_shape", "lineage_preferences", "uniform"),
        ("bad_traits_vocab", "forbidden_traits", {"roles": ["wing"]}),
        ("bad_traits_repeat", "forbidden_traits", {"roles": ["shell", "shell"]}),
        ("bad_traits_empty", "forbidden_traits", {}),
        ("bad_traits_extra", "forbidden_traits", {"colors": ["red"]}),
        ("contradiction", "forbidden_traits", {"roles": ["eye"]}),
    ]:
        profiles.append((name, _v2_profile(**{field: value})))
    return profiles


class PackageSlipValidateParityTests(unittest.TestCase):
    def test_fixture_corpus_outcomes_identical_verbatim(self):
        fixtures = sorted(VALID_DIR.glob("*.json")) + sorted(
            FAILURE_DIR.glob("*.json")
        )
        self.assertGreater(len(fixtures), 10)
        for path in fixtures:
            profile = _load(path)
            lab_result = lab_slip.validate_slip(profile)
            for module_name, mirror in MIRRORS.items():
                with self.subTest(fixture=path.name, mirror=module_name):
                    mirror_result = mirror.validate_slip(profile)
                    self.assertEqual(lab_result.ok, mirror_result.ok)
                    self.assertEqual(lab_result.errors, mirror_result.errors)

    def test_valid_fixtures_pass_and_failure_fixtures_carry_errors(self):
        for path in sorted(VALID_DIR.glob("*.json")):
            self.assertEqual([], lab_slip.validate_slip(_load(path)).errors, path.name)
        for path in sorted(FAILURE_DIR.glob("*.json")):
            self.assertTrue(lab_slip.validate_slip(_load(path)).errors, path.name)

    def test_synthetic_ladder_probes_identical_verbatim(self):
        for name, profile in _synthetic_profiles():
            lab_result = lab_slip.validate_slip(profile)
            for module_name, mirror in MIRRORS.items():
                with self.subTest(probe=name, mirror=module_name):
                    mirror_result = mirror.validate_slip(profile)
                    self.assertEqual(lab_result.ok, mirror_result.ok)
                    self.assertEqual(lab_result.errors, mirror_result.errors)


class PackageSlipAlignmentParityTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.grids = build_seed_grids()[:10]
        cls.profiles = [
            ("v1_baseline", _load(VALID_DIR / "slip_lcd_seed.json")),
            ("v2_fixture", _load(VALID_DIR / "slip_v2_no_shell.json")),
            (
                "v2_binding_forbidden",
                _v2_profile(
                    forbidden_traits={"roles": ["body"], "materials": ["hard"]}
                ),
            ),
        ]

    def test_alignment_outcomes_identical_verbatim_v1_and_v2(self):
        for profile_name, profile in self.profiles:
            for grid in self.grids:
                lab_result = lab_slip.is_grid_aligned(grid, profile)
                for module_name, mirror in MIRRORS.items():
                    with self.subTest(
                        profile=profile_name,
                        grid=grid["grid_id"],
                        mirror=module_name,
                    ):
                        mirror_result = mirror.is_grid_aligned(grid, profile)
                        self.assertEqual(lab_result.ok, mirror_result.ok)
                        self.assertEqual(lab_result.errors, mirror_result.errors)

    def test_binding_forbidden_traits_name_the_offending_values(self):
        _, profile = self.profiles[2]
        result = lab_slip.is_grid_aligned(self.grids[0], profile)
        self.assertIn("forbidden role present in grid: body", result.errors)
        self.assertIn("forbidden material present in grid: hard", result.errors)


if __name__ == "__main__":
    unittest.main()
