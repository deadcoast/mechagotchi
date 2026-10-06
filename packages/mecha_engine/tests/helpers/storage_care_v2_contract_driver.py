"""Versioned X7 v2 passive-ledger parity with unchanged identity refusal gates."""
import copy
import importlib.util
from pathlib import Path
import unittest

spec = importlib.util.spec_from_file_location('storage_care_v1_probes',
    Path(__file__).with_name('storage_care_contract_driver.py'))
legacy = importlib.util.module_from_spec(spec)
spec.loader.exec_module(legacy)


class StorageCareV2Tests(legacy.StorageCareTests):
    def setUp(self):
        super().setUp()
        value = legacy.payload(self.bundle)
        value['policy'] = 'observed_care_selection_v2'
        legacy.rehash(self.bundle, value)
        self.era['report']['care_selection']['policy'] = value['policy']
        self.bundle['manifest']['report_sha256'] = legacy.legacy.digest(self.era['report'])

    def test_policy_version_is_immutable_on_input_and_output(self):
        before = copy.deepcopy(self.bundle)
        self.store.validate_execution(self.bundle)
        self.assertEqual(before, self.bundle)
        value = legacy.payload(self.bundle)
        value['policy'] = 'observed_care_selection_v3'
        legacy.rehash(self.bundle, value)
        with self.assertRaises(ValueError):
            self.store.validate_execution(self.bundle)


if __name__ == '__main__':
    unittest.main()
