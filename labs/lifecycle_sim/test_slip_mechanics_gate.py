import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
import slip_mechanics_gate as gate
from slip_mechanics_gate import build_report, judge, write_report


class SlipMechanicsGateTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.report = build_report()

    def test_every_required_check_passes_with_frozen_incumbent_instruments(self):
        self.assertEqual('adopt_authorship', self.report['decision']['verdict'])
        self.assertEqual(32, self.report['metrics']['authority_cases'])
        self.assertEqual(192, self.report['metrics']['authority_votes'])
        self.assertEqual(4, self.report['metrics']['incumbent_profiles'])
        self.assertEqual([], self.report['metrics']['incumbent_engine_mismatches'])
        self.assertEqual([], self.report['metrics']['incumbent_game_mismatches'])
        self.assertEqual(0.0685, self.report['metrics']['dr0059_instrument']['committed_keeper_floor'])

    def test_each_gate_can_independently_withhold_adoption(self):
        for name in self.report['metrics']['checks']:
            with self.subTest(check=name):
                checks = dict(self.report['metrics']['checks'], **{name: False})
                self.assertEqual({'verdict': 'withhold', 'failed_checks': [name], 'rule': self.report['decision']['rule']}, judge(checks))

    def test_missing_checks_cannot_adopt(self):
        self.assertEqual('withhold', judge({})['verdict'])
        for name in self.report['metrics']['checks']:
            checks = dict(self.report['metrics']['checks'])
            del checks[name]
            self.assertEqual([name], judge(checks)['failed_checks'])

    def test_changed_committed_instrument_withholds_without_rebasing(self):
        original = gate.read

        def read_changed(name):
            artifact = original(name)
            if name == 'data/lifecycle/cleanliness_mechanic_gate_stage0.json':
                artifact['metrics']['instrument_check']['committed_keeper_floor'] = -1
            return artifact

        with patch.object(gate, 'read', side_effect=read_changed):
            report = build_report()
        self.assertEqual('withhold', report['decision']['verdict'])
        self.assertEqual(['dr0059_reproduced'], report['decision']['failed_checks'])

    def test_writer_targets_isolated_output_and_roundtrips(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / 'nested/report.json'
            write_report(path, self.report)
            self.assertEqual(self.report, json.loads(path.read_text()))


if __name__ == '__main__':
    unittest.main()
