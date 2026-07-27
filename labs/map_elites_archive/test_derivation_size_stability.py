"""Pins for cycle 24 N1: do 600 creatures determine the octile edges?

Written BEFORE the module (the RED run is pasted into the experiment
report). The pins assert the pre-registered RULE and the arithmetic —
never the measured values, which are the study's output.

The one integration pin is deliberate and is the instrument's own
validation: at ``derivation_count = 600`` on M2's exact seed pair, this
module's re-addressing statistic must reproduce DR 0046's committed
incumbent control of **0.2 exactly**. If it does not, the ladder is
measuring something other than what M2 measured, and every number on it
is uninterpretable.
"""

import json
import sys
import tempfile
import unittest
from pathlib import Path

LAB_DIR = Path(__file__).resolve().parent
ROOT = LAB_DIR.parents[1]
if str(LAB_DIR) not in sys.path:
    sys.path.insert(0, str(LAB_DIR))

from derivation_size_stability import (  # noqa: E402
    ARTIFACT_ID,
    DERIVATION_SIZE_LADDER,
    E1_DERIVATION_COUNT,
    PRE_REGISTERED_RULE,
    RECIPES,
    REPLICATE_SEED_COUNT,
    SAMPLING_THEORY_SLOPE,
    SLOPE_CONTROL_FACTOR,
    build_derivation_size_stability_report,
    derivation_replicate_seeds,
    disjoint_pairs,
    judge_derivation_protocol,
    judge_determined_size,
    log_log_slope,
    measure_derivation_unit,
    per_axis_readdressing,
    readdressing_rate,
    write_derivation_size_stability_artifacts,
)


class LadderShapeTests(unittest.TestCase):
    def test_ladder_contains_e1s_own_derivation_count(self):
        # The question is "do 600 creatures determine the edges", so the
        # ladder must be able to answer it AT 600.
        self.assertEqual(E1_DERIVATION_COUNT, 600)
        self.assertIn(E1_DERIVATION_COUNT, DERIVATION_SIZE_LADDER)

    def test_ladder_is_strictly_increasing(self):
        self.assertEqual(
            list(DERIVATION_SIZE_LADDER), sorted(set(DERIVATION_SIZE_LADDER))
        )

    def test_ladder_brackets_e1_on_both_sides(self):
        # A one-sided ladder could only say "bigger is better"; bracketing
        # is what lets the study locate a size at which movement stops.
        self.assertLess(min(DERIVATION_SIZE_LADDER), E1_DERIVATION_COUNT)
        self.assertGreater(max(DERIVATION_SIZE_LADDER), E1_DERIVATION_COUNT)

    def test_ladder_spans_at_least_one_order_of_magnitude(self):
        # A log-log slope needs a real lever arm.
        self.assertGreaterEqual(
            max(DERIVATION_SIZE_LADDER) / min(DERIVATION_SIZE_LADDER), 10
        )

    def test_every_ladder_size_can_support_eight_octiles(self):
        # derive_scale_bin_edges refuses fewer values than bins.
        self.assertGreaterEqual(min(DERIVATION_SIZE_LADDER), 8)

    def test_replicate_seeds_are_distinct_and_pairable(self):
        seeds = derivation_replicate_seeds()
        self.assertEqual(len(seeds), REPLICATE_SEED_COUNT)
        self.assertEqual(len(set(seeds)), REPLICATE_SEED_COUNT)
        self.assertEqual(REPLICATE_SEED_COUNT % 2, 0)

    def test_both_recipes_are_measured(self):
        self.assertEqual(tuple(RECIPES), ("incumbent", "probe"))


