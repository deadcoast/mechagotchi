"""Pins for cycle 25 O3: the headline studies restated under the adopted default.

DR 0053's rule 3, scoped there and left unfinished by design:
`evaluation_loop_scale` (the source of **DR 0042's headline coverage
0.8984**) and `coverage_qd_gates` (the E4 gates) are the only two of the
eight loop callers whose migration is a real question rather than an
evidence-destroying regeneration.

**This restates; it does not overwrite.** DR 0053's rule 2 —
*a measurement does not improve, it is reproduced or superseded by a new
measurement answering a new question* — means the committed incumbent
artifacts stay exactly as they are. "What does the loop achieve under
the adopted default" is a **new question**, so it gets a **new
artifact**, and the delta is reported between them.

**The gate that can fail**: the documented E4 gates are re-judged
VERBATIM (`judge_gates` imported, never re-implemented). If a gate that
PASSED under the incumbent FAILS under the adopted default, that is a
blocking finding — the adoption's consequence would need its own record
rather than being absorbed into a restatement.
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

from adopted_default_restatement import (  # noqa: E402
    ADOPTED_ARM,
    ARTIFACT_ID,
    INCUMBENT_ARM,
    PRE_REGISTERED_RULE,
    build_restatement_report,
    judge_gate_regressions,
    load_committed_e4,
    load_committed_headline,
    write_restatement_artifacts,
)


class ProvenanceTests(unittest.TestCase):
    """Both sides are READ from committed artifacts, never re-measured."""

    def test_the_committed_e4_evidence_is_read_not_rerun(self):
        committed = load_committed_e4()
        self.assertEqual(len(committed["map_elites_runs"]), 10)
        self.assertEqual(len(committed["ga_runs"]), 10)

    def test_the_ga_control_is_reused_because_the_arm_cannot_touch_it(self):
        # `run_ga_baseline` takes no slip_admission — the plain GA is
        # unaffected by the arm, so re-running it would spend an hour to
        # reproduce numbers that cannot have moved.
        committed = load_committed_e4()
        for run in committed["ga_runs"]:
            self.assertIn("best_fitness", run)
            self.assertIn("history_coverage", run)

    def test_the_dr0042_headline_is_read_from_its_own_artifact(self):
        headline = load_committed_headline()
        # The number DR 0042 quotes, read rather than transcribed.
        self.assertEqual(headline["incumbent_coverage"], 0.898438)
        self.assertEqual(headline["rng_seed"], 20260709)

    def test_the_adopted_side_of_the_headline_comes_from_N4(self):
        # N4 already measured `insertion` at DR 0047's/DR 0042's own
        # seed and configuration; re-running it would be a second
        # measurement of a committed number.
        headline = load_committed_headline()
        self.assertEqual(headline["adopted_coverage"], 0.880859)

    def test_the_arms_are_the_incumbent_and_the_adopted_default(self):
        self.assertEqual(INCUMBENT_ARM, "none")
        self.assertEqual(ADOPTED_ARM, "insertion")


class RegressionGateTests(unittest.TestCase):
    """A documented gate that passed and now fails is a BLOCKING finding."""

    def test_no_regression_when_every_gate_still_passes(self):
        judged = judge_gate_regressions(
            incumbent={"coverage_gate_met": True, "recurrent_family_gate_met": True},
            adopted={"coverage_gate_met": True, "recurrent_family_gate_met": True},
        )
        self.assertEqual(judged["verdict"], "no_regression")
        self.assertEqual(judged["regressed_gates"], [])

    def test_a_gate_that_passed_and_now_fails_is_a_regression(self):
        judged = judge_gate_regressions(
            incumbent={"coverage_gate_met": True},
            adopted={"coverage_gate_met": False},
        )
        self.assertEqual(judged["verdict"], "regression")
        self.assertEqual(judged["regressed_gates"], ["coverage_gate_met"])

    def test_a_gate_that_already_failed_is_not_a_regression(self):
        # DR 0032's GA-advantage clause has been refuted three times.
        # Failing again is the incumbent's own state, not a consequence
        # of the adoption, and conflating them would blame the arm for
        # something it did not do.
        judged = judge_gate_regressions(
            incumbent={"ga_advantage_gate_met": False},
            adopted={"ga_advantage_gate_met": False},
        )
        self.assertEqual(judged["verdict"], "no_regression")
        self.assertEqual(judged["already_failing_gates"], ["ga_advantage_gate_met"])

    def test_a_gate_that_failed_and_now_passes_is_recorded_as_a_gain(self):
        judged = judge_gate_regressions(
            incumbent={"ga_advantage_gate_met": False},
            adopted={"ga_advantage_gate_met": True},
        )
        self.assertEqual(judged["recovered_gates"], ["ga_advantage_gate_met"])
        self.assertEqual(judged["verdict"], "no_regression")

    def test_every_documented_gate_is_compared_not_a_chosen_subset(self):
        judged = judge_gate_regressions(
            incumbent={"a_gate_met": True, "b_gate_met": True},
            adopted={"a_gate_met": True, "b_gate_met": False},
        )
        self.assertEqual(sorted(judged["compared_gates"]), ["a_gate_met", "b_gate_met"])

    def test_a_gate_missing_from_either_side_is_refused(self):
        # Silently skipping a gate would let a regression hide.
        with self.assertRaises(ValueError):
            judge_gate_regressions(
                incumbent={"a_gate_met": True, "b_gate_met": True},
                adopted={"a_gate_met": True},
            )


class PreRegistrationTests(unittest.TestCase):
    def test_the_rule_names_restatement_and_the_regression_gate(self):
        rule = PRE_REGISTERED_RULE.lower()
        self.assertIn("pre-registered", rule)
        self.assertIn("restat", rule)
        self.assertIn("regression", rule)
        self.assertIn("never overwrites", rule)


class ArtifactTests(unittest.TestCase):
    report: dict

    @classmethod
    def setUpClass(cls):
        cls.report = build_restatement_report(seeds=[20260709], population=8,
                                              target_evaluations=16,
                                              lifecycle_ticks=4)

    def test_report_carries_every_required_artifact_key(self):
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
            self.assertIn(key, self.report)
        self.assertEqual(self.report["artifact_id"], ARTIFACT_ID)

    def test_the_report_carries_both_sides_and_their_delta(self):
        headline = self.report["metrics"]["headline"]
        for key in ("incumbent_coverage", "adopted_coverage", "delta"):
            self.assertIn(key, headline)

    def test_the_incumbent_artifacts_are_named_as_preserved(self):
        blocked = " ".join(self.report["blocked_states"]).lower()
        self.assertIn("overwrite", blocked)

    def test_source_artifact_paths_are_repo_relative(self):
        for path in self.report["source_artifacts"]:
            self.assertFalse(Path(path).is_absolute())
            self.assertNotIn("\\", path)

    def test_artifact_round_trips_as_json(self):
        with tempfile.TemporaryDirectory() as directory:
            written = write_restatement_artifacts(directory, self.report)
            self.assertEqual(len(written), 1)
            reloaded = json.loads(written[0].read_text(encoding="utf-8"))
        self.assertEqual(reloaded["artifact_id"], ARTIFACT_ID)
        self.assertEqual(reloaded["decision"]["rule"], PRE_REGISTERED_RULE)


if __name__ == "__main__":
    unittest.main()
