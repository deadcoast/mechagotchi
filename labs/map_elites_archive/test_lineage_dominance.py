"""Cycle 22 L2: the documented lineage-dominance clause, judged at last.

`deep-research.md:205` states the MAP-Elites evaluation gate in two
halves: *"archive coverage >= 25% on a 576-cell repertoire after 20k
evaluations; no single lineage > 40% of occupied cells"*. The coverage
half has been judged five times (Phase E, DR 0032, K2's symmetric E4
re-run). **The dominance half has never been measured at all.**

These pins fix the contract: the loop gains an additive lineage seam
(byte-identical when off, proven), a founder is derived from the
engine's own recorded ancestry rather than guessed, and the verdict is
computed by a rule pre-registered in the module before any run — with
`pass` and `refuse` equally first-class.

The clause is also the quantitative form of Evolution Q1
(`research/questions.md`: *"Can MAP-Elites preserve multiple companion
families instead of one dominant optimum?"*), which Phase E answered
qualitatively with 52 recurrent families but never against this bar.
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

from lineage_dominance import (  # noqa: E402
    ARTIFACT_ID,
    DOMINANCE_BAR,
    ARCHIVE_CELLS,
    DOCUMENTED_REPERTOIRE_CELLS,
    build_lineage_dominance_report,
    founder_of,
    judge_dominance,
)
from lineage_dominance import write_lineage_dominance_artifacts  # noqa: E402

TINY = dict(population=16, target_evaluations=64, rng_seed=31)


class FounderDerivationTests(unittest.TestCase):
    def test_a_seed_grid_is_its_own_founder(self):
        # Depth 0, no recorded ancestry: the creature founds its line.
        grid = {"grid_id": "mg_seed16_001", "lineage": {"ancestor_ids": []}}
        self.assertEqual("mg_seed16_001", founder_of(grid))

    def test_a_descendant_reports_the_OLDEST_ancestor(self):
        # generate.py composes `[*parent_ancestors, parent_grid_id]`, so
        # ancestry accumulates oldest-first and element 0 is the
        # founder. Taking the LAST element would report the parent —
        # a different question entirely.
        grid = {
            "grid_id": "gen_ffff",
            "lineage": {"ancestor_ids": ["mg_seed16_001", "gen_aaaa", "gen_bbbb"]},
        }
        self.assertEqual("mg_seed16_001", founder_of(grid))

    def test_a_missing_or_malformed_lineage_falls_back_to_the_grid_itself(self):
        # Never invent an ancestor; a creature with no recorded line is
        # its own founder, and that is reported as such.
        self.assertEqual("solo", founder_of({"grid_id": "solo"}))
        self.assertEqual("solo", founder_of({"grid_id": "solo", "lineage": None}))


class PreRegisteredRuleTests(unittest.TestCase):
    def test_the_bar_is_the_documented_one(self):
        # deep-research.md:205 — "no single lineage > 40% of occupied
        # cells". The bar is a documented constant, not a tuned one.
        self.assertEqual(0.40, DOMINANCE_BAR)

    def test_a_share_at_the_bar_passes_and_above_it_refuses(self):
        # "> 40%" is the documented wording: exactly 40% is NOT a
        # violation. The boundary is part of the rule, so it is pinned.
        self.assertEqual("pass", judge_dominance(0.40)["verdict"])
        self.assertEqual("refuse", judge_dominance(0.4001)["verdict"])
        self.assertEqual("pass", judge_dominance(0.10)["verdict"])

    def test_the_verdict_carries_the_rule_it_was_judged_by(self):
        judged = judge_dominance(0.5)
        self.assertIn("rule", judged)
        self.assertIn("deep-research", judged["rule"])

    def test_the_repertoire_divergence_is_declared_not_silently_substituted(self):
        # The documented clause pairs with a 576-cell repertoire; the
        # proven geometry is 512 (8x8x8, DR 0029/E1). Judging one bar
        # against the other's population without saying so is exactly
        # the statistic error L1 just caught.
        self.assertEqual(512, ARCHIVE_CELLS)
        self.assertEqual(576, DOCUMENTED_REPERTOIRE_CELLS)
        self.assertNotEqual(ARCHIVE_CELLS, DOCUMENTED_REPERTOIRE_CELLS)


class LoopLineageSeamTests(unittest.TestCase):
    def test_the_seam_is_byte_identical_when_off(self):
        implicit = run_evaluation_loop(**TINY)
        explicit = run_evaluation_loop(collect_lineage=False, **TINY)
        self.assertEqual(implicit, explicit)
        self.assertNotIn("lineage_collection", implicit)

    def test_collecting_lineage_adds_exactly_one_key(self):
        off = run_evaluation_loop(**TINY)
        on = run_evaluation_loop(collect_lineage=True, **TINY)
        self.assertEqual({"lineage_collection"}, set(on) - set(off))
        self.assertEqual(
            off, {k: v for k, v in on.items() if k != "lineage_collection"}
        )

    def test_one_lineage_record_per_occupied_niche(self):
        # The clause's denominator is OCCUPIED cells, so the collection
        # must cover exactly the occupied niches — no more, no fewer.
        result = run_evaluation_loop(collect_lineage=True, **TINY)
        collection = result["lineage_collection"]
        self.assertEqual(
            result["archive_summary"]["occupied_niches"],
            len(collection["elites"]),
        )
        self.assertEqual(
            result["archive_summary"]["occupied_niches"],
            collection["occupied_niches"],
        )

    def test_every_elite_record_carries_the_ancestry_the_founder_comes_from(self):
        # The loop COLLECTS; the instrument DERIVES. Keeping the
        # founder rule in one pinned place (`founder_of`) is what stops
        # the two from drifting apart, so the loop emits the engine's
        # recorded ancestry verbatim and nothing more.
        result = run_evaluation_loop(collect_lineage=True, **TINY)
        for record in result["lineage_collection"]["elites"]:
            self.assertIn("niche", record)
            self.assertIn("grid_id", record)
            self.assertIsInstance(record["lineage"]["ancestor_ids"], list)
            # …and the shared rule applies directly to the record.
            self.assertTrue(founder_of(record))


class LineageDominanceReportTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.report = build_lineage_dominance_report(**TINY)

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

    def test_every_founder_line_is_reported_with_a_share(self):
        # The exact structural invariant: one share per founder line,
        # covering the whole archive. (The shares are rounded for the
        # artifact, so their sum is only ~1 — asserting equality to
        # 6 places would be pinning float rounding, not the science.)
        metrics = self.report["metrics"]
        self.assertEqual(
            metrics["distinct_founders"], len(metrics["founder_share"])
        )
        self.assertAlmostEqual(
            1.0, sum(metrics["founder_share"].values()), places=3
        )

    def test_the_max_share_is_the_largest_share_reported(self):
        metrics = self.report["metrics"]
        self.assertAlmostEqual(
            max(metrics["founder_share"].values()),
            metrics["max_founder_share"],
            places=6,
        )

    def test_the_verdict_follows_the_pre_registered_rule(self):
        metrics = self.report["metrics"]
        expected = judge_dominance(metrics["max_founder_share"])["verdict"]
        self.assertEqual(expected, self.report["decision"]["verdict"])

    def test_the_documented_divergence_rides_in_the_artifact(self):
        metrics = self.report["metrics"]
        self.assertEqual(512, metrics["archive_cells"])
        self.assertEqual(576, metrics["documented_repertoire_cells"])

    def test_the_artifact_writes_and_reloads(self):
        with tempfile.TemporaryDirectory() as tmp:
            written = write_lineage_dominance_artifacts(Path(tmp), self.report)
            self.assertTrue(written)
            for path in written:
                reloaded = json.loads(Path(path).read_text(encoding="utf-8"))
                self.assertEqual(ARTIFACT_ID, reloaded["artifact_id"])


if __name__ == "__main__":
    unittest.main()
