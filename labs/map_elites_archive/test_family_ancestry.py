"""Cycle 23 M4: ancestry versus morphology — do the recurrent families share ancestors?

L2 named the question and never asked it. Phase E measured recurrent
**morphological** families by coarse-descriptor intersection; L2 measured
founder **lines** by recorded ancestry. They are different objects — one
is descriptor similarity, the other is who descends from whom — and both
are now exposed. Do morphologically-recurrent families trace to common
ancestors, or **converge from different lines**? Convergence would be a
genuine ALife result about the descriptor space, and it bears on
Evolution Q3.

These pins fix the contract:

* the family rule is E5's OWN (`recurrent_families.family_key`) and the
  founder rule is L2's OWN (`lineage_dominance.founder_of`) — both
  imported, never re-implemented, so this study cannot quietly measure
  different objects than the two it is comparing;
* the null is **MEASURED by shuffling**, not assumed: founder labels are
  permuted across elites and the statistic recomputed, which is what
  "more than chance" has to mean here;
* single-member families are **excluded and counted**, because their
  largest-founder share is 1.0 by construction and would manufacture
  common descent out of arithmetic;
* the verdict names what it can and cannot claim: `convergent` is the
  NULL, so it is an absence of evidence for common descent, and the
  positive evidence for convergence is reported separately as the
  distinct-founder count.
"""

import json
import sys
import tempfile
import unittest
from pathlib import Path

LAB_DIR = Path(__file__).resolve().parent
if str(LAB_DIR) not in sys.path:
    sys.path.insert(0, str(LAB_DIR))

from lineage_dominance import founder_of  # noqa: E402
from recurrent_families import family_key  # noqa: E402

from family_ancestry import (  # noqa: E402
    ARTIFACT_ID,
    COMMON_DESCENT_Z,
    PRE_REGISTERED_RULE,
    build_family_ancestry_report,
    family_founder_stats,
    judge_ancestry,
    shuffled_null,
    write_family_ancestry_artifacts,
)


class FamilyFounderStatisticTests(unittest.TestCase):
    def test_the_family_and_founder_rules_are_the_IMPORTED_ones(self):
        # If this study re-implemented either rule it would be comparing
        # two objects that are not the ones the ledger reports.
        self.assertEqual((0, 1, 2), family_key([1, 3, 5]))
        self.assertEqual(
            "mg_seed16_001",
            founder_of({"grid_id": "x", "lineage": {"ancestor_ids": ["mg_seed16_001", "y"]}}),
        )

    def test_single_member_families_are_EXCLUDED_and_counted(self):
        # A one-member family has a largest-founder share of 1.0 by
        # construction. Including them would manufacture common descent
        # out of arithmetic.
        elites = [
            {"family": (0, 0, 0), "founder": "a"},
            {"family": (1, 1, 1), "founder": "b"},
            {"family": (1, 1, 1), "founder": "c"},
        ]
        stats = family_founder_stats(elites)
        self.assertEqual(1, stats["families_scored"])
        self.assertEqual(1, stats["single_member_families_excluded"])

    def test_a_family_from_ONE_founder_scores_share_one(self):
        elites = [
            {"family": (0, 0, 0), "founder": "a"},
            {"family": (0, 0, 0), "founder": "a"},
        ]
        stats = family_founder_stats(elites)
        self.assertEqual(1.0, stats["mean_largest_founder_share"])
        self.assertEqual(1.0, stats["mean_distinct_founders_per_family"])

    def test_a_family_from_DIFFERENT_founders_scores_low(self):
        elites = [
            {"family": (0, 0, 0), "founder": name} for name in "abcd"
        ]
        stats = family_founder_stats(elites)
        self.assertEqual(0.25, stats["mean_largest_founder_share"])
        self.assertEqual(4.0, stats["mean_distinct_founders_per_family"])

    def test_no_scorable_family_is_refused_rather_than_averaged_to_zero(self):
        with self.assertRaises(ValueError):
            family_founder_stats([{"family": (0, 0, 0), "founder": "a"}])


