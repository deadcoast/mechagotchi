"""Cycle 23 M1: the archive measured on its own inhabitants.

Phase L's convergent finding arrived four separate times without anyone
looking for it: **every instrument measures a different population from
the one the archive is actually filled with.** L1's permanent niche
holders are bootstrap creatures; L2's dominant founder lines are
bootstrap-founded; L3's geometry is calibrated on `build_population`
while the archive is filled by `generate_candidate`; L4 judged a
candidate axis on the derivation population.

These pins fix the contract for turning the instruments around:

* the loop gains an additive `collect_elite_grids` seam — byte-identical
  when off (proven, not asserted), exactly one gated key when on;
* the material-difference bar is **MEASURED** (the same population type
  drawn twice at different seeds), never a constant, and it can fail in
  BOTH directions;
* two of L4's four gates are **structurally undefined** on the elite
  population — not un-run, *undefined* — because the archive holds
  exactly one elite per niche. That fact is pinned here, so no future
  run can quietly report a number for them.
"""

import json
import sys
import tempfile
import unittest
from pathlib import Path

LAB_DIR = Path(__file__).resolve().parent
if str(LAB_DIR) not in sys.path:
    sys.path.insert(0, str(LAB_DIR))

from evaluation_loop_scale import run_evaluation_loop  # noqa: E402

from animation_density_axis import animation_density  # noqa: E402

from elite_population_measures import (  # noqa: E402
    ARTIFACT_ID,
    LOOP_BOUND_S,
    MATERIAL_CONTROL_FACTOR,
    PRE_REGISTERED_BOUND_S,
    PRE_REGISTERED_RULE,
    UNDEFINED_ON_ELITES,
    build_elite_population_report,
    elite_animation_density,
    histogram_tvd,
    judge_material,
    octile_histogram,
    same_three_axis_bin_pairs,
    write_elite_population_artifacts,
)

TINY = dict(population=16, target_evaluations=64, rng_seed=31)


class OctileHistogramTests(unittest.TestCase):
    def test_the_histogram_has_one_bin_more_than_it_has_edges(self):
        # 7 interior edges -> 8 octiles. A histogram that silently
        # dropped the top bin would misreport every distribution.
        self.assertEqual(8, len(octile_histogram([0.5], [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7])))

    def test_a_value_ON_an_edge_falls_in_the_UPPER_bin(self):
        # The boundary convention is `value >= edge` -> step up, matching
        # `niche_scale_archive._bin` and L3's `octile_occupancy`. If this
        # module drifted the other way, its histograms would not be
        # comparable with any number already in the ledger.
        self.assertEqual([0, 1], octile_histogram([0.5], [0.5]))
        self.assertEqual([1, 0], octile_histogram([0.4999], [0.5]))

    def test_values_below_and_above_every_edge_land_in_the_end_bins(self):
        self.assertEqual([2, 0, 1], octile_histogram([-1.0, 0.0, 9.0], [0.5, 1.5]))

    def test_the_counts_total_the_sample_size(self):
        # Nothing may be dropped: a population's members are all binned.
        values = [i / 37 for i in range(37)]
        self.assertEqual(37, sum(octile_histogram(values, [0.25, 0.5, 0.75])))


class HistogramDistanceTests(unittest.TestCase):
    def test_identical_shapes_are_zero_apart(self):
        self.assertEqual(0.0, histogram_tvd([3, 1, 4], [3, 1, 4]))

    def test_the_same_SHAPE_at_a_different_SCALE_is_still_zero_apart(self):
        # The elite set (~460) and the derivation population (600) have
        # different sizes by construction, so the statistic must compare
        # shapes, not counts. Comparing raw counts would report a large
        # difference for two identical distributions.
        self.assertEqual(0.0, histogram_tvd([3, 1, 4], [30, 10, 40]))

    def test_disjoint_shapes_are_exactly_one_apart(self):
        self.assertEqual(1.0, histogram_tvd([5, 0], [0, 5]))

    def test_a_half_moved_distribution_measures_one_half(self):
        self.assertAlmostEqual(0.5, histogram_tvd([10, 10], [0, 20]), places=9)

    def test_mismatched_bin_counts_are_refused_not_zero_padded(self):
        # Silently padding would compare two different geometries and
        # return a number — exactly the class of error L3 caught.
        with self.assertRaises(ValueError):
            histogram_tvd([1, 2, 3], [1, 2])

    def test_an_empty_population_is_refused_rather_than_divided_by(self):
        with self.assertRaises(ValueError):
            histogram_tvd([0, 0], [1, 1])


