import json
import tempfile
import unittest
from pathlib import Path

from generation_bakeoff16 import (
    build_bakeoff_report,
    build_hybrid_corpus,
    write_bakeoff_artifacts,
)
from wfc_grid import split_corpus, train_wfc_model

import sys

LAB_DIR = Path(__file__).resolve().parent
REPO_ROOT = LAB_DIR.parents[1]
GRID_GENOME = REPO_ROOT / "labs" / "grid_genome"
if str(GRID_GENOME) not in sys.path:
    sys.path.insert(0, str(GRID_GENOME))

from corpus_builder import build_seed_grids_16  # noqa: E402
from validator import validate_grid  # noqa: E402


class BakeoffTests(unittest.TestCase):
    report: dict

    @classmethod
    def setUpClass(cls):
        cls.report = build_bakeoff_report()

    def test_report_is_deterministic(self):
        again = build_bakeoff_report()
        self.assertEqual(
            json.dumps(self.report, sort_keys=True),
            json.dumps(again, sort_keys=True),
        )

    def test_all_five_documented_arms_ran(self):
        self.assertEqual(
            ["constrained", "hybrid", "markov", "random", "wfc"],
            sorted(self.report["metrics"]["arms"]),
        )
        for name, arm in self.report["metrics"]["arms"].items():
            with self.subTest(arm=name):
                self.assertEqual(100, arm["candidate_count"])

    def test_dossier_validity_bar_verdicts(self):
        arms = self.report["metrics"]["arms"]
        # The gated generators clear the bar; the raw proposal source and
        # the mutation baseline are honest floors below it.
        for name in ["constrained", "wfc", "hybrid"]:
            self.assertTrue(arms[name]["meets_validity_bar"], name)
        for name in ["markov", "random"]:
            self.assertFalse(arms[name]["meets_validity_bar"], name)

    def test_the_pre_registered_verdict_wfc_wins_hybrid_refuted(self):
        # Deterministic drift guard (fixed corpus + seed): the verdict is
        # a pure function of the batches. A corpus change legitimately
        # re-runs the rule — this pin makes that visible, never silent.
        verdict = self.report["metrics"]["verdict"]
        self.assertEqual(["hybrid", "wfc"], sorted(verdict["eligible"]))
        self.assertEqual("wfc", verdict["winner"])
        self.assertTrue(verdict["hybrid_refuted"])
        # The constrained arm is barred from eligibility by the rich-
        # alphabet requirement, not by quality: it clears validity.
        self.assertNotIn("constrained", verdict["eligible"])
        self.assertTrue(
            self.report["metrics"]["arms"]["constrained"]["meets_validity_bar"]
        )

    def test_hybrid_candidates_are_gated_valid(self):
        train = split_corpus(build_seed_grids_16())[0]
        model = train_wfc_model(train)
        batch = build_hybrid_corpus(model, count=10, rng_seed=77)
        for grid in batch:
            with self.subTest(grid_id=grid["grid_id"]):
                self.assertTrue(validate_grid(grid).ok)
                self.assertEqual(
                    "hybrid_wfc_mutation_gate_lab",
                    grid["metadata"]["source"],
                )

    def test_artifact_writer_carries_the_measured_section_separately(self):
        with tempfile.TemporaryDirectory() as tmp:
            output_dir = Path(tmp)
            measured = {
                "context": "test",
                "arms": {"wfc": {"mean_ms_per_candidate": 1.0, "meets_time_bar": True}},
            }
            write_bakeoff_artifacts(output_dir, self.report, measured)
            loaded = json.loads(
                (output_dir / "generation_bakeoff16_stage0.json").read_text(
                    encoding="utf-8"
                )
            )
            self.assertEqual(self.report["metrics"], loaded["metrics"])
            self.assertIn("measured", loaded)
            self.assertIn("context", loaded["measured"])


if __name__ == "__main__":
    unittest.main()
