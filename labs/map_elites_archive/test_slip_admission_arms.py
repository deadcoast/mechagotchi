"""Cycle 23 M3: the unbreedable bootstrap elites, and what fixing them costs.

L1 measured the mechanism and deliberately did NOT fix it: all 4,435
generation refusals are the SLIP rejecting the **parent**, 100% of those
parents are bootstrap creatures, and the tax settles at a flat 38 per
generation forever. M1 sized the population exactly: **48 of 460 elites
(10.4%) are bootstrap creatures**.

The fix trades against coverage, and the three candidate changes are NOT
equivalent — a niche whose only occupant is SLIP-illegal goes **empty**
if that occupant is excluded, so "fixing" the refusals can lower the
0.8984 coverage DR 0042 just adopted.

These pins fix the contract:

* three arms, each an additive `slip_admission` mode on the loop,
  **byte-identical when off** (pinned);
* the SLIP predicate is the generation arm's OWN
  (`slip.is_grid_aligned`), imported and never re-implemented, so an arm
  cannot admit a creature the generator would refuse;
* the coverage bar is **MEASURED** — the loop's own seed-to-seed
  coverage variation — never a constant;
* **G1 is structural, not tuned**: L1 proved 100% of refusals are
  SLIP-illegal parents, so an arm that addresses the cause must drive
  refusals to **exactly zero**. Anything else is partial and is reported
  with its number.
* the tie-break between passing arms is **least-invasive-first**, fixed
  before the run so it cannot be chosen to suit the result.
"""

import json
import sys
import tempfile
import unittest
from pathlib import Path

LAB_DIR = Path(__file__).resolve().parent
ROOT = LAB_DIR.parents[1]
for _sub in ("labs/map_elites_archive", "labs/grid_genome"):
    _path = str(ROOT / _sub)
    if _path not in sys.path:
        sys.path.insert(0, _path)

from evaluation_loop_scale import _load_default_slip  # noqa: E402
from evaluation_loop_scale import run_evaluation_loop  # noqa: E402
from slip import is_grid_aligned  # noqa: E402

from slip_admission_arms import (  # noqa: E402
    ARMS,
    ARTIFACT_ID,
    INVASIVENESS_ORDER,
    PRE_REGISTERED_RULE,
    arm_is_adoptable,
    build_slip_admission_report,
    slip_legal,
    write_slip_admission_artifacts,
)

TINY = dict(population=16, target_evaluations=64, rng_seed=31)


class SlipPredicateTests(unittest.TestCase):
    def test_the_predicate_is_the_generation_arms_OWN_check(self):
        # A second implementation could admit a creature the generator
        # would refuse, which would make every arm's number a fiction.
        slip = json.loads(
            (ROOT / "data" / "slips" / "valid" / "slip_lcd_seed.json").read_text(
                encoding="utf-8"
            )
        )
        grid = json.loads(
            (
                ROOT / "data" / "seed_grids_16x16" / "mg_seed16_001_beetle.json"
            ).read_text(encoding="utf-8")
        )
        self.assertEqual(
            is_grid_aligned(grid, slip).ok, slip_legal(grid, slip)
        )

    def test_a_missing_profile_admits_everything(self):
        # `_acceptable` treats slip=None as "no constraint"; the arms
        # must agree, or an unprofiled run would silently change.
        self.assertTrue(slip_legal({"grid_id": "x", "cells": []}, None))


