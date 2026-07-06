"""Parity pin: lab animation states vs the mecha_engine.genome v2 publics.

Runs the Stage 0 lab surfaces (``animation_states.project_animation_state``,
``select_animation_state``, and ``build_render_packet_v2`` — the T4/T16
authorities behind ``data/grid_genome/animation_states_stage0.json``) and
the promoted package surfaces (``mecha_engine.genome.ANIMATION_STATES``,
``project_animation_state``, ``render_packet_v2`` through the package src
layout, per decision record 0013) over the same grids, states, and
lifecycle snapshots, and asserts identical results.

Documented equivalence scope: the package functions are verbatim ports —
identical vocabulary and order, identical projection semantics (idle is
the identity; blink/sleep/beg/ill derive from palette + role only),
identical selection thresholds (mirroring the mood estimator: energy 0.2 /
hunger 0.65 / stress 0.65; blink every fifth tick in the curious band),
and the identical packet contract (the lab builder already wraps
``mecha_engine.genome.render_packet_from_grid``, so full packet equality
pins the projection, the selection, and the three v2 keys together). All
five states are pinned across several seed grids (the deliverable's
"all 5 states x several seeds").

Direction note: labs may import the package for regression evidence; the
reverse (package importing labs) stays forbidden by the genome contract
gate, and this file lives on the lab side precisely so the package tree
keeps zero lab references.
"""

import sys
import unittest
from pathlib import Path


LAB_DIR = Path(__file__).resolve().parent
REPO_ROOT = LAB_DIR.parents[1]
PACKAGE_SRC = REPO_ROOT / "packages" / "mecha_engine" / "src"
if str(LAB_DIR) not in sys.path:
    sys.path.insert(0, str(LAB_DIR))
if str(PACKAGE_SRC) not in sys.path:
    sys.path.insert(0, str(PACKAGE_SRC))

from animation_states import (  # noqa: E402
    ANIMATION_STATES as LAB_ANIMATION_STATES,
    build_render_packet_v2,
    project_animation_state as lab_project,
    select_animation_state as lab_select,
)
from corpus_builder import build_seed_grids  # noqa: E402

from mecha_engine.genome import (  # noqa: E402
    ANIMATION_STATES as PACKAGE_ANIMATION_STATES,
    project_animation_state as package_project,
    render_packet_v2,
)
from mecha_engine.genome.animation import (  # noqa: E402
    select_animation_state as package_select,
)


PARITY_SEED_COUNT = 8
LIFECYCLE_SNAPSHOTS = [
    {"alive": True, "energy": 0.1, "hunger": 0.3, "stress": 0.2, "age_ticks": 1},
    {"alive": True, "energy": 0.6, "hunger": 0.8, "stress": 0.2, "age_ticks": 1},
    {"alive": True, "energy": 0.6, "hunger": 0.3, "stress": 0.8, "age_ticks": 1},
    {"alive": True, "energy": 0.6, "hunger": 0.3, "stress": 0.2, "age_ticks": 5},
    {"alive": True, "energy": 0.6, "hunger": 0.3, "stress": 0.2, "age_ticks": 3},
    {"alive": True, "energy": 0.19, "hunger": 0.66, "stress": 0.66, "age_ticks": 10},
    {},
]


class AnimationVocabularyParityTests(unittest.TestCase):
    def test_vocabulary_pin(self):
        self.assertEqual(LAB_ANIMATION_STATES, PACKAGE_ANIMATION_STATES)
        self.assertEqual(
            ["idle", "blink", "sleep", "beg", "ill"], PACKAGE_ANIMATION_STATES
        )


class ProjectionParityTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.grids = build_seed_grids()[:PARITY_SEED_COUNT]

    def test_all_five_states_project_identically_across_seeds(self):
        for grid in self.grids:
            for state in LAB_ANIMATION_STATES:
                with self.subTest(grid=grid["grid_id"], state=state):
                    self.assertEqual(
                        lab_project(grid, state), package_project(grid, state)
                    )

    def test_idle_is_the_identity_on_both_sides(self):
        grid = self.grids[0]
        self.assertEqual(grid, lab_project(grid, "idle"))
        self.assertEqual(grid, package_project(grid, "idle"))

    def test_unknown_state_fails_loudly_with_the_same_error(self):
        grid = self.grids[0]
        with self.assertRaises(ValueError) as lab_raised:
            lab_project(grid, "dance")
        with self.assertRaises(ValueError) as package_raised:
            package_project(grid, "dance")
        self.assertEqual(str(lab_raised.exception), str(package_raised.exception))


class SelectionParityTests(unittest.TestCase):
    def test_selection_matches_over_the_threshold_snapshots(self):
        for snapshot in LIFECYCLE_SNAPSHOTS:
            with self.subTest(snapshot=snapshot):
                self.assertEqual(
                    lab_select(snapshot), package_select(snapshot)
                )


class RenderPacketV2ParityTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.grids = build_seed_grids()[:PARITY_SEED_COUNT]

    def test_packets_identical_across_seeds_and_lifecycle_snapshots(self):
        for grid in self.grids:
            for snapshot in LIFECYCLE_SNAPSHOTS:
                with self.subTest(grid=grid["grid_id"], snapshot=snapshot):
                    self.assertEqual(
                        build_render_packet_v2(grid, snapshot),
                        render_packet_v2(grid, snapshot),
                    )

    def test_packets_identical_without_lifecycle_state(self):
        for grid in self.grids:
            with self.subTest(grid=grid["grid_id"]):
                self.assertEqual(
                    build_render_packet_v2(grid), render_packet_v2(grid)
                )

    def test_explicit_override_packets_identical_for_every_state(self):
        grid = self.grids[0]
        tired = LIFECYCLE_SNAPSHOTS[0]
        for state in LAB_ANIMATION_STATES:
            with self.subTest(state=state):
                self.assertEqual(
                    build_render_packet_v2(grid, tired, animation=state),
                    render_packet_v2(grid, tired, animation=state),
                )
                self.assertEqual(
                    build_render_packet_v2(grid, None, animation=state),
                    render_packet_v2(grid, None, animation=state),
                )


if __name__ == "__main__":
    unittest.main()
