"""Pins for cycle 25 O4: Stage 2's undispositioned generator arms.

`deep-research.md` names two generator-adjacent methods that have never
been dispositioned — no card, no prototype, no reject/watch verdict —
since the dossier was written. This slice judges both.

**THE CHARTER'S FRAMING WAS WRONG FOR ONE OF THEM, and the pins encode
the correction.** O4's charter said *"judge them against the adopted
generation layer on its own bake-off terms"*. Measured against the
dossier rather than the charter:

* **CPPN** — *"Indirect encoding… optional late-stage"*, priority
  low-to-medium, integration risk **High**, stance *"keep as a late
  exploratory generator"*. A generator bake-off is exactly its
  documented role.
* **Shape grammar** — filed under **Constraint systems** with WFC and
  SAT/SMT, stance *"**use as validator or post-generator
  stabilizer**"*. It is **explicitly not** proposed as a primary
  generator, so a bake-off would test it at a job the dossier never
  gave it, and a rejection earned that way would mean nothing.

So each is judged **in its documented role**, and the artifact records
that the roles differ. **Rejecting both is first-class** — DR 0031
already refuted the hybrid arm, and a measured refutation is worth more
than a third generator nobody asked for.
"""

import json
import sys
import tempfile
import unittest
from pathlib import Path

LAB_DIR = Path(__file__).resolve().parent
ROOT = LAB_DIR.parents[1]
for _sub in ("labs/wfc_grid", "labs/grid_genome", "labs/readability_benchmark"):
    _path = str(ROOT / _sub)
    if _path not in sys.path:
        sys.path.insert(0, _path)

from stage2_generator_arms import (  # noqa: E402
    ARTIFACT_ID,
    ARMS,
    DOCUMENTED_ROLES,
    PRE_REGISTERED_RULE,
    PRE_RUN_PREDICTION,
    build_stage2_arms_report,
    cppn_grid,
    judge_generator_arm,
    judge_stabilizer_arm,
    shape_grammar_stabilize,
    write_stage2_arms_artifacts,
)


class DocumentedRoleTests(unittest.TestCase):
    """Each method is judged at the job the dossier gave it."""

    def test_both_undispositioned_arms_are_carried(self):
        self.assertEqual(sorted(ARMS), ["cppn", "shape_grammar"])

    def test_cppn_is_judged_as_a_generator(self):
        self.assertEqual(DOCUMENTED_ROLES["cppn"]["role"], "generator")

    def test_shape_grammar_is_judged_as_a_stabilizer_not_a_generator(self):
        # The correction this slice makes to its own charter.
        role = DOCUMENTED_ROLES["shape_grammar"]
        self.assertEqual(role["role"], "post_generator_stabilizer")
        self.assertIn("validator or post-generator stabilizer", role["dossier_stance"])

    def test_every_arm_quotes_the_dossier_stance_it_is_judged_against(self):
        for name in ARMS:
            self.assertTrue(DOCUMENTED_ROLES[name]["dossier_stance"])

    def test_the_verdict_vocabulary_is_the_algorithm_card_one(self):
        # reject / watch / prototype / adopt — the fixed template's own
        # decision verbs, not invented ones.
        judged = judge_generator_arm(
            arm="cppn",
            validity_rate=0.0,
            baseline_validity_rate=1.0,
            readability=0.0,
            baseline_readability=1.0,
            distinct_rate=0.0,
        )
        self.assertIn(judged["verdict"], ("reject", "watch", "prototype", "adopt"))


class CppnMechanismTests(unittest.TestCase):
    def test_a_cppn_grid_is_deterministic_for_a_seed(self):
        first = cppn_grid(rng_seed=7, size=8)
        second = cppn_grid(rng_seed=7, size=8)
        self.assertEqual(first, second)

    def test_different_seeds_give_different_bodies(self):
        self.assertNotEqual(cppn_grid(rng_seed=1, size=8), cppn_grid(rng_seed=2, size=8))

    def test_the_cppn_produces_a_grid_shaped_object(self):
        grid = cppn_grid(rng_seed=3, size=8)
        self.assertIn("cells", grid)
        self.assertIn("grid_size", grid)
        self.assertEqual(grid["grid_size"], [8, 8])

    def test_the_indirect_encoding_is_a_function_of_position(self):
        # The whole point of a CPPN: the body is f(x, y), so symmetry
        # and repeated motifs come free. A body whose cells do not vary
        # with position is not a CPPN body.
        grid = cppn_grid(rng_seed=11, size=8)
        roles = {(cell["x"], cell["y"]): cell["role"] for cell in grid["cells"]}
        self.assertGreater(len(roles), 1)


class ShapeGrammarMechanismTests(unittest.TestCase):
    def test_the_stabilizer_returns_a_grid_and_a_trace(self):
        grid = cppn_grid(rng_seed=5, size=8)
        stabilized, trace = shape_grammar_stabilize(grid)
        self.assertIn("cells", stabilized)
        self.assertIsInstance(trace, list)

    def test_the_stabilizer_never_mutates_its_input(self):
        grid = cppn_grid(rng_seed=5, size=8)
        before = json.dumps(grid, sort_keys=True)
        shape_grammar_stabilize(grid)
        self.assertEqual(before, json.dumps(grid, sort_keys=True))

    def test_every_applied_production_is_named_in_the_trace(self):
        # A stabilizer that cannot say what it did is a black box, and
        # the dossier's stance for this method is "validator" — an
        # unexplainable validator is worthless.
        grid = cppn_grid(rng_seed=9, size=8)
        _, trace = shape_grammar_stabilize(grid)
        for entry in trace:
            self.assertIn("rule", entry)


