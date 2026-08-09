"""The cleanliness mechanic seam (cycle 26 P3, DR 0059).

`validity-research.md` §1.17 names `cleanliness` a VISIBLE companion
state axis; M5 measured that nothing in the engine accumulates dirt and
no action answers it, and DR 0048 recorded the gap as needing a
MECHANIC with its own record. This seam is that mechanic, OPT-IN and
**byte-identical when off — proven against the committed Stage 0
artifact's own numbers, not against a second call to the new code**
(the cycle-23 M3 lesson: pin off-mode against frozen literals).

The seam's parameters are DERIVED from the incumbent engine, never
picked: the per-tick decay is the median incumbent drift magnitude at
the Stage 0 default weights; `mutate`'s extra mess is exactly the
grid-stability cost the action already charges; `clean` restores by the
incumbent table's strongest care effect (feed's hunger relief); the
dirt→stress coupling reuses the engine's own hunger→stress coefficient
verbatim. The mechanic is NON-LETHAL (`_life_status` untouched) and the
autonomous policies never choose `clean` — the companion cannot clean
itself, the same documented interaction model that keeps feeding
keeper-mediated.

Import mechanics match the other contract tests: one ``python -B``
subprocess whose PYTHONPATH points at this package's own ``src``.
"""

import json
import os
import subprocess
import sys
import unittest
from pathlib import Path

PACKAGE_ROOT = Path(__file__).resolve().parents[1]
REPO_ROOT = PACKAGE_ROOT.parents[1]
SRC_DIR = PACKAGE_ROOT / "src"
PROBE_TIMEOUT_S = 240

# The off-mode state key set, FROZEN (the committed M5 survey's
# lifecycle_state_keys). A key both modes gained would slip past a
# new-vs-new comparison; it cannot slip past this list.
FROZEN_OFF_MODE_KEYS = [
    "action_counts",
    "action_rewards",
    "age_ticks",
    "alive",
    "body_mass",
    "bond",
    "curiosity",
    "death_cause",
    "energy",
    "grid_id",
    "grid_stability",
    "history",
    "hunger",
    "neediness",
    "recent_interactions",
    "recovery_events",
    "sleepiness",
    "slip_profile_id",
    "stress",
]

# The committed Stage 0 comparator episode (data/lifecycle/
# lifecycle_stage0.json, switchboard arm) — what the surface returned
# BEFORE the seam existed. Off-mode must reproduce it verbatim.
COMMITTED_SWITCHBOARD = {
    "survival_ticks": 72,
    "alive": True,
    "death_cause": None,
    "need_balance": 0.789129,
    "recovery_events": 14,
    "action_counts": {"feed": 14, "play": 44, "sleep": 14, "idle": 0, "mutate": 0},
    "final_state": {
        "hunger": 0.6004,
        "energy": 0.484,
        "stress": 0.0,
        "bond": 0.993,
        "grid_stability": 1.0,
    },
}
COMMITTED_IDLE = {
    "survival_ticks": 11,
    "alive": False,
    "death_cause": "starvation",
    "need_balance": 0.121004,
}

# The derived parameters, pinned BY VALUE (a mechanic whose numbers can
# drift is not a contract): median incumbent drift magnitude at the
# Stage 0 defaults; mutate's own grid-stability cost; feed's own hunger
# relief; the engine's own hunger→stress coefficient.
DERIVED_DECAY = 0.0124
DERIVED_MUTATE_MESS = 0.055
DERIVED_CLEAN_RESTORE = 0.32
DERIVED_STRESS_COEFFICIENT = 0.01

