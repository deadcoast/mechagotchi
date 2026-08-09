"""Pins for cycle 26 P5: the probe artifacts carry their own edges.

DR 0050 froze the probe geometry, rewired the three consumers to one
shared loader, and named its own remainder precisely (item 2 of "What
this record does NOT do"): `occupancy_saturation_stage0.json` and
`reachability_escalation_stage0.json` were committed BEFORE the rewire,
so neither carries `edges_source` in its body — each depends on a draw
it cannot prove. *"Regenerating them is a re-run of each, named rather
than silently skipped."*

P5 is that named re-run, DR 0053-shaped: the committed artifacts stay
exactly as they are; each study re-runs through its own committed
builder (imported, never re-implemented) at its documented defaults,
and the result is written as a NEW restated artifact beside the
original — a new id, a `restates` pointer, and `parameters.edges_source`
naming the committed frozen geometry. The pre-registered expectation:
the studies are deterministic under the frozen edges, so every
committed number reproduces EXACTLY (`restated_identical`); any
difference is per-key recorded and the verdict is `restated_with_deltas`
— a finding, not a patch. DR 0046's comparability rule applies
throughout: nothing here reads one geometry against the other.
"""

import json
import sys
import unittest
from pathlib import Path

LAB_DIR = Path(__file__).resolve().parent
ROOT = LAB_DIR.parents[1]
if str(LAB_DIR) not in sys.path:
    sys.path.insert(0, str(LAB_DIR))

from probe_artifact_restatement import (  # noqa: E402
    PRE_REGISTERED_RULE,
    RESTATEMENTS,
    compare_restatement,
    judge_restatement,
    restate_report,
)


class PreRegistrationTests(unittest.TestCase):
    def test_the_rule_is_pre_registered_and_names_both_verdicts(self):
        rule = PRE_REGISTERED_RULE.lower()
        self.assertIn("pre-registered", rule)
        self.assertIn("restated_identical", rule)
        self.assertIn("restated_with_deltas", rule)

    def test_both_named_restatements_are_carried(self):
        self.assertEqual(
            sorted(RESTATEMENTS),
            ["occupancy_saturation", "reachability_escalation"],
        )
        for spec in RESTATEMENTS.values():
            self.assertIn("committed_artifact", spec)
            self.assertIn("restated_artifact_id", spec)


class CompareTests(unittest.TestCase):
    def test_identical_bodies_compare_identical(self):
        committed = {"metrics": {"a": 1, "nested": {"b": [1, 2]}}}
        restated = {"metrics": {"a": 1, "nested": {"b": [1, 2]}}}
        result = compare_restatement(committed, restated, allowed_added=())
        self.assertTrue(result["identical"])
        self.assertEqual(result["differing_paths"], [])

    def test_an_allowed_addition_does_not_break_identity(self):
        committed = {"parameters": {"seed": 7}}
        restated = {"parameters": {"seed": 7, "edges_source": "frozen"}}
        result = compare_restatement(
            committed, restated, allowed_added=("parameters.edges_source",)
        )
        self.assertTrue(result["identical"])
        self.assertEqual(result["added_paths"], ["parameters.edges_source"])

    def test_a_changed_value_is_reported_by_path(self):
        committed = {"metrics": {"ceiling": 460}}
        restated = {"metrics": {"ceiling": 458}}
        result = compare_restatement(committed, restated, allowed_added=())
        self.assertFalse(result["identical"])
        self.assertEqual(result["differing_paths"], ["metrics.ceiling"])

    def test_an_unexpected_addition_is_a_difference(self):
        committed = {"metrics": {}}
        restated = {"metrics": {"surprise": 1}}
        result = compare_restatement(committed, restated, allowed_added=())
        self.assertFalse(result["identical"])
        self.assertEqual(result["added_paths"], ["metrics.surprise"])

    def test_a_removed_key_is_a_difference(self):
        committed = {"metrics": {"kept": 1, "gone": 2}}
        restated = {"metrics": {"kept": 1}}
        result = compare_restatement(committed, restated, allowed_added=())
        self.assertFalse(result["identical"])
        self.assertEqual(result["removed_paths"], ["metrics.gone"])