class GeneratorGateTests(unittest.TestCase):
    """CPPN's gate — the documented generator threshold."""

    def test_an_arm_that_cannot_produce_valid_bodies_is_rejected(self):
        judged = judge_generator_arm(
            arm="cppn",
            validity_rate=0.0,
            baseline_validity_rate=1.0,
            readability=0.0,
            baseline_readability=0.83,
            distinct_rate=1.0,
        )
        self.assertEqual(judged["verdict"], "reject")

    def test_an_arm_matching_the_adopted_layer_is_at_least_watched(self):
        judged = judge_generator_arm(
            arm="cppn",
            validity_rate=1.0,
            baseline_validity_rate=1.0,
            readability=0.9,
            baseline_readability=0.83,
            distinct_rate=1.0,
        )
        self.assertIn(judged["verdict"], ("watch", "prototype", "adopt"))

    def test_validity_is_the_first_gate_and_nothing_offsets_it(self):
        # Novelty cannot buy a generator that produces invalid bodies:
        # the validator is the engine's own hard floor.
        judged = judge_generator_arm(
            arm="cppn",
            validity_rate=0.02,
            baseline_validity_rate=1.0,
            readability=0.99,
            baseline_readability=0.83,
            distinct_rate=1.0,
        )
        self.assertEqual(judged["verdict"], "reject")
        self.assertIn("validity", judged["reason"].lower())

    def test_a_negative_rate_is_refused(self):
        with self.assertRaises(ValueError):
            judge_generator_arm(
                arm="cppn",
                validity_rate=-0.1,
                baseline_validity_rate=1.0,
                readability=0.5,
                baseline_readability=0.5,
                distinct_rate=1.0,
            )


class StabilizerGateTests(unittest.TestCase):
    """Shape grammar's gate — its OWN documented job."""

    def test_a_stabilizer_that_raises_validity_is_at_least_watched(self):
        judged = judge_stabilizer_arm(
            arm="shape_grammar",
            validity_before=0.10,
            validity_after=0.60,
            distinct_before=1.0,
            distinct_after=0.95,
        )
        self.assertIn(judged["verdict"], ("watch", "prototype", "adopt"))

    def test_a_stabilizer_that_does_not_raise_validity_is_rejected(self):
        judged = judge_stabilizer_arm(
            arm="shape_grammar",
            validity_before=0.10,
            validity_after=0.10,
            distinct_before=1.0,
            distinct_after=1.0,
        )
        self.assertEqual(judged["verdict"], "reject")

    def test_over_constraining_novelty_is_the_documented_risk_and_is_gated(self):
        # The dossier's named risk for constraint systems is
        # "over-constraining novelty". A stabilizer that collapses the
        # population to one body has not helped.
        judged = judge_stabilizer_arm(
            arm="shape_grammar",
            validity_before=0.10,
            validity_after=1.00,
            distinct_before=1.0,
            distinct_after=0.02,
        )
        self.assertEqual(judged["verdict"], "reject")
        self.assertIn("novelty", judged["reason"].lower())


class PreRegistrationTests(unittest.TestCase):
    def test_the_rule_names_the_role_correction(self):
        rule = PRE_REGISTERED_RULE.lower()
        self.assertIn("pre-registered", rule)
        self.assertIn("documented role", rule)
        self.assertIn("stabilizer", rule)

    def test_a_prediction_is_recorded_before_the_run(self):
        self.assertIn("cppn", PRE_RUN_PREDICTION.lower())


class ArtifactTests(unittest.TestCase):
    report: dict

    @classmethod
    def setUpClass(cls):
        cls.report = build_stage2_arms_report(count=12, size=16)

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

    def test_both_arms_are_dispositioned(self):
        verdicts = self.report["decision"]["arms"]
        self.assertEqual(sorted(verdicts), ["cppn", "shape_grammar"])
        for entry in verdicts.values():
            self.assertIn(entry["verdict"], ("reject", "watch", "prototype", "adopt"))

    def test_source_artifact_paths_are_repo_relative(self):
        for path in self.report["source_artifacts"]:
            self.assertFalse(Path(path).is_absolute())
            self.assertNotIn("\\", path)

    def test_artifact_round_trips_as_json(self):
        with tempfile.TemporaryDirectory() as directory:
            written = write_stage2_arms_artifacts(directory, self.report)
            self.assertEqual(len(written), 1)
            reloaded = json.loads(written[0].read_text(encoding="utf-8"))
        self.assertEqual(reloaded["artifact_id"], ARTIFACT_ID)
        self.assertEqual(reloaded["decision"]["rule"], PRE_REGISTERED_RULE)


if __name__ == "__main__":
    unittest.main()
