"""E3 gates: the consumers are deterministic, the physics labeling is
falsifiable, the replay statistics reconstruct the engine's own rule
exactly, and dataset integrity rides every evaluation."""

import gzip
import json
import sys
import tempfile
import unittest
from pathlib import Path

LAB_DIR = Path(__file__).resolve().parent
ROOT = LAB_DIR.parents[1]
if str(LAB_DIR) not in sys.path:
    sys.path.insert(0, str(LAB_DIR))

from dataset_consumers import (  # noqa: E402
    CORPUS_PROFILE_PATH,
    _physics_label,
    evaluate_learned_on_mutationbench,
    evaluate_replay_corpus,
    load_bench_rows,
)
from dataset_program import build_seed_grids  # noqa: E402
from learned_readability import build_learned_readability_report  # noqa: E402

from mecha_engine.generation import train_generation_model  # noqa: E402

SAMPLE = 150  # a fast slice of the 5000 for the live-evaluation tests


class PhysicsLabelTests(unittest.TestCase):
    """The R3 admission rule on real mutations: monotone across the four
    verified metrics, at least one strict move — falsifiable both ways."""

    BASE = {
        "palette_contrast": 0.5,
        "organ_detectability": 0.5,
        "inverse_component_count": 0.5,
        "animation_anchor_coverage": 0.5,
    }

    def test_strict_monotone_decrease_is_degraded(self):
        child = dict(self.BASE, organ_detectability=0.4)
        self.assertEqual("physics_degraded", _physics_label(self.BASE, child))

    def test_strict_monotone_increase_is_improved(self):
        child = dict(self.BASE, palette_contrast=0.6)
        self.assertEqual("physics_improved", _physics_label(self.BASE, child))

    def test_mixed_moves_are_unlabeled_not_guessed(self):
        child = dict(
            self.BASE, palette_contrast=0.6, organ_detectability=0.4
        )
        self.assertEqual("unlabeled", _physics_label(self.BASE, child))

    def test_no_moves_are_unlabeled(self):
        self.assertEqual("unlabeled", _physics_label(self.BASE, dict(self.BASE)))


class MutationbenchConsumerTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        seeds = build_seed_grids()
        cls.seeds_by_id = {seed["grid_id"]: seed for seed in seeds}
        cls.generation_model = train_generation_model(seeds)
        cls.slip_profile = json.loads(
            CORPUS_PROFILE_PATH.read_text(encoding="utf-8")
        )
        report = build_learned_readability_report(rng_seed=20260706)
        cls.model = {
            "weights": report["model"]["weights"],
            "reference_features": report["model"]["reference_features"],
        }
        cls.rows = load_bench_rows()[:SAMPLE]
        cls.result = evaluate_learned_on_mutationbench(
            cls.rows,
            cls.seeds_by_id,
            cls.generation_model,
            cls.slip_profile,
            cls.model,
        )

    def test_every_regenerated_candidate_matches_its_signature(self):
        self.assertEqual(0, self.result["signature_mismatches"])

    def test_the_label_accounting_is_complete(self):
        labels = self.result["labels"]
        self.assertEqual(
            self.result["case_count"],
            labels["physics_degraded"]
            + labels["physics_improved"]
            + labels["unlabeled"]
            + self.result["signature_mismatches"],
        )
        self.assertEqual(
            labels["physics_degraded"] + labels["physics_improved"],
            self.result["labeled_count"],
        )

    def test_the_accuracy_is_a_real_measurement(self):
        self.assertGreater(self.result["labeled_count"], 0)
        accuracy = self.result["pairwise_accuracy"]
        self.assertIsNotNone(accuracy)
        self.assertGreaterEqual(accuracy, 0.0)
        self.assertLessEqual(accuracy, 1.0)

    def test_the_evaluation_is_deterministic(self):
        again = evaluate_learned_on_mutationbench(
            self.rows,
            self.seeds_by_id,
            self.generation_model,
            self.slip_profile,
            self.model,
        )
        self.assertEqual(self.result, again)


class ReplayCorpusStatisticTests(unittest.TestCase):
    """The engine-faithful statistic, verified on a crafted corpus with
    hand-computed expectations — the padding rule is the whole point."""

    def _write_corpus(self, tmp: Path, rows: list[dict]) -> Path:
        path = tmp / "corpus.jsonl.gz"
        with gzip.open(path, "wt", encoding="utf-8") as handle:
            for row in rows:
                handle.write(json.dumps(row) + "\n")
        return path

    def _tick(self, episode, policy, tick, balance, alive, horizon=4):
        return {
            "episode_id": episode,
            "policy": policy,
            "tick": tick,
            "balance": balance,
            "alive": alive,
            "death_cause": None if alive else "starvation",
            "ticks_requested": horizon,
        }

    def test_post_death_ticks_count_as_zero_exactly_like_the_engine(self):
        # Episode A (policy "early_death"): dies after 2 of 4 ticks with
        # perfect balance -> engine need_balance = (1+1+0+0)/4 = 0.5.
        # Episode B (policy "steady"): lives all 4 ticks at 0.6 -> 0.6.
        # The naive lived-tick mean would call them 1.0 vs 0.6 — the
        # survivorship bias the engine's rule exists to prevent.
        rows = (
            [self._tick("a", "early_death", t, 1.0, t < 2) for t in (1, 2)]
            + [self._tick("b", "steady", t, 0.6, True) for t in (1, 2, 3, 4)]
        )
        with tempfile.TemporaryDirectory() as tmp:
            result = evaluate_replay_corpus(
                self._write_corpus(Path(tmp), rows)
            )
        early = result["by_policy"]["early_death"]
        steady = result["by_policy"]["steady"]
        self.assertEqual(0.5, early["mean_episode_need_balance"])
        self.assertEqual(1.0, early["mean_balance_per_lived_tick"])
        self.assertEqual(0.6, steady["mean_episode_need_balance"])
        self.assertEqual(0.0, early["survival_rate"])
        self.assertEqual(1.0, steady["survival_rate"])
        self.assertEqual({"starvation": 1}, early["death_causes"])
        # The engine-faithful ranking puts steady first — the naive
        # statistic would have flipped it.
        self.assertEqual(["steady", "early_death"], result["need_balance_ranking"])

    def test_the_shipped_corpus_evaluation_ran_at_full_scale(self):
        # The committed artifact consumed all 100k+ ticks with the
        # switchboard leading on the engine-faithful statistic at full
        # survival — pin the shipped numbers' shape.
        artifact = json.loads(
            (
                ROOT / "data" / "datasets" / "dataset_consumers_stage0.json"
            ).read_text(encoding="utf-8")
        )
        replay = artifact["metrics"]["replay_corpus_evaluation"]
        self.assertGreaterEqual(replay["tick_count"], 100_000)
        self.assertTrue(replay["switchboard_beats_all_on_need_balance"])
        self.assertEqual(
            1.0, replay["by_policy"]["switchboard"]["survival_rate"]
        )


if __name__ == "__main__":
    unittest.main()
