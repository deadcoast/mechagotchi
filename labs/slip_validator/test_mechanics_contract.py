import json
import unittest
from mechanics_contract import ROOT, evaluate_cases
from pydantic_contract import _generated_schema


class MechanicsContractTests(unittest.TestCase):
    def test_committed_schema_matches_current_generation(self):
        committed = json.loads((ROOT / 'research/slip/slip_pydantic_model.schema.json').read_text(encoding='utf-8'))
        self.assertEqual(committed, _generated_schema())

    def test_every_authority_matches_the_preregistered_adversarial_matrix(self):
        rows = evaluate_cases()
        self.assertEqual(32, len(rows))
        for row in rows:
            for authority, accepted in row['votes'].items():
                with self.subTest(case=row['case'], authority=authority):
                    self.assertEqual(row['expected'], accepted)
            self.assertTrue(row['inputs_preserved'])


if __name__ == '__main__':
    unittest.main()