_PROBE = r"""
import json, sys
from mecha_engine.lifecycle import ACTIONS, advance_tick, initial_state, run_episode

grid = json.loads(open(sys.argv[1], encoding="utf-8").read())
slip = json.loads(open(sys.argv[2], encoding="utf-8").read())
out = {}

# Off mode: the incumbent surface, untouched.
off = initial_state(grid, slip)
out["off_keys"] = sorted(off)
episode = run_episode(grid, slip, policy="switchboard")
out["off_switchboard"] = {
    key: episode[key]
    for key in (
        "survival_ticks", "alive", "death_cause", "need_balance",
        "recovery_events", "action_counts", "final_state",
    )
}
idle_episode = run_episode(grid, slip, policy="idle")
out["off_idle"] = {
    key: idle_episode[key]
    for key in ("survival_ticks", "alive", "death_cause", "need_balance")
}
try:
    advance_tick(off, "clean")
    out["clean_off_error"] = None
except ValueError as error:
    out["clean_off_error"] = str(error)
try:
    initial_state(grid, slip, mechanics=("nonsense",))
    out["unknown_mechanic_error"] = None
except ValueError as error:
    out["unknown_mechanic_error"] = str(error)

# On mode.
on = initial_state(grid, slip, mechanics=("cleanliness",))
out["on_keys"] = sorted(on)
out["on_seed"] = on["cleanliness"]

after_idle = advance_tick(on, "idle")
after_mutate = advance_tick(on, "mutate")
out["after_one_idle"] = after_idle["cleanliness"]
out["after_one_mutate"] = after_mutate["cleanliness"]

# A clean tick vs an idle tick from the SAME state: clean's only
# incumbent-axis load is the shared drift, so per axis
# clean_after == idle_after - IDLE_EFFECTS.
AXES = ["hunger", "energy", "stress", "bond", "grid_stability"]
after_clean = advance_tick(on, "clean")
out["clean_vs_idle"] = {
    axis: [after_clean[axis], after_idle[axis]] for axis in AXES
}
out["clean_from_full"] = after_clean["cleanliness"]

# Dirty, then cleaned — on a LIVE companion (dirt accumulates under any
# action but clean, so a cared-for life still gets dirty).
dirty = on
care = ["feed", "play", "sleep"]
for step in range(30):
    dirty = advance_tick(dirty, care[step % 3])
cleaned = advance_tick(dirty, "clean")
out["dirty_alive"] = dirty["alive"]
out["dirty_after_30_care"] = dirty["cleanliness"]
out["cleaned_value"] = cleaned["cleanliness"]

# You cannot clean a corpse: dead states return unchanged, clean included.
corpse = on
for _ in range(30):
    corpse = advance_tick(corpse, "idle")
out["corpse_alive"] = corpse["alive"]
out["corpse_cleanliness"] = corpse["cleanliness"]
out["corpse_after_clean"] = advance_tick(corpse, "clean")["cleanliness"]

# The coupling and non-lethality: the neglect stream on vs off.
off_run = run_episode(grid, slip, actions=["idle"] * 72, ticks=72)
on_run = run_episode(
    grid, slip, actions=["idle"] * 72, ticks=72, mechanics=("cleanliness",)
)
out["neglect_off"] = {
    "survival_ticks": off_run["survival_ticks"],
    "death_cause": off_run["death_cause"],
    "final_stress": off_run["final_state"]["stress"],
}
out["neglect_on"] = {
    "survival_ticks": on_run["survival_ticks"],
    "death_cause": on_run["death_cause"],
    "final_stress": on_run["final_state"]["stress"],
}

# Non-lethal at the floor: a filthy but otherwise healthy companion lives.
filthy = dict(on)
filthy["cleanliness"] = 0.0
out["filthy_alive"] = advance_tick(filthy, "idle")["alive"]

# The clean action in an explicit episode stream (on), rejected (off).
stream = ["feed", "clean", "sleep"] * 24
on_stream = run_episode(
    grid, slip, actions=stream, ticks=72, mechanics=("cleanliness",)
)
out["clean_stream_final_cleanliness"] = on_stream.get("final_cleanliness")
out["clean_stream_alive"] = on_stream["alive"]
try:
    run_episode(grid, slip, actions=stream, ticks=72)
    out["clean_stream_off_error"] = None
except ValueError as error:
    out["clean_stream_off_error"] = str(error)

# ACTIONS itself never changes: the autonomous vocabulary is untouched.
out["actions"] = list(ACTIONS)
print(json.dumps(out))
"""


def _probe_env() -> dict:
    env = os.environ.copy()
    existing = env.get("PYTHONPATH")
    env["PYTHONPATH"] = str(SRC_DIR) + (
        os.pathsep + existing if existing else ""
    )
    return env


