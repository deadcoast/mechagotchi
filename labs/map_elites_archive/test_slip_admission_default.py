"""Pins for cycle 24 N4: the `slip_admission` default, decided.

Written BEFORE the module (the RED run is pasted into the experiment
report). DR 0047 adopted three arms, recorded `parents` as its own
rule's winner, and WITHHELD the loop default because the arms separate
in the OPPOSITE direction on two dimensions that rule never gated. It
then named its decider exactly:

    "a re-run with quality and archive legality pre-registered as gates
     alongside coverage, over multiple seeds. On this evidence the
     likely winner is `insertion`, not `parents` — and that is exactly
     why it needs its own gate rather than a paragraph here."

So the pins assert that the gate is written first, that **every one of
the four gates can fail independently**, and that **refusing all three
is reachable**. A gate that cannot fail is a bug; a gate that cannot
refuse would make DR 0047's prediction self-fulfilling.

Measured values are never asserted; they are the study's output.
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

from slip_admission_default import (  # noqa: E402
    ARTIFACT_ID,
    INVASIVENESS_ORDER,
    PRE_REGISTERED_BOUND_S,
    PRE_REGISTERED_RULE,
    SEED_COUNT,
    build_slip_admission_default_report,
    choose_default,
    judge_arm,
    measured_control,
)
from slip_admission_arms import ARMS  # noqa: E402


def _passing(**overrides) -> dict:
    payload = {
        "arm": "insertion",
        "refusals_by_seed": [0, 0, 0],
        "illegal_by_seed": [0, 0, 0],
        "coverage_cost": 0.01,
        "coverage_control": 0.033,
        "quality_delta": +2.0,
        "quality_control": 5.0,
    }
    payload.update(overrides)
    return payload


class PreRegistrationTests(unittest.TestCase):
    def test_the_rule_names_the_two_gates_dr0047_asked_for(self):
        rule = PRE_REGISTERED_RULE.lower()
        self.assertIn("pre-registered", rule)
        self.assertIn("quality", rule)
        self.assertIn("legality", rule)
        self.assertIn("measured", rule)

    def test_multiple_seeds_as_dr0047_required(self):
        self.assertGreaterEqual(SEED_COUNT, 3)

    def test_the_tie_break_is_dr0047s_invasiveness_order_verbatim(self):
        self.assertEqual(INVASIVENESS_ORDER, ("parents", "insertion", "bootstrap"))

    def test_every_dr0047_arm_is_carried(self):
        self.assertEqual(tuple(ARMS), ("bootstrap", "insertion", "parents"))

    def test_the_wall_clock_bound_is_derived_from_the_incumbent_loop(self):
        # DR 0028: derived from the incumbent's own bound, never picked.
        # Four configurations at SEED_COUNT seeds each.
        self.assertEqual(PRE_REGISTERED_BOUND_S % (4 * SEED_COUNT), 0)


class MeasuredControlTests(unittest.TestCase):
    def test_the_control_is_the_spread_of_the_incumbents_own_seeds(self):
        self.assertAlmostEqual(
            measured_control([0.90, 0.88, 0.86]), 0.04, places=9
        )

    def test_an_identical_set_of_seeds_has_a_zero_control(self):
        self.assertEqual(measured_control([0.9, 0.9, 0.9]), 0.0)

    def test_fewer_than_two_seeds_is_refused(self):
        with self.assertRaises(ValueError):
            measured_control([0.9])


class ConfigurationMatchTests(unittest.TestCase):
    """N4 must run the loop DR 0047 withheld on, or nothing compares.

    A first run of this study used population 512 — a parameter the
    module invented rather than inherited — and produced numbers that
    could not be read against DR 0047 at all. These pins exist so that
    cannot recur silently.
    """

    def test_dr0047_parameters_are_READ_from_its_artifact(self):
        from slip_admission_default import load_dr0047_baseline

        committed = load_dr0047_baseline()
        for key in (
            "population",
            "target_evaluations",
            "rng_seed",
            "coverage",
            "qd_score",
            "refusals",
            "slip_illegal_elites",
        ):
            self.assertIn(key, committed)

    def test_the_module_default_population_is_dr0047s(self):
        from slip_admission_default import (
            build_slip_admission_default_report,
            load_dr0047_baseline,
        )
        import inspect

        default = inspect.signature(
            build_slip_admission_default_report
        ).parameters["population"].default
        self.assertEqual(default, load_dr0047_baseline()["population"])

    def test_the_first_seed_is_dr0047s_seed(self):
        from slip_admission_default import _seeds, load_dr0047_baseline

        self.assertEqual(_seeds(3)[0], load_dr0047_baseline()["rng_seed"])

    def test_a_diverged_population_is_caught_not_silently_run(self):
        from slip_admission_default import judge_configuration_match

        committed = {
            "population": 256,
            "target_evaluations": 20_480,
            "rng_seed": 20260709,
        }
        judged = judge_configuration_match(
            committed=committed,
            population=512,
            target_evaluations=20_480,
            first_seed=20260709,
        )
        self.assertEqual(judged["verdict"], "configuration_diverged")
        self.assertEqual(len(judged["mismatches"]), 1)

    def test_the_matching_configuration_passes(self):
        from slip_admission_default import judge_configuration_match

        committed = {
            "population": 256,
            "target_evaluations": 20_480,
            "rng_seed": 20260709,
        }
        judged = judge_configuration_match(
            committed=committed,
            population=256,
            target_evaluations=20_480,
            first_seed=20260709,
        )
        self.assertEqual(judged["verdict"], "configuration_matched")
        self.assertEqual(judged["mismatches"], [])


class GateTests(unittest.TestCase):
    """All four gates, each able to fail on its own."""

    def test_an_arm_passing_everything_is_adoptable(self):
        judged = judge_arm(**_passing())
        self.assertTrue(judged["adoptable"])
        self.assertEqual(judged["failed_gates"], [])

    def test_g1_fails_when_any_seed_still_refuses(self):
        judged = judge_arm(**_passing(refusals_by_seed=[0, 3, 0]))
        self.assertFalse(judged["adoptable"])
        self.assertIn("G1_cause_eliminated", judged["failed_gates"])

    def test_g1_is_structural_across_every_seed_not_a_mean(self):
        # A mean would let one clean seed hide a dirty one.
        self.assertFalse(judge_arm(**_passing(refusals_by_seed=[0, 0, 1]))["adoptable"])

    def test_g2_fails_when_coverage_cost_exceeds_the_measured_control(self):
        judged = judge_arm(**_passing(coverage_cost=0.09, coverage_control=0.033))
        self.assertIn("G2_coverage_preserved", judged["failed_gates"])

    def test_g2_never_penalises_a_coverage_gain(self):
        judged = judge_arm(**_passing(coverage_cost=-0.05, coverage_control=0.001))
        self.assertNotIn("G2_coverage_preserved", judged["failed_gates"])

    def test_g3_fails_when_quality_falls_beyond_the_measured_control(self):
        judged = judge_arm(**_passing(quality_delta=-9.0, quality_control=5.0))
        self.assertIn("G3_quality_preserved", judged["failed_gates"])

    def test_g3_never_penalises_a_quality_gain(self):
        judged = judge_arm(**_passing(quality_delta=+50.0, quality_control=0.001))
        self.assertNotIn("G3_quality_preserved", judged["failed_gates"])

    def test_g3_tolerates_a_decline_inside_the_measured_control(self):
        judged = judge_arm(**_passing(quality_delta=-2.0, quality_control=5.0))
        self.assertNotIn("G3_quality_preserved", judged["failed_gates"])

    def test_g4_fails_when_any_seed_leaves_an_illegal_elite(self):
        judged = judge_arm(**_passing(illegal_by_seed=[0, 0, 35]))
        self.assertIn("G4_archive_legality", judged["failed_gates"])

    def test_g4_is_structural_like_g1_not_a_percentage(self):
        # A covenant either holds over the archive or it does not; a
        # "mostly legal" archive is an illegal archive.
        judged = judge_arm(**_passing(illegal_by_seed=[1, 0, 0]))
        self.assertIn("G4_archive_legality", judged["failed_gates"])

    def test_all_four_gates_can_fail_together(self):
        judged = judge_arm(
            **_passing(
                refusals_by_seed=[5, 5, 5],
                illegal_by_seed=[35, 35, 35],
                coverage_cost=0.5,
                quality_delta=-100.0,
            )
        )
        self.assertEqual(len(judged["failed_gates"]), 4)

    def test_a_non_positive_control_is_refused(self):
        # M3's precedent: a zero control would make every cost fatal.
        with self.assertRaises(ValueError):
            judge_arm(**_passing(coverage_control=0.0))
        with self.assertRaises(ValueError):
            judge_arm(**_passing(quality_control=0.0))


class DefaultChoiceTests(unittest.TestCase):
    def test_the_least_invasive_passing_arm_wins(self):
        judged = {
            "parents": {"adoptable": True},
            "insertion": {"adoptable": True},
            "bootstrap": {"adoptable": True},
        }
        chosen = choose_default(judged)
        self.assertEqual(chosen["verdict"], "adopt_default")
        self.assertEqual(chosen["default"], "parents")

    def test_a_failing_least_invasive_arm_yields_to_the_next(self):
        # DR 0047's predicted outcome — reachable, never assumed.
        judged = {
            "parents": {"adoptable": False},
            "insertion": {"adoptable": True},
            "bootstrap": {"adoptable": True},
        }
        chosen = choose_default(judged)
        self.assertEqual(chosen["verdict"], "adopt_default")
        self.assertEqual(chosen["default"], "insertion")

    def test_refusing_all_three_is_reachable_and_first_class(self):
        judged = {arm: {"adoptable": False} for arm in ARMS}
        chosen = choose_default(judged)
        self.assertEqual(chosen["verdict"], "withhold_default")
        self.assertIsNone(chosen["default"])

    def test_the_withholding_says_the_loop_default_does_not_move(self):
        chosen = choose_default({arm: {"adoptable": False} for arm in ARMS})
        self.assertIn("none", chosen["incumbent_default"])

    def test_the_choice_records_every_arm_it_considered(self):
        chosen = choose_default(
            {
                "parents": {"adoptable": False},
                "insertion": {"adoptable": True},
                "bootstrap": {"adoptable": True},
            }
        )
        self.assertEqual(sorted(chosen["passing_arms"]), ["bootstrap", "insertion"])


class ArtifactTests(unittest.TestCase):
    report: dict

    @classmethod
    def setUpClass(cls):
        cls.report = build_slip_admission_default_report(
            population=6, target_evaluations=12, lifecycle_ticks=4, seed_count=2
        )

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

    def test_every_arm_is_judged_on_every_seed(self):
        per_seed = self.report["metrics"]["per_seed"]
        for arm in ARMS:
            self.assertIn(arm, per_seed)
            self.assertEqual(len(per_seed[arm]), 2)

    def test_the_incumbent_is_measured_on_every_seed_for_the_control(self):
        self.assertEqual(len(self.report["metrics"]["per_seed"]["none"]), 2)

    def test_the_decision_carries_the_rule_and_a_verdict(self):
        decision = self.report["decision"]
        self.assertEqual(decision["rule"], PRE_REGISTERED_RULE)
        self.assertIn(
            decision["choice"]["verdict"], ("adopt_default", "withhold_default")
        )

    def test_source_artifact_paths_are_repo_relative(self):
        for path in self.report["source_artifacts"]:
            self.assertFalse(Path(path).is_absolute())
            self.assertNotIn("\\", path)

    def test_artifact_round_trips_as_json(self):
        with tempfile.TemporaryDirectory() as directory:
            from slip_admission_default import (
                write_slip_admission_default_artifacts,
            )

            written = write_slip_admission_default_artifacts(directory, self.report)
            self.assertEqual(len(written), 1)
            reloaded = json.loads(written[0].read_text(encoding="utf-8"))
        self.assertEqual(reloaded["artifact_id"], ARTIFACT_ID)
        self.assertEqual(reloaded["decision"]["rule"], PRE_REGISTERED_RULE)


if __name__ == "__main__":
    unittest.main()
