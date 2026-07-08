import json
import sys
import tempfile
import unittest
from pathlib import Path

from thread_fleet import (
    FLEET_THREAD_NAMES,
    FLEET_THREADS,
    attention_forecast_observe,
    attention_forecast_signal,
    boredom_novelty_observe,
    boredom_novelty_signal,
    build_thread_fleet_report,
    energy_forecast_observe,
    energy_forecast_signal,
    hunger_forecast_observe,
    hunger_forecast_signal,
    interaction_timing_observe,
    interaction_timing_signal,
    observe_fleet,
    write_thread_fleet_artifacts,
)

LAB_DIR = Path(__file__).resolve().parent
REPO_ROOT = LAB_DIR.parents[1]
GRID_GENOME = REPO_ROOT / "labs" / "grid_genome"
PACKAGE_SRC = REPO_ROOT / "packages" / "mecha_engine" / "src"
for path in [GRID_GENOME, PACKAGE_SRC]:
    if str(path) not in sys.path:
        sys.path.insert(0, str(path))

from micro_switchboard import run_switchboard  # noqa: E402

from mecha_engine.learning import decide  # noqa: E402


def _state(**overrides) -> dict:
    state = {
        "hunger": 0.4,
        "energy": 0.8,
        "stress": 0.1,
        "grid_stability": 0.9,
        "recent_interactions": [1, 0, 1],
        "action_rewards": {},
    }
    state.update(overrides)
    return state


class FleetContractTests(unittest.TestCase):
    def test_the_registry_names_the_fleet(self):
        self.assertIn("hunger_forecast", FLEET_THREAD_NAMES)
        for name, observe, signal in FLEET_THREADS:
            self.assertTrue(callable(observe))
            self.assertTrue(callable(signal))

    def test_the_registry_execution_order_is_fixed(self):
        self.assertEqual(
            [
                "hunger_forecast",
                "energy_forecast",
                "boredom_novelty",
                "attention_forecast",
                "interaction_timing",
            ],
            FLEET_THREAD_NAMES,
        )

    def test_observe_fleet_is_pure_and_json_serializable(self):
        state = _state(learning_switches={"hunger_forecast": True})
        pristine = json.loads(json.dumps(state))
        thread_states = observe_fleet(state)
        self.assertEqual(pristine, state)  # never mutates the input
        json.dumps(thread_states)  # bounded, serializable memory
        self.assertIn("hunger_forecast", thread_states)

    def test_observe_fleet_only_runs_opted_in_threads(self):
        state = _state()  # no switches at all
        self.assertEqual({}, observe_fleet(state))
        state = _state(learning_switches={"hunger_forecast": False})
        self.assertEqual({}, observe_fleet(state))


class HungerForecastTests(unittest.TestCase):
    def test_cold_start_is_silent(self):
        signal = hunger_forecast_signal({}, _state())
        self.assertEqual(0.0, signal["confidence"])
        self.assertEqual({}, signal["effects"])

    def test_rising_hunger_raises_anticipatory_feed_utility(self):
        thread_state: dict = {}
        for hunger in [0.30, 0.38, 0.46, 0.54, 0.62]:
            thread_state = hunger_forecast_observe(
                thread_state, _state(hunger=hunger)
            )
        signal = hunger_forecast_signal(thread_state, _state(hunger=0.62))
        self.assertGreater(signal["confidence"], 0.3)
        self.assertGreater(signal["effects"].get("feed", 0.0), 0.0)
        self.assertGreater(signal["output"]["predicted_hunger"], 0.62)

    def test_flat_low_hunger_stays_quiet(self):
        thread_state: dict = {}
        for _ in range(6):
            thread_state = hunger_forecast_observe(
                thread_state, _state(hunger=0.3)
            )
        signal = hunger_forecast_signal(thread_state, _state(hunger=0.3))
        self.assertEqual(0.0, signal["effects"].get("feed", 0.0))

    def test_memory_is_bounded(self):
        thread_state: dict = {}
        for index in range(50):
            thread_state = hunger_forecast_observe(
                thread_state, _state(hunger=0.5)
            )
        self.assertLessEqual(len(thread_state["history"]), 8)


