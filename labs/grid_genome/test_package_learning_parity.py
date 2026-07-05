"""Parity pin: lab switchboard learning surface vs promoted mecha_engine.learning.

Runs the Stage 0 lab surfaces (``micro_switchboard.run_switchboard``, the
``switchboard_feedback`` episode loop behind
``data/micro_learners/switchboard_lifecycle_feedback_stage0.json``, and the
stress benchmark's ``_policy_episode`` behind
``data/runtime_integration/stress_learning_benchmark_stage0.json``) and the
promoted package surface (``mecha_engine.learning`` through the package src
layout) over the same seed grid, SLIP profile, stress-probed candidates,
and tick horizons, and asserts identical results.

Documented equivalence scope:

- ``decide`` is a verbatim port of the lab ``run_switchboard`` — identical
  thread math, additive utilities with the 0.05 idle prior, tie-break
  ordering, rounding, and decision dict (action, confidence, utilities,
  threads, explanation) — pinned here for every state visited during a
  full 48-tick lab feedback episode, both arms.
- ``run_feedback_episode`` ports the lab episode mechanics without the
  scenario/event machinery (lab-only per the interface spec's non-goals).
  Included fields, compared for full equality on both arms: ``policy``,
  ``ticks_requested``, ``episode_deterministic``, ``survival_ticks``,
  ``alive``, ``death_cause``, ``need_balance``, ``recovery_events``,
  ``action_counts``, ``reward_update_count``,
  ``initial_action_reward_means``, ``final_action_reward_means``, and the
  full per-tick ``history`` (the shapes match, so history is included).
  Excluded lab fields, by design: ``scenario_id`` and ``events_applied``
  (scenario machinery stays lab-only) and ``rng_seed`` (recorded by the
  lab for interface parity only — no code path consumes it, and the
  package signature deliberately has no seed parameter). The sheltered
  need-balance delta is pinned to the artifact value +0.03964.
- The stress pins reuse the stress benchmark's exact arm mechanics
  (``_policy_episode``) and generation setup (``generate_candidate`` over
  the aligned seed pool, ``_stress_probe``): for three stress-probed
  generated candidates, the package episode must equal the lab episode
  field-by-field on the shared fields (``survival_ticks``, ``alive``,
  ``death_cause``, ``need_balance``, ``recovery_events``,
  ``reward_update_count``). Excluded: ``survival_ratio``, a lab-only
  derived convenience (survival_ticks / ticks) not part of the package
  episode shape.

These are wellbeing pins per decision record 0009's bounded claim: no
assertion here is a survival-improvement claim (survival is
morphology-decided; the sheltered arms tie at 48 ticks).

Direction note: labs may import the package for regression evidence; the
reverse (package importing labs) stays forbidden by the learning interface
spec and decision record 0009, and this file lives on the lab side
precisely so the package tree keeps zero lab references.
"""

import json
import sys
import unittest
from copy import deepcopy
from pathlib import Path


LAB_DIR = Path(__file__).resolve().parent
REPO_ROOT = LAB_DIR.parents[1]
LIFECYCLE = REPO_ROOT / "labs" / "lifecycle_sim"
RUNTIME_INTEGRATION = REPO_ROOT / "labs" / "runtime_integration"
PACKAGE_SRC = REPO_ROOT / "packages" / "mecha_engine" / "src"
for path in [LAB_DIR, LIFECYCLE, RUNTIME_INTEGRATION]:
    if str(path) not in sys.path:
        sys.path.insert(0, str(path))
if str(PACKAGE_SRC) not in sys.path:
    sys.path.insert(0, str(PACKAGE_SRC))

from corpus_builder import build_seed_grids  # noqa: E402
from lifecycle_sim import (  # noqa: E402
    advance_tick as lab_advance_tick,
    initial_lifecycle_state,
)
from micro_switchboard import ACTIONS as LAB_ACTIONS, run_switchboard  # noqa: E402
from slip import is_grid_aligned  # noqa: E402
from switchboard_feedback import (  # noqa: E402
    _miscalibrate_rewards,
    run_feedback_episode as lab_run_feedback_episode,
)

from mecha_engine_runtime_loop import _stress_probe  # noqa: E402
from stress_learning_benchmark import _policy_episode  # noqa: E402

from mecha_engine.generation import (  # noqa: E402
    generate_candidate,
    train_generation_model,
)
from mecha_engine.learning import (  # noqa: E402
    ACTIONS as PACKAGE_ACTIONS,
    decide,
    run_feedback_episode as package_run_feedback_episode,
)


PARITY_TICKS = 48
STRESS_TICKS = 72
STRESS_CANDIDATE_COUNT = 3
STRESS_RNG_SEED = 20260512  # the stress benchmark's per-candidate seed base
# The sheltered measurement's artifact pin
# (data/micro_learners/switchboard_lifecycle_feedback_stage0.json summary).
SHELTERED_NEED_BALANCE_DELTA = 0.03964

SHARED_EPISODE_FIELDS = [
    "policy",
    "ticks_requested",
    "episode_deterministic",
    "survival_ticks",
    "alive",
    "death_cause",
    "need_balance",
    "recovery_events",
    "action_counts",
    "reward_update_count",
    "initial_action_reward_means",
    "final_action_reward_means",
    "history",
]
LAB_ONLY_EPISODE_FIELDS = ["rng_seed", "scenario_id", "events_applied"]
SHARED_STRESS_FIELDS = [
    "survival_ticks",
    "alive",
    "death_cause",
    "need_balance",
    "recovery_events",
    "reward_update_count",
]


