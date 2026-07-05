import json
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
LAB_DIR = Path(__file__).resolve().parent
if str(LAB_DIR) not in sys.path:
    sys.path.insert(0, str(LAB_DIR))

from mecha_engine_runtime_loop import (  # noqa: E402
    run_mecha_engine_evolution_loop,
    run_mecha_engine_runtime_loop,
    write_evolution_loop_artifacts,
    write_runtime_loop_artifacts,
)


class MechaEngineRuntimeLoopTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # Small but complete loop: every stage runs for every creature.
        cls.report = run_mecha_engine_runtime_loop(
            count=3,
            ticks=24,
            dropout_rate=0.2,
            repair_epochs=150,
            rng_seed=20260512,
        )

    def test_loop_runs_every_stage_for_every_creature(self):
        report = self.report
        self.assertEqual("mecha_engine_runtime_loop_stage0", report["lab_id"])
        self.assertEqual(3, len(report["runs"]))
        for run in report["runs"]:
            stages = run["stages"]
            self.assertTrue(stages["parent_valid"])
            self.assertTrue(stages["candidate_valid"])
            self.assertTrue(stages["render_packet_serializable"])
            self.assertTrue(stages["episode_pre_completed"])
            self.assertGreater(run["damage"]["removed_cell_count"], 0)
            self.assertTrue(stages["repaired_valid"])
            # The wound-site contract: repair restores exactly the damaged
            # positions, so the live-cell set matches the pre-damage
            # candidate; only tokens may differ.
            self.assertEqual(1.0, run["repair"]["position_restoration"])
            self.assertGreaterEqual(run["repair"]["token_restoration"], 0.5)
            # SLIP alignment retention is a measured stage (the loop's
            # first integration finding: lifecycle rejects unaligned
            # grids); an aligned repair flows through episode, scoring,
            # and the archive — an unaligned one is skipped honestly.
            if stages["slip_aligned_post_repair"]:
                self.assertTrue(stages["episode_post_completed"])
                self.assertTrue(stages["scored"])
                self.assertIn(
                    run["archive_decision"],
                    {"inserted", "replaced", "kept_incumbent"},
                )
            else:
                self.assertFalse(stages["scored"])
                self.assertEqual("skipped_unaligned", run["archive_decision"])
                self.assertIsNone(run["score"])

    def test_summary_carries_cross_module_evidence(self):
        summary = self.report["summary"]
        self.assertEqual(1.0, summary["candidate_valid_rate"])
        self.assertEqual(1.0, summary["repaired_valid_rate"])
        # With the SLIP-aware guard the runtime hands the active profile
        # to repair, so alignment survives damage/repair.
        self.assertEqual(1.0, summary["slip_alignment_retention_rate"])
        self.assertGreaterEqual(summary["archived_run_count"], 1)
        self.assertGreaterEqual(summary["archive"]["filled_niches"], 1)
        self.assertTrue(self.report["provenance"]["ledger_ok"])
        self.assertTrue(self.report["provenance"]["ci_ok"])
        # Proxy readability must stay visibly uncalibrated (deferred).
        archived = next(
            run for run in self.report["runs"] if run["score"] is not None
        )
        self.assertEqual(
            "not_collected",
            archived["score"]["readability"]["manual_rating_status"],
        )

    def test_loop_is_deterministic(self):
        again = run_mecha_engine_runtime_loop(
            count=3,
            ticks=24,
            dropout_rate=0.2,
            repair_epochs=150,
            rng_seed=20260512,
        )
        self.assertEqual(self.report, again)

    def test_write_artifacts_creates_report_and_readme(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            output_dir = Path(temp_dir)
            write_runtime_loop_artifacts(output_dir, self.report)
            artifact = output_dir / "mecha_engine_runtime_loop_stage0.json"
            self.assertTrue(artifact.exists())
            self.assertTrue((output_dir / "README.md").exists())
            loaded = json.loads(artifact.read_text(encoding="utf-8"))
            self.assertEqual("mecha_engine_runtime_loop_stage0", loaded["lab_id"])


class MechaEngineEvolutionLoopTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.report = run_mecha_engine_evolution_loop(
            generations=2,
            population=3,
            damage_cycles=2,
            ticks=24,
            repair_epochs=150,
            rng_seed=20260512,
        )

    def test_generations_descend_from_archive_elites(self):
        report = self.report
        self.assertEqual("mecha_engine_evolution_loop_stage0", report["lab_id"])
        self.assertEqual(2, len(report["generations"]))
        self.assertEqual(
            "seed_pool", report["generations"][0]["parent_source"]
        )
        self.assertEqual(
            "archive_elites", report["generations"][1]["parent_source"]
        )
        # Multi-generation ancestry is real: a later-generation creature's
        # lineage generation exceeds any single-cycle creature's.
        self.assertGreaterEqual(report["summary"]["max_lineage_generation"], 2)

    def test_every_creature_survives_repeated_damage_repair_cycles(self):
        for generation in self.report["generations"]:
            for creature in generation["creatures"]:
                self.assertTrue(creature["stages"]["candidate_valid"])
                self.assertTrue(creature["stages"]["all_cycles_aligned"])
                self.assertTrue(creature["stages"]["all_cycles_valid"])
                self.assertTrue(creature["stages"]["scored"])
                self.assertEqual(2, len(creature["cycles"]))
                for cycle in creature["cycles"]:
                    # A stochastic damage event may destroy zero cells
                    # (repair is then a no-op); the position guarantee
                    # holds either way.
                    self.assertGreaterEqual(cycle["removed_cell_count"], 0)
                    self.assertEqual(1.0, cycle["position_restoration"])

    def test_summary_tracks_archive_growth_and_retention(self):
        summary = self.report["summary"]
        self.assertEqual(1.0, summary["candidate_valid_rate"])
        self.assertEqual(1.0, summary["slip_alignment_retention_rate"])
        self.assertGreaterEqual(summary["archive"]["filled_niches"], 1)
        self.assertEqual(6, summary["creature_count"])
        self.assertEqual(12, summary["total_damage_events"])
        # Damage genuinely occurred across the run even if individual
        # events removed nothing.
        self.assertGreater(summary["guard_substitution_total"] + sum(
            cycle["removed_cell_count"]
            for generation in self.report["generations"]
            for creature in generation["creatures"]
            for cycle in creature["cycles"]
        ), 0)

    def test_evolution_loop_is_deterministic(self):
        again = run_mecha_engine_evolution_loop(
            generations=2,
            population=3,
            damage_cycles=2,
            ticks=24,
            repair_epochs=150,
            rng_seed=20260512,
        )
        self.assertEqual(self.report, again)

    def test_write_artifacts_creates_report_and_readme(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            output_dir = Path(temp_dir)
            write_evolution_loop_artifacts(output_dir, self.report)
            artifact = output_dir / "mecha_engine_evolution_loop_stage0.json"
            self.assertTrue(artifact.exists())
            self.assertTrue((output_dir / "evolution_loop_README.md").exists())
            loaded = json.loads(artifact.read_text(encoding="utf-8"))
            self.assertEqual("mecha_engine_evolution_loop_stage0", loaded["lab_id"])


if __name__ == "__main__":
    unittest.main()
