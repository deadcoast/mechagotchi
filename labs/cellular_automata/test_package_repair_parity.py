"""Parity pin: lab wound-site repair vs promoted mecha_engine.repair.

Runs the Stage 0 lab surfaces (flat import, the authoritative research
behavior from the trained-repair benchmark) and the promoted package
surfaces (mecha_engine.repair through the package src layout) over the
same corpus, seeds, and cycles, and asserts byte-identical results.

Documented equivalence scope: the package surface maps onto the lab entry
points exactly — ``train_repair_model`` onto
``train_neighborhood_repair_model`` (identical defaults: dropout_rates
``(0.1, 0.2, 0.3, 0.4)``, damage_instances 1, epochs 150, learning_rate
1.5, live_class_weight 3.0, rng_seed 20260512; identical example
generation seeding and iteration order, so weights, losses, and every
model field including ``model_id`` match), ``repair_wound_sites`` onto
``repair_with_wound_sites`` (identical most-confident-first fill,
validity-guard substitution order and acceptance rule, metadata, and
``_wound_repaired`` grid-id suffix, with the guard validating through
``mecha_engine.genome.validate_grid`` — the promoted verbatim port of the
lab validator), and ``repair_blind`` onto
``repair_with_neighborhood_model`` (the below-bar blind benchmark
comparator, identical synchronous fill rule and ``_trained_repaired``
suffix) — so the full dictionaries are compared for equality with no
excluded keys. The template-assisted ``repair_with_local_attractor`` has
no package counterpart by design (decision record 0006) and is out of
scope here.

The multi-cycle case pins the guard's benchmark effect: the mg_seed_046
site-aware trajectory (five compounding dropout-0.2 cycles with the
benchmark seeds ``20260512 + index*1000 + cycle`` and per-cycle grid-id
reassignment, exactly as ``run_trained_repair_benchmark`` does) ends
valid with final overlap 1.0 — the trajectory whose guard-off failure
mode motivated the validity guard.

Direction note: labs may import the package for regression evidence; the
reverse (package importing labs) stays forbidden by the repair interface
spec and decision record 0006, and this file lives on the lab side
precisely so the package tree keeps zero lab references.
"""

import sys
import unittest
from pathlib import Path


LAB_DIR = Path(__file__).resolve().parent
REPO_ROOT = LAB_DIR.parents[1]
GRID_GENOME = REPO_ROOT / "labs" / "grid_genome"
PACKAGE_SRC = REPO_ROOT / "packages" / "mecha_engine" / "src"
for path in [LAB_DIR, GRID_GENOME]:
    if str(path) not in sys.path:
        sys.path.insert(0, str(path))
if str(PACKAGE_SRC) not in sys.path:
    sys.path.insert(0, str(PACKAGE_SRC))

from ca_nca_growth_repair import (  # noqa: E402
    apply_stochastic_damage,
    matrix_overlap,
    repair_with_neighborhood_model,
    repair_with_wound_sites,
    structural_agreement,
    train_neighborhood_repair_model,
)
from corpus_builder import build_seed_grids  # noqa: E402
from validator import validate_grid  # noqa: E402

from mecha_engine.repair import (  # noqa: E402
    repair_blind,
    repair_wound_sites as package_repair_wound_sites,
    train_repair_model,
)


TRAINING_COUNT = 40
BENCHMARK_RNG_SEED = 20260512
BENCHMARK_DROPOUT_RATE = 0.2
BENCHMARK_CYCLES = 5


