import unittest

from micro_switchboard import (
    action_preference_bandit,
    estimate_hidden_mood,
    estimate_mutation_risk,
    recent_interaction_ewma,
    run_switchboard,
)


def sample_state():
    return {
        "hunger": 0.72,
        "energy": 0.28,
        "bond": 0.55,
        "stress": 0.36,
        "grid_stability": 0.82,
        "recent_interactions": [1, 0, 1, 1, 0],
        "action_rewards": {
            "feed": [0.7, 0.8],
            "play": [0.4, 0.6, 0.5],
            "sleep": [0.9],
            "idle": [0.2, 0.3],
        },
    }


class MicroSwitchboardTests(unittest.TestCase):
    def test_each_thread_returns_required_contract(self):
        state = sample_state()
        threads = [
            recent_interaction_ewma(state),
            estimate_hidden_mood(state),
            action_preference_bandit(state),
            estimate_mutation_risk(state),
        ]

        for thread in threads:
            with self.subTest(thread=thread["name"]):
                self.assertIn("input", thread)
                self.assertIn("output", thread)
                self.assertIn("confidence", thread)
                self.assertIn("explanation", thread)
                self.assertIn("effects", thread)
                self.assertGreaterEqual(thread["confidence"], 0)
                self.assertLessEqual(thread["confidence"], 1)

    def test_switchboard_selects_explainable_action(self):
        decision = run_switchboard(sample_state())

        self.assertIn(decision["action"], {"feed", "play", "sleep", "idle", "mutate"})
        self.assertGreaterEqual(decision["confidence"], 0)
        self.assertLessEqual(decision["confidence"], 1)
        self.assertGreaterEqual(len(decision["threads"]), 4)
        self.assertTrue(decision["explanation"])

    def test_switchboard_prioritizes_sleep_when_energy_is_low(self):
        state = sample_state()
        state["hunger"] = 0.2
        state["energy"] = 0.08

        decision = run_switchboard(state)

        self.assertEqual("sleep", decision["action"])


if __name__ == "__main__":
    unittest.main()