class PreRegisteredMaterialRuleTests(unittest.TestCase):
    def test_the_bar_is_a_FACTOR_over_a_measured_control_not_a_constant(self):
        # L3's precedent, and the reason it matters here: the TODO warns
        # that "the elites look different" must not become a conclusion
        # in search of a bar. The bar is a multiple of a control this
        # study measures for itself.
        self.assertEqual(2.0, MATERIAL_CONTROL_FACTOR)
        self.assertIn("MEASURED", PRE_REGISTERED_RULE)

    def test_a_difference_AT_the_bar_is_material_and_below_it_is_not(self):
        # The boundary belongs to the rule, so it is pinned.
        self.assertEqual(
            "material", judge_material(difference=0.20, control=0.10)["verdict"]
        )
        self.assertEqual(
            "within_sampling_noise",
            judge_material(difference=0.1999, control=0.10)["verdict"],
        )

    def test_the_gate_can_fail_in_BOTH_directions(self):
        # A gate that cannot fail is a bug. Both verdicts must be
        # reachable from real inputs.
        verdicts = {
            judge_material(difference=0.9, control=0.01)["verdict"],
            judge_material(difference=0.001, control=0.01)["verdict"],
        }
        self.assertEqual({"material", "within_sampling_noise"}, verdicts)

    def test_a_zero_control_is_refused_rather_than_made_infinitely_significant(self):
        # L3's exact guard: dividing by a zero control would make every
        # difference material. Measure the control, never assume it.
        with self.assertRaises(ValueError):
            judge_material(difference=0.5, control=0.0)

    def test_the_verdict_carries_the_rule_it_was_judged_by(self):
        judged = judge_material(difference=0.5, control=0.1)
        self.assertEqual(PRE_REGISTERED_RULE, judged["rule"])
        self.assertEqual(0.1, judged["control"])
        self.assertAlmostEqual(5.0, judged["ratio"], places=6)

    def test_the_wall_clock_bound_is_DERIVED_from_the_loops_own_bound(self):
        # DR 0028 discipline: this study measures an elite control, which
        # means running the documented-budget loop TWICE. The bound is
        # two of the loop's own pre-registered bound — derived from the
        # incumbent record, never picked to fit a measurement.
        self.assertEqual(2 * LOOP_BOUND_S, PRE_REGISTERED_BOUND_S)


class StructurallyUndefinedGateTests(unittest.TestCase):
    def test_same_bin_pairs_counts_repeats_and_is_zero_when_all_bins_differ(self):
        self.assertEqual(0, same_three_axis_bin_pairs([(0, 0, 0), (1, 1, 1)]))
        # three members of one bin -> three pairs.
        self.assertEqual(
            3, same_three_axis_bin_pairs([(0, 0, 0), (0, 0, 0), (0, 0, 0)])
        )

    def test_L4s_discrimination_and_cost_gates_are_declared_UNDEFINED_here(self):
        # NOT "not yet run" — undefined. The archive holds exactly one
        # elite per niche, so no two elites can share a three-axis bin
        # and the same-bin-pair denominator is structurally zero. L4's
        # own remainder said the axis was "judged on the derivation
        # population, not the loop's elites"; this pin records that for
        # A3/A4 the elite measurement is not merely missing, it cannot
        # exist.
        self.assertIn("A3_discrimination", UNDEFINED_ON_ELITES)
        self.assertIn("A4_coverage_cost", UNDEFINED_ON_ELITES)
        for reason in UNDEFINED_ON_ELITES.values():
            self.assertIn("one elite per niche", reason)