class PackageRepairParityTests(unittest.TestCase):
    seed_grids: list[dict]
    lab_model: dict
    package_model: dict

    @classmethod
    def setUpClass(cls):
        # One full-default benchmark training per side (grids[:40], epochs
        # 150, rng_seed 20260512), shared by every parity case below.
        cls.seed_grids = build_seed_grids()
        training_grids = cls.seed_grids[:TRAINING_COUNT]
        cls.lab_model = train_neighborhood_repair_model(training_grids)
        cls.package_model = train_repair_model(training_grids)

    def _benchmark_damaged_grids(self) -> list[tuple[dict, dict]]:
        """Held-out grids damaged with the benchmark's cycle-1 seeds."""
        damaged_grids = []
        for index, target in enumerate(self.seed_grids[TRAINING_COUNT:]):
            damage_seed = BENCHMARK_RNG_SEED + index * 1000 + 1
            damaged = apply_stochastic_damage(
                target,
                dropout_rate=BENCHMARK_DROPOUT_RATE,
                rng_seed=damage_seed,
                event_index=1,
            )
            damaged_grids.append((target, damaged))
        return damaged_grids

    def test_trained_model_parity_every_field(self):
        self.assertEqual(
            sorted(self.lab_model), sorted(self.package_model)
        )
        for key in sorted(self.lab_model):
            with self.subTest(field=key):
                self.assertEqual(self.lab_model[key], self.package_model[key])
        # model_id is kept identical to the lab's for parity (the interface
        # spec requires the field but pins no other value).
        self.assertEqual(
            "neighborhood_softmax_repair_model_stage0",
            self.package_model["model_id"],
        )
        self.assertEqual(self.lab_model, self.package_model)

    def test_wound_repair_parity_guard_on_and_off_over_heldout_grids(self):
        damaged_grids = self._benchmark_damaged_grids()
        self.assertEqual(10, len(damaged_grids))
        for target, damaged in damaged_grids:
            for validity_guard in [True, False]:
                with self.subTest(
                    target=target["grid_id"], validity_guard=validity_guard
                ):
                    lab_repaired = repair_with_wound_sites(
                        damaged, self.lab_model, validity_guard=validity_guard
                    )
                    package_repaired = package_repair_wound_sites(
                        damaged, self.package_model, validity_guard=validity_guard
                    )
                    self.assertEqual(
                        lab_repaired["cells"], package_repaired["cells"]
                    )
                    self.assertEqual(
                        lab_repaired["organs"], package_repaired["organs"]
                    )
                    self.assertEqual(
                        lab_repaired["metadata"], package_repaired["metadata"]
                    )
                    self.assertEqual(lab_repaired, package_repaired)

    def test_blind_arm_parity_over_heldout_grids(self):
        for target, damaged in self._benchmark_damaged_grids():
            with self.subTest(target=target["grid_id"]):
                lab_repaired = repair_with_neighborhood_model(
                    damaged, self.lab_model
                )
                package_repaired = repair_blind(damaged, self.package_model)
                self.assertEqual(lab_repaired["cells"], package_repaired["cells"])
                self.assertEqual(lab_repaired["organs"], package_repaired["organs"])
                self.assertEqual(
                    lab_repaired["metadata"], package_repaired["metadata"]
                )
                self.assertEqual(lab_repaired, package_repaired)

    def test_site_aware_trajectory_mg_seed_046_ends_valid_with_full_overlap(self):
        targets = self.seed_grids[TRAINING_COUNT:]
        index = next(
            position
            for position, grid in enumerate(targets)
            if grid["grid_id"] == "mg_seed_046"
        )
        target = targets[index]
        current = target
        for cycle in range(1, BENCHMARK_CYCLES + 1):
            damage_seed = BENCHMARK_RNG_SEED + index * 1000 + cycle
            damaged = apply_stochastic_damage(
                current,
                dropout_rate=BENCHMARK_DROPOUT_RATE,
                rng_seed=damage_seed,
                event_index=cycle,
            )
            lab_repaired = repair_with_wound_sites(damaged, self.lab_model)
            package_repaired = package_repair_wound_sites(
                damaged, self.package_model
            )
            self.assertEqual(lab_repaired, package_repaired)
            # Grid-id reassignment exactly as run_trained_repair_benchmark
            # does for the site_aware arm.
            package_repaired["grid_id"] = (
                f"{target['grid_id']}_cycle_{cycle:02d}_site_aware"
            )
            current = package_repaired

        validation = validate_grid(current)
        self.assertTrue(validation.ok, validation.errors)
        self.assertEqual(1.0, matrix_overlap(current, target))
        # The site-aware live-position invariant: one-sided overlap equals
        # two-sided structural agreement identically.
        self.assertEqual(
            matrix_overlap(current, target), structural_agreement(current, target)
        )


if __name__ == "__main__":
    unittest.main()