class CleanlinessSeamTests(unittest.TestCase):
    probe: dict

    @classmethod
    def setUpClass(cls):
        grid = REPO_ROOT / "data" / "seed_grids" / "mg_seed_001.json"
        slip = REPO_ROOT / "data" / "slips" / "valid" / "slip_lcd_seed.json"
        result = subprocess.run(
            [sys.executable, "-B", "-c", _PROBE, str(grid), str(slip)],
            capture_output=True,
            text=True,
            env=_probe_env(),
            cwd=str(REPO_ROOT),
            timeout=PROBE_TIMEOUT_S,
        )
        if result.returncode != 0:
            raise AssertionError(
                f"cleanliness seam probe failed:\n{result.stderr}"
            )
        cls.probe = json.loads(result.stdout)

    # -- the seam law: byte-identical when off -------------------------

    def test_off_mode_state_keys_match_the_frozen_list(self):
        self.assertEqual(self.probe["off_keys"], FROZEN_OFF_MODE_KEYS)

    def test_off_mode_reproduces_the_committed_switchboard_episode(self):
        self.assertEqual(
            self.probe["off_switchboard"], COMMITTED_SWITCHBOARD
        )

    def test_off_mode_reproduces_the_committed_idle_episode(self):
        self.assertEqual(self.probe["off_idle"], COMMITTED_IDLE)

    def test_clean_off_mode_is_the_incumbent_error_verbatim(self):
        self.assertEqual(
            self.probe["clean_off_error"],
            "unsupported lifecycle action: clean",
        )

    def test_the_autonomous_action_vocabulary_is_untouched(self):
        self.assertEqual(
            self.probe["actions"], ["feed", "play", "sleep", "idle", "mutate"]
        )

    # -- the opt-in ----------------------------------------------------

    def test_an_unknown_mechanic_name_is_refused(self):
        self.assertIsNotNone(self.probe["unknown_mechanic_error"])
        self.assertIn("mechanic", self.probe["unknown_mechanic_error"])

    def test_on_mode_adds_exactly_the_cleanliness_key(self):
        self.assertEqual(
            self.probe["on_keys"],
            sorted(FROZEN_OFF_MODE_KEYS + ["cleanliness"]),
        )

    def test_a_fresh_companion_is_as_clean_as_its_body_is_undamaged(self):
        self.assertEqual(self.probe["on_seed"], 1.0)

    # -- the derived dynamics, pinned by value -------------------------

    def test_the_need_decays_by_the_derived_median_drift(self):
        self.assertEqual(
            self.probe["after_one_idle"], round(1.0 - DERIVED_DECAY, 6)
        )

    def test_mutate_is_messier_by_its_own_grid_cost(self):
        self.assertEqual(
            self.probe["after_one_mutate"],
            round(1.0 - DERIVED_DECAY - DERIVED_MUTATE_MESS, 6),
        )

    def test_clean_restores_by_the_incumbent_strongest_care_effect(self):
        self.assertTrue(self.probe["dirty_alive"])
        dirty = self.probe["dirty_after_30_care"]
        self.assertEqual(
            self.probe["cleaned_value"],
            round(
                min(1.0, dirty - DERIVED_DECAY + DERIVED_CLEAN_RESTORE), 6
            ),
        )

    def test_a_dead_companion_cannot_be_cleaned(self):
        # Dead states return unchanged — the incumbent rule, and clean
        # earns no exception to it.
        self.assertFalse(self.probe["corpse_alive"])
        self.assertEqual(
            self.probe["corpse_after_clean"],
            self.probe["corpse_cleanliness"],
        )

    def test_clean_costs_a_tick_and_nothing_else(self):
        # Per incumbent axis, clean_after == idle_after − idle's own
        # action effects: cleaning is time spent, not nourishment.
        idle_effects = {
            "hunger": 0.02,
            "energy": -0.012,
            "stress": 0.018,
            "bond": -0.012,
            "grid_stability": -0.002,
        }
        for axis, (clean_after, idle_after) in self.probe[
            "clean_vs_idle"
        ].items():
            self.assertEqual(
                round(clean_after, 6),
                round(idle_after - idle_effects[axis], 6),
                axis,
            )

    # -- the consequence, bounded --------------------------------------

    def test_dirt_pressures_stress_on_the_neglect_stream(self):
        self.assertGreater(
            self.probe["neglect_on"]["final_stress"],
            self.probe["neglect_off"]["final_stress"],
        )

    def test_the_mechanic_is_not_lethal_on_the_neglect_stream(self):
        self.assertEqual(
            self.probe["neglect_on"]["survival_ticks"],
            self.probe["neglect_off"]["survival_ticks"],
        )
        self.assertEqual(
            self.probe["neglect_on"]["death_cause"],
            self.probe["neglect_off"]["death_cause"],
        )

    def test_a_filthy_companion_does_not_die_of_dirt(self):
        self.assertTrue(self.probe["filthy_alive"])

    # -- the episode surface -------------------------------------------

    def test_clean_rides_an_explicit_stream_only_with_the_mechanic_on(self):
        self.assertTrue(self.probe["clean_stream_alive"])
        self.assertEqual(
            self.probe["clean_stream_off_error"],
            "unsupported lifecycle action: clean",
        )


if __name__ == "__main__":
    unittest.main()
