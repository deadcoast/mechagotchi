import copy
import unittest
from hidden_axis_source_survey import build_report, check_visible_instrument, HIDDEN_AXES

class HiddenAxisSourceSurveyTests(unittest.TestCase):
    def test_six_axes_have_bounded_sources_and_absences_have_no_invented_value(self):
        report=build_report()
        self.assertEqual(set(HIDDEN_AXES),set(report['metrics']['axes']))
        self.assertTrue(report['metrics']['visible_instrument_reproduced'])
        for axis,row in report['metrics']['axes'].items():
            self.assertIn(row['disposition'],('field','derived_engine_value','absent'))
            self.assertTrue(row['cause'])
            if row['disposition']=='absent': self.assertIsNone(row['value'])
            else:
                self.assertIsNotNone(row['value'])
                self.assertTrue(row['source'])
        self.assertEqual('survey_only_no_adoption',report['decision']['verdict'])

    def test_visible_instrument_refuses_a_changed_committed_record(self):
        report=build_report()
        bad=copy.deepcopy(report['instrument']['committed_visible_axes'])
        bad['age']['on_screen']['shown']=False
        with self.assertRaisesRegex(ValueError,'visible'):
            check_visible_instrument(report['instrument']['observed_visible_axes'],bad)

    def test_off_cold_warm_and_alignment_controls_are_real(self):
        observations=build_report()['metrics']['probe']
        self.assertEqual([],observations['fleet_off'])
        self.assertIsNone(observations['novelty_cold']['output']['boredom'])
        self.assertGreater(observations['novelty_repeat']['output']['boredom'],observations['novelty_varied']['output']['boredom'])
        self.assertEqual(0.0,observations['attention_cold']['confidence'])
        self.assertGreater(observations['attention_warm']['confidence'],0.0)
        self.assertTrue(observations['alignment_valid']['ok'])
        self.assertFalse(observations['alignment_invalid']['ok'])
        self.assertNotIn('cubff_pressure',observations['pressure_off_keys'])
        self.assertTrue(observations['pressure_on'])
