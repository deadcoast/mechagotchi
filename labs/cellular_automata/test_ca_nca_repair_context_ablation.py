import json
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
LAB_DIR = Path(__file__).resolve().parent
GRID_GENOME = ROOT / "labs" / "grid_genome"
if str(LAB_DIR) not in sys.path:
    sys.path.insert(0, str(LAB_DIR))
if str(GRID_GENOME) not in sys.path:
    sys.path.insert(0, str(GRID_GENOME))

from ca_nca_repair_context_ablation import (  # noqa: E402
    retrieval_ceiling_probe,
    run_context_ablation,
    train_context_repair_model,
    write_context_ablation_artifacts,
)
from corpus_builder import build_seed_grids  # noqa: E402


class CaNcaRepairContextAblationTests(unittest.TestCase):
    def test_retrieval_ceiling_probe_bounds_the_exemplar_family(self):
        seed_grids = build_seed_grids()
        probe = retrieval_ceiling_probe(
            seed_grids[:10],
            seed_grids[10:13],
            dropout_rate=0.2,
            rng_seed=20260512,
        )

        self.assertEqual(3, len(probe["per_target"]))
        for entry in probe["per_target"]:
            self.assertGreater(entry["oracle_agreement"], 0.0)
            self.assertLessEqual(entry["oracle_agreement"], 1.0)
            # Retrieval under damage can never beat the oracle exemplar.
            self.assertLessEqual(
                entry["retrieved_agreement"], entry["oracle_agreement"]
            )
        self.assertGreater(probe["mean_oracle_agreement"], 0.0)
        self.assertGreaterEqual(
            probe["mean_oracle_agreement"],
            probe["mean_retrieved_agreement"],
        )

    def test_train_context_repair_model_is_deterministic_and_templateless(self):
        training_grids = build_seed_grids()[:8]

        first = train_context_repair_model(
            training_grids,
            use_context=True,
            self_play=False,
            epochs=15,
            rng_seed=20260512,
        )
        second = train_context_repair_model(
            training_grids,
            use_context=True,
            self_play=False,
            epochs=15,
            rng_seed=20260512,
        )

        self.assertFalse(first["target_template_used"])
        self.assertTrue(first["use_context"])
        self.assertEqual(first["weights"], second["weights"])
        self.assertGreater(first["example_count"], 0)
        # Self-play retraining adds examples from the model's own repairs.
        with_self_play = train_context_repair_model(
            training_grids,
            use_context=True,
            self_play=True,
            epochs=15,
            rng_seed=20260512,
        )
        self.assertGreater(
            with_self_play["example_count"], first["example_count"]
        )

    def test_run_context_ablation_measures_all_configs_on_heldout_grids(self):
        report = run_context_ablation(
            training_count=10,
            holdout_count=2,
            cycles=2,
            dropout_rate=0.2,
            epochs=15,
            rng_seed=20260512,
        )

        self.assertEqual(
            "ca_nca_repair_context_ablation_stage0", report["lab_id"]
        )
        self.assertEqual(
            {
                "plain_replication",
                "context",
                "context_self_play",
                "context_self_play_prune",
                "plain_self_play_prune",
            },
            set(report["configs"].keys()),
        )
        for config in report["configs"].values():
            self.assertGreaterEqual(config["mean_final_overlap"], 0.0)
            self.assertLessEqual(config["mean_final_overlap"], 1.0)
            self.assertGreaterEqual(config["mean_final_agreement"], 0.0)
            self.assertLessEqual(config["validity_rate"], 1.0)
        self.assertIn("retrieval_ceiling", report)
        self.assertIn(
            report["decision"]["status"],
            {
                "reject_context_conditioning",
                "adopt_context_conditioning",
            },
        )
        # The verdict must be derived from the measured configs, not pinned.
        context_helps = (
            report["configs"]["context"]["mean_final_overlap"]
            > report["configs"]["plain_replication"]["mean_final_overlap"]
        )
        expected = (
            "adopt_context_conditioning"
            if context_helps
            else "reject_context_conditioning"
        )
        self.assertEqual(expected, report["decision"]["status"])

    def test_write_context_ablation_artifacts_creates_report_and_readme(self):
        report = run_context_ablation(
            training_count=10,
            holdout_count=2,
            cycles=2,
            dropout_rate=0.2,
            epochs=10,
            rng_seed=7,
        )
        with tempfile.TemporaryDirectory() as temp_dir:
            output_dir = Path(temp_dir)
            write_context_ablation_artifacts(output_dir, report)

            artifact = output_dir / "ca_nca_repair_context_ablation_stage0.json"
            self.assertTrue(artifact.exists())
            self.assertTrue(
                (output_dir / "repair_context_ablation_README.md").exists()
            )
            loaded = json.loads(artifact.read_text(encoding="utf-8"))
            self.assertEqual(
                "ca_nca_repair_context_ablation_stage0", loaded["lab_id"]
            )


if __name__ == "__main__":
    unittest.main()