class ShuffledNullTests(unittest.TestCase):
    def test_the_null_is_measured_by_permuting_founders_not_assumed(self):
        elites = [
            {"family": (i // 3, 0, 0), "founder": f"f{i % 4}"} for i in range(12)
        ]
        null = shuffled_null(elites, rounds=32, rng_seed=7)
        self.assertGreater(null["mean"], 0.0)
        self.assertGreaterEqual(null["stdev"], 0.0)
        self.assertEqual(32, null["rounds"])

    def test_the_null_is_deterministic_under_its_seed(self):
        elites = [
            {"family": (i // 3, 0, 0), "founder": f"f{i % 4}"} for i in range(12)
        ]
        first = shuffled_null(elites, rounds=16, rng_seed=11)
        second = shuffled_null(elites, rounds=16, rng_seed=11)
        self.assertEqual(first, second)

    def test_the_null_PRESERVES_both_marginals(self):
        # Permuting founder labels keeps the family sizes and the founder
        # line sizes exactly as observed — the null must differ from the
        # observation only in the pairing, or it tests the wrong thing.
        elites = [
            {"family": (i // 3, 0, 0), "founder": f"f{i % 4}"} for i in range(12)
        ]
        null = shuffled_null(elites, rounds=8, rng_seed=3)
        self.assertEqual(
            sorted(e["founder"] for e in elites), sorted(null["founder_multiset"])
        )


class PreRegisteredRuleTests(unittest.TestCase):
    def test_the_bar_is_a_z_against_the_MEASURED_null(self):
        self.assertEqual(2.0, COMMON_DESCENT_Z)
        self.assertIn("MEASURED", PRE_REGISTERED_RULE)

    def test_families_far_MORE_founder_homogeneous_than_chance_are_common_descent(self):
        judged = judge_ancestry(observed=0.9, null_mean=0.4, null_stdev=0.05)
        self.assertEqual("common_descent", judged["verdict"])

    def test_families_no_more_homogeneous_than_chance_are_convergent(self):
        judged = judge_ancestry(observed=0.41, null_mean=0.40, null_stdev=0.05)
        self.assertEqual("convergent", judged["verdict"])

    def test_the_boundary_at_the_z_bar_is_common_descent(self):
        judged = judge_ancestry(observed=0.5, null_mean=0.4, null_stdev=0.05)
        self.assertAlmostEqual(2.0, judged["z"], places=6)
        self.assertEqual("common_descent", judged["verdict"])

    def test_a_zero_spread_null_is_refused_rather_than_made_infinite(self):
        with self.assertRaises(ValueError):
            judge_ancestry(observed=0.5, null_mean=0.4, null_stdev=0.0)

    def test_the_verdict_states_that_convergent_is_the_NULL(self):
        # The honesty pin: `convergent` is an absence of evidence for
        # common descent, not positive proof of convergence. The
        # positive evidence is the distinct-founder count, reported
        # separately.
        judged = judge_ancestry(observed=0.41, null_mean=0.40, null_stdev=0.05)
        self.assertIn("absence of evidence", judged["interpretation"].lower())


class FamilyAncestryReportTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.report = build_family_ancestry_report(
            population=16,
            target_evaluations=64,
            rng_seeds=(31, 97),
            shuffle_rounds=32,
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

    def test_every_run_is_judged_by_the_pre_registered_rule(self):
        for run in self.report["metrics"]["runs"]:
            with self.subTest(seed=run["rng_seed"]):
                expected = judge_ancestry(
                    observed=run["mean_largest_founder_share"],
                    null_mean=run["null"]["mean"],
                    null_stdev=run["null"]["stdev"],
                )
                self.assertEqual(expected["verdict"], run["verdict"])

    def test_cross_run_founder_identity_is_declared_UNDEFINED(self):
        # The structural point that reshapes L2's question: each run
        # builds its own bootstrap, so a founder id in one run is not the
        # same object as a founder id in another. "Do recurrent families
        # share ancestry ACROSS runs" is not merely unmeasured — it is
        # not well posed.
        blocked = " ".join(self.report["blocked_states"])
        self.assertIn("not well posed", blocked)

    def test_the_recurrent_family_count_is_read_from_the_ARTIFACT(self):
        # The count moved 52 -> 54 when the vocabulary changed and the
        # prose never followed. This study reads the committed artifact
        # rather than repeating a number from a document.
        recurrence = self.report["metrics"]["e5_recurrence"]
        self.assertEqual(
            recurrence["committed_recurrent_family_count"],
            recurrence["recomputed_from_artifact"],
        )

    def test_the_artifact_writes_and_reloads(self):
        with tempfile.TemporaryDirectory() as tmp:
            written = write_family_ancestry_artifacts(Path(tmp), self.report)
            self.assertTrue(written)
            for path in written:
                reloaded = json.loads(Path(path).read_text(encoding="utf-8"))
                self.assertEqual(ARTIFACT_ID, reloaded["artifact_id"])


if __name__ == "__main__":
    unittest.main()
