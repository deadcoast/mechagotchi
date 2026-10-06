"""Cycle 38 X1: actual lives survive adoption without inventing ancestry or care."""
import copy
import json
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
for relative in ("game/src", "packages/mecha_engine/src"):
    sys.path.insert(0, str(ROOT / relative))

from mecha_engine.generation import generate_candidate, train_generation_model
from mecha_game.hatchery import hatch_founders
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
    raise AssertionError("actual neglect did not reach death")


def attentive(session):
    if session.state["hunger"] > .55:
        return "feed"
    if session.state["energy"] < .35:
        return "sleep"
    if session.state.get("cleanliness", 1) < .6:
        return "clean"
    return None


class KeeperChronicleTests(unittest.TestCase):
    def test_real_care_death_child_hatch_archive_restart_for_both_policies(self):
        for policy in ("incumbent", "qtable"):
            with self.subTest(policy=policy), tempfile.TemporaryDirectory() as tmp:
                session = pet(learning_policy=policy)
                session.bind_campaign("campaign-one")
                session.advance("feed")
                session.advance("play")
                founder_id = session.grid["grid_id"]
                neglect(session)
                session.succeed()
                session.advance("feed")
                original_records = copy.deepcopy(session.lineage)
                hatched = hatch_founders([session.grid], session.slip_profile, rng_seed=441)[0]["grid"]
                before = copy.deepcopy(session.lineage)
                adopted = session.adopt(hatched, session.slip_profile,
                    model=train_generation_model([hatched]), origin="hatched")
                self.assertEqual(before, session.lineage)
                self.assertEqual(session.session_tick, adopted.session_tick)
                self.assertEqual(3, len(adopted.lineage))
                adopted.advance("clean")
                adopted = adopted.adopt(hatched, adopted.slip_profile, origin="era_elite",
                    source={"campaign_id": "campaign-one", "era_index": 1})
                adopted.advance("feed")
                path = Path(tmp) / "companion.json"
                adopted.save_checkpoint(path)
                adopted.advance("sleep")
                adopted.save_checkpoint(path)
                resumed = CompanionSession.load(path)
                self.assertEqual(4, len(resumed.lineage))
                self.assertEqual(adopted.lineage, resumed.lineage)
                self.assertEqual(adopted.keeper_id, resumed.keeper_id)
                self.assertEqual("campaign-one", resumed.campaign_id)
                self.assertEqual(policy, resumed.learning_policy)
                self.assertEqual(original_records[0], resumed.lineage[0])
                self.assertEqual("dead", resumed.lineage[0]["outcome"])
                self.assertEqual({"feed": 1, "play": 1}, resumed.lineage[0]["care_summary"]["keeper_actions"])
                self.assertEqual(founder_id, resumed.lineage[1]["parent_grid_id"])
                self.assertEqual(resumed.lineage[0]["life_id"], resumed.lineage[1]["parent_life_id"])
                for index in (1, 2):
                    self.assertEqual("replaced_alive", resumed.lineage[index]["outcome"])
                    self.assertNotIn("death_cause", resumed.lineage[index])
                self.assertNotIn("parent_life_id", resumed.lineage[2])
                self.assertEqual(hatched["lineage"], resumed.lineage[3]["lineage"])
                self.assertEqual(4, len({row["life_id"] for row in resumed.lineage}))
                self.assertEqual(resumed.lineage, json.loads(path.with_name("lineage.json").read_text())["records"])
                self.assertEqual(4, len(json.loads(path.with_suffix(".bak.json").read_text())["lineage"]))

    def test_adoption_keeps_configuration_but_learning_starts_cold(self):
        for fleet in (False, True):
            for policy in ("incumbent", "qtable"):
                with self.subTest(fleet=fleet, policy=policy):
                    session = pet(fleet=fleet, learning_policy=policy, mechanics=())
                    for _ in range(8):
                        session.advance("feed")
                    adopted = session.adopt(session.grid, session.slip_profile, origin="hatched")
                    self.assertEqual(fleet, adopted.fleet)
                    self.assertEqual(policy, adopted.learning_policy)
                    self.assertEqual((), adopted.mechanics)
                    self.assertNotIn("cleanliness", adopted.state)
                    self.assertNotIn("qtable_policy", adopted.state.get("thread_states", {}))
                    self.assertEqual(0, adopted.state["age_ticks"])
                    self.assertEqual(session.keeper_id, adopted.keeper_id)

    def test_explicit_new_life_policy_does_not_rewrite_earlier_policy(self):
        session = pet(learning_policy="qtable")
        adopted = session.adopt(session.grid, session.slip_profile,
                                origin="new_companion", learning_policy="incumbent")
        self.assertEqual("qtable", adopted.lineage[0]["learning_policy"])
        self.assertEqual("incumbent", adopted.learning_policy)
        self.assertNotIn("qtable_policy", adopted.state["learning_switches"])

    def test_exact_care_totals_outlive_bounded_event_tail_and_restart(self):
        session = pet()
        expected = {}
        for _ in range(LOG_LIMIT + 35):
            action = attentive(session)
            if action:
                expected[action] = expected.get(action, 0) + 1
            session.advance(action)
        summary = session.lineage[-1]["care_summary"]
        self.assertEqual(expected, summary["keeper_actions"])
        self.assertEqual(LOG_LIMIT + 35, summary["ticks_observed"])
        self.assertEqual(LOG_LIMIT, len(session.lineage[-1]["events"]))
        self.assertEqual(35, session.lineage[-1]["events_omitted"])
        with tempfile.TemporaryDirectory() as tmp:
            path = session.save(Path(tmp) / "companion.json")
            loaded = CompanionSession.load(path)
            loaded.advance("feed")
            self.assertEqual(expected["feed"] + 1, loaded.lineage[-1]["care_summary"]["keeper_actions"]["feed"])

    def test_beg_request_is_not_counted_as_keeper_feeding(self):
        session = pet()
        session.state["hunger"] = .9
        session.advance()
        summary = session.lineage[-1]["care_summary"]
        self.assertEqual({}, summary["keeper_actions"])
        self.assertEqual({"idle": 1}, summary["companion_actions"])
        self.assertEqual(1, summary["beg_requests"])
        session.advance("feed")
        self.assertEqual({"feed": 1}, summary["keeper_actions"])

    def test_invalid_adoption_does_not_change_the_original_story(self):
        session = pet()
        before = copy.deepcopy(session.__dict__)
        invalid = copy.deepcopy(session.grid)
        invalid["cells"] = []
        with self.assertRaises(ValueError):
            session.adopt(invalid, session.slip_profile, origin="hatched")
        self.assertEqual(before["state"], session.state)
        self.assertEqual(before["lineage"], session.lineage)
        self.assertEqual(before["chronicle"], session.chronicle)

    def test_succession_outputs_keep_the_per_adoption_seed_sequence(self):
        session = pet()
        for _ in range(2):
            session = session.adopt(session.grid, session.slip_profile, origin="hatched")
        for index in (1, 2):
            neglect(session)
            expected = generate_candidate(session.grid, session.model, slip_profile=session.slip_profile,
                                          rng_seed=session.succession_seed + index)
            session.succeed()
            self.assertEqual(expected, session.grid)
        with tempfile.TemporaryDirectory() as tmp:
            path = session.save(Path(tmp) / "companion.json")
            resumed = CompanionSession.load(path)
            neglect(resumed)
            expected = generate_candidate(resumed.grid, resumed.model, slip_profile=resumed.slip_profile,
                                          rng_seed=resumed.succession_seed + 3)
            resumed.succeed()
            self.assertEqual(expected, resumed.grid)

    def test_legacy_reads_preserve_bytes_state_and_unknown_history(self):
        session = pet(learning_policy="qtable")
        session.advance("feed")
        neglect(session)
        session.succeed()
        session.advance("play")
        with tempfile.TemporaryDirectory() as tmp:
            path = session.save(Path(tmp) / "companion.json")
            payload = json.loads(path.read_text())
            payload.pop("chronicle", None)
            payload.pop("succession_index", None)
            keep = {"grid_id", "parent_grid_id", "lineage", "born_session_tick", "origin",
                    "learning_policy", "died_age_ticks", "died_session_tick", "death_cause"}
            payload["lineage"] = [{key: value for key, value in row.items() if key in keep}
                                  for row in payload["lineage"]]
            path.write_text(json.dumps(payload))
            before = path.read_bytes()
            loaded = CompanionSession.load(path)
            self.assertEqual(before, path.read_bytes())
            self.assertEqual(payload["state"], loaded.state)
            self.assertEqual(payload["log"], loaded.log)
            self.assertEqual("unavailable", loaded.lineage[0]["care_summary"]["history"])
            self.assertEqual("partial", loaded.lineage[-1]["care_summary"]["history"])
            self.assertEqual({}, loaded.lineage[-1]["care_summary"]["keeper_actions"])
            self.assertEqual(2, loaded.succession_index)
            loaded.advance("feed")
            self.assertEqual({"feed": 1}, loaded.lineage[-1]["care_summary"]["keeper_actions"])
            self.assertIn("unavailable", " ".join(LineageBrowser(loaded.lineage).detail_lines()).lower())

    def test_bad_new_chronicle_refuses_before_writing(self):
        session = pet()
        session = session.adopt(session.grid, session.slip_profile, origin="hatched")
        with tempfile.TemporaryDirectory() as tmp:
            path = session.save(Path(tmp) / "companion.json")
            base = json.loads(path.read_text())
            mutations = [
                lambda p: p["lineage"][-1].update(life_id=p["lineage"][0]["life_id"]),
                lambda p: p["lineage"][-1].update(grid_id="not-the-active-grid"),
                lambda p: p["lineage"][-1]["care_summary"].update(ticks_observed=-1),
                lambda p: p["lineage"][-1]["care_summary"].update(keeper_actions={"feed": True}),
                lambda p: p["lineage"][-1].update(outcome="dead"),
                lambda p: p["chronicle"].update(keeper_id=""),
                lambda p: p["chronicle"].update(keeper_id="different-keeper"),
                lambda p: p["lineage"][-1].update(lineage={"generation": 987}),
                lambda p: p["state"].update(grid_id="different-active-grid"),
                lambda p: p.update(succession_index=0),
            ]
            for mutate in mutations:
                payload = copy.deepcopy(base)
                mutate(payload)
                path.write_text(json.dumps(payload))
                before = path.read_bytes()
                with self.subTest(payload=payload["lineage"][-1]), self.assertRaises(ValueError):
                    CompanionSession.load(path)
                self.assertEqual(before, path.read_bytes())

    def test_backup_recovery_restores_exact_recorded_story_and_keeps_newer_bytes(self):
        with tempfile.TemporaryDirectory() as tmp:
            session = pet()
            path = session.save(Path(tmp) / "companion.json")
            session = session.adopt(session.grid, session.slip_profile, origin="hatched")
            session.save(path)
            expected = path.read_bytes()
            session = session.adopt(session.grid, session.slip_profile, origin="era_elite")
            session.save(path)
            newer = path.read_bytes()
            restored, archive = CompanionSession.recover_backup(path)
            self.assertEqual(expected, path.read_bytes())
            self.assertEqual(newer, archive.read_bytes())
            self.assertEqual(2, len(restored.lineage))
            self.assertEqual(session.keeper_id, restored.keeper_id)

    def test_recovery_branches_to_a_unique_life_without_merging_archived_progress(self):
        with tempfile.TemporaryDirectory() as tmp:
            session = pet()
            path = session.save(Path(tmp) / "companion.json")
            newer = session.adopt(session.grid, session.slip_profile, origin="hatched")
            newer.save(path)
            recovered, archive = CompanionSession.recover_backup(path)
            archived = CompanionSession.load(archive)
            branched = recovered.adopt(recovered.grid, recovered.slip_profile, origin="era_elite")
            self.assertEqual(1, len(recovered.lineage))
            self.assertEqual(2, len(branched.lineage))
            self.assertEqual(2, len(archived.lineage))
            self.assertEqual(archived.keeper_id, branched.keeper_id)
            self.assertNotEqual(archived.lineage[-1]["life_id"], branched.lineage[-1]["life_id"])
            self.assertEqual(archived.lineage[0]["life_id"], branched.lineage[0]["life_id"])

    def test_campaign_binding_requires_a_known_successor_and_never_tends(self):
        session = pet()
        self.assertIsNone(session.campaign_id)
        self.assertTrue(session.bind_campaign("one"))
        self.assertFalse(session.bind_campaign("one"))
        with self.assertRaises(ValueError):
            session.bind_campaign("foreign")
        with self.assertRaises(ValueError):
            session.bind_campaign("two", predecessor_campaign_id="foreign")
        self.assertTrue(session.bind_campaign("two", predecessor_campaign_id="one"))
        self.assertEqual("two", session.campaign_id)
        self.assertEqual(0, session.session_tick)
        self.assertEqual(2, len(session.chronicle["campaign_links"]))
        adopted = session.adopt(session.grid, session.slip_profile,
                                source={"campaign_id": "historical-source", "era_index": 1})
        self.assertEqual("two", adopted.campaign_id)
        self.assertEqual("historical-source", adopted.lineage[-1]["source"]["campaign_id"])

    def test_unknown_legacy_binding_accepts_a_validated_successor_without_inventing_a_prior_link(self):
        session = pet()
        session.mark_history_unavailable("No old campaign association was recorded.")
        self.assertTrue(session.bind_campaign("known-successor", predecessor_campaign_id="known-predecessor"))
        self.assertEqual("known-successor", session.campaign_id)
        self.assertEqual(1, len(session.chronicle["campaign_links"]))
        link = session.chronicle["campaign_links"][0]
        self.assertNotIn("predecessor_campaign_id", link)
        self.assertEqual("known-predecessor", link["campaign_predecessor_id"])
        with tempfile.TemporaryDirectory() as tmp:
            loaded = CompanionSession.load(session.save(Path(tmp) / "companion.json"))
            self.assertEqual(session.chronicle, loaded.chronicle)

    def test_saved_earlier_life_and_history_reason_must_remain_renderable(self):
        session = pet()
        session = session.adopt(session.grid, session.slip_profile, origin="hatched")
        with tempfile.TemporaryDirectory() as tmp:
            path = session.save(Path(tmp) / "companion.json")
            base = json.loads(path.read_text())
            for mutation in (lambda p: p["lineage"][0].update(lineage=["malformed"]),
                             lambda p: p["lineage"][0]["lineage"].update(mutation_events={"lost": "value"}),
                             lambda p: p["chronicle"].update(prior_history_reason=["malformed"]),
                             lambda p: p["lineage"][-1].update(learning_policy="qtable")):
                payload = copy.deepcopy(base)
                mutation(payload)
                path.write_text(json.dumps(payload))
                with self.subTest(mutation=mutation), self.assertRaises(ValueError):
                    CompanionSession.load(path)

    def test_corrupt_event_tail_cannot_claim_different_care_or_death(self):
        session = pet()
        session.advance("feed")
        with tempfile.TemporaryDirectory() as tmp:
            path = session.save(Path(tmp) / "companion.json")
            base = json.loads(path.read_text())
            for mutation in (lambda row: row["events"][-1].update(action="play"),
                             lambda row: row["events"][-1].update(alive=False),
                             lambda row: row["events"][-1].update(begging=True)):
                payload = copy.deepcopy(base)
                mutation(payload["lineage"][-1])
                path.write_text(json.dumps(payload))
                with self.subTest(payload=payload["lineage"][-1]), self.assertRaises(ValueError):
                    CompanionSession.load(path)

    def test_unknown_discarded_history_is_marked_without_fabricated_lives(self):
        session = pet()
        session.mark_history_unavailable("Explicit new companion replaced unreadable primary.")
        self.assertEqual("unavailable", session.chronicle["prior_history"])
        self.assertEqual(1, len(session.lineage))

    def test_browser_exposes_recorded_campaign_links_and_missing_prior_history(self):
        session = pet()
        session.mark_history_unavailable("Unreadable original retained before replacement.")
        session.bind_campaign("campaign-one")
        session.bind_campaign("campaign-two", predecessor_campaign_id="campaign-one")
        browser = LineageBrowser(session.lineage, chronicle=session.chronicle)
        text = " ".join(browser.detail_lines())
        self.assertIn(session.keeper_id, text)
        self.assertIn("campaign-one", text)
        self.assertIn("campaign-two", text)
        self.assertIn("unavailable", text)

    def test_browser_shows_life_identity_care_replacement_and_source(self):
        session = pet()
        session.advance("feed")
        session = session.adopt(session.grid, session.slip_profile, origin="era_elite",
                                source={"campaign_id": "source-campaign", "era_index": 3})
        browser = LineageBrowser(session.lineage)
        self.assertIn("source-campaign", " ".join(browser.detail_lines()))
        browser.back()
        self.assertIn("replaced alive", browser.caption())
        self.assertNotIn("died", browser.caption())
        text = " ".join(browser.detail_lines())
        self.assertIn(session.lineage[0]["life_id"], text)
        self.assertIn("feed: 1", text)
        self.assertIn("keeper", text.lower())


if __name__ == "__main__":
    unittest.main()