class DisjointPairTests(unittest.TestCase):
    def test_pairs_are_disjoint_and_cover_every_seed(self):
        pairs = disjoint_pairs([1, 2, 3, 4, 5, 6])
        self.assertEqual(pairs, [(1, 2), (3, 4), (5, 6)])
        flattened = [seed for pair in pairs for seed in pair]
        self.assertEqual(sorted(flattened), [1, 2, 3, 4, 5, 6])

    def test_first_pair_is_the_first_two_seeds(self):
        # Pair 0 must be M2's pair, so the ladder reproduces DR 0046.
        self.assertEqual(disjoint_pairs([10, 20, 30, 40])[0], (10, 20))

    def test_odd_seed_count_is_refused(self):
        # A dangling seed would silently reduce the replicate count.
        with self.assertRaises(ValueError):
            disjoint_pairs([1, 2, 3])


class ReaddressingRateTests(unittest.TestCase):
    def test_identical_addressing_is_zero(self):
        addresses = [(0, 1, 2), (3, 4, 5)]
        self.assertEqual(readdressing_rate(addresses, addresses), 0.0)

    def test_completely_different_addressing_is_one(self):
        self.assertEqual(
            readdressing_rate([(0, 0, 0), (1, 1, 1)], [(1, 1, 1), (0, 0, 0)]),
            1.0,
        )

    def test_one_axis_off_by_one_counts_as_a_whole_address_change(self):
        # A niche is a whole address (DR 0046's unit).
        self.assertEqual(
            readdressing_rate([(0, 0, 0), (0, 0, 0)], [(0, 0, 1), (0, 0, 0)]),
            0.5,
        )

    def test_mismatched_population_lengths_are_refused(self):
        with self.assertRaises(ValueError):
            readdressing_rate([(0, 0, 0)], [(0, 0, 0), (1, 1, 1)])

    def test_empty_population_is_refused(self):
        with self.assertRaises(ValueError):
            readdressing_rate([], [])


class PerAxisReaddressingTests(unittest.TestCase):
    def test_change_is_attributed_to_the_axis_that_moved(self):
        per_axis = per_axis_readdressing(
            [(0, 0, 0), (0, 0, 0)], [(0, 1, 0), (0, 0, 0)]
        )
        self.assertEqual(per_axis["symmetry"], 0.0)
        self.assertEqual(per_axis["visual_complexity"], 0.5)
        self.assertEqual(per_axis["behavior_neediness"], 0.0)

    def test_per_axis_rates_never_exceed_the_whole_address_rate_sum(self):
        first = [(0, 0, 0), (1, 1, 1)]
        second = [(1, 1, 1), (1, 1, 1)]
        per_axis = per_axis_readdressing(first, second)
        self.assertLessEqual(
            readdressing_rate(first, second), sum(per_axis.values())
        )


class LogLogSlopeTests(unittest.TestCase):
    def test_exact_inverse_root_law_recovers_the_theory_slope(self):
        sizes = [100, 400, 1600, 6400]
        rates = [size ** -0.5 for size in sizes]
        self.assertAlmostEqual(log_log_slope(sizes, rates), -0.5, places=9)

    def test_flat_curve_recovers_zero_slope(self):
        self.assertAlmostEqual(
            log_log_slope([100, 200, 400], [0.3, 0.3, 0.3]), 0.0, places=9
        )

    def test_fewer_than_two_points_is_refused(self):
        with self.assertRaises(ValueError):
            log_log_slope([100], [0.5])

    def test_non_positive_rate_is_refused(self):
        # log(0) is not a number; a zero rate must be reported, not fitted.
        with self.assertRaises(ValueError):
            log_log_slope([100, 200], [0.5, 0.0])

    def test_mismatched_lengths_are_refused(self):
        with self.assertRaises(ValueError):
            log_log_slope([100, 200], [0.5])


