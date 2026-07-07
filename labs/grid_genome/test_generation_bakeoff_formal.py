import tempfile
import unittest
from pathlib import Path

from generation_bakeoff_formal import (
    build_generation_bakeoff_report,
    corpus_split,
    write_generation_bakeoff_artifacts,
)


class CorpusDisciplineTests(unittest.TestCase):
    """T17: train/dev/holdout discipline enters the repo here."""

    def test_split_is_deterministic_and_disjoint(self):
        split = corpus_split()
        self.assertEqual(30, len(split["train"]))
        self.assertEqual(10, len(split["dev"]))
        self.assertEqual(10, len(split["holdout"]))
        ids = [g["grid_id"] for part in ("train", "dev", "holdout") for g in split[part]]
        self.assertEqual(50, len(set(ids)))
        again = corpus_split()
        self.assertEqual(
            [g["grid_id"] for g in split["holdout"]],
            [g["grid_id"] for g in again["holdout"]],
        )


class FormalBakeoffTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.report = build_generation_bakeoff_report(
            outputs_per_seed=3, bootstrap_resamples=200
        )

    def test_four_arms_trained_on_train_evaluated_on_holdout(self):
        arms = {arm["arm"] for arm in self.report["arms"]}
        self.assertEqual(
            {
                "random_mutation",
                "markov_raw",
                "constrained_wfc",
                "package_hybrid",
            },
            arms,
        )
        for arm in self.report["arms"]:
            self.assertEqual(
                self.report["protocol"]["candidates_per_arm"],
                arm["candidate_count"],
            )
            for metric in (
                "validity_rate",
                "alignment_rate",
                "mean_symmetry",
                "mean_novelty",
                "generation_seconds",
            ):
                self.assertIn(metric, arm)
            ci = arm["validity_ci95"]
            self.assertLessEqual(ci[0], arm["validity_rate"])
            self.assertLessEqual(arm["validity_rate"], ci[1])

    def test_gate_selects_the_simplest_qualifying_arm(self):
        gate = self.report["gate"]
        qualifying = [
            arm["arm"]
            for arm in self.report["arms"]
            if arm["validity_rate"] >= 0.95
        ]
        if qualifying:
            order = [
                "random_mutation",
                "markov_raw",
                "constrained_wfc",
                "package_hybrid",
            ]
            simplest = min(qualifying, key=order.index)
            self.assertEqual(simplest, gate["selected_arm"])
        else:
            self.assertIsNone(gate["selected_arm"])
        self.assertIn(
            gate["shipped_choice_verdict"], ("confirmed", "challenged")
        )

    def test_blocked_states_record_the_deferred_protocol_arms(self):
        blocked = " ".join(self.report["blocked_states"])
        self.assertIn("human", blocked)
        self.assertIn("size", blocked)

    def test_deterministic_modulo_wall_clock(self):
        again = build_generation_bakeoff_report(
            outputs_per_seed=3, bootstrap_resamples=200
        )

        def strip_timing(report):
            import json as _json
            clone = _json.loads(_json.dumps(report))
            for arm in clone["arms"]:
                arm.pop("generation_seconds")
            return clone

        self.assertEqual(strip_timing(self.report), strip_timing(again))

    def test_artifacts_write(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            output = Path(temp_dir)
            write_generation_bakeoff_artifacts(output, self.report)
            self.assertTrue(
                (output / "generation_bakeoff_formal_stage0.json").exists()
            )


if __name__ == "__main__":
    unittest.main()
