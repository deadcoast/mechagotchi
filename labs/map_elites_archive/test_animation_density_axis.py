"""Cycle 22 L4: animation_density judged as a CANDIDATE descriptor axis.

`deep-research.md:530` shows a four-axis archive descriptor
`{symmetry, visual_complexity, neediness, animation_density}` — but it
shows it in a worked JSON example and **never defines the axis**. So
the definition here is one this lab CHOSE, grounded in the engine's own
clip tables, and it is labelled as chosen rather than documented.

These pins fix the contract: the axis is derived from the clip model's
own role tables (never a hardcoded copy), the gates are pre-registered
with refusal first-class, the coverage cost of a fourth axis is
reported rather than hidden, and the documented selection criterion —
inter-rater interpretability, which needs the owner-deferred human
panel — is BLOCKED explicitly instead of being met by a proxy.
"""

import json
import sys
import tempfile
import unittest
from pathlib import Path

LAB_DIR = Path(__file__).resolve().parent
if str(LAB_DIR) not in sys.path:
    sys.path.insert(0, str(LAB_DIR))

from animation_density_axis import (  # noqa: E402
    ANIMATING_ROLES,
    ARTIFACT_ID,
    INDEPENDENCE_BAR,
    DISCRIMINATION_BAR,
    TARGET_GEOMETRY,
    animation_density,
    build_animation_density_report,
    judge_axis,
    pearson,
    realised_idle_density,
    write_animation_density_artifacts,
)

TINY = dict(population_count=120)


def _grid(roles: list[str]) -> dict:
    """A minimal grid whose cells carry the given roles in a row."""
    return {
        "grid_id": "t",
        "grid_size": [16, 16],
        "cells": [
            {"x": i, "y": 0, "role": role, "visual": "B", "material": "hard",
             "organ": "", "animation_anchor": i == 0}
            for i, role in enumerate(roles)
        ],
    }


class AnimatingRoleTests(unittest.TestCase):
    def test_the_role_set_comes_from_the_clip_model_not_a_copy(self):
        # If the engine's clip tables gain or lose an animating role,
        # this axis must follow automatically — a hardcoded copy would
        # drift silently, which is the mirror-never-import hazard.
        from clip_model import (
            DECOR_BOB_ROLES,
            FLICKER_ROLES,
            JOINT_FLEX_ROLES,
            LIMB_STEP_ROLES,
            SWAY_ROLES,
        )

        expected = (
            set(SWAY_ROLES)
            | set(FLICKER_ROLES)
            | set(LIMB_STEP_ROLES)
            | set(JOINT_FLEX_ROLES)
            | set(DECOR_BOB_ROLES)
        )
        self.assertEqual(expected, set(ANIMATING_ROLES))

    def test_a_creature_of_pure_body_has_density_zero(self):
        self.assertEqual(0.0, animation_density(_grid(["body", "body", "body"])))

    def test_a_creature_of_pure_limbs_has_density_one(self):
        self.assertEqual(1.0, animation_density(_grid(["limb", "limb"])))

    def test_density_is_the_animating_fraction_of_live_cells(self):
        # two of four cells animate
        measured = animation_density(_grid(["body", "limb", "eye", "antenna"]))
        self.assertAlmostEqual(0.5, measured, places=9)

    def test_an_empty_grid_is_refused_rather_than_dividing_by_zero(self):
        with self.assertRaises(ValueError):
            animation_density({"grid_id": "t", "grid_size": [16, 16], "cells": []})


class RealisedMotionTests(unittest.TestCase):
    def test_realised_idle_density_never_exceeds_the_potential(self):
        # The potential measure counts cells the engine WOULD animate;
        # collision and bounds skips mean fewer actually move. The
        # realised figure bounds the potential from below — never the
        # other way round. Measured on REAL committed creatures, since
        # the clip model consumes whole engine grids.
        from corpus_builder import build_seed_grids_16

        for grid in build_seed_grids_16()[:8]:
            with self.subTest(grid=grid["grid_id"]):
                self.assertLessEqual(
                    realised_idle_density(grid), animation_density(grid)
                )


class PearsonTests(unittest.TestCase):
    def test_a_perfect_line_is_one(self):
        self.assertAlmostEqual(1.0, pearson([1, 2, 3], [2, 4, 6]), places=9)

    def test_a_perfect_inverse_is_minus_one(self):
        self.assertAlmostEqual(-1.0, pearson([1, 2, 3], [6, 4, 2]), places=9)

    def test_a_constant_series_has_no_correlation_and_says_so(self):
        # Zero variance is not "uncorrelated" — it is undefined, and
        # reporting 0.0 would launder a degenerate axis into an
        # independent-looking one.
        self.assertIsNone(pearson([1, 1, 1], [1, 2, 3]))