class ProtocolVerdictTests(unittest.TestCase):
    """The pre-registered rule — every verdict must be reachable."""

    def test_slope_consistent_with_theory_is_sampling_limited(self):
        judged = judge_derivation_protocol(slope=-0.50, slope_spread=0.05)
        self.assertEqual(judged["verdict"], "sampling_limited")

    def test_flat_slope_is_structurally_indeterminate(self):
        judged = judge_derivation_protocol(slope=-0.02, slope_spread=0.01)
        self.assertEqual(judged["verdict"], "structurally_indeterminate")

    def test_steep_slope_is_faster_than_sampling(self):
        judged = judge_derivation_protocol(slope=-0.95, slope_spread=0.01)
        self.assertEqual(judged["verdict"], "faster_than_sampling")

    def test_a_wide_measured_spread_widens_the_consistent_band(self):
        # The bar is a multiple of the MEASURED spread, not a constant:
        # the same slope judged against a larger spread becomes
        # consistent with theory.
        self.assertEqual(
            judge_derivation_protocol(slope=-0.20, slope_spread=0.01)["verdict"],
            "structurally_indeterminate",
        )
        self.assertEqual(
            judge_derivation_protocol(slope=-0.20, slope_spread=0.40)["verdict"],
            "sampling_limited",
        )

    def test_negative_spread_is_refused(self):
        with self.assertRaises(ValueError):
            judge_derivation_protocol(slope=-0.5, slope_spread=-0.1)

    def test_verdict_carries_the_band_it_was_judged_against(self):
        judged = judge_derivation_protocol(slope=-0.4, slope_spread=0.1)
        self.assertAlmostEqual(
            judged["consistent_band"][0],
            -0.4 - SLOPE_CONTROL_FACTOR * 0.1,
            places=9,
        )
        self.assertAlmostEqual(
            judged["consistent_band"][1],
            -0.4 + SLOPE_CONTROL_FACTOR * 0.1,
            places=9,
        )
        self.assertEqual(judged["theory_slope"], SAMPLING_THEORY_SLOPE)


class DeterminedSizeTests(unittest.TestCase):
    """The practical verdict, gated against a MEASURED floor."""

    def test_smallest_size_at_or_below_the_floor_is_returned(self):
        judged = judge_determined_size(
            movement_by_size={75: 9.0, 150: 6.0, 600: 2.0, 2400: 1.0},
            floor=2.5,
        )
        self.assertEqual(judged["verdict"], "determined")
        self.assertEqual(judged["determined_at"], 600)

    def test_no_size_reaching_the_floor_reports_honestly(self):
        judged = judge_determined_size(
            movement_by_size={75: 9.0, 600: 8.0, 2400: 7.5}, floor=1.0
        )
        self.assertEqual(judged["verdict"], "not_determined_within_reach")
        self.assertIsNone(judged["determined_at"])

    def test_e1s_own_size_is_reported_separately_from_the_verdict(self):
        # "Is 600 enough?" must be answerable even when a larger size is.
        judged = judge_determined_size(
            movement_by_size={600: 5.0, 2400: 1.0}, floor=2.0
        )
        self.assertEqual(judged["determined_at"], 2400)
        self.assertFalse(judged["e1_size_determined"])

    def test_e1_size_determined_when_600_itself_reaches_the_floor(self):
        judged = judge_determined_size(
            movement_by_size={600: 1.0, 2400: 0.5}, floor=2.0
        )
        self.assertTrue(judged["e1_size_determined"])

    def test_non_positive_floor_is_refused(self):
        # M2's precedent: a zero control makes every movement infinitely
        # significant. Measure it, never assume it.
        with self.assertRaises(ValueError):
            judge_determined_size(movement_by_size={600: 1.0}, floor=0.0)

    def test_empty_ladder_is_refused(self):
        with self.assertRaises(ValueError):
            judge_determined_size(movement_by_size={}, floor=1.0)


class PreRegistrationTests(unittest.TestCase):
    def test_rule_names_its_pre_registration_and_both_gates(self):
        rule = PRE_REGISTERED_RULE.lower()
        self.assertIn("pre-registered", rule)
        self.assertIn("measured", rule)
        self.assertIn("re-addressing", rule)

    def test_theory_slope_is_the_inverse_root_law(self):
        self.assertEqual(SAMPLING_THEORY_SLOPE, -0.5)

    def test_slope_control_factor_matches_the_repo_control_factor(self):
        self.assertEqual(SLOPE_CONTROL_FACTOR, 2.0)


