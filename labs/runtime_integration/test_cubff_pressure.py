import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
LAB_DIR = Path(__file__).resolve().parent
CUBFF = ROOT / "labs" / "cubff_transducer"
for path in [LAB_DIR, CUBFF]:
    if str(path) not in sys.path:
        sys.path.insert(0, str(path))

from cubff_transducer import extract_cubff_features  # noqa: E402

from mecha_engine_runtime_loop import (  # noqa: E402
    run_mecha_engine_evolution_loop,
)


def _stable_snapshot(index: int) -> dict:
    # A calmly replicating soup: one motif dominates, high replication,
    # low churn -> low instability / low mutation pressure.
    tape = [7, 7, 7, 8, 7, 7, 7, 8] * 8
    return {
        "snapshot_id": f"stable_{index:03d}",
        "epoch": 100 + index,
        "language": "bff_noheads",
        "program_size": 64,
        "tape": tape,
        "replication_scores": [64, 64, 64, 48, 64, 64, 48, 64],
        "brotli_size": 12,
        "lineage_events": [{"parent": 0, "child": 0}],
    }


def _chaotic_snapshot(index: int) -> dict:
    # A turbulent soup: near-uniform tape, weak replication, high churn
    # -> high instability / high mutation pressure.
    tape = [(index * 13 + p * 31) % 64 for p in range(64)]
    return {
        "snapshot_id": f"chaotic_{index:03d}",
        "epoch": 100 + index,
        "language": "bff_noheads",
        "program_size": 64,
        "tape": tape,
        "replication_scores": [0, 4, 8, 0, 4, 8, 0, 4],
        "brotli_size": 57,
        "lineage_events": [
            {"parent": p % 8, "child": (p + 1) % 8} for p in range(8)
        ],
    }


STABLE = [_stable_snapshot(i) for i in range(6)]
CHAOTIC = [_chaotic_snapshot(i) for i in range(6)]


class CubffPressurePremiseTests(unittest.TestCase):
    """The snapshots must actually differ in mutation pressure."""

    def test_chaotic_snapshots_carry_higher_instability(self):
        from cubff_transducer import features_to_traits

        stable = features_to_traits(extract_cubff_features(STABLE[0]))
        chaotic = features_to_traits(extract_cubff_features(CHAOTIC[0]))
        self.assertGreater(
            chaotic["mutation_pressure"], stable["mutation_pressure"]
        )


class CubffPressureEvolutionTests(unittest.TestCase):
    """R2 (DR 0018): CuBFF dynamics shape every generation."""

    KW = dict(
        generations=3,
        population=4,
        damage_cycles=2,
        ticks=16,
        repair_epochs=20,
        rng_seed=20260512,
    )

    def test_pressure_source_drives_a_recorded_per_generation_multiplier(self):
        report = run_mecha_engine_evolution_loop(
            cubff_pressure_source=CHAOTIC, **self.KW
        )
        self.assertEqual(
            "mecha_engine_evolution_cubff_pressure_stage0", report["lab_id"]
        )
        cubff = report["cubff_pressure"]
        self.assertEqual(3, len(cubff["by_generation"]))
        for entry in cubff["by_generation"]:
            self.assertIn("snapshot_id", entry)
            self.assertIn("mutation_pressure", entry)
            self.assertIn("dropout_multiplier", entry)
            self.assertGreaterEqual(entry["dropout_multiplier"], 0.5)
            self.assertLessEqual(entry["dropout_multiplier"], 1.6)

    def test_chaotic_pressure_damages_more_than_stable(self):
        chaotic = run_mecha_engine_evolution_loop(
            cubff_pressure_source=CHAOTIC, **self.KW
        )
        stable = run_mecha_engine_evolution_loop(
            cubff_pressure_source=STABLE, **self.KW
        )
        chaotic_removed = sum(
            cycle["removed_cell_count"]
            for generation in chaotic["generations"]
            for creature in generation["creatures"]
            for cycle in creature["cycles"]
        )
        stable_removed = sum(
            cycle["removed_cell_count"]
            for generation in stable["generations"]
            for creature in generation["creatures"]
            for cycle in creature["cycles"]
        )
        # CuBFF dynamics visibly move the ecosystem.
        self.assertGreater(chaotic_removed, stable_removed)

    def test_cubff_never_sets_cell_tokens_only_pressure_scalars(self):
        report = run_mecha_engine_evolution_loop(
            cubff_pressure_source=CHAOTIC, **self.KW
        )
        # The semantic-compiler rule: only scalars cross the boundary.
        for entry in report["cubff_pressure"]["by_generation"]:
            self.assertEqual(
                {"snapshot_id", "mutation_pressure", "dropout_multiplier"},
                set(entry),
            )
        self.assertEqual(
            "lineage_dynamics_to_mutation_weights_pipeline_c",
            report["cubff_pressure"]["semantic_rule"],
        )

    def test_deterministic(self):
        first = run_mecha_engine_evolution_loop(
            cubff_pressure_source=CHAOTIC, **self.KW
        )
        second = run_mecha_engine_evolution_loop(
            cubff_pressure_source=CHAOTIC, **self.KW
        )
        self.assertEqual(first, second)

    def test_absent_source_is_byte_identical_frozen(self):
        report = run_mecha_engine_evolution_loop(**self.KW)
        self.assertNotIn("cubff_pressure", report)
        self.assertEqual(
            "mecha_engine_evolution_loop_stage0", report["lab_id"]
        )


if __name__ == "__main__":
    unittest.main()
