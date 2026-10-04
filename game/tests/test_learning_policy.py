"""R2: the experimental learner is playable, persistent and keeper-mediated."""
import json
import sys
import tempfile
import unittest
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]
for relative in ("game/src", "packages/mecha_engine/src"):
    sys.path.insert(0,str(ROOT/relative))
from mecha_game.session import CompanionSession, KEPT_THREADS, load_session_inputs
from mecha_game.app import _footer_lines, build_parser


def companion(**kwargs):
    grid,slip,model=load_session_inputs(ROOT/"data/seed_grids_16x16/mg_seed16_001_beetle.json", ROOT/"data/slips/valid/slip_v2_cleanliness.json")
    return CompanionSession(grid,slip,model=model,**kwargs)


def care(session):
    state=session.state
    if state["hunger"]>.55: return "feed"
    if state["energy"]<.35: return "sleep"
    if state.get("cleanliness",1)<.6: return "clean"
    return None


class LearningPolicyTests(unittest.TestCase):
    def test_opt_in_enables_only_the_measured_addition(self):
        base=companion()
        enabled=companion(learning_policy="qtable")
        self.assertEqual("incumbent",base.learning_policy)
        self.assertNotIn("qtable_policy",base.state["learning_switches"])
        enabled.advance()
        self.assertEqual(set(KEPT_THREADS)|{"qtable_policy"},set(enabled.state["thread_states"]))
        self.assertIn("experimental", " ".join(_footer_lines(enabled.snapshot(),None)).lower())

    def test_cold_to_warm_and_exact_resume_continuation(self):
        session=companion(learning_policy="qtable")
        for _ in range(160):
            session.advance(care(session))
        self.assertTrue(session.alive)
        self.assertTrue(any(row.get("thought",{}).get("qtable_consumer") for row in session.log))
        with tempfile.TemporaryDirectory() as directory:
            path=Path(directory)/"companion.json"
            session.save(path)
            resumed=CompanionSession.load(path)
            self.assertEqual("qtable",resumed.learning_policy)
            self.assertEqual(session.state,resumed.state)
            for _ in range(30):
                action=care(session)
                self.assertEqual(session.advance(action),resumed.advance(action))
            self.assertEqual(session.snapshot(),resumed.snapshot())

    def test_existing_save_and_resume_conflict_are_safe(self):
        with tempfile.TemporaryDirectory() as directory:
            path=Path(directory)/"companion.json"
            companion().save(path)
            self.assertNotIn("learning_policy",json.loads(path.read_text()))
            before=path.read_bytes()
            self.assertEqual("incumbent",CompanionSession.load(path).learning_policy)
            with self.assertRaisesRegex(ValueError,"conflict"):
                CompanionSession.load(path,learning_policy="qtable")
            self.assertEqual(before,path.read_bytes())
            self.assertFalse(path.with_suffix(".bak.json").exists())

    def test_invalid_and_corrupt_modes_fail_before_writes(self):
        for policy in (None,True,1,"", "adaptive", [], {}):
            with self.subTest(policy=policy), self.assertRaises(ValueError):
                companion(learning_policy=policy)
        with tempfile.TemporaryDirectory() as directory:
            path=Path(directory)/"companion.json"
            companion(learning_policy="qtable").save(path)
            original=json.loads(path.read_text())
            for corrupt in ("unknown", None, True, {}):
                payload=dict(original,learning_policy=corrupt)
                path.write_text(json.dumps(payload))
                before=path.read_bytes()
                with self.assertRaises(ValueError): CompanionSession.load(path)
                self.assertEqual(before,path.read_bytes())
            original["state"]["thread_states"]={"qtable_policy":{"q":{"11|feed":{"mean":.5,"n":"bad"}}}}
            path.write_text(json.dumps(original))
            with self.assertRaisesRegex(ValueError,"Q-table"):
                CompanionSession.load(path)

    def test_fleet_off_is_inert(self):
        baseline=companion(fleet=False)
        experimental=companion(fleet=False,learning_policy="qtable")
        for _ in range(10):
            self.assertEqual(baseline.advance("feed"),experimental.advance("feed"))
        self.assertEqual({},experimental.snapshot()["threads"])
        self.assertNotIn("qtable_policy",experimental.state.get("thread_states",{}))

    def test_succession_keeps_mode_but_child_learning_is_cold(self):
        session=companion(learning_policy="qtable")
        while session.alive: session.advance()
        self.assertTrue(session.state["thread_states"]["qtable_policy"]["q"])
        parent=session.grid["grid_id"]
        session.succeed()
        self.assertEqual("qtable",session.learning_policy)
        self.assertEqual("qtable",session.lineage[-2]["learning_policy"])
        self.assertEqual(parent,session.lineage[-1]["parent_grid_id"])
        self.assertNotIn("qtable_policy",session.state.get("thread_states",{}))
        session.advance()
        self.assertEqual({},session.state["thread_states"]["qtable_policy"]["q"])

    def test_full_confidence_feed_remains_a_beg(self):
        session=companion(learning_policy="qtable")
        session.state.update(hunger=.55,energy=.55)
        session.state["thread_states"]={"qtable_policy":{"q":{"11|feed":{"mean":1.,"n":12}}}}
        session.advance()
        self.assertEqual("idle",session.log[-1]["action"])
        self.assertTrue(session.log[-1]["begging"])
        self.assertEqual("feed",session.log[-1]["thought"]["qtable_consumer"]["recommended"])
        text=" ".join(_footer_lines(session.snapshot(),None))
        self.assertIn("feed",text)
        session.advance("feed")
        self.assertEqual("keeper",session.log[-1]["actor"])
        self.assertEqual("feed",session.log[-1]["action"])

    def test_experimental_evaluator_keeps_engine_reflexes(self):
        for values, expected, begging in (({"energy":.1,"hunger":.55},"sleep",False),
                                          ({"energy":.55,"hunger":.9},"idle",True),
                                          ({"energy":.55,"hunger":.55,"stress":.9},"idle",False)):
            with self.subTest(values=values):
                session=companion(learning_policy="qtable")
                session.state.update(values)
                session.advance()
                self.assertEqual(expected,session.log[-1]["action"])
                self.assertEqual(begging,session.log[-1]["begging"])
                self.assertNotIn("thought",session.log[-1])

    def test_app_parser_exposes_new_life_choice_without_forcing_resume(self):
        self.assertIsNone(build_parser().parse_args([]).learning_policy)
        self.assertEqual("qtable",build_parser().parse_args(["--learning-policy","qtable"]).learning_policy)


if __name__ == "__main__": unittest.main()
