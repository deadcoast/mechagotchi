"""R1 complete decision/state parity with the existing bounded lab policy."""
import json
import sys
import unittest
from copy import deepcopy
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
for relative in ("labs/micro_threads", "labs/grid_genome", "labs/lifecycle_sim", "packages/mecha_engine/src"):
    sys.path.insert(0, str(ROOT / relative))
from thread_fleet import observe_fleet as lab_observe
from micro_switchboard import run_switchboard, run_scenarios
from mecha_engine.learning import decide
from mecha_engine.learning.threads import observe_fleet
from mecha_engine.lifecycle import initial_state, advance_tick


def fixture(**values):
    state = dict(hunger=.55, energy=.55, bond=.5, stress=.2,
                 grid_stability=.9, recent_interactions=[1,0,1], history=[])
    state.update(values)
    return state


class PackageQtableParityTests(unittest.TestCase):
    def assert_parity(self, state):
        before = deepcopy(state)
        self.assertEqual(lab_observe(state), observe_fleet(state))
        self.assertEqual(run_switchboard(state), decide(state))
        self.assertEqual(before, state)

    def test_switches_cold_and_missing_producer(self):
        for producer in (None, False, 0, 1, "true", True):
            for consumer in (None, False, 0, 1, "true", True):
                switches = {k:v for k,v in (("qtable_policy",producer), ("qtable_consumer",consumer)) if v is not None}
                with self.subTest(switches=switches):
                    self.assert_parity(fixture(learning_switches=switches))

    def test_floor_boundaries_ties_and_deliberation(self):
        for hunger in (.339999, .34, .669999, .67):
            bucket = ("0" if hunger < .34 else "1" if hunger < .67 else "2") + "1"
            for visits in (2, 3, 11, 12, 13):
                for deliberation in (None, 4):
                    for tied in (False, True):
                        table = {f"{bucket}|mutate": {"mean":.9,"n":visits}}
                        if tied:
                            table[f"{bucket}|feed"] = {"mean":.9,"n":visits}
                        state = fixture(hunger=hunger, learning_switches={"qtable_policy":True,"qtable_consumer":True},
                            thread_states={"qtable_policy":{"q":table,"pending_bucket":bucket}})
                        if deliberation:
                            state.update(deliberation_max_ticks=deliberation, deliberation_confidence_threshold=.99)
                        with self.subTest(hunger=hunger, visits=visits, deliberation=deliberation, tied=tied):
                            self.assert_parity(state)
                            decision=decide(state)
                            if visits >= 12:
                                self.assertEqual("mutate", decision["action"])


    def test_follower_can_override_additive_action(self):
        state=fixture(hunger=.9, stress=.9,
            learning_switches={"qtable_policy":True,"qtable_consumer":True},
            thread_states={"qtable_policy":{"q":{"21|mutate":{"mean":.9,"n":12}}}})
        self.assert_parity(state)
        self.assertEqual("mutate",decide(state)["action"])
        self.assertFalse(decide(state)["qtable_consumer"]["agreed"])

    def test_complete_episodes_execute_and_credit_same_actions(self):
        grid=json.loads((ROOT/"data/seed_grids_16x16/mg_seed16_001_beetle.json").read_text())
        slip=json.loads((ROOT/"data/slips/valid/slip_lcd_seed.json").read_text())
        for consumer in (False, True):
            state=initial_state(grid, slip)
            state["learning_switches"]={"qtable_policy":True,"qtable_consumer":consumer}
            for tick in range(200):
                self.assert_parity(state)
                state["thread_states"]=observe_fleet(state)
                self.assert_parity(state)
                decision=decide(state)
                executed="feed" if state["hunger"]>.6 else decision["action"]
                state=advance_tick(state, executed)
                state["history"]=state["history"][-32:]
                if not state["alive"]:
                    break
            table=state["thread_states"]["qtable_policy"]["q"]
            self.assertTrue(table)
            self.assertLessEqual(len(table),45)

    def test_committed_off_mode_instrument(self):
        committed=json.loads((ROOT/"data/micro_learners/switchboard_stage0.json").read_text())
        self.assertEqual(committed,run_scenarios())
        # Existing package episode pins also compare the complete off-mode outputs.


if __name__ == "__main__":
    unittest.main()