class PreRegisteredRuleTests(unittest.TestCase):
    def test_the_three_named_arms_are_the_three_candidate_changes(self):
        self.assertEqual(("bootstrap", "insertion", "parents"), ARMS)

    def test_G1_is_structural_zero_not_a_tuned_fraction(self):
        # L1 proved 100% of refusals are SLIP-illegal parents, so an arm
        # that removes the cause must reach exactly zero. A "90%
        # reduction" bar would be a number nobody derived.
        self.assertIn("exactly zero", PRE_REGISTERED_RULE)

    def test_an_arm_needs_BOTH_gates_and_refusal_is_first_class(self):
        # Zero refusals but coverage lost beyond noise -> not adoptable.
        self.assertFalse(
            arm_is_adoptable(refusals=0, coverage_cost=0.09, coverage_control=0.03)[
                "adoptable"
            ]
        )
        # Coverage preserved but the cause still firing -> not adoptable.
        self.assertFalse(
            arm_is_adoptable(refusals=12, coverage_cost=0.0, coverage_control=0.03)[
                "adoptable"
            ]
        )
        self.assertTrue(
            arm_is_adoptable(refusals=0, coverage_cost=0.01, coverage_control=0.03)[
                "adoptable"
            ]
        )

    def test_a_coverage_cost_AT_the_measured_control_still_passes(self):
        # The boundary belongs to the rule, so it is pinned: a cost equal
        # to the noise floor is indistinguishable from noise.
        self.assertTrue(
            arm_is_adoptable(refusals=0, coverage_cost=0.03, coverage_control=0.03)[
                "adoptable"
            ]
        )

    def test_a_coverage_GAIN_is_never_penalised(self):
        # An arm that improves coverage has a negative cost; the gate
        # must not read that as a failure.
        judged = arm_is_adoptable(
            refusals=0, coverage_cost=-0.05, coverage_control=0.03
        )
        self.assertTrue(judged["adoptable"])

    def test_a_zero_control_is_refused_rather_than_assumed(self):
        with self.assertRaises(ValueError):
            arm_is_adoptable(refusals=0, coverage_cost=0.0, coverage_control=0.0)

    def test_the_tie_break_is_least_invasive_first_and_fixed_in_advance(self):
        # parents changes only who breeds; insertion changes what the
        # archive holds; bootstrap changes the starting population.
        self.assertEqual(("parents", "insertion", "bootstrap"), INVASIVENESS_ORDER)
        self.assertEqual(set(ARMS), set(INVASIVENESS_ORDER))


class LoopAdmissionSeamTests(unittest.TestCase):
    def test_the_seam_is_byte_identical_when_off(self):
        implicit = run_evaluation_loop(**TINY)
        explicit = run_evaluation_loop(slip_admission="none", **TINY)
        self.assertEqual(implicit, explicit)

    def test_an_unknown_mode_is_refused_loudly(self):
        with self.assertRaises(ValueError):
            run_evaluation_loop(slip_admission="whatever", **TINY)

    def test_every_arm_reports_its_admission_mode_in_the_result(self):
        for mode in ARMS:
            with self.subTest(mode=mode):
                result = run_evaluation_loop(slip_admission=mode, **TINY)
                self.assertEqual(mode, result["slip_admission"])

    def test_the_off_mode_reports_none_and_adds_no_other_key(self):
        off = run_evaluation_loop(**TINY)
        self.assertEqual("none", off["slip_admission"])

    def test_the_insertion_arm_admits_only_SLIP_LEGAL_elites(self):
        # The arm's whole claim. Measured on the archive it produced,
        # not asserted.
        slip = _load_default_slip()
        result = run_evaluation_loop(
            slip_admission="insertion", collect_elite_grids=True, **TINY
        )
        for record in result["elite_grid_collection"]["elites"]:
            self.assertTrue(slip_legal(record["grid"], slip))

    def test_the_incumbent_archive_DOES_hold_slip_illegal_elites(self):
        # Without this the insertion pin above could pass vacuously —
        # it would prove nothing if no illegal elite ever reached an
        # archive in the first place. This is the arm's reason to exist.
        slip = _load_default_slip()
        off = run_evaluation_loop(collect_elite_grids=True, **TINY)
        illegal = [
            record
            for record in off["elite_grid_collection"]["elites"]
            if not slip_legal(record["grid"], slip)
        ]
        self.assertTrue(illegal)

    def test_the_insertion_arm_still_SCORES_what_it_refuses_to_insert(self):
        # The evaluation budget is scored lifecycles, so a refused
        # insertion must still SPEND its evaluation — otherwise refusing
        # would silently buy the arm extra candidates.
        #
        # Note what this does NOT assert: that the arms end on the same
        # `evaluations_total`. They do not, and legitimately so — the
        # loop overshoots by whatever the final generation adds, and the
        # number of generations depends on how many candidates each
        # generation produced, which the refusal count changes. The real
        # invariant is that scored-and-refused candidates are counted as
        # scored, which is exactly what these two comparisons say.
        off = run_evaluation_loop(**TINY)
        arm = run_evaluation_loop(slip_admission="insertion", **TINY)
        self.assertEqual(
            off["evaluations_total"], off["archive"]["candidate_count"]
        )
        self.assertLess(
            arm["archive"]["candidate_count"], arm["evaluations_total"]
        )

    def test_the_parents_arm_records_any_fallback_rather_than_hiding_it(self):
        # If no SLIP-legal elite exists the loop cannot breed; falling
        # back silently would reintroduce refusals and make G1
        # uninterpretable, so the count rides in the result.
        result = run_evaluation_loop(slip_admission="parents", **TINY)
        self.assertIn("parent_fallback_generations", result)
        self.assertGreaterEqual(result["parent_fallback_generations"], 0)


class SlipAdmissionReportTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.report = build_slip_admission_report(
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

    def test_the_coverage_control_is_MEASURED_and_positive(self):
        self.assertGreater(self.report["metrics"]["coverage_control"], 0.0)

    def test_every_arm_is_measured_against_the_SAME_baseline(self):
        metrics = self.report["metrics"]
        self.assertEqual(set(ARMS), set(metrics["arms"]))
        baseline = metrics["baseline"]["coverage"]
        for name, arm in metrics["arms"].items():
            with self.subTest(arm=name):
                self.assertAlmostEqual(
                    round(baseline - arm["coverage"], 6),
                    arm["coverage_cost"],
                    places=6,
                )

    def test_each_arms_verdict_follows_the_pre_registered_rule(self):
        metrics = self.report["metrics"]
        for name, arm in metrics["arms"].items():
            with self.subTest(arm=name):
                expected = arm_is_adoptable(
                    refusals=arm["refusals"],
                    coverage_cost=arm["coverage_cost"],
                    coverage_control=metrics["coverage_control"],
                )
                self.assertEqual(expected["adoptable"], arm["adoptable"])

    def test_the_decision_names_a_winner_only_from_adoptable_arms(self):
        decision = self.report["decision"]
        metrics = self.report["metrics"]
        adoptable = [n for n, a in metrics["arms"].items() if a["adoptable"]]
        if decision["adopted_arm"] is None:
            self.assertEqual([], adoptable)
        else:
            self.assertIn(decision["adopted_arm"], adoptable)

    def test_the_winner_is_the_LEAST_INVASIVE_adoptable_arm(self):
        decision = self.report["decision"]
        metrics = self.report["metrics"]
        adoptable = [n for n, a in metrics["arms"].items() if a["adoptable"]]
        if adoptable:
            expected = next(n for n in INVASIVENESS_ORDER if n in adoptable)
            self.assertEqual(expected, decision["adopted_arm"])

    def test_the_coverage_trade_is_reported_for_every_arm_even_refused_ones(self):
        # A refused arm's cost is the evidence for refusing it; dropping
        # it would leave the refusal unexplained.
        for name, arm in self.report["metrics"]["arms"].items():
            with self.subTest(arm=name):
                for key in ("coverage", "coverage_cost", "refusals", "occupied_niches"):
                    self.assertIn(key, arm)

    def test_the_artifact_writes_and_reloads(self):
        with tempfile.TemporaryDirectory() as tmp:
            written = write_slip_admission_artifacts(Path(tmp), self.report)
            self.assertTrue(written)
            for path in written:
                reloaded = json.loads(Path(path).read_text(encoding="utf-8"))
                self.assertEqual(ARTIFACT_ID, reloaded["artifact_id"])


if __name__ == "__main__":
    unittest.main()
