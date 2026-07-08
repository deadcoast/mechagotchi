"""16x16 repair gates (cycle 09 A3, DR 0029): lab + package, in parity.

The repair feature layout was structurally 8x8 (64-position one-hot,
bias at index 160, range(8) scans). These tests pin the size-parametric
layout at the ratified 16x16 default on BOTH the lab origin and the
promoted package, in exact parity, with wound-site semantics unchanged
and a loud mismatch guard between a model's training scale and the grid
it is asked to repair. Training here uses a 10-grid slice of the 16x16
corpus (the full-corpus 21s stdlib training wall-clock is recorded in
the A3 report; the parity suite's 40-grid 8x8 convention scales the
same way).
"""

import sys
import unittest
from pathlib import Path


LAB_DIR = Path(__file__).resolve().parent
REPO_ROOT = LAB_DIR.parents[1]
GRID_GENOME = REPO_ROOT / "labs" / "grid_genome"
PACKAGE_SRC = REPO_ROOT / "packages" / "mecha_engine" / "src"
for path in [LAB_DIR, GRID_GENOME, PACKAGE_SRC]:
    if str(path) not in sys.path:
        sys.path.insert(0, str(path))

from ca_nca_growth_repair import (  # noqa: E402
    apply_stochastic_damage,
    repair_with_wound_sites,
    train_neighborhood_repair_model,
)
from corpus_builder import build_seed_grids, build_seed_grids_16  # noqa: E402
from validator import validate_grid  # noqa: E402

from mecha_engine.repair import (  # noqa: E402
    repair_wound_sites as package_repair_wound_sites,
)
from mecha_engine.repair import train_repair_model  # noqa: E402


TRAINING_COUNT = 10
DAMAGE_RNG_SEED = 20260512


class RepairScale16Tests(unittest.TestCase):
    seeds_16: list[dict]
    lab_model: dict
    package_model: dict

    @classmethod
    def setUpClass(cls):
        cls.seeds_16 = build_seed_grids_16()
        training = cls.seeds_16[:TRAINING_COUNT]
        cls.lab_model = train_neighborhood_repair_model(training)
        cls.package_model = train_repair_model(training)

    def test_models_record_their_training_scale_in_parity(self):
        self.assertEqual(16, self.package_model["width"])
        self.assertEqual(16, self.package_model["height"])
        self.assertEqual(sorted(self.lab_model), sorted(self.package_model))
        for key in sorted(self.lab_model):
            with self.subTest(field=key):
                self.assertEqual(self.lab_model[key], self.package_model[key])

    def test_wound_repair_refills_sites_beyond_the_8x8_quadrant(self):
        # The old layout silently never touched x,y >= 8; the turtle's
        # shell spans rows 11+ and columns 12+, so its wound sites land
        # outside the historical quadrant.
        target = next(
            grid
            for grid in self.seeds_16[TRAINING_COUNT:]
            if grid["grid_id"].endswith("hornbeetle")
        )
        damaged = apply_stochastic_damage(
            target, dropout_rate=0.2, rng_seed=DAMAGE_RNG_SEED, event_index=1
        )
        removed = damaged["metadata"]["removed_cells"]
        self.assertTrue(
            any(x >= 8 or y >= 8 for x, y in removed),
            "damage must hit cells beyond the 8x8 quadrant for this pin",
        )
        lab_repaired = repair_with_wound_sites(damaged, self.lab_model)
        package_repaired = package_repair_wound_sites(
            damaged, self.package_model
        )
        self.assertEqual(lab_repaired["cells"], package_repaired["cells"])
        self.assertEqual(
            lab_repaired["metadata"], package_repaired["metadata"]
        )
        refilled = {
            (cell["x"], cell["y"]) for cell in package_repaired["cells"]
        }
        for x, y in removed:
            with self.subTest(site=(x, y)):
                self.assertIn((x, y), refilled)

    def test_guarded_wound_repair_stays_valid_over_heldout_16x16(self):
        # The A3 stability re-gate at scale: guarded wound repair over
        # every held-out 16x16 seed returns a validator-clean creature.
        for index, target in enumerate(self.seeds_16[TRAINING_COUNT:]):
            damaged = apply_stochastic_damage(
                target,
                dropout_rate=0.2,
                rng_seed=DAMAGE_RNG_SEED + index * 1000 + 1,
                event_index=1,
            )
            with self.subTest(target=target["grid_id"]):
                repaired = package_repair_wound_sites(
                    damaged, self.package_model
                )
                result = validate_grid(repaired)
                self.assertTrue(result.ok, result.errors)
                self.assertEqual([16, 16], repaired["grid_size"])

    def test_scale_mismatch_between_model_and_grid_fails_loudly(self):
        seed_8 = build_seed_grids()[0]
        damaged_8 = apply_stochastic_damage(
            seed_8, dropout_rate=0.2, rng_seed=DAMAGE_RNG_SEED, event_index=1
        )
        with self.assertRaises(ValueError) as context:
            package_repair_wound_sites(damaged_8, self.package_model)
        self.assertIn("trained at 16x16", str(context.exception))
        with self.assertRaises(ValueError):
            repair_with_wound_sites(damaged_8, self.lab_model)

    def test_mixed_size_training_corpus_fails_loudly(self):
        mixed = [build_seed_grids()[0], self.seeds_16[0]]
        with self.assertRaises(ValueError):
            train_repair_model(mixed)
        with self.assertRaises(ValueError):
            train_neighborhood_repair_model(mixed)


if __name__ == "__main__":
    unittest.main()