class JudgeTests(unittest.TestCase):
    def test_identical_earns_the_identical_verdict(self):
        self.assertEqual(
            judge_restatement(
                {"identical": True, "differing_paths": [], "added_paths": [],
                 "removed_paths": []},
                edges_source_present=True,
            )["verdict"],
            "restated_identical",
        )

    def test_deltas_earn_the_deltas_verdict(self):
        judged = judge_restatement(
            {"identical": False, "differing_paths": ["metrics.x"],
             "added_paths": [], "removed_paths": []},
            edges_source_present=True,
        )
        self.assertEqual(judged["verdict"], "restated_with_deltas")

    def test_a_restatement_without_edges_is_refused(self):
        # The entire point of the re-run is the in-body draw; a
        # restated artifact that still cannot prove its geometry is not
        # a restatement.
        judged = judge_restatement(
            {"identical": True, "differing_paths": [], "added_paths": [],
             "removed_paths": []},
            edges_source_present=False,
        )
        self.assertEqual(judged["verdict"], "refuse_missing_edges")


class RestateWrapperTests(unittest.TestCase):
    def test_the_wrapper_stamps_the_new_identity_and_pointer(self):
        committed = {"artifact_id": "old_stage0", "metrics": {"a": 1}}
        rerun = {"artifact_id": "old_stage0", "metrics": {"a": 1}}
        restated = restate_report(
            rerun,
            restated_artifact_id="old_edged_stage0",
            restates="data/archives/old_stage0.json",
            restatement_check={"verdict": "restated_identical"},
        )
        self.assertEqual(restated["artifact_id"], "old_edged_stage0")
        self.assertEqual(restated["restates"], "data/archives/old_stage0.json")
        self.assertEqual(
            restated["restatement_check"]["verdict"], "restated_identical"
        )
        # The rerun body itself is not mutated.
        self.assertEqual(rerun["artifact_id"], "old_stage0")


class RestatedArtifactTests(unittest.TestCase):
    """Pins over the WRITTEN restated artifacts (the run's output)."""

    def _load(self, name: str) -> tuple[dict, dict]:
        spec = RESTATEMENTS[name]
        committed = json.loads(
            (ROOT / spec["committed_artifact"]).read_text(encoding="utf-8")
        )
        restated_path = (
            ROOT / "data" / "archives" / f"{spec['restated_artifact_id']}.json"
        )
        self.assertTrue(
            restated_path.exists(),
            f"restated artifact missing: run the P5 module ({restated_path})",
        )
        return committed, json.loads(restated_path.read_text(encoding="utf-8"))

    def test_both_restated_artifacts_carry_their_edges(self):
        for name in RESTATEMENTS:
            _, restated = self._load(name)
            self.assertIn("edges_source", restated["parameters"], name)

    def test_both_restated_artifacts_point_at_their_committed_originals(self):
        for name, spec in RESTATEMENTS.items():
            _, restated = self._load(name)
            self.assertEqual(
                restated["restates"], spec["committed_artifact"], name
            )
            self.assertEqual(
                restated["artifact_id"], spec["restated_artifact_id"], name
            )

    def test_the_restatement_checks_carry_a_pre_registered_verdict(self):
        for name in RESTATEMENTS:
            _, restated = self._load(name)
            self.assertIn(
                restated["restatement_check"]["verdict"],
                ("restated_identical", "restated_with_deltas"),
                name,
            )

    def test_the_committed_bodies_still_do_not_carry_edges(self):
        # The committed originals are records and stay exactly as they
        # were — the restatement lives BESIDE them, never inside them.
        for name in RESTATEMENTS:
            committed, _ = self._load(name)
            self.assertNotIn("edges_source", json.dumps(committed), name)


if __name__ == "__main__":
    unittest.main()
