"""Cycle 23 M2: the geometry split, decided.

L3 found the repo runs TWO scale geometries and diagnosed the hazard
without repairing it: the loop and the E4 gates consume the frozen
**train**-derived edges, while `reachability_probe` and
`occupancy_saturation` derive **live from all 50 seeds**. Edge sets
differ by up to 0.0375 — 3.7× L3's measured sampling control — so
`460/512 occupied` and `508/512 reachable` are counted in different
coordinate systems and have been read against each other in prose.

These pins fix the contract for deciding it:

* the disagreement is measured in the unit that actually matters — **how
  often the same creature gets a different address** — not in edge
  distance, which is not the unit any ledger number is expressed in;
* the bar is **MEASURED** (the same recipe derived at two seeds), never
  a constant, and the rule is **status-quo-favouring**: the split stands
  unless the geometries disagree by more than sampling can explain;
* **whether** to converge is decided by measurement; **which way** is
  decided by a principle stated before the measurement, so the direction
  cannot be chosen to suit the number;
* K2's cross-geometry claim — *"460 occupied is exactly the measured
  support ceiling"* — is re-measured with both numbers computed in the
  SAME geometry, which is the specific error L3 named.
"""

import json
import sys
import tempfile
import unittest
from pathlib import Path

LAB_DIR = Path(__file__).resolve().parent
if str(LAB_DIR) not in sys.path:
    sys.path.insert(0, str(LAB_DIR))

from geometry_decision import (  # noqa: E402
    ARTIFACT_ID,
    CONVERGENCE_TARGET,
    CONVERGENCE_TARGET_REASON,
    DISAGREEMENT_CONTROL_FACTOR,
    PRE_REGISTERED_RULE,
    bin_disagreement,
    build_geometry_decision_report,
    judge_geometry_split,
    per_axis_disagreement,
    write_geometry_decision_artifacts,
)

TINY = dict(derivation_count=48, evaluation_count=64)


class DisagreementStatisticTests(unittest.TestCase):
    def test_identical_addressings_disagree_nowhere(self):
        rows = [(1, 2, 3), (4, 5, 6)]
        self.assertEqual(0.0, bin_disagreement(rows, list(rows)))

    def test_a_single_axis_difference_makes_the_ADDRESS_differ(self):
        # A descriptor is a whole address: one axis off by one octile is
        # a different niche, not a partial match. This is the unit every
        # coverage number is counted in.
        self.assertEqual(
            1.0, bin_disagreement([(1, 2, 3)], [(1, 2, 4)])
        )

    def test_the_rate_is_the_fraction_of_the_population(self):
        first = [(0, 0, 0), (1, 1, 1), (2, 2, 2), (3, 3, 3)]
        second = [(0, 0, 0), (1, 1, 9), (2, 2, 2), (3, 3, 9)]
        self.assertEqual(0.5, bin_disagreement(first, second))

    def test_mismatched_populations_are_refused_not_zipped_short(self):
        # Silently truncating would compare two different populations
        # and still return a number.
        with self.assertRaises(ValueError):
            bin_disagreement([(1, 2, 3)], [(1, 2, 3), (4, 5, 6)])

    def test_an_empty_population_is_refused_rather_than_divided_by(self):
        with self.assertRaises(ValueError):
            bin_disagreement([], [])

    def test_per_axis_disagreement_localises_the_split(self):
        # The headline rate says the geometries disagree; the per-axis
        # rate says WHERE, which is what a convergence decision needs.
        first = [(0, 0, 0), (1, 1, 1)]
        second = [(0, 5, 0), (1, 5, 1)]
        per_axis = per_axis_disagreement(first, second)
        self.assertEqual(0.0, per_axis["symmetry"])
        self.assertEqual(1.0, per_axis["visual_complexity"])
        self.assertEqual(0.0, per_axis["behavior_neediness"])


