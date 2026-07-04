"""Parity pin: lab lifecycle simulator vs promoted mecha_engine.lifecycle.

Runs the Stage 0 lab simulator (flat import, the authoritative research
behavior, including the pinned survival_ticks death-tick arithmetic) and
the promoted package simulator (mecha_engine.lifecycle through the package
src layout) over the same grid, SLIP profile, policies, tick horizons, and
RNG seeds, and asserts byte-identical results.

Documented equivalence scope: the package surface maps onto the lab entry
points exactly — ``initial_state`` onto ``initial_lifecycle_state`` and
``run_episode(grid, slip_profile, policy=..., ticks=..., rng_seed=...)``
onto ``run_lifecycle_simulation(grid, slip_profile, ticks=..., policy=...,
rng_seed=...)`` — with identical state keys, need decay, action effects,
recovery counting, death causes, RNG consumption (only the ``random``
policy draws), and episode report shape, so the full dictionaries are
compared for equality with no excluded keys. The package additionally
accepts explicit action streams and defaults ``rng_seed=None`` to the
pinned Stage 0 seed 20260512 (the lab default); both are asserted here.

Direction note: labs may import the package for regression evidence; the
reverse (package importing labs) stays forbidden by the lifecycle contract
gate, and this file lives on the lab side precisely so the package tree
keeps zero lab references.
"""

import json
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

from corpus_builder import build_seed_grids  # noqa: E402
from lifecycle_sim import (  # noqa: E402
    advance_tick as lab_advance_tick,
    initial_lifecycle_state,
    run_lifecycle_simulation,
)

from mecha_engine.lifecycle import (  # noqa: E402
    advance_tick as package_advance_tick,
    initial_state,
    run_episode,
)


POLICIES = ["switchboard", "idle", "random"]


def load_lcd_slip() -> dict:
    return json.loads(
        (REPO_ROOT / "data" / "slips" / "valid" / "slip_lcd_seed.json").read_text(
            encoding="utf-8"
        )
    )


class PackageLifecycleParityTests(unittest.TestCase):
    def test_initial_state_parity_with_and_without_slip(self):
        grid = build_seed_grids()[0]
        slip = load_lcd_slip()

        self.assertEqual(initial_lifecycle_state(grid, slip), initial_state(grid, slip))
        self.assertEqual(initial_lifecycle_state(grid), initial_state(grid))

    def test_single_transition_parity_for_every_action(self):
        grid = build_seed_grids()[0]
        slip = load_lcd_slip()
        for action in ["feed", "sleep", "play", "idle", "mutate"]:
            with self.subTest(action=action):
                lab_state = lab_advance_tick(initial_lifecycle_state(grid, slip), action)
                package_state = package_advance_tick(initial_state(grid, slip), action)
                self.assertEqual(lab_state, package_state)

    def test_stage0_comparator_episode_parity_72_ticks(self):
        grid = build_seed_grids()[0]
        slip = load_lcd_slip()
        for policy in POLICIES:
            with self.subTest(policy=policy):
                lab_result = run_lifecycle_simulation(
                    grid, slip, ticks=72, policy=policy, rng_seed=20260512
                )
                package_result = run_episode(
                    grid, slip, policy=policy, ticks=72, rng_seed=20260512
                )
                self.assertEqual(lab_result, package_result)

    def test_episode_parity_across_horizons_seeds_and_grids(self):
        seeds_grids = build_seed_grids()
        slip = load_lcd_slip()
        second_aligned_grid = next(
            grid
            for grid in seeds_grids[1:]
            if grid["palette"]["palette_id"] in slip["grid"]["allowed_palettes"]
        )
        cases = [
            (seeds_grids[0], 48, 7, "switchboard"),
            (seeds_grids[0], 96, 777, "random"),
            (seeds_grids[0], 200, 20260512, "idle"),
            (second_aligned_grid, 72, 20260512, "switchboard"),
        ]
        for grid, ticks, rng_seed, policy in cases:
            with self.subTest(grid_id=grid["grid_id"], ticks=ticks, seed=rng_seed, policy=policy):
                lab_result = run_lifecycle_simulation(
                    grid, slip, ticks=ticks, policy=policy, rng_seed=rng_seed
                )
                package_result = run_episode(
                    grid, slip, policy=policy, ticks=ticks, rng_seed=rng_seed
                )
                self.assertEqual(lab_result, package_result)

    def test_episode_parity_without_slip_profile(self):
        grid = build_seed_grids()[0]
        lab_result = run_lifecycle_simulation(
            grid, None, ticks=48, policy="switchboard", rng_seed=20260512
        )
        package_result = run_episode(
            grid, policy="switchboard", ticks=48, rng_seed=20260512
        )
        self.assertEqual(lab_result, package_result)

    def test_package_default_seed_matches_lab_default_seed(self):
        # Package rng_seed=None resolves to the pinned Stage 0 seed
        # 20260512, which is the lab's documented default.
        grid = build_seed_grids()[0]
        slip = load_lcd_slip()
        lab_result = run_lifecycle_simulation(grid, slip, ticks=36, policy="random")
        package_result = run_episode(grid, slip, policy="random", ticks=36)
        self.assertEqual(lab_result, package_result)

    def test_survival_ticks_death_tick_semantics_parity(self):
        # The pinned lab arithmetic (death tick is counted) must hold
        # identically through the package surface.
        grid = build_seed_grids()[0]
        slip = load_lcd_slip()
        lab_result = run_lifecycle_simulation(
            grid, slip, ticks=200, policy="idle", rng_seed=20260512
        )
        package_result = run_episode(
            grid, slip, policy="idle", ticks=200, rng_seed=20260512
        )
        self.assertEqual(lab_result, package_result)
        self.assertFalse(package_result["alive"])
        death_entry = next(
            entry for entry in package_result["history"] if not entry["alive"]
        )
        self.assertEqual(death_entry["tick"], package_result["survival_ticks"])
        self.assertEqual(len(package_result["history"]), package_result["survival_ticks"])


if __name__ == "__main__":
    unittest.main()