class PreRegisteredGateTests(unittest.TestCase):
    def test_all_machine_gates_passing_still_does_not_adopt(self):
        # The documented selection criterion (inter-rater
        # interpretability >= 0.7) needs the owner-deferred human
        # panel. The best available verdict is therefore "adoptable
        # pending a BLOCKED clause" — never "adopt".
        judged = judge_axis(
            supports_full_bins=True,
            max_abs_correlation=0.1,
            discrimination=0.9,
        )
        self.assertEqual("adoptable_pending_blocked_clause", judged["verdict"])
        self.assertTrue(judged["interpretability_clause_blocked"])

    def test_a_degenerate_axis_is_refused(self):
        judged = judge_axis(
            supports_full_bins=False,
            max_abs_correlation=0.1,
            discrimination=0.9,
        )
        self.assertEqual("refuse", judged["verdict"])
        self.assertIn("spread", judged["failed_gates"])

    def test_an_axis_that_merely_restates_an_incumbent_is_refused(self):
        judged = judge_axis(
            supports_full_bins=True,
            max_abs_correlation=INDEPENDENCE_BAR + 0.01,
            discrimination=0.9,
        )
        self.assertEqual("refuse", judged["verdict"])
        self.assertIn("independence", judged["failed_gates"])

    def test_an_axis_that_splits_nothing_new_is_refused(self):
        judged = judge_axis(
            supports_full_bins=True,
            max_abs_correlation=0.1,
            discrimination=DISCRIMINATION_BAR - 0.01,
        )
        self.assertEqual("refuse", judged["verdict"])
        self.assertIn("discrimination", judged["failed_gates"])


class AnimationDensityReportTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.report = build_animation_density_report(**TINY)

    def test_the_report_carries_the_stage0_contract(self):
        for key in (
            "artifact_id",
            "status",
            "date",
            "purpose",
            "source_artifacts",
            "metrics",
            "closed_states",
            "blocked_states",
            "decision",
            "next_research_step",
        ):
            with self.subTest(key=key):
                self.assertIn(key, self.report)
        self.assertEqual(ARTIFACT_ID, self.report["artifact_id"])

    def test_the_definition_is_declared_as_chosen_not_documented(self):
        # The honesty rule for this slice: the documentation names the
        # axis and never defines it.
        self.assertIn("definition_provenance", self.report["metrics"])
        self.assertIn(
            "chosen", self.report["metrics"]["definition_provenance"].lower()
        )

    def test_the_target_geometry_is_named(self):
        # L3 found the repo runs two geometries; a new axis must say
        # which one it would join.
        self.assertEqual(TARGET_GEOMETRY, self.report["metrics"]["target_geometry"])

    def test_correlations_against_every_incumbent_axis_are_reported(self):
        correlations = self.report["metrics"]["correlation_with_incumbent"]
        for axis in ("symmetry", "visual_complexity", "behavior_neediness"):
            with self.subTest(axis=axis):
                self.assertIn(axis, correlations)

    def test_the_coverage_cost_of_a_fourth_axis_is_reported(self):
        cost = self.report["metrics"]["coverage_cost"]
        self.assertEqual(512, cost["cells_3_axis"])
        self.assertEqual(4096, cost["cells_4_axis"])

    def test_the_verdict_follows_the_pre_registered_rule(self):
        metrics = self.report["metrics"]
        expected = judge_axis(
            supports_full_bins=metrics["edge_diagnostics"]["supports_full_bins"],
            max_abs_correlation=metrics["max_abs_correlation"],
            discrimination=metrics["discrimination"],
        )["verdict"]
        self.assertEqual(expected, self.report["decision"]["verdict"])

    def test_the_blocked_human_clause_is_named_in_blocked_states(self):
        blocked = " ".join(self.report["blocked_states"]).lower()
        self.assertIn("interpretability", blocked)

    def test_the_artifact_writes_and_reloads(self):
        with tempfile.TemporaryDirectory() as tmp:
            written = write_animation_density_artifacts(Path(tmp), self.report)
            self.assertTrue(written)
            for path in written:
                reloaded = json.loads(Path(path).read_text(encoding="utf-8"))
                self.assertEqual(ARTIFACT_ID, reloaded["artifact_id"])


if __name__ == "__main__":
    unittest.main()