class PreRegisteredRuleTests(unittest.TestCase):
    def test_the_bar_is_a_FACTOR_over_a_MEASURED_control(self):
        self.assertEqual(2.0, DISAGREEMENT_CONTROL_FACTOR)
        self.assertIn("MEASURED", PRE_REGISTERED_RULE)

    def test_the_rule_is_status_quo_favouring_and_can_fail_both_ways(self):
        # The split STANDS unless the disagreement beats the control by
        # the factor. A gate that cannot fail is a bug, so both verdicts
        # must be reachable.
        self.assertEqual(
            "converge",
            judge_geometry_split(disagreement=0.40, control=0.10)["verdict"],
        )
        self.assertEqual(
            "freeze_split",
            judge_geometry_split(disagreement=0.19, control=0.10)["verdict"],
        )

    def test_a_disagreement_AT_the_bar_converges(self):
        # The boundary belongs to the rule, so it is pinned.
        self.assertEqual(
            "converge",
            judge_geometry_split(disagreement=0.20, control=0.10)["verdict"],
        )

    def test_a_zero_control_is_refused_rather_than_made_infinite(self):
        with self.assertRaises(ValueError):
            judge_geometry_split(disagreement=0.5, control=0.0)

    def test_the_direction_of_convergence_is_fixed_BEFORE_the_measurement(self):
        # The measurement decides WHETHER to converge; it must not be
        # allowed to decide WHICH WAY, or the direction becomes a
        # post-hoc choice. The target and its reason are constants of
        # this module, pinned.
        self.assertEqual("incumbent", CONVERGENCE_TARGET)
        self.assertIn("frozen", CONVERGENCE_TARGET_REASON)
        # ...and the reason must name the property that makes it the
        # conservative direction: converging ONTO the incumbent leaves
        # every committed coverage/QD number untouched.
        self.assertIn("no historical", CONVERGENCE_TARGET_REASON.lower())

    def test_the_verdict_carries_the_rule_it_was_judged_by(self):
        judged = judge_geometry_split(disagreement=0.5, control=0.1)
        self.assertEqual(PRE_REGISTERED_RULE, judged["rule"])
        self.assertAlmostEqual(5.0, judged["ratio"], places=6)


class GeometryDecisionReportTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.report = build_geometry_decision_report(**TINY)

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

    def test_both_geometries_are_recorded_with_the_edges_they_used(self):
        # A bin index means nothing without its edges; an artifact that
        # decided between two geometries without recording them would be
        # unverifiable.
        edges = self.report["metrics"]["edges"]
        self.assertIn("incumbent", edges)
        self.assertIn("probe", edges)
        self.assertNotEqual(edges["incumbent"], edges["probe"])

    def test_the_control_is_MEASURED_and_positive(self):
        control = self.report["metrics"]["measured_control"]
        self.assertGreater(control, 0.0)

    def test_the_verdict_follows_the_pre_registered_rule(self):
        metrics = self.report["metrics"]
        expected = judge_geometry_split(
            disagreement=metrics["bin_disagreement"],
            control=metrics["measured_control"],
        )
        self.assertEqual(expected["verdict"], self.report["decision"]["verdict"])

    def test_the_support_ceiling_is_reported_in_BOTH_geometries(self):
        # K2's headline compared 460 occupied (incumbent) against a
        # support ceiling counted in the probe geometry. Both numbers
        # must be available in the SAME geometry before any equality
        # claim can be made about them.
        ceiling = self.report["metrics"]["support_ceiling"]
        self.assertIn("incumbent", ceiling)
        self.assertIn("probe", ceiling)
        for value in ceiling.values():
            self.assertGreater(value, 0)

    def test_the_report_states_what_prior_numbers_do_and_do_not_mean(self):
        # The queue's explicit requirement: every historical artifact
        # stays true under the edges it was measured with, and the
        # record must say so plainly rather than leaving it implied.
        prose = " ".join(
            self.report["closed_states"] + self.report["blocked_states"]
        ) + json.dumps(self.report["decision"])
        self.assertIn("stays true under the edges", prose)

    def test_the_report_is_deterministic_under_its_seeds(self):
        again = build_geometry_decision_report(**TINY)

        def measured(report):
            metrics = dict(report["metrics"])
            metrics.pop("wall_clock_s", None)
            return metrics

        self.assertEqual(measured(self.report), measured(again))

    def test_the_artifact_writes_and_reloads(self):
        with tempfile.TemporaryDirectory() as tmp:
            written = write_geometry_decision_artifacts(Path(tmp), self.report)
            self.assertTrue(written)
            for path in written:
                reloaded = json.loads(Path(path).read_text(encoding="utf-8"))
                self.assertEqual(ARTIFACT_ID, reloaded["artifact_id"])


if __name__ == "__main__":
    unittest.main()
