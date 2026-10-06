"""X7 frozen factual care inputs and explicit cold succession."""
import copy
import json
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
for folder in ("game/src", "packages/mecha_engine/src"):
    sys.path.insert(0, str(ROOT / folder))

from mecha_engine.generation import generate_candidate
from mecha_game.care_history import capture_care_context, validate_care_context
from mecha_game.contribute import companion_release_source
from mecha_game.era_plan import EraPlan
from mecha_game.lineage import LineageBrowser
from mecha_game.session import CompanionSession, LOG_LIMIT, load_session_inputs


def pet(**kwargs):
    grid, profile, model = load_session_inputs(
        ROOT / "data/seed_grids_16x16/mg_seed16_001_beetle.json",
        ROOT / "data/slips/valid/slip_v2_cleanliness.json")
    return CompanionSession(grid, profile, model=model, **kwargs)


def neglect(session):
    for _ in range(400):
        if not session.alive:
            return
        session.advance()
    raise AssertionError("neglect failed to reach an actual death")


class CareHistoryTests(unittest.TestCase):
    def test_frozen_source_and_first_staging_keep_actual_observation(self):
        session = pet()
        session.advance("feed")
        source = companion_release_source(session)
        frozen = copy.deepcopy(source["care_context"])
        self.assertEqual(session.keeper_id, frozen["keeper_id"])
        self.assertEqual(session.lineage[-1]["life_id"], frozen["life_id"])
        self.assertEqual({"feed": 1}, frozen["care_summary"]["keeper_actions"])
        self.assertEqual("feed", frozen["events"][0]["action"])
        with tempfile.TemporaryDirectory() as tmp:
            plan = EraPlan(Path(tmp) / "plan.json")
            plan.stage([session.grid], [source])
            session.advance("sleep")
            self.assertEqual(0, plan.stage([session.grid], [companion_release_source(session)]))
            self.assertEqual(frozen, plan.release_sources[0]["care_context"])
            self.assertEqual(frozen, EraPlan(plan.path).release_sources[0]["care_context"])
            plan.unstage_all()
            plan.stage([session.grid], [companion_release_source(session)])
            self.assertEqual(2, plan.release_sources[0]["care_context"]["care_summary"]["ticks_observed"])
        self.assertEqual(frozen, source["care_context"])

    def test_exact_summary_survives_trim_adoption_and_restart(self):
        session = pet()
        for _ in range(LOG_LIMIT + 11):
            action = ("feed" if session.state["hunger"] > .55 else
                      "sleep" if session.state["energy"] < .35 else
                      "clean" if session.state.get("cleanliness", 1) < .6 else None)
            session.advance(action)
        context = capture_care_context(session)
        self.assertEqual(LOG_LIMIT, len(context["events"]))
        self.assertEqual(11, context["events_omitted"])
        self.assertEqual(12, context["events"][0]["tick"])
        self.assertEqual(LOG_LIMIT + 11, context["care_summary"]["ticks_observed"])
        with tempfile.TemporaryDirectory() as tmp:
            path = session.save(Path(tmp) / "companion.json")
            loaded = CompanionSession.load(path)
            self.assertEqual(context, capture_care_context(loaded))
            adopted = loaded.adopt(loaded.grid, loaded.slip_profile)
            self.assertEqual(context["care_summary"], adopted.lineage[-2]["care_summary"])
            self.assertEqual([], capture_care_context(adopted)["events"])

    def test_context_rejects_counter_tail_and_identity_corruption(self):
        session = pet()
        session.advance("feed")
        context = capture_care_context(session)
        corruptions = [
            lambda c: c["care_summary"]["keeper_actions"].update(feed=2),
            lambda c: c["care_summary"].update(beg_requests=2),
            lambda c: c["events"][0].update(tick=2),
            lambda c: c.update(events_omitted=2),
            lambda c: c.update(outcome="dead"),
        ]
        for mutate in corruptions:
            with self.subTest(mutate=mutate):
                corrupt = copy.deepcopy(context)
                mutate(corrupt)
                with self.assertRaises(ValueError):
                    validate_care_context(corrupt)
        with self.assertRaises(ValueError):
            validate_care_context(context, life_id="different-life")

    def test_disabled_succession_is_exact_legacy_child(self):
        session = pet()
        session.advance("feed")
        neglect(session)
        expected = generate_candidate(session.grid, session.model, session.slip_profile,
            rng_seed=session.succession_seed + session.succession_index)
        session.succeed()
        self.assertEqual(expected, session.grid)
        self.assertNotIn("care_selection", session.lineage[-1])

    def test_enabled_succession_persists_context_and_newborn_starts_cold(self):
        session = pet(care_selection_policy="observed_care_selection_v1", learning_policy="qtable")
        session.advance("feed")
        neglect(session)
        context = capture_care_context(session)
        session.succeed()
        selected = session.lineage[-1]["care_selection"]
        self.assertEqual(context, selected["context"])
        self.assertEqual(context["life_id"], session.lineage[-1]["parent_life_id"])
        self.assertEqual(8, selected["receipt"]["pool_size"])
        self.assertNotIn("thread_states", session.state)
        self.assertEqual(0, session.state["age_ticks"])
        with tempfile.TemporaryDirectory() as tmp:
            path = session.save(Path(tmp) / "companion.json")
            loaded = CompanionSession.load(path)
            self.assertEqual(selected, loaded.lineage[-1]["care_selection"])
            self.assertEqual("observed_care_selection_v1", loaded.care_selection_policy)
            adopted = loaded.adopt(loaded.grid, loaded.slip_profile)
            self.assertEqual(loaded.care_selection_policy, adopted.care_selection_policy)
            with self.assertRaises(ValueError):
                CompanionSession.load(path, care_selection_policy="off")
            payload = json.loads(path.read_text())
            payload["lineage"][-1]["care_selection"]["context"]["life_id"] += "-wrong"
            with self.assertRaises(ValueError):
                CompanionSession._from_payload(payload)
        lines = " ".join(LineageBrowser(session.lineage).detail_lines())
        self.assertIn("stress", lines.lower())
        self.assertIn("species", lines.lower())

    def test_explicit_disabled_pristine_evaluator_round_trips(self):
        session = pet(care_selection_policy="off", care_evaluator="pristine")
        with tempfile.TemporaryDirectory() as tmp:
            path = session.save(Path(tmp) / "companion.json")
            loaded = CompanionSession.load(path, care_selection_policy="off", care_evaluator="pristine")
            self.assertEqual("pristine", loaded.care_evaluator)
            self.assertEqual("off", loaded.care_selection_policy)
            path = pet().save(Path(tmp) / "default.json")
            payload = json.loads(path.read_text())
            self.assertNotIn("care_selection_policy", payload)
            self.assertNotIn("care_evaluator", payload)

    def test_rehashed_tape_cannot_replace_actual_parent_care(self):
        from mecha_game.care_history import care_grid_digest, validate_care_selection
        session = pet(care_selection_policy="observed_care_selection_v1")
        session.advance("feed")
        neglect(session)
        session.succeed()
        selected = copy.deepcopy(session.lineage[-1]["care_selection"])
        selected["context"]["events"][0]["action"] = "play"
        selected["context"]["care_summary"]["keeper_actions"] = {"play": 1}
        selected["receipt"]["context_sha256"] = care_grid_digest(selected["context"])
        with self.assertRaisesRegex(ValueError, "actual parent's care"):
            validate_care_selection(selected, parent_record=session.lineage[-2], child_grid=session.grid)

    def test_receipt_schema_window_rank_and_historical_child_are_validated(self):
        from mecha_game.care_history import validate_care_selection
        session = pet(care_selection_policy="observed_care_selection_v1")
        neglect(session)
        session.succeed()
        selected = session.lineage[-1]["care_selection"]
        mutations = [
            lambda r: r["observed_window"].update(ticks=999),
            lambda r: r["candidates"][0].update(index=999),
            lambda r: r["candidates"][0].update(need_balance=-100),
            lambda r: r["candidates"][0].update(need_balance=float("nan")),
            lambda r: r["candidates"][1].update(rng_seed=-999),
            lambda r: r.update(selected_structure_sha256="0" * 64),
            lambda r: r.update(selected_index=(r["selected_index"] + 1) % 8),
        ]
        for mutate in mutations:
            with self.subTest(mutation=mutate):
                corrupt = copy.deepcopy(selected)
                mutate(corrupt["receipt"])
                with self.assertRaises(ValueError):
                    validate_care_selection(corrupt, parent_record=session.lineage[-2], child_grid=session.grid)
        historical = copy.deepcopy(session.lineage[-1])
        historical["grid_sha256"] = "0" * 64
        with self.assertRaisesRegex(ValueError, "recorded body"):
            validate_care_selection(selected, parent_record=session.lineage[-2], child_record=historical)

    def test_engine_game_context_negative_vectors_agree(self):
        from mecha_engine.runtime.care import validate_care_context as validate_engine
        session = pet()
        session.advance("feed")
        context = capture_care_context(session)
        vectors = [None, {}, context]
        def alter(**values):
            result = copy.deepcopy(context)
            result.update(values)
            return result
        vectors.extend([alter(life_id="someone-else:life-x"), alter(life_id=context["keeper_id"] + ":life-"),
                        alter(last_age_ticks=-1),
                        alter(events_omitted=1), alter(grid_sha256="g" * 64)])
        for field, value in (("beg_requests", 1), ("keeper_actions", {"feed": 0}),
                             ("companion_actions", {"feed": 1})):
            result = copy.deepcopy(context)
            result["care_summary"][field] = value
            vectors.append(result)
        for vector in vectors:
            outcomes = []
            for validator in (validate_care_context, validate_engine):
                try:
                    validator(vector)
                    outcomes.append("accept")
                except ValueError:
                    outcomes.append("refuse")
            self.assertEqual(outcomes[0], outcomes[1])

    def test_new_event_and_snapshot_are_bound_to_current_life(self):
        session = pet()
        session.advance()
        snapshot = session.snapshot()
        self.assertEqual(session.lineage[-1]["life_id"], snapshot["life_id"])
        self.assertEqual(snapshot["life_id"], snapshot["log"][-1]["life_id"])
        self.assertEqual(0, snapshot["born_session_tick"])
        adopted = session.adopt(session.grid, session.slip_profile)
        self.assertNotEqual(snapshot["life_id"], adopted.snapshot()["life_id"])
        self.assertEqual(1, adopted.snapshot()["born_session_tick"])


if __name__ == "__main__":
    unittest.main()
