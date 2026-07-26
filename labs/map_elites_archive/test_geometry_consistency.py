"""Cycle 22 L3: is the scale geometry stale, or merely inconsistent?

K3 named the frozen derivation edges as the mechanism behind its four
measure-thin bins and asked whether the geometry should re-derive under
the adopted generation layer. These pins fix the instrument that
answers it: the same octile protocol run under several named derivation
recipes, an evidence-derived sampling-noise control so "different" means
something, and a rule pre-registered before the run with the incumbent
geometry favoured.

The instrument NEVER changes the geometry: whatever it finds, moving the
edges would invalidate every coverage number in the ledger and is its
own gated record.
"""

import json
import sys
import tempfile
import unittest
from pathlib import Path

LAB_DIR = Path(__file__).resolve().parent
if str(LAB_DIR) not in sys.path:
    sys.path.insert(0, str(LAB_DIR))

from geometry_consistency import (  # noqa: E402
    ARTIFACT_ID,
    RECIPES,
    build_geometry_consistency_report,
    edge_separation,
    judge_geometry,
    octile_occupancy,
    write_geometry_consistency_artifacts,
)

TINY = dict(derivation_count=120, control_count=120)


class EdgeSeparationTests(unittest.TestCase):
    def test_identical_edge_sets_separate_by_zero(self):
        edges = {"a": [1.0, 2.0, 3.0]}
        self.assertEqual(0.0, edge_separation(edges, edges)["max_abs"])

    def test_separation_is_the_largest_absolute_edge_move(self):
        first = {"a": [1.0, 2.0], "b": [0.0, 0.0]}
        second = {"a": [1.0, 2.5], "b": [0.1, 0.0]}
        measured = edge_separation(first, second)
        self.assertAlmostEqual(0.5, measured["max_abs"], places=9)
        self.assertAlmostEqual(0.5, measured["per_axis"]["a"], places=9)
        self.assertAlmostEqual(0.1, measured["per_axis"]["b"], places=9)

    def test_separation_is_symmetric(self):
        first = {"a": [1.0, 2.0]}
        second = {"a": [1.4, 2.0]}
        self.assertEqual(
            edge_separation(first, second)["max_abs"],
            edge_separation(second, first)["max_abs"],
        )


class OctileOccupancyTests(unittest.TestCase):
    def test_a_perfectly_split_population_has_zero_deviation(self):
        # Eight values, seven edges between them: one per octile.
        values = [0.5, 1.5, 2.5, 3.5, 4.5, 5.5, 6.5, 7.5]
        edges = [1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0]
        measured = octile_occupancy(values, edges)
        self.assertEqual([1] * 8, measured["counts"])
        self.assertAlmostEqual(0.0, measured["total_variation"], places=9)
        self.assertEqual(0, measured["empty_octiles"])

    def test_a_collapsed_population_reports_its_empty_octiles(self):
        # Everything below the first edge: one occupied octile, seven empty.
        values = [0.1] * 8
        edges = [1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0]
        measured = octile_occupancy(values, edges)
        self.assertEqual(7, measured["empty_octiles"])
        self.assertAlmostEqual(0.875, measured["total_variation"], places=9)


class PreRegisteredRuleTests(unittest.TestCase):
    def test_the_incumbent_stands_when_drift_is_within_sampling_noise(self):
        # Incumbent-favouring: a difference no larger than the measured
        # sampling control is not evidence of anything.
        judged = judge_geometry(drift=0.001, control=0.010)
        self.assertEqual("withhold_regeneration", judged["verdict"])

    def test_drift_far_beyond_the_control_recommends_regeneration(self):
        judged = judge_geometry(drift=0.10, control=0.010)
        self.assertEqual("regenerate", judged["verdict"])

    def test_the_bar_is_derived_from_the_measured_control_not_a_constant(self):
        # The house rule: gates derive from evidence. Doubling the
        # control must double the threshold.
        loose = judge_geometry(drift=0.05, control=0.010)
        tight = judge_geometry(drift=0.05, control=0.050)
        self.assertEqual("regenerate", loose["verdict"])
        self.assertEqual("withhold_regeneration", tight["verdict"])

    def test_a_zero_control_cannot_make_every_difference_significant(self):
        # A degenerate control would otherwise divide by zero and call
        # any drift infinite. Refused loudly instead.
        with self.assertRaises(ValueError):
            judge_geometry(drift=0.05, control=0.0)

    def test_the_verdict_carries_the_rule_and_the_numbers(self):
        judged = judge_geometry(drift=0.05, control=0.010)
        self.assertIn("rule", judged)
        self.assertIn("ratio", judged)


class GeometryConsistencyReportTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.report = build_geometry_consistency_report(**TINY)

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

    def test_every_named_recipe_is_measured(self):
        measured = self.report["metrics"]["recipes"]
        for name in RECIPES:
            with self.subTest(recipe=name):
                self.assertIn(name, measured)
                self.assertIn("edges", measured[name])

    def test_the_incumbent_recipe_is_compared_against_the_committed_edges(self):
        # The whole staleness question: does E1's own protocol, re-run
        # under today's code, still produce the committed edges?
        self.assertIn("frozen_vs_incumbent", self.report["metrics"])

    def test_the_sampling_control_is_measured_not_assumed(self):
        control = self.report["metrics"]["sampling_control"]
        self.assertIn("max_abs", control)
        self.assertGreater(control["max_abs"], 0.0)

    def test_the_geometry_split_is_reported_axis_by_axis(self):
        # The finding this instrument exists to surface: the probe's
        # derivation recipe and the loop's are not the same geometry.
        split = self.report["metrics"]["recipe_separation"]
        self.assertIn("incumbent_vs_probe", split)
        self.assertIn("per_axis", split["incumbent_vs_probe"])

    def test_the_decision_is_the_pre_registered_rule_applied(self):
        decision = self.report["decision"]
        expected = judge_geometry(
            drift=self.report["metrics"]["frozen_vs_incumbent"]["max_abs"],
            control=self.report["metrics"]["sampling_control"]["max_abs"],
        )["verdict"]
        self.assertEqual(expected, decision["verdict"])

    def test_the_artifact_writes_and_reloads(self):
        with tempfile.TemporaryDirectory() as tmp:
            written = write_geometry_consistency_artifacts(Path(tmp), self.report)
            self.assertTrue(written)
            for path in written:
                reloaded = json.loads(Path(path).read_text(encoding="utf-8"))
                self.assertEqual(ARTIFACT_ID, reloaded["artifact_id"])


if __name__ == "__main__":
    unittest.main()
