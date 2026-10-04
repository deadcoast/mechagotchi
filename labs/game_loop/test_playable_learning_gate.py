"""R3 refuses incomplete comparisons; no corpus or reward retuning."""
import sys
import unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
from playable_learning_gate import judge, run_trial, summarize, load_inputs


class PlayableLearningGateTests(unittest.TestCase):
    def test_every_required_gate_binds(self):
        good=dict(instruments=True,parity=True,release=True,complete_budget=True,
                  corpus_comparable=True,consumer_fires=True,gain_vs_incumbent=True,
                  gain_vs_additive=True,attentive_survives=True,neglect_unchanged=True)
        self.assertEqual("ADOPT",judge(good)["verdict"])
        for key in good:
            for value in (False,None):
                with self.subTest(key=key,value=value):
                    self.assertEqual("REFUSE",judge(dict(good,**{key:value}))["verdict"])
            missing=dict(good);missing.pop(key)
            self.assertEqual("REFUSE",judge(missing)["verdict"])

    def test_real_sessions_keep_palette_refusals_and_paired_seeds(self):
        seeds,slip,models=load_inputs()
        self.assertEqual(50,len(seeds))
        for arm in ("incumbent","additive","follower"):
            accepted=run_trial(seeds[0],slip,models[0],"attentive",arm,20,20260709)
            repeated=run_trial(seeds[0],slip,models[0],"attentive",arm,20,20260709)
            rejected=run_trial(seeds[1],slip,models[1],"attentive",arm,20,20260710)
            self.assertEqual(accepted,repeated)
            self.assertEqual("admitted",accepted["status"])
            self.assertEqual("refused",rejected["status"])
            self.assertIn("palette",rejected["reason"])
            self.assertNotIn("welfare",rejected)
            summary=summarize([accepted,rejected])
            self.assertIsNone(summary["welfare"])
            self.assertEqual(1,summary["refused_lifecycles"])
            self.assertEqual(1,summary["admitted_lifecycles"])
            if arm != "follower": self.assertEqual(0,accepted["consumer_recommendations"])


if __name__=="__main__": unittest.main()
