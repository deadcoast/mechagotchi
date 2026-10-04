import unittest
from default_covenant_gate import build_report, decide


class DefaultCovenantGateTests(unittest.TestCase):
    def test_candidate_is_measured_against_frozen_instruments(self):
        report = build_report()
        self.assertTrue(report['metrics']['instrument_reproduced'])
        self.assertEqual(400, report['metrics']['candidate_attentive']['age_ticks'])
        self.assertEqual(10, report['metrics']['candidate_neglect']['age_ticks'])
        self.assertTrue(report['metrics']['scripted_care']['alive'])
        self.assertGreater(report['metrics']['scripted_care']['clean_count'], 0)
        self.assertEqual('ADOPT', report['decision']['verdict'])

    def test_each_missing_or_false_acceptance_check_refuses(self):
        names = ['instrument_reproduced', 'attentive_survives', 'neglect_unchanged', 'scripted_care_survives', 'clean_answers', 'window_contract']
        self.assertEqual('REFUSE', decide({})['verdict'])
        for name in names:
            with self.subTest(check=name):
                checks = dict.fromkeys(names, True)
                checks[name] = False
                self.assertEqual([name], decide(checks)['failed_checks'])