class EnergyForecastTests(unittest.TestCase):
    def test_cold_start_is_silent(self):
        signal = energy_forecast_signal({}, _state())
        self.assertEqual(0.0, signal["confidence"])
        self.assertEqual({}, signal["effects"])

    def test_falling_energy_raises_anticipatory_sleep_utility(self):
        thread_state: dict = {}
        for energy in [0.60, 0.52, 0.44, 0.38, 0.32]:
            thread_state = energy_forecast_observe(
                thread_state, _state(energy=energy)
            )
        signal = energy_forecast_signal(thread_state, _state(energy=0.32))
        self.assertGreater(signal["confidence"], 0.3)
        self.assertGreater(signal["effects"].get("sleep", 0.0), 0.0)
        self.assertLess(signal["output"]["predicted_energy"], 0.32)

    def test_high_flat_energy_stays_quiet(self):
        thread_state: dict = {}
        for _ in range(6):
            thread_state = energy_forecast_observe(
                thread_state, _state(energy=0.8)
            )
        signal = energy_forecast_signal(thread_state, _state(energy=0.8))
        self.assertEqual(0.0, signal["effects"].get("sleep", 0.0))

    def test_memory_is_bounded(self):
        thread_state: dict = {}
        for _ in range(50):
            thread_state = energy_forecast_observe(
                thread_state, _state(energy=0.5)
            )
        self.assertLessEqual(len(thread_state["history"]), 8)


class BoredomNoveltyTests(unittest.TestCase):
    def _observe_actions(self, actions: list[str]) -> dict:
        thread_state: dict = {}
        counts = {a: 0 for a in ["feed", "play", "sleep", "idle", "mutate"]}
        for action in actions:
            counts[action] += 1
            thread_state = boredom_novelty_observe(
                thread_state, _state(action_counts=dict(counts))
            )
        return thread_state

    def test_cold_start_is_silent(self):
        signal = boredom_novelty_signal({}, _state())
        self.assertEqual(0.0, signal["confidence"])
        self.assertEqual({}, signal["effects"])

    def test_repetition_raises_boredom_and_play_utility(self):
        thread_state = self._observe_actions(["idle"] * 8)
        signal = boredom_novelty_signal(thread_state, _state())
        self.assertGreater(signal["output"]["boredom"], 0.6)
        self.assertGreater(signal["effects"].get("play", 0.0), 0.0)
        self.assertGreater(signal["output"]["predicted_repeat_probability"], 0.9)

    def test_varied_actions_stay_novel(self):
        thread_state = self._observe_actions(
            ["feed", "play", "sleep", "idle", "mutate", "feed", "play", "sleep"]
        )
        signal = boredom_novelty_signal(thread_state, _state())
        self.assertLess(signal["output"]["boredom"], 0.5)

    def test_memory_is_bounded(self):
        thread_state = self._observe_actions(["idle"] * 50)
        self.assertLessEqual(len(thread_state["recent_actions"]), 8)


class AttentionForecastTests(unittest.TestCase):
    def test_cold_start_has_low_confidence(self):
        signal = attention_forecast_signal({}, _state())
        self.assertEqual(0.0, signal["confidence"])
        self.assertEqual({}, signal["effects"])

    def test_sustained_interaction_raises_predicted_attention(self):
        thread_state: dict = {}
        for _ in range(25):
            thread_state = attention_forecast_observe(
                thread_state, _state(recent_interactions=[1, 1, 1, 1, 1])
            )
        signal = attention_forecast_signal(thread_state, _state())
        self.assertGreater(
            signal["output"]["predicted_interaction_probability"], 0.8
        )
        self.assertGreater(signal["confidence"], 0.9)
        self.assertGreater(signal["effects"].get("play", 0.0), 0.0)

    def test_absence_lowers_predicted_attention(self):
        thread_state: dict = {}
        for _ in range(25):
            thread_state = attention_forecast_observe(
                thread_state, _state(recent_interactions=[0, 0, 0, 0, 0])
            )
        signal = attention_forecast_signal(thread_state, _state())
        self.assertLess(
            signal["output"]["predicted_interaction_probability"], 0.2
        )


class InteractionTimingTests(unittest.TestCase):
    def test_cold_start_is_silent(self):
        signal = interaction_timing_signal({}, _state())
        self.assertEqual(0.0, signal["confidence"])
        self.assertEqual({}, signal["effects"])

    def test_periodic_interactions_predict_the_next_gap(self):
        thread_state: dict = {}
        # A strict every-4th-tick interaction rhythm.
        for tick in range(24):
            interaction = 1 if tick % 4 == 3 else 0
            thread_state = interaction_timing_observe(
                thread_state, _state(recent_interactions=[0, 0, 0, interaction])
            )
        signal = interaction_timing_signal(thread_state, _state())
        self.assertGreater(signal["confidence"], 0.5)
        self.assertAlmostEqual(
            4.0, signal["output"]["mean_gap_ticks"], delta=1.0
        )

    def test_imminent_interaction_raises_play_readiness(self):
        thread_state: dict = {}
        for tick in range(24):
            interaction = 1 if tick % 4 == 3 else 0
            thread_state = interaction_timing_observe(
                thread_state, _state(recent_interactions=[0, 0, 0, interaction])
            )
        # Three quiet ticks into the rhythm: the next one is due.
        for _ in range(3):
            thread_state = interaction_timing_observe(
                thread_state, _state(recent_interactions=[0, 0, 0, 0])
            )
        signal = interaction_timing_signal(thread_state, _state())
        self.assertLessEqual(
            signal["output"]["predicted_ticks_to_next_interaction"], 1.5
        )
        self.assertGreater(signal["effects"].get("play", 0.0), 0.0)


