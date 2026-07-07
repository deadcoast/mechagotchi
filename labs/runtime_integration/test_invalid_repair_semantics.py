"""Parity + crash pin: aligned-but-invalid repairs must not break evolve.

Found during G2 (the game-loop session runner, 2026-07-07): under damage
heavy enough that wound-site repair returns a grid that is SLIP-ALIGNED
yet LIFECYCLE-INVALID ("required body core is disconnected"), the
promoted ``runtime.live_cycle`` ran the episode anyway and raised, while
the LAB loop had gated episodes on ``valid and aligned`` since T1
(commit d382805) — scoring on ``all_valid and all_aligned`` with the
``skipped_invalid`` decision. A silent promotion drift: the frozen
parity pins never hit an invalid repair, so no gate caught it.

These tests pin the synced semantics at a configuration measured to
produce an invalid repair (probe 2026-07-07: rng_seed 20260700,
dropout 0.95, 4 cycles): the package completes, invalid cycles carry no
episode, aligned-but-invalid creatures record ``skipped_invalid``, and
the lab and package reports agree record-for-record.
"""

import sys
import unittest
from pathlib import Path

LAB_DIR = Path(__file__).resolve().parent
REPO_ROOT = LAB_DIR.parents[1]
GRID_GENOME = REPO_ROOT / "labs" / "grid_genome"
READABILITY = REPO_ROOT / "labs" / "readability_benchmark"
PACKAGE_SRC = REPO_ROOT / "packages" / "mecha_engine" / "src"
for path in [LAB_DIR, GRID_GENOME, READABILITY]:
    if str(path) not in sys.path:
        sys.path.insert(0, str(path))
if str(PACKAGE_SRC) not in sys.path:
    sys.path.insert(0, str(PACKAGE_SRC))

import json  # noqa: E402

from corpus_builder import build_seed_grids  # noqa: E402
from readability_benchmark import score_readability  # noqa: E402

from mecha_engine_runtime_loop import (  # noqa: E402
    run_mecha_engine_evolution_loop,
)

from mecha_engine.generation import train_generation_model  # noqa: E402
from mecha_engine.repair import train_repair_model  # noqa: E402
from mecha_engine.runtime import evolve  # noqa: E402

# The measured boundary configuration: heavy enough that at least one
# repair comes back aligned-but-invalid (probe 2026-07-07: 8 of 60
# scanned seeds hit the boundary at this configuration).
BOUNDARY_SEED = 20260703
BOUNDARY_KW = dict(
    generations=2,
    population=2,
    damage_cycles=4,
    ticks=8,
    rng_seed=BOUNDARY_SEED,
)
BOUNDARY_DROPOUT = 0.95
REPAIR_EPOCHS = 20
REPAIR_TRAINING_COUNT = 40  # the lab loop's fixed training split


class InvalidRepairSemanticsTests(unittest.TestCase):
    seeds: list[dict]

    @classmethod
    def setUpClass(cls):
        cls.seeds = build_seed_grids()
        cls.generation_model = train_generation_model(cls.seeds)
        cls.repair_model = train_repair_model(
            cls.seeds[:REPAIR_TRAINING_COUNT],
            epochs=REPAIR_EPOCHS,
            rng_seed=BOUNDARY_SEED,
        )
        cls.slip_profile = json.loads(
            (
                REPO_ROOT / "data" / "slips" / "valid" / "slip_lcd_seed.json"
            ).read_text(encoding="utf-8")
        )

    def _package_report(self) -> dict:
        _, report = evolve(
            self.seeds,
            self.slip_profile,
            self.generation_model,
            self.repair_model,
            readability_scorer=score_readability,
            dropout_rate=BOUNDARY_DROPOUT,
            **BOUNDARY_KW,
        )
        return report

    def test_package_evolve_survives_aligned_but_invalid_repairs(self):
        report = self._package_report()
        creatures = [
            creature
            for generation in report["generations"]
            for creature in generation["creatures"]
        ]
        # The premise: this configuration actually produces an invalid
        # repair — otherwise the pin is vacuous.
        self.assertTrue(
            any(not c["stages"]["all_cycles_valid"] for c in creatures)
        )

    def test_invalid_cycles_carry_no_episode(self):
        report = self._package_report()
        for generation in report["generations"]:
            for creature in generation["creatures"]:
                for cycle in creature["cycles"]:
                    if not cycle["valid"]:
                        self.assertIsNone(cycle["episode"])

    def test_aligned_but_invalid_creatures_record_skipped_invalid(self):
        report = self._package_report()
        seen = False
        for generation in report["generations"]:
            for creature in generation["creatures"]:
                stages = creature["stages"]
                if stages["all_cycles_aligned"] and not stages[
                    "all_cycles_valid"
                ]:
                    seen = True
                    self.assertEqual(
                        "skipped_invalid", creature["archive_decision"]
                    )
                    self.assertIsNone(creature["score"])
                    self.assertFalse(stages["scored"])
        self.assertTrue(seen)

    def test_lab_and_package_agree_at_the_boundary(self):
        lab_report = run_mecha_engine_evolution_loop(
            dropout_rate=BOUNDARY_DROPOUT,
            repair_epochs=REPAIR_EPOCHS,
            **BOUNDARY_KW,
        )
        package_report = self._package_report()
        self.assertEqual(
            lab_report["generations"], package_report["generations"]
        )
        self.assertEqual(lab_report["summary"], package_report["summary"])


if __name__ == "__main__":
    unittest.main()