def load_lcd_slip() -> dict:
    return json.loads(
        (REPO_ROOT / "data" / "slips" / "valid" / "slip_lcd_seed.json").read_text(
            encoding="utf-8"
        )
    )


class PackageLearningParityTests(unittest.TestCase):
    seed_grid: dict
    slip_profile: dict

    @classmethod
    def setUpClass(cls):
        cls.slip_profile = load_lcd_slip()
        # The lab episode builds its subject internally from the corpus
        # builder's first seed; the package episode receives the same grid
        # explicitly (frozen as data/seed_grids/mg_seed_001.json).
        cls.seed_grid = build_seed_grids()[0]

    def test_actions_pin(self):
        self.assertEqual(LAB_ACTIONS, PACKAGE_ACTIONS)

    # -- (a) decide parity over a full episode trajectory ---------------------

    def test_decide_matches_lab_switchboard_over_episode_trajectory(self):
        # Replay the exact state trajectory of a full lab feedback episode
        # (both arms) and pin the package decision equal to the lab decision
        # at every visited state. Trajectory fidelity is proven by matching
        # each replayed action against the lab episode's recorded history.
        for feedback_enabled in (True, False):
            with self.subTest(feedback_enabled=feedback_enabled):
                lab_episode = lab_run_feedback_episode(
                    ticks=PARITY_TICKS, feedback_enabled=feedback_enabled
                )
                recorded_actions = [
                    entry["action"] for entry in lab_episode["history"]
                ]
                state = initial_lifecycle_state(self.seed_grid, self.slip_profile)
                state = _miscalibrate_rewards(state)
                initial_rewards = deepcopy(state["action_rewards"])
                visited = 0
                for recorded_action in recorded_actions:
                    lab_decision = run_switchboard(state)
                    self.assertEqual(lab_decision, decide(state))
                    self.assertEqual(recorded_action, lab_decision["action"])
                    next_state = lab_advance_tick(state, recorded_action)
                    if not feedback_enabled:
                        next_state["action_rewards"] = deepcopy(initial_rewards)
                    state = next_state
                    visited += 1
                self.assertEqual(PARITY_TICKS, visited)

    # -- (b) episode parity on the sheltered seed grid -------------------------

    def test_episode_parity_both_arms_on_the_seed_grid(self):
        for feedback_enabled in (True, False):
            with self.subTest(feedback_enabled=feedback_enabled):
                lab_episode = lab_run_feedback_episode(
                    ticks=PARITY_TICKS, feedback_enabled=feedback_enabled
                )
                package_episode = package_run_feedback_episode(
                    self.seed_grid,
                    self.slip_profile,
                    ticks=PARITY_TICKS,
                    feedback_enabled=feedback_enabled,
                )
                # The package episode is exactly the shared shape; the lab
                # carries only its documented lab-only extras.
                self.assertEqual(
                    sorted(SHARED_EPISODE_FIELDS), sorted(package_episode)
                )
                self.assertEqual(
                    sorted(SHARED_EPISODE_FIELDS + LAB_ONLY_EPISODE_FIELDS),
                    sorted(lab_episode),
                )
                for field in SHARED_EPISODE_FIELDS:
                    with self.subTest(field=field):
                        self.assertEqual(
                            lab_episode[field], package_episode[field]
                        )

    def test_sheltered_need_balance_delta_matches_the_artifact_pin(self):
        # A wellbeing pin, never a survival claim: both arms survive all 48
        # ticks (decision record 0009's bounded claim).
        feedback = package_run_feedback_episode(
            self.seed_grid, self.slip_profile, ticks=PARITY_TICKS
        )
        frozen = package_run_feedback_episode(
            self.seed_grid,
            self.slip_profile,
            ticks=PARITY_TICKS,
            feedback_enabled=False,
        )
        self.assertEqual(
            SHELTERED_NEED_BALANCE_DELTA,
            round(feedback["need_balance"] - frozen["need_balance"], 6),
        )
        self.assertEqual(feedback["survival_ticks"], frozen["survival_ticks"])

    # -- (c) stress pins over stress-probed generated candidates ----------------

    def test_stress_pins_match_the_benchmark_policy_episode_both_arms(self):
        # The stress benchmark's exact generation setup: candidates from the
        # aligned seed pool via the package generation model, probed by the
        # archive's contracted morphology stress probe.
        seeds = build_seed_grids()
        generation_model = train_generation_model(seeds)
        pool = [
            seed for seed in seeds if is_grid_aligned(seed, self.slip_profile).ok
        ]
        self.assertGreater(len(pool), 0)
        for index in range(STRESS_CANDIDATE_COUNT):
            candidate = generate_candidate(
                pool[index % len(pool)],
                generation_model,
                self.slip_profile,
                rng_seed=STRESS_RNG_SEED + index,
            )
            probed, load = _stress_probe(candidate)
            for feedback_enabled in (True, False):
                with self.subTest(
                    candidate=candidate["grid_id"],
                    stress_load=load,
                    feedback_enabled=feedback_enabled,
                ):
                    lab_episode = _policy_episode(
                        probed,
                        self.slip_profile,
                        ticks=STRESS_TICKS,
                        feedback_enabled=feedback_enabled,
                    )
                    package_episode = package_run_feedback_episode(
                        probed,
                        self.slip_profile,
                        ticks=STRESS_TICKS,
                        feedback_enabled=feedback_enabled,
                    )
                    for field in SHARED_STRESS_FIELDS:
                        with self.subTest(field=field):
                            self.assertEqual(
                                lab_episode[field], package_episode[field]
                            )


if __name__ == "__main__":
    unittest.main()