class SwitchboardSeamTests(unittest.TestCase):
    def test_frozen_paths_are_byte_identical_without_opt_in(self):
        # The load-bearing D1 rule: no flow that does not opt in may see
        # ANY change — lab and package, plain and switched states.
        for state in [
            _state(),
            _state(learning_switches={"hidden_mood_estimator": False}),
        ]:
            with self.subTest(state=json.dumps(state, sort_keys=True)[:60]):
                lab = run_switchboard(state)
                package = decide(state)
                self.assertEqual(lab, package)
                thread_names = [t["name"] for t in lab["threads"]]
                self.assertNotIn("hunger_forecast", thread_names)

    def test_opted_in_fleet_thread_rides_the_decision(self):
        thread_state: dict = {}
        for hunger in [0.30, 0.40, 0.50, 0.60, 0.70]:
            thread_state = hunger_forecast_observe(
                thread_state, _state(hunger=hunger)
            )
        state = _state(
            hunger=0.6,
            learning_switches={"hunger_forecast": True},
            thread_states={"hunger_forecast": thread_state},
        )
        lab = run_switchboard(state)
        package = decide(state)
        self.assertEqual(lab, package)
        thread_names = [t["name"] for t in lab["threads"]]
        self.assertIn("hunger_forecast", thread_names)
        # The anticipatory signal moved the utility table.
        baseline = run_switchboard(_state(hunger=0.6))
        self.assertGreater(
            lab["utilities"]["feed"], baseline["utilities"]["feed"]
        )

    def test_the_whole_fleet_rides_when_every_thread_opts_in(self):
        state = _state(
            learning_switches={name: True for name in FLEET_THREAD_NAMES}
        )
        state["thread_states"] = observe_fleet(state)
        lab = run_switchboard(state)
        package = decide(state)
        self.assertEqual(lab, package)
        thread_names = [t["name"] for t in lab["threads"]]
        for name in FLEET_THREAD_NAMES:
            self.assertIn(name, thread_names)


class ReportTests(unittest.TestCase):
    report: dict

    @classmethod
    def setUpClass(cls):
        cls.report = build_thread_fleet_report()

    def test_report_shape_and_serializability(self):
        for key in [
            "artifact_id",
            "status",
            "date",
            "purpose",
            "source_artifacts",
            "metrics",
            "closed_states",
            "blocked_states",
            "decision",
            "next_research_step",
        ]:
            self.assertIn(key, self.report)
        self.assertEqual(
            "micro_thread_fleet_contract_stage0", self.report["artifact_id"]
        )
        self.assertEqual("complete", self.report["status"])
        self.assertEqual(
            self.report, json.loads(json.dumps(self.report))
        )
        self.assertTrue(self.report["blocked_states"])

    def test_frozen_replay_is_byte_identical_lab_and_package(self):
        frozen = self.report["metrics"]["frozen_replay"]
        self.assertEqual(frozen["ticks"], frozen["lab_package_decisions_identical"])
        self.assertEqual(0, frozen["fleet_thread_appearances"])

    def test_fleet_replay_anticipates_the_reactive_threshold(self):
        fleet = self.report["metrics"]["fleet_replay"]
        self.assertGreater(fleet["anticipatory_signal_ticks"], 0)
        self.assertGreater(fleet["utility_moved_ticks"], 0)
        if fleet["first_reactive_hungry_tick"] is not None:
            self.assertLess(
                fleet["first_anticipatory_signal_tick"],
                fleet["first_reactive_hungry_tick"],
            )
        self.assertGreaterEqual(fleet["cold_start_silent_ticks"], 1)

    def test_write_artifacts_round_trips(self):
        with tempfile.TemporaryDirectory() as tmp:
            output_dir = Path(tmp)
            write_thread_fleet_artifacts(output_dir, self.report)
            written = output_dir / "micro_thread_fleet_contract_stage0.json"
            self.assertTrue(written.exists())
            self.assertEqual(
                self.report,
                json.loads(written.read_text(encoding="utf-8")),
            )


if __name__ == "__main__":
    unittest.main()