class EliteGridSeamTests(unittest.TestCase):
    def test_the_seam_is_byte_identical_when_off(self):
        implicit = run_evaluation_loop(**TINY)
        explicit = run_evaluation_loop(collect_elite_grids=False, **TINY)
        self.assertEqual(implicit, explicit)
        self.assertNotIn("elite_grid_collection", implicit)

    def test_collecting_elite_grids_adds_exactly_one_key(self):
        off = run_evaluation_loop(**TINY)
        on = run_evaluation_loop(collect_elite_grids=True, **TINY)
        self.assertEqual({"elite_grid_collection"}, set(on) - set(off))
        self.assertEqual(
            off, {k: v for k, v in on.items() if k != "elite_grid_collection"}
        )

    def test_the_seam_composes_with_the_L2_lineage_seam(self):
        # Two observation seams, both additive: turning both on adds
        # exactly the two keys and perturbs nothing else.
        off = run_evaluation_loop(**TINY)
        both = run_evaluation_loop(
            collect_elite_grids=True, collect_lineage=True, **TINY
        )
        self.assertEqual(
            {"elite_grid_collection", "lineage_collection"}, set(both) - set(off)
        )

    def test_one_record_per_occupied_niche_each_carrying_a_WHOLE_grid(self):
        # The L2 seam emits ancestry only; measuring animation density
        # needs the cells themselves, which is why this seam exists.
        result = run_evaluation_loop(collect_elite_grids=True, **TINY)
        collection = result["elite_grid_collection"]
        occupied = result["archive_summary"]["occupied_niches"]
        self.assertEqual(occupied, collection["occupied_niches"])
        self.assertEqual(occupied, len(collection["elites"]))
        for record in collection["elites"]:
            self.assertIn("niche", record)
            self.assertIn("grid_id", record)
            self.assertTrue(record["grid"]["cells"])
            self.assertEqual(record["grid_id"], record["grid"]["grid_id"])

    def test_the_collected_grid_is_a_COPY_the_caller_cannot_corrupt(self):
        # An observation seam must never hand out a live reference into
        # the loop's working set.
        result = run_evaluation_loop(collect_elite_grids=True, **TINY)
        record = result["elite_grid_collection"]["elites"][0]
        record["grid"]["cells"].clear()
        elite = result["archive"]["elites"][record["niche"]]
        self.assertEqual(record["grid_id"], elite["grid_id"])

    def test_origin_is_measured_by_MEMBERSHIP_not_inferred_from_depth(self):
        # L1's recorded process error, pinned so it cannot recur: a
        # bootstrap creature is generated FROM a seed and already sits at
        # lineage depth 1, so reading depth as provenance mislabels every
        # one of them.
        result = run_evaluation_loop(collect_elite_grids=True, **TINY)
        origins = {
            record["origin"] for record in result["elite_grid_collection"]["elites"]
        }
        self.assertTrue(origins <= {"bootstrap", "loop_offspring"})

    def test_no_two_elites_share_a_three_axis_bin(self):
        # The structural fact that makes L4's A3/A4 undefined here,
        # measured on a real archive rather than argued.
        result = run_evaluation_loop(collect_elite_grids=True, **TINY)
        niches = [record["niche"] for record in result["elite_grid_collection"]["elites"]]
        self.assertEqual(len(niches), len(set(niches)))


class EliteAnimationDensityTests(unittest.TestCase):
    def test_the_axis_is_the_L4_definition_itself_never_a_second_copy(self):
        # A re-measure that redefined the axis would be measuring a
        # different thing and calling it the same name.
        grid = {
            "grid_id": "x",
            "cells": [
                {"x": 0, "y": 0, "role": "limb"},
                {"x": 1, "y": 0, "role": "core"},
            ],
        }
        self.assertEqual(animation_density(grid), elite_animation_density(grid))


class ElitePopulationReportTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.report = build_elite_population_report(
            derivation_count=48,
            population=16,
            target_evaluations=64,
            rng_seed=31,
            control_rng_seed=97,
        )

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

    def test_the_control_is_MEASURED_and_positive_for_every_statistic(self):
        # The whole design rests on this: if a control were zero or
        # absent, the verdict would be arithmetic rather than evidence.
        controls = self.report["metrics"]["measured_controls"]
        self.assertTrue(controls)
        for name, value in controls.items():
            with self.subTest(statistic=name):
                self.assertGreater(value, 0.0)

    def test_the_control_is_the_LARGER_of_the_two_population_types(self):
        # The elite set is an extreme-value selection from a stochastic
        # process, so its own between-seed movement may exceed the
        # derivation population's. Taking the larger keeps "material"
        # hard to claim.
        metrics = self.report["metrics"]
        for name, value in metrics["measured_controls"].items():
            with self.subTest(statistic=name):
                self.assertAlmostEqual(
                    max(
                        metrics["derivation_control"][name],
                        metrics["elite_control"][name],
                    ),
                    value,
                    places=9,
                )

    def test_every_judged_statistic_follows_the_pre_registered_rule(self):
        metrics = self.report["metrics"]
        for name, judged in metrics["judgements"].items():
            with self.subTest(statistic=name):
                expected = judge_material(
                    difference=metrics["derivation_vs_elite"][name],
                    control=metrics["measured_controls"][name],
                )
                self.assertEqual(expected["verdict"], judged["verdict"])

    def test_the_undefined_gates_are_reported_as_undefined_not_as_numbers(self):
        # The honesty pin: no proxy, no zero, no "0.0 discrimination".
        undefined = self.report["metrics"]["undefined_on_elites"]
        self.assertEqual(set(UNDEFINED_ON_ELITES), set(undefined))
        for reason in undefined.values():
            self.assertIsInstance(reason, str)
        self.assertEqual(
            0, self.report["metrics"]["elite_same_three_axis_bin_pairs"]
        )

    def test_the_artifact_records_the_edges_it_binned_against(self):
        # A histogram is meaningless without its reference. Both the
        # frozen incumbent edges and the candidate axis's derived edges
        # ride in the artifact so a reader can check them against the
        # committed geometry and against L4 without re-deriving either.
        metrics = self.report["metrics"]
        self.assertEqual(
            set(metrics["frozen_edges"]),
            set(metrics["octile_histograms"]["elite"]) - {"animation_density"},
        )
        reference = metrics["animation_density_reference_edges"]
        self.assertEqual(
            len(metrics["octile_histograms"]["elite"]["animation_density"]),
            len(reference) + 1,
        )

    def test_the_blocked_states_name_the_structural_limit(self):
        blocked = " ".join(self.report["blocked_states"])
        self.assertIn("one elite per niche", blocked)

    def test_the_decision_reports_the_headline_ratio_and_its_verdict(self):
        decision = self.report["decision"]
        self.assertIn(decision["verdict"], ("material", "within_sampling_noise"))
        self.assertIn("rule", decision)
        self.assertIn("driving_statistic", decision)

    def test_the_report_is_deterministic_under_its_seeds(self):
        again = build_elite_population_report(
            derivation_count=48,
            population=16,
            target_evaluations=64,
            rng_seed=31,
            control_rng_seed=97,
        )

        def measured(report):
            metrics = dict(report["metrics"])
            # The three per-run observations that differ by construction.
            metrics.pop("wall_clock_s", None)
            metrics.pop("within_bound", None)
            return metrics

        self.assertEqual(measured(self.report), measured(again))

    def test_the_artifact_writes_and_reloads(self):
        with tempfile.TemporaryDirectory() as tmp:
            written = write_elite_population_artifacts(Path(tmp), self.report)
            self.assertTrue(written)
            for path in written:
                reloaded = json.loads(Path(path).read_text(encoding="utf-8"))
                self.assertEqual(ARTIFACT_ID, reloaded["artifact_id"])


if __name__ == "__main__":
    unittest.main()