class PilotTests(unittest.TestCase):
    def test_pilot_projects_the_full_ladder_cost(self):
        # DR 0028: wall-clock FIRST, and derived from the incumbent's own
        # measured unit rather than picked.
        measured = measure_derivation_unit(sample_count=40)
        unit = measured["derivation_unit"]
        self.assertEqual(unit["sample_count"], 40)
        self.assertGreater(unit["mean_ms_per_grid"], 0)
        self.assertGreater(measured["projections"]["full_ladder_s"], 0)
        self.assertEqual(
            measured["projections"]["ladder_grid_total"],
            sum(DERIVATION_SIZE_LADDER) * REPLICATE_SEED_COUNT * len(RECIPES),
        )


class ArtifactTests(unittest.TestCase):
    def test_report_carries_every_required_artifact_key(self):
        report = build_derivation_size_stability_report(
            size_ladder=(8, 16),
            replicate_seed_count=2,
            evaluation_count=12,
            evaluation_replicate_count=2,
        )
        for key in (
            "artifact_id",
            "status",
            "date",
            "purpose",
            "source_artifacts",
            "parameters",
            "metrics",
            "closed_states",
            "blocked_states",
            "decision",
            "next_research_step",
        ):
            self.assertIn(key, report)
        self.assertEqual(report["artifact_id"], ARTIFACT_ID)

    def test_report_measures_every_recipe_on_every_ladder_size(self):
        report = build_derivation_size_stability_report(
            size_ladder=(8, 16),
            replicate_seed_count=2,
            evaluation_count=12,
            evaluation_replicate_count=2,
        )
        ladder = report["metrics"]["ladder"]
        for recipe in RECIPES:
            self.assertIn(recipe, ladder)
            self.assertEqual(sorted(ladder[recipe]), ["16", "8"])

    def test_source_artifact_paths_are_repo_relative(self):
        report = build_derivation_size_stability_report(
            size_ladder=(8, 16),
            replicate_seed_count=2,
            evaluation_count=12,
            evaluation_replicate_count=2,
        )
        for path in report["source_artifacts"]:
            self.assertFalse(Path(path).is_absolute())
            self.assertNotIn("\\", path)

    def test_artifact_round_trips_as_json(self):
        report = build_derivation_size_stability_report(
            size_ladder=(8, 16),
            replicate_seed_count=2,
            evaluation_count=12,
            evaluation_replicate_count=2,
        )
        with tempfile.TemporaryDirectory() as directory:
            written = write_derivation_size_stability_artifacts(directory, report)
            self.assertEqual(len(written), 1)
            reloaded = json.loads(written[0].read_text(encoding="utf-8"))
        self.assertEqual(reloaded["artifact_id"], ARTIFACT_ID)
        self.assertEqual(reloaded["decision"]["rule"], PRE_REGISTERED_RULE)


class M2ReproductionTests(unittest.TestCase):
    """The instrument's validation against a COMMITTED number.

    DR 0046 measured the incumbent recipe's self-disagreement at two
    seeds as **0.2 exactly**, over a 3,000-creature evaluation
    population. This module's ladder is that statistic as a function of
    derivation size, so at 600 on the same seed pair it must reproduce
    the committed value. This pin is what makes every other rung on the
    ladder interpretable.
    """

    def test_ladder_reproduces_dr0046_incumbent_control_at_600(self):
        report = build_derivation_size_stability_report(
            size_ladder=(E1_DERIVATION_COUNT,),
            replicate_seed_count=2,
            evaluation_count=3000,
            evaluation_replicate_count=2,
            recipes=("incumbent",),
        )
        rung = report["metrics"]["ladder"]["incumbent"][str(E1_DERIVATION_COUNT)]
        self.assertEqual(rung["readdressing_by_pair"][0], 0.2)
        self.assertEqual(
            report["metrics"]["dr0046_reproduction"]["incumbent"]["measured"], 0.2
        )
        self.assertTrue(
            report["metrics"]["dr0046_reproduction"]["incumbent"]["reproduced"]
        )


if __name__ == "__main__":
    unittest.main()
